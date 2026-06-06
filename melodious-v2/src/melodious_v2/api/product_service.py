"""Real Melodious V2 product upload service.

This module turns an uploaded sheet-music image into actual transcription
artifacts using the trained V2 note-extraction path
(:func:`melodious_v2.omr.note_extraction.extract_notes_from_image`).

Design notes
------------
* Extraction is CPU-bound and can take tens of seconds, so each upload runs in a
  background worker thread. Callers poll the job by ``job_id``.
* A small in-process semaphore serializes heavy extraction work so concurrent
  uploads queue cleanly instead of thrashing CPU/RAM. Queued jobs report
  ``status = "queued"`` until a worker slot frees up.
* Generated artifacts are written under an ignored app run directory
  (``runs/app/uploads/{job_id}/``) and served back through the API.
* This path is explicitly a demo transcription, not an official metric run. The
  honesty disclaimer is attached to every response.
"""

from __future__ import annotations

import os
import threading
import time
import uuid
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from melodious_v2.api.product_models import (
    ModelAvailability,
    ModelProvenance,
    NoteEvent,
    ProductCounts,
    ProductSample,
    ProductTranscription,
    QualitySummary,
)
from melodious_v2.omr.note_extraction import (
    ExtractedNote,
    ExtractedRest,
    ExtractionResult,
    extract_notes_from_image,
    write_midi,
)

# melodious-v2 repository root: api -> melodious_v2 -> src -> melodious-v2
REPO_ROOT = Path(__file__).resolve().parents[3]

ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
IMAGE_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
}

# General MIDI program numbers for the instrument selector. The default app
# instrument is Piano, which is a more natural default than the extractor's
# violin-leaning default.
INSTRUMENT_PROGRAMS = {
    "Piano": 0,
    "Electric Piano": 4,
    "Organ": 19,
    "Guitar": 24,
    "Violin": 40,
    "Strings": 48,
    "Flute": 73,
    "Music Box": 10,
}
DEFAULT_INSTRUMENT = "Piano"

STAGE_LABELS = {
    "queued": "Queued",
    "uploading": "Receiving upload",
    "reading_image": "Reading image",
    "detecting_staff": "Detecting staff systems",
    "detecting_symbols": "Detecting symbols",
    "detecting_thin_symbols": "Detecting thin symbols (tiled)",
    "building_graph": "Building note graph (GNN)",
    "assembling_events": "Assembling musical events",
    "exporting": "Exporting MusicXML & MIDI",
    "rendering": "Rendering playback",
    "complete": "Complete",
    "failed": "Failed",
}


def _model_root() -> Path:
    raw = os.getenv("MELODIOUS_MODEL_ROOT")
    return Path(raw) if raw else REPO_ROOT / "artifacts" / "models"


def _upload_root() -> Path:
    raw = os.getenv("MELODIOUS_APP_UPLOAD_ROOT")
    root = Path(raw) if raw else REPO_ROOT / "runs" / "app" / "uploads"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def resolve_detector_checkpoint() -> Path | None:
    """Resolve the default full-page notehead detector checkpoint."""
    return _first_existing(
        [
            _model_root() / "note_extraction_default_fullpage" / "best.pt",
            REPO_ROOT
            / "runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/best.pt",
            _model_root() / "detection_136class_yolov8m_v1" / "best.pt",
        ]
    )


def resolve_thin_symbol_checkpoint() -> Path | None:
    """Resolve the default tiled thin-symbol (stem/beam/flag) checkpoint."""
    return _first_existing(
        [
            _model_root() / "note_extraction_tiled_stem_pilot" / "best.pt",
            REPO_ROOT
            / "runs/detection/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/ultralytics/train/weights/best.pt",
        ]
    )


def resolve_gnn_checkpoint() -> Path | None:
    """Resolve the legacy GNN relationship checkpoint, honoring env override."""
    raw = os.getenv("MELODIOUS_GNN_CHECKPOINT")
    if raw:
        path = Path(raw)
        return path if path.exists() else None
    default = REPO_ROOT.parent / "outputs" / "gnn_checkpoint.pt"
    return default if default.exists() else None


def model_availability_snapshot() -> dict[str, bool]:
    """Report which model artifacts are currently available on disk."""
    return {
        "full_page_detector": resolve_detector_checkpoint() is not None,
        "tiled_detector": resolve_thin_symbol_checkpoint() is not None,
        "gnn": resolve_gnn_checkpoint() is not None,
    }


def midi_program_for_instrument(instrument: str | None) -> int:
    return INSTRUMENT_PROGRAMS.get(instrument or DEFAULT_INSTRUMENT, INSTRUMENT_PROGRAMS[DEFAULT_INSTRUMENT])


def _pitch_label(step: str, alter: int, octave: int) -> str:
    if alter > 0:
        accidental = "#" * alter
    elif alter < 0:
        accidental = "b" * abs(alter)
    else:
        accidental = ""
    return f"{step}{accidental}{octave}"


@dataclass
class _Job:
    """In-memory record for one upload transcription job."""

    transcription: ProductTranscription
    job_dir: Path
    image_path: Path
    instrument: str
    events: list = field(default_factory=list)
    midi_cache: dict[str, Path] = field(default_factory=dict)
    bundle_path: Path | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)


_JOBS: dict[str, _Job] = {}
_JOBS_LOCK = threading.Lock()


def _max_concurrency() -> int:
    raw = os.getenv("MELODIOUS_APP_MAX_CONCURRENCY")
    try:
        value = int(raw) if raw else 1
    except ValueError:
        value = 1
    return max(1, value)


_EXTRACTION_SEMAPHORE = threading.BoundedSemaphore(_max_concurrency())


def _artifact_base(job_id: str) -> str:
    return f"/product/jobs/{job_id}/artifacts"


def _set_stage(job: _Job, stage: str, progress: float) -> None:
    with job.lock:
        job.transcription.stage = stage
        job.transcription.stage_label = STAGE_LABELS.get(stage, stage.replace("_", " ").title())
        job.transcription.progress = max(job.transcription.progress, round(float(progress), 4))
        if stage not in {"complete", "failed", "queued"}:
            job.transcription.status = "processing"
        job.transcription.updated_at = time.time()


def _media_type_for_image(path: Path) -> str:
    return IMAGE_MEDIA_TYPES.get(path.suffix.lower(), "application/octet-stream")


def _build_quality(counts: ProductCounts, result: ExtractionResult, gnn_used: bool) -> QualitySummary:
    """Derive a presentation-only confidence summary from counts and warnings.

    This is intentionally heuristic and is NEVER reported as a measured metric.
    """
    reasons: list[str] = []
    notes = counts.notes
    if notes <= 0:
        return QualitySummary(
            label="low",
            score=0.0,
            headline="No notes were extracted",
            reasons=["The detector did not return usable noteheads for this page."],
        )

    stem_ratio = counts.stem_confirmed_notes / notes if notes else 0.0
    score = 0.0
    score += 0.30 if counts.staff_systems > 0 else 0.0
    score += 0.25 * min(1.0, notes / 24.0)
    score += 0.25 * stem_ratio
    score += 0.20 if gnn_used else 0.0
    score = round(min(1.0, score), 3)

    if counts.staff_systems > 0:
        reasons.append(f"Detected {counts.staff_systems} staff systems and {notes} notes.")
    reasons.append(f"{counts.stem_confirmed_notes}/{notes} notes have detector-confirmed stems.")
    if gnn_used:
        reasons.append(f"GNN contributed {counts.relationship_count} note relationships for rhythm.")
    else:
        reasons.append("GNN relationship model was not applied; rhythm relies on geometry only.")
    if counts.rests:
        reasons.append(f"Recovered {counts.rests} rests.")
    if result.warnings:
        reasons.append(f"{len(result.warnings)} processing note(s) to review.")

    if score >= 0.75:
        label, headline = "high", "Strong, confident transcription"
    elif score >= 0.45:
        label, headline = "review", "Usable transcription — review recommended"
    else:
        label, headline = "low", "Low-confidence transcription"
    return QualitySummary(label=label, score=score, headline=headline, reasons=reasons)


def _note_events_from_result(result: ExtractionResult) -> list[NoteEvent]:
    events: list[NoteEvent] = []
    for event in result.events:
        if isinstance(event, ExtractedRest):
            events.append(
                NoteEvent(
                    order=event.order,
                    event_type="rest",
                    staff_index=event.staff_index,
                    onset_quarter=round(event.onset_quarter, 4),
                    quarter_length=round(event.quarter_length, 4),
                    dotted=event.dotted,
                    rhythm_source=event.rhythm_source,
                    source=event.source,
                    confidence=round(event.confidence, 4),
                )
            )
        elif isinstance(event, ExtractedNote):
            events.append(
                NoteEvent(
                    order=event.order,
                    event_type="note",
                    staff_index=event.staff_index,
                    onset_quarter=round(event.onset_quarter, 4),
                    quarter_length=round(event.quarter_length, 4),
                    dotted=event.dotted,
                    rhythm_source=event.rhythm_source,
                    source=event.source,
                    confidence=round(event.confidence, 4),
                    step=event.step,
                    octave=event.octave,
                    alter=event.alter,
                    midi_pitch=event.midi_pitch,
                    pitch_label=_pitch_label(event.step, event.alter, event.octave),
                    pitch_source=event.pitch_source,
                    stem_detected=event.stem_detected,
                    slur_start_count=len(event.slur_starts),
                    slur_stop_count=len(event.slur_stops),
                    tie_start_count=len(event.tie_starts),
                    tie_stop_count=len(event.tie_stops),
                )
            )
    return events


def _finalize_success(job: _Job, result: ExtractionResult) -> None:
    notes = result.notes
    counts = ProductCounts(
        staff_systems=len(result.staff_systems),
        events=len(result.events),
        notes=len(notes),
        rests=sum(1 for event in result.events if isinstance(event, ExtractedRest)),
        dotted_notes=sum(1 for note in notes if note.dotted),
        stem_confirmed_notes=sum(1 for note in notes if note.stem_detected),
        slur_starts=sum(len(note.slur_starts) for note in notes),
        tie_starts=sum(len(note.tie_starts) for note in notes),
        relationship_count=result.relationship_count,
    )
    assembly_applied = "none"
    gnn_used = False
    if result.assembly_mode:
        assembly_applied = str(result.assembly_mode.get("applied_mode", "none"))
        gnn_used = bool(result.assembly_mode.get("inference_ran"))
    provenance = ModelProvenance(
        extractor_mode=result.extractor_mode,
        detector_checkpoint=result.detector_checkpoint,
        thin_symbol_checkpoint=result.thin_symbol_checkpoint,
        gnn_checkpoint=result.gnn_checkpoint,
        assembly_mode=assembly_applied,
    )
    availability = ModelAvailability(
        full_page_detector=result.detector_checkpoint is not None
        and result.extractor_mode.startswith("yolo"),
        tiled_detector=result.thin_symbol_checkpoint is not None
        and "tiled_thin_symbols" in result.extractor_mode,
        gnn=gnn_used,
    )

    base = _artifact_base(job.transcription.job_id)
    artifacts = result.artifacts
    detector_payload_url = (
        f"{base}/detector_payload" if artifacts and artifacts.detector_payload_json else None
    )
    relationships_url = f"{base}/relationships" if artifacts and artifacts.relationships_json else None

    job.events = list(result.events)

    with job.lock:
        transcription = job.transcription
        transcription.status = "complete"
        transcription.stage = "complete"
        transcription.stage_label = STAGE_LABELS["complete"]
        transcription.progress = 1.0
        transcription.updated_at = time.time()
        transcription.image_width = result.image_width
        transcription.image_height = result.image_height
        transcription.key_fifths = result.key_fifths
        transcription.counts = counts
        transcription.model_provenance = provenance
        transcription.model_availability = availability
        transcription.quality = _build_quality(counts, result, gnn_used)
        transcription.note_events = _note_events_from_result(result)
        transcription.warnings = list(result.warnings or [])
        transcription.original_image_url = f"{base}/original"
        transcription.overlay_image_url = f"{base}/overlay"
        transcription.musicxml_url = f"{base}/musicxml"
        transcription.midi_url = f"{base}/midi"
        transcription.notes_json_url = f"{base}/notes"
        transcription.detector_payload_url = detector_payload_url
        transcription.relationships_url = relationships_url
        transcription.bundle_url = f"{base}/bundle"


def _run_extraction(job_id: str) -> None:
    job = _get_job(job_id)
    if job is None:
        return
    _set_stage(job, "queued", 0.01)
    with _EXTRACTION_SEMAPHORE:
        _set_stage(job, "uploading", 0.02)

        def progress_callback(stage: str, fraction: float) -> None:
            _set_stage(job, stage, fraction)

        try:
            result = extract_notes_from_image(
                image_path=job.image_path,
                output_dir=job.job_dir,
                checkpoint_path=resolve_detector_checkpoint(),
                thin_symbol_checkpoint_path=resolve_thin_symbol_checkpoint(),
                gnn_checkpoint_path=resolve_gnn_checkpoint(),
                snapshot_live_checkpoint=False,
                device=os.getenv("MELODIOUS_APP_DEVICE", "cpu"),
                title=job.transcription.filename or "Melodious V2 Transcription",
                progress_callback=progress_callback,
            )
        except Exception as exc:  # pragma: no cover - runtime/model failure path
            with job.lock:
                job.transcription.status = "failed"
                job.transcription.stage = "failed"
                job.transcription.stage_label = STAGE_LABELS["failed"]
                job.transcription.error = f"Extraction failed: {exc}"
                job.transcription.updated_at = time.time()
            return

    # Re-render MIDI with the selected instrument's GM program so playback and
    # download reflect the chosen instrument.
    try:
        program = midi_program_for_instrument(job.instrument)
        if program != 40 and result.artifacts is not None:
            write_midi(result.events, Path(result.artifacts.midi_path), program=program)
    except Exception:  # pragma: no cover - non-fatal instrument re-render
        pass

    _finalize_success(job, result)


def _get_job(job_id: str) -> _Job | None:
    with _JOBS_LOCK:
        return _JOBS.get(job_id)


def start_image_transcription(
    *,
    image_bytes: bytes,
    filename: str | None,
    instrument: str | None = None,
) -> ProductTranscription:
    """Persist an uploaded image and launch a background transcription job."""
    if not image_bytes:
        raise ValueError("Uploaded image was empty.")

    safe_name = Path(filename or "upload.png").name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_IMAGE_SUFFIXES:
        raise ValueError(
            f"Unsupported image type '{suffix or 'unknown'}'. "
            f"Supported types: {', '.join(sorted(ALLOWED_IMAGE_SUFFIXES))}."
        )

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    job_dir = _upload_root() / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    image_path = job_dir / f"original{suffix}"
    image_path.write_bytes(image_bytes)

    now = time.time()
    instrument_name = instrument if instrument in INSTRUMENT_PROGRAMS else DEFAULT_INSTRUMENT
    transcription = ProductTranscription(
        job_id=job_id,
        status="queued",
        stage="queued",
        stage_label=STAGE_LABELS["queued"],
        progress=0.0,
        filename=safe_name,
        created_at=now,
        updated_at=now,
    )
    job = _Job(
        transcription=transcription,
        job_dir=job_dir,
        image_path=image_path,
        instrument=instrument_name,
    )
    with _JOBS_LOCK:
        _JOBS[job_id] = job

    thread = threading.Thread(target=_run_extraction, args=(job_id,), daemon=True)
    thread.start()
    return transcription.model_copy(deep=True)


def get_transcription_job(job_id: str) -> ProductTranscription | None:
    """Return the current state of a transcription job."""
    job = _get_job(job_id)
    if job is None:
        return None
    with job.lock:
        return job.transcription.model_copy(deep=True)


def _ensure_bundle(job: _Job) -> Path | None:
    if job.bundle_path and job.bundle_path.exists():
        return job.bundle_path
    result_files = [
        job.image_path,
        job.job_dir / f"{job.image_path.stem}_notes_overlay.png",
        job.job_dir / f"{job.image_path.stem}_notes.musicxml",
        job.job_dir / f"{job.image_path.stem}_notes.mid",
        job.job_dir / f"{job.image_path.stem}_notes.json",
        job.job_dir / f"{job.image_path.stem}_detector_payload.json",
        job.job_dir / f"{job.image_path.stem}_relationships.json",
    ]
    bundle_path = job.job_dir / "melodious_v2_result_bundle.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in result_files:
            if path.exists():
                archive.write(path, arcname=path.name)
    job.bundle_path = bundle_path
    return bundle_path


def _regenerate_midi(job: _Job, instrument: str, tempo_bpm: int) -> Path | None:
    program = midi_program_for_instrument(instrument)
    cache_key = f"{instrument}@{tempo_bpm}"
    cached = job.midi_cache.get(cache_key)
    if cached and cached.exists():
        return cached
    if not job.events:
        return None
    safe_instrument = instrument.replace(" ", "_")
    out_path = job.job_dir / f"{job.image_path.stem}_notes_{safe_instrument}_{tempo_bpm}bpm.mid"
    write_midi(job.events, out_path, tempo_bpm=tempo_bpm, program=program)
    job.midi_cache[cache_key] = out_path
    return out_path


def get_artifact_response(
    job_id: str,
    name: str,
    instrument: str | None = None,
    tempo_bpm: int | None = None,
) -> tuple[Path, str, str] | None:
    """Resolve an artifact request to ``(path, media_type, download_name)``.

    Returns ``None`` when the job or artifact is unavailable. Raises ``KeyError``
    for an unknown artifact name.
    """
    job = _get_job(job_id)
    if job is None:
        return None
    stem = job.image_path.stem
    job_dir = job.job_dir

    if name == "original":
        path = job.image_path
        return (path, _media_type_for_image(path), path.name) if path.exists() else None
    if name == "overlay":
        path = job_dir / f"{stem}_notes_overlay.png"
        return (path, "image/png", "overlay.png") if path.exists() else None
    if name == "musicxml":
        path = job_dir / f"{stem}_notes.musicxml"
        return (
            (path, "application/vnd.recordare.musicxml+xml", "transcription.musicxml")
            if path.exists()
            else None
        )
    if name == "midi":
        want_instrument = instrument if instrument in INSTRUMENT_PROGRAMS else None
        want_tempo = int(tempo_bpm) if tempo_bpm and 20 <= int(tempo_bpm) <= 300 else None
        needs_custom = (want_instrument and want_instrument != DEFAULT_INSTRUMENT) or (
            want_tempo and want_tempo != 96
        )
        if needs_custom:
            with job.lock:
                regenerated = _regenerate_midi(job, want_instrument or DEFAULT_INSTRUMENT, want_tempo or 96)
            if regenerated is not None:
                label = (want_instrument or DEFAULT_INSTRUMENT).replace(" ", "_")
                return regenerated, "audio/midi", f"transcription_{label}_{want_tempo or 96}bpm.mid"
        path = job_dir / f"{stem}_notes.mid"
        return (path, "audio/midi", "transcription.mid") if path.exists() else None
    if name == "notes":
        path = job_dir / f"{stem}_notes.json"
        return (path, "application/json", "notes.json") if path.exists() else None
    if name == "detector_payload":
        path = job_dir / f"{stem}_detector_payload.json"
        return (path, "application/json", "detector_payload.json") if path.exists() else None
    if name == "relationships":
        path = job_dir / f"{stem}_relationships.json"
        return (path, "application/json", "relationships.json") if path.exists() else None
    if name == "bundle":
        with job.lock:
            bundle = _ensure_bundle(job)
        return (bundle, "application/zip", "melodious_v2_result_bundle.zip") if bundle else None

    raise KeyError(f"Unknown artifact: {name}")


# Curated demo samples. Files live in the legacy parent project workspace and are
# only offered when present, so the demo gallery never advertises missing files.
_CURATED_SAMPLES = [
    {
        "sample_id": "sad-romance",
        "title": "Sad Romance",
        "subtitle": "Expressive piano ballad",
        "description": "Multi-system romantic piano score with slurs and dotted rhythm.",
        "path": REPO_ROOT.parent / "sad_romance_clearer_smooth.png",
    },
    {
        "sample_id": "espresso",
        "title": "Espresso",
        "subtitle": "Dense pop arrangement",
        "description": "Busy multi-staff screenshot with beams, rests, slurs, and ties.",
        "path": REPO_ROOT.parent / "Screenshot 2026-06-06 001627.png",
    },
    {
        "sample_id": "fur-elise",
        "title": "Für Elise",
        "subtitle": "Beethoven classic",
        "description": "Classic recital page exercising accidentals and rapid runs.",
        "path": REPO_ROOT.parent / "image(305).png",
    },
]


def list_product_samples() -> list[ProductSample]:
    """Return curated demo samples, flagged by whether their file exists."""
    samples: list[ProductSample] = []
    for entry in _CURATED_SAMPLES:
        samples.append(
            ProductSample(
                sample_id=entry["sample_id"],
                title=entry["title"],
                subtitle=entry["subtitle"],
                description=entry["description"],
                available=Path(entry["path"]).exists(),
            )
        )
    return samples


def start_sample_transcription(sample_id: str, instrument: str | None = None) -> ProductTranscription:
    """Launch a transcription job from a curated demo sample image."""
    entry = next((item for item in _CURATED_SAMPLES if item["sample_id"] == sample_id), None)
    if entry is None:
        raise KeyError(f"Unknown sample_id: {sample_id}")
    path = Path(entry["path"])
    if not path.exists():
        raise FileNotFoundError(f"Sample image is not available on this host: {entry['title']}")
    return start_image_transcription(
        image_bytes=path.read_bytes(),
        filename=path.name,
        instrument=instrument,
    )


def list_instruments() -> list[str]:
    """Return the instrument names available to the instrument selector."""
    return list(INSTRUMENT_PROGRAMS.keys())
