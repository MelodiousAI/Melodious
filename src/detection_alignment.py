"""Align detector outputs to MUSCIMA++ ground-truth nodes.

This file bridges the project's two graph worlds:
- parsed MUSCIMA++ reference nodes from the dataset
- predicted detection boxes from a detector

The core alignment strategy is greedy IoU matching with optional class-aware
filtering. The goal is to keep the first version standard, explainable, and
useful for later evaluation.
"""

from pathlib import Path
import argparse
import json

from pyg_graph_builder import extract_detection_sequence, adapt_detection_to_canonical


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NODES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "muscima_nodes.json"


def load_muscima_nodes(nodes_json_path=NODES_JSON_PATH):
    """Load the parsed MUSCIMA node dictionaries from disk."""
    with open(nodes_json_path, "r", encoding="utf-8") as nodes_file:
        return json.load(nodes_file)


def get_document_nodes(all_nodes, document_name):
    """Keep only the ground-truth nodes for one MUSCIMA document."""
    return [node for node in all_nodes if node["document"] == document_name]


def prepare_alignment_detections(raw_detections):
    """Normalize raw detections while preserving optional class-name metadata.

    The PyG builder already knows how to adapt several realistic detector output
    aliases to the canonical detection schema. Alignment reuses that logic but
    also keeps an optional `class_name` field when the caller provides it.
    """
    raw_detection_list = extract_detection_sequence(raw_detections)
    prepared_detections = []

    for raw_detection in raw_detection_list:
        canonical_detection = adapt_detection_to_canonical(raw_detection)
        prepared_detection = dict(canonical_detection)

        if "class_name" in raw_detection:
            prepared_detection["class_name"] = raw_detection["class_name"]

        prepared_detections.append(prepared_detection)

    return prepared_detections


def get_node_bbox_xyxy(node):
    """Convert one MUSCIMA node box to `(x_min, y_min, x_max, y_max)` format."""
    bounding_box = node["bounding_box"]
    return (
        float(bounding_box["left"]),
        float(bounding_box["top"]),
        float(bounding_box["right"]),
        float(bounding_box["bottom"]),
    )


def get_detection_bbox_xyxy(detection):
    """Convert one center-based detection box to `(x_min, y_min, x_max, y_max)`."""
    x_center, y_center, width, height = detection["bbox"]
    return (
        float(x_center) - (float(width) / 2.0),
        float(y_center) - (float(height) / 2.0),
        float(x_center) + (float(width) / 2.0),
        float(y_center) + (float(height) / 2.0),
    )


def compute_iou(box_a, box_b):
    """Compute intersection-over-union for two axis-aligned boxes."""
    ax_min, ay_min, ax_max, ay_max = box_a
    bx_min, by_min, bx_max, by_max = box_b

    intersection_x_min = max(ax_min, bx_min)
    intersection_y_min = max(ay_min, by_min)
    intersection_x_max = min(ax_max, bx_max)
    intersection_y_max = min(ay_max, by_max)

    intersection_width = max(0.0, intersection_x_max - intersection_x_min)
    intersection_height = max(0.0, intersection_y_max - intersection_y_min)
    intersection_area = intersection_width * intersection_height

    area_a = max(0.0, ax_max - ax_min) * max(0.0, ay_max - ay_min)
    area_b = max(0.0, bx_max - bx_min) * max(0.0, by_max - by_min)
    union_area = area_a + area_b - intersection_area

    if union_area <= 0.0:
        return 0.0

    return intersection_area / union_area


def classes_are_compatible(detection, ground_truth_node, class_name_to_id=None):
    """Check whether a detection and ground-truth node should be allowed to match.

    Class-aware matching is enabled only when enough metadata exists:
    - if the detection includes `class_name`, compare names directly
    - else if `class_name_to_id` is provided, compare the detection `class_id`
      to the mapped ID for the ground-truth class name
    - otherwise, fall back to geometry-only matching
    """
    if "class_name" in detection:
        return detection["class_name"] == ground_truth_node["class_name"]

    if class_name_to_id is not None:
        expected_class_id = class_name_to_id.get(ground_truth_node["class_name"])

        if expected_class_id is None:
            return False

        return int(detection["class_id"]) == int(expected_class_id)

    return True


def build_candidate_matches(detections, ground_truth_nodes, iou_threshold, class_name_to_id=None):
    """Build all valid detection-to-node candidate matches above the IoU threshold."""
    candidate_matches = []

    for detection_index, detection in enumerate(detections):
        detection_bbox = get_detection_bbox_xyxy(detection)

        for node_index, ground_truth_node in enumerate(ground_truth_nodes):
            if not classes_are_compatible(detection, ground_truth_node, class_name_to_id):
                continue

            node_bbox = get_node_bbox_xyxy(ground_truth_node)
            iou = compute_iou(detection_bbox, node_bbox)

            if iou >= iou_threshold:
                candidate_matches.append(
                    {
                        "detection_index": detection_index,
                        "node_index": node_index,
                        "iou": iou,
                    }
                )

    candidate_matches.sort(key=lambda match: match["iou"], reverse=True)
    return candidate_matches


def build_alignment_summary(match_count, false_positive_count, false_negative_count):
    """Compute a compact evaluation summary from the final matching counts."""
    if match_count + false_positive_count > 0:
        precision = match_count / (match_count + false_positive_count)
    else:
        precision = 0.0

    if match_count + false_negative_count > 0:
        recall = match_count / (match_count + false_negative_count)
    else:
        recall = 0.0

    if precision + recall > 0:
        f1_score = 2.0 * precision * recall / (precision + recall)
    else:
        f1_score = 0.0

    return {
        "match_count": match_count,
        "false_positive_count": false_positive_count,
        "false_negative_count": false_negative_count,
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1_score": round(f1_score, 6),
    }


def align_detections_to_ground_truth(raw_detections, ground_truth_nodes, iou_threshold=0.5, class_name_to_id=None):
    """Align detections to one document's ground-truth nodes with greedy IoU matching.

    The algorithm is intentionally standard and explainable:
    1. normalize detections
    2. build all valid detection-node candidates above the IoU threshold
    3. sort them by IoU descending
    4. greedily accept a match only if both the detection and node are still free

    This guarantees a one-to-one matching without solving a more complex global
    assignment problem yet.
    """
    detections = prepare_alignment_detections(raw_detections)
    candidate_matches = build_candidate_matches(
        detections,
        ground_truth_nodes,
        iou_threshold,
        class_name_to_id=class_name_to_id,
    )

    matched_detection_indices = set()
    matched_node_indices = set()
    accepted_matches = []

    for candidate_match in candidate_matches:
        detection_index = candidate_match["detection_index"]
        node_index = candidate_match["node_index"]

        if detection_index in matched_detection_indices:
            continue

        if node_index in matched_node_indices:
            continue

        matched_detection_indices.add(detection_index)
        matched_node_indices.add(node_index)
        accepted_matches.append(
            {
                "detection_index": detection_index,
                "node_index": node_index,
                "iou": round(candidate_match["iou"], 6),
                "detection": detections[detection_index],
                "ground_truth_node_key": ground_truth_nodes[node_index]["node_key"],
                "ground_truth_class_name": ground_truth_nodes[node_index]["class_name"],
            }
        )

    false_positives = [
        {
            "detection_index": index,
            "detection": detection,
        }
        for index, detection in enumerate(detections)
        if index not in matched_detection_indices
    ]

    false_negatives = [
        {
            "node_index": index,
            "ground_truth_node_key": node["node_key"],
            "ground_truth_class_name": node["class_name"],
        }
        for index, node in enumerate(ground_truth_nodes)
        if index not in matched_node_indices
    ]

    summary = build_alignment_summary(
        match_count=len(accepted_matches),
        false_positive_count=len(false_positives),
        false_negative_count=len(false_negatives),
    )

    return {
        "matches": accepted_matches,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "summary": summary,
    }


def align_document_detections(document_name, raw_detections, all_nodes, iou_threshold=0.5, class_name_to_id=None):
    """Align detections against the ground-truth nodes for one MUSCIMA document."""
    document_nodes = get_document_nodes(all_nodes, document_name)

    if not document_nodes:
        raise ValueError(f"No ground-truth nodes found for document: {document_name}")

    alignment_result = align_detections_to_ground_truth(
        raw_detections,
        document_nodes,
        iou_threshold=iou_threshold,
        class_name_to_id=class_name_to_id,
    )
    alignment_result["document"] = document_name
    return alignment_result


def parse_cli_args():
    """Parse command-line arguments for one-document alignment runs."""
    parser = argparse.ArgumentParser(description="Align detections to MUSCIMA ground truth for one document.")
    parser.add_argument("--document", type=str, required=True, help="MUSCIMA document name.")
    parser.add_argument("--detections-json", type=str, required=True, help="Path to one detections JSON file.")
    parser.add_argument("--iou-threshold", type=float, default=0.5, help="IoU threshold for a valid match.")
    return parser.parse_args()


def load_detections_json(detections_json_path):
    """Load raw detections from one JSON file."""
    detections_json_path = Path(detections_json_path)

    if not detections_json_path.is_absolute():
        detections_json_path = PROJECT_ROOT / detections_json_path

    with open(detections_json_path, "r", encoding="utf-8") as detections_file:
        return json.load(detections_file)


def main():
    """Run one-document alignment from the command line."""
    args = parse_cli_args()
    all_nodes = load_muscima_nodes()
    raw_detections = load_detections_json(args.detections_json)
    alignment_result = align_document_detections(
        args.document,
        raw_detections,
        all_nodes,
        iou_threshold=args.iou_threshold,
    )

    print(f"Document: {alignment_result['document']}")
    print(f"Matches: {alignment_result['summary']['match_count']}")
    print(f"False positives: {alignment_result['summary']['false_positive_count']}")
    print(f"False negatives: {alignment_result['summary']['false_negative_count']}")
    print(f"Precision: {alignment_result['summary']['precision']}")
    print(f"Recall: {alignment_result['summary']['recall']}")
    print(f"F1: {alignment_result['summary']['f1_score']}")


if __name__ == "__main__":
    main()
