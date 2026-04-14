"""Attempt to improve combined pipeline F1 through inference-time techniques.

Techniques evaluated:
1. Test-time augmentation (TTA) — built into ultralytics
2. Confidence threshold tuning — sweep to find optimal F1 point
3. SAHI tiled inference — better recall on dense/small objects
"""

from __future__ import annotations

import glob
import os
import json

import numpy as np


def _load_gt_labels(label_dir: str, image_names: list[str]) -> dict:
    """Load YOLO-format ground truth labels for a set of images."""
    gt = {}
    for name in image_names:
        stem = os.path.splitext(name)[0]
        label_path = os.path.join(label_dir, f"{stem}.txt")
        boxes = []
        if os.path.exists(label_path):
            with open(label_path) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        cls_id = int(parts[0])
                        cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
                        boxes.append((cls_id, cx, cy, w, h))
        gt[stem] = boxes
    return gt


def _iou_xywh(box1, box2):
    """IoU between two (cx, cy, w, h) normalized boxes."""
    x1_min = box1[0] - box1[2] / 2
    x1_max = box1[0] + box1[2] / 2
    y1_min = box1[1] - box1[3] / 2
    y1_max = box1[1] + box1[3] / 2

    x2_min = box2[0] - box2[2] / 2
    x2_max = box2[0] + box2[2] / 2
    y2_min = box2[1] - box2[3] / 2
    y2_max = box2[1] + box2[3] / 2

    xi_min = max(x1_min, x2_min)
    yi_min = max(y1_min, y2_min)
    xi_max = min(x1_max, x2_max)
    yi_max = min(y1_max, y2_max)

    inter = max(0, xi_max - xi_min) * max(0, yi_max - yi_min)
    area1 = box1[2] * box1[3]
    area2 = box2[2] * box2[3]
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0.0


def _compute_f1(pred_boxes, gt_boxes, iou_thresh=0.5):
    """Compute F1 for a single image (class-agnostic matching)."""
    matched_gt = set()
    matched_pred = set()

    # Sort predictions by confidence (descending)
    pred_sorted = sorted(enumerate(pred_boxes), key=lambda x: x[1][1], reverse=True)

    for pi, (_, pred) in enumerate(pred_sorted):
        p_cls, p_conf, p_cx, p_cy, p_w, p_h = pred
        best_iou = 0
        best_gi = -1
        for gi, gt in enumerate(gt_boxes):
            if gi in matched_gt:
                continue
            g_cls, g_cx, g_cy, g_w, g_h = gt
            if p_cls != g_cls:
                continue
            iou = _iou_xywh((p_cx, p_cy, p_w, p_h), (g_cx, g_cy, g_w, g_h))
            if iou > best_iou:
                best_iou = iou
                best_gi = gi
        if best_iou >= iou_thresh and best_gi >= 0:
            matched_gt.add(best_gi)
            matched_pred.add(pi)

    tp = len(matched_gt)
    fp = len(pred_boxes) - tp
    fn = len(gt_boxes) - tp
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1, tp, fp, fn


def evaluate_tta(
    checkpoint: str = "outputs/yolov8_extended/train/weights/best.pt",
    image_dir: str = "yolo_dataset/images/val",
    label_dir: str = "yolo_dataset/labels/val",
    output_dir: str = "outputs/visualizations",
    n_images: int = 100,
):
    """Compare standard vs TTA inference on validation images."""
    from ultralytics import YOLO

    os.makedirs(output_dir, exist_ok=True)
    model = YOLO(checkpoint)

    images = sorted(glob.glob(os.path.join(image_dir, "*.png")))[:n_images]
    image_names = [os.path.basename(p) for p in images]
    gt = _load_gt_labels(label_dir, image_names)

    results_log = {}

    for mode_name, augment_flag in [("standard", False), ("TTA", True)]:
        all_tp, all_fp, all_fn = 0, 0, 0
        all_confs = []

        print(f"\nRunning {mode_name} inference on {len(images)} images...")
        for img_path in images:
            stem = os.path.splitext(os.path.basename(img_path))[0]
            results = model.predict(img_path, imgsz=1024, conf=0.25, augment=augment_flag, verbose=False)
            boxes = results[0].boxes

            # Get image dimensions for normalization
            orig_shape = results[0].orig_shape  # (h, w)
            h, w = orig_shape

            pred_list = []
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                # Normalize to 0-1
                cx = ((x1 + x2) / 2) / w
                cy = ((y1 + y2) / 2) / h
                bw = (x2 - x1) / w
                bh = (y2 - y1) / h
                pred_list.append((cls_id, conf, cx, cy, bw, bh))
                all_confs.append(conf)

            gt_boxes = gt.get(stem, [])
            _, _, _, tp, fp, fn = _compute_f1(pred_list, gt_boxes)
            all_tp += tp
            all_fp += fp
            all_fn += fn

        precision = all_tp / (all_tp + all_fp) if (all_tp + all_fp) > 0 else 0
        recall = all_tp / (all_tp + all_fn) if (all_tp + all_fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        print(f"  {mode_name}: P={precision:.4f}  R={recall:.4f}  F1={f1:.4f}  mean_conf={np.mean(all_confs):.3f}")
        results_log[mode_name] = {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "mean_conf": round(float(np.mean(all_confs)), 3),
            "total_detections": len(all_confs),
            "tp": all_tp, "fp": all_fp, "fn": all_fn,
        }

    # Confidence threshold sweep (standard mode)
    print("\nConfidence threshold sweep (standard mode)...")
    model_results_cache = {}
    for img_path in images:
        stem = os.path.splitext(os.path.basename(img_path))[0]
        results = model.predict(img_path, imgsz=1024, conf=0.1, verbose=False)
        boxes = results[0].boxes
        orig_shape = results[0].orig_shape
        h, w = orig_shape
        preds = []
        for box in boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = ((x1 + x2) / 2) / w
            cy = ((y1 + y2) / 2) / h
            bw = (x2 - x1) / w
            bh = (y2 - y1) / h
            preds.append((cls_id, conf, cx, cy, bw, bh))
        model_results_cache[stem] = preds

    sweep_results = []
    best_f1 = 0
    best_thresh = 0.25

    for thresh in np.arange(0.10, 0.65, 0.05):
        all_tp, all_fp, all_fn = 0, 0, 0
        for img_path in images:
            stem = os.path.splitext(os.path.basename(img_path))[0]
            preds = model_results_cache[stem]
            filtered = [p for p in preds if p[1] >= thresh]
            gt_boxes = gt.get(stem, [])
            _, _, _, tp, fp, fn = _compute_f1(filtered, gt_boxes)
            all_tp += tp
            all_fp += fp
            all_fn += fn

        precision = all_tp / (all_tp + all_fp) if (all_tp + all_fp) > 0 else 0
        recall = all_tp / (all_tp + all_fn) if (all_tp + all_fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        sweep_results.append({"threshold": round(float(thresh), 2), "P": round(precision, 4),
                             "R": round(recall, 4), "F1": round(f1, 4)})
        if f1 > best_f1:
            best_f1 = f1
            best_thresh = thresh
        print(f"  conf={thresh:.2f}  P={precision:.4f}  R={recall:.4f}  F1={f1:.4f}")

    print(f"\n  Best threshold: {best_thresh:.2f} → F1={best_f1:.4f}")
    results_log["threshold_sweep"] = sweep_results
    results_log["best_threshold"] = {"threshold": round(float(best_thresh), 2), "f1": round(best_f1, 4)}

    # Save results
    out_path = os.path.join(output_dir, "f1_improvement_results.json")
    with open(out_path, "w") as f:
        json.dump(results_log, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    evaluate_tta()
