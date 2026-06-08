"""Typed request/response models for the Melodious V2 product upload app.

These models describe the real upload-to-MusicXML/MIDI product flow exposed at
``/product/*``. They are intentionally separate from the contract-sample
``/transcriptions`` models so the demo app surface can evolve without changing
the strict detector payload contract.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

JobStatus = Literal["queued", "processing", "complete", "failed"]


class ProductCounts(BaseModel):
    """Aggregate musical counts extracted from an uploaded page."""

    staff_systems: int = 0
    events: int = 0
    notes: int = 0
    rests: int = 0
    dotted_notes: int = 0
    stem_confirmed_notes: int = 0
    slur_starts: int = 0
    tie_starts: int = 0
    relationship_count: int = 0


class ModelProvenance(BaseModel):
    """Which model artifacts produced this transcription."""

    extractor_mode: str = "unknown"
    detector_checkpoint: str | None = None
    thin_symbol_checkpoint: str | None = None
    gnn_checkpoint: str | None = None
    assembly_mode: str = "none"


class ModelAvailability(BaseModel):
    """Which model stages were actually used for this run.

    Drives the frontend model-availability badge so the demo honestly shows
    whether the full-page detector, the tiled thin-symbol detector, and the GNN
    relationship model contributed to the result.
    """

    full_page_detector: bool = False
    tiled_detector: bool = False
    gnn: bool = False


class QualitySummary(BaseModel):
    """Heuristic confidence/quality summary derived from counts and warnings.

    This is a presentation-only signal. It is explicitly NOT a measured metric
    and must not be reported as detector or end-to-end accuracy.
    """

    label: Literal["high", "review", "low"] = "review"
    score: float = 0.0
    headline: str = ""
    reasons: list[str] = Field(default_factory=list)


class NoteEvent(BaseModel):
    """A single ordered musical event for the note/event table."""

    order: int
    event_type: Literal["note", "rest"]
    staff_index: int
    onset_quarter: float
    quarter_length: float
    dotted: bool = False
    rhythm_source: str = "default"
    source: str = ""
    confidence: float = 0.0
    # Pitch fields are absent for rests.
    step: str | None = None
    octave: int | None = None
    alter: int = 0
    midi_pitch: int | None = None
    pitch_label: str | None = None
    pitch_source: str | None = None
    stem_detected: bool = False
    slur_start_count: int = 0
    slur_stop_count: int = 0
    tie_start_count: int = 0
    tie_stop_count: int = 0


class ProductTranscription(BaseModel):
    """Full product transcription job record and result payload.

    While the job is still running, ``status`` is ``queued``/``processing`` and
    the result fields (counts, urls, note_events) stay at their empty defaults.
    Once ``status`` is ``complete`` every result field is populated. On failure,
    ``status`` is ``failed`` and ``error`` explains why.
    """

    job_id: str
    status: JobStatus
    stage: str = "queued"
    stage_label: str = "Queued"
    progress: float = 0.0
    filename: str | None = None
    created_at: float
    updated_at: float

    # Artifact URLs (populated when complete).
    original_image_url: str | None = None
    overlay_image_url: str | None = None
    musicxml_url: str | None = None
    midi_url: str | None = None
    notes_json_url: str | None = None
    detector_payload_url: str | None = None
    relationships_url: str | None = None
    bundle_url: str | None = None

    # Result detail.
    image_width: int | None = None
    image_height: int | None = None
    key_fifths: int = 0
    counts: ProductCounts = Field(default_factory=ProductCounts)
    model_provenance: ModelProvenance = Field(default_factory=ModelProvenance)
    model_availability: ModelAvailability = Field(default_factory=ModelAvailability)
    quality: QualitySummary = Field(default_factory=QualitySummary)
    note_events: list[NoteEvent] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    error: str | None = None

    # Honesty marker so the UI never mislabels this as an official metric run.
    metric_claim: str = "none"
    disclaimer: str = (
        "Demo transcription. Pitch is estimated from treble-clef staff geometry "
        "and rhythm is heuristic. This is not an official evaluation metric run."
    )


class ProductSample(BaseModel):
    """A curated demo image bundled with the backend for one-click transcription."""

    sample_id: str
    title: str
    subtitle: str
    description: str
    available: bool = True
