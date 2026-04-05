"""FastAPI app for the Week 2 Melodious backend skeleton."""

from fastapi import FastAPI, HTTPException

from src.api.models import (
    AssembleRequest,
    AssembleResponse,
    HealthResponse,
    MidiRequest,
    MidiResponse,
)
from src.api.service import assemble_from_request, export_from_request


app = FastAPI(
    title="Melodious Backend",
    version="0.3.0",
    description="Week 3 FastAPI service for graph assembly plus MusicXML/MIDI export.",
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return a minimal service-health payload."""
    return HealthResponse(
        status="ok",
        service="melodious-backend",
        stage="v0.3",
    )


@app.post("/assemble", response_model=AssembleResponse)
def assemble_graph(request: AssembleRequest):
    """Build graph outputs from one detector payload."""
    try:
        return assemble_from_request(request)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/midi", response_model=MidiResponse)
def export_score(request: MidiRequest):
    """Export one detector payload as inline MusicXML or base64 MIDI."""
    try:
        return export_from_request(request)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
