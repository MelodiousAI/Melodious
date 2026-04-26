"""Product-facing service helpers for the Week 5 public frontend."""

from __future__ import annotations

import base64
import json
import re
from functools import lru_cache
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from PIL import Image, ImageDraw, UnidentifiedImageError

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
from src.graph.muscima_graph_builder import get_image_path_from_document
from src.inference.image_detector import build_detection_payload_for_image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MUSCIMA_SAMPLE_DIR = PROJECT_ROOT / "sample_detections" / "muscima_reference"
UPLOAD_ROOT = PROJECT_ROOT / "outputs" / "product_uploads"
SAMPLE_PREVIEW_ROOT = PROJECT_ROOT / "outputs" / "product_sample_previews"
PRODUCT_STAGE = "v0.5"
ALLOWED_UPLOAD_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
_UPLOAD_RESULTS: dict[str, dict] = {}


def build_product_feature_flags() -> ProductFeatureFlagsResponse:
    """Return the public Week 5 feature flags."""
    return ProductFeatureFlagsResponse(
        image_upload_enabled=True,
        attention_overlay_enabled=False,
        llm_explainer_enabled=False,
    )


def build_product_config() -> ProductConfigResponse:
    """Return the public frontend configuration surface."""
    return ProductConfigResponse(
        app_name="Melodious",
        stage=PRODUCT_STAGE,
        active_experience="upload_enabled",
        upload_status_message=(
            "Upload a PNG or JPG score image to run the detector/export pipeline. "
            "When no trained checkpoint is configured, Melodious uses a lightweight OpenCV fallback."
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
    image_path = get_image_path_from_document(sample.document_name)

    if image_path.exists():
        return image_path

    return build_product_sample_preview_image(sample_id)


def build_product_sample_preview_image(sample_id: str) -> Path:
    """Render a lightweight preview when raw MUSCIMA images are not checked in."""
    payload = load_product_sample_payload(sample_id)
    image_size = payload.get("image_size", {})
    source_width = max(1, int(image_size.get("width", 1000)))
    source_height = max(1, int(image_size.get("height", 700)))
    preview_width = 900
    preview_height = max(180, int(source_height * (preview_width / source_width)))
    scale_x = preview_width / source_width
    scale_y = preview_height / source_height

    SAMPLE_PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    preview_path = SAMPLE_PREVIEW_ROOT / f"{sample_id}.png"

    if preview_path.exists():
        return preview_path

    image = Image.new("RGB", (preview_width, preview_height), "white")
    draw = ImageDraw.Draw(image)

    for detection in payload.get("detections", []):
        box = detection.get("bbox_pixels")
        if not box:
            continue

        x1 = float(box["x1"]) * scale_x
        y1 = float(box["y1"]) * scale_y
        x2 = float(box["x2"]) * scale_x
        y2 = float(box["y2"]) * scale_y
        class_name = detection.get("class_name", "")
        outline = "#3f3f46" if class_name.startswith("notehead") else "#a16207"
        draw.rectangle((x1, y1, x2, y2), outline=outline, width=1)

    image.save(preview_path)
    return preview_path


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


def _build_uploaded_sample(upload_id: str, file_name: str) -> ProductSampleResponse:
    return ProductSampleResponse(
        id=upload_id,
        title=Path(file_name).stem.replace("_", " ").replace("-", " ").strip() or "Uploaded score",
        subtitle="Uploaded score image",
        document_name=upload_id,
        preview_image_url=f"/product/uploads/{upload_id}/image",
        description="A user-uploaded score processed through the Melodious upload transcription flow.",
        tags=["Uploaded", "Image", "Prototype"],
    )


def _build_response_from_payload(
    sample: ProductSampleResponse,
    payload: dict,
    download_prefix: str,
    initial_notices: list[str] | None = None,
) -> ProductTranscriptionResponse:
    """Run assembly/export on one detector payload and wrap it for the product UI."""
    notices = list(initial_notices or [])

    assemble_response = assemble_from_request(
        AssembleRequest(
            payload=payload,
            payload_kind="generic",
            assembly_mode="auto",
        )
    )
    musicxml_response = export_from_request(
        MidiRequest(
            payload=payload,
            output_format="musicxml",
            payload_kind="generic",
            assembly_mode="auto",
            document_name=sample.document_name,
            title=sample.title,
        )
    )
    midi_response = export_from_request(
        MidiRequest(
            payload=payload,
            output_format="midi",
            payload_kind="generic",
            assembly_mode="auto",
            document_name=sample.document_name,
            title=sample.title,
        )
    )

    for warning in assemble_response.warnings + musicxml_response.warnings + midi_response.warnings:
        if warning not in notices:
            notices.append(warning)

    summary = ProductTranscriptionSummaryResponse(
        detection_count=assemble_response.detection_count,
        note_count=assemble_response.assembly_summary.note_count,
        clef_count=assemble_response.assembly_summary.clef_count,
        rest_count=assemble_response.assembly_summary.rest_count,
        unmatched_count=assemble_response.assembly_summary.unmatched_count,
    )

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
        downloads=ProductDownloadsResponse(
            musicxml=ProductDownloadResponse(
                ready=True,
                url=f"{download_prefix}/musicxml",
                file_name=f"{sample.document_name}.musicxml",
                content_type=musicxml_response.content_type,
            ),
            midi=ProductDownloadResponse(
                ready=True,
                url=f"{download_prefix}/midi",
                file_name=f"{sample.document_name}.mid",
                content_type=midi_response.content_type,
            ),
        ),
        audio=ProductAudioResponse(
            playable=True,
            source_url=f"{download_prefix}/midi",
            format="midi",
            message="MIDI playback uses the exported file for this transcription.",
        ),
        feature_flags=build_product_feature_flags(),
        notices=notices,
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


def transcribe_uploaded_image(file_name: str, image_bytes: bytes) -> ProductTranscriptionResponse:
    """Save one uploaded score image and run the upload transcription flow."""
    extension = Path(file_name).suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Please upload a PNG, JPG, JPEG, TIF, or TIFF score image.")

    upload_id = f"upload-{uuid4().hex}"
    upload_dir = UPLOAD_ROOT / upload_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    image_path = upload_dir / f"score{extension}"

    try:
        with Image.open(__import__("io").BytesIO(image_bytes)) as image:
            image.convert("RGB").save(image_path)
    except UnidentifiedImageError as exc:
        raise HTTPException(status_code=400, detail="The uploaded file could not be read as an image.") from exc

    payload, notices = build_detection_payload_for_image(image_path)
    sample = _build_uploaded_sample(upload_id, file_name)
    response = _build_response_from_payload(
        sample=sample,
        payload=payload,
        download_prefix=f"/product/uploads/{upload_id}/downloads",
        initial_notices=notices,
    )

    _UPLOAD_RESULTS[upload_id] = {
        "image_path": image_path,
        "payload": payload,
        "sample": sample,
    }
    return response


def get_uploaded_image_path(upload_id: str) -> Path:
    result = _UPLOAD_RESULTS.get(upload_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown upload: {upload_id}")
    return result["image_path"]


def build_uploaded_download_asset(upload_id: str, output_format: str) -> tuple[bytes, str, str]:
    """Return bytes, MIME type, and filename for one uploaded transcription export."""
    result = _UPLOAD_RESULTS.get(upload_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Unknown upload: {upload_id}")

    sample: ProductSampleResponse = result["sample"]
    export_response = export_from_request(
        MidiRequest(
            payload=result["payload"],
            output_format=output_format,
            payload_kind="generic",
            assembly_mode="auto",
            document_name=sample.document_name,
            title=sample.title,
        )
    )

    if output_format == "musicxml":
        return (
            export_response.content.encode("utf-8"),
            export_response.content_type,
            f"{sample.document_name}.musicxml",
        )

    return (
        base64.b64decode(export_response.content),
        export_response.content_type,
        f"{sample.document_name}.mid",
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
