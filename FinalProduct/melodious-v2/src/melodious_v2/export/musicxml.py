"""MusicXML and MIDI artifact generation."""

from __future__ import annotations

import base64
import xml.etree.ElementTree as ET
from typing import Iterable

from melodious_v2.assembly.service import Relationship
from melodious_v2.contracts import DetectorPayloadV2


def _pitch_for_detection_index(index: int) -> tuple[str, int, int]:
    steps = ["C", "D", "E", "F", "G", "A", "B"]
    return steps[index % len(steps)], 4 + (index % 2), 1


def payload_to_musicxml(
    payload: DetectorPayloadV2,
    relationships: Iterable[Relationship] | None = None,
    title: str = "Melodious V2 Export",
) -> str:
    """Create a compact but valid MusicXML document from detector output."""
    _ = list(relationships or [])
    note_like = [
        det for det in payload.detections if det.semantic_group in {"notehead", "rest"}
    ]
    if not note_like:
        note_like = payload.detections[:1]

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<score-partwise version="3.1">',
        "  <work>",
        f"    <work-title>{title}</work-title>",
        "  </work>",
        "  <part-list>",
        '    <score-part id="P1"><part-name>Melodious V2</part-name></score-part>',
        "  </part-list>",
        '  <part id="P1">',
        '    <measure number="1">',
        "      <attributes>",
        "        <divisions>1</divisions>",
        "        <key><fifths>0</fifths></key>",
        "        <time><beats>4</beats><beat-type>4</beat-type></time>",
        "        <clef><sign>G</sign><line>2</line></clef>",
        "      </attributes>",
    ]

    for index, detection in enumerate(note_like[:16]):
        parts.append("      <note>")
        if detection.semantic_group == "rest":
            parts.append("        <rest/>")
        else:
            step, octave, duration = _pitch_for_detection_index(index)
            parts.extend(
                [
                    "        <pitch>",
                    f"          <step>{step}</step>",
                    f"          <octave>{octave}</octave>",
                    "        </pitch>",
                ]
            )
        parts.extend(
            [
                "        <duration>1</duration>",
                "        <type>quarter</type>",
                "      </note>",
            ]
        )

    parts.extend(["    </measure>", "  </part>", "</score-partwise>"])
    return "\n".join(parts) + "\n"


def validate_musicxml(content: str) -> bool:
    """Return whether the MusicXML string is parseable XML with score root."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return False
    return root.tag == "score-partwise"


def minimal_midi_bytes() -> bytes:
    """Return a minimal valid Standard MIDI File with one empty track."""
    return (
        b"MThd"
        + (6).to_bytes(4, "big")
        + (1).to_bytes(2, "big")
        + (1).to_bytes(2, "big")
        + (480).to_bytes(2, "big")
        + b"MTrk"
        + (4).to_bytes(4, "big")
        + b"\x00\xff\x2f\x00"
    )


def minimal_midi_base64() -> str:
    """Return base64 for a minimal valid MIDI file."""
    return base64.b64encode(minimal_midi_bytes()).decode("ascii")
