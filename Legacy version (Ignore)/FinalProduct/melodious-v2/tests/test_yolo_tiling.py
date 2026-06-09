from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml
from PIL import Image

from melodious_v2.datasets.yolo_tiling import (
    PixelBox,
    TileWindow,
    clip_box_to_tile,
    generate_tile_windows,
    materialize_tiled_yolo_dataset,
    parse_yolo_labels,
)
from melodious_v2.taxonomies import DEEPSCORES_136_CLASS_NAMES


class YoloTilingTest(unittest.TestCase):
    def test_generate_tile_windows_covers_edges(self) -> None:
        windows = generate_tile_windows(
            100,
            70,
            tile_width=32,
            tile_height=32,
            stride_x=24,
            stride_y=24,
        )

        self.assertEqual(windows[0], TileWindow(0, 0, 32, 32))
        self.assertEqual(windows[-1], TileWindow(68, 38, 100, 70))
        self.assertTrue(any(window.x2 == 100 for window in windows))
        self.assertTrue(any(window.y2 == 70 for window in windows))

    def test_clip_box_to_tile_keeps_visible_fraction(self) -> None:
        box = PixelBox(class_id=41, x1=20.0, y1=10.0, x2=30.0, y2=60.0)
        tile = TileWindow(0, 0, 25, 50)

        clipped = clip_box_to_tile(box, tile, min_visibility=0.35)
        self.assertIsNotNone(clipped)
        assert clipped is not None
        self.assertEqual(clipped.class_id, 41)
        self.assertAlmostEqual(clipped.x_center, 0.9)
        self.assertAlmostEqual(clipped.width, 0.2)
        self.assertAlmostEqual(clipped.height, 0.8)

        self.assertIsNone(clip_box_to_tile(box, tile, min_visibility=0.5))

    def test_materialize_tiled_dataset_keeps_focus_tiles_and_context(self) -> None:
        stem_id = DEEPSCORES_136_CLASS_NAMES.index("stem")
        notehead_id = DEEPSCORES_136_CLASS_NAMES.index("noteheadBlackOnLine")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            for split in ("train", "val", "test"):
                (source / "images" / split).mkdir(parents=True)
                (source / "labels" / split).mkdir(parents=True)
                Image.new("RGB", (100, 100), color="white").save(source / "images" / split / "page.png")
                (source / "labels" / split / "page.txt").write_text(
                    "\n".join(
                        [
                            f"{stem_id} 0.25000000 0.50000000 0.02000000 0.60000000",
                            f"{notehead_id} 0.28000000 0.50000000 0.10000000 0.10000000",
                        ]
                    ),
                    encoding="utf-8",
                )
            names = {index: name for index, name in enumerate(DEEPSCORES_136_CLASS_NAMES)}
            (source / "dataset.yaml").write_text(
                yaml.safe_dump(
                    {
                        "path": source.as_posix(),
                        "train": "images/train",
                        "val": "images/val",
                        "test": "images/test",
                        "nc": 136,
                        "names": names,
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            output = root / "tiled"
            manifest = materialize_tiled_yolo_dataset(
                source_dir=source,
                output_dir=output,
                tile_size=50,
                stride=50,
                min_visibility=0.5,
                focus_class_names=["stem"],
                target_imgsz=100,
            )

            self.assertEqual(manifest["splits"]["train"]["tile_count"], 2)
            self.assertEqual(manifest["splits"]["train"]["focus_class_counts"]["stem"], 2)
            self.assertTrue((output / "dataset.yaml").exists())
            labels = parse_yolo_labels(next((output / "labels" / "train").glob("*.txt")))
            self.assertEqual([label.class_id for label in labels], [stem_id, notehead_id])
            projected = manifest["projected_focus_widths"]["stem"]
            self.assertGreater(projected["median_projected_width_px_at_target_imgsz"], 3.0)


if __name__ == "__main__":
    unittest.main()
