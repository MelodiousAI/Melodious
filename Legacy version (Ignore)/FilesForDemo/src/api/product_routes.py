"""Public-facing routes for the Week 5 musician product experience."""

from __future__ import annotations

from typing import Literal
from urllib.parse import unquote

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import FileResponse

from src.api.product_models import (
    ProductConfigResponse,
    ProductImageClassificationResponse,
    ProductSamplesResponse,
    ProductTranscribeRequest,
    ProductTranscriptionResponse,
)
from src.api.product_service import (
    build_product_config,
    build_product_download_asset,
    classify_uploaded_score_image,
    get_product_sample_image_path,
    list_product_samples,
    transcribe_product_sample,
)


router = APIRouter(prefix="/product", tags=["product"])


@router.get("/config", response_model=ProductConfigResponse)
def get_product_config():
    """Return configuration for the Week 5 public frontend."""
    return build_product_config()


@router.get("/samples", response_model=ProductSamplesResponse)
def get_product_samples():
    """Return the curated public sample catalog."""
    return ProductSamplesResponse(items=list_product_samples())


@router.post("/classify-image", response_model=ProductImageClassificationResponse)
async def classify_uploaded_image(
    request: Request,
    confidence: float = Query(default=0.25, ge=0.01, le=0.95),
    max_detections: int = Query(default=100, ge=1, le=300),
):
    """Run detector-only classification on one uploaded score image."""
    content_type = request.headers.get("content-type", "")
    if not content_type.lower().startswith("image/"):
        return Response(
            content='{"detail":"Upload an image file such as PNG or JPG."}',
            media_type="application/json",
            status_code=400,
        )

    raw_file_name = request.headers.get("x-file-name", "uploaded-score")
    file_name = unquote(raw_file_name)
    content = await request.body()

    return classify_uploaded_score_image(
        file_name=file_name,
        content=content,
        confidence_threshold=confidence,
        max_detections=max_detections,
    )


@router.get("/samples/{sample_id}/image")
def get_product_sample_image(sample_id: str):
    """Return the repo-local preview image for one curated sample."""
    image_path = get_product_sample_image_path(sample_id)
    return FileResponse(image_path, media_type="image/png")


@router.get("/samples/{sample_id}/downloads/{output_format}")
def download_product_sample_asset(sample_id: str, output_format: Literal["musicxml", "midi"]):
    """Return one public export asset for a curated sample."""
    content, content_type, file_name = build_product_download_asset(sample_id, output_format)
    headers = {"Content-Disposition": f'attachment; filename="{file_name}"'}
    return Response(content=content, media_type=content_type, headers=headers)


@router.post("/transcribe", response_model=ProductTranscriptionResponse)
def transcribe_product(request: ProductTranscribeRequest):
    """Run the public sample-based Week 5 transcription flow."""
    return transcribe_product_sample(request.sample_id)
