"""Rule-based heuristic assembler baseline.

Given a set of detected symbols with bounding boxes, this module
groups them into musical structures (notes, chords, beams) using
purely spatial heuristics — no learned graph model.

This provides a lower bound for the GNN assembler to beat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence


@dataclass
class Symbol:
    class_id: int
    class_name: str
    x_center: float
    y_center: float
    width: float
    height: float
    confidence: float = 1.0


@dataclass
class NoteGroup:
    """A note = notehead + optional stem + optional beam."""
    notehead: Symbol
    stem: Optional[Symbol] = None
    beam: Optional[Symbol] = None
    accidental: Optional[Symbol] = None


@dataclass
class AssembledOutput:
    """Container returned by the heuristic assembler."""
    notes: List[NoteGroup] = field(default_factory=list)
    clefs: List[Symbol] = field(default_factory=list)
    rests: List[Symbol] = field(default_factory=list)
    unmatched: List[Symbol] = field(default_factory=list)


# Class-name sets for heuristic grouping
_NOTEHEADS = {"notehead-full", "notehead-half", "notehead-whole"}
_STEMS = {"stem"}
_BEAMS = {"beam"}
_CLEFS = {"clefG", "clefF", "clefC"}
_RESTS = {"rest-8th", "rest-quarter", "rest-half", "rest-whole"}
_ACCIDENTALS = {"accidentalSharp", "accidentalFlat", "accidentalNatural"}


def _dist(a: Symbol, b: Symbol) -> float:
    return ((a.x_center - b.x_center) ** 2 + (a.y_center - b.y_center) ** 2) ** 0.5


def _nearest(target: Symbol, candidates: List[Symbol], max_dist: float) -> Optional[int]:
    best_idx = None
    best_d = max_dist
    for i, c in enumerate(candidates):
        d = _dist(target, c)
        if d < best_d:
            best_d = d
            best_idx = i
    return best_idx


def assemble_detections(
    detections: Sequence[Dict],
    proximity_threshold: float = 0.06,
) -> AssembledOutput:
    """Group detections into musical structures using spatial heuristics.

    Parameters
    ----------
    detections : sequence of detection dicts
        Each dict must have ``class_name``, ``confidence``, and a ``bbox`` sub-dict
        with ``x_center``, ``y_center``, ``width``, ``height`` (all normalised 0-1).
    proximity_threshold : float
        Maximum normalised Euclidean distance to link a stem or accidental
        to a notehead.

    Returns
    -------
    AssembledOutput with grouped notes, clefs, rests, and unmatched symbols.
    """
    symbols: List[Symbol] = []
    for d in detections:
        bbox = d["bbox"]
        symbols.append(Symbol(
            class_id=d["class_id"],
            class_name=d["class_name"],
            x_center=bbox["x_center"],
            y_center=bbox["y_center"],
            width=bbox["width"],
            height=bbox["height"],
            confidence=d.get("confidence", 1.0),
        ))

    noteheads = [s for s in symbols if s.class_name in _NOTEHEADS]
    stems = [s for s in symbols if s.class_name in _STEMS]
    beams = [s for s in symbols if s.class_name in _BEAMS]
    accidentals = [s for s in symbols if s.class_name in _ACCIDENTALS]
    clefs = [s for s in symbols if s.class_name in _CLEFS]
    rests = [s for s in symbols if s.class_name in _RESTS]

    used_stems: set = set()
    used_beams: set = set()
    used_accidentals: set = set()
    groups: List[NoteGroup] = []

    for nh in noteheads:
        group = NoteGroup(notehead=nh)

        # Link nearest stem
        idx = _nearest(nh, stems, proximity_threshold)
        if idx is not None and idx not in used_stems:
            group.stem = stems[idx]
            used_stems.add(idx)

        # Link nearest beam
        idx = _nearest(nh, beams, proximity_threshold * 1.5)
        if idx is not None and idx not in used_beams:
            group.beam = beams[idx]
            used_beams.add(idx)

        # Link nearest accidental
        idx = _nearest(nh, accidentals, proximity_threshold)
        if idx is not None and idx not in used_accidentals:
            group.accidental = accidentals[idx]
            used_accidentals.add(idx)

        groups.append(group)

    # Collect unmatched symbols
    unmatched = []
    for i, s in enumerate(stems):
        if i not in used_stems:
            unmatched.append(s)
    for i, s in enumerate(beams):
        if i not in used_beams:
            unmatched.append(s)
    for i, s in enumerate(accidentals):
        if i not in used_accidentals:
            unmatched.append(s)

    return AssembledOutput(
        notes=groups,
        clefs=clefs,
        rests=rests,
        unmatched=unmatched,
    )
