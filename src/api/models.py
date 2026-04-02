"""Pydantic models for the Week 2 FastAPI backend contract."""

from typing import Any, Literal

from pydantic import BaseModel, Field


PayloadKind = Literal["auto", "generic", "muscima_reference"]


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
    """Optional full graph payload for callers that need tensor contents as JSON."""

    node_feature_names: list[str]
    edge_feature_names: list[str]
    node_features: list[list[float]]
    edge_index: list[list[int]]
    edge_attr: list[list[float]]


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
    """Placeholder request contract for the future MIDI route."""

    payload: dict[str, Any] | None = None


class MidiResponse(BaseModel):
    """Placeholder response for the Week 2 MIDI stub."""

    status: str
    stage: str
    message: str
