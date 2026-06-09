import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.app import app


class TestProductRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_product_config_exposes_week_5_flags(self):
        response = self.client.get("/product/config")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["app_name"], "Melodious")
        self.assertEqual(body["stage"], "v0.5")
        self.assertEqual(body["active_experience"], "sample_first")
        self.assertFalse(body["feature_flags"]["image_upload_enabled"])
        self.assertFalse(body["feature_flags"]["attention_overlay_enabled"])
        self.assertFalse(body["feature_flags"]["llm_explainer_enabled"])

    def test_product_samples_lists_curated_muscima_samples(self):
        response = self.client.get("/product/samples")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertGreaterEqual(len(body["items"]), 5)
        first_sample = body["items"][0]
        self.assertIn("id", first_sample)
        self.assertIn("title", first_sample)
        self.assertIn("preview_image_url", first_sample)
        self.assertEqual(first_sample["preview_image_url"], f"/product/samples/{first_sample['id']}/image")
        self.assertIn("MUSCIMA++", first_sample["tags"])

    def test_product_sample_image_resolves_repo_local_png(self):
        response = self.client.get("/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/image")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "image/png")
        self.assertGreater(len(response.content), 0)

    def test_product_transcribe_returns_merged_public_contract(self):
        response = self.client.post(
            "/product/transcribe",
            json={"sample_id": "CVC-MUSCIMA_W-01_N-10_D-ideal"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["sample"]["id"], "CVC-MUSCIMA_W-01_N-10_D-ideal")
        self.assertEqual(body["score_preview"]["image_url"], "/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/image")
        self.assertGreater(body["transcription_summary"]["detection_count"], 0)
        self.assertIn(body["confidence_indicator"]["tone"], ["high", "medium", "low"])
        self.assertFalse(body["confidence_indicator"]["calibrated"])
        self.assertEqual(body["explainability"]["state"], "placeholder")
        self.assertIn("attention", body["explainability"]["title"].lower())
        self.assertTrue(body["downloads"]["musicxml"]["ready"])
        self.assertTrue(body["downloads"]["midi"]["ready"])
        self.assertEqual(
            body["downloads"]["musicxml"]["url"],
            "/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/musicxml",
        )
        self.assertTrue(body["audio"]["playable"])
        self.assertEqual(
            body["audio"]["source_url"],
            "/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/midi",
        )
        self.assertFalse(body["feature_flags"]["image_upload_enabled"])

    def test_product_sample_download_returns_musicxml(self):
        response = self.client.get("/product/samples/CVC-MUSCIMA_W-01_N-10_D-ideal/downloads/musicxml")

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/vnd.recordare.musicxml+xml", response.headers["content-type"])
        self.assertIn("attachment;", response.headers["content-disposition"])
        self.assertIn(b"<score-partwise", response.content)


if __name__ == "__main__":
    unittest.main()
