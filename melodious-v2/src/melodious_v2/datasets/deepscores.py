"""DeepScores conversion helpers for full-taxonomy detector training."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from melodious_v2.taxonomies import DEEPSCORES_136_CLASS_NAMES


@dataclass(frozen=True)
class YoloLabel:
    """One YOLO label row in normalized center format."""

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


def load_coco_json(path: str | Path) -> dict[str, Any]:
    """Load a DeepScores COCO-style annotation file."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def deepscores_categories(coco: dict[str, Any]) -> dict[str, int]:
    """Return DeepScores category-name to V2 zero-based class id mapping."""
    mapping: dict[str, int] = {}
    categories = coco.get("categories", {})
    for raw_id, info in categories.items():
        if info.get("annotation_set") != "deepscores":
            continue
        name = info["name"]
        if name in DEEPSCORES_136_CLASS_NAMES:
            mapping[str(raw_id)] = DEEPSCORES_136_CLASS_NAMES.index(name)
    return mapping


def bbox_xyxy_to_yolo(
    bbox: list[float],
    image_width: float,
    image_height: float,
) -> tuple[float, float, float, float]:
    """Convert `[x1, y1, x2, y2]` to normalized YOLO center format."""
    x1, y1, x2, y2 = [float(value) for value in bbox]
    x1 = max(0.0, min(x1, image_width))
    x2 = max(0.0, min(x2, image_width))
    y1 = max(0.0, min(y1, image_height))
    y2 = max(0.0, min(y2, image_height))
    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)
    x_center = x1 + width / 2.0
    y_center = y1 + height / 2.0
    return (
        x_center / image_width,
        y_center / image_height,
        width / image_width,
        height / image_height,
    )


def labels_for_image(
    image_info: dict[str, Any],
    annotations: dict[str, Any],
    category_id_to_class_id: dict[str, int],
) -> list[YoloLabel]:
    """Build all full-taxonomy YOLO labels for one image record."""
    labels: list[YoloLabel] = []
    width = float(image_info["width"])
    height = float(image_info["height"])

    for annotation_id in image_info.get("ann_ids", []):
        annotation = annotations.get(str(annotation_id))
        if not annotation:
            continue
        bbox = annotation.get("a_bbox")
        if not bbox or len(bbox) != 4:
            continue

        class_id = None
        for raw_category_id in annotation.get("cat_id", []):
            mapped_id = category_id_to_class_id.get(str(raw_category_id))
            if mapped_id is not None:
                class_id = mapped_id
                break
        if class_id is None:
            continue

        x_center, y_center, box_width, box_height = bbox_xyxy_to_yolo(bbox, width, height)
        if box_width <= 0.0 or box_height <= 0.0:
            continue
        labels.append(
            YoloLabel(
                class_id=class_id,
                x_center=x_center,
                y_center=y_center,
                width=box_width,
                height=box_height,
            )
        )
    return labels


def build_manifest(coco: dict[str, Any], split_name: str) -> dict[str, Any]:
    """Build a deterministic manifest summary for a DeepScores split."""
    category_map = deepscores_categories(coco)
    image_count = len(coco.get("images", []))
    annotation_count = len(coco.get("annotations", {}))
    class_counts = {name: 0 for name in DEEPSCORES_136_CLASS_NAMES}

    for image_info in coco.get("images", []):
        labels = labels_for_image(image_info, coco.get("annotations", {}), category_map)
        for label in labels:
            class_counts[DEEPSCORES_136_CLASS_NAMES[label.class_id]] += 1

    return {
        "split": split_name,
        "taxonomy_id": "deepscores_136",
        "image_count": image_count,
        "annotation_count": annotation_count,
        "class_count": len(DEEPSCORES_136_CLASS_NAMES),
        "class_counts": class_counts,
        "classes_with_support": sum(1 for count in class_counts.values() if count > 0),
    }


def write_yolo_split(
    coco_json: str | Path,
    output_dir: str | Path,
    split_name: str,
) -> dict[str, Any]:
    """Write YOLO label files and a manifest for one DeepScores split.

    This function writes only labels and manifests. Image copying/symlinking is
    intentionally left to deployment scripts so raw data does not enter Git.
    """
    coco = load_coco_json(coco_json)
    category_map = deepscores_categories(coco)
    root = Path(output_dir)
    label_dir = root / "labels" / split_name
    label_dir.mkdir(parents=True, exist_ok=True)

    image_paths: list[str] = []
    for image_info in coco.get("images", []):
        labels = labels_for_image(image_info, coco.get("annotations", {}), category_map)
        label_path = label_dir / f"{Path(image_info['filename']).stem}.txt"
        label_path.write_text("\n".join(label.to_line() for label in labels), encoding="utf-8")
        image_paths.append(image_info["filename"])

    manifest = build_manifest(coco, split_name)
    manifest["image_files"] = image_paths
    manifest_path = root / "manifests" / f"{split_name}.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest

