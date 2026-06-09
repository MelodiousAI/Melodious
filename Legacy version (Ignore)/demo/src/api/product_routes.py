"""Public-facing routes for the Week 5 musician product experience."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Response
from fastapi.responses import FileResponse

from src.api.product_models import (
    ProductConfigResponse,
    ProductSamplesResponse,
    ProductTranscribeRequest,
    ProductTranscriptionResponse,
)
from src.api.product_service import (
    build_product_config,
    build_product_download_asset,
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
