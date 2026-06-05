from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from scripts.extract_notes_from_image import default_checkpoint


class NoteExtractionCliTest(unittest.TestCase):
    def test_default_checkpoint_prefers_saved_demo_artifact(self) -> None:
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            demo_checkpoint = tmp_path / "artifacts/models/note_extraction_default_fullpage/best.pt"
            fine_tune_checkpoint = (
                tmp_path
                / "runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/"
                / "ultralytics/train/weights/best.pt"
            )
            base_checkpoint = tmp_path / "artifacts/models/detection_136class_yolov8m_v1/best.pt"
            for checkpoint in (demo_checkpoint, fine_tune_checkpoint, base_checkpoint):
                checkpoint.parent.mkdir(parents=True, exist_ok=True)
                checkpoint.write_bytes(b"checkpoint")

            try:
                os.chdir(tmp_path)
                self.assertEqual(default_checkpoint(), Path("artifacts/models/note_extraction_default_fullpage/best.pt"))
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
