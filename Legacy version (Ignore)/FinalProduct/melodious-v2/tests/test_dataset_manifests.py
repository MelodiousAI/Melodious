import json
import tempfile
import unittest
from pathlib import Path

from melodious_v2.datasets.manifests import (
    build_deepscores_leakage_report,
    build_deepscores_manifest_run,
    build_muscima_manifest_run,
    deterministic_split,
)


class DatasetManifestTests(unittest.TestCase):
    def test_deterministic_split_is_repeatable(self):
        items = [{"id": index} for index in range(10)]

        first = deterministic_split(items, (("train", 0.8), ("val", 0.2)), 42, lambda item: item["id"])
        second = deterministic_split(items, (("train", 0.8), ("val", 0.2)), 42, lambda item: item["id"])

        self.assertEqual(first, second)
        self.assertEqual(len(first["train"]), 8)
        self.assertEqual(len(first["val"]), 2)
        self.assertEqual(
            sorted(item["id"] for split in first.values() for item in split),
            list(range(10)),
        )

    def test_deepscores_manifest_summaries_report_136_classes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            train_json = root / "deepscores_train.json"
            test_json = root / "deepscores_test.json"
            image_root = root / "images"
            image_root.mkdir()

            categories = {"1": {"name": "brace", "annotation_set": "deepscores"}}
            train_images = [
                {
                    "id": index,
                    "filename": f"lg-work-aug-style--page-{index}.png",
                    "width": 100,
                    "height": 100,
                    "ann_ids": [f"a{index}"],
                }
                for index in range(10)
            ]
            train_annotations = {
                f"a{index}": {"a_bbox": [10, 10, 20, 20], "cat_id": ["1"]}
                for index in range(10)
            }
            test_images = [
                {
                    "id": 100,
                    "filename": "lg-holdout-aug-style--page-1.png",
                    "width": 100,
                    "height": 100,
                    "ann_ids": ["t1"],
                }
            ]
            test_annotations = {"t1": {"a_bbox": [10, 10, 20, 20], "cat_id": ["1"]}}
            train_json.write_text(
                json.dumps({"categories": categories, "images": train_images, "annotations": train_annotations}),
                encoding="utf-8",
            )
            test_json.write_text(
                json.dumps({"categories": categories, "images": test_images, "annotations": test_annotations}),
                encoding="utf-8",
            )

            manifest = build_deepscores_manifest_run(
                train_json=train_json,
                test_json=test_json,
                image_root=image_root,
                output_dir=root / "runs" / "deepscores",
                generated_at="2026-05-12T00:00:00Z",
            )

            self.assertEqual(manifest["class_count"], 136)
            for split_summary in manifest["splits"].values():
                self.assertEqual(split_summary["class_count"], 136)

    def test_deepscores_duplicate_ids_across_splits_are_caught(self):
        split_manifests = {
            "train": {"images": [{"image_id": "same", "filename": "train.png"}]},
            "val": {"images": [{"image_id": "same", "filename": "val.png"}]},
            "test": {"images": [{"image_id": "other", "filename": "test.png"}]},
        }

        report = build_deepscores_leakage_report(split_manifests)

        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["checks"]["duplicate_image_ids"]["status"], "failed")
        self.assertEqual(report["checks"]["duplicate_image_ids"]["count"], 1)

    def test_muscima_splits_have_no_duplicate_page_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            annotations = Path(tmp) / "annotations"
            annotations.mkdir()
            for index in range(10):
                writer = index % 3 + 1
                (annotations / f"CVC-MUSCIMA_W-{writer:02d}_N-{index:02d}_D-ideal.xml").write_text(
                    """<?xml version="1.0" encoding="utf-8"?>
<Nodes>
  <Node><Id>0</Id><ClassName>noteheadFull</ClassName></Node>
</Nodes>
""",
                    encoding="utf-8",
                )

            manifest = build_muscima_manifest_run(
                annotations_dir=annotations,
                output_dir=Path(tmp) / "runs" / "muscima",
                generated_at="2026-05-12T00:00:00Z",
            )

            split_page_ids = {}
            for split_name in ("train", "val", "holdout"):
                split_payload = json.loads(Path(manifest["outputs"][f"{split_name}_manifest"]).read_text())
                split_page_ids[split_name] = {page["page_id"] for page in split_payload["pages"]}

            self.assertFalse(split_page_ids["train"] & split_page_ids["val"])
            self.assertFalse(split_page_ids["train"] & split_page_ids["holdout"])
            self.assertFalse(split_page_ids["val"] & split_page_ids["holdout"])
            self.assertEqual(manifest["leakage_status"], "passed")


if __name__ == "__main__":
    unittest.main()
