import base64
import io
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from melodious_v2.api.app import app
from melodious_v2.assembly.service import AssemblyModeStatus, Relationship


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

    def test_sample_transcription_can_return_gnn_mode_metadata(self):
        fake_mode = AssemblyModeStatus(
            requested_mode="gnn",
            applied_mode="gnn",
            fallback_applied=False,
            fallback_reason=None,
            checkpoint_ready=True,
            checkpoint_path="fake-checkpoint.pt",
            adapter_name="fake-ready-adapter",
            inference_ran=True,
        )
        fake_relationships = [Relationship(0, 1, "stem_notehead", 0.9)]
        with patch(
            "melodious_v2.api.service.assemble_payload",
            return_value=(fake_mode, fake_relationships),
        ):
            response = self.client.post(
                "/transcriptions",
                json={"sample_id": "sample-notation-1", "requested_assembly_mode": "gnn"},
            )

        self.assertEqual(response.status_code, 200)
        mode = response.json()["assembly_mode"]
        self.assertEqual(mode["applied_mode"], "gnn")
        self.assertTrue(mode["checkpoint_ready"])
        self.assertTrue(mode["inference_ran"])
        self.assertEqual(mode["adapter_name"], "fake-ready-adapter")

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
