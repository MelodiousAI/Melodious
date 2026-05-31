"""FastAPI application for Melodious V2."""

from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from melodious_v2.api.models import (
    HealthResponse,
    SampleRecord,
    TranscriptionRequest,
    TranscriptionResponse,
    VersionResponse,
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
