"""Stateful in-memory product service for local demo and tests."""

from __future__ import annotations

import base64
import os
import uuid
from dataclasses import asdict

from melodious_v2 import __version__
from melodious_v2.api.models import (
    AssemblyModeResponse,
    HealthResponse,
    SampleRecord,
    TranscriptionRequest,
    TranscriptionResponse,
    VersionResponse,
)
from melodious_v2.assembly.service import assemble_payload
from melodious_v2.contracts import (
    ArtifactRecord,
    DetectionV2,
    DetectorPayloadV2,
    ImageSize,
    NormalizedBBox,
    PixelBBox,
    SCHEMA_VERSION,
)
from melodious_v2.detector.heuristic import detect_image_bytes
from melodious_v2.export.musicxml import (
    minimal_midi_base64,
    payload_to_musicxml,
    validate_musicxml,
)
from melodious_v2.taxonomies import DEEPSCORES_136_NAME_TO_ID
from melodious_v2.utils import sha256_bytes


class TranscriptionStore:
    """Small in-memory store for local/demo transcriptions."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict] = {}

    def save(self, job_id: str, record: dict) -> None:
        self._jobs[job_id] = record

    def get(self, job_id: str) -> dict | None:
        return self._jobs.get(job_id)


STORE = TranscriptionStore()


def _sample_payload() -> DetectorPayloadV2:
    note_id = DEEPSCORES_136_NAME_TO_ID["noteheadBlackOnLine"]
    stem_id = DEEPSCORES_136_NAME_TO_ID["stem"]
    beam_id = DEEPSCORES_136_NAME_TO_ID["beam"]
    return DetectorPayloadV2(
        run_id="sample_bootstrap_001",
        model_id="sample_payload",
        taxonomy_id="deepscores_136",
        image_size=ImageSize(width=1200, height=800),
        detections=[
            DetectionV2(
                class_id=note_id,
                class_name="noteheadBlackOnLine",
                confidence=1.0,
                bbox=NormalizedBBox(x_center=0.40, y_center=0.52, width=0.025, height=0.035),
                bbox_pixels=PixelBBox(x1=465, y1=402, x2=495, y2=430),
            ),
            DetectionV2(
                class_id=stem_id,
                class_name="stem",
                confidence=1.0,
                bbox=NormalizedBBox(x_center=0.425, y_center=0.45, width=0.006, height=0.16),
                bbox_pixels=PixelBBox(x1=506, y1=296, x2=514, y2=424),
            ),
            DetectionV2(
                class_id=beam_id,
                class_name="beam",
                confidence=1.0,
                bbox=NormalizedBBox(x_center=0.48, y_center=0.36, width=0.15, height=0.02),
                bbox_pixels=PixelBBox(x1=486, y1=280, x2=666, y2=296),
            ),
        ],
    )


SAMPLES = {
    "sample-notation-1": SampleRecord(
        sample_id="sample-notation-1",
        title="Compact Notation Sample",
        description="Tiny V2 contract sample with notehead, stem, and beam symbols.",
        payload=_sample_payload(),
    )
}


def health_response() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="melodious-v2-api",
        version=__version__,
        environment=os.getenv("MELODIOUS_ENV", "local"),
        detector_modes=["heuristic_bootstrap", "onnx_detector_pending"],
        assembly_modes=["auto", "heuristic", "gnn"],
    )


def version_response() -> VersionResponse:
    return VersionResponse(
        version=__version__,
        schema_version=SCHEMA_VERSION,
        detector_taxonomy="deepscores_136",
        semantic_taxonomy="semantic_omr_v2",
    )


def list_samples() -> list[SampleRecord]:
    return list(SAMPLES.values())


def _payload_from_request(request: TranscriptionRequest, job_id: str) -> tuple[str, DetectorPayloadV2, list[str]]:
    warnings: list[str] = []
    if request.sample_id:
        sample = SAMPLES.get(request.sample_id)
        if sample is None:
            raise KeyError(f"Unknown sample_id: {request.sample_id}")
        return "sample_payload", sample.payload, warnings

    if request.image_base64:
        try:
            image_bytes = base64.b64decode(request.image_base64, validate=True)
        except Exception as exc:
            raise ValueError("image_base64 must be valid base64 image bytes.") from exc
        warnings.append(
            "Upload used heuristic_bootstrap detector. Do not report this as trained model performance."
        )
        return "heuristic_bootstrap", detect_image_bytes(image_bytes, run_id=job_id), warnings

    raise ValueError("Provide either sample_id or image_base64.")


def create_transcription(request: TranscriptionRequest) -> TranscriptionResponse:
    job_id = f"tr_{uuid.uuid4().hex[:12]}"
    detector_mode, payload, warnings = _payload_from_request(request, job_id)
    assembly_mode, relationships = assemble_payload(payload, request.requested_assembly_mode)
    musicxml = payload_to_musicxml(payload, relationships, title=request.filename or "Melodious V2 Export")
    if not validate_musicxml(musicxml):
        raise ValueError("Generated MusicXML failed XML validation.")
    midi_b64 = minimal_midi_base64()

    artifacts = [
        ArtifactRecord(
            artifact_id=f"{job_id}:musicxml",
            artifact_type="musicxml",
            content_type="application/vnd.recordare.musicxml+xml",
            sha256=sha256_bytes(musicxml.encode("utf-8")),
            uri=f"/transcriptions/{job_id}/artifacts/musicxml",
        ),
        ArtifactRecord(
            artifact_id=f"{job_id}:midi",
            artifact_type="midi",
            content_type="audio/midi",
            sha256=sha256_bytes(base64.b64decode(midi_b64)),
            uri=f"/transcriptions/{job_id}/artifacts/midi",
        ),
    ]
    mode_response = AssemblyModeResponse(**asdict(assembly_mode))
    all_warnings = warnings + assembly_mode.warnings
    response = TranscriptionResponse(
        job_id=job_id,
        status="complete",
        detector_mode=detector_mode,
        assembly_mode=mode_response,
        detection_count=len(payload.detections),
        relationship_count=len(relationships),
        payload=payload,
        artifacts=artifacts,
        metric_provenance={
            "metric_claim": "none",
            "reason": "transcription API response is not an evaluation run",
        },
        warnings=all_warnings,
    )
    STORE.save(
        job_id,
        {
            "response": response,
            "musicxml": musicxml,
            "midi_base64": midi_b64,
        },
    )
    return response


def get_transcription(job_id: str) -> TranscriptionResponse | None:
    record = STORE.get(job_id)
    if record is None:
        return None
    return record["response"]


def get_artifact(job_id: str, artifact_format: str) -> tuple[bytes, str] | None:
    record = STORE.get(job_id)
    if record is None:
        return None
    if artifact_format == "musicxml":
        return record["musicxml"].encode("utf-8"), "application/vnd.recordare.musicxml+xml"
    if artifact_format == "midi":
        return base64.b64decode(record["midi_base64"]), "audio/midi"
    raise KeyError(f"Unsupported artifact format: {artifact_format}")

