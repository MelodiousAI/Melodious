import unittest

from melodious_v2.datasets.deepscores import (
    bbox_xyxy_to_yolo,
    build_manifest,
    deepscores_categories,
    labels_for_image,
)


class DeepScoresDatasetTests(unittest.TestCase):
    def tiny_coco(self):
        return {
            "categories": {
                "1": {"name": "brace", "annotation_set": "deepscores"},
                "137": {"name": "brace", "annotation_set": "muscima++"},
                "25": {"name": "noteheadBlackOnLine", "annotation_set": "deepscores"},
            },
            "images": [
                {
                    "id": 1,
                    "filename": "page.png",
                    "width": 100,
                    "height": 200,
                    "ann_ids": ["a1"],
                }
            ],
            "annotations": {
                "a1": {"a_bbox": [10, 20, 30, 60], "cat_id": ["25"]},
            },
        }

    def test_category_map_uses_deepscores_only(self):
        mapping = deepscores_categories(self.tiny_coco())
        self.assertEqual(mapping["1"], 0)
        self.assertNotIn("137", mapping)

    def test_bbox_conversion(self):
        converted = bbox_xyxy_to_yolo([10, 20, 30, 60], 100, 200)
        self.assertEqual(converted, (0.2, 0.2, 0.2, 0.2))

    def test_manifest_reports_136_classes(self):
        coco = self.tiny_coco()
        labels = labels_for_image(coco["images"][0], coco["annotations"], deepscores_categories(coco))
        self.assertEqual(len(labels), 1)
        manifest = build_manifest(coco, "unit")
        self.assertEqual(manifest["class_count"], 136)
        self.assertEqual(manifest["classes_with_support"], 1)


if __name__ == "__main__":
    unittest.main()

