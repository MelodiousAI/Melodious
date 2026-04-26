import unittest

from src.export.heuristic_assembler import assemble_detections, summarize_assembled_output


class TestHeuristicAssembler(unittest.TestCase):
    def test_assemble_detections_groups_related_symbols(self):
        detections = [
            {
                "class_id": 1,
                "class_name": "clefG",
                "confidence": 0.99,
                "bbox": {"x_center": 0.10, "y_center": 0.30, "width": 0.04, "height": 0.18},
            },
            {
                "class_id": 2,
                "class_name": "notehead-full",
                "confidence": 0.95,
                "bbox": {"x_center": 0.25, "y_center": 0.35, "width": 0.03, "height": 0.03},
            },
            {
                "class_id": 3,
                "class_name": "stem",
                "confidence": 0.94,
                "bbox": {"x_center": 0.28, "y_center": 0.33, "width": 0.01, "height": 0.10},
            },
            {
                "class_id": 4,
                "class_name": "beam",
                "confidence": 0.91,
                "bbox": {"x_center": 0.29, "y_center": 0.31, "width": 0.05, "height": 0.02},
            },
            {
                "class_id": 5,
                "class_name": "rest-quarter",
                "confidence": 0.88,
                "bbox": {"x_center": 0.55, "y_center": 0.38, "width": 0.03, "height": 0.05},
            },
            {
                "class_id": 6,
                "class_name": "accidentalSharp",
                "confidence": 0.87,
                "bbox": {"x_center": 0.22, "y_center": 0.35, "width": 0.02, "height": 0.05},
            },
        ]

        assembled_output = assemble_detections(detections)

        self.assertEqual(len(assembled_output.notes), 1)
        self.assertEqual(len(assembled_output.clefs), 1)
        self.assertEqual(len(assembled_output.rests), 1)
        self.assertEqual(len(assembled_output.unmatched), 0)
        self.assertIsNotNone(assembled_output.notes[0].stem)
        self.assertIsNotNone(assembled_output.notes[0].beam)
        self.assertIsNotNone(assembled_output.notes[0].accidental)

    def test_summarize_assembled_output_returns_count_fields(self):
        detections = [
            {
                "class_id": 1,
                "class_name": "notehead-half",
                "confidence": 0.95,
                "bbox": {"x_center": 0.25, "y_center": 0.35, "width": 0.03, "height": 0.03},
            },
            {
                "class_id": 2,
                "class_name": "stem",
                "confidence": 0.94,
                "bbox": {"x_center": 0.28, "y_center": 0.33, "width": 0.01, "height": 0.10},
            },
            {
                "class_id": 3,
                "class_name": "beam",
                "confidence": 0.91,
                "bbox": {"x_center": 0.70, "y_center": 0.60, "width": 0.05, "height": 0.02},
            },
        ]

        summary = summarize_assembled_output(assemble_detections(detections))

        self.assertEqual(summary["note_count"], 1)
        self.assertEqual(summary["clef_count"], 0)
        self.assertEqual(summary["rest_count"], 0)
        self.assertEqual(summary["unmatched_count"], 1)


if __name__ == "__main__":
    unittest.main()
