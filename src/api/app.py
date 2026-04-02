"""FastAPI app for the Week 2 Melodious backend skeleton."""

from fastapi import FastAPI, HTTPException

from src.api.models import (
    AssembleRequest,
    AssembleResponse,
    HealthResponse,
    MidiRequest,
    MidiResponse,
)
from src.api.service import assemble_from_request, build_midi_placeholder_response


app = FastAPI(
    title="Melodious Backend",
    version="0.2.0",
    description="Week 2 FastAPI skeleton for graph assembly and future MIDI export.",
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return a minimal service-health payload."""
    return HealthResponse(
        status="ok",
        service="melodious-backend",
        stage="v0.2",
    )


@app.post("/assemble", response_model=AssembleResponse)
def assemble_graph(request: AssembleRequest):
    """Build graph outputs from one detector payload."""
    try:
        return assemble_from_request(request)
    except (FileNotFoundError, KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/midi", response_model=MidiResponse, status_code=501)
def midi_placeholder(_request: MidiRequest):
    """Reserve the MIDI endpoint for the later export pipeline wiring."""
    return build_midi_placeholder_response()
