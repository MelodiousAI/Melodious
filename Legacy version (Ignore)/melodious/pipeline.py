"""End-to-end detection pipeline: image -> detection JSON payloads.

Supports both the custom YOLO model and a YOLOv8 checkpoint, selected
at construction time.  The pipeline wraps preprocessing, inference,
NMS, and contract-compliant JSON export into a single callable.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import torch
from PIL import Image

from .detection_contract import build_detection_payload, build_detection_record


class DetectionPipeline:
    """Unified interface for running either detector variant."""

    def __init__(
        self,
        model_type: str = "custom",
        checkpoint: Optional[str] = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        conf_thresh: float = 0.3,
        img_size: int = 640,
    ):
        self.model_type = model_type
        self.device = device
        self.conf_thresh = conf_thresh
        self.img_size = img_size
        self.checkpoint = checkpoint
        self._model = None

    # ------------------------------------------------------------------
    # Lazy model loading
    # ------------------------------------------------------------------
    def _load_model(self) -> None:
        if self._model is not None:
            return
        if self.checkpoint is None:
            raise ValueError("checkpoint path is required")

        if self.model_type == "custom":
            from .inference import load_model
            self._model = load_model(self.checkpoint, device=self.device)
        elif self.model_type == "yolov8":
            from ultralytics import YOLO
            self._model = YOLO(self.checkpoint)
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}")

    # ------------------------------------------------------------------
    # Inference
    # ------------------------------------------------------------------
    def predict(self, image_path: str) -> Dict:
        """Run detection on a single image and return a contract payload."""
        self._load_model()

        if self.model_type == "custom":
            payload = self._predict_custom(image_path)
        else:
            payload = self._predict_yolov8(image_path)

        warning = self.check_distribution_warning(payload)
        if warning:
            payload["distribution_warning"] = warning

        return payload

    def predict_batch(self, image_paths: Sequence[str]) -> List[Dict]:
        """Run detection on multiple images."""
        return [self.predict(p) for p in image_paths]

    # ------------------------------------------------------------------
    # Custom YOLO path
    # ------------------------------------------------------------------
    def _predict_custom(self, image_path: str) -> Dict:
        from .inference import preprocess_image

        image_tensor, original_image = preprocess_image(image_path, img_size=self.img_size)
        image_tensor = image_tensor.to(self.device)
        ih, iw = original_image.shape[:2]

        with torch.no_grad():
            raw = self._model(image_tensor)
            dets = self._model.get_detections(raw, conf_thresh=self.conf_thresh, img_size=self.img_size)[0]

        boxes = dets["boxes"].cpu()
        if boxes.numel() > 0:
            boxes[:, [0, 2]] *= iw / self.img_size
            boxes[:, [1, 3]] *= ih / self.img_size

        records = [
            build_detection_record(
                int(label), float(score), box.tolist(), iw, ih,
            )
            for box, score, label in zip(
                boxes, dets["scores"].cpu().tolist(), dets["labels"].cpu().tolist(),
            )
        ]
        return build_detection_payload(
            image_path=image_path,
            image_width=iw,
            image_height=ih,
            detections=records,
            model_type="custom-yolo",
            checkpoint=self.checkpoint,
        )

    # ------------------------------------------------------------------
    # YOLOv8 path
    # ------------------------------------------------------------------
    def _predict_yolov8(self, image_path: str) -> Dict:
        img = Image.open(image_path).convert("RGB")
        iw, ih = img.size
        result = self._model.predict(source=image_path, conf=self.conf_thresh, verbose=False)[0]

        boxes = result.boxes.xyxy.cpu().tolist() if result.boxes is not None else []
        scores = result.boxes.conf.cpu().tolist() if result.boxes is not None else []
        labels = result.boxes.cls.cpu().tolist() if result.boxes is not None else []

        records = [
            build_detection_record(int(label), score, box, iw, ih)
            for box, score, label in zip(boxes, scores, labels)
        ]
        return build_detection_payload(
            image_path=image_path,
            image_width=iw,
            image_height=ih,
            detections=records,
            model_type="yolov8",
            checkpoint=self.checkpoint,
        )

    # ------------------------------------------------------------------
    # Convenience I/O
    # ------------------------------------------------------------------
    @staticmethod
    def check_distribution_warning(payload: Dict, low_conf_threshold: float = 0.5,
                                    warning_fraction: float = 0.5) -> Optional[str]:
        """Check if detections suggest out-of-distribution input.

        If more than ``warning_fraction`` of detections have confidence below
        ``low_conf_threshold``, returns a warning string.  Otherwise returns
        ``None``.  This implements the confidence-based non-Western notation
        flag required by the responsible ML specification.
        """
        detections = payload.get("detections", [])
        if not detections:
            return None
        low = sum(1 for d in detections if d.get("confidence", 1.0) < low_conf_threshold)
        if low / len(detections) > warning_fraction:
            return (
                "This score may use notation outside the system's training "
                "distribution. Results may be unreliable."
            )
        return None

    @staticmethod
    def save_payload(payload: Dict, path: str) -> None:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
