"""Public-facing product models for the Week 5 musician experience."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ProductFeatureFlagsResponse(BaseModel):
    """Public frontend capability flags."""

    image_upload_enabled: bool
    attention_overlay_enabled: bool
    llm_explainer_enabled: bool


class ProductConfigResponse(BaseModel):
    """Frontend configuration for the public Week 5 experience."""

    app_name: str
    stage: str
    active_experience: Literal["sample_first"]
    upload_status_message: str
    feature_flags: ProductFeatureFlagsResponse


class ProductBoundingBoxResponse(BaseModel):
    """Pixel and normalized box coordinates for an uploaded-image detection."""

    x1: float
    y1: float
    x2: float
    y2: float
    x_center: float
    y_center: float
    width: float
    height: float


class ProductImageDetectionResponse(BaseModel):
    """One YOLO symbol detection returned for an uploaded image."""

    class_id: int
    class_name: str
    confidence: float
    bbox: ProductBoundingBoxResponse


class ProductClassCountResponse(BaseModel):
    """Detected count for one symbol class."""

    class_name: str
    count: int


class ProductImageClassificationResponse(BaseModel):
    """Detector-only response for uploaded score images or phone camera captures."""

    file_name: str
    image_width: int
    image_height: int
    model_checkpoint: str
    confidence_threshold: float
    detection_count: int
    returned_detection_count: int
    class_counts: list[ProductClassCountResponse]
    detections: list[ProductImageDetectionResponse]
    notices: list[str] = Field(default_factory=list)


class ProductSampleResponse(BaseModel):
    """One curated product sample exposed to the public frontend."""

    id: str
    title: str
    subtitle: str
    document_name: str
    preview_image_url: str
    description: str
    tags: list[str] = Field(default_factory=list)


class ProductSamplesResponse(BaseModel):
    """List response for the public sample catalog."""

    items: list[ProductSampleResponse]


class ProductTranscribeRequest(BaseModel):
    """Week 5 request contract for public sample transcription."""

    sample_id: str


class ProductScorePreviewResponse(BaseModel):
    """Score-image preview metadata for the public UI."""

    image_url: str
    alt_text: str


class ProductTranscriptionSummaryResponse(BaseModel):
    """Simple musician-facing transcription counts."""

    detection_count: int
    note_count: int
    clef_count: int
    rest_count: int
    unmatched_count: int


class ProductConfidenceIndicatorResponse(BaseModel):
    """Qualitative, non-calibrated confidence cue for the Week 5 demo."""

    tone: Literal["high", "medium", "low"]
    label: str
    message: str
    calibrated: bool


class ProductExplainabilityResponse(BaseModel):
    """Stable explainability surface that wraps backend attention placeholders."""

    state: Literal["available", "placeholder", "unavailable"]
    title: str
    message: str


class ProductDownloadResponse(BaseModel):
    """Download metadata for one exported asset."""

    ready: bool
    url: str
    file_name: str
    content_type: str


class ProductDownloadsResponse(BaseModel):
    """Download affordances exposed to the public frontend."""

    musicxml: ProductDownloadResponse
    midi: ProductDownloadResponse


class ProductAudioResponse(BaseModel):
    """Playback metadata for the public UI."""

    playable: bool
    source_url: str
    format: Literal["midi"]
    message: str


class ProductTranscriptionResponse(BaseModel):
    """Merged public-facing transcription response."""

    sample: ProductSampleResponse
    score_preview: ProductScorePreviewResponse
    transcription_summary: ProductTranscriptionSummaryResponse
    confidence_indicator: ProductConfidenceIndicatorResponse
    explainability: ProductExplainabilityResponse
    downloads: ProductDownloadsResponse
    audio: ProductAudioResponse
    feature_flags: ProductFeatureFlagsResponse
    notices: list[str] = Field(default_factory=list)
