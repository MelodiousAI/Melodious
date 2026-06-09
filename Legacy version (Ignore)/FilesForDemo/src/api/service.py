"""Service-layer helpers for the Week 4 FastAPI backend."""

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
from src.export.heuristic_assembler import assemble_detections, summarize_assembled_output
from src.export.musicxml_export import export_payload_content
from src.inference.gnn_service import GnnAssemblyService

from src.api.models import (
    AttentionPreviewResponse,
    AssemblySummaryResponse,
    AssemblyModeResponse,
    AlignmentSummaryResponse,
    AssembleRequest,
    AssembleResponse,
    GnnStatusResponse,
    GraphStatisticsResponse,
    HealthResponse,
    MidiRequest,
    MidiResponse,
    SerializedGraphResponse,
)


SERVICE_STAGE = "v0.4"


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


def get_gnn_service():
    """Build the Week 4 GNN service scaffold on demand."""
    return GnnAssemblyService()


def build_health_response():
    """Return service health plus GNN readiness for the current process."""
    gnn_status = get_gnn_service().get_runtime_status()

    return HealthResponse(
        status="ok",
        service="melodious-backend",
        stage=SERVICE_STAGE,
        available_assembly_modes=["auto", "heuristic", "gnn"],
        default_assembly_mode="auto",
        gnn_status=GnnStatusResponse(**gnn_status.__dict__),
    )


def build_assembly_summary(detection_sequence):
    """Return the current assembly summary baseline used by API responses."""
    assembled_output = assemble_detections(detection_sequence)
    return AssemblySummaryResponse(**summarize_assembled_output(assembled_output))


def build_graph_for_payload(payload, payload_kind, staff_regions, warnings):
    """Construct one graph while preserving the locked Week 3 payload behavior."""
    normalized_staff_regions = normalize_staff_regions(staff_regions)

    if payload_kind == "muscima_reference":
        if normalized_staff_regions:
            warnings.append("staff_regions were ignored because MUSCIMA reference payloads derive staff regions locally.")

        return build_graph_from_muscima_detection_payload(payload)

    return build_graph_from_detection_payload(
        payload,
        staff_regions=normalized_staff_regions,
    )


def resolve_assembly_runtime(requested_mode, warnings):
    """Resolve Week 4 assembly mode metadata and attach fallback warnings."""
    gnn_service = get_gnn_service()
    mode_decision = gnn_service.resolve_assembly_mode(requested_mode)
    warnings.extend(mode_decision.warnings)

    return (
        AssemblyModeResponse(
            requested_mode=mode_decision.requested_mode,
            applied_mode=mode_decision.applied_mode,
            fallback_applied=mode_decision.fallback_applied,
            fallback_reason=mode_decision.fallback_reason,
            checkpoint_ready=mode_decision.checkpoint_ready,
        ),
        AttentionPreviewResponse(**gnn_service.build_attention_preview(mode_decision).__dict__),
    )


def export_from_request(request: MidiRequest):
    """Build inline MusicXML or MIDI content from one detector payload."""
    detection_sequence = extract_detection_sequence(request.payload)
    document_name = request.document_name or infer_document_name(request.payload)
    title = request.title or document_name or "Melodious Export"
    warnings = []

    if document_name is None and request.title is None:
        warnings.append(
            "document_name could not be inferred from payload.image_path, so a generic export title was used."
        )

    payload_kind = resolve_payload_kind(request.payload, request.payload_kind)
    if request.assembly_mode != "heuristic":
        build_graph_for_payload(
            request.payload,
            payload_kind=payload_kind,
            staff_regions=request.staff_regions,
            warnings=warnings,
        )

    assembly_mode, attention_preview = resolve_assembly_runtime(request.assembly_mode, warnings)
    assembly_summary = build_assembly_summary(detection_sequence)
    content, content_type, content_encoding = export_payload_content(
        request.payload,
        output_format=request.output_format,
        title=title,
    )

    return MidiResponse(
        status="ok",
        stage=SERVICE_STAGE,
        output_format=request.output_format,
        content_type=content_type,
        content_encoding=content_encoding,
        document_name=document_name,
        title=title,
        detection_count=len(detection_sequence),
        assembly_mode=assembly_mode,
        assembly_summary=assembly_summary,
        attention_preview=attention_preview,
        content=content,
        warnings=warnings,
    )


def assemble_from_request(request: AssembleRequest):
    """Build one graph response from the incoming assemble request."""
    payload_kind = resolve_payload_kind(request.payload, request.payload_kind)
    detection_count = len(extract_detection_sequence(request.payload))
    warnings = []
    detection_sequence = extract_detection_sequence(request.payload)

    graph_data = build_graph_for_payload(
        request.payload,
        payload_kind=payload_kind,
        staff_regions=request.staff_regions,
        warnings=warnings,
    )

    graph_statistics = GraphStatisticsResponse(**build_graph_statistics(graph_data))
    document_name = request.document_name or infer_document_name(request.payload)
    assembly_mode, attention_preview = resolve_assembly_runtime(request.assembly_mode, warnings)
    assembly_summary = build_assembly_summary(detection_sequence)
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
        stage=SERVICE_STAGE,
        payload_kind=payload_kind,
        document_name=document_name,
        detection_count=detection_count,
        graph_statistics=graph_statistics,
        assembly_mode=assembly_mode,
        assembly_summary=assembly_summary,
        attention_preview=attention_preview,
        alignment_summary=alignment_summary,
        graph_data=serialized_graph,
        warnings=warnings,
    )
