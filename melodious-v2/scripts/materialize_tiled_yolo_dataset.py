"""Materialize a tiled YOLO dataset for tiny OMR symbols such as stems."""

from __future__ import annotations

import argparse
import json

from melodious_v2.datasets.yolo_tiling import materialize_tiled_yolo_dataset
from melodious_v2.paths import PROJECT_ROOT


DEFAULT_FOCUS_CLASSES = [
    "stem",
    "ledgerLine",
    "augmentationDot",
    "beam",
    "flag8thUp",
    "flag16thUp",
    "flag32ndUp",
    "flag64thUp",
    "flag128thUp",
    "flag8thDown",
    "flag16thDown",
    "flag32ndDown",
    "flag64thDown",
    "flag128thDown",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        default=str(PROJECT_ROOT / "runs" / "data" / "deepscores_136_yolo_materialized"),
        help="Existing materialized full-page YOLO dataset.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "runs" / "data" / "deepscores_136_yolo_tiled_stem_v1"),
        help="Ignored output directory for the tiled YOLO dataset.",
    )
    parser.add_argument("--tile-size", type=int, default=384, help="Square tile size in source pixels.")
    parser.add_argument("--stride", type=int, default=256, help="Tile stride in source pixels.")
    parser.add_argument(
        "--min-visibility",
        type=float,
        default=0.5,
        help="Minimum original box area fraction visible inside a tile before keeping the label.",
    )
    parser.add_argument(
        "--focus-classes",
        nargs="+",
        default=DEFAULT_FOCUS_CLASSES,
        help="Tiles are kept only when at least one of these classes is visible.",
    )
    parser.add_argument(
        "--focus-only-labels",
        action="store_true",
        help="Write only focus-class labels instead of all visible labels in focused tiles.",
    )
    parser.add_argument(
        "--target-imgsz",
        type=int,
        default=1024,
        help="Expected YOLO training image size used for projected tiny-symbol pixel-width audit.",
    )
    parser.add_argument(
        "--max-images-per-split",
        type=int,
        default=None,
        help="Optional smoke limit per split. Omit for full materialization.",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["train", "val", "test"],
        choices=["train", "val", "test"],
        help="Dataset splits to tile.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = materialize_tiled_yolo_dataset(
        source_dir=args.source_dir,
        output_dir=args.output_dir,
        tile_size=args.tile_size,
        stride=args.stride,
        min_visibility=args.min_visibility,
        focus_class_names=args.focus_classes,
        include_all_labels_in_focused_tiles=not args.focus_only_labels,
        target_imgsz=args.target_imgsz,
        max_images_per_split=args.max_images_per_split,
        splits=args.splits,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
