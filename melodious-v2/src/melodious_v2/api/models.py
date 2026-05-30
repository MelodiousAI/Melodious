"""API request and response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from melodious_v2.contracts import ArtifactRecord, DetectorPayloadV2


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str
    environment: str
    detector_modes: list[str]
    assembly_modes: list[str]


class VersionResponse(BaseModel):
    version: str
    schema_version: str
    detector_taxonomy: str
    semantic_taxonomy: str


class SampleRecord(BaseModel):
    sample_id: str
    title: str
    description: str
    payload: DetectorPayloadV2


class TranscriptionRequest(BaseModel):
    sample_id: str | None = None
    image_base64: str | None = None
    filename: str | None = None
    requested_assembly_mode: Literal["auto", "heuristic", "gnn"] = "auto"


class AssemblyModeResponse(BaseModel):
    requested_mode: str
    applied_mode: str
    fallback_applied: bool
    fallback_reason: str | None
    checkpoint_ready: bool
    warnings: list[str] = Field(default_factory=list)


class TranscriptionResponse(BaseModel):
    job_id: str
    status: Literal["complete"]
    detector_mode: str
    assembly_mode: AssemblyModeResponse
    detection_count: int
    relationship_count: int
    payload: DetectorPayloadV2
    artifacts: list[ArtifactRecord]
    metric_provenance: dict
    warnings: list[str] = Field(default_factory=list)

