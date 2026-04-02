import json
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DETECTIONS_DIR = PROJECT_ROOT / "sample_detections"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.api.app import app


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
                "stage": "v0.2",
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

    def test_midi_endpoint_is_present_but_not_yet_implemented(self):
        response = self.client.post("/midi", json={"payload": None})

        self.assertEqual(response.status_code, 501)
        self.assertEqual(response.json()["status"], "not_implemented")
        self.assertEqual(response.json()["stage"], "v0.2")


if __name__ == "__main__":
    unittest.main()
