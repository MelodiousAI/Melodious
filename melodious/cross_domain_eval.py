"""Cross-domain evaluation: print-trained YOLOv8s on handwritten (CVC-MUSCIMA) scores.

Measures distribution shift by comparing detection statistics on the
DeepScores-v2 validation set (printed, in-domain) versus CVC-MUSCIMA
(handwritten, out-of-domain).
"""

from __future__ import annotations

import glob
import json
import os
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def _run_on_images(model, image_paths: list[str], img_size: int = 1024,
                   conf: float = 0.25) -> dict:
    """Run YOLOv8 on a list of images and collect detection statistics."""
    all_confs = []
    per_image_counts = []
    per_class_counts: dict[str, int] = {}

    for path in image_paths:
        results = model.predict(path, imgsz=img_size, conf=conf, verbose=False)
        boxes = results[0].boxes
        confs = [float(c) for c in boxes.conf]
        all_confs.extend(confs)
        per_image_counts.append(len(confs))

        for cls_id in boxes.cls:
            name = model.names[int(cls_id)]
            per_class_counts[name] = per_class_counts.get(name, 0) + 1

    return {
        "n_images": len(image_paths),
        "total_detections": len(all_confs),
        "mean_conf": float(np.mean(all_confs)) if all_confs else 0.0,
        "median_conf": float(np.median(all_confs)) if all_confs else 0.0,
        "std_conf": float(np.std(all_confs)) if all_confs else 0.0,
        "high_frac": sum(1 for c in all_confs if c >= 0.7) / max(len(all_confs), 1),
        "med_frac": sum(1 for c in all_confs if 0.5 <= c < 0.7) / max(len(all_confs), 1),
        "low_frac": sum(1 for c in all_confs if c < 0.5) / max(len(all_confs), 1),
        "detections_per_image": float(np.mean(per_image_counts)) if per_image_counts else 0.0,
        "per_class_counts": per_class_counts,
        "all_confs": all_confs,
    }


def cross_domain_comparison(
    checkpoint: str = "outputs/yolov8_extended/train/weights/best.pt",
    printed_dir: str = "yolo_dataset/images/val",
    handwritten_dir: str = "data/cvc-muscima/CVCMUSCIMA_WI/PNG_GT_Gray",
    output_dir: str = "outputs/visualizations",
    n_printed: int = 50,
    n_handwritten: int = 50,
    seed: int = 42,
):
    """Compare YOLOv8s detection behavior on printed vs handwritten scores."""
    from ultralytics import YOLO

    os.makedirs(output_dir, exist_ok=True)
    random.seed(seed)

    model = YOLO(checkpoint)

    # Collect printed images (in-domain)
    printed_images = sorted(glob.glob(os.path.join(printed_dir, "*.png")))
    if len(printed_images) > n_printed:
        printed_images = random.sample(printed_images, n_printed)

    # Collect handwritten images (out-of-domain) — sample across writers
    hw_images = sorted(glob.glob(os.path.join(handwritten_dir, "w-*", "*.png")))
    if len(hw_images) > n_handwritten:
        hw_images = random.sample(hw_images, n_handwritten)

    print(f"Printed (in-domain): {len(printed_images)} images")
    print(f"Handwritten (OOD):   {len(hw_images)} images")
    print()

    print("Running on printed images...")
    stats_printed = _run_on_images(model, printed_images)
    print("Running on handwritten images...")
    stats_hw = _run_on_images(model, hw_images)

    # Print comparison table
    print("\n" + "=" * 65)
    print(f"{'Metric':<30} {'Printed':>15} {'Handwritten':>15}")
    print("-" * 65)
    for key in ["n_images", "total_detections", "detections_per_image",
                "mean_conf", "median_conf", "std_conf",
                "high_frac", "med_frac", "low_frac"]:
        vp = stats_printed[key]
        vh = stats_hw[key]
        if isinstance(vp, float):
            print(f"{key:<30} {vp:>15.3f} {vh:>15.3f}")
        else:
            print(f"{key:<30} {vp:>15} {vh:>15}")
    print("=" * 65)

    # Confidence distribution comparison plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    bins = np.arange(0.25, 1.01, 0.05)

    for ax, confs, title, color in [
        (axes[0], stats_printed["all_confs"], "Printed (In-Domain)", "#2196F3"),
        (axes[1], stats_hw["all_confs"], "Handwritten (OOD)", "#F44336"),
    ]:
        if confs:
            ax.hist(confs, bins=bins, color=color, edgecolor="white", alpha=0.8)
        ax.set_xlabel("Confidence", fontsize=11)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.axvline(0.7, color="green", ls="--", lw=1)
        ax.axvline(0.5, color="orange", ls="--", lw=1)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Count", fontsize=11)

    fig.suptitle("Detection Confidence: Printed vs Handwritten Scores", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cross_domain_confidence.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Detections-per-image comparison
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ["Printed\n(In-Domain)", "Handwritten\n(OOD)"]
    means = [stats_printed["detections_per_image"], stats_hw["detections_per_image"]]
    colors = ["#2196F3", "#F44336"]
    ax.bar(labels, means, color=colors, edgecolor="white", width=0.5)
    for i, v in enumerate(means):
        ax.text(i, v + 1, f"{v:.1f}", ha="center", fontsize=11, fontweight="bold")
    ax.set_ylabel("Mean Detections per Image", fontsize=11)
    ax.set_title("Detection Volume: Print vs Handwritten", fontsize=13, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "cross_domain_det_count.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Confidence overlay on 3 handwritten images
    from melodious.visualize import plot_confidence_overlay, CLASS_NAMES

    hw_sample = hw_images[:3]
    if hw_sample:
        print("\nGenerating confidence overlays on handwritten samples...")
        plot_confidence_overlay(hw_sample, checkpoint, output_dir)

    # Save stats as JSON
    def _clean(s):
        s2 = {k: v for k, v in s.items() if k != "all_confs"}
        return s2

    stats_path = os.path.join(output_dir, "cross_domain_stats.json")
    with open(stats_path, "w") as f:
        json.dump({"printed": _clean(stats_printed), "handwritten": _clean(stats_hw)}, f, indent=2)
    print(f"\nSaved cross_domain_stats.json, cross_domain_confidence.png, cross_domain_det_count.png")

    return stats_printed, stats_hw


if __name__ == "__main__":
    cross_domain_comparison()
