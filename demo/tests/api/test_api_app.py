import json
import os
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

    def test_health_endpoint_returns_week_4_service_status(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["service"], "melodious-backend")
        self.assertEqual(body["stage"], "v0.4")
        self.assertEqual(body["available_assembly_modes"], ["auto", "heuristic", "gnn"])
        self.assertEqual(body["default_assembly_mode"], "auto")
        self.assertEqual(body["gnn_status"]["adapter_name"], "checkpoint-scaffold")
        self.assertFalse(body["gnn_status"]["adapter_ready"])
        self.assertFalse(body["gnn_status"]["checkpoint_configured"])
        self.assertFalse(body["gnn_status"]["checkpoint_exists"])
        self.assertFalse(body["gnn_status"]["ready"])
        self.assertIn("MELODIOUS_GNN_CHECKPOINT", body["gnn_status"]["message"])

    def test_assemble_endpoint_builds_graph_from_generic_reference_payload(self):
        payload_path = next((SAMPLE_DETECTIONS_DIR / "reference").glob("*.json"))

        with payload_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        with patch.dict(os.environ, {}, clear=True):
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
        self.assertEqual(body["stage"], "v0.4")
        self.assertEqual(body["payload_kind"], "generic")
        self.assertGreater(body["detection_count"], 0)
        self.assertGreater(body["graph_statistics"]["num_nodes"], 0)
        self.assertGreater(body["graph_statistics"]["num_edges"], 0)
        self.assertEqual(body["assembly_mode"]["requested_mode"], "auto")
        self.assertEqual(body["assembly_mode"]["applied_mode"], "heuristic")
        self.assertFalse(body["assembly_mode"]["fallback_applied"])
        self.assertFalse(body["assembly_mode"]["checkpoint_ready"])
        self.assertIn("note_count", body["assembly_summary"])
        self.assertFalse(body["attention_preview"]["available"])
        self.assertIsNone(body["graph_data"])

    def test_assemble_endpoint_can_return_serialized_graph_arrays(self):
        payload_path = next((SAMPLE_DETECTIONS_DIR / "reference").glob("*.json"))

        with payload_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        with patch.dict(os.environ, {}, clear=True):
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

    def test_assemble_endpoint_falls_back_when_gnn_mode_is_requested_without_checkpoint(self):
        payload_path = next((SAMPLE_DETECTIONS_DIR / "model_outputs_quick").glob("*.json"))

        with payload_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post(
                "/assemble",
                json={
                    "payload": payload,
                    "payload_kind": "generic",
                    "assembly_mode": "gnn",
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["assembly_mode"]["requested_mode"], "gnn")
        self.assertEqual(body["assembly_mode"]["applied_mode"], "heuristic")
        self.assertTrue(body["assembly_mode"]["fallback_applied"])
        self.assertFalse(body["assembly_mode"]["checkpoint_ready"])
        self.assertIn("MELODIOUS_GNN_CHECKPOINT", body["assembly_mode"]["fallback_reason"])
        self.assertTrue(any("Falling back to heuristic mode" in warning for warning in body["warnings"]))
        self.assertIn("fell back to heuristic mode", body["attention_preview"]["message"])

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

        with patch.dict(os.environ, {}, clear=True):
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
            stage="v0.4",
            output_format="musicxml",
            content_type="application/vnd.recordare.musicxml+xml",
            content_encoding="utf-8",
            document_name="demo-score",
            title="Demo Score",
            detection_count=3,
            assembly_mode={
                "requested_mode": "auto",
                "applied_mode": "heuristic",
                "fallback_applied": False,
                "fallback_reason": None,
                "checkpoint_ready": False,
            },
            assembly_summary={
                "note_count": 2,
                "clef_count": 1,
                "rest_count": 0,
                "unmatched_count": 0,
            },
            attention_preview={
                "available": False,
                "source": "placeholder",
                "message": "Attention preview is reserved for the future GNN checkpoint integration.",
                "top_edges": [],
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
        self.assertEqual(body["stage"], "v0.4")
        self.assertEqual(body["output_format"], "musicxml")
        self.assertEqual(body["content_encoding"], "utf-8")
        self.assertEqual(body["assembly_mode"]["applied_mode"], "heuristic")
        self.assertFalse(body["attention_preview"]["available"])
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
