import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pyg_graph_builder import (
    EDGE_FEATURE_NAMES,
    NODE_FEATURE_NAMES,
    adapt_detections,
    build_fake_test_detections,
    build_graph,
    build_graph_from_image_and_detections,
)


class TestPyGGraphBuilder(unittest.TestCase):
    def test_fake_graph_has_expected_shapes(self):
        image_shape = (400, 300)
        staff_regions = [(90, 160), (220, 290)]
        detections = build_fake_test_detections()

        graph_data = build_graph(
            detections,
            image_shape,
            staff_regions=staff_regions,
        )

        self.assertEqual(graph_data.num_nodes, 3)
        self.assertEqual(list(graph_data.x.shape), [3, len(NODE_FEATURE_NAMES)])
        self.assertGreater(graph_data.edge_index.numel(), 0)

    def test_fake_graph_without_staff_regions_uses_minus_one(self):
        image_shape = (400, 300)
        detections = build_fake_test_detections()

        graph_data = build_graph(
            detections,
            image_shape,
            staff_regions=None,
        )

        staff_index_column = graph_data.x[:, 6].tolist()

        self.assertEqual(graph_data.num_nodes, 3)
        self.assertEqual(staff_index_column, [-1.0, -1.0, -1.0])

    def test_edge_attributes_have_expected_width_and_signal(self):
        image_shape = (400, 300)
        staff_regions = [(90, 160), (220, 290)]
        detections = build_fake_test_detections()

        graph_data = build_graph(
            detections,
            image_shape,
            staff_regions=staff_regions,
        )

        self.assertEqual(graph_data.edge_attr.shape[1], len(EDGE_FEATURE_NAMES))
        self.assertGreater(float(graph_data.edge_attr.sum().item()), 0.0)

    def test_empty_detections_returns_valid_empty_graph(self):
        graph_data = build_graph([], (400, 300), staff_regions=None)

        self.assertEqual(graph_data.num_nodes, 0)
        self.assertEqual(list(graph_data.x.shape), [0, len(NODE_FEATURE_NAMES)])
        self.assertEqual(list(graph_data.edge_index.shape), [2, 0])
        self.assertEqual(list(graph_data.edge_attr.shape), [0, len(EDGE_FEATURE_NAMES)])

    def test_invalid_detection_raises_error(self):
        bad_detections = [{"class_id": 1, "bbox": [100, 120, 30, 24]}]

        with self.assertRaises(KeyError):
            build_graph(bad_detections, (400, 300), staff_regions=None)

    def test_alias_based_detection_adapter_normalizes_common_keys(self):
        raw_detections = {
            "detections": [
                {
                    "class": 4,
                    "xywh": [120, 140, 24, 18],
                    "score": 0.87,
                },
                {
                    "label_id": 2,
                    "x_center": 80,
                    "y_center": 200,
                    "width": 30,
                    "height": 26,
                    "confidence": 0.93,
                },
            ]
        }

        adapted = adapt_detections(raw_detections)

        self.assertEqual(
            adapted,
            [
                {"class_id": 4, "bbox": [120.0, 140.0, 24.0, 18.0], "conf": 0.87},
                {"class_id": 2, "bbox": [80.0, 200.0, 30.0, 26.0], "conf": 0.93},
            ],
        )

    def test_build_graph_from_image_and_detections_uses_image_and_staff_wrapper(self):
        detections = [
            {"class": 1, "x_center": 50, "y_center": 60, "width": 20, "height": 16, "score": 0.95},
            {"class": 2, "x_center": 95, "y_center": 68, "width": 18, "height": 14, "score": 0.91},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "page.png"
            image = np.full((240, 180), 255, dtype=np.uint8)
            cv2.imwrite(str(image_path), image)

            with patch("pyg_graph_builder.detect_staff_lines", return_value=[(40, 90)]):
                graph_data = build_graph_from_image_and_detections(image_path, detections)

        self.assertEqual(graph_data.num_nodes, 2)
        self.assertEqual(list(graph_data.x.shape), [2, len(NODE_FEATURE_NAMES)])
        self.assertGreater(graph_data.edge_index.numel(), 0)
        self.assertEqual(graph_data.x[:, 6].tolist(), [0.0, 0.0])


if __name__ == "__main__":
    unittest.main()
