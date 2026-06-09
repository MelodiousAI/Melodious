"""Product-facing service helpers for the Week 5 public frontend."""

from __future__ import annotations

import base64
import json
import re
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException

from src.api.models import AssembleRequest, MidiRequest
from src.api.product_models import (
    ProductAudioResponse,
    ProductConfidenceIndicatorResponse,
    ProductConfigResponse,
    ProductDownloadResponse,
    ProductDownloadsResponse,
    ProductExplainabilityResponse,
    ProductFeatureFlagsResponse,
    ProductSampleResponse,
    ProductScorePreviewResponse,
    ProductTranscriptionResponse,
    ProductTranscriptionSummaryResponse,
)
from src.api.service import assemble_from_request, export_from_request
from src.graph.muscima_graph_builder import ensure_document_image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MUSCIMA_SAMPLE_DIR = PROJECT_ROOT / "sample_detections" / "muscima_reference"
PRODUCT_STAGE = "v0.5"


def build_product_feature_flags() -> ProductFeatureFlagsResponse:
    """Return the public Week 5 feature flags."""
    return ProductFeatureFlagsResponse(
        image_upload_enabled=False,
        attention_overlay_enabled=False,
        llm_explainer_enabled=False,
    )


def build_product_config() -> ProductConfigResponse:
    """Return the public frontend configuration surface."""
    return ProductConfigResponse(
        app_name="Melodious",
        stage=PRODUCT_STAGE,
        active_experience="sample_first",
        upload_status_message=(
            "Raw sheet-music upload is reserved for a later detector integration. "
            "Week 5 focuses on polished sample-based transcription demos."
        ),
        feature_flags=build_product_feature_flags(),
    )


def _parse_writer_and_page(document_name: str) -> tuple[int, int]:
    """Extract MUSCIMA writer and page numbers from one document name."""
    writer_match = re.search(r"W-(\d+)", document_name)
    page_match = re.search(r"N-(\d+)", document_name)

    if writer_match is None or page_match is None:
        raise ValueError(f"Could not parse writer/page from MUSCIMA document name: {document_name}")

    return int(writer_match.group(1)), int(page_match.group(1))


def _build_product_sample(document_name: str) -> ProductSampleResponse:
    """Build one public sample record from a MUSCIMA document name."""
    writer_number, page_number = _parse_writer_and_page(document_name)

    return ProductSampleResponse(
        id=document_name,
        title=f"Handwritten Study {page_number:02d}",
        subtitle=f"Writer {writer_number:02d} · MUSCIMA++ sample",
        document_name=document_name,
        preview_image_url=f"/product/samples/{document_name}/image",
        description=(
            "A curated handwritten notation sample used to demo the Melodious transcription flow."
        ),
        tags=["Handwritten", "MUSCIMA++", "Demo"],
    )


@lru_cache(maxsize=1)
def get_product_sample_catalog() -> dict[str, ProductSampleResponse]:
    """Load and cache the public MUSCIMA sample catalog."""
    sample_catalog: dict[str, ProductSampleResponse] = {}

    if not MUSCIMA_SAMPLE_DIR.exists():
        return sample_catalog

    for payload_path in sorted(MUSCIMA_SAMPLE_DIR.glob("*.json")):
        sample = _build_product_sample(payload_path.stem)
        sample_catalog[sample.id] = sample

    return sample_catalog


def list_product_samples() -> list[ProductSampleResponse]:
    """Return the sorted public sample list."""
    return list(get_product_sample_catalog().values())


def get_product_sample(sample_id: str) -> ProductSampleResponse:
    """Return one sample definition or raise a public 404."""
    sample = get_product_sample_catalog().get(sample_id)

    if sample is None:
        raise HTTPException(status_code=404, detail=f"Unknown product sample: {sample_id}")

    return sample


def load_product_sample_payload(sample_id: str) -> dict:
    """Load one MUSCIMA sample payload from disk."""
    payload_path = MUSCIMA_SAMPLE_DIR / f"{sample_id}.json"

    if not payload_path.exists():
        raise HTTPException(status_code=404, detail=f"Unknown product sample: {sample_id}")

    with payload_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_product_sample_image_path(sample_id: str) -> Path:
    """Resolve the repo-local score image for one public sample."""
    sample = get_product_sample(sample_id)
    image_path = ensure_document_image(sample.document_name)

    if not image_path.exists():
        raise HTTPException(status_code=404, detail=f"Local score image not found for sample: {sample_id}")

    return image_path


def build_product_confidence_indicator(
    detection_count: int,
    unmatched_count: int,
) -> ProductConfidenceIndicatorResponse:
    """Turn current assembly counts into a simple qualitative cue."""
    if detection_count <= 0:
        coverage_ratio = 0.0
    else:
        coverage_ratio = max(0.0, min(1.0, (detection_count - unmatched_count) / detection_count))

    if coverage_ratio >= 0.9:
        tone = "high"
        label = "Stable demo result"
    elif coverage_ratio >= 0.75:
        tone = "medium"
        label = "Promising preview"
    else:
        tone = "low"
        label = "Interpret with care"

    return ProductConfidenceIndicatorResponse(
        tone=tone,
        label=label,
        message=(
            "This is a qualitative Week 5 cue based on current assembly coverage. "
            "It is not a calibrated model probability."
        ),
        calibrated=False,
    )


def build_product_explainability(assemble_response) -> ProductExplainabilityResponse:
    """Wrap the backend attention placeholder in a product-facing message."""
    attention_preview = assemble_response.attention_preview
    state = "available" if attention_preview.available else "placeholder"

    return ProductExplainabilityResponse(
        state=state,
        title="Attention Overlay",
        message=attention_preview.message,
    )


def build_product_downloads(sample_id: str, musicxml_response, midi_response) -> ProductDownloadsResponse:
    """Build download metadata for frontend use."""
    document_name = musicxml_response.document_name or sample_id

    return ProductDownloadsResponse(
        musicxml=ProductDownloadResponse(
            ready=True,
            url=f"/product/samples/{sample_id}/downloads/musicxml",
            file_name=f"{document_name}.musicxml",
            content_type=musicxml_response.content_type,
        ),
        midi=ProductDownloadResponse(
            ready=True,
            url=f"/product/samples/{sample_id}/downloads/midi",
            file_name=f"{document_name}.mid",
            content_type=midi_response.content_type,
        ),
    )


def build_product_audio(sample_id: str) -> ProductAudioResponse:
    """Build frontend audio playback metadata."""
    return ProductAudioResponse(
        playable=True,
        source_url=f"/product/samples/{sample_id}/downloads/midi",
        format="midi",
        message="MIDI playback uses the exported demo file for this sample.",
    )


def transcribe_product_sample(sample_id: str) -> ProductTranscriptionResponse:
    """Run the public Week 5 transcription flow for one curated sample."""
    sample = get_product_sample(sample_id)
    payload = load_product_sample_payload(sample_id)

    assemble_response = assemble_from_request(
        AssembleRequest(
            payload=payload,
            payload_kind="auto",
            assembly_mode="auto",
        )
    )
    musicxml_response = export_from_request(
        MidiRequest(
            payload=payload,
            output_format="musicxml",
            payload_kind="auto",
            assembly_mode="auto",
        )
    )
    midi_response = export_from_request(
        MidiRequest(
            payload=payload,
            output_format="midi",
            payload_kind="auto",
            assembly_mode="auto",
        )
    )

    summary = ProductTranscriptionSummaryResponse(
        detection_count=assemble_response.detection_count,
        note_count=assemble_response.assembly_summary.note_count,
        clef_count=assemble_response.assembly_summary.clef_count,
        rest_count=assemble_response.assembly_summary.rest_count,
        unmatched_count=assemble_response.assembly_summary.unmatched_count,
    )
    notices = list(assemble_response.warnings)

    for warning in musicxml_response.warnings + midi_response.warnings:
        if warning not in notices:
            notices.append(warning)

    return ProductTranscriptionResponse(
        sample=sample,
        score_preview=ProductScorePreviewResponse(
            image_url=sample.preview_image_url,
            alt_text=f"Preview image for {sample.title}",
        ),
        transcription_summary=summary,
        confidence_indicator=build_product_confidence_indicator(
            detection_count=assemble_response.detection_count,
            unmatched_count=assemble_response.assembly_summary.unmatched_count,
        ),
        explainability=build_product_explainability(assemble_response),
        downloads=build_product_downloads(sample_id, musicxml_response, midi_response),
        audio=build_product_audio(sample_id),
        feature_flags=build_product_feature_flags(),
        notices=notices,
    )


def build_product_download_asset(sample_id: str, output_format: str) -> tuple[bytes, str, str]:
    """Return bytes, MIME type, and filename for one public export asset."""
    payload = load_product_sample_payload(sample_id)
    export_response = export_from_request(
        MidiRequest(
            payload=payload,
            output_format=output_format,
            payload_kind="auto",
            assembly_mode="auto",
        )
    )
    document_name = export_response.document_name or sample_id

    if output_format == "musicxml":
        return (
            export_response.content.encode("utf-8"),
            export_response.content_type,
            f"{document_name}.musicxml",
        )

    return (
        base64.b64decode(export_response.content),
        export_response.content_type,
        f"{document_name}.mid",
    )
