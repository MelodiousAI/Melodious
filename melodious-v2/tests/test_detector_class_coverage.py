import json
import tempfile
import unittest
from pathlib import Path

from melodious_v2.evaluation.class_coverage import (
    build_class_coverage_audit,
    write_class_coverage_report,
)


class DetectorClassCoverageTests(unittest.TestCase):
    def test_audit_separates_training_gaps_validation_blind_spots_and_zero_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_dir = root / "manifest"
            manifest_dir.mkdir()
            class_names = ["seen_good", "seen_zero", "train_only", "zero_data"]

            payloads = {
                "train": {
                    "image_count": 3,
                    "annotation_count": 17,
                    "class_counts": {
                        "seen_good": 10,
                        "seen_zero": 5,
                        "train_only": 2,
                        "zero_data": 0,
                    },
                },
                "val": {
                    "image_count": 1,
                    "annotation_count": 4,
                    "class_counts": {
                        "seen_good": 3,
                        "seen_zero": 1,
                        "train_only": 0,
                        "zero_data": 0,
                    },
                },
                "test": {
                    "image_count": 1,
                    "annotation_count": 2,
                    "class_counts": {
                        "seen_good": 2,
                        "seen_zero": 0,
                        "train_only": 0,
                        "zero_data": 0,
                    },
                },
            }
            for split, payload in payloads.items():
                (manifest_dir / f"{split}.json").write_text(json.dumps(payload), encoding="utf-8")

            metrics_path = root / "metrics.json"
            metrics_path.write_text(
                json.dumps(
                    {
                        "provenance": {
                            "run_id": "unit",
                            "split": "val",
                            "artifact_sha256": "abc",
                        },
                        "metrics": {
                            "primary_metric": "mAP@0.5:0.95",
                            "mAP@0.5:0.95": 0.5,
                            "mAP@0.5": 0.7,
                            "precision@0.5": 0.8,
                            "recall@0.5": 0.6,
                            "F1@0.5": 0.6857142857,
                            "per_class_mAP@0.5:0.95": {
                                "seen_good": 0.4,
                                "seen_zero": 0.0,
                                "train_only": 0.5,
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )

            audit = build_class_coverage_audit(
                manifest_dir=manifest_dir,
                metrics_path=metrics_path,
                class_names=class_names,
                high_support_threshold=1,
                generated_at="2026-06-01T00:00:00Z",
            )

            summary = audit["summary"]
            self.assertEqual(summary["class_count"], 4)
            self.assertEqual(summary["splits"]["train"]["supported_class_count"], 3)
            self.assertEqual(summary["splits"]["val"]["supported_class_count"], 2)
            self.assertEqual(summary["zero_data_classes"], ["zero_data"])
            self.assertEqual(summary["train_supported_val_absent_classes"], ["train_only"])
            self.assertEqual(summary["zero_map_supported_classes"], ["seen_zero"])
            self.assertEqual(summary["unsupported_metric_value_count"], 1)

            train_only = next(row for row in audit["per_class"] if row["class_name"] == "train_only")
            self.assertIsNone(train_only["mAP@0.5:0.95"])
            self.assertTrue(train_only["raw_map_ignored_because_no_evaluation_support"])

    def test_write_class_coverage_report_writes_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_dir = root / "manifest"
            manifest_dir.mkdir()
            for split in ("train", "val", "test"):
                (manifest_dir / f"{split}.json").write_text(
                    json.dumps(
                        {
                            "image_count": 1,
                            "annotation_count": 1,
                            "class_counts": {"a": 1},
                        }
                    ),
                    encoding="utf-8",
                )

            audit = build_class_coverage_audit(
                manifest_dir=manifest_dir,
                class_names=["a"],
                generated_at="2026-06-01T00:00:00Z",
            )
            outputs = write_class_coverage_report(audit=audit, output_dir=root / "out")

            self.assertTrue(Path(outputs["json"]).exists())
            self.assertTrue(Path(outputs["markdown"]).exists())


if __name__ == "__main__":
    unittest.main()
