import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DETECTIONS_DIR = PROJECT_ROOT / "sample_detections"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.app import app
from src.api.models import MidiResponse


class TestApiApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def load_payload(self, relative_path):
        payload_path = PROJECT_ROOT / relative_path

        with payload_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_health_endpoint_returns_week_2_service_status(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "melodious-backend",
                "stage": "v0.3",
            },
        )

    def test_assemble_endpoint_builds_graph_from_generic_reference_payload(self):
        payload_path = next((SAMPLE_DETECTIONS_DIR / "reference").glob("*.json"))

        with payload_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        response = self.client.post(
            "/assemble",
            json={
                "payload": payload,
                "payload_kind": "generic",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["payload_kind"], "generic")
        self.assertGreater(body["detection_count"], 0)
        self.assertGreater(body["graph_statistics"]["num_nodes"], 0)
        self.assertGreater(body["graph_statistics"]["num_edges"], 0)
        self.assertIsNone(body["graph_data"])

    def test_assemble_endpoint_can_return_serialized_graph_arrays(self):
        payload_path = next((SAMPLE_DETECTIONS_DIR / "reference").glob("*.json"))

        with payload_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        response = self.client.post(
            "/assemble",
            json={
                "payload": payload,
                "payload_kind": "generic",
                "include_graph_data": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        graph_data = response.json()["graph_data"]
        self.assertIsNotNone(graph_data)
        self.assertGreater(len(graph_data["node_feature_names"]), 0)
        self.assertGreater(len(graph_data["edge_feature_names"]), 0)
        self.assertGreater(len(graph_data["node_features"]), 0)
        self.assertEqual(len(graph_data["edge_index"]), 2)

    def test_assemble_serialized_graph_preserves_input_detection_order(self):
        payload = {
            "image_path": "demo\\ordering_check.png",
            "image_size": {"width": 1000, "height": 500},
            "detections": [
                {
                    "class_id": 91,
                    "class_name": "symbol-a",
                    "confidence": 0.91,
                    "bbox": {
                        "x_center": 0.80,
                        "y_center": 0.20,
                        "width": 0.04,
                        "height": 0.08,
                    },
                },
                {
                    "class_id": 52,
                    "class_name": "symbol-b",
                    "confidence": 0.82,
                    "bbox": {
                        "x_center": 0.15,
                        "y_center": 0.75,
                        "width": 0.03,
                        "height": 0.06,
                    },
                },
                {
                    "class_id": 73,
                    "class_name": "symbol-c",
                    "confidence": 0.77,
                    "bbox": {
                        "x_center": 0.45,
                        "y_center": 0.42,
                        "width": 0.05,
                        "height": 0.07,
                    },
                },
            ],
        }

        response = self.client.post(
            "/assemble",
            json={
                "payload": payload,
                "payload_kind": "generic",
                "include_graph_data": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        graph_data = body["graph_data"]
        node_features = graph_data["node_features"]
        edge_index = graph_data["edge_index"]

        self.assertEqual(body["detection_count"], 3)
        self.assertEqual(body["graph_statistics"]["num_nodes"], 3)

        self.assertEqual([row[0] for row in node_features], [91.0, 52.0, 73.0])
        self.assertAlmostEqual(node_features[0][1], 0.80)
        self.assertAlmostEqual(node_features[0][2], 0.20)
        self.assertAlmostEqual(node_features[1][1], 0.15)
        self.assertAlmostEqual(node_features[1][2], 0.75)
        self.assertAlmostEqual(node_features[2][1], 0.45)
        self.assertAlmostEqual(node_features[2][2], 0.42)

        edge_pairs = list(zip(edge_index[0], edge_index[1]))
        self.assertGreater(len(edge_pairs), 0)

        for source_index, target_index in edge_pairs:
            self.assertIn(source_index, [0, 1, 2])
            self.assertIn(target_index, [0, 1, 2])

    def test_midi_endpoint_returns_inline_export_content(self):
        payload_path = next((SAMPLE_DETECTIONS_DIR / "reference").glob("*.json"))

        with payload_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        mocked_response = MidiResponse(
            status="ok",
            stage="v0.3",
            output_format="musicxml",
            content_type="application/vnd.recordare.musicxml+xml",
            content_encoding="utf-8",
            document_name="demo-score",
            title="Demo Score",
            detection_count=3,
            assembly_summary={
                "note_count": 2,
                "clef_count": 1,
                "rest_count": 0,
                "unmatched_count": 0,
            },
            content="<score-partwise />",
            warnings=[],
        )

        with patch("src.api.app.export_from_request", return_value=mocked_response) as mocked_export:
            response = self.client.post(
                "/midi",
                json={
                    "payload": payload,
                    "output_format": "musicxml",
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["stage"], "v0.3")
        self.assertEqual(body["output_format"], "musicxml")
        self.assertEqual(body["content_encoding"], "utf-8")
        self.assertEqual(body["content"], "<score-partwise />")
        mocked_export.assert_called_once()

    def test_midi_endpoint_returns_503_when_music21_is_unavailable(self):
        payload_path = next((SAMPLE_DETECTIONS_DIR / "reference").glob("*.json"))

        with payload_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        with patch("src.api.app.export_from_request", side_effect=ImportError("music21 missing")):
            response = self.client.post(
                "/midi",
                json={
                    "payload": payload,
                    "output_format": "midi",
                },
            )

        self.assertEqual(response.status_code, 503)
        self.assertIn("music21 missing", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
