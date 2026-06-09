"""Relationship assembly service with explicit fallback metadata."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from melodious_v2.contracts import DetectorPayloadV2


RELATIONSHIP_TYPES = [
    "no_relation",
    "stem_notehead",
    "beam_notegroup",
    "slur_phrase",
    "tie_sustained",
]


@dataclass(frozen=True)
class Relationship:
    """Predicted relationship between two detection indices."""

    source_idx: int
    target_idx: int
    relationship_type: str
    confidence: float


@dataclass(frozen=True)
class AssemblyModeStatus:
    """Applied assembly mode and fallback provenance."""

    requested_mode: str
    applied_mode: Literal["heuristic", "heuristic_fallback", "checkpoint_missing", "gnn"]
    fallback_applied: bool
    fallback_reason: str | None
    checkpoint_ready: bool
    checkpoint_path: str | None = None
    adapter_name: str | None = None
    inference_ran: bool = False
    warnings: list[str] = field(default_factory=list)


def resolve_checkpoint_path(checkpoint_path: str | None = None) -> Path | None:
    """Resolve the configured GNN checkpoint path."""
    value = checkpoint_path or os.getenv("MELODIOUS_GNN_CHECKPOINT")
    if not value:
        return None
    return Path(value).expanduser().resolve()


def resolve_assembly_mode(requested_mode: str, checkpoint_path: str | None = None) -> AssemblyModeStatus:
    """Resolve the actual assembly mode without pretending fallback is GNN."""
    checkpoint = resolve_checkpoint_path(checkpoint_path)
    checkpoint_ready = bool(checkpoint and checkpoint.exists())
    warnings: list[str] = []

    if requested_mode == "heuristic":
        return AssemblyModeStatus(
            requested_mode="heuristic",
            applied_mode="heuristic",
            fallback_applied=False,
            fallback_reason=None,
            checkpoint_ready=checkpoint_ready,
            checkpoint_path=str(checkpoint) if checkpoint else None,
            warnings=warnings,
        )

    if requested_mode in {"auto", "gnn"} and checkpoint_ready:
        reason = "checkpoint exists, but the V2 GNN adapter did not run in this resolver-only call"
        warnings.append(f"GNN adapter unavailable. Applying heuristic fallback. {reason}.")
        return AssemblyModeStatus(
            requested_mode=requested_mode,
            applied_mode="heuristic_fallback",
            fallback_applied=True,
            fallback_reason=reason,
            checkpoint_ready=True,
            checkpoint_path=str(checkpoint),
            warnings=warnings,
        )

    if requested_mode == "gnn":
        reason = "checkpoint_missing: MELODIOUS_GNN_CHECKPOINT is not configured or the file does not exist"
        warnings.append(f"GNN mode requested but unavailable. Applying heuristic fallback. {reason}.")
        return AssemblyModeStatus(
            requested_mode="gnn",
            applied_mode="checkpoint_missing",
            fallback_applied=True,
            fallback_reason=reason,
            checkpoint_ready=False,
            checkpoint_path=str(checkpoint) if checkpoint else None,
            warnings=warnings,
        )

    return AssemblyModeStatus(
        requested_mode="auto",
        applied_mode="heuristic",
        fallback_applied=False,
        fallback_reason=None,
        checkpoint_ready=checkpoint_ready,
        checkpoint_path=str(checkpoint) if checkpoint else None,
        warnings=warnings,
    )


def heuristic_relationships(payload: DetectorPayloadV2) -> list[Relationship]:
    """Infer a small set of local structural relationships from detections."""
    relationships: list[Relationship] = []
    detections = payload.detections
    noteheads = [
        (idx, det)
        for idx, det in enumerate(detections)
        if det.semantic_group == "notehead"
    ]
    stems = [
        (idx, det)
        for idx, det in enumerate(detections)
        if det.semantic_group == "stem"
    ]
    beams = [
        (idx, det)
        for idx, det in enumerate(detections)
        if det.semantic_group == "beam"
    ]

    for stem_idx, stem in stems:
        best_note = None
        best_distance = float("inf")
        for note_idx, note in noteheads:
            dx = abs(stem.bbox.x_center - note.bbox.x_center)
            dy = abs(stem.bbox.y_center - note.bbox.y_center)
            distance = dx + dy
            if dx < 0.06 and distance < best_distance:
                best_note = note_idx
                best_distance = distance
        if best_note is not None:
            relationships.append(Relationship(stem_idx, best_note, "stem_notehead", 0.55))

    for beam_idx, beam in beams:
        for note_idx, note in noteheads:
            dx = abs(beam.bbox.x_center - note.bbox.x_center)
            dy = abs(beam.bbox.y_center - note.bbox.y_center)
            if dx < 0.12 and dy < 0.08:
                relationships.append(Relationship(beam_idx, note_idx, "beam_notegroup", 0.45))

    return relationships


def assemble_payload(
    payload: DetectorPayloadV2,
    requested_mode: str = "auto",
    checkpoint_path: str | None = None,
    gnn_adapter: Any | None = None,
) -> tuple[AssemblyModeStatus, list[Relationship]]:
    """Resolve mode and return relationships for one payload."""
    if requested_mode == "heuristic":
        mode = resolve_assembly_mode("heuristic", checkpoint_path=checkpoint_path)
        return mode, heuristic_relationships(payload)

    checkpoint = resolve_checkpoint_path(checkpoint_path)
    checkpoint_exists = bool(checkpoint and checkpoint.exists())

    if not checkpoint_exists and gnn_adapter is None:
        mode = resolve_assembly_mode(requested_mode, checkpoint_path=checkpoint_path)
        return mode, heuristic_relationships(payload)

    adapter = gnn_adapter
    adapter_name = getattr(adapter, "name", None) if adapter is not None else None
    warnings: list[str] = []
    if adapter is None:
        try:
            from melodious_v2.assembly.legacy_gnn import LegacyGnnAdapter

            adapter = LegacyGnnAdapter(checkpoint)
            adapter_name = adapter.name
        except Exception as exc:
            reason = f"gnn_adapter_error: {exc}"
            warnings.append(f"GNN checkpoint could not be loaded. Applying heuristic fallback. {reason}")
            return (
                AssemblyModeStatus(
                    requested_mode=requested_mode,
                    applied_mode="heuristic_fallback",
                    fallback_applied=True,
                    fallback_reason=reason,
                    checkpoint_ready=checkpoint_exists,
                    checkpoint_path=str(checkpoint) if checkpoint else None,
                    adapter_name=adapter_name,
                    inference_ran=False,
                    warnings=warnings,
                ),
                heuristic_relationships(payload),
            )

    try:
        prediction = adapter.predict_payload(payload)
    except Exception as exc:
        reason = f"gnn_inference_error: {exc}"
        warnings.append(f"GNN inference failed. Applying heuristic fallback. {reason}")
        return (
            AssemblyModeStatus(
                requested_mode=requested_mode,
                applied_mode="heuristic_fallback",
                fallback_applied=True,
                fallback_reason=reason,
                checkpoint_ready=True,
                checkpoint_path=str(checkpoint) if checkpoint else None,
                adapter_name=adapter_name,
                inference_ran=False,
                warnings=warnings,
            ),
            heuristic_relationships(payload),
        )

    if getattr(prediction, "inference_ran", False):
        mode = AssemblyModeStatus(
            requested_mode=requested_mode,
            applied_mode="gnn",
            fallback_applied=False,
            fallback_reason=None,
            checkpoint_ready=True,
            checkpoint_path=str(checkpoint) if checkpoint else None,
            adapter_name=adapter_name,
            inference_ran=True,
            warnings=list(getattr(prediction, "warnings", [])),
        )
        return mode, list(prediction.relationships)

    reason = "gnn_no_candidate_edges: checkpoint loaded but inference did not run for this payload"
    warnings.extend(getattr(prediction, "warnings", []))
    warnings.append(f"Applying heuristic fallback. {reason}")
    return (
        AssemblyModeStatus(
            requested_mode=requested_mode,
            applied_mode="heuristic_fallback",
            fallback_applied=True,
            fallback_reason=reason,
            checkpoint_ready=True,
            checkpoint_path=str(checkpoint) if checkpoint else None,
            adapter_name=adapter_name,
            inference_ran=False,
            warnings=warnings,
        ),
        heuristic_relationships(payload),
    )
