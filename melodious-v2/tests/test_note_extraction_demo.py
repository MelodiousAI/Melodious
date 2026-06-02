from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from melodious_v2.omr.note_extraction import (
    DetectionCandidate,
    StaffSystem,
    detect_staff_systems,
    extract_notes_from_image,
    notes_from_candidates,
    pitch_from_y,
    write_midi,
)


class NoteExtractionDemoTest(unittest.TestCase):
    def _synthetic_staff_image(self, path: Path) -> None:
        image = Image.new("L", (420, 180), color=255)
        draw = ImageDraw.Draw(image)
        lines = [60, 70, 80, 90, 100]
        for y in lines:
            draw.line((40, y, 380, y), fill=0, width=1)
        for x, y in [(120, 95), (170, 85), (220, 75), (270, 65)]:
            draw.ellipse((x - 6, y - 4, x + 6, y + 4), fill=0)
            draw.line((x + 6, y, x + 6, y - 35), fill=0, width=2)
        image.save(path)

    def test_staff_detection_and_pitch_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            image_path = Path(tmp) / "staff.png"
            self._synthetic_staff_image(image_path)
            image = Image.open(image_path).convert("L")
            import numpy as np

            staff_systems = detect_staff_systems(np.asarray(image))
            self.assertEqual(len(staff_systems), 1)
            step, octave, midi_pitch = pitch_from_y(staff_systems[0].bottom_y, staff_systems[0])
            self.assertEqual((step, octave, midi_pitch), ("E", 4, 64))

    def test_staff_detection_keeps_light_staff_lines(self) -> None:
        image = Image.new("L", (520, 360), color=255)
        draw = ImageDraw.Draw(image)
        for base_y, fill in [(70, 0), (210, 205)]:
            for offset in range(0, 50, 10):
                draw.line((45, base_y + offset, 470, base_y + offset), fill=fill, width=1)
        draw.text((180, 25), "Light staff regression", fill=0)

        import numpy as np

        staff_systems = detect_staff_systems(np.asarray(image))
        self.assertEqual(len(staff_systems), 2)
        self.assertEqual([round(staff.spacing) for staff in staff_systems], [10, 10])

    def test_cv_extraction_writes_real_midi(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            image_path = tmp_path / "staff.png"
            self._synthetic_staff_image(image_path)
            result = extract_notes_from_image(
                image_path=image_path,
                output_dir=tmp_path / "out",
                checkpoint_path=None,
                use_cv_fallback=True,
                default_quarter_length=1.0,
            )
            self.assertGreaterEqual(len(result.notes), 3)
            midi_path = Path(result.artifacts.midi_path)  # type: ignore[union-attr]
            self.assertTrue(midi_path.exists())
            self.assertGreater(midi_path.stat().st_size, 26)
            self.assertEqual(midi_path.read_bytes()[:4], b"MThd")

    def test_rhythm_inference_uses_beams_flags_and_dots(self) -> None:
        staff = StaffSystem(
            index=0,
            line_y=(60.0, 70.0, 80.0, 90.0, 100.0),
            spacing=10.0,
            start_x=40.0,
            end_x=380.0,
        )
        notes = [
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(100.0, 91.0, 112.0, 99.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(150.0, 81.0, 162.0, 89.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(200.0, 71.0, 212.0, 79.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=1,
                class_name="noteheadBlackInSpace",
                confidence=0.9,
                bbox_xyxy=(250.0, 61.0, 262.0, 69.0),
                source="unit",
            ),
        ]
        symbols = [
            DetectionCandidate(
                class_id=2,
                class_name="augmentationDot",
                confidence=0.8,
                bbox_xyxy=(116.0, 92.0, 119.0, 95.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=3,
                class_name="beam",
                confidence=0.8,
                bbox_xyxy=(145.0, 45.0, 166.0, 49.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=4,
                class_name="flag16thUp",
                confidence=0.8,
                bbox_xyxy=(207.0, 30.0, 216.0, 52.0),
                source="unit",
            ),
            DetectionCandidate(
                class_id=5,
                class_name="stem",
                confidence=0.8,
                bbox_xyxy=(261.0, 30.0, 264.0, 69.0),
                source="unit",
            ),
        ]

        extracted = notes_from_candidates(
            notes,
            [staff],
            rhythm_symbols=symbols,
            default_quarter_length=1.0,
        )

        self.assertEqual([note.quarter_length for note in extracted], [1.5, 0.5, 0.25, 1.0])
        self.assertEqual(
            [note.rhythm_source for note in extracted],
            [
                "black_notehead_quarter_rule_no_stem+augmentation_dot",
                "beam_x1",
                "flag",
                "stem_quarter",
            ],
        )
        self.assertTrue(extracted[0].dotted)
        self.assertFalse(extracted[0].stem_detected)
        self.assertTrue(extracted[3].stem_detected)

    def test_midi_writer_handles_empty_note_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            midi_path = Path(tmp) / "empty.mid"
            write_midi([], midi_path)
            self.assertEqual(midi_path.read_bytes()[:4], b"MThd")


if __name__ == "__main__":
    unittest.main()
