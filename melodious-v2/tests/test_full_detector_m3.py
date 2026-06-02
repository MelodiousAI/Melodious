import tempfile
import unittest
from pathlib import Path

from melodious_v2.evaluation.full_detector import (
    detector_metrics_from_ultralytics,
    materialize_yolo_dataset,
    summarize_ultralytics_results_csv,
    write_detector_run_analysis,
)
from scripts.run_detection_136class_yolo import existing_yolo_dataset_manifest, parse_args


class FullDetectorM3Tests(unittest.TestCase):
    def test_materialize_yolo_dataset_writes_standard_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_images = root / "source_images"
            manifest_dir = root / "manifest"
            output_dir = root / "materialized"
            source_images.mkdir()

            names = "\n".join(f"  {index}: class{index}" for index in range(136))
            (manifest_dir / "yolo_dataset.yaml").parent.mkdir(parents=True)
            (manifest_dir / "yolo_dataset.yaml").write_text(
                "path: .\ntrain: generated/image_lists/train.txt\nval: generated/image_lists/val.txt\ntest: generated/image_lists/test.txt\nnc: 136\nnames:\n"
                + names
                + "\n",
                encoding="utf-8",
            )

            for split in ("train", "val", "test"):
                image = source_images / f"{split}.png"
                image.write_bytes(b"image")
                image_list = manifest_dir / "generated" / "image_lists" / f"{split}.txt"
                label_dir = manifest_dir / "generated" / "labels" / split
                image_list.parent.mkdir(parents=True, exist_ok=True)
                label_dir.mkdir(parents=True, exist_ok=True)
                image_list.write_text(str(image) + "\n", encoding="utf-8")
                (label_dir / f"{split}.txt").write_text("0 0.5 0.5 0.1 0.1\n", encoding="utf-8")

            manifest = materialize_yolo_dataset(
                manifest_dir=manifest_dir,
                output_dir=output_dir,
                generated_at="2026-05-20T00:00:00Z",
            )

            self.assertEqual(manifest["class_count"], 136)
            self.assertTrue((output_dir / "dataset.yaml").exists())
            for split in ("train", "val", "test"):
                self.assertTrue((output_dir / "images" / split / f"{split}.png").exists())
                self.assertTrue((output_dir / "labels" / split / f"{split}.txt").exists())
                self.assertEqual(manifest["splits"][split]["materialized_image_count"], 1)
                self.assertEqual(manifest["splits"][split]["materialized_label_count"], 1)

    def test_detector_metrics_from_ultralytics_normalizes_keys(self):
        class Result:
            results_dict = {
                "metrics/precision(B)": 0.75,
                "metrics/recall(B)": 0.5,
                "metrics/mAP50(B)": 0.4,
                "metrics/mAP50-95(B)": 0.2,
            }

        metrics = detector_metrics_from_ultralytics(Result())

        self.assertEqual(metrics["primary_metric"], "mAP@0.5:0.95")
        self.assertAlmostEqual(metrics["mAP@0.5:0.95"], 0.2)
        self.assertAlmostEqual(metrics["mAP@0.5"], 0.4)
        self.assertAlmostEqual(metrics["precision@0.5"], 0.75)
        self.assertAlmostEqual(metrics["recall@0.5"], 0.5)
        self.assertAlmostEqual(metrics["F1@0.5"], 0.6)

    def test_summarize_ultralytics_results_csv_selects_best_epoch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.csv"
            path.write_text(
                "\n".join(
                    [
                        "epoch,time,train/box_loss,train/cls_loss,train/dfl_loss,metrics/precision(B),metrics/recall(B),metrics/mAP50(B),metrics/mAP50-95(B),val/box_loss,val/cls_loss,val/dfl_loss",
                        "1,10,1.0,2.0,3.0,0.4,0.3,0.5,0.2,1.1,2.1,3.1",
                        "2,20,0.9,1.9,2.9,0.6,0.5,0.7,0.4,1.0,2.0,3.0",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            summary = summarize_ultralytics_results_csv(path)

            self.assertTrue(summary["exists"])
            self.assertEqual(summary["row_count"], 2)
            self.assertEqual(summary["last_completed"]["epoch"], 2)
            self.assertEqual(summary["best_by_mAP@0.5:0.95"]["epoch"], 2)
            self.assertAlmostEqual(summary["best_by_mAP@0.5:0.95"]["mAP@0.5:0.95"], 0.4)

    def test_parse_args_accepts_validation_augmentation_flag(self):
        args = parse_args(
            [
                "--finalize-existing-run",
                "--val-augment",
                "--max-det",
                "2000",
                "--nms-iou",
                "0.8",
                "--resume-training",
                "--resume-checkpoint",
                "last.pt",
            ]
        )

        self.assertTrue(args.finalize_existing_run)
        self.assertTrue(args.val_augment)
        self.assertEqual(args.max_det, 2000)
        self.assertAlmostEqual(args.nms_iou, 0.8)
        self.assertTrue(args.resume_training)
        self.assertEqual(args.resume_checkpoint, "last.pt")

    def test_parse_args_accepts_existing_dataset_yaml(self):
        args = parse_args(
            [
                "--dataset-yaml",
                "runs/data/tiled/dataset.yaml",
                "--dataset-id",
                "tiled_stem",
            ]
        )

        self.assertEqual(args.dataset_yaml, "runs/data/tiled/dataset.yaml")
        self.assertEqual(args.dataset_id, "tiled_stem")

    def test_existing_yolo_dataset_manifest_counts_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "dataset"
            names = "\n".join(f"  {index}: class{index}" for index in range(136))
            (dataset / "dataset.yaml").parent.mkdir(parents=True)
            (dataset / "dataset.yaml").write_text(
                f"path: {dataset.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnc: 136\nnames:\n"
                + names
                + "\n",
                encoding="utf-8",
            )
            for split in ("train", "val", "test"):
                (dataset / "images" / split).mkdir(parents=True)
                (dataset / "labels" / split).mkdir(parents=True)
                (dataset / "images" / split / "tile.png").write_bytes(b"image")
                (dataset / "labels" / split / "tile.txt").write_text(
                    "41 0.5 0.5 0.02 0.7\n0 0.2 0.2 0.1 0.1\n",
                    encoding="utf-8",
                )

            manifest = existing_yolo_dataset_manifest(dataset / "dataset.yaml", dataset_id="unit_tiled")

            self.assertEqual(manifest["dataset_id"], "unit_tiled")
            self.assertEqual(manifest["splits"]["train"]["image_count"], 1)
            self.assertEqual(manifest["splits"]["train"]["materialized_label_count"], 1)
            self.assertEqual(manifest["splits"]["train"]["class_counts"]["class41"], 1)

    def test_existing_yolo_dataset_manifest_accepts_list_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset = root / "dataset"
            names = "\n".join(f"  - class{index}" for index in range(136))
            (dataset / "dataset.yaml").parent.mkdir(parents=True)
            (dataset / "dataset.yaml").write_text(
                f"path: {dataset.as_posix()}\ntrain: images/train\nval: images/val\ntest: images/test\nnc: 136\nnames:\n"
                + names
                + "\n",
                encoding="utf-8",
            )
            for split in ("train", "val", "test"):
                (dataset / "images" / split).mkdir(parents=True)
                (dataset / "labels" / split).mkdir(parents=True)

            manifest = existing_yolo_dataset_manifest(dataset / "dataset.yaml")

            self.assertEqual(manifest["class_count"], 136)
            self.assertIn("class41", manifest["splits"]["train"]["class_counts"])

    def test_write_detector_run_analysis_uses_metrics_and_split_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "run"
            run_dir.mkdir()
            split_manifest = root / "val.json"
            (run_dir / "metrics.json").write_text(
                """
{
  "provenance": {
    "run_id": "unit",
    "dataset_id": "dataset",
    "split": "val",
    "taxonomy_id": "deepscores_136"
  },
  "metrics": {
    "primary_metric": "mAP@0.5:0.95",
    "mAP@0.5:0.95": 0.25,
    "mAP@0.5": 0.5,
    "precision@0.5": 0.75,
    "recall@0.5": 0.5,
    "F1@0.5": 0.6,
    "per_class_mAP@0.5:0.95": {
      "accidentalSharp": 0.0,
      "clefG": 0.5
    }
  }
}
""",
                encoding="utf-8",
            )
            split_manifest.write_text(
                """
{
  "class_counts": {
    "accidentalSharp": 5,
    "clefG": 20,
    "stem": 0
  }
}
""",
                encoding="utf-8",
            )

            analysis = write_detector_run_analysis(run_dir=run_dir, split_manifest=split_manifest)

            self.assertEqual(analysis["summary"]["supported_class_count"], 2)
            self.assertEqual(analysis["summary"]["rare_class_count_support_lte_10"], 1)
            self.assertEqual(analysis["summary"]["zero_map_supported_class_count"], 1)
            self.assertTrue((run_dir / "analysis.json").exists())
            self.assertTrue((run_dir / "analysis.md").exists())


if __name__ == "__main__":
    unittest.main()
