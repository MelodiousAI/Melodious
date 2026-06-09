"""Tile a materialized YOLO dataset for tiny OMR symbol training."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Iterable

import yaml
from PIL import Image


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
SPLITS = ("train", "val", "test")


@dataclass(frozen=True)
class YoloBox:
    """One normalized YOLO box."""

    class_id: int
    x_center: float
    y_center: float
    width: float
    height: float

    def to_line(self) -> str:
        return (
            f"{self.class_id} {self.x_center:.8f} {self.y_center:.8f} "
            f"{self.width:.8f} {self.height:.8f}"
        )


@dataclass(frozen=True)
class PixelBox:
    """One pixel-space box in xyxy format."""

    class_id: int
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def area(self) -> float:
        return max(0.0, self.x2 - self.x1) * max(0.0, self.y2 - self.y1)


@dataclass(frozen=True)
class TileWindow:
    """Pixel-space crop window."""

    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_yolo_labels(path: str | Path) -> list[YoloBox]:
    """Read normalized YOLO labels from disk."""
    label_path = Path(path)
    if not label_path.exists():
        return []
    labels: list[YoloBox] = []
    for line_number, line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 5:
            raise ValueError(f"Invalid YOLO label at {label_path}:{line_number}")
        labels.append(
            YoloBox(
                class_id=int(float(parts[0])),
                x_center=float(parts[1]),
                y_center=float(parts[2]),
                width=float(parts[3]),
                height=float(parts[4]),
            )
        )
    return labels


def yolo_to_pixel(label: YoloBox, image_width: int, image_height: int) -> PixelBox:
    """Convert a normalized YOLO box to clipped pixel xyxy coordinates."""
    width = label.width * image_width
    height = label.height * image_height
    x_center = label.x_center * image_width
    y_center = label.y_center * image_height
    x1 = max(0.0, min(float(image_width), x_center - width / 2.0))
    y1 = max(0.0, min(float(image_height), y_center - height / 2.0))
    x2 = max(0.0, min(float(image_width), x_center + width / 2.0))
    y2 = max(0.0, min(float(image_height), y_center + height / 2.0))
    return PixelBox(label.class_id, x1, y1, x2, y2)


def pixel_to_yolo(box: PixelBox, tile: TileWindow) -> YoloBox | None:
    """Convert a clipped pixel-space box inside a tile to normalized YOLO format."""
    width = max(0.0, box.x2 - box.x1)
    height = max(0.0, box.y2 - box.y1)
    if width <= 0.0 or height <= 0.0 or tile.width <= 0 or tile.height <= 0:
        return None
    return YoloBox(
        class_id=box.class_id,
        x_center=((box.x1 + box.x2) / 2.0 - tile.x1) / tile.width,
        y_center=((box.y1 + box.y2) / 2.0 - tile.y1) / tile.height,
        width=width / tile.width,
        height=height / tile.height,
    )


def _axis_starts(length: int, tile_length: int, stride: int) -> list[int]:
    if length <= 0:
        raise ValueError("Image dimensions must be positive.")
    if tile_length <= 0 or stride <= 0:
        raise ValueError("Tile size and stride must be positive.")
    if length <= tile_length:
        return [0]
    starts = list(range(0, max(1, length - tile_length + 1), stride))
    final_start = length - tile_length
    if starts[-1] != final_start:
        starts.append(final_start)
    return sorted(set(starts))


def generate_tile_windows(
    image_width: int,
    image_height: int,
    *,
    tile_width: int,
    tile_height: int,
    stride_x: int,
    stride_y: int,
) -> list[TileWindow]:
    """Generate tile windows that cover the full image, including right/bottom edges."""
    windows: list[TileWindow] = []
    for y in _axis_starts(image_height, tile_height, stride_y):
        for x in _axis_starts(image_width, tile_width, stride_x):
            windows.append(
                TileWindow(
                    x1=x,
                    y1=y,
                    x2=min(image_width, x + tile_width),
                    y2=min(image_height, y + tile_height),
                )
            )
    return windows


def clip_box_to_tile(
    box: PixelBox,
    tile: TileWindow,
    *,
    min_visibility: float,
) -> YoloBox | None:
    """Clip one pixel-space box into one tile and return a normalized tile label."""
    clipped = PixelBox(
        class_id=box.class_id,
        x1=max(box.x1, tile.x1),
        y1=max(box.y1, tile.y1),
        x2=min(box.x2, tile.x2),
        y2=min(box.y2, tile.y2),
    )
    if clipped.area <= 0.0 or box.area <= 0.0:
        return None
    if clipped.area / box.area < min_visibility:
        return None
    return pixel_to_yolo(clipped, tile)


def _load_dataset_yaml(source_dir: Path) -> dict[str, Any]:
    payload = yaml.safe_load((source_dir / "dataset.yaml").read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected dataset.yaml mapping under {source_dir}")
    names = payload.get("names")
    if not isinstance(names, dict):
        raise ValueError("Expected YOLO dataset names mapping.")
    return payload


def _class_ids_for_names(names: dict[Any, Any], class_names: Iterable[str]) -> set[int]:
    by_name = {str(value): int(key) for key, value in names.items()}
    missing = [name for name in class_names if name not in by_name]
    if missing:
        raise ValueError(f"Unknown focus classes: {', '.join(missing)}")
    return {by_name[name] for name in class_names}


def _image_paths(split_image_dir: Path, limit: int | None) -> list[Path]:
    paths = sorted(path for path in split_image_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
    return paths[:limit] if limit is not None else paths


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")


def materialize_tiled_yolo_dataset(
    *,
    source_dir: str | Path,
    output_dir: str | Path,
    tile_size: int = 384,
    stride: int = 256,
    min_visibility: float = 0.5,
    focus_class_names: Iterable[str] = ("stem", "ledgerLine", "augmentationDot", "beam"),
    include_all_labels_in_focused_tiles: bool = True,
    target_imgsz: int = 1024,
    max_images_per_split: int | None = None,
    splits: Iterable[str] = SPLITS,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Materialize a tiled YOLO dataset focused on tiny notation symbols.

    The output keeps only tiles that contain at least one visible focus-class
    label. All labels inside those focused tiles are retained by default so the
    detector still sees noteheads, beams, accidentals, rests, and context.
    """
    if not (0.0 < min_visibility <= 1.0):
        raise ValueError("min_visibility must be in (0, 1].")
    source_root = Path(source_dir).resolve()
    target_root = Path(output_dir).resolve()
    dataset_yaml = _load_dataset_yaml(source_root)
    names = dataset_yaml["names"]
    focus_class_ids = _class_ids_for_names(names, focus_class_names)
    generated_at = generated_at or utc_timestamp()

    split_summaries: dict[str, Any] = {}
    overall_class_counts: Counter[int] = Counter()
    overall_focus_counts: Counter[int] = Counter()
    focus_projected_widths: dict[int, list[float]] = {class_id: [] for class_id in focus_class_ids}

    for split in splits:
        if split not in SPLITS:
            raise ValueError(f"Unsupported split: {split}")
        image_dir = source_root / "images" / split
        label_dir = source_root / "labels" / split
        output_image_dir = target_root / "images" / split
        output_label_dir = target_root / "labels" / split
        output_image_dir.mkdir(parents=True, exist_ok=True)
        output_label_dir.mkdir(parents=True, exist_ok=True)

        source_images = _image_paths(image_dir, max_images_per_split)
        split_class_counts: Counter[int] = Counter()
        split_focus_counts: Counter[int] = Counter()
        tile_count = 0
        skipped_tile_count = 0
        source_label_count = 0
        clipped_label_count = 0
        focus_tile_count = 0

        for image_path in source_images:
            labels = parse_yolo_labels(label_dir / f"{image_path.stem}.txt")
            if not labels:
                continue
            with Image.open(image_path) as image:
                width, height = image.size
                pixel_boxes = [yolo_to_pixel(label, width, height) for label in labels]
                source_label_count += len(pixel_boxes)
                windows = generate_tile_windows(
                    width,
                    height,
                    tile_width=tile_size,
                    tile_height=tile_size,
                    stride_x=stride,
                    stride_y=stride,
                )
                for tile_index, tile in enumerate(windows):
                    tile_labels: list[YoloBox] = []
                    focus_visible = False
                    for pixel_box in pixel_boxes:
                        clipped_label = clip_box_to_tile(
                            pixel_box,
                            tile,
                            min_visibility=min_visibility,
                        )
                        if clipped_label is None:
                            continue
                        if pixel_box.class_id in focus_class_ids:
                            focus_visible = True
                        if include_all_labels_in_focused_tiles or pixel_box.class_id in focus_class_ids:
                            tile_labels.append(clipped_label)
                    if not focus_visible or not tile_labels:
                        skipped_tile_count += 1
                        continue

                    tile_name = f"{image_path.stem}_tile_{tile_index:04d}_x{tile.x1}_y{tile.y1}{image_path.suffix}"
                    label_name = f"{Path(tile_name).stem}.txt"
                    image.crop((tile.x1, tile.y1, tile.x2, tile.y2)).save(output_image_dir / tile_name)
                    (output_label_dir / label_name).write_text(
                        "\n".join(label.to_line() for label in tile_labels),
                        encoding="utf-8",
                    )
                    tile_count += 1
                    focus_tile_count += 1
                    clipped_label_count += len(tile_labels)
                    for label in tile_labels:
                        split_class_counts[label.class_id] += 1
                        overall_class_counts[label.class_id] += 1
                        if label.class_id in focus_class_ids:
                            split_focus_counts[label.class_id] += 1
                            overall_focus_counts[label.class_id] += 1
                            focus_projected_widths[label.class_id].append(label.width * target_imgsz)

        split_summaries[split] = {
            "source_image_count": len(source_images),
            "source_label_count": source_label_count,
            "tile_count": tile_count,
            "focus_tile_count": focus_tile_count,
            "skipped_tile_count": skipped_tile_count,
            "clipped_label_count": clipped_label_count,
            "class_counts": {
                str(names[class_id]): count for class_id, count in sorted(split_class_counts.items())
            },
            "focus_class_counts": {
                str(names[class_id]): count for class_id, count in sorted(split_focus_counts.items())
            },
        }

    output_yaml = {
        "path": target_root.as_posix(),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": int(dataset_yaml.get("nc", len(names))),
        "names": {int(index): name for index, name in names.items()},
    }
    (target_root / "dataset.yaml").write_text(yaml.safe_dump(output_yaml, sort_keys=False), encoding="utf-8")

    projected_focus_widths = {}
    for class_id, values in sorted(focus_projected_widths.items()):
        if not values:
            continue
        projected_focus_widths[str(names[class_id])] = {
            "count": len(values),
            "median_projected_width_px_at_target_imgsz": median(values),
            "min_projected_width_px_at_target_imgsz": min(values),
            "max_projected_width_px_at_target_imgsz": max(values),
        }

    manifest = {
        "dataset_id": "deepscores_136_yolo_tiled_tiny_symbols",
        "source_dataset_dir": source_root.as_posix(),
        "output_dir": target_root.as_posix(),
        "dataset_yaml": (target_root / "dataset.yaml").as_posix(),
        "generated_at": generated_at,
        "tile_size": tile_size,
        "stride": stride,
        "min_visibility": min_visibility,
        "target_imgsz": target_imgsz,
        "focus_class_names": list(focus_class_names),
        "focus_class_ids": sorted(focus_class_ids),
        "include_all_labels_in_focused_tiles": include_all_labels_in_focused_tiles,
        "max_images_per_split": max_images_per_split,
        "splits": split_summaries,
        "overall_class_counts": {
            str(names[class_id]): count for class_id, count in sorted(overall_class_counts.items())
        },
        "overall_focus_class_counts": {
            str(names[class_id]): count for class_id, count in sorted(overall_focus_counts.items())
        },
        "projected_focus_widths": projected_focus_widths,
    }
    _write_json(target_root / "manifest.json", manifest)
    return manifest
