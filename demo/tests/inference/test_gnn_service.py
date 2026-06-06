import os
import tempfile
import unittest
from unittest.mock import patch

from src.inference.gnn_service import CHECKPOINT_ENV_VAR, GnnAssemblyService


class ReadyAdapter:
    name = "ready-test-adapter"

    def is_ready(self):
        return True

    def predict(self, graph_data, detection_sequence, document_name=None):
        return {}


class TestGnnAssemblyService(unittest.TestCase):
    def test_runtime_status_reports_missing_checkpoint_when_unconfigured(self):
        with patch.dict(os.environ, {}, clear=True):
            status = GnnAssemblyService().get_runtime_status()

        self.assertEqual(status.adapter_name, "checkpoint-scaffold")
        self.assertFalse(status.adapter_ready)
        self.assertFalse(status.checkpoint_configured)
        self.assertFalse(status.checkpoint_exists)
        self.assertFalse(status.ready)
        self.assertIn(CHECKPOINT_ENV_VAR, status.message)

    def test_runtime_status_reports_ready_when_checkpoint_and_adapter_are_available(self):
        with tempfile.NamedTemporaryFile(suffix=".pt") as handle:
            status = GnnAssemblyService(
                checkpoint_path=handle.name,
                adapter=ReadyAdapter(),
            ).get_runtime_status()

        self.assertEqual(status.adapter_name, "ready-test-adapter")
        self.assertTrue(status.adapter_ready)
        self.assertTrue(status.checkpoint_configured)
        self.assertTrue(status.checkpoint_exists)
        self.assertTrue(status.ready)
        self.assertIn("ready for inference", status.message)

    def test_auto_mode_switches_to_gnn_when_runtime_is_ready(self):
        with tempfile.NamedTemporaryFile(suffix=".pt") as handle:
            decision = GnnAssemblyService(
                checkpoint_path=handle.name,
                adapter=ReadyAdapter(),
            ).resolve_assembly_mode("auto")

        self.assertEqual(decision.requested_mode, "auto")
        self.assertEqual(decision.applied_mode, "gnn")
        self.assertFalse(decision.fallback_applied)
        self.assertTrue(decision.checkpoint_ready)

    def test_gnn_mode_falls_back_when_checkpoint_path_is_missing(self):
        missing_checkpoint = "outputs/checkpoints/missing-week4.pt"
        decision = GnnAssemblyService(
            checkpoint_path=missing_checkpoint,
            adapter=ReadyAdapter(),
        ).resolve_assembly_mode("gnn")

        self.assertEqual(decision.requested_mode, "gnn")
        self.assertEqual(decision.applied_mode, "heuristic")
        self.assertTrue(decision.fallback_applied)
        self.assertFalse(decision.checkpoint_ready)
        self.assertIn("not found", decision.fallback_reason)
        self.assertTrue(any("Falling back to heuristic mode" in warning for warning in decision.warnings))


if __name__ == "__main__":
    unittest.main()
