"""MusicXML and MIDI export from assembled notation graphs.

Converts detection payloads (with GNN relationship edges or heuristic
groupings) into playable music using the music21 library.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

try:
    import music21
    from music21 import (
        chord as m21chord,
        clef as m21clef,
        key as m21key,
        metadata as m21meta,
        meter as m21meter,
        note as m21note,
        pitch as m21pitch,
        stream as m21stream,
    )
    MUSIC21_AVAILABLE = True
except ImportError:
    MUSIC21_AVAILABLE = False


# ---------------------------------------------------------------------------
# Staff pitch mapping
# ---------------------------------------------------------------------------

# Treble clef: line 1 (bottom) = E4, line 3 (middle) = B4, line 5 (top) = F5
# Bass clef: line 1 (bottom) = G2, line 3 (middle) = D3, line 5 (top) = A3
# 0.0 = bottom of staff region, 1.0 = top of staff region
# Each step = half a staff position

# Treble clef pitch names by staff position (bottom to top, half-step intervals)
_TREBLE_PITCHES = [
    "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5",
]

# Bass clef pitch names by staff position
_BASS_PITCHES = [
    "F2", "G2", "A2", "B2", "C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4",
]


def _y_to_pitch_name(
    y_norm: float,
    staff_top: float,
    staff_bottom: float,
    clef_type: str = "treble",
) -> str:
    """Map a normalised y-coordinate to a pitch name using staff boundaries."""
    pitch_table = _TREBLE_PITCHES if clef_type == "treble" else _BASS_PITCHES
    if staff_bottom <= staff_top:
        return pitch_table[len(pitch_table) // 2]

    # Position within staff (0 = bottom line, 1 = top line)
    pos = (staff_bottom - y_norm) / (staff_bottom - staff_top)
    pos = max(0.0, min(1.0, pos))
    index = int(round(pos * (len(pitch_table) - 1)))
    index = max(0, min(len(pitch_table) - 1, index))
    return pitch_table[index]


# ---------------------------------------------------------------------------
# Duration mapping
# ---------------------------------------------------------------------------

_CLASS_DURATION = {
    "notehead-full": 1.0,   # quarter note
    "notehead-half": 2.0,   # half note
    "notehead-whole": 4.0,  # whole note
}


def _get_duration(class_name: str, has_beam: bool = False) -> float:
    """Return music21 quarterLength for a notehead class."""
    base = _CLASS_DURATION.get(class_name, 1.0)
    if has_beam and class_name == "notehead-full":
        return 0.5  # eighth note if beamed
    return base


# ---------------------------------------------------------------------------
# Clef detection from detections
# ---------------------------------------------------------------------------

def _detect_clef(detections: Sequence[Dict]) -> str:
    """Determine the dominant clef from detections."""
    clef_counts: Dict[str, int] = {}
    for d in detections:
        cn = d.get("class_name", "")
        if cn.startswith("clef"):
            clef_counts[cn] = clef_counts.get(cn, 0) + 1
    if not clef_counts:
        return "treble"
    dominant = max(clef_counts, key=clef_counts.get)
    if "F" in dominant:
        return "bass"
    return "treble"


# ---------------------------------------------------------------------------
# Assemble payload into music21 Score
# ---------------------------------------------------------------------------

@dataclass
class StaffRegion:
    """Detected staff with y-bounds and assigned clef."""
    staff_id: int
    y_top: float
    y_bottom: float
    clef_type: str = "treble"


def _infer_staff_regions(
    detections: Sequence[Dict],
    num_staves: int = 1,
) -> List[StaffRegion]:
    """Estimate staff regions from clef detections and symbol distribution."""
    clefs = [d for d in detections if d.get("class_name", "").startswith("clef")]

    if clefs:
        # Sort clefs by vertical position
        clefs_sorted = sorted(clefs, key=lambda d: d["bbox"]["y_center"])
        regions = []
        for i, c in enumerate(clefs_sorted):
            ctype = "bass" if "F" in c["class_name"] else "treble"
            yc = c["bbox"]["y_center"]
            regions.append(StaffRegion(
                staff_id=i,
                y_top=max(0.0, yc - 0.08),
                y_bottom=min(1.0, yc + 0.08),
                clef_type=ctype,
            ))
        return regions if regions else [StaffRegion(0, 0.0, 1.0, "treble")]

    return [StaffRegion(0, 0.0, 1.0, _detect_clef(detections))]


def _assign_to_staff(y_center: float, staves: List[StaffRegion]) -> StaffRegion:
    """Assign a symbol to its closest staff region."""
    best = staves[0]
    best_dist = abs(y_center - (best.y_top + best.y_bottom) / 2)
    for s in staves[1:]:
        d = abs(y_center - (s.y_top + s.y_bottom) / 2)
        if d < best_dist:
            best_dist = d
            best = s
    return best


def assemble_score(
    detections: Sequence[Dict],
    title: str = "Melodious Export",
) -> "m21stream.Score":
    """Convert a list of detection dicts into a music21 Score.

    Parameters
    ----------
    detections : sequence of detection dicts
        Each must have class_id, class_name, confidence, and bbox with
        x_center, y_center, width, height (all normalised 0-1).
    title : str
        Title metadata for the score.

    Returns
    -------
    music21.stream.Score
    """
    if not MUSIC21_AVAILABLE:
        raise ImportError("music21 is required for MusicXML export. Install with: pip install music21")

    score = m21stream.Score()
    score.metadata = m21meta.Metadata()
    score.metadata.title = title

    staves = _infer_staff_regions(detections)

    # One Part per staff
    parts: Dict[int, m21stream.Part] = {}
    for s in staves:
        part = m21stream.Part()
        if s.clef_type == "bass":
            part.append(m21clef.BassClef())
        else:
            part.append(m21clef.TrebleClef())
        part.append(m21meter.TimeSignature("4/4"))
        parts[s.staff_id] = part

    # Collect noteheads sorted by x-position (left to right)
    _NOTEHEAD_CLASSES = {"notehead-full", "notehead-half", "notehead-whole"}
    _BEAM_CLASS = "beam"

    noteheads = [d for d in detections if d.get("class_name") in _NOTEHEAD_CLASSES]
    beams = [d for d in detections if d.get("class_name") == _BEAM_CLASS]
    noteheads.sort(key=lambda d: d["bbox"]["x_center"])

    # Check if notehead is beamed
    def is_beamed(nh: Dict) -> bool:
        nx = nh["bbox"]["x_center"]
        ny = nh["bbox"]["y_center"]
        for b in beams:
            bx = b["bbox"]["x_center"]
            by = b["bbox"]["y_center"]
            if abs(nx - bx) < 0.05 and abs(ny - by) < 0.08:
                return True
        return False

    # Build measures (group by x-position chunks)
    for nh in noteheads:
        bbox = nh["bbox"]
        staff = _assign_to_staff(bbox["y_center"], staves)
        pitch_name = _y_to_pitch_name(
            bbox["y_center"], staff.y_top, staff.y_bottom, staff.clef_type,
        )
        duration = _get_duration(nh["class_name"], has_beam=is_beamed(nh))

        n = m21note.Note(pitch_name, quarterLength=duration)
        n.volume.velocity = int(min(127, max(20, nh.get("confidence", 0.8) * 127)))
        parts[staff.staff_id].append(n)

    # Add rests for rest detections
    _REST_DURATIONS = {
        "rest-8th": 0.5,
        "rest-quarter": 1.0,
        "rest-half": 2.0,
        "rest-whole": 4.0,
    }
    rests = [d for d in detections if d.get("class_name", "").startswith("rest-")]
    rests.sort(key=lambda d: d["bbox"]["x_center"])
    for r in rests:
        staff = _assign_to_staff(r["bbox"]["y_center"], staves)
        dur = _REST_DURATIONS.get(r["class_name"], 1.0)
        rest_obj = m21note.Rest(quarterLength=dur)
        parts[staff.staff_id].append(rest_obj)

    for part in parts.values():
        part.makeMeasures(inPlace=True)
        score.append(part)

    return score


# ---------------------------------------------------------------------------
# File export helpers
# ---------------------------------------------------------------------------

def export_musicxml(score: "m21stream.Score", output_path: str) -> Path:
    """Write a music21 Score to MusicXML file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    score.write("musicxml", fp=str(out))
    return out


def export_midi(score: "m21stream.Score", output_path: str) -> Path:
    """Write a music21 Score to MIDI file."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    score.write("midi", fp=str(out))
    return out


def payload_to_musicxml(
    payload: Dict,
    output_path: str,
    title: Optional[str] = None,
) -> Path:
    """Convert a detection payload JSON to MusicXML."""
    detections = payload.get("detections", [])
    if title is None:
        title = Path(payload.get("image_path", "score")).stem
    score = assemble_score(detections, title=title)
    return export_musicxml(score, output_path)


def payload_to_midi(
    payload: Dict,
    output_path: str,
    title: Optional[str] = None,
) -> Path:
    """Convert a detection payload JSON to MIDI."""
    detections = payload.get("detections", [])
    if title is None:
        title = Path(payload.get("image_path", "score")).stem
    score = assemble_score(detections, title=title)
    return export_midi(score, output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Export detection payload to MusicXML / MIDI.")
    parser.add_argument("input", type=Path, help="Detection payload JSON file")
    parser.add_argument("--musicxml", type=str, default=None, help="Output MusicXML path")
    parser.add_argument("--midi", type=str, default=None, help="Output MIDI path")
    parser.add_argument("--title", type=str, default=None)
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)

    stem = args.input.stem
    if args.musicxml:
        path = payload_to_musicxml(payload, args.musicxml, title=args.title)
        print(f"Wrote MusicXML: {path}")
    if args.midi:
        path = payload_to_midi(payload, args.midi, title=args.title)
        print(f"Wrote MIDI: {path}")

    if not args.musicxml and not args.midi:
        # Default: write both next to the input file
        xml_path = payload_to_musicxml(payload, f"outputs/{stem}.musicxml", title=args.title)
        mid_path = payload_to_midi(payload, f"outputs/{stem}.mid", title=args.title)
        print(f"Wrote MusicXML: {xml_path}")
        print(f"Wrote MIDI: {mid_path}")


if __name__ == "__main__":
    main()
