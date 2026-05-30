import tempfile
import unittest
from dataclasses import dataclass, field
from pathlib import Path

from melodious_v2.api.service import _sample_payload
from melodious_v2.assembly.service import Relationship, assemble_payload


@dataclass(frozen=True)
class FakePrediction:
    relationships: list[Relationship]
    edges: list[tuple[int, int]] = field(default_factory=list)
    predicted_labels: list[int] = field(default_factory=list)
    confidences: list[float] = field(default_factory=list)
    inference_ran: bool = True
    warnings: list[str] = field(default_factory=list)


class FakeReadyAdapter:
    name = "fake_ready_gnn"

    def predict_payload(self, payload):
        return FakePrediction(
            relationships=[Relationship(0, 1, "stem_notehead", 0.91)],
            edges=[(0, 1)],
            predicted_labels=[1],
            confidences=[0.91],
            inference_ran=True,
        )


class AssemblyGnnRuntimeTests(unittest.TestCase):
    def test_gnn_mode_is_only_reported_after_adapter_inference(self):
        mode, relationships = assemble_payload(
            _sample_payload(),
            requested_mode="gnn",
            gnn_adapter=FakeReadyAdapter(),
        )

        self.assertEqual(mode.applied_mode, "gnn")
        self.assertTrue(mode.checkpoint_ready)
        self.assertTrue(mode.inference_ran)
        self.assertFalse(mode.fallback_applied)
        self.assertEqual(mode.adapter_name, "fake_ready_gnn")
        self.assertEqual(len(relationships), 1)

    def test_missing_checkpoint_is_explicit_and_uses_fallback_relationships(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = str(Path(temp_dir) / "missing.pt")
            mode, relationships = assemble_payload(
                _sample_payload(),
                requested_mode="gnn",
                checkpoint_path=missing_path,
            )

        self.assertEqual(mode.applied_mode, "checkpoint_missing")
        self.assertTrue(mode.fallback_applied)
        self.assertFalse(mode.checkpoint_ready)
        self.assertIn("checkpoint_missing", mode.fallback_reason)
        self.assertGreaterEqual(len(relationships), 1)

    def test_bad_checkpoint_does_not_claim_gnn(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bad_checkpoint = Path(temp_dir) / "bad.pt"
            bad_checkpoint.write_text("not a torch checkpoint", encoding="utf-8")
            mode, relationships = assemble_payload(
                _sample_payload(),
                requested_mode="gnn",
                checkpoint_path=str(bad_checkpoint),
            )

        self.assertEqual(mode.applied_mode, "heuristic_fallback")
        self.assertTrue(mode.fallback_applied)
        self.assertFalse(mode.inference_ran)
        self.assertIn("gnn_adapter_error", mode.fallback_reason)
        self.assertGreaterEqual(len(relationships), 1)


if __name__ == "__main__":
    unittest.main()
