"""Relationship assembly service with explicit fallback metadata."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

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
    applied_mode: Literal["heuristic", "heuristic_fallback", "gnn"]
    fallback_applied: bool
    fallback_reason: str | None
    checkpoint_ready: bool
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
        return AssemblyModeStatus("heuristic", "heuristic", False, None, checkpoint_ready, warnings)

    if requested_mode in {"auto", "gnn"} and checkpoint_ready:
        # The checkpoint exists, but this pass still requires a model-specific
        # adapter before claiming live GNN inference.
        reason = "checkpoint exists, but the V2 GNN adapter has not been selected for this run"
        warnings.append(f"GNN adapter unavailable. Applying heuristic fallback. {reason}.")
        return AssemblyModeStatus(
            requested_mode=requested_mode,
            applied_mode="heuristic_fallback",
            fallback_applied=True,
            fallback_reason=reason,
            checkpoint_ready=True,
            warnings=warnings,
        )

    if requested_mode == "gnn":
        reason = "MELODIOUS_GNN_CHECKPOINT is not configured or the file does not exist"
        warnings.append(f"GNN mode requested but unavailable. Applying heuristic fallback. {reason}.")
        return AssemblyModeStatus("gnn", "heuristic_fallback", True, reason, False, warnings)

    return AssemblyModeStatus("auto", "heuristic", False, None, checkpoint_ready, warnings)


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
) -> tuple[AssemblyModeStatus, list[Relationship]]:
    """Resolve mode and return relationships for one payload."""
    mode = resolve_assembly_mode(requested_mode, checkpoint_path=checkpoint_path)
    relationships = heuristic_relationships(payload)
    return mode, relationships

