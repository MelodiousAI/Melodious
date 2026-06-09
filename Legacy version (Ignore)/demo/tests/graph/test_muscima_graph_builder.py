import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.graph.muscima_graph_builder import (
    build_graph_for_document,
    build_summary_row,
    compute_graph_statistics,
    count_unassigned_nodes,
    get_graph_output_path,
    load_muscima_data,
)


class TestMuscimaGraphBuilder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_nodes, cls.all_edges = load_muscima_data()
        cls.document_name = "CVC-MUSCIMA_W-01_N-10_D-ideal"
        cls.graph_data = build_graph_for_document(
            cls.document_name,
            cls.all_nodes,
            cls.all_edges,
        )

    def test_build_graph_for_known_document_returns_basic_structure(self):
        graph_data = self.graph_data

        self.assertEqual(graph_data["document"], self.document_name)
        self.assertTrue(Path(graph_data["image_path"]).exists())
        self.assertGreater(len(graph_data["staff_regions"]), 0)
        self.assertGreater(len(graph_data["nodes"]), 0)
        self.assertGreater(len(graph_data["edges"]), 0)

    def test_known_document_has_no_unassigned_nodes(self):
        self.assertEqual(count_unassigned_nodes(self.graph_data), 0)

    def test_graph_statistics_are_consistent_with_graph_data(self):
        statistics = compute_graph_statistics(self.graph_data)

        self.assertEqual(statistics["document"], self.document_name)
        self.assertEqual(statistics["node_count"], len(self.graph_data["nodes"]))
        self.assertEqual(statistics["edge_count"], len(self.graph_data["edges"]))
        self.assertEqual(statistics["staff_region_count"], len(self.graph_data["staff_regions"]))
        self.assertEqual(statistics["unassigned_node_count"], 0)
        self.assertGreater(statistics["unique_node_class_count"], 0)
        self.assertGreaterEqual(statistics["assigned_node_ratio"], 0.0)
        self.assertLessEqual(statistics["assigned_node_ratio"], 1.0)

    def test_summary_row_includes_expected_output_fields(self):
        summary_row = build_summary_row(self.graph_data)
        output_path = get_graph_output_path(self.document_name)

        self.assertEqual(summary_row["document"], self.document_name)
        self.assertEqual(summary_row["graph_json_path"], str(output_path))
        self.assertIn("average_nodes_per_staff", summary_row)
        self.assertIn("edge_density", summary_row)
        self.assertEqual(summary_row["unassigned_node_count"], 0)


if __name__ == "__main__":
    unittest.main()
