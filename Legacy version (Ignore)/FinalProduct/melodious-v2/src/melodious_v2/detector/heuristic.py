"""Honest bootstrap detector used before trained artifacts are wired in.

This detector is for API/UI integration only. It is deliberately labeled as
`heuristic_bootstrap` and must not be reported as trained model performance.
"""

from __future__ import annotations

import io
import time

import cv2
import numpy as np
from PIL import Image

from melodious_v2.contracts import (
    DetectionV2,
    DetectorPayloadV2,
    ImageSize,
    NormalizedBBox,
    PixelBBox,
)
from melodious_v2.taxonomies import DEEPSCORES_136_NAME_TO_ID


BOOTSTRAP_CLASS_NAME = "noteheadBlackOnLine"


def detect_image_bytes(
    image_bytes: bytes,
    run_id: str,
    max_detections: int = 80,
) -> DetectorPayloadV2:
    """Produce a V2 payload from uploaded image bytes using contour proposals."""
    start = time.perf_counter()
    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    width, height = image.size
    array = np.asarray(image)
    _, binary = cv2.threshold(array, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    image_area = width * height
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area < 8 or area > image_area * 0.05:
            continue
        if w <= 1 or h <= 1:
            continue
        confidence = min(0.85, 0.25 + float(area) / max(image_area * 0.002, 1.0))
        candidates.append((confidence, x, y, w, h))

    candidates.sort(reverse=True, key=lambda item: item[0])
    class_id = DEEPSCORES_136_NAME_TO_ID[BOOTSTRAP_CLASS_NAME]
    detections: list[DetectionV2] = []

    for confidence, x, y, w, h in candidates[:max_detections]:
        detections.append(
            DetectionV2(
                class_id=class_id,
                class_name=BOOTSTRAP_CLASS_NAME,
                confidence=float(confidence),
                bbox=NormalizedBBox(
                    x_center=(x + w / 2.0) / width,
                    y_center=(y + h / 2.0) / height,
                    width=w / width,
                    height=h / height,
                ),
                bbox_pixels=PixelBBox(x1=x, y1=y, x2=x + w, y2=y + h),
            )
        )

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return DetectorPayloadV2(
        run_id=run_id,
        model_id="heuristic_bootstrap_detector",
        taxonomy_id="deepscores_136",
        image_size=ImageSize(width=width, height=height),
        detections=detections,
        inference_ms=elapsed_ms,
    )

