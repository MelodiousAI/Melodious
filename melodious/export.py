"""Export utilities for trained models and detection results.

Provides helpers to:
- Save / load custom YOLO checkpoints with metadata.
- Export a model to ONNX for deployment.
- Batch-export detection payloads to a directory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import torch

from .detection_contract import build_detection_payload, build_detection_record


def save_checkpoint(
    model: torch.nn.Module,
    path: str,
    epoch: int = 0,
    metrics: Optional[Dict] = None,
) -> None:
    """Save a custom YOLO checkpoint with training metadata."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_state_dict": model.state_dict(),
        "epoch": epoch,
        "metrics": metrics or {},
    }
    torch.save(payload, str(out))


def load_checkpoint(
    path: str,
    model: torch.nn.Module,
    device: str = "cpu",
) -> Dict:
    """Load a custom YOLO checkpoint and return the metadata dict."""
    ckpt = torch.load(path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    return {"epoch": ckpt.get("epoch", 0), "metrics": ckpt.get("metrics", {})}


def export_onnx(
    model: torch.nn.Module,
    path: str,
    img_size: int = 640,
    opset_version: int = 17,
) -> None:
    """Export a custom YOLO model to ONNX format."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    model.eval()
    dummy = torch.randn(1, 3, img_size, img_size)
    torch.onnx.export(
        model,
        dummy,
        str(out),
        opset_version=opset_version,
        input_names=["image"],
        output_names=["scale_8", "scale_16", "scale_32"],
        dynamic_axes={
            "image": {0: "batch"},
            "scale_8": {0: "batch"},
            "scale_16": {0: "batch"},
            "scale_32": {0: "batch"},
        },
    )


def batch_export_payloads(
    payloads: Sequence[Dict],
    output_dir: str,
) -> List[Path]:
    """Write a sequence of detection payloads to JSON files."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved: List[Path] = []
    for payload in payloads:
        img_name = Path(payload["image_path"]).stem
        dest = out / f"{img_name}.json"
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        saved.append(dest)
    return saved
