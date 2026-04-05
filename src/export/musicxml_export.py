"""MusicXML and MIDI export helpers built around the shared detector payload."""

from __future__ import annotations

import base64
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


ExportFormat = Literal["midi", "musicxml"]


@dataclass
class StaffRegion:
    """Detected or inferred staff bounds in normalized y-space."""

    staff_id: int
    y_top: float
    y_bottom: float
    clef_type: str = "treble"


_TREBLE_PITCHES = [
    "D4",
    "E4",
    "F4",
    "G4",
    "A4",
    "B4",
    "C5",
    "D5",
    "E5",
    "F5",
    "G5",
    "A5",
]

_BASS_PITCHES = [
    "F2",
    "G2",
    "A2",
    "B2",
    "C3",
    "D3",
    "E3",
    "F3",
    "G3",
    "A3",
    "B3",
    "C4",
]

_CLASS_DURATION = {
    "notehead-full": 1.0,
    "notehead-half": 2.0,
    "notehead-whole": 4.0,
}

_REST_DURATIONS = {
    "rest-8th": 0.5,
    "rest-quarter": 1.0,
    "rest-half": 2.0,
    "rest-whole": 4.0,
}

_NOTEHEAD_CLASSES = {"notehead-full", "notehead-half", "notehead-whole"}


def _load_music21():
    try:
        from music21 import clef as m21clef
        from music21 import metadata as m21meta
        from music21 import meter as m21meter
        from music21 import note as m21note
        from music21 import stream as m21stream
    except ImportError as exc:
        raise ImportError(
            "music21 is required for MusicXML/MIDI export. Install the project requirements first."
        ) from exc

    return {
        "clef": m21clef,
        "metadata": m21meta,
        "meter": m21meter,
        "note": m21note,
        "stream": m21stream,
    }


def _y_to_pitch_name(
    y_norm: float,
    staff_top: float,
    staff_bottom: float,
    clef_type: str = "treble",
) -> str:
    pitch_table = _TREBLE_PITCHES if clef_type == "treble" else _BASS_PITCHES

    if staff_bottom <= staff_top:
        return pitch_table[len(pitch_table) // 2]

    position = (staff_bottom - y_norm) / (staff_bottom - staff_top)
    position = max(0.0, min(1.0, position))
    index = int(round(position * (len(pitch_table) - 1)))
    index = max(0, min(len(pitch_table) - 1, index))
    return pitch_table[index]


def _get_duration(class_name: str, has_beam: bool = False) -> float:
    base_duration = _CLASS_DURATION.get(class_name, 1.0)

    if has_beam and class_name == "notehead-full":
        return 0.5

    return base_duration


def _detect_clef(detections: list[dict[str, Any]]) -> str:
    clef_counts: dict[str, int] = {}

    for detection in detections:
        class_name = detection.get("class_name", "")

        if class_name.startswith("clef"):
            clef_counts[class_name] = clef_counts.get(class_name, 0) + 1

    if not clef_counts:
        return "treble"

    dominant_clef = max(clef_counts, key=clef_counts.get)
    return "bass" if "F" in dominant_clef else "treble"


def _infer_staff_regions(detections: list[dict[str, Any]]) -> list[StaffRegion]:
    clefs = [detection for detection in detections if detection.get("class_name", "").startswith("clef")]

    if clefs:
        clefs_sorted = sorted(clefs, key=lambda detection: detection["bbox"]["y_center"])
        regions = []

        for index, clef_detection in enumerate(clefs_sorted):
            clef_type = "bass" if "F" in clef_detection["class_name"] else "treble"
            y_center = float(clef_detection["bbox"]["y_center"])
            regions.append(
                StaffRegion(
                    staff_id=index,
                    y_top=max(0.0, y_center - 0.08),
                    y_bottom=min(1.0, y_center + 0.08),
                    clef_type=clef_type,
                )
            )

        return regions

    return [StaffRegion(staff_id=0, y_top=0.0, y_bottom=1.0, clef_type=_detect_clef(detections))]


def _assign_to_staff(y_center: float, staves: list[StaffRegion]) -> StaffRegion:
    best_staff = staves[0]
    best_distance = abs(y_center - ((best_staff.y_top + best_staff.y_bottom) / 2))

    for staff in staves[1:]:
        distance = abs(y_center - ((staff.y_top + staff.y_bottom) / 2))

        if distance < best_distance:
            best_distance = distance
            best_staff = staff

    return best_staff


def _resolve_title(payload: dict[str, Any], title: str | None) -> str:
    if title:
        return title

    image_path = payload.get("image_path")

    if image_path:
        return Path(image_path).stem

    return "Melodious Export"


def assemble_score(
    detections: list[dict[str, Any]],
    title: str = "Melodious Export",
):
    """Convert detector payload detections into a music21 score."""

    music21 = _load_music21()
    m21clef = music21["clef"]
    m21meta = music21["metadata"]
    m21meter = music21["meter"]
    m21note = music21["note"]
    m21stream = music21["stream"]

    score = m21stream.Score()
    score.metadata = m21meta.Metadata()
    score.metadata.title = title

    staves = _infer_staff_regions(detections)
    parts = {}

    for staff in staves:
        part = m21stream.Part()

        if staff.clef_type == "bass":
            part.append(m21clef.BassClef())
        else:
            part.append(m21clef.TrebleClef())

        part.append(m21meter.TimeSignature("4/4"))
        parts[staff.staff_id] = part

    noteheads = [detection for detection in detections if detection.get("class_name") in _NOTEHEAD_CLASSES]
    beams = [detection for detection in detections if detection.get("class_name") == "beam"]
    noteheads.sort(key=lambda detection: detection["bbox"]["x_center"])

    def is_beamed(notehead_detection):
        note_x = float(notehead_detection["bbox"]["x_center"])
        note_y = float(notehead_detection["bbox"]["y_center"])

        for beam in beams:
            beam_x = float(beam["bbox"]["x_center"])
            beam_y = float(beam["bbox"]["y_center"])

            if abs(note_x - beam_x) < 0.05 and abs(note_y - beam_y) < 0.08:
                return True

        return False

    for notehead in noteheads:
        bbox = notehead["bbox"]
        staff = _assign_to_staff(float(bbox["y_center"]), staves)
        pitch_name = _y_to_pitch_name(
            float(bbox["y_center"]),
            staff.y_top,
            staff.y_bottom,
            staff.clef_type,
        )
        duration = _get_duration(notehead["class_name"], has_beam=is_beamed(notehead))

        note = m21note.Note(pitch_name, quarterLength=duration)
        note.volume.velocity = int(min(127, max(20, float(notehead.get("confidence", 0.8)) * 127)))
        parts[staff.staff_id].append(note)

    rests = [detection for detection in detections if detection.get("class_name", "").startswith("rest-")]
    rests.sort(key=lambda detection: detection["bbox"]["x_center"])

    for rest in rests:
        staff = _assign_to_staff(float(rest["bbox"]["y_center"]), staves)
        duration = _REST_DURATIONS.get(rest["class_name"], 1.0)
        rest_note = m21note.Rest(quarterLength=duration)
        parts[staff.staff_id].append(rest_note)

    for part in parts.values():
        part.makeMeasures(inPlace=True)
        score.append(part)

    return score


def _render_musicxml_text(score) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "score.musicxml"
        score.write("musicxml", fp=str(output_path))
        return output_path.read_text(encoding="utf-8")


def _render_midi_bytes(score) -> bytes:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "score.mid"
        score.write("midi", fp=str(output_path))
        return output_path.read_bytes()


def payload_to_musicxml_text(payload: dict[str, Any], title: str | None = None) -> str:
    detections = payload.get("detections", [])
    score = assemble_score(detections, title=_resolve_title(payload, title))
    return _render_musicxml_text(score)


def payload_to_midi_base64(payload: dict[str, Any], title: str | None = None) -> str:
    detections = payload.get("detections", [])
    score = assemble_score(detections, title=_resolve_title(payload, title))
    midi_bytes = _render_midi_bytes(score)
    return base64.b64encode(midi_bytes).decode("ascii")


def export_payload_content(
    payload: dict[str, Any],
    output_format: ExportFormat,
    title: str | None = None,
) -> tuple[str, str, str]:
    """Return encoded export content plus response metadata."""

    if output_format == "musicxml":
        return (
            payload_to_musicxml_text(payload, title=title),
            "application/vnd.recordare.musicxml+xml",
            "utf-8",
        )

    if output_format == "midi":
        return (
            payload_to_midi_base64(payload, title=title),
            "audio/midi",
            "base64",
        )

    raise ValueError(f"Unsupported output_format: {output_format}")
