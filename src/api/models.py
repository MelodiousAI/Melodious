"""Pydantic models for the Week 2 FastAPI backend contract."""

from typing import Any, Literal

from pydantic import BaseModel, Field


PayloadKind = Literal["auto", "generic", "muscima_reference"]
ExportFormat = Literal["midi", "musicxml"]


class HealthResponse(BaseModel):
    """Simple service-health response for the backend skeleton."""

    status: str
    service: str
    stage: str


class AssembleRequest(BaseModel):
    """Request contract for turning one detector payload into graph outputs."""

    payload: dict[str, Any]
    payload_kind: PayloadKind = "auto"
    staff_regions: list[list[int]] | None = None
    run_alignment: bool = False
    document_name: str | None = None
    iou_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    include_graph_data: bool = False


class GraphStatisticsResponse(BaseModel):
    """Compact graph summary returned by the backend."""

    num_nodes: int
    num_edges: int
    node_feature_dim: int
    edge_feature_dim: int
    average_degree: float


class AlignmentSummaryResponse(BaseModel):
    """Compact alignment metrics returned when alignment is requested."""

    match_count: int
    false_positive_count: int
    false_negative_count: int
    precision: float
    recall: float
    f1_score: float


class SerializedGraphResponse(BaseModel):
    """Optional full graph payload for callers that need tensor contents as JSON.

    `node_features[i]` matches input detection `i` after normalization, and
    every pair in `edge_index` refers to that same serialized node row space.
    """

    node_feature_names: list[str]
    edge_feature_names: list[str]
    node_features: list[list[float]]
    edge_index: list[list[int]]
    edge_attr: list[list[float]]


class AssemblySummaryResponse(BaseModel):
    """Compact heuristic-assembly counts used by the export route."""

    note_count: int
    clef_count: int
    rest_count: int
    unmatched_count: int


class AssembleResponse(BaseModel):
    """Response contract for `/assemble`."""

    status: str
    payload_kind: Literal["generic", "muscima_reference"]
    document_name: str | None = None
    detection_count: int
    graph_statistics: GraphStatisticsResponse
    alignment_summary: AlignmentSummaryResponse | None = None
    graph_data: SerializedGraphResponse | None = None
    warnings: list[str] = Field(default_factory=list)


class MidiRequest(BaseModel):
    """Request contract for Week 3 score export."""

    payload: dict[str, Any]
    output_format: ExportFormat = "midi"
    title: str | None = None
    document_name: str | None = None


class MidiResponse(BaseModel):
    """Inline export response for the `/midi` route."""

    status: str
    stage: str
    output_format: ExportFormat
    content_type: str
    content_encoding: Literal["base64", "utf-8"]
    document_name: str | None = None
    title: str
    detection_count: int
    assembly_summary: AssemblySummaryResponse
    content: str
    warnings: list[str] = Field(default_factory=list)
