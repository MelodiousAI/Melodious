"""FastAPI app for the Melodious backend and Week 5 product facade."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.models import (
    AssembleRequest,
    AssembleResponse,
    HealthResponse,
    MidiRequest,
    MidiResponse,
)
from src.api.product_routes import router as product_router
from src.api.service import assemble_from_request, build_health_response, export_from_request


app = FastAPI(
    title="Melodious Backend",
    version="0.5.0",
    description="FastAPI service for the Week 4 engineering contract plus the Week 5 public product facade.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(product_router)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return service health plus Week 4 GNN readiness details."""
    return build_health_response()


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
