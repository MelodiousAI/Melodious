"""Evaluation framework for comparing detection methods.

Runs YOLO (custom and/or YOLOv8), template-matching baseline,
HOG+SVM baseline, and optionally the heuristic assembler against
a shared holdout set, then prints a consolidated comparison table.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

from .dataset import CLASS_NAMES, NUM_CLASSES, DeepScoresDataset


# ---------------------------------------------------------------------------
# IoU and matching helpers
# ---------------------------------------------------------------------------

def compute_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    """IoU between two [x1, y1, x2, y2] boxes."""
    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = max(0.0, box_a[2] - box_a[0]) * max(0.0, box_a[3] - box_a[1])
    area_b = max(0.0, box_b[2] - box_b[0]) * max(0.0, box_b[3] - box_b[1])
    return inter / (area_a + area_b - inter + 1e-8)


def match_predictions(
    pred_boxes: np.ndarray,
    pred_labels: np.ndarray,
    pred_scores: np.ndarray,
    gt_boxes: np.ndarray,
    gt_labels: np.ndarray,
    iou_threshold: float = 0.5,
) -> Tuple[int, int, int]:
    """Match predictions to ground truth using greedy IoU assignment.

    Returns (tp, fp, fn).
    """
    if len(gt_boxes) == 0:
        return 0, len(pred_boxes), 0
    if len(pred_boxes) == 0:
        return 0, 0, len(gt_boxes)

    matched_gt = set()
    tp = fp = 0

    # Sort predictions by confidence (descending)
    order = np.argsort(-pred_scores)

    for idx in order:
        best_iou = 0.0
        best_gt = -1
        for j in range(len(gt_boxes)):
            if j in matched_gt:
                continue
            iou = compute_iou(pred_boxes[idx], gt_boxes[j])
            if iou > best_iou:
                best_iou = iou
                best_gt = j
        if best_iou >= iou_threshold and best_gt >= 0 and pred_labels[idx] == gt_labels[best_gt]:
            tp += 1
            matched_gt.add(best_gt)
        else:
            fp += 1

    fn = len(gt_boxes) - len(matched_gt)
    return tp, fp, fn


def compute_ap(precisions: List[float], recalls: List[float]) -> float:
    """Compute average precision from precision-recall curve."""
    if not precisions:
        return 0.0
    mrec = [0.0] + list(recalls) + [1.0]
    mpre = [0.0] + list(precisions) + [0.0]
    # Monotonically decreasing precision
    for i in range(len(mpre) - 2, -1, -1):
        mpre[i] = max(mpre[i], mpre[i + 1])
    # Integrate
    ap = 0.0
    for i in range(1, len(mrec)):
        if mrec[i] != mrec[i - 1]:
            ap += (mrec[i] - mrec[i - 1]) * mpre[i]
    return ap


# ---------------------------------------------------------------------------
# Per-method evaluation
# ---------------------------------------------------------------------------

def evaluate_detections(
    all_preds: List[Dict],
    all_targets: List[Dict],
    iou_thresholds: Tuple[float, ...] = (0.25, 0.5, 0.75),
) -> Dict:
    """Compute detection metrics at multiple IoU thresholds.

    Each element of all_preds / all_targets is a dict with:
      boxes: np.ndarray (N, 4)  [x1,y1,x2,y2]
      labels: np.ndarray (N,)
      scores: np.ndarray (N,)     (1.0 for ground truth)
    """
    results: Dict = {}
    for iou_t in iou_thresholds:
        total_tp = total_fp = total_fn = 0
        per_class = {c: {"tp": 0, "fp": 0, "fn": 0} for c in range(NUM_CLASSES)}
        all_confidences: List[float] = []

        for pred, gt in zip(all_preds, all_targets):
            pboxes = pred["boxes"]
            plabels = pred["labels"]
            pscores = pred["scores"]
            gboxes = gt["boxes"]
            glabels = gt["labels"]

            if len(pscores) > 0:
                all_confidences.extend(pscores.tolist())

            tp, fp, fn = match_predictions(pboxes, plabels, pscores, gboxes, glabels, iou_t)
            total_tp += tp
            total_fp += fp
            total_fn += fn

            # Per-class counts (simplified — aggregate level)
            for lbl in plabels:
                per_class[int(lbl)]["fp"] += 0  # placeholder; exact per-class needs more logic
            for lbl in glabels:
                per_class[int(lbl)]["fn"] += 0

        prec = total_tp / (total_tp + total_fp + 1e-8)
        rec = total_tp / (total_tp + total_fn + 1e-8)
        f1 = 2 * prec * rec / (prec + rec + 1e-8)

        key = f"iou_{iou_t:.2f}"
        results[key] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "tp": total_tp,
            "fp": total_fp,
            "fn": total_fn,
        }

    # Confidence stats
    if all_confidences:
        confs = np.array(all_confidences)
        results["confidence"] = {
            "mean": round(float(confs.mean()), 4),
            "median": round(float(np.median(confs)), 4),
            "frac_above_0.7": round(float((confs >= 0.7).mean()), 4),
        }
    else:
        results["confidence"] = {"mean": 0.0, "median": 0.0, "frac_above_0.7": 0.0}

    return results


# ---------------------------------------------------------------------------
# Run evaluation for each method
# ---------------------------------------------------------------------------

def evaluate_yolo_custom(
    checkpoint_path: str,
    dataset: DeepScoresDataset,
    device: str = "cuda",
    img_size: int = 640,
    conf_thresh: float = 0.3,
    limit: Optional[int] = None,
) -> Dict:
    """Evaluate the custom YOLO detector on a dataset split."""
    from .inference import load_model, preprocess_image

    model = load_model(checkpoint_path, device=device)
    all_preds: List[Dict] = []
    all_targets: List[Dict] = []

    n = min(len(dataset), limit) if limit else len(dataset)
    for i in range(n):
        sample = dataset[i]
        img_path = dataset.annotations[i]["image_path"]

        image_tensor, _ = preprocess_image(img_path, img_size=img_size)
        image_tensor = image_tensor.to(device)

        with torch.no_grad():
            raw = model(image_tensor)
            dets = model.get_detections(raw, conf_thresh=conf_thresh, img_size=img_size)[0]

        all_preds.append({
            "boxes": dets["boxes"].cpu().numpy(),
            "labels": dets["labels"].cpu().numpy(),
            "scores": dets["scores"].cpu().numpy(),
        })

        gt_boxes = sample["boxes"].numpy() if isinstance(sample["boxes"], torch.Tensor) else np.array(sample["boxes"])
        gt_labels = sample["labels"].numpy() if isinstance(sample["labels"], torch.Tensor) else np.array(sample["labels"])
        all_targets.append({
            "boxes": gt_boxes,
            "labels": gt_labels,
            "scores": np.ones(len(gt_labels)),
        })

    return evaluate_detections(all_preds, all_targets)


def evaluate_template_matching(
    dataset_root: str,
    dataset: DeepScoresDataset,
    threshold: float = 0.75,
    limit: Optional[int] = None,
) -> Dict:
    """Evaluate the template-matching baseline."""
    import cv2
    from .baselines.template_matching import extract_templates, detect_with_templates

    templates = extract_templates(Path(dataset_root), max_per_class=20)
    all_preds: List[Dict] = []
    all_targets: List[Dict] = []

    n = min(len(dataset), limit) if limit else len(dataset)
    for i in range(n):
        sample = dataset[i]
        img_path = dataset.annotations[i]["image_path"]
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            continue

        dets = detect_with_templates(image, templates, threshold=threshold)

        pred_boxes = []
        pred_labels = []
        pred_scores = []
        for d in dets:
            b = d["bbox_pixels"]
            pred_boxes.append([b["x1"], b["y1"], b["x2"], b["y2"]])
            pred_labels.append(d["class_id"])
            pred_scores.append(d["confidence"])

        all_preds.append({
            "boxes": np.array(pred_boxes) if pred_boxes else np.zeros((0, 4)),
            "labels": np.array(pred_labels) if pred_labels else np.zeros(0, dtype=int),
            "scores": np.array(pred_scores) if pred_scores else np.zeros(0),
        })

        gt_boxes = sample["boxes"].numpy() if isinstance(sample["boxes"], torch.Tensor) else np.array(sample["boxes"])
        gt_labels = sample["labels"].numpy() if isinstance(sample["labels"], torch.Tensor) else np.array(sample["labels"])
        all_targets.append({
            "boxes": gt_boxes,
            "labels": gt_labels,
            "scores": np.ones(len(gt_labels)),
        })

    return evaluate_detections(all_preds, all_targets)


def evaluate_hog_svm(
    dataset_root: str,
    dataset: DeepScoresDataset,
    limit: Optional[int] = None,
) -> Dict:
    """Evaluate the HOG+SVM baseline."""
    import cv2
    from .baselines.hog_svm import collect_training_data, train_svm, detect_with_svm

    X_train, y_train = collect_training_data(Path(dataset_root), max_per_class=200)
    svm = train_svm(X_train, y_train)

    all_preds: List[Dict] = []
    all_targets: List[Dict] = []

    n = min(len(dataset), limit) if limit else len(dataset)
    for i in range(n):
        sample = dataset[i]
        img_path = dataset.annotations[i]["image_path"]
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            continue

        dets = detect_with_svm(image, svm)

        pred_boxes = []
        pred_labels = []
        pred_scores = []
        for d in dets:
            b = d["bbox_pixels"]
            pred_boxes.append([b["x1"], b["y1"], b["x2"], b["y2"]])
            pred_labels.append(d["class_id"])
            pred_scores.append(d["confidence"])

        all_preds.append({
            "boxes": np.array(pred_boxes) if pred_boxes else np.zeros((0, 4)),
            "labels": np.array(pred_labels) if pred_labels else np.zeros(0, dtype=int),
            "scores": np.array(pred_scores) if pred_scores else np.zeros(0),
        })

        gt_boxes = sample["boxes"].numpy() if isinstance(sample["boxes"], torch.Tensor) else np.array(sample["boxes"])
        gt_labels = sample["labels"].numpy() if isinstance(sample["labels"], torch.Tensor) else np.array(sample["labels"])
        all_targets.append({
            "boxes": gt_boxes,
            "labels": gt_labels,
            "scores": np.ones(len(gt_labels)),
        })

    return evaluate_detections(all_preds, all_targets)


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

def print_comparison_table(results: Dict[str, Dict]) -> str:
    """Format a comparison table across methods."""
    lines = []
    header = f"{'Method':<25} | {'P@0.25':>8} {'R@0.25':>8} {'F1@0.25':>8} | {'P@0.50':>8} {'R@0.50':>8} {'F1@0.50':>8} | {'MeanConf':>8} {'>0.7':>6}"
    lines.append(header)
    lines.append("-" * len(header))

    for method, metrics in results.items():
        m25 = metrics.get("iou_0.25", {})
        m50 = metrics.get("iou_0.50", {})
        conf = metrics.get("confidence", {})
        row = (
            f"{method:<25} | "
            f"{m25.get('precision', 0):>8.4f} {m25.get('recall', 0):>8.4f} {m25.get('f1', 0):>8.4f} | "
            f"{m50.get('precision', 0):>8.4f} {m50.get('recall', 0):>8.4f} {m50.get('f1', 0):>8.4f} | "
            f"{conf.get('mean', 0):>8.4f} {conf.get('frac_above_0.7', 0):>6.2%}"
        )
        lines.append(row)

    table = "\n".join(lines)
    print(table)
    return table


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate detection methods on DeepScores holdout.")
    parser.add_argument("--dataset-root", type=str, default="dataset_ds2_dense")
    parser.add_argument("--split", choices=["train", "test"], default="test")
    parser.add_argument("--checkpoint", type=str, default=None, help="Custom YOLO checkpoint path")
    parser.add_argument("--limit", type=int, default=100, help="Max images to evaluate (100 = holdout)")
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    parser.add_argument("--methods", nargs="+", default=["template", "hog_svm", "custom_yolo"],
                        choices=["template", "hog_svm", "custom_yolo", "yolov8"])
    parser.add_argument("--output", type=str, default=None, help="Save results JSON to this path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = DeepScoresDataset(args.dataset_root, split=args.split, augment=False)

    results: Dict[str, Dict] = {}

    if "template" in args.methods:
        print("Evaluating template matching baseline...")
        results["Template Matching"] = evaluate_template_matching(
            args.dataset_root, dataset, limit=args.limit,
        )

    if "hog_svm" in args.methods:
        print("Evaluating HOG + SVM baseline...")
        results["HOG + SVM"] = evaluate_hog_svm(
            args.dataset_root, dataset, limit=args.limit,
        )

    if "custom_yolo" in args.methods and args.checkpoint:
        print("Evaluating custom YOLO detector...")
        results["Custom YOLO"] = evaluate_yolo_custom(
            args.checkpoint, dataset, device=args.device, limit=args.limit,
        )

    if results:
        print("\n" + "=" * 80)
        print("DETECTION METHOD COMPARISON")
        print("=" * 80)
        table = print_comparison_table(results)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
