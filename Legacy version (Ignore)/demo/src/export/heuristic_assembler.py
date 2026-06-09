"""Rule-based notation assembly helpers for Week 3 export work."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Symbol:
    """Compact symbol view used by the heuristic assembler."""

    class_id: int
    class_name: str
    x_center: float
    y_center: float
    width: float
    height: float
    confidence: float = 1.0


@dataclass
class NoteGroup:
    """A notehead plus the nearby notation symbols that likely belong to it."""

    notehead: Symbol
    stem: Symbol | None = None
    beam: Symbol | None = None
    accidental: Symbol | None = None


@dataclass
class AssembledOutput:
    """Container returned by the heuristic assembler baseline."""

    notes: list[NoteGroup] = field(default_factory=list)
    clefs: list[Symbol] = field(default_factory=list)
    rests: list[Symbol] = field(default_factory=list)
    unmatched: list[Symbol] = field(default_factory=list)


_NOTEHEADS = {"notehead-full", "notehead-half", "notehead-whole"}
_STEMS = {"stem"}
_BEAMS = {"beam"}
_CLEFS = {"clefG", "clefF", "clefC"}
_RESTS = {"rest-8th", "rest-quarter", "rest-half", "rest-whole"}
_ACCIDENTALS = {"accidentalSharp", "accidentalFlat", "accidentalNatural"}


def _dist(a: Symbol, b: Symbol) -> float:
    return ((a.x_center - b.x_center) ** 2 + (a.y_center - b.y_center) ** 2) ** 0.5


def _nearest(target: Symbol, candidates: list[Symbol], max_dist: float) -> int | None:
    best_idx = None
    best_distance = max_dist

    for index, candidate in enumerate(candidates):
        distance = _dist(target, candidate)

        if distance < best_distance:
            best_distance = distance
            best_idx = index

    return best_idx


def _build_symbol(detection: dict[str, Any]) -> Symbol:
    bbox = detection["bbox"]

    return Symbol(
        class_id=int(detection["class_id"]),
        class_name=detection["class_name"],
        x_center=float(bbox["x_center"]),
        y_center=float(bbox["y_center"]),
        width=float(bbox["width"]),
        height=float(bbox["height"]),
        confidence=float(detection.get("confidence", 1.0)),
    )


def assemble_detections(
    detections: list[dict[str, Any]],
    proximity_threshold: float = 0.06,
) -> AssembledOutput:
    """Group detector payload symbols into simple musical structures."""

    symbols = [_build_symbol(detection) for detection in detections]

    noteheads = [symbol for symbol in symbols if symbol.class_name in _NOTEHEADS]
    stems = [symbol for symbol in symbols if symbol.class_name in _STEMS]
    beams = [symbol for symbol in symbols if symbol.class_name in _BEAMS]
    accidentals = [symbol for symbol in symbols if symbol.class_name in _ACCIDENTALS]
    clefs = [symbol for symbol in symbols if symbol.class_name in _CLEFS]
    rests = [symbol for symbol in symbols if symbol.class_name in _RESTS]

    used_stems: set[int] = set()
    used_beams: set[int] = set()
    used_accidentals: set[int] = set()
    groups: list[NoteGroup] = []

    for notehead in noteheads:
        group = NoteGroup(notehead=notehead)

        stem_index = _nearest(notehead, stems, proximity_threshold)
        if stem_index is not None and stem_index not in used_stems:
            group.stem = stems[stem_index]
            used_stems.add(stem_index)

        beam_index = _nearest(notehead, beams, proximity_threshold * 1.5)
        if beam_index is not None and beam_index not in used_beams:
            group.beam = beams[beam_index]
            used_beams.add(beam_index)

        accidental_index = _nearest(notehead, accidentals, proximity_threshold)
        if accidental_index is not None and accidental_index not in used_accidentals:
            group.accidental = accidentals[accidental_index]
            used_accidentals.add(accidental_index)

        groups.append(group)

    unmatched = [
        symbol
        for index, symbol in enumerate(stems)
        if index not in used_stems
    ]
    unmatched.extend(
        symbol
        for index, symbol in enumerate(beams)
        if index not in used_beams
    )
    unmatched.extend(
        symbol
        for index, symbol in enumerate(accidentals)
        if index not in used_accidentals
    )

    return AssembledOutput(
        notes=groups,
        clefs=clefs,
        rests=rests,
        unmatched=unmatched,
    )


def summarize_assembled_output(assembled_output: AssembledOutput) -> dict[str, int]:
    """Return compact counts for API responses and debugging."""

    return {
        "note_count": len(assembled_output.notes),
        "clef_count": len(assembled_output.clefs),
        "rest_count": len(assembled_output.rests),
        "unmatched_count": len(assembled_output.unmatched),
    }
