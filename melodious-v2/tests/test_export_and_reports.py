import tempfile
import unittest
from pathlib import Path

from melodious_v2.api.service import _sample_payload
from melodious_v2.contracts import MetricProvenance
from melodious_v2.export.musicxml import payload_to_musicxml, validate_musicxml
from melodious_v2.reports import assert_no_cross_metric_claims, write_run_report


class ExportAndReportTests(unittest.TestCase):
    def test_musicxml_validates(self):
        content = payload_to_musicxml(_sample_payload())
        self.assertTrue(validate_musicxml(content))

    def test_rejects_map_f1_comparison(self):
        with self.assertRaises(ValueError):
            assert_no_cross_metric_claims("mAP50 >= 0.27 F1 target")

    def test_write_run_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run"
            write_run_report(
                run_dir,
                MetricProvenance(
                    run_id="unit",
                    commit="abc123",
                    config_path="configs/unit.yaml",
                    dataset_id="tiny",
                    split="test",
                    taxonomy_id="deepscores_136",
                ),
                {
                    "primary_metric": "mAP@0.5:0.95",
                    "mAP@0.5:0.95": 1.0,
                    "mAP@0.5": 1.0,
                    "precision@0.5": 1.0,
                    "recall@0.5": 1.0,
                    "F1@0.5": 1.0,
                },
            )
            self.assertTrue((run_dir / "metrics.json").exists())
            self.assertTrue((run_dir / "report.md").exists())
            report = (run_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("## Secondary Metrics", report)
            self.assertIn("`F1@0.5`", report)


if __name__ == "__main__":
    unittest.main()
