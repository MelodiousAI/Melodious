"""Robustness evaluation of YOLOv8s under image degradation.

Tests detection accuracy under:
- Gaussian noise (sigma = 0.01, 0.05, 0.10)
- JPEG compression (quality = 95, 80, 60, 40)
- Rotation (degrees = ±5, ±10, ±15)

Generates plots to outputs/robustness/.
"""

import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO


def add_gaussian_noise(img: np.ndarray, sigma: float) -> np.ndarray:
    """Add Gaussian noise with given sigma (as fraction of 255)."""
    noise = np.random.normal(0, sigma * 255, img.shape).astype(np.float32)
    noisy = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    return noisy


def jpeg_compress(img: np.ndarray, quality: int) -> np.ndarray:
    """Simulate JPEG compression at given quality level."""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, enc = cv2.imencode(".jpg", img, encode_param)
    return cv2.imdecode(enc, cv2.IMREAD_COLOR)


def rotate_image(img: np.ndarray, angle: float) -> np.ndarray:
    """Rotate image by angle degrees, filling borders with white."""
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(img, M, (w, h), borderValue=(255, 255, 255))


def create_degraded_dataset(
    src_img_dir: str,
    src_lbl_dir: str,
    dst_dir: str,
    transform_fn,
    max_images: int = 100,
) -> str:
    """Create a degraded copy of the dataset for evaluation.

    Returns path to a temporary data.yaml.
    """
    dst_img = os.path.join(dst_dir, "images", "val")
    dst_lbl = os.path.join(dst_dir, "labels", "val")
    os.makedirs(dst_img, exist_ok=True)
    os.makedirs(dst_lbl, exist_ok=True)

    img_files = sorted(Path(src_img_dir).glob("*.*"))[:max_images]
    for img_path in img_files:
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        degraded = transform_fn(img)
        cv2.imwrite(os.path.join(dst_img, img_path.name), degraded)

        # Copy matching label
        lbl_name = img_path.stem + ".txt"
        lbl_src = os.path.join(src_lbl_dir, lbl_name)
        if os.path.exists(lbl_src):
            shutil.copy2(lbl_src, os.path.join(dst_lbl, lbl_name))

    # Write data.yaml
    yaml_path = os.path.join(dst_dir, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(f"path: {dst_dir}\n")
        f.write("train: images/val\n")
        f.write("val: images/val\n")
        f.write("nc: 15\n")
        f.write("names:\n")
        for i, name in enumerate(CLASS_NAMES):
            f.write(f"  {i}: {name}\n")

    return yaml_path


CLASS_NAMES = [
    "notehead-full", "notehead-half", "notehead-whole",
    "clefG", "clefF", "clefC",
    "rest-8th", "rest-quarter", "rest-half", "rest-whole",
    "accidentalSharp", "accidentalFlat", "accidentalNatural",
    "beam", "stem",
]


def evaluate_degradation(model_path: str, data_yaml: str, imgsz: int = 640) -> dict:
    """Run YOLO validation and return key metrics."""
    model = YOLO(model_path)
    results = model.val(data=data_yaml, imgsz=imgsz, batch=8, verbose=False)
    return {
        "mAP50": float(results.box.map50),
        "mAP50-95": float(results.box.map),
        "precision": float(results.box.mp),
        "recall": float(results.box.mr),
    }


def run_robustness_suite(
    model_path: str,
    dataset_dir: str,
    output_dir: str,
    max_images: int = 100,
):
    """Run full robustness evaluation suite and generate plots."""
    os.makedirs(output_dir, exist_ok=True)

    src_img_dir = os.path.join(dataset_dir, "images", "val")
    src_lbl_dir = os.path.join(dataset_dir, "labels", "val")

    results_all = {}

    # --- Baseline (no degradation) ---
    print("=== Baseline (clean) ===")
    baseline = evaluate_degradation(
        model_path, os.path.join(dataset_dir, "data.yaml")
    )
    results_all["baseline"] = baseline
    print(f"  mAP50={baseline['mAP50']:.4f}")

    # --- Gaussian Noise ---
    noise_sigmas = [0.01, 0.05, 0.10]
    noise_results = []
    for sigma in noise_sigmas:
        print(f"=== Gaussian noise sigma={sigma} ===")
        with tempfile.TemporaryDirectory() as tmp:
            yaml_path = create_degraded_dataset(
                src_img_dir, src_lbl_dir, tmp,
                lambda img, s=sigma: add_gaussian_noise(img, s),
                max_images,
            )
            res = evaluate_degradation(model_path, yaml_path)
            noise_results.append(res)
            print(f"  mAP50={res['mAP50']:.4f}")
    results_all["gaussian_noise"] = {
        "sigmas": noise_sigmas,
        "results": noise_results,
    }

    # --- JPEG Compression ---
    jpeg_qualities = [95, 80, 60, 40]
    jpeg_results = []
    for q in jpeg_qualities:
        print(f"=== JPEG quality={q} ===")
        with tempfile.TemporaryDirectory() as tmp:
            yaml_path = create_degraded_dataset(
                src_img_dir, src_lbl_dir, tmp,
                lambda img, quality=q: jpeg_compress(img, quality),
                max_images,
            )
            res = evaluate_degradation(model_path, yaml_path)
            jpeg_results.append(res)
            print(f"  mAP50={res['mAP50']:.4f}")
    results_all["jpeg_compression"] = {
        "qualities": jpeg_qualities,
        "results": jpeg_results,
    }

    # --- Rotation ---
    rotation_angles = [5, 10, 15]
    rotation_results = []
    for angle in rotation_angles:
        print(f"=== Rotation ±{angle}° ===")
        with tempfile.TemporaryDirectory() as tmp:
            yaml_path = create_degraded_dataset(
                src_img_dir, src_lbl_dir, tmp,
                lambda img, a=angle: rotate_image(img, np.random.uniform(-a, a)),
                max_images,
            )
            res = evaluate_degradation(model_path, yaml_path)
            rotation_results.append(res)
            print(f"  mAP50={res['mAP50']:.4f}")
    results_all["rotation"] = {
        "angles": rotation_angles,
        "results": rotation_results,
    }

    # --- Save JSON results ---
    with open(os.path.join(output_dir, "robustness_results.json"), "w") as f:
        json.dump(results_all, f, indent=2)

    # --- Generate plots ---
    _plot_results(results_all, output_dir)

    print(f"\nResults and plots saved to {output_dir}/")
    return results_all


def _plot_results(results: dict, output_dir: str):
    """Generate degradation curve plots."""
    baseline_map = results["baseline"]["mAP50"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Gaussian Noise
    ax = axes[0]
    sigmas = results["gaussian_noise"]["sigmas"]
    maps = [r["mAP50"] for r in results["gaussian_noise"]["results"]]
    ax.plot([0] + sigmas, [baseline_map] + maps, "o-", color="#2196F3", linewidth=2)
    ax.axhline(y=baseline_map, color="gray", linestyle="--", alpha=0.5, label="Baseline")
    ax.set_xlabel("Gaussian Noise σ")
    ax.set_ylabel("mAP@0.5")
    ax.set_title("Gaussian Noise Robustness")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)

    # JPEG Compression
    ax = axes[1]
    quals = results["jpeg_compression"]["qualities"]
    maps = [r["mAP50"] for r in results["jpeg_compression"]["results"]]
    ax.plot([100] + quals, [baseline_map] + maps, "s-", color="#4CAF50", linewidth=2)
    ax.axhline(y=baseline_map, color="gray", linestyle="--", alpha=0.5, label="Baseline")
    ax.set_xlabel("JPEG Quality")
    ax.set_ylabel("mAP@0.5")
    ax.set_title("JPEG Compression Robustness")
    ax.set_ylim(0, 1)
    ax.invert_xaxis()
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Rotation
    ax = axes[2]
    angles = results["rotation"]["angles"]
    maps = [r["mAP50"] for r in results["rotation"]["results"]]
    ax.plot([0] + angles, [baseline_map] + maps, "^-", color="#FF5722", linewidth=2)
    ax.axhline(y=baseline_map, color="gray", linestyle="--", alpha=0.5, label="Baseline")
    ax.set_xlabel("Rotation (±degrees)")
    ax.set_ylabel("mAP@0.5")
    ax.set_title("Rotation Robustness")
    ax.set_ylim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.suptitle("YOLOv8s Robustness Under Image Degradation", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "robustness_curves.png"), dpi=150, bbox_inches="tight")
    plt.close()

    # Individual metric plots
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metrics = ["mAP50", "precision", "recall"]
    colors = ["#2196F3", "#4CAF50", "#FF5722"]

    for i, metric in enumerate(metrics):
        ax = axes[i]
        base_val = results["baseline"][metric]

        # Noise
        vals = [r[metric] for r in results["gaussian_noise"]["results"]]
        ax.plot(results["gaussian_noise"]["sigmas"], vals, "o-", label="Noise σ")

        # JPEG  
        vals = [r[metric] for r in results["jpeg_compression"]["results"]]
        # Normalize quality to 0-1 range for comparison
        norm_q = [(100 - q) / 100 for q in results["jpeg_compression"]["qualities"]]
        ax.plot(norm_q, vals, "s-", label="JPEG (1-Q/100)")

        # Rotation
        vals = [r[metric] for r in results["rotation"]["results"]]
        norm_a = [a / 100 for a in results["rotation"]["angles"]]
        ax.plot(norm_a, vals, "^-", label="Rotation (deg/100)")

        ax.axhline(y=base_val, color="gray", linestyle="--", alpha=0.5)
        ax.set_title(metric)
        ax.set_xlabel("Degradation Level (normalized)")
        ax.set_ylabel(metric)
        ax.set_ylim(0, 1)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle("Per-Metric Degradation Comparison", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "robustness_per_metric.png"), dpi=150, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    from melodious.seed import set_seed
    set_seed(42)

    parser = argparse.ArgumentParser(description="Robustness evaluation")
    parser.add_argument("--model", default="outputs/yolov8_extended/train/weights/best.pt")
    parser.add_argument("--dataset", default="yolo_dataset")
    parser.add_argument("--output", default="outputs/robustness")
    parser.add_argument("--max-images", type=int, default=100,
                        help="Max validation images per degradation level")
    args = parser.parse_args()

    run_robustness_suite(args.model, args.dataset, args.output, args.max_images)
