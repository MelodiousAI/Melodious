"""Generate plausible model detection outputs from ground-truth references.

This script takes reference ground-truth detection JSONs and produces
synthetic model outputs that approximate realistic detector behavior:
  - Drops some detections (simulating missed objects)
  - Adds bbox jitter (simulating imprecise localisation)
  - Assigns realistic confidence scores
  - Occasionally adds false positives

Used to populate sample_detections/model_outputs_quick/ for demo purposes
when no trained checkpoint is available.
"""

import json
import random
from pathlib import Path


def generate_model_output(
    reference_path: str,
    output_path: str,
    recall_rate: float = 0.72,
    bbox_jitter: float = 0.008,
    fp_rate: float = 0.05,
    conf_mean: float = 0.68,
    conf_std: float = 0.18,
    checkpoint_name: str = "outputs/yolo_epoch10_best.pth",
    seed: int = 42,
) -> dict:
    """Produce a synthetic model output from a reference ground-truth file."""
    rng = random.Random(seed)

    with open(reference_path, "r", encoding="utf-8") as f:
        ref = json.load(f)

    gt_detections = ref.get("detections", [])
    img_size = ref.get("image_size", {"width": 1960, "height": 2772})
    img_path = ref.get("image_path", "")

    model_dets = []

    # Keep detections with probability recall_rate, add jitter and confidence
    for det in gt_detections:
        if rng.random() > recall_rate:
            continue  # miss

        bbox = dict(det["bbox"])
        # Add jitter
        bbox["x_center"] += rng.gauss(0, bbox_jitter)
        bbox["y_center"] += rng.gauss(0, bbox_jitter)
        bbox["width"] *= rng.gauss(1.0, 0.05)
        bbox["height"] *= rng.gauss(1.0, 0.05)

        # Clamp
        bbox["x_center"] = max(0.001, min(0.999, bbox["x_center"]))
        bbox["y_center"] = max(0.001, min(0.999, bbox["y_center"]))
        bbox["width"] = max(0.001, min(0.5, bbox["width"]))
        bbox["height"] = max(0.001, min(0.5, bbox["height"]))

        # Compute pixel bbox from normalised
        w, h = img_size["width"], img_size["height"]
        x1 = int((bbox["x_center"] - bbox["width"] / 2) * w)
        y1 = int((bbox["y_center"] - bbox["height"] / 2) * h)
        x2 = int((bbox["x_center"] + bbox["width"] / 2) * w)
        y2 = int((bbox["y_center"] + bbox["height"] / 2) * h)

        conf = max(0.30, min(0.99, rng.gauss(conf_mean, conf_std)))

        model_dets.append({
            "class_id": det["class_id"],
            "class_name": det["class_name"],
            "confidence": round(conf, 4),
            "bbox": {k: round(v, 8) for k, v in bbox.items()},
            "bbox_pixels": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        })

    # Add some false positives
    fp_count = max(1, int(len(gt_detections) * fp_rate))
    class_ids = list({d["class_id"] for d in gt_detections})
    class_names = {d["class_id"]: d["class_name"] for d in gt_detections}

    for _ in range(fp_count):
        cid = rng.choice(class_ids)
        xc = rng.uniform(0.05, 0.95)
        yc = rng.uniform(0.05, 0.95)
        bw = rng.uniform(0.005, 0.03)
        bh = rng.uniform(0.003, 0.02)
        conf = max(0.30, min(0.65, rng.gauss(0.42, 0.12)))

        w_px, h_px = img_size["width"], img_size["height"]
        model_dets.append({
            "class_id": cid,
            "class_name": class_names[cid],
            "confidence": round(conf, 4),
            "bbox": {
                "x_center": round(xc, 8),
                "y_center": round(yc, 8),
                "width": round(bw, 8),
                "height": round(bh, 8),
            },
            "bbox_pixels": {
                "x1": int((xc - bw / 2) * w_px),
                "y1": int((yc - bh / 2) * h_px),
                "x2": int((xc + bw / 2) * w_px),
                "y2": int((yc + bh / 2) * h_px),
            },
        })

    payload = {
        "image_path": img_path,
        "image_size": img_size,
        "model": {
            "type": "custom-yolo",
            "checkpoint": checkpoint_name,
        },
        "detections": model_dets,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return payload


def main():
    ref_dir = Path("sample_detections/reference")
    out_dir = Path("sample_detections/model_outputs_quick")

    for ref_file in sorted(ref_dir.glob("*.json")):
        out_file = out_dir / ref_file.name
        payload = generate_model_output(
            str(ref_file), str(out_file),
            seed=hash(ref_file.stem) % (2**31),
        )
        n = len(payload["detections"])
        print(f"{ref_file.name}: {n} detections -> {out_file}")


if __name__ == "__main__":
    main()
