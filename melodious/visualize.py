"""Generate visualization plots for the OMR project report.

1. Per-class F1 bar chart for YOLOv8s (15 classes)
2. Per-class PR curves for top classes
3. Baseline comparison bar chart
"""

import json
import os

import matplotlib.pyplot as plt
import numpy as np


CLASS_NAMES = [
    "notehead-full", "notehead-half", "notehead-whole",
    "clefG", "clefF", "clefC",
    "rest-8th", "rest-quarter", "rest-half", "rest-whole",
    "accidentalSharp", "accidentalFlat", "accidentalNatural",
    "beam", "stem",
]

# Per-class mAP50 from ONNX validation (full 352-image val set)
PER_CLASS_MAP50 = {
    "notehead-full": 0.683,
    "notehead-half": 0.582,
    "notehead-whole": 0.658,
    "clefG": 0.994,
    "clefF": 0.988,
    "clefC": 0.972,
    "rest-8th": 0.709,
    "rest-quarter": 0.752,
    "rest-half": 0.313,
    "rest-whole": 0.404,
    "accidentalSharp": 0.787,
    "accidentalFlat": 0.754,
    "accidentalNatural": 0.520,
    "beam": 0.644,
    "stem": 0.000,
}

PER_CLASS_PRECISION = {
    "notehead-full": 0.973,
    "notehead-half": 0.803,
    "notehead-whole": 0.678,
    "clefG": 0.986,
    "clefF": 0.978,
    "clefC": 0.859,
    "rest-8th": 0.870,
    "rest-quarter": 0.856,
    "rest-half": 0.767,
    "rest-whole": 0.843,
    "accidentalSharp": 0.840,
    "accidentalFlat": 0.836,
    "accidentalNatural": 0.682,
    "beam": 0.917,
    "stem": 1.000,
}

PER_CLASS_RECALL = {
    "notehead-full": 0.371,
    "notehead-half": 0.425,
    "notehead-whole": 0.604,
    "clefG": 0.999,
    "clefF": 0.968,
    "clefC": 0.957,
    "rest-8th": 0.571,
    "rest-quarter": 0.640,
    "rest-half": 0.143,
    "rest-whole": 0.148,
    "accidentalSharp": 0.676,
    "accidentalFlat": 0.661,
    "accidentalNatural": 0.437,
    "beam": 0.378,
    "stem": 0.000,
}


def plot_per_class_f1(output_dir: str):
    """Per-class mAP50 bar chart with color coding by performance tier."""
    os.makedirs(output_dir, exist_ok=True)

    classes = list(PER_CLASS_MAP50.keys())
    values = [PER_CLASS_MAP50[c] for c in classes]

    # Sort by value
    sorted_indices = np.argsort(values)[::-1]
    classes = [classes[i] for i in sorted_indices]
    values = [values[i] for i in sorted_indices]

    # Color by tier
    colors = []
    for v in values:
        if v >= 0.9:
            colors.append("#4CAF50")  # Green — excellent
        elif v >= 0.6:
            colors.append("#2196F3")  # Blue — good
        elif v >= 0.3:
            colors.append("#FF9800")  # Orange — moderate
        else:
            colors.append("#F44336")  # Red — poor

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(range(len(classes)), values, color=colors, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(classes)))
    ax.set_yticklabels(classes, fontsize=10)
    ax.set_xlabel("mAP@0.5", fontsize=12)
    ax.set_title("YOLOv8s Per-Class Detection Performance (mAP@0.5)", fontsize=14, fontweight="bold")
    ax.set_xlim(0, 1.05)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)

    # Add value labels
    for bar, val in zip(bars, values):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#4CAF50", label="Excellent (≥0.9)"),
        Patch(facecolor="#2196F3", label="Good (0.6–0.9)"),
        Patch(facecolor="#FF9800", label="Moderate (0.3–0.6)"),
        Patch(facecolor="#F44336", label="Poor (<0.3)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "per_class_map50.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved per_class_map50.png")


def plot_precision_recall_scatter(output_dir: str):
    """Precision vs Recall scatter plot for all 15 classes."""
    os.makedirs(output_dir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))

    for cls in CLASS_NAMES:
        p = PER_CLASS_PRECISION[cls]
        r = PER_CLASS_RECALL[cls]
        m = PER_CLASS_MAP50[cls]

        # Size by mAP50
        size = max(m * 200, 20)
        color = "#4CAF50" if m >= 0.9 else "#2196F3" if m >= 0.6 else "#FF9800" if m >= 0.3 else "#F44336"

        ax.scatter(r, p, s=size, c=color, alpha=0.7, edgecolors="black", linewidth=0.5)
        ax.annotate(cls, (r, p), fontsize=7, ha="center", va="bottom",
                    xytext=(0, 5), textcoords="offset points")

    ax.set_xlabel("Recall", fontsize=12)
    ax.set_ylabel("Precision", fontsize=12)
    ax.set_title("YOLOv8s Per-Class Precision vs Recall", fontsize=14, fontweight="bold")
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)

    # Add diagonal F1 contour lines
    for f1 in [0.2, 0.4, 0.6, 0.8]:
        recall_range = np.linspace(0.01, 1.0, 100)
        precision_at_f1 = (f1 * recall_range) / (2 * recall_range - f1)
        valid = (precision_at_f1 > 0) & (precision_at_f1 <= 1)
        ax.plot(recall_range[valid], precision_at_f1[valid], "--", color="gray", alpha=0.3, linewidth=0.8)
        # Label
        idx = np.argmin(np.abs(precision_at_f1 - recall_range))
        if valid[idx]:
            ax.text(recall_range[idx], precision_at_f1[idx], f"F1={f1}", fontsize=7, color="gray")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "precision_recall_scatter.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved precision_recall_scatter.png")


def plot_baseline_comparison(output_dir: str):
    """Baseline comparison bar chart."""
    os.makedirs(output_dir, exist_ok=True)

    methods = ["Template\nMatching", "HOG+SVM", "Custom YOLO\n(10 ep)", "YOLOv8s\n(100 ep)"]
    f1_values = [0.165, 0.003, 0.235, 0.652]
    colors = ["#9E9E9E", "#9E9E9E", "#FF9800", "#4CAF50"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(methods, f1_values, color=colors, edgecolor="white", linewidth=1.5, width=0.6)

    # Add value labels
    for bar, val in zip(bars, f1_values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{val:.3f}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    # Add target line
    ax.axhline(y=0.27, color="red", linestyle="--", linewidth=1, label="Target F1 ≥ 0.27")

    ax.set_ylabel("F1 Score / mAP@0.5", fontsize=12)
    ax.set_title("Detection Method Comparison", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 0.8)
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "baseline_comparison.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved baseline_comparison.png")


def plot_gnn_metrics(output_dir: str):
    """GNN per-relationship-type F1 bar chart."""
    os.makedirs(output_dir, exist_ok=True)

    rel_types = ["no_relation", "stem_notehead", "beam_notegroup", "staff_symbol", "accidental_note"]
    f1_values = [0.939, 0.670, 0.785, 0.000, 0.000]
    colors = ["#4CAF50", "#2196F3", "#2196F3", "#F44336", "#F44336"]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(rel_types, f1_values, color=colors, edgecolor="white", linewidth=1.5, width=0.6)

    for bar, val in zip(bars, f1_values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f"{val:.3f}", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_ylabel("F1 Score", fontsize=12)
    ax.set_title("GNN Assembler — Per-Relationship F1", fontsize=14, fontweight="bold")
    ax.set_ylim(0, 1.1)
    ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=15, ha="right")

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "gnn_relationship_f1.png"), dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved gnn_relationship_f1.png")


def plot_confidence_overlay(
    image_paths: list,
    model_checkpoint: str,
    output_dir: str,
    img_size: int = 1024,
    conf_thresh: float = 0.25,
):
    """Draw bounding boxes on score images color-coded by detection confidence.

    Green  = high confidence  (≥ 0.7)
    Yellow = medium confidence (0.5 – 0.7)
    Red    = low confidence   (< 0.5)

    Generates one annotated PNG per input image plus a summary histogram of
    confidence scores across all detections.
    """
    from ultralytics import YOLO
    from PIL import Image, ImageDraw, ImageFont

    os.makedirs(output_dir, exist_ok=True)
    model = YOLO(model_checkpoint)

    all_confs: list = []

    for img_path in image_paths:
        results = model.predict(img_path, imgsz=img_size, conf=conf_thresh, verbose=False)
        result = results[0]

        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        boxes = result.boxes
        for box in boxes:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f"cls{cls_id}"
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            all_confs.append(conf)

            # Color by confidence tier
            if conf >= 0.7:
                color = (34, 139, 34)   # forest green
                tier = "high"
            elif conf >= 0.5:
                color = (255, 200, 0)   # yellow
                tier = "med"
            else:
                color = (220, 20, 60)   # crimson
                tier = "low"

            lw = 2
            draw.rectangle([x1, y1, x2, y2], outline=color, width=lw)
            label = f"{cls_name} {conf:.2f}"
            draw.text((x1, max(y1 - 12, 0)), label, fill=color)

        # Legend box in top-left
        legend_y = 10
        for label_text, lc in [("≥0.7 high", (34, 139, 34)),
                                ("0.5–0.7 med", (255, 200, 0)),
                                ("<0.5 low", (220, 20, 60))]:
            draw.rectangle([10, legend_y, 26, legend_y + 12], fill=lc, outline="black")
            draw.text((30, legend_y), label_text, fill="black")
            legend_y += 18

        stem = os.path.splitext(os.path.basename(img_path))[0]
        out_path = os.path.join(output_dir, f"conf_overlay_{stem}.png")
        img.save(out_path)
        print(f"  Saved {out_path}  ({len(boxes)} detections)")

    # Confidence histogram across all images
    if all_confs:
        fig, ax = plt.subplots(figsize=(7, 4))
        bins = np.arange(conf_thresh, 1.01, 0.05)
        n, _, patches = ax.hist(all_confs, bins=bins, edgecolor="white", linewidth=0.5)
        for patch, left in zip(patches, bins):
            mid = left + 0.025
            if mid >= 0.7:
                patch.set_facecolor("#228B22")
            elif mid >= 0.5:
                patch.set_facecolor("#FFC800")
            else:
                patch.set_facecolor("#DC143C")
        ax.set_xlabel("Detection Confidence", fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.set_title("Confidence Score Distribution (YOLOv8s)", fontsize=14, fontweight="bold")
        ax.axvline(0.7, color="green", ls="--", lw=1, label="High ≥ 0.7")
        ax.axvline(0.5, color="orange", ls="--", lw=1, label="Med ≥ 0.5")
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        hist_path = os.path.join(output_dir, "confidence_histogram.png")
        plt.savefig(hist_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  Saved {hist_path}")

        total = len(all_confs)
        high = sum(1 for c in all_confs if c >= 0.7)
        med = sum(1 for c in all_confs if 0.5 <= c < 0.7)
        low = sum(1 for c in all_confs if c < 0.5)
        print(f"\n  Confidence breakdown ({total} detections):")
        print(f"    High (≥0.7): {high} ({100*high/total:.1f}%)")
        print(f"    Med  (0.5–0.7): {med} ({100*med/total:.1f}%)")
        print(f"    Low  (<0.5): {low} ({100*low/total:.1f}%)")


if __name__ == "__main__":
    output_dir = "outputs/visualizations"
    plot_per_class_f1(output_dir)
    plot_precision_recall_scatter(output_dir)
    plot_baseline_comparison(output_dir)
    plot_gnn_metrics(output_dir)

    # Confidence overlay on a sample of validation images
    import glob
    val_images = sorted(glob.glob("yolo_dataset/images/val/*.png"))[:5]
    if val_images:
        checkpoint = "outputs/yolov8_extended/train/weights/best.pt"
        if os.path.exists(checkpoint):
            print("\nGenerating confidence overlays...")
            plot_confidence_overlay(val_images, checkpoint, output_dir)

    print(f"\nAll plots saved to {output_dir}/")
