"""Service-layer helpers for the Week 2 FastAPI backend."""

from functools import lru_cache
from pathlib import Path

from src.graph.detection_alignment import (
    MUSCIMA_SHARED_CLASS_NAME_TO_ID,
    align_document_detections,
    load_muscima_nodes,
)
from src.graph.pyg_graph_builder import (
    EDGE_FEATURE_NAMES,
    NODE_FEATURE_NAMES,
    build_graph_from_detection_payload,
    build_graph_from_muscima_detection_payload,
    build_graph_statistics,
    extract_detection_sequence,
    extract_payload_image_path,
)

from src.api.models import (
    AlignmentSummaryResponse,
    AssembleRequest,
    AssembleResponse,
    GraphStatisticsResponse,
    MidiResponse,
    SerializedGraphResponse,
)


@lru_cache(maxsize=1)
def load_cached_muscima_nodes():
    """Load parsed MUSCIMA nodes once for repeated alignment requests."""
    return load_muscima_nodes()


def normalize_staff_regions(staff_regions):
    """Normalize request staff regions to `(y_min, y_max)` integer tuples."""
    if staff_regions is None:
        return None

    normalized_regions = []

    for region in staff_regions:
        if len(region) != 2:
            raise ValueError("Each staff region must contain exactly two integers: [y_min, y_max].")

        y_min, y_max = int(region[0]), int(region[1])

        if y_min > y_max:
            raise ValueError("Each staff region must satisfy y_min <= y_max.")

        normalized_regions.append((y_min, y_max))

    return normalized_regions


def infer_document_name(payload):
    """Infer one document name from the payload image path when possible."""
    image_path = extract_payload_image_path(payload)

    if image_path is None:
        return None

    return Path(image_path).stem


def resolve_payload_kind(payload, requested_kind):
    """Resolve the actual graph-building path to use for one request."""
    if requested_kind != "auto":
        return requested_kind

    document_name = infer_document_name(payload)

    if document_name and document_name.startswith("CVC-MUSCIMA_"):
        return "muscima_reference"

    return "generic"


def serialize_graph(graph_data):
    """Convert PyG graph tensors to JSON-friendly Python lists."""
    return SerializedGraphResponse(
        node_feature_names=list(NODE_FEATURE_NAMES),
        edge_feature_names=list(EDGE_FEATURE_NAMES),
        node_features=graph_data.x.tolist(),
        edge_index=graph_data.edge_index.tolist(),
        edge_attr=graph_data.edge_attr.tolist(),
    )


def build_midi_placeholder_response():
    """Return the Week 2 MIDI placeholder response."""
    return MidiResponse(
        status="not_implemented",
        stage="v0.2",
        message="The /midi endpoint is reserved for Week 3 wiring to the MusicXML/MIDI export pipeline.",
    )


def assemble_from_request(request: AssembleRequest):
    """Build one graph response from the incoming assemble request."""
    payload_kind = resolve_payload_kind(request.payload, request.payload_kind)
    detection_count = len(extract_detection_sequence(request.payload))
    warnings = []
    staff_regions = normalize_staff_regions(request.staff_regions)

    if payload_kind == "muscima_reference":
        if staff_regions:
            warnings.append("staff_regions were ignored because MUSCIMA reference payloads derive staff regions locally.")

        graph_data = build_graph_from_muscima_detection_payload(request.payload)
    else:
        graph_data = build_graph_from_detection_payload(
            request.payload,
            staff_regions=staff_regions,
        )

    graph_statistics = GraphStatisticsResponse(**build_graph_statistics(graph_data))
    document_name = request.document_name or infer_document_name(request.payload)
    alignment_summary = None

    if request.run_alignment:
        if document_name is None:
            raise ValueError("Alignment requires document_name or a payload image_path that resolves to a document stem.")

        alignment_result = align_document_detections(
            document_name,
            request.payload,
            load_cached_muscima_nodes(),
            iou_threshold=request.iou_threshold,
            class_name_to_id=MUSCIMA_SHARED_CLASS_NAME_TO_ID,
        )
        alignment_summary = AlignmentSummaryResponse(**alignment_result["summary"])

    serialized_graph = serialize_graph(graph_data) if request.include_graph_data else None

    return AssembleResponse(
        status="ok",
        payload_kind=payload_kind,
        document_name=document_name,
        detection_count=detection_count,
        graph_statistics=graph_statistics,
        alignment_summary=alignment_summary,
        graph_data=serialized_graph,
        warnings=warnings,
    )
