"""Detection metric implementation with explicit IoU matching."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class DetectionPrediction:
    """Prediction record for metric computation."""

    image_id: str
    box_xyxy: tuple[float, float, float, float]
    class_id: int
    score: float


@dataclass(frozen=True)
class DetectionTarget:
    """Ground-truth detection record."""

    image_id: str
    box_xyxy: tuple[float, float, float, float]
    class_id: int


def compute_iou(
    box_a: tuple[float, float, float, float],
    box_b: tuple[float, float, float, float],
) -> float:
    """Compute IoU for two `[x1, y1, x2, y2]` boxes."""
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_area = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = area_a + area_b - inter_area
    if denom <= 0:
        return 0.0
    return inter_area / denom


def _group_targets_by_image_and_class(
    targets: Iterable[DetectionTarget],
) -> dict[tuple[str, int], list[DetectionTarget]]:
    grouped: dict[tuple[str, int], list[DetectionTarget]] = {}
    for target in targets:
        grouped.setdefault((target.image_id, target.class_id), []).append(target)
    return grouped


def _match_class_predictions(
    predictions: list[DetectionPrediction],
    targets: list[DetectionTarget],
    iou_threshold: float,
) -> tuple[list[int], list[int], int]:
    """Return confidence-sorted TP/FP arrays for one class."""
    targets_by_image = _group_targets_by_image_and_class(targets)
    matched: dict[tuple[str, int], set[int]] = {
        key: set() for key in targets_by_image
    }
    ordered_predictions = sorted(predictions, key=lambda item: item.score, reverse=True)
    tp: list[int] = []
    fp: list[int] = []

    for prediction in ordered_predictions:
        key = (prediction.image_id, prediction.class_id)
        candidate_targets = targets_by_image.get(key, [])
        best_iou = 0.0
        best_index = -1
        for target_index, target in enumerate(candidate_targets):
            if target_index in matched.get(key, set()):
                continue
            iou = compute_iou(prediction.box_xyxy, target.box_xyxy)
            if iou > best_iou:
                best_iou = iou
                best_index = target_index

        if best_iou >= iou_threshold and best_index >= 0:
            tp.append(1)
            fp.append(0)
            matched.setdefault(key, set()).add(best_index)
        else:
            tp.append(0)
            fp.append(1)

    return tp, fp, len(targets)


def average_precision(tp: list[int], fp: list[int], target_count: int) -> float:
    """Compute all-point interpolated AP from confidence-sorted TP/FP arrays."""
    if target_count <= 0:
        return float("nan")
    if not tp:
        return 0.0

    tp_cum = np.cumsum(np.asarray(tp, dtype=float))
    fp_cum = np.cumsum(np.asarray(fp, dtype=float))
    recalls = tp_cum / target_count
    precisions = tp_cum / np.maximum(tp_cum + fp_cum, 1e-12)

    mrec = np.concatenate(([0.0], recalls, [1.0]))
    mpre = np.concatenate(([0.0], precisions, [0.0]))
    for index in range(len(mpre) - 2, -1, -1):
        mpre[index] = max(mpre[index], mpre[index + 1])

    ap = 0.0
    for index in range(1, len(mrec)):
        if mrec[index] != mrec[index - 1]:
            ap += (mrec[index] - mrec[index - 1]) * mpre[index]
    return float(ap)


def _micro_counts(
    predictions: list[DetectionPrediction],
    targets: list[DetectionTarget],
    iou_threshold: float,
    class_ids: list[int],
) -> tuple[int, int, int]:
    total_tp = 0
    total_fp = 0
    total_targets = 0

    for class_id in class_ids:
        class_predictions = [item for item in predictions if item.class_id == class_id]
        class_targets = [item for item in targets if item.class_id == class_id]
        tp, fp, target_count = _match_class_predictions(
            class_predictions,
            class_targets,
            iou_threshold=iou_threshold,
        )
        total_tp += sum(tp)
        total_fp += sum(fp)
        total_targets += target_count

    total_fn = total_targets - total_tp
    return total_tp, total_fp, total_fn


def evaluate_detection_dataset(
    predictions: list[DetectionPrediction],
    targets: list[DetectionTarget],
    class_names: list[str],
    iou_thresholds: Iterable[float] | None = None,
) -> dict:
    """Evaluate a detection dataset with AP and matched F1 metrics.

    Classes without ground-truth support are excluded from mAP means and marked
    with `support = 0` in the per-class table.
    """
    thresholds = list(iou_thresholds or np.arange(0.5, 1.0, 0.05))
    class_ids = list(range(len(class_names)))
    per_threshold_ap: dict[str, dict[str, float]] = {}

    for threshold in thresholds:
        ap_by_class: dict[str, float] = {}
        for class_id, class_name in enumerate(class_names):
            class_predictions = [item for item in predictions if item.class_id == class_id]
            class_targets = [item for item in targets if item.class_id == class_id]
            tp, fp, target_count = _match_class_predictions(
                class_predictions,
                class_targets,
                iou_threshold=float(threshold),
            )
            ap = average_precision(tp, fp, target_count)
            ap_by_class[class_name] = None if np.isnan(ap) else ap
        per_threshold_ap[f"{threshold:.2f}"] = ap_by_class

    map_values = []
    for ap_by_class in per_threshold_ap.values():
        map_values.extend([value for value in ap_by_class.values() if value is not None])

    ap50_by_class = per_threshold_ap.get("0.50", {})
    ap50_values = [value for value in ap50_by_class.values() if value is not None]

    tp, fp, fn = _micro_counts(predictions, targets, 0.5, class_ids)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    per_class = {}
    for class_id, class_name in enumerate(class_names):
        class_predictions = [item for item in predictions if item.class_id == class_id]
        class_targets = [item for item in targets if item.class_id == class_id]
        ctp, cfp, cfn = _micro_counts(class_predictions, class_targets, 0.5, [class_id])
        cprecision = ctp / (ctp + cfp) if (ctp + cfp) else 0.0
        crecall = ctp / (ctp + cfn) if (ctp + cfn) else 0.0
        cf1 = (
            2 * cprecision * crecall / (cprecision + crecall)
            if (cprecision + crecall)
            else 0.0
        )
        ap50 = ap50_by_class.get(class_name)
        per_class[class_name] = {
            "support": len(class_targets),
            "ap@0.5": ap50,
            "precision@0.5": cprecision,
            "recall@0.5": crecall,
            "F1@0.5": cf1,
            "tp": ctp,
            "fp": cfp,
            "fn": cfn,
        }

    return {
        "metric_version": "detection_v2.0",
        "primary_metric": "mAP@0.5:0.95",
        "mAP@0.5:0.95": float(np.mean(map_values)) if map_values else 0.0,
        "mAP@0.5": float(np.mean(ap50_values)) if ap50_values else 0.0,
        "precision@0.5": precision,
        "recall@0.5": recall,
        "F1@0.5": f1,
        "tp@0.5": tp,
        "fp@0.5": fp,
        "fn@0.5": fn,
        "per_class": per_class,
        "ap_by_iou": per_threshold_ap,
    }
