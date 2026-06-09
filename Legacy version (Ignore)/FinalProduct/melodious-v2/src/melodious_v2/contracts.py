"""Versioned payload contracts for Melodious V2."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from melodious_v2.taxonomies import (
    DEEPSCORES_136_CLASS_NAMES,
    SEMANTIC_OMR_V2_CLASS_MAP,
)


SCHEMA_VERSION = "2.0"


class ImageSize(BaseModel):
    """Image dimensions in pixels."""

    width: int = Field(gt=0)
    height: int = Field(gt=0)


class NormalizedBBox(BaseModel):
    """Center-based normalized bounding box in `[0, 1]` coordinates."""

    x_center: float = Field(ge=0.0, le=1.0)
    y_center: float = Field(ge=0.0, le=1.0)
    width: float = Field(gt=0.0, le=1.0)
    height: float = Field(gt=0.0, le=1.0)


class PixelBBox(BaseModel):
    """Axis-aligned pixel bounding box."""

    x1: float = Field(ge=0.0)
    y1: float = Field(ge=0.0)
    x2: float = Field(ge=0.0)
    y2: float = Field(ge=0.0)

    @model_validator(mode="after")
    def validate_corners(self) -> "PixelBBox":
        if self.x2 <= self.x1:
            raise ValueError("x2 must be greater than x1.")
        if self.y2 <= self.y1:
            raise ValueError("y2 must be greater than y1.")
        return self


class DetectionV2(BaseModel):
    """Single detector output record."""

    class_id: int = Field(ge=0)
    class_name: str
    semantic_group: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: NormalizedBBox
    bbox_pixels: PixelBBox | None = None

    @model_validator(mode="after")
    def validate_class_pair(self) -> "DetectionV2":
        if self.class_name in DEEPSCORES_136_CLASS_NAMES:
            expected_id = DEEPSCORES_136_CLASS_NAMES.index(self.class_name)
            if self.class_id != expected_id:
                raise ValueError(
                    f"class_id {self.class_id} does not match {self.class_name} id {expected_id}."
                )
            if self.semantic_group is None:
                self.semantic_group = SEMANTIC_OMR_V2_CLASS_MAP[self.class_name]
        return self


class DetectorPayloadV2(BaseModel):
    """Canonical detector payload stored by runs and exchanged with the API."""

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["2.0"] = SCHEMA_VERSION
    run_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    taxonomy_id: Literal["deepscores_136", "semantic_omr_v2"]
    image_size: ImageSize
    detections: list[DetectionV2]
    model_artifact_sha256: str | None = None
    source_image_uri: str | None = None
    inference_ms: float | None = Field(default=None, ge=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("model_artifact_sha256")
    @classmethod
    def validate_sha256(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) != 64 or any(char not in "0123456789abcdef" for char in value.lower()):
            raise ValueError("model_artifact_sha256 must be a 64-character hex digest.")
        return value.lower()


class MetricProvenance(BaseModel):
    """Metadata required for generated metric reports."""

    run_id: str
    commit: str
    config_path: str
    dataset_id: str
    split: str
    taxonomy_id: str
    metric_version: str = "v2.0"
    artifact_sha256: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArtifactRecord(BaseModel):
    """Artifact metadata returned by API and saved in run manifests."""

    artifact_id: str
    artifact_type: Literal["musicxml", "midi", "overlay", "metrics", "payload"]
    content_type: str
    sha256: str | None = None
    uri: str | None = None


def write_detector_payload_schema(output_path: str | Path) -> None:
    """Write the JSON schema for external handoff and validation."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(DetectorPayloadV2.model_json_schema(), indent=2), encoding="utf-8")
