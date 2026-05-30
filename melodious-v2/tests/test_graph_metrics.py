import unittest

from melodious_v2.metrics.classification import classification_report


class GraphMetricTests(unittest.TestCase):
    def test_positive_macro_f1_excludes_no_relation(self):
        labels = ["no_relation", "stem_notehead", "beam_notegroup"]
        report = classification_report(
            y_true=[0, 0, 0, 1, 1, 2],
            y_pred=[0, 0, 0, 1, 0, 0],
            label_names=labels,
        )
        self.assertIn("no_relation", report)
        self.assertEqual(report["primary_metric"], "positive_macro_f1")
        self.assertLess(report["positive_macro_f1"], report["accuracy"])
        self.assertEqual(report["no_relation"]["support"], 3)


if __name__ == "__main__":
    unittest.main()

