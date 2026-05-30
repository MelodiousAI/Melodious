import json
import tempfile
import unittest
from pathlib import Path

from melodious_v2.evaluation.reduced_detection import (
    DEEPSCORES_TO_REDUCED_15_ID,
    REDUCED_15_NAME_TO_ID,
    write_reduced_repro_run,
)


class DetectionReproTests(unittest.TestCase):
    def test_reduced_class_mapping_groups_deepscores_noteheads(self):
        self.assertEqual(
            DEEPSCORES_TO_REDUCED_15_ID["noteheadBlackOnLine"],
            REDUCED_15_NAME_TO_ID["notehead-full"],
        )
        self.assertEqual(
            DEEPSCORES_TO_REDUCED_15_ID["noteheadBlackInSpace"],
            REDUCED_15_NAME_TO_ID["notehead-full"],
        )

    def test_reduced_repro_run_writes_complete_metric_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            predictions_dir = root / "predictions"
            predictions_dir.mkdir()
            train_json = root / "deepscores_train.json"
            test_json = root / "deepscores_test.json"
            checkpoint = root / "best.pt"
            config = root / "config.yaml"
            run_dir = root / "runs" / "detection" / "unit"

            checkpoint.write_bytes(b"unit checkpoint")
            config.write_text("run_family: unit\n", encoding="utf-8")
            prediction_payload = {
                "image_path": "dataset_ds2_dense/images/page-1.png",
                "image_size": {"width": 100, "height": 100},
                "model": {"type": "unit", "checkpoint": str(checkpoint)},
                "detections": [
                    {
                        "class_id": 0,
                        "class_name": "notehead-full",
                        "confidence": 0.99,
                        "bbox_pixels": {"x1": 10, "y1": 10, "x2": 20, "y2": 20},
                        "bbox": {
                            "x_center": 0.15,
                            "y_center": 0.15,
                            "width": 0.1,
                            "height": 0.1,
                        },
                    }
                ],
            }
            (predictions_dir / "page-1.json").write_text(json.dumps(prediction_payload), encoding="utf-8")

            categories = {"1": {"name": "noteheadBlackOnLine", "annotation_set": "deepscores"}}
            train_json.write_text(
                json.dumps(
                    {
                        "categories": categories,
                        "images": [
                            {
                                "id": 1,
                                "filename": "page-1.png",
                                "width": 100,
                                "height": 100,
                                "ann_ids": ["a1"],
                            }
                        ],
                        "annotations": {"a1": {"a_bbox": [10, 10, 20, 20], "cat_id": ["1"]}},
                    }
                ),
                encoding="utf-8",
            )
            test_json.write_text(
                json.dumps({"categories": categories, "images": [], "annotations": {}}),
                encoding="utf-8",
            )

            result = write_reduced_repro_run(
                run_dir=run_dir,
                run_id="unit",
                config_path=config,
                predictions_dir=predictions_dir,
                train_json=train_json,
                test_json=test_json,
                checkpoint_path=checkpoint,
                commit="test",
                generated_at="2026-05-20T00:00:00Z",
            )

            self.assertEqual(result["manifest"]["class_count"], 15)
            self.assertEqual(result["manifest"]["image_count"], 1)
            self.assertEqual(result["manifest"]["prediction_count"], 1)
            self.assertEqual(result["manifest"]["target_count"], 1)
            self.assertEqual(result["metrics"]["mAP@0.5:0.95"], 1.0)
            self.assertTrue((run_dir / "metrics.json").exists())
            self.assertTrue((run_dir / "report.md").exists())
            self.assertTrue((run_dir / "manifest.json").exists())
            self.assertTrue((run_dir / "artifacts.json").exists())
            self.assertTrue((run_dir / "config.yaml").exists())

            metrics_payload = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
            self.assertEqual(metrics_payload["provenance"]["run_id"], "unit")
            self.assertEqual(metrics_payload["provenance"]["taxonomy_id"], "deepscores_15_reduced")
            self.assertIsNotNone(metrics_payload["provenance"]["artifact_sha256"])


if __name__ == "__main__":
    unittest.main()

