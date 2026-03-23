import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from detection_alignment import align_detections_to_ground_truth, align_document_detections


class TestDetectionAlignment(unittest.TestCase):
    def build_ground_truth_nodes(self):
        return [
            {
                "document": "doc-1",
                "id": 1,
                "node_key": "doc-1::1",
                "class_name": "noteheadFull",
                "bounding_box": {"top": 100, "left": 50, "bottom": 120, "right": 70},
            },
            {
                "document": "doc-1",
                "id": 2,
                "node_key": "doc-1::2",
                "class_name": "stem",
                "bounding_box": {"top": 98, "left": 72, "bottom": 145, "right": 78},
            },
        ]

    def test_exact_overlap_match_succeeds(self):
        ground_truth_nodes = self.build_ground_truth_nodes()[:1]
        detections = [
            {
                "class_name": "noteheadFull",
                "class_id": 1,
                "bbox": [60, 110, 20, 20],
                "conf": 0.95,
            }
        ]

        result = align_detections_to_ground_truth(detections, ground_truth_nodes, iou_threshold=0.5)

        self.assertEqual(result["summary"]["match_count"], 1)
        self.assertEqual(result["summary"]["false_positive_count"], 0)
        self.assertEqual(result["summary"]["false_negative_count"], 0)
        self.assertEqual(result["summary"]["precision"], 1.0)
        self.assertEqual(result["summary"]["recall"], 1.0)

    def test_class_mismatch_blocks_match(self):
        ground_truth_nodes = self.build_ground_truth_nodes()[:1]
        detections = [
            {
                "class_name": "restWhole",
                "class_id": 9,
                "bbox": [60, 110, 20, 20],
                "conf": 0.95,
            }
        ]

        result = align_detections_to_ground_truth(detections, ground_truth_nodes, iou_threshold=0.5)

        self.assertEqual(result["summary"]["match_count"], 0)
        self.assertEqual(result["summary"]["false_positive_count"], 1)
        self.assertEqual(result["summary"]["false_negative_count"], 1)

    def test_greedy_matching_keeps_one_detection_per_ground_truth_node(self):
        ground_truth_nodes = self.build_ground_truth_nodes()[:1]
        detections = [
            {
                "class_name": "noteheadFull",
                "class_id": 1,
                "bbox": [60, 110, 20, 20],
                "conf": 0.95,
            },
            {
                "class_name": "noteheadFull",
                "class_id": 1,
                "bbox": [61, 110, 20, 20],
                "conf": 0.91,
            },
        ]

        result = align_detections_to_ground_truth(detections, ground_truth_nodes, iou_threshold=0.5)

        self.assertEqual(result["summary"]["match_count"], 1)
        self.assertEqual(result["summary"]["false_positive_count"], 1)
        self.assertEqual(result["summary"]["false_negative_count"], 0)

    def test_document_wrapper_filters_ground_truth_by_document(self):
        all_nodes = self.build_ground_truth_nodes() + [
            {
                "document": "doc-2",
                "id": 7,
                "node_key": "doc-2::7",
                "class_name": "clefG",
                "bounding_box": {"top": 30, "left": 20, "bottom": 90, "right": 45},
            }
        ]
        detections = [
            {
                "class_name": "noteheadFull",
                "class_id": 1,
                "bbox": [60, 110, 20, 20],
                "conf": 0.95,
            }
        ]

        result = align_document_detections("doc-1", detections, all_nodes, iou_threshold=0.5)

        self.assertEqual(result["document"], "doc-1")
        self.assertEqual(result["summary"]["match_count"], 1)
        self.assertEqual(result["summary"]["false_negative_count"], 1)


if __name__ == "__main__":
    unittest.main()
