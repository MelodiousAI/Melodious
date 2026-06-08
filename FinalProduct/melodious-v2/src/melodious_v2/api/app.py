"""FastAPI application for Melodious V2."""

from __future__ import annotations

import os

from fastapi import FastAPI, File, Form, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from melodious_v2.api.models import (
    HealthResponse,
    SampleRecord,
    TranscriptionRequest,
    TranscriptionResponse,
    VersionResponse,
)
from melodious_v2.api.product_models import (
    ProductSample,
    ProductTranscription,
)
from melodious_v2.api.product_service import (
    get_artifact_response,
    get_transcription_job,
    list_instruments,
    list_product_samples,
    model_availability_snapshot,
    start_image_transcription,
    start_sample_transcription,
)
from melodious_v2.api.service import (
    create_transcription,
    get_artifact,
    get_transcription,
    health_response,
    list_samples,
    version_response,
)


def _cors_origins_from_env() -> list[str]:
    """Return allowed CORS origins for local and deployed frontends."""
    raw = os.getenv("MELODIOUS_CORS_ORIGINS")
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return ["http://localhost:5173", "http://127.0.0.1:5173"]


app = FastAPI(
    title="Melodious V2 API",
    version="0.1.0",
    description="Full-taxonomy cloud OMR API with strict metric provenance.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins_from_env(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return health_response()


@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return version_response()


@app.get("/samples", response_model=list[SampleRecord])
def samples() -> list[SampleRecord]:
    return list_samples()


@app.post("/transcriptions", response_model=TranscriptionResponse)
def transcriptions(request: TranscriptionRequest) -> TranscriptionResponse:
    try:
        return create_transcription(request)
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/transcriptions/{job_id}", response_model=TranscriptionResponse)
def transcription(job_id: str) -> TranscriptionResponse:
    response = get_transcription(job_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Transcription not found.")
    return response


@app.get("/transcriptions/{job_id}/artifacts/{artifact_format}")
def artifact(job_id: str, artifact_format: str) -> Response:
    try:
        artifact_result = get_artifact(job_id, artifact_format)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if artifact_result is None:
        raise HTTPException(status_code=404, detail="Transcription not found.")
    content, media_type = artifact_result
    return Response(content=content, media_type=media_type)


# ---------------------------------------------------------------------------
# Product upload app routes (real V2 note-extraction path)
# ---------------------------------------------------------------------------


@app.get("/product/models")
def product_models() -> dict:
    """Report which model artifacts are available for the real extraction path."""
    availability = model_availability_snapshot()
    return {
        "availability": availability,
        "instruments": list_instruments(),
        "ready": availability["full_page_detector"],
        "note": (
            "Uploaded transcriptions use the local trained YOLO + tiled + GNN "
            "extraction path. Results are demo transcriptions, not official metric runs."
        ),
    }


@app.get("/product/samples", response_model=list[ProductSample])
def product_samples() -> list[ProductSample]:
    return list_product_samples()


@app.post("/product/transcribe-image", response_model=ProductTranscription)
async def transcribe_image(
    file: UploadFile = File(...),
    instrument: str | None = Form(default=None),
) -> ProductTranscription:
    """Accept a multipart image upload and start a real V2 transcription job."""
    image_bytes = await file.read()
    try:
        return start_image_transcription(
            image_bytes=image_bytes,
            filename=file.filename,
            instrument=instrument,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/product/transcribe-sample", response_model=ProductTranscription)
def transcribe_sample(
    sample_id: str = Form(...),
    instrument: str | None = Form(default=None),
) -> ProductTranscription:
    """Start a transcription job from a curated demo sample image."""
    try:
        return start_sample_transcription(sample_id, instrument=instrument)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/product/jobs/{job_id}", response_model=ProductTranscription)
def product_job(job_id: str) -> ProductTranscription:
    """Return the current state/result of a product transcription job."""
    job = get_transcription_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


@app.get("/product/jobs/{job_id}/artifacts/{name}")
def product_artifact(
    job_id: str,
    name: str,
    download: bool = Query(default=False),
    instrument: str | None = Query(default=None),
    tempo_bpm: int | None = Query(default=None),
) -> FileResponse:
    """Serve a generated artifact file for a transcription job."""
    try:
        resolved = get_artifact_response(job_id, name, instrument=instrument, tempo_bpm=tempo_bpm)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if resolved is None:
        raise HTTPException(status_code=404, detail="Artifact not available.")
    path, media_type, download_name = resolved
    if download:
        return FileResponse(path, media_type=media_type, filename=download_name)
    return FileResponse(path, media_type=media_type)
