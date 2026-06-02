from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from melodious_v2.omr.note_extraction import (
    detect_staff_systems,
    extract_notes_from_image,
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
                default_quarter_length=0.5,
            )
            self.assertGreaterEqual(len(result.notes), 3)
            midi_path = Path(result.artifacts.midi_path)  # type: ignore[union-attr]
            self.assertTrue(midi_path.exists())
            self.assertGreater(midi_path.stat().st_size, 26)
            self.assertEqual(midi_path.read_bytes()[:4], b"MThd")

    def test_midi_writer_handles_empty_note_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            midi_path = Path(tmp) / "empty.mid"
            write_midi([], midi_path)
            self.assertEqual(midi_path.read_bytes()[:4], b"MThd")


if __name__ == "__main__":
    unittest.main()
