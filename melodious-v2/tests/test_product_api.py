"""Tests for the real product upload API (`/product/*`).

These tests force the model-free CV fallback extractor by patching the checkpoint
resolvers to return ``None``. That keeps the suite fast and offline while still
exercising the full upload -> background job -> artifact-serving lifecycle.
"""

from __future__ import annotations

import io
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from melodious_v2.api.app import app
from melodious_v2.api import product_service


def _synthetic_staff_png() -> bytes:
    image = Image.new("L", (480, 200), color=255)
    draw = ImageDraw.Draw(image)
    for y in (70, 80, 90, 100, 110):
        draw.line((40, y, 440, y), fill=0, width=1)
    for x, y in [(150, 105), (200, 95), (250, 85), (300, 95), (350, 105)]:
        draw.ellipse((x - 6, y - 4, x + 6, y + 4), fill=0)
        draw.line((x + 6, y, x + 6, y - 38), fill=0, width=2)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class ProductApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        # Force the offline CV fallback path for fast, model-free tests.
        self._patches = [
            patch.object(product_service, "resolve_detector_checkpoint", return_value=None),
            patch.object(product_service, "resolve_thin_symbol_checkpoint", return_value=None),
            patch.object(product_service, "resolve_gnn_checkpoint", return_value=None),
        ]
        for item in self._patches:
            item.start()

    def tearDown(self) -> None:
        for item in self._patches:
            item.stop()

    def _wait_for_job(self, job_id: str, timeout: float = 30.0) -> dict:
        deadline = time.time() + timeout
        payload: dict = {}
        while time.time() < deadline:
            response = self.client.get(f"/product/jobs/{job_id}")
            self.assertEqual(response.status_code, 200)
            payload = response.json()
            if payload["status"] in {"complete", "failed"}:
                return payload
            time.sleep(0.2)
        self.fail(f"Job {job_id} did not finish within {timeout}s; last status={payload.get('status')}")

    def test_existing_routes_still_work(self) -> None:
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/version").status_code, 200)
        self.assertEqual(self.client.get("/samples").status_code, 200)

    def test_product_models_and_samples(self) -> None:
        models = self.client.get("/product/models")
        self.assertEqual(models.status_code, 200)
        body = models.json()
        self.assertIn("availability", body)
        self.assertIn("Piano", body["instruments"])

        samples = self.client.get("/product/samples")
        self.assertEqual(samples.status_code, 200)
        self.assertEqual(len(samples.json()), 3)

    def test_unsupported_file_type_is_rejected(self) -> None:
        response = self.client.post(
            "/product/transcribe-image",
            files={"file": ("notes.txt", b"not an image", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)

    def test_unknown_job_returns_404(self) -> None:
        self.assertEqual(self.client.get("/product/jobs/job_missing").status_code, 404)

    def test_full_upload_lifecycle_and_artifacts(self) -> None:
        response = self.client.post(
            "/product/transcribe-image",
            files={"file": ("staff.png", _synthetic_staff_png(), "image/png")},
            data={"instrument": "Flute"},
        )
        self.assertEqual(response.status_code, 200)
        started = response.json()
        self.assertIn(started["status"], {"queued", "processing"})
        job_id = started["job_id"]

        result = self._wait_for_job(job_id)
        self.assertEqual(result["status"], "complete", msg=result.get("error"))
        self.assertGreaterEqual(result["counts"]["notes"], 1)
        self.assertEqual(result["metric_claim"], "none")
        self.assertEqual(result["model_provenance"]["extractor_mode"], "cv_staff_notehead_pitch")
        self.assertTrue(result["note_events"])

        for name in ("original", "overlay", "musicxml", "midi", "notes", "bundle"):
            artifact = self.client.get(f"/product/jobs/{job_id}/artifacts/{name}")
            self.assertEqual(artifact.status_code, 200, msg=f"artifact {name} failed")
            self.assertTrue(artifact.content)

        # Instrument-specific MIDI re-render.
        flute_midi = self.client.get(f"/product/jobs/{job_id}/artifacts/midi", params={"instrument": "Flute"})
        self.assertEqual(flute_midi.status_code, 200)
        self.assertEqual(flute_midi.headers["content-type"], "audio/midi")

        # Download variant sets an attachment filename.
        download = self.client.get(
            f"/product/jobs/{job_id}/artifacts/musicxml", params={"download": "true"}
        )
        self.assertEqual(download.status_code, 200)
        self.assertIn("attachment", download.headers.get("content-disposition", ""))

        # Unknown artifact name is a 400 once the job exists.
        self.assertEqual(
            self.client.get(f"/product/jobs/{job_id}/artifacts/nonsense").status_code, 400
        )


if __name__ == "__main__":
    unittest.main()
