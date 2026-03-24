"""OpenCV template-matching baseline for music symbol detection.

Uses normalised cross-correlation against a small library of template
crops extracted from the training set.  This is intentionally simple
so it serves as a credible lower-bound comparison.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import cv2
import numpy as np


def extract_templates(
    dataset_root: Path,
    split_json: str = "deepscores_train.json",
    target_classes: Optional[Dict[str, int]] = None,
    max_per_class: int = 20,
    pad: int = 4,
) -> Dict[int, List[np.ndarray]]:
    """Crop small template patches from annotated bounding boxes.

    Returns a dict mapping class_id -> list of grayscale template images.
    """
    if target_classes is None:
        from melodious.dataset import TARGET_CLASSES
        target_classes = TARGET_CLASSES

    coco_path = dataset_root / split_json
    with coco_path.open("r", encoding="utf-8") as fh:
        coco = json.load(fh)

    cat_lookup = {cid: info["name"] for cid, info in coco["categories"].items()}
    templates: Dict[int, List[np.ndarray]] = {v: [] for v in target_classes.values()}

    for img_info in coco["images"]:
        img_path = dataset_root / "images" / img_info["filename"]
        if not img_path.exists():
            continue

        gray = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            continue

        h, w = gray.shape[:2]

        for ann_id in img_info.get("ann_ids", []):
            ann = coco["annotations"].get(str(ann_id))
            if ann is None:
                continue

            for cid in ann.get("cat_id", []):
                cname = cat_lookup.get(str(cid))
                if cname not in target_classes:
                    continue

                cls_id = target_classes[cname]
                if len(templates[cls_id]) >= max_per_class:
                    continue

                x1, y1, x2, y2 = [int(round(v)) for v in ann["a_bbox"]]
                x1 = max(0, x1 - pad)
                y1 = max(0, y1 - pad)
                x2 = min(w, x2 + pad)
                y2 = min(h, y2 + pad)

                crop = gray[y1:y2, x1:x2]
                if crop.size > 0:
                    templates[cls_id].append(crop)
                break

        if all(len(v) >= max_per_class for v in templates.values()):
            break

    return templates


def detect_with_templates(
    image: np.ndarray,
    templates: Dict[int, List[np.ndarray]],
    threshold: float = 0.75,
    nms_iou: float = 0.3,
) -> List[Dict]:
    """Run template matching on a single grayscale image.

    Returns a list of detection dicts with keys:
        class_id, confidence, bbox_pixels (x1, y1, x2, y2)
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    all_detections: List[Dict] = []

    for cls_id, tmpl_list in templates.items():
        for tmpl in tmpl_list:
            th, tw = tmpl.shape[:2]
            if th > gray.shape[0] or tw > gray.shape[1]:
                continue

            result = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
            locs = np.where(result >= threshold)

            for pt_y, pt_x in zip(*locs):
                all_detections.append({
                    "class_id": cls_id,
                    "confidence": float(result[pt_y, pt_x]),
                    "bbox_pixels": {
                        "x1": int(pt_x),
                        "y1": int(pt_y),
                        "x2": int(pt_x + tw),
                        "y2": int(pt_y + th),
                    },
                })

    # Simple greedy NMS
    all_detections.sort(key=lambda d: d["confidence"], reverse=True)
    keep: List[Dict] = []
    for det in all_detections:
        b = det["bbox_pixels"]
        overlaps = False
        for kept in keep:
            kb = kept["bbox_pixels"]
            ix1 = max(b["x1"], kb["x1"])
            iy1 = max(b["y1"], kb["y1"])
            ix2 = min(b["x2"], kb["x2"])
            iy2 = min(b["y2"], kb["y2"])
            inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
            area_a = (b["x2"] - b["x1"]) * (b["y2"] - b["y1"])
            area_b = (kb["x2"] - kb["x1"]) * (kb["y2"] - kb["y1"])
            union = area_a + area_b - inter
            if union > 0 and inter / union > nms_iou:
                overlaps = True
                break
        if not overlaps:
            keep.append(det)

    return keep
