import json
import tempfile
import unittest
from pathlib import Path

from melodious_v2.api.service import _sample_payload
from melodious_v2.contracts import MetricProvenance
from melodious_v2.evaluation.e2e_export import (
    PayloadBuildSummary,
    evaluate_page_export,
    summarize_page_results,
    write_e2e_run_outputs,
)


class E2EExportTests(unittest.TestCase):
    def test_e2e_artifact_manifest_writes_tiny_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            config = root / "config.yaml"
            config.write_text("run_family: unit\n", encoding="utf-8")
            source_manifest = root / "manifest.json"
            split_manifest = root / "holdout.json"
            source_manifest.write_text("{}", encoding="utf-8")
            split_manifest.write_text("{}", encoding="utf-8")

            payload_summary = PayloadBuildSummary(
                page_id="unit_page",
                source_xml="unit.xml",
                parsed_node_count=3,
                mapped_detection_count=3,
                skipped_node_count=0,
                mapped_class_counts={"noteheadBlackOnLine": 1, "stem": 1, "beam": 1},
                skipped_class_counts={},
            )
            result = evaluate_page_export(
                payload=_sample_payload(),
                payload_summary=payload_summary,
                page_dir=run_dir / "exports" / "unit_page",
                requested_assembly_mode="heuristic",
                checkpoint_path=None,
            )
            metrics = summarize_page_results([result])
            write_e2e_run_outputs(
                run_dir=run_dir,
                provenance=MetricProvenance(
                    run_id="unit_e2e",
                    commit="abc123",
                    config_path="config.yaml",
                    dataset_id="tiny",
                    split="holdout",
                    taxonomy_id="deepscores_136_to_semantic_omr_v2",
                ),
                metrics=metrics,
                page_results=[result],
                source_manifest_path=source_manifest,
                split_manifest_path=split_manifest,
                config_path=config,
                upstream_artifacts={"detector_source": {"mode": "fixture"}},
            )

            self.assertTrue((run_dir / "metrics.json").exists())
            self.assertTrue((run_dir / "manifest.json").exists())
            self.assertTrue((run_dir / "artifacts.json").exists())
            self.assertTrue((run_dir / "config.yaml").exists())
            artifacts = json.loads((run_dir / "artifacts.json").read_text(encoding="utf-8"))
            self.assertIn("unit_page", artifacts["page_artifacts"])
            self.assertEqual(metrics["musicxml_validity_rate"], 1.0)
            self.assertEqual(metrics["midi_generation_success_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
