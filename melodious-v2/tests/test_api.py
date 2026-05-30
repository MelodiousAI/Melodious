import base64
import io
import unittest

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from melodious_v2.api.app import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_and_version(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")
        version = self.client.get("/version")
        self.assertEqual(version.status_code, 200)
        self.assertEqual(version.json()["schema_version"], "2.0")

    def test_sample_transcription_and_artifacts(self):
        response = self.client.post(
            "/transcriptions",
            json={"sample_id": "sample-notation-1", "requested_assembly_mode": "auto"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "complete")
        self.assertGreaterEqual(payload["detection_count"], 1)
        musicxml = self.client.get(f"/transcriptions/{payload['job_id']}/artifacts/musicxml")
        self.assertEqual(musicxml.status_code, 200)
        self.assertIn(b"score-partwise", musicxml.content)

    def test_upload_transcription_is_labeled_bootstrap(self):
        image = Image.new("L", (120, 80), 255)
        draw = ImageDraw.Draw(image)
        draw.ellipse((40, 30, 55, 45), fill=0)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        response = self.client.post(
            "/transcriptions",
            json={"image_base64": image_b64, "filename": "unit.png"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["detector_mode"], "heuristic_bootstrap")
        self.assertTrue(payload["warnings"])


if __name__ == "__main__":
    unittest.main()

