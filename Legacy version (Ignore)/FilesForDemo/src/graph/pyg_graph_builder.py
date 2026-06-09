"""Build PyTorch Geometric graphs from detection dictionaries and staff regions.

This file is the model-facing graph builder.
It takes a list of symbol detections and turns them into a PyG `Data` object
with node features, edge connections, and edge attributes.
"""

import json
import math
from pathlib import Path

import cv2
import torch
from torch_geometric.data import Data

from src.data_prep.staff_detection import detect_staff_lines
from src.graph.muscima_graph_builder import ensure_document_image


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Each node stores a compact but richer description than the original 7-feature version.
# These names are kept in one place so tests and debugging code can refer to them directly.
NODE_FEATURE_NAMES = [
    "class_id",
    "x_norm",
    "y_norm",
    "w_norm",
    "h_norm",
    "conf",
    "staff_index",
    "aspect_ratio",
    "area_norm",
    "staff_center_distance_norm",
]

# Edge attributes mix relation flags with geometric strength information.
# The first 4 values say what kind of relationship the edge represents.
# The last 4 values describe how close or how aligned the two detections are.
EDGE_FEATURE_NAMES = [
    "is_knn",
    "is_same_staff_local",
    "is_vertical_overlap",
    "is_horizontal_neighbor",
    "center_distance_norm",
    "x_distance_norm",
    "y_distance_norm",
    "vertical_overlap_ratio",
]

# k controls how many local geometric neighbors each node can connect to.
KNN_K = 4

# Radius pruning avoids keeping a nearest neighbor if it is still unrealistically far away.
MAX_NEIGHBOR_DISTANCE_RATIO = 0.22

# Same-staff edges are kept local on purpose so each staff does not become a dense clique.
SAME_STAFF_NEIGHBORS = 2

# Vertical-overlap edges are created only when two boxes overlap enough to be meaningful.
VERTICAL_OVERLAP_THRESHOLD = 0.3

# Canonical detection schema used internally and recommended for saved JSON files.
# A real detector adapter may accept a few common aliases, but everything is
# normalized to this format before graph construction continues.
CANONICAL_DETECTION_SCHEMA = {
    "class_id": "integer class index",
    "bbox": "[x_center, y_center, width, height] in pixels",
    "conf": "confidence score in [0, 1]",
}


def extract_detection_sequence(raw_detections):
    """Extract the actual list of detections from a few simple container shapes.

    Supported inputs are intentionally limited to keep the interface easy to
    reason about:
    - a plain list of detection dictionaries
    - a dictionary with a top-level `detections` list
    """
    if isinstance(raw_detections, list):
        return raw_detections

    if isinstance(raw_detections, dict) and "detections" in raw_detections:
        detections = raw_detections["detections"]

        if not isinstance(detections, list):
            raise TypeError("The 'detections' field must contain a list.")

        return detections

    raise TypeError(
        "Detections must be a list or a dictionary with a top-level 'detections' list."
    )


def get_first_present(mapping, keys, required=False, default=None):
    """Return the first present key from a mapping across a small alias list."""
    for key in keys:
        if key in mapping:
            return mapping[key]

    if required:
        raise KeyError(f"Missing required keys. Expected one of: {keys}")

    return default


def extract_payload_image_shape(raw_detections):
    """Extract `(height, width)` from a detector payload when available."""
    if not isinstance(raw_detections, dict):
        return None

    image_size = raw_detections.get("image_size")

    if not isinstance(image_size, dict):
        return None

    width = image_size.get("width")
    height = image_size.get("height")

    if width is None or height is None:
        return None

    return int(height), int(width)


def extract_payload_image_path(raw_detections):
    """Extract the payload image path when the detector JSON includes one."""
    if isinstance(raw_detections, dict):
        image_path = raw_detections.get("image_path")

        if image_path:
            return Path(image_path)

    return None


def load_detection_payload(json_path):
    """Load one raw detector payload JSON file from disk."""
    json_path = Path(json_path)

    with json_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_normalized_bbox_dict(bbox):
    """Check whether a bbox dictionary is the normalized handoff format."""
    values = [
        float(bbox["x_center"]),
        float(bbox["y_center"]),
        float(bbox["width"]),
        float(bbox["height"]),
    ]
    return all(0.0 <= value <= 1.0 for value in values)


def convert_bbox_pixels_to_xywh(bbox_pixels):
    """Convert top-left pixel corners to center-based xywh pixels."""
    x1 = float(bbox_pixels["x1"])
    y1 = float(bbox_pixels["y1"])
    x2 = float(bbox_pixels["x2"])
    y2 = float(bbox_pixels["y2"])
    width = x2 - x1
    height = y2 - y1
    x_center = x1 + (width / 2.0)
    y_center = y1 + (height / 2.0)
    return [x_center, y_center, width, height]


def convert_bbox_object_to_xywh_pixels(bbox, image_shape=None):
    """Convert a bbox object to canonical pixel-space center-based xywh."""
    x_center = float(bbox["x_center"])
    y_center = float(bbox["y_center"])
    width = float(bbox["width"])
    height = float(bbox["height"])

    if is_normalized_bbox_dict(bbox):
        if image_shape is None:
            raise ValueError(
                "Normalized bbox objects require image dimensions from image_shape or payload image_size."
            )

        image_height, image_width = image_shape
        return [
            x_center * image_width,
            y_center * image_height,
            width * image_width,
            height * image_height,
        ]

    return [x_center, y_center, width, height]


def adapt_detection_to_canonical(detection, image_shape=None):
    """Convert likely detector-output dictionaries to the canonical internal schema."""
    if not isinstance(detection, dict):
        raise TypeError("Each detection must be a dictionary.")

    class_id = get_first_present(
        detection,
        ["class_id", "class", "class_index", "label_id"],
        required=True,
    )
    confidence = get_first_present(
        detection,
        ["conf", "confidence", "score"],
        required=True,
    )

    bbox = get_first_present(detection, ["bbox", "xywh"], required=False)

    if isinstance(bbox, (list, tuple)):
        bbox_xywh = [float(value) for value in bbox]
    elif isinstance(bbox, dict):
        if all(key in bbox for key in ["x_center", "y_center", "width", "height"]):
            bbox_xywh = convert_bbox_object_to_xywh_pixels(bbox, image_shape=image_shape)
        else:
            raise ValueError("bbox dictionaries must contain x_center, y_center, width, and height.")
    elif bbox is None and "bbox_pixels" in detection:
        bbox_xywh = convert_bbox_pixels_to_xywh(detection["bbox_pixels"])
    elif bbox is None:
        x_center = get_first_present(detection, ["x", "x_center", "cx"], required=True)
        y_center = get_first_present(detection, ["y", "y_center", "cy"], required=True)
        width = get_first_present(detection, ["w", "width"], required=True)
        height = get_first_present(detection, ["h", "height"], required=True)
        bbox_xywh = [float(x_center), float(y_center), float(width), float(height)]
    else:
        raise ValueError("bbox must be a list, tuple, or supported bbox dictionary.")

    return {
        "class_id": int(class_id),
        "bbox": bbox_xywh,
        "conf": float(confidence),
    }


def adapt_detections(raw_detections, image_shape=None):
    """Normalize raw detector output to the canonical list-of-dicts schema."""
    if image_shape is None:
        image_shape = extract_payload_image_shape(raw_detections)

    detections = extract_detection_sequence(raw_detections)
    return [adapt_detection_to_canonical(detection, image_shape=image_shape) for detection in detections]


def load_detections_from_json(json_path):
    """Load saved detections from JSON and normalize them to canonical form."""
    payload = load_detection_payload(json_path)
    payload_image_shape = extract_payload_image_shape(payload)
    return adapt_detections(payload, image_shape=payload_image_shape)


def load_image_shape(image_path):
    """Load only the image shape needed for graph construction from one page image."""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    return image.shape


def validate_image_shape(image_shape):
    """Validate that `image_shape` is a usable `(height, width)` pair.

    This function fails early when the image size is missing or malformed,
    which is much easier to debug than letting invalid values propagate into
    normalization code later in the pipeline.
    """
    if not isinstance(image_shape, (list, tuple)) or len(image_shape) != 2:
        raise ValueError("image_shape must be (height, width).")

    image_height, image_width = image_shape

    if image_height <= 0 or image_width <= 0:
        raise ValueError(f"Invalid image_shape: {image_shape}")


def validate_detections(detections):
    """Validate that detections follow the expected input format.

    Expected format for each detection:
    `{"class_id": int, "bbox": [x, y, w, h], "conf": float}`

    The graph builder assumes center-based bounding boxes, so this function
    checks that all required keys are present and that box sizes are positive.
    """
    if detections is None:
        raise TypeError("detections must be a list, not None.")

    if not isinstance(detections, list):
        raise TypeError("detections must be a list of dictionaries.")

    for index, detection in enumerate(detections):
        if not isinstance(detection, dict):
            raise TypeError(f"Detection {index} must be a dictionary.")

        required_keys = ["class_id", "bbox", "conf"]

        for key in required_keys:
            if key not in detection:
                raise KeyError(f"Detection {index} is missing required key: {key}")

        bbox = detection["bbox"]

        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            raise ValueError(f"Detection {index} must have bbox = [x, y, w, h].")

        _, _, width, height = bbox

        if width <= 0 or height <= 0:
            raise ValueError(f"Detection {index} has invalid bbox size: {bbox}")


def normalize_detection(detection, image_shape, input_index=None):
    """Convert one raw detection into a consistent internal representation.

    The builder keeps both pixel-space values and normalized values because:
    - pixel values are useful for geometric reasoning
    - normalized values are better for model input
    """
    image_height, image_width = image_shape
    image_area = image_height * image_width
    x, y, width, height = detection["bbox"]

    x_min = float(x) - (float(width) / 2)
    x_max = float(x) + (float(width) / 2)
    y_min = float(y) - (float(height) / 2)
    y_max = float(y) + (float(height) / 2)

    normalized_detection = {
        "class_id": int(detection["class_id"]),
        "conf": float(detection["conf"]),
        "x": float(x),
        "y": float(y),
        "w": float(width),
        "h": float(height),
        "x_min": x_min,
        "x_max": x_max,
        "y_min": y_min,
        "y_max": y_max,
        "x_norm": float(x) / image_width,
        "y_norm": float(y) / image_height,
        "w_norm": float(width) / image_width,
        "h_norm": float(height) / image_height,
        "area_norm": (float(width) * float(height)) / image_area,
        "aspect_ratio": float(width) / float(height),
    }

    if input_index is not None:
        normalized_detection["input_index"] = int(input_index)

    return normalized_detection


def prepare_detections(detections, image_shape):
    """Validate and normalize the raw detections before graph construction.

    The returned list preserves input order exactly. That order is the node
    index space exposed through `/assemble` when graph data is serialized.
    """
    validate_image_shape(image_shape)
    validate_detections(detections)
    return [
        normalize_detection(detection, image_shape, input_index=index)
        for index, detection in enumerate(detections)
    ]


def validate_detection_index_order(detections):
    """Ensure processed detections still occupy their original input positions.

    Future graph changes may add helper passes that sort or regroup detections.
    This check makes the `/assemble` contract explicit: node row `i` must still
    correspond to input detection `i`, and edge indices must refer to that same
    row-index space.
    """
    for expected_index, detection in enumerate(detections):
        input_index = detection.get("input_index")

        if input_index is None:
            continue

        if int(input_index) != expected_index:
            raise ValueError(
                "Processed detections were reordered. Serialized graph rows must preserve input detection order."
            )


def get_detection_bounds(detection):
    """Return `(x_min, y_min, x_max, y_max)` for one detection.

    This helper keeps boundary conversion in one place so overlap code stays
    short and consistent.
    """
    return (
        detection["x_min"],
        detection["y_min"],
        detection["x_max"],
        detection["y_max"],
    )


def assign_detection_to_staff(detection, staff_regions):
    """Assign one detection to the most appropriate staff region.

    The primary rule is simple: if the detection center lies inside a staff
    region, use that staff. If no region contains the center, fall back to the
    closest staff center so every detection still gets a usable staff index.
    """
    if not staff_regions:
        return -1

    center_y = detection["y"]

    for staff_index, (y_min, y_max) in enumerate(staff_regions):
        if y_min <= center_y <= y_max:
            return staff_index

    closest_staff_index = -1
    closest_distance = None

    for staff_index, (y_min, y_max) in enumerate(staff_regions):
        staff_center_y = (y_min + y_max) / 2
        distance = abs(center_y - staff_center_y)

        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_staff_index = staff_index

    return closest_staff_index


def compute_staff_center_distance_norm(detection, staff_regions, image_shape):
    """Measure how far a detection is from the center of its assigned staff.

    This becomes a node feature because distance-to-staff-center can help the
    model distinguish symbols that sit near the middle of a staff from symbols
    that float far above or below it.
    """
    if not staff_regions:
        return -1.0

    staff_index = detection["staff_index"]

    if staff_index < 0 or staff_index >= len(staff_regions):
        return -1.0

    image_height, _ = image_shape
    y_min, y_max = staff_regions[staff_index]
    staff_center_y = (y_min + y_max) / 2
    return abs(detection["y"] - staff_center_y) / image_height


def attach_staff_info(detections, staff_regions, image_shape):
    """Add staff-related metadata to every normalized detection."""
    enriched_detections = []

    for detection in detections:
        enriched_detection = dict(detection)
        enriched_detection["staff_index"] = assign_detection_to_staff(
            detection,
            staff_regions,
        )
        enriched_detection["staff_center_distance_norm"] = compute_staff_center_distance_norm(
            enriched_detection,
            staff_regions,
            image_shape,
        )
        enriched_detections.append(enriched_detection)

    return enriched_detections


def build_node_feature_vector(detection):
    """Build the final numeric feature vector for one graph node.

    The vector mixes:
    - identity (`class_id`)
    - geometry (`x/y/w/h`, aspect ratio, area)
    - detector confidence (`conf`)
    - musical layout context (`staff_index`, distance to staff center)
    """
    return [
        float(detection["class_id"]),
        float(detection["x_norm"]),
        float(detection["y_norm"]),
        float(detection["w_norm"]),
        float(detection["h_norm"]),
        float(detection["conf"]),
        float(detection["staff_index"]),
        float(detection["aspect_ratio"]),
        float(detection["area_norm"]),
        float(detection["staff_center_distance_norm"]),
    ]


def build_node_features(detections):
    """Stack all node feature vectors into the feature matrix `x`."""
    return [build_node_feature_vector(detection) for detection in detections]


def get_center_distance_norm(source_detection, target_detection, image_shape):
    """Return normalized center-to-center distance between two detections."""
    image_height, image_width = image_shape
    diagonal = math.sqrt((image_width ** 2) + (image_height ** 2))
    dx = source_detection["x"] - target_detection["x"]
    dy = source_detection["y"] - target_detection["y"]
    distance = math.sqrt((dx ** 2) + (dy ** 2))
    return distance / diagonal


def get_axis_distance_norms(source_detection, target_detection, image_shape):
    """Return normalized x-distance and y-distance between two detections."""
    image_height, image_width = image_shape
    x_distance_norm = abs(source_detection["x"] - target_detection["x"]) / image_width
    y_distance_norm = abs(source_detection["y"] - target_detection["y"]) / image_height
    return x_distance_norm, y_distance_norm


def build_knn_edges(detections, image_shape, k=KNN_K, max_distance_ratio=MAX_NEIGHBOR_DISTANCE_RATIO):
    """Build local geometric edges with k-nearest neighbors plus radius pruning.

    This is more stable than a plain distance threshold:
    - k-NN keeps local connectivity predictable
    - radius pruning avoids absurdly long edges on sparse pages
    - the fallback nearest neighbor prevents isolated nodes when the page is sparse
    """
    edges = set()

    if len(detections) <= 1:
        return edges

    for source_index, source_detection in enumerate(detections):
        candidate_neighbors = []

        for target_index, target_detection in enumerate(detections):
            if source_index == target_index:
                continue

            distance_norm = get_center_distance_norm(
                source_detection,
                target_detection,
                image_shape,
            )
            candidate_neighbors.append((distance_norm, target_index))

        candidate_neighbors.sort(key=lambda item: item[0])
        selected_neighbors = [
            target_index
            for distance_norm, target_index in candidate_neighbors[:k]
            if distance_norm <= max_distance_ratio
        ]

        # If radius pruning removes everything, keep the single nearest node
        # so isolated detections still participate in the graph.
        if not selected_neighbors and candidate_neighbors:
            selected_neighbors = [candidate_neighbors[0][1]]

        for target_index in selected_neighbors:
            edges.add((source_index, target_index))
            edges.add((target_index, source_index))

    return edges


def group_indices_by_staff(detections):
    """Group detection indices by staff so staff-local edges can be built cleanly."""
    grouped_indices = {}

    for index, detection in enumerate(detections):
        staff_index = detection["staff_index"]

        if staff_index == -1:
            continue

        grouped_indices.setdefault(staff_index, []).append(index)

    return grouped_indices


def build_same_staff_local_edges(detections, local_neighbors=SAME_STAFF_NEIGHBORS):
    """Connect each detection to a few nearby neighbors on the same staff.

    This intentionally avoids connecting every symbol on a staff to every other
    symbol. A full same-staff clique becomes too dense very quickly and usually
    adds more noise than useful structure.
    """
    edges = set()
    grouped_indices = group_indices_by_staff(detections)

    for staff_indices in grouped_indices.values():
        sorted_indices = sorted(staff_indices, key=lambda index: detections[index]["x"])

        for position, source_index in enumerate(sorted_indices):
            for neighbor_offset in range(1, local_neighbors + 1):
                target_position = position + neighbor_offset

                if target_position >= len(sorted_indices):
                    break

                target_index = sorted_indices[target_position]
                edges.add((source_index, target_index))
                edges.add((target_index, source_index))

    return edges


def build_horizontal_neighbor_edges(detections):
    """Connect immediate left-right neighbors within the same staff.

    These edges give the graph a simple notion of local reading order along a
    staff without forcing a fully sequential model.
    """
    edges = set()
    grouped_indices = group_indices_by_staff(detections)

    for staff_indices in grouped_indices.values():
        sorted_indices = sorted(staff_indices, key=lambda index: detections[index]["x"])

        for position in range(len(sorted_indices) - 1):
            source_index = sorted_indices[position]
            target_index = sorted_indices[position + 1]
            edges.add((source_index, target_index))
            edges.add((target_index, source_index))

    return edges


def vertical_overlap_ratio(source_detection, target_detection):
    """Measure how much two boxes overlap vertically.

    The overlap is normalized by the smaller box height so the score stays
    meaningful even when the two detections have different sizes.
    """
    _, source_y_min, _, source_y_max = get_detection_bounds(source_detection)
    _, target_y_min, _, target_y_max = get_detection_bounds(target_detection)

    overlap_top = max(source_y_min, target_y_min)
    overlap_bottom = min(source_y_max, target_y_max)
    overlap_height = max(0.0, overlap_bottom - overlap_top)

    smaller_height = min(source_detection["h"], target_detection["h"])

    if smaller_height <= 0:
        return 0.0

    return overlap_height / smaller_height


def build_vertical_overlap_edges(detections, threshold=VERTICAL_OVERLAP_THRESHOLD):
    """Connect detections whose boxes overlap strongly in the vertical direction."""
    edges = set()

    for source_index in range(len(detections)):
        source_detection = detections[source_index]

        for target_index in range(source_index + 1, len(detections)):
            target_detection = detections[target_index]
            overlap = vertical_overlap_ratio(source_detection, target_detection)

            if overlap >= threshold:
                edges.add((source_index, target_index))
                edges.add((target_index, source_index))

    return edges


def build_edge_index_and_attr(
    detections,
    image_shape,
    knn_edges,
    same_staff_edges,
    overlap_edges,
    horizontal_neighbor_edges,
):
    """Merge edge sets into PyG `edge_index` and `edge_attr`.

    Multiple edge builders may propose the same pair of nodes. Instead of
    storing duplicate edges, this function merges them and records all active
    relation flags in a single edge attribute vector.
    """
    edge_map = {}

    for source_index, target_index in knn_edges:
        edge_map.setdefault((source_index, target_index), [0.0, 0.0, 0.0, 0.0])[0] = 1.0

    for source_index, target_index in same_staff_edges:
        edge_map.setdefault((source_index, target_index), [0.0, 0.0, 0.0, 0.0])[1] = 1.0

    for source_index, target_index in overlap_edges:
        edge_map.setdefault((source_index, target_index), [0.0, 0.0, 0.0, 0.0])[2] = 1.0

    for source_index, target_index in horizontal_neighbor_edges:
        edge_map.setdefault((source_index, target_index), [0.0, 0.0, 0.0, 0.0])[3] = 1.0

    edge_pairs = sorted(edge_map.keys())
    edge_index = [
        [source_index for source_index, _ in edge_pairs],
        [target_index for _, target_index in edge_pairs],
    ]
    edge_attr = []

    for source_index, target_index in edge_pairs:
        source_detection = detections[source_index]
        target_detection = detections[target_index]
        relation_flags = edge_map[(source_index, target_index)]
        center_distance_norm = get_center_distance_norm(
            source_detection,
            target_detection,
            image_shape,
        )
        x_distance_norm, y_distance_norm = get_axis_distance_norms(
            source_detection,
            target_detection,
            image_shape,
        )
        overlap_ratio = vertical_overlap_ratio(source_detection, target_detection)

        edge_attr.append(
            relation_flags
            + [
                center_distance_norm,
                x_distance_norm,
                y_distance_norm,
                overlap_ratio,
            ]
        )

    return edge_index, edge_attr


def validate_graph_data(graph_data):
    """Run structural checks on the final PyG graph.

    These checks are intentionally strict. It is much better for graph
    construction to fail loudly here than to silently feed a malformed graph
    into model code later.
    """
    if graph_data.x.ndim != 2:
        raise ValueError("graph_data.x must be a 2D tensor.")

    if graph_data.edge_index.ndim != 2 or graph_data.edge_index.shape[0] != 2:
        raise ValueError("graph_data.edge_index must have shape [2, num_edges].")

    if graph_data.edge_attr.ndim != 2:
        raise ValueError("graph_data.edge_attr must be a 2D tensor.")

    if graph_data.edge_attr.shape[0] != graph_data.edge_index.shape[1]:
        raise ValueError("edge_attr row count must match edge_index column count.")

    if torch.isnan(graph_data.x).any():
        raise ValueError("graph_data.x contains NaN values.")

    if torch.isnan(graph_data.edge_attr).any():
        raise ValueError("graph_data.edge_attr contains NaN values.")

    if graph_data.edge_index.numel() > 0:
        if int(graph_data.edge_index.max().item()) >= graph_data.num_nodes:
            raise ValueError("graph_data.edge_index contains an invalid node index.")

        if int(graph_data.edge_index.min().item()) < 0:
            raise ValueError("graph_data.edge_index contains a negative node index.")


def build_empty_graph():
    """Return a valid empty PyG graph when there are no detections."""
    return Data(
        x=torch.empty((0, len(NODE_FEATURE_NAMES)), dtype=torch.float),
        edge_index=torch.empty((2, 0), dtype=torch.long),
        edge_attr=torch.empty((0, len(EDGE_FEATURE_NAMES)), dtype=torch.float),
        num_nodes=0,
    )


def build_graph_statistics(graph_data):
    """Summarize the final graph for debugging and inspection."""
    if graph_data.num_nodes == 0:
        average_degree = 0.0
    else:
        average_degree = graph_data.edge_index.shape[1] / graph_data.num_nodes

    return {
        "num_nodes": graph_data.num_nodes,
        "num_edges": int(graph_data.edge_index.shape[1]),
        "node_feature_dim": int(graph_data.x.shape[1]),
        "edge_feature_dim": int(graph_data.edge_attr.shape[1]),
        "average_degree": average_degree,
    }


def scale_staff_regions(staff_regions, source_height, target_height):
    """Scale staff regions from one image height into another coordinate space."""
    if source_height <= 0 or target_height <= 0:
        raise ValueError("source_height and target_height must be positive.")

    if source_height == target_height:
        return [(int(y_min), int(y_max)) for y_min, y_max in staff_regions]

    scale = target_height / source_height
    scaled_regions = []

    for y_min, y_max in staff_regions:
        scaled_regions.append(
            (
                int(round(y_min * scale)),
                int(round(y_max * scale)),
            )
        )

    return scaled_regions


def resolve_local_muscima_image_path(payload):
    """Resolve a MUSCIMA payload's stem to the local grayscale page image path."""
    payload_image_path = extract_payload_image_path(payload)

    if payload_image_path is None:
        raise ValueError("MUSCIMA payload must include image_path.")

    document_name = payload_image_path.stem

    if not document_name.startswith("CVC-MUSCIMA_"):
        raise ValueError(f"Payload does not look like a MUSCIMA page: {payload_image_path}")

    image_path = ensure_document_image(document_name)

    if not image_path.exists():
        raise FileNotFoundError(f"Could not resolve local MUSCIMA image: {image_path}")

    return image_path


def build_graph_from_detection_payload(payload, staff_regions=None):
    """Build a graph directly from one full detector payload.

    This path is useful for imported handoff JSON files where image dimensions are
    present in the payload, but the referenced image may not exist locally.
    """
    image_shape = extract_payload_image_shape(payload)

    if image_shape is None:
        raise ValueError("Detection payload must include image_size with width and height.")

    detections = adapt_detections(payload, image_shape=image_shape)
    return build_graph(detections, image_shape, staff_regions=staff_regions)


def build_graph_from_muscima_detection_payload(payload):
    """Build a graph from a MUSCIMA reference payload plus the local page image.

    MUSCIMA reference payloads use annotation-space image dimensions, while the
    local grayscale PNGs can differ slightly in pixel size. This wrapper runs
    staff detection on the local image and then scales the detected staff regions
    into the payload coordinate space before building the graph.
    """
    payload_shape = extract_payload_image_shape(payload)

    if payload_shape is None:
        raise ValueError("MUSCIMA payload must include image_size with width and height.")

    local_image_path = resolve_local_muscima_image_path(payload)
    local_image_shape = load_image_shape(local_image_path)
    local_staff_regions = detect_staff_lines(local_image_path)
    scaled_staff_regions = scale_staff_regions(
        local_staff_regions,
        source_height=local_image_shape[0],
        target_height=payload_shape[0],
    )

    detections = adapt_detections(payload, image_shape=payload_shape)
    return build_graph(detections, payload_shape, staff_regions=scaled_staff_regions)


def build_graph_from_image_and_detections(image_path, raw_detections):
    """Build a PyG graph directly from one image path and raw detector output."""
    image_path = Path(image_path)
    image_shape = load_image_shape(image_path)
    detections = adapt_detections(raw_detections, image_shape=image_shape)
    staff_regions = detect_staff_lines(image_path)
    return build_graph(detections, image_shape, staff_regions=staff_regions)


def build_graph_from_detection_json(detections_json_path, image_path=None, detect_staff=False):
    """Build a graph from one saved detector JSON payload."""
    payload = load_detection_payload(detections_json_path)

    if detect_staff:
        resolved_image_path = Path(image_path) if image_path is not None else extract_payload_image_path(payload)

        if resolved_image_path is None:
            raise ValueError("Staff detection requires an explicit image path or a payload image_path.")

        return build_graph_from_image_and_detections(resolved_image_path, payload)

    return build_graph_from_detection_payload(payload)


def build_graph_from_muscima_detection_json(detections_json_path):
    """Build a graph from one MUSCIMA reference payload JSON file."""
    payload = load_detection_payload(detections_json_path)
    return build_graph_from_muscima_detection_payload(payload)


def build_graph(detections, image_shape, staff_regions=None):
    """Build one PyTorch Geometric `Data` graph from detections.

    Pipeline:
    1. validate and normalize detections
    2. attach staff information
    3. build node features
    4. build several complementary edge sets
    5. merge edge sets into `edge_index` and `edge_attr`
    6. validate the final graph before returning it
    """
    if staff_regions is None:
        staff_regions = []

    if not detections:
        empty_graph = build_empty_graph()
        validate_graph_data(empty_graph)
        return empty_graph

    processed_detections = prepare_detections(detections, image_shape)
    processed_detections = attach_staff_info(processed_detections, staff_regions, image_shape)
    validate_detection_index_order(processed_detections)

    node_features = build_node_features(processed_detections)
    knn_edges = build_knn_edges(processed_detections, image_shape)
    same_staff_edges = build_same_staff_local_edges(processed_detections)
    overlap_edges = build_vertical_overlap_edges(processed_detections)
    horizontal_neighbor_edges = build_horizontal_neighbor_edges(processed_detections)
    edge_index, edge_attr = build_edge_index_and_attr(
        processed_detections,
        image_shape,
        knn_edges,
        same_staff_edges,
        overlap_edges,
        horizontal_neighbor_edges,
    )

    x_tensor = torch.tensor(node_features, dtype=torch.float)

    if edge_index[0]:
        edge_index_tensor = torch.tensor(edge_index, dtype=torch.long)
        edge_attr_tensor = torch.tensor(edge_attr, dtype=torch.float)
    else:
        edge_index_tensor = torch.empty((2, 0), dtype=torch.long)
        edge_attr_tensor = torch.empty((0, len(EDGE_FEATURE_NAMES)), dtype=torch.float)

    graph_data = Data(
        x=x_tensor,
        edge_index=edge_index_tensor,
        edge_attr=edge_attr_tensor,
        num_nodes=len(processed_detections),
    )

    validate_graph_data(graph_data)
    return graph_data


def build_fake_test_detections():
    """Return three tiny fake detections for quick local testing."""
    return [
        {"class_id": 1, "bbox": [100, 120, 30, 24], "conf": 0.95},
        {"class_id": 2, "bbox": [145, 128, 28, 22], "conf": 0.91},
        {"class_id": 3, "bbox": [110, 250, 26, 30], "conf": 0.88},
    ]


def run_fake_graph_test():
    """Run a tiny end-to-end demo of the PyG graph builder."""
    image_shape = (400, 300)
    staff_regions = [(90, 160), (220, 290)]
    detections = build_fake_test_detections()
    graph_data = build_graph(detections, image_shape, staff_regions=staff_regions)
    graph_stats = build_graph_statistics(graph_data)

    print("Fake graph test:")
    print(f"num_nodes: {graph_data.num_nodes}")
    print(f"x.shape: {list(graph_data.x.shape)}")
    print(f"edge_index.shape: {list(graph_data.edge_index.shape)}")
    print(f"edge_attr.shape: {list(graph_data.edge_attr.shape)}")
    print(f"graph_stats: {graph_stats}")

    print()
    print("Checks:")
    print(f"num_nodes == 3: {graph_data.num_nodes == 3}")
    print(
        f"x.shape == [3, {len(NODE_FEATURE_NAMES)}]: "
        f"{list(graph_data.x.shape) == [3, len(NODE_FEATURE_NAMES)]}"
    )
    print(f"edge_index is not empty: {graph_data.edge_index.numel() > 0}")

    return graph_data


def main():
    """Run the tiny fake graph demo when this file is executed directly."""
    run_fake_graph_test()


if __name__ == "__main__":
    main()
