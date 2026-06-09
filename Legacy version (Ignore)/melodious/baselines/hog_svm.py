"""HOG + SVM baseline detector for music symbol classification.

Extracts HOG features from candidate regions and trains a linear SVM
per class.  Candidate regions come from a simple contour-based proposal
generator rather than an exhaustive sliding window.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

# HOG descriptor settings
HOG_WIN_SIZE = (64, 64)
HOG_BLOCK_SIZE = (16, 16)
HOG_BLOCK_STRIDE = (8, 8)
HOG_CELL_SIZE = (8, 8)
HOG_NBINS = 9


def _create_hog() -> cv2.HOGDescriptor:
    return cv2.HOGDescriptor(
        HOG_WIN_SIZE, HOG_BLOCK_SIZE, HOG_BLOCK_STRIDE, HOG_CELL_SIZE, HOG_NBINS
    )


def _resize_patch(patch: np.ndarray) -> np.ndarray:
    """Resize a grayscale patch to the fixed HOG window size."""
    return cv2.resize(patch, HOG_WIN_SIZE, interpolation=cv2.INTER_AREA)


def extract_hog_features(image: np.ndarray) -> np.ndarray:
    """Compute HOG descriptor for a fixed-size grayscale patch."""
    hog = _create_hog()
    resized = _resize_patch(image)
    descriptor = hog.compute(resized)
    if descriptor is None:
        return np.zeros((1, ), dtype=np.float32)
    return descriptor.flatten()


def collect_training_data(
    dataset_root: Path,
    split_json: str = "deepscores_train.json",
    target_classes: Optional[Dict[str, int]] = None,
    max_per_class: int = 200,
    negative_ratio: float = 1.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Build feature matrix X and label vector y from annotated crops.

    Positive samples are cropped from annotated boxes.
    Negative samples are randomly cropped from regions that do not overlap
    with any annotation.
    """
    if target_classes is None:
        from melodious.dataset import TARGET_CLASSES
        target_classes = TARGET_CLASSES

    coco_path = dataset_root / split_json
    with coco_path.open("r", encoding="utf-8") as fh:
        coco = json.load(fh)

    cat_lookup = {cid: info["name"] for cid, info in coco["categories"].items()}
    features: List[np.ndarray] = []
    labels: List[int] = []
    counts: Dict[int, int] = {v: 0 for v in target_classes.values()}
    neg_count = 0
    max_neg = int(max_per_class * negative_ratio * len(target_classes))

    rng = np.random.RandomState(42)

    for img_info in coco["images"]:
        img_path = dataset_root / "images" / img_info["filename"]
        if not img_path.exists():
            continue
        gray = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            continue
        ih, iw = gray.shape[:2]

        boxes_in_image: List[Tuple[int, int, int, int]] = []

        for ann_id in img_info.get("ann_ids", []):
            ann = coco["annotations"].get(str(ann_id))
            if ann is None:
                continue
            for cid in ann.get("cat_id", []):
                cname = cat_lookup.get(str(cid))
                if cname not in target_classes:
                    continue
                cls_id = target_classes[cname]
                if counts[cls_id] >= max_per_class:
                    continue

                x1, y1, x2, y2 = [int(round(v)) for v in ann["a_bbox"]]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(iw, x2), min(ih, y2)
                crop = gray[y1:y2, x1:x2]
                if crop.size == 0:
                    continue

                feat = extract_hog_features(crop)
                features.append(feat)
                labels.append(cls_id)
                counts[cls_id] += 1
                boxes_in_image.append((x1, y1, x2, y2))
                break

        # Random negative crops
        for _ in range(min(5, max_neg - neg_count)):
            rw = rng.randint(20, min(100, iw))
            rh = rng.randint(20, min(100, ih))
            rx = rng.randint(0, iw - rw)
            ry = rng.randint(0, ih - rh)
            overlap = any(
                rx < bx2 and rx + rw > bx1 and ry < by2 and ry + rh > by1
                for bx1, by1, bx2, by2 in boxes_in_image
            )
            if overlap:
                continue
            crop = gray[ry : ry + rh, rx : rx + rw]
            feat = extract_hog_features(crop)
            features.append(feat)
            labels.append(-1)  # background class
            neg_count += 1

        if all(c >= max_per_class for c in counts.values()) and neg_count >= max_neg:
            break

    X = np.stack(features, axis=0).astype(np.float32)
    y = np.array(labels, dtype=np.int32)
    return X, y


def train_svm(X: np.ndarray, y: np.ndarray) -> cv2.ml.SVM:
    """Train a multi-class linear SVM on HOG features."""
    svm = cv2.ml.SVM_create()
    svm.setType(cv2.ml.SVM_C_SVC)
    svm.setKernel(cv2.ml.SVM_LINEAR)
    svm.setTermCriteria((cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 1000, 1e-6))
    svm.train(X, cv2.ml.ROW_SAMPLE, y)
    return svm


def propose_regions(
    image: np.ndarray,
    min_area: int = 100,
    max_area: int = 50000,
) -> List[Tuple[int, int, int, int]]:
    """Generate candidate bounding boxes from contours."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    proposals: List[Tuple[int, int, int, int]] = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if min_area <= area <= max_area:
            proposals.append((x, y, x + w, y + h))
    return proposals


def detect_with_svm(
    image: np.ndarray,
    svm: cv2.ml.SVM,
) -> List[Dict]:
    """Run contour proposals through the trained SVM classifier."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    proposals = propose_regions(gray)
    detections: List[Dict] = []

    for x1, y1, x2, y2 in proposals:
        crop = gray[y1:y2, x1:x2]
        if crop.size == 0:
            continue
        feat = extract_hog_features(crop).reshape(1, -1)
        _, result = svm.predict(feat)
        cls_id = int(result[0, 0])
        if cls_id < 0:
            continue
        detections.append({
            "class_id": cls_id,
            "confidence": 0.5,  # SVM doesn't naturally produce probabilities
            "bbox_pixels": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        })

    return detections
