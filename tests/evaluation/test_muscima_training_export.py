import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.muscima_training_export import (
    TRAINING_EDGE_LABELS,
    TRAINING_EDGE_TYPES,
    build_document_training_export,
    build_raw_relation_maps,
)


class TestMuscimaTrainingExport(unittest.TestCase):
    def test_build_document_training_export_matches_expected_schema(self):
        training_export = build_document_training_export("CVC-MUSCIMA_W-01_N-10_D-ideal")

        self.assertEqual(training_export["page_id"], "CVC-MUSCIMA_W-01_N-10_D-ideal")
        self.assertIn("image_path", training_export)
        self.assertIn("image_size", training_export)
        self.assertGreater(len(training_export["nodes"]), 0)
        self.assertGreater(len(training_export["edges"]), 0)

        node = training_export["nodes"][0]
        self.assertEqual(node["node_idx"], 0)
        self.assertEqual(node["node_id"], "CVC-MUSCIMA_W-01_N-10_D-ideal::0")
        self.assertIn("class_id", node)
        self.assertIn("class_name", node)
        self.assertIn("confidence", node)
        self.assertIn("bbox", node)
        self.assertIn("bbox_pixels", node)
        self.assertIn("staff_index", node)

        edge = training_export["edges"][0]
        self.assertIn(edge["edge_type"], TRAINING_EDGE_TYPES)
        self.assertIn(edge["edge_label"], TRAINING_EDGE_LABELS)
        self.assertGreaterEqual(edge["source_idx"], 0)
        self.assertGreaterEqual(edge["target_idx"], 0)
        self.assertLess(edge["source_idx"], len(training_export["nodes"]))
        self.assertLess(edge["target_idx"], len(training_export["nodes"]))

    def test_build_document_training_export_contains_positive_relation_labels(self):
        training_export = build_document_training_export("CVC-MUSCIMA_W-01_N-10_D-ideal")
        edge_labels = {edge["edge_label"] for edge in training_export["edges"]}

        self.assertIn("stem_notehead", edge_labels)
        self.assertIn("beam_notegroup", edge_labels)
        self.assertIn("slur_phrase", edge_labels)
        self.assertIn("no_relation", edge_labels)

    def test_build_raw_relation_maps_derives_tie_and_slur_notehead_pairs(self):
        document_graph = {
            "nodes": [
                {"id": 10, "class_name": "noteheadFull", "outlinks": [30, 40]},
                {"id": 11, "class_name": "noteheadHalf", "outlinks": [30]},
                {"id": 12, "class_name": "noteheadWhole", "outlinks": [40]},
                {"id": 13, "class_name": "stem", "outlinks": []},
                {"id": 14, "class_name": "beam", "outlinks": []},
                {"id": 30, "class_name": "slur", "outlinks": []},
                {"id": 40, "class_name": "tie", "outlinks": []},
            ]
        }

        relation_pairs = build_raw_relation_maps(
            document_graph,
            kept_raw_node_ids={10, 11, 12, 13, 14},
        )

        self.assertIn(frozenset({10, 11}), relation_pairs["slur_phrase"])
        self.assertIn(frozenset({10, 12}), relation_pairs["tie_sustained"])


if __name__ == "__main__":
    unittest.main()
