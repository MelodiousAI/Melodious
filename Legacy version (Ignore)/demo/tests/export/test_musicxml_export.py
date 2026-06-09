import base64
import importlib.util
import unittest

from src.export.musicxml_export import payload_to_midi_base64, payload_to_musicxml_text


MUSIC21_AVAILABLE = importlib.util.find_spec("music21") is not None


@unittest.skipUnless(MUSIC21_AVAILABLE, "music21 is required for export rendering tests")
class TestMusicXmlExport(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "image_path": "demo\\simple_score.png",
            "detections": [
                {
                    "class_id": 1,
                    "class_name": "clefG",
                    "confidence": 1.0,
                    "bbox": {"x_center": 0.08, "y_center": 0.35, "width": 0.04, "height": 0.18},
                },
                {
                    "class_id": 2,
                    "class_name": "notehead-full",
                    "confidence": 0.95,
                    "bbox": {"x_center": 0.25, "y_center": 0.34, "width": 0.03, "height": 0.03},
                },
                {
                    "class_id": 3,
                    "class_name": "beam",
                    "confidence": 0.90,
                    "bbox": {"x_center": 0.27, "y_center": 0.31, "width": 0.05, "height": 0.02},
                },
                {
                    "class_id": 4,
                    "class_name": "rest-quarter",
                    "confidence": 0.88,
                    "bbox": {"x_center": 0.50, "y_center": 0.40, "width": 0.03, "height": 0.05},
                },
            ],
        }

    def test_payload_to_musicxml_text_returns_xml_document(self):
        xml_text = payload_to_musicxml_text(self.payload, title="Test Score")

        self.assertIn("score-partwise", xml_text)
        self.assertIn("Test Score", xml_text)

    def test_payload_to_midi_base64_returns_valid_midi_header(self):
        midi_base64 = payload_to_midi_base64(self.payload, title="Test Score")
        midi_bytes = base64.b64decode(midi_base64)

        self.assertTrue(midi_bytes.startswith(b"MThd"))


if __name__ == "__main__":
    unittest.main()
