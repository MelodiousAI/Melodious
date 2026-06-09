import unittest

from melodious_v2.metrics.detection import (
    DetectionPrediction,
    DetectionTarget,
    compute_iou,
    evaluate_detection_dataset,
)


class DetectionMetricTests(unittest.TestCase):
    def test_iou_exact_overlap(self):
        self.assertEqual(compute_iou((0, 0, 10, 10), (0, 0, 10, 10)), 1.0)

    def test_golden_tp_fp_fn_and_f1(self):
        predictions = [
            DetectionPrediction("img1", (0, 0, 10, 10), 0, 0.99),
            DetectionPrediction("img1", (50, 50, 60, 60), 0, 0.50),
        ]
        targets = [
            DetectionTarget("img1", (0, 0, 10, 10), 0),
            DetectionTarget("img1", (20, 20, 30, 30), 0),
        ]
        result = evaluate_detection_dataset(
            predictions,
            targets,
            class_names=["note"],
            iou_thresholds=[0.5],
        )
        self.assertEqual(result["tp@0.5"], 1)
        self.assertEqual(result["fp@0.5"], 1)
        self.assertEqual(result["fn@0.5"], 1)
        self.assertAlmostEqual(result["precision@0.5"], 0.5)
        self.assertAlmostEqual(result["recall@0.5"], 0.5)
        self.assertAlmostEqual(result["F1@0.5"], 0.5)
        self.assertAlmostEqual(result["mAP@0.5"], 0.5)


if __name__ == "__main__":
    unittest.main()
