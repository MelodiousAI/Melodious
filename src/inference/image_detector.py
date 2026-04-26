"""Image-to-detector-payload helpers for product uploads.

The production path uses a configured detector checkpoint. The fallback path is
intentionally simple and deterministic so the upload/export flow can be tested
even when large model weights are not present in the repository.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image

from src.data_prep.staff_detection import detect_staff_lines


CLASS_ID_TO_NAME = {
    0: "notehead-full",
    1: "notehead-half",
    2: "notehead-whole",
    3: "clefG",
    4: "clefF",
    5: "clefC",
    6: "rest-8th",
    7: "rest-quarter",
    8: "rest-half",
    9: "rest-whole",
    10: "accidentalSharp",
    11: "accidentalFlat",
    12: "accidentalNatural",
    13: "beam",
    14: "stem",
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DETECTOR_CHECKPOINT_ENV = "MELODIOUS_DETECTOR_CHECKPOINT"
DETECTOR_MODEL_TYPE_ENV = "MELODIOUS_DETECTOR_MODEL_TYPE"
DETECTOR_CONF_ENV = "MELODIOUS_DETECTOR_CONFIDENCE"


def _resolve_project_path(path_value: str | os.PathLike[str] | None) -> Path | None:
    if not path_value:
        return None

    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path


def get_detector_runtime_status() -> dict[str, Any]:
    """Return detector readiness details for health/debug surfaces."""

    checkpoint_path = _resolve_project_path(os.getenv(DETECTOR_CHECKPOINT_ENV))
    checkpoint_configured = checkpoint_path is not None
    checkpoint_exists = bool(checkpoint_path and checkpoint_path.exists())
    model_type = os.getenv(DETECTOR_MODEL_TYPE_ENV, "yolov8")
    ready = checkpoint_configured and checkpoint_exists

    if ready:
        message = f"Using {model_type} checkpoint at {checkpoint_path}."
    elif checkpoint_configured:
        message = f"Configured detector checkpoint was not found at {checkpoint_path}; using OpenCV fallback."
    else:
        message = (
            f"Set {DETECTOR_CHECKPOINT_ENV} to enable trained detector inference; "
            "using OpenCV fallback."
        )

    return {
        "model_type": model_type,
        "checkpoint_configured": checkpoint_configured,
        "checkpoint_path": str(checkpoint_path) if checkpoint_path else None,
        "checkpoint_exists": checkpoint_exists,
        "ready": ready,
        "fallback": not ready,
        "message": message,
    }


def _xyxy_to_normalized_center(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    image_width: int,
    image_height: int,
) -> dict[str, float]:
    width = max(0.0, x2 - x1)
    height = max(0.0, y2 - y1)
    return {
        "x_center": (x1 + width / 2.0) / image_width,
        "y_center": (y1 + height / 2.0) / image_height,
        "width": width / image_width,
        "height": height / image_height,
    }


def _build_detection_record(
    class_id: int,
    confidence: float,
    xyxy: tuple[float, float, float, float],
    image_width: int,
    image_height: int,
) -> dict[str, Any]:
    x1, y1, x2, y2 = xyxy
    return {
        "class_id": class_id,
        "class_name": CLASS_ID_TO_NAME[class_id],
        "confidence": confidence,
        "bbox": _xyxy_to_normalized_center(x1, y1, x2, y2, image_width, image_height),
        "bbox_pixels": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
    }


def _build_payload(
    image_path: Path,
    image_width: int,
    image_height: int,
    detections: list[dict[str, Any]],
    model_type: str,
    checkpoint: str | None = None,
) -> dict[str, Any]:
    return {
        "image_path": str(image_path),
        "image_size": {"width": image_width, "height": image_height},
        "model": {"type": model_type, "checkpoint": checkpoint},
        "detections": detections,
    }


@lru_cache(maxsize=4)
def _load_detector_pipeline(model_type: str, checkpoint: str, conf_thresh: float):
    from melodious.pipeline import DetectionPipeline

    return DetectionPipeline(
        model_type=model_type,
        checkpoint=checkpoint,
        conf_thresh=conf_thresh,
    )


def _configured_detector_payload(image_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Run a configured detector checkpoint, or return notices explaining why not."""

    checkpoint_path = _resolve_project_path(os.getenv(DETECTOR_CHECKPOINT_ENV))
    if checkpoint_path is None:
        return None, [
            (
                f"{DETECTOR_CHECKPOINT_ENV} is not configured, so upload transcription used "
                "the built-in OpenCV fallback detector."
            )
        ]

    if not checkpoint_path.exists():
        return None, [
            (
                f"Configured detector checkpoint was not found at {checkpoint_path}; "
                "used the built-in OpenCV fallback detector."
            )
        ]

    model_type = os.getenv(DETECTOR_MODEL_TYPE_ENV, "yolov8")
    conf_thresh = float(os.getenv(DETECTOR_CONF_ENV, "0.3"))
    pipeline = _load_detector_pipeline(model_type, str(checkpoint_path), conf_thresh)
    payload = pipeline.predict(str(image_path))
    return payload, [f"Ran {model_type} detector checkpoint: {checkpoint_path.name}."]


def _estimate_staff_regions(image_path: Path, image_height: int) -> tuple[list[tuple[int, int]], list[str]]:
    notices: list[str] = []

    try:
        staff_regions = detect_staff_lines(str(image_path))
    except Exception as exc:  # pragma: no cover - defensive path for unusual images
        staff_regions = []
        notices.append(f"Staff detection failed ({exc}); using a centered fallback staff.")

    if not staff_regions:
        top = int(image_height * 0.38)
        bottom = int(image_height * 0.62)
        staff_regions = [(top, bottom)]
        notices.append("No staff lines were confidently detected; using a centered fallback staff.")

    return staff_regions, notices


def _find_notehead_candidates(
    gray_image: np.ndarray,
    staff_regions: list[tuple[int, int]],
) -> list[tuple[int, int, int, int]]:
    """Detect compact dark blobs near staff regions as notehead candidates."""

    image_height, image_width = gray_image.shape[:2]
    _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(15, image_width // 18), 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
    cleaned = cv2.subtract(binary, horizontal_lines)
    cleaned = cv2.morphologyEx(
        cleaned,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
    )

    component_count, _, stats, _ = cv2.connectedComponentsWithStats(cleaned, connectivity=8)
    candidates: list[tuple[int, int, int, int]] = []
    min_area = max(8, int(image_width * image_height * 0.00002))
    max_area = max(min_area + 1, int(image_width * image_height * 0.004))

    for label in range(1, component_count):
        x, y, w, h, area = stats[label]
        if area < min_area or area > max_area:
            continue
        if w < 3 or h < 3:
            continue

        aspect_ratio = w / max(h, 1)
        if aspect_ratio < 0.45 or aspect_ratio > 2.4:
            continue

        center_y = y + h / 2.0
        near_staff = any((top - 20) <= center_y <= (bottom + 20) for top, bottom in staff_regions)
        if not near_staff:
            continue

        if x < image_width * 0.12:
            continue

        candidates.append((int(x), int(y), int(x + w), int(y + h)))

    return sorted(candidates, key=lambda box: (box[0], box[1]))[:64]


def _fallback_payload_from_image(image_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Build a simple detector payload from staff lines and dark notehead blobs."""

    with Image.open(image_path) as image:
        image_width, image_height = image.size

    gray_image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if gray_image is None:
        raise FileNotFoundError(f"Could not load uploaded image: {image_path}")

    staff_regions, notices = _estimate_staff_regions(image_path, image_height)
    detections: list[dict[str, Any]] = []

    for top, bottom in staff_regions:
        center_y = (top + bottom) / 2.0
        staff_height = max(18.0, float(bottom - top))
        detections.append(
            _build_detection_record(
                3,
                0.45,
                (
                    image_width * 0.035,
                    max(0.0, center_y - staff_height * 0.55),
                    image_width * 0.095,
                    min(float(image_height), center_y + staff_height * 0.55),
                ),
                image_width,
                image_height,
            )
        )

    notehead_boxes = _find_notehead_candidates(gray_image, staff_regions)
    for box in notehead_boxes:
        detections.append(_build_detection_record(0, 0.42, box, image_width, image_height))

    if not notehead_boxes:
        notices.append(
            "No notehead-like blobs were found; generated quarter-rest placeholders so export stays usable."
        )
        for top, bottom in staff_regions:
            center_y = (top + bottom) / 2.0
            size = max(10.0, (bottom - top) * 0.22)
            detections.append(
                _build_detection_record(
                    7,
                    0.35,
                    (
                        image_width * 0.28,
                        max(0.0, center_y - size),
                        image_width * 0.31,
                        min(float(image_height), center_y + size),
                    ),
                    image_width,
                    image_height,
                )
            )

    payload = _build_payload(
        image_path=image_path,
        image_width=image_width,
        image_height=image_height,
        detections=detections,
        model_type="opencv-fallback",
        checkpoint=None,
    )
    return payload, notices


def build_detection_payload_for_image(image_path: Path) -> tuple[dict[str, Any], list[str]]:
    """Return a detector-contract payload and product-facing processing notices."""

    configured_payload, notices = _configured_detector_payload(image_path)
    if configured_payload is not None:
        return configured_payload, notices

    fallback_payload, fallback_notices = _fallback_payload_from_image(image_path)
    return fallback_payload, notices + fallback_notices
