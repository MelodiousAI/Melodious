"""Clean-sheet note extraction helpers for local demos.

This module is intentionally separate from the official detector metric path.
It can use a YOLO checkpoint to detect notehead boxes, estimate pitch from staff
geometry, and infer simple rhythm from notehead/beam/flag/dot geometry.
"""

from __future__ import annotations

import json
import shutil
from collections import Counter
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np


STEP_NAMES = ["C", "D", "E", "F", "G", "A", "B"]
STEP_TO_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
TREBLE_BOTTOM_LINE_DIATONIC = 7 * 4 + STEP_NAMES.index("E")
FLAT_KEY_ORDER = ["B", "E", "A", "D", "G", "C", "F"]
SHARP_KEY_ORDER = ["F", "C", "G", "D", "A", "E", "B"]


@dataclass(frozen=True)
class StaffSystem:
    """Detected five-line staff geometry."""

    index: int
    line_y: tuple[float, float, float, float, float]
    spacing: float
    start_x: float
    end_x: float

    @property
    def top_y(self) -> float:
        return self.line_y[0]

    @property
    def bottom_y(self) -> float:
        return self.line_y[-1]

    def contains_y(self, y: float, ledger_margin_steps: float = 6.0) -> bool:
        margin = (self.spacing / 2.0) * ledger_margin_steps
        return self.top_y - margin <= y <= self.bottom_y + margin


@dataclass(frozen=True)
class DetectionCandidate:
    """Raw note/rest detection candidate."""

    class_id: int
    class_name: str
    confidence: float
    bbox_xyxy: tuple[float, float, float, float]
    source: str

    @property
    def x_center(self) -> float:
        return (self.bbox_xyxy[0] + self.bbox_xyxy[2]) / 2.0

    @property
    def y_center(self) -> float:
        return (self.bbox_xyxy[1] + self.bbox_xyxy[3]) / 2.0

    @property
    def width(self) -> float:
        return self.bbox_xyxy[2] - self.bbox_xyxy[0]

    @property
    def height(self) -> float:
        return self.bbox_xyxy[3] - self.bbox_xyxy[1]


@dataclass(frozen=True)
class ExtractedNote:
    """Pitch-level note extracted from an image."""

    event_type: str
    order: int
    staff_index: int
    x_center: float
    y_center: float
    bbox_xyxy: tuple[float, float, float, float]
    class_name: str
    confidence: float
    source: str
    step: str
    octave: int
    midi_pitch: int
    quarter_length: float
    onset_quarter: float
    alter: int = 0
    pitch_source: str = "staff_geometry"
    dotted: bool = False
    rhythm_source: str = "default"
    stem_detected: bool = False
    slur_starts: tuple[int, ...] = ()
    slur_stops: tuple[int, ...] = ()
    tie_starts: tuple[int, ...] = ()
    tie_stops: tuple[int, ...] = ()


@dataclass(frozen=True)
class ExtractedRest:
    """Rest event extracted from an image."""

    event_type: str
    order: int
    staff_index: int
    x_center: float
    y_center: float
    bbox_xyxy: tuple[float, float, float, float]
    class_name: str
    confidence: float
    source: str
    quarter_length: float
    onset_quarter: float
    dotted: bool = False
    rhythm_source: str = "rest_class"


ExtractedMusicEvent = ExtractedNote | ExtractedRest


@dataclass(frozen=True)
class CandidateRelationship:
    """Relationship between two detection candidates used during extraction."""

    source: DetectionCandidate
    target: DetectionCandidate
    relationship_type: str
    confidence: float


@dataclass(frozen=True)
class ExtractionArtifacts:
    """Paths written by an extraction run."""

    output_dir: str
    notes_json: str
    midi_path: str
    musicxml_path: str
    overlay_path: str
    checkpoint_snapshot: str | None = None
    thin_symbol_checkpoint_snapshot: str | None = None
    detector_payload_json: str | None = None
    relationships_json: str | None = None


@dataclass(frozen=True)
class ExtractionResult:
    """Complete result for a note extraction run."""

    image_path: str
    image_width: int
    image_height: int
    extractor_mode: str
    detector_checkpoint: str | None
    thin_symbol_checkpoint: str | None
    gnn_checkpoint: str | None
    staff_systems: list[StaffSystem]
    events: list[ExtractedMusicEvent]
    notes: list[ExtractedNote]
    key_signatures: dict[int, dict[str, int]]
    key_fifths: int = 0
    assembly_mode: dict[str, Any] | None = None
    relationship_count: int = 0
    relationship_counts: dict[str, int] | None = None
    notation_symbol_count: int = 0
    artifacts: ExtractionArtifacts | None = None
    warnings: list[str] | None = None


def read_grayscale_image(image_path: str | Path) -> np.ndarray:
    """Read an image as grayscale and fail clearly if OpenCV cannot decode it."""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {Path(image_path)}")
    return image


def _group_runs(values: np.ndarray, max_gap: int = 3) -> list[tuple[int, int]]:
    if values.size == 0:
        return []
    groups: list[tuple[int, int]] = []
    start = previous = int(values[0])
    for raw in values[1:]:
        value = int(raw)
        if value - previous <= max_gap:
            previous = value
            continue
        groups.append((start, previous))
        start = previous = value
    groups.append((start, previous))
    return groups


def _largest_column_run(mask: np.ndarray) -> tuple[float, float]:
    columns = np.where(mask.any(axis=0))[0]
    if columns.size == 0:
        return 0.0, float(mask.shape[1] - 1)
    runs = _group_runs(columns, max_gap=8)
    start, end = max(runs, key=lambda item: item[1] - item[0])
    return float(start), float(end)


def _horizontal_staff_masks(image: np.ndarray, width: int) -> list[np.ndarray]:
    """Return horizontal masks that preserve both dark and light staff strokes."""
    _, otsu_binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, light_line_binary = cv2.threshold(image, 245, 255, cv2.THRESH_BINARY_INV)
    adaptive_binary = cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        12,
    )
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(30, width // 60), 1))
    masks = []
    for binary in (otsu_binary, light_line_binary, adaptive_binary):
        masks.append(cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1))
    return masks


def _staff_candidates_from_horizontal(horizontal: np.ndarray, height: int, width: int) -> list[StaffSystem]:
    """Detect candidate five-line systems from one horizontal-line mask."""
    row_counts = (horizontal > 0).sum(axis=1)
    thresholds = (max(120, int(width * 0.15)),)
    candidates: list[StaffSystem] = []
    for threshold in thresholds:
        rows = np.where(row_counts > threshold)[0]
        line_centers = [(start + end) / 2.0 for start, end in _group_runs(rows, max_gap=3)]

        i = 0
        while i <= len(line_centers) - 5:
            group = line_centers[i : i + 5]
            diffs = np.diff(group)
            if len(diffs) == 4 and float(np.std(diffs)) < 3.0 and 5.0 <= float(np.mean(diffs)) <= 30.0:
                spacing = float(np.mean(diffs))
                y0 = max(0, int(min(group)) - 3)
                y1 = min(height, int(max(group)) + 4)
                start_x, end_x = _largest_column_run(horizontal[y0:y1, :])
                candidates.append(
                    StaffSystem(
                        index=0,
                        line_y=tuple(float(value) for value in group),  # type: ignore[arg-type]
                        spacing=spacing,
                        start_x=start_x,
                        end_x=end_x,
                    )
                )
                i += 5
                continue
            i += 1
    return candidates


def _merge_staff_system_candidates(candidates: list[StaffSystem]) -> list[StaffSystem]:
    """Merge duplicate staff detections from several horizontal-line masks."""
    merged: list[StaffSystem] = []
    for candidate in sorted(candidates, key=lambda staff: (staff.top_y + staff.bottom_y) / 2.0):
        replacement_index: int | None = None
        candidate_center = (candidate.top_y + candidate.bottom_y) / 2.0
        for index, existing in enumerate(merged):
            existing_center = (existing.top_y + existing.bottom_y) / 2.0
            center_close = abs(candidate_center - existing_center) <= max(candidate.spacing, existing.spacing) * 1.5
            vertical_overlap = candidate.top_y <= existing.bottom_y and existing.top_y <= candidate.bottom_y
            if center_close or vertical_overlap:
                replacement_index = index
                break

        if replacement_index is None:
            merged.append(candidate)
            continue

        existing = merged[replacement_index]
        candidate_span = candidate.end_x - candidate.start_x
        existing_span = existing.end_x - existing.start_x
        candidate_height = candidate.bottom_y - candidate.top_y
        existing_height = existing.bottom_y - existing.top_y
        if candidate_span > existing_span * 1.05 or (
            candidate_span >= existing_span * 0.95 and candidate_height > existing_height * 1.1
        ):
            merged[replacement_index] = candidate

    return [
        StaffSystem(
            index=index,
            line_y=staff.line_y,
            spacing=staff.spacing,
            start_x=staff.start_x,
            end_x=staff.end_x,
        )
        for index, staff in enumerate(sorted(merged, key=lambda item: item.top_y))
    ]


def detect_staff_systems(image: np.ndarray) -> list[StaffSystem]:
    """Detect five-line staff systems from long horizontal strokes."""
    height, width = image.shape[:2]
    candidates: list[StaffSystem] = []
    for horizontal in _horizontal_staff_masks(image, width):
        candidates.extend(_staff_candidates_from_horizontal(horizontal, height, width))
    return _merge_staff_system_candidates(candidates)


def _bbox_iou(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    inter_w = max(0.0, ix2 - ix1)
    inter_h = max(0.0, iy2 - iy1)
    intersection = inter_w * inter_h
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - intersection
    return intersection / union if union else 0.0


def _deduplicate_candidates(candidates: list[DetectionCandidate], spacing: float) -> list[DetectionCandidate]:
    ordered = sorted(candidates, key=lambda item: item.confidence, reverse=True)
    kept: list[DetectionCandidate] = []
    for candidate in ordered:
        duplicate = False
        for existing in kept:
            center_close = (
                abs(candidate.x_center - existing.x_center) <= spacing * 0.75
                and abs(candidate.y_center - existing.y_center) <= spacing * 0.75
            )
            if center_close or _bbox_iou(candidate.bbox_xyxy, existing.bbox_xyxy) > 0.45:
                duplicate = True
                break
        if not duplicate:
            kept.append(candidate)
    return sorted(kept, key=lambda item: (item.y_center, item.x_center))


def snapshot_checkpoint(checkpoint_path: str | Path, output_dir: str | Path, *, label: str | None = None) -> Path:
    """Copy a checkpoint before inference so live training can keep writing safely."""
    source = Path(checkpoint_path)
    if not source.exists():
        raise FileNotFoundError(f"Checkpoint not found: {source}")
    prefix = f"{label}_" if label else ""
    destination = Path(output_dir) / f"{prefix}{source.stem}_snapshot{source.suffix}"
    shutil.copy2(source, destination)
    return destination


def yolo_detection_candidates(
    image_path: str | Path,
    checkpoint_path: str | Path,
    *,
    confidence: float = 0.12,
    imgsz: int = 1472,
    max_det: int = 2000,
    device: str = "cpu",
) -> list[DetectionCandidate]:
    """Run YOLO and return all detector candidates."""
    try:
        from ultralytics import YOLO
    except Exception as exc:  # pragma: no cover - optional runtime dependency
        raise RuntimeError("ultralytics is required for YOLO note extraction.") from exc

    model = YOLO(str(checkpoint_path))
    result = model.predict(
        source=str(image_path),
        imgsz=imgsz,
        conf=confidence,
        iou=0.5,
        max_det=max_det,
        device=device,
        verbose=False,
    )[0]
    names = model.names
    candidates: list[DetectionCandidate] = []
    for box in result.boxes:
        class_id = int(box.cls.item())
        if isinstance(names, dict):
            class_name = str(names.get(class_id, class_id))
        else:
            class_name = str(names[class_id])
        candidates.append(
            DetectionCandidate(
                class_id=class_id,
                class_name=class_name,
                confidence=float(box.conf.item()),
                bbox_xyxy=tuple(float(value) for value in box.xyxy[0].tolist()),  # type: ignore[arg-type]
                source="yolo",
            )
        )
    return candidates


def _axis_starts(length: int, tile_length: int, stride: int) -> list[int]:
    if tile_length <= 0 or stride <= 0:
        raise ValueError("Tile size and stride must be positive.")
    if length <= tile_length:
        return [0]
    starts = list(range(0, length - tile_length + 1, stride))
    final = length - tile_length
    if starts[-1] != final:
        starts.append(final)
    return sorted(set(starts))


def yolo_tiled_detection_candidates(
    image_path: str | Path,
    checkpoint_path: str | Path,
    *,
    confidence: float = 0.05,
    imgsz: int = 1024,
    max_det: int = 1000,
    device: str = "cpu",
    tile_size: int = 384,
    stride: int = 256,
) -> list[DetectionCandidate]:
    """Run YOLO on overlapping source-pixel tiles and map boxes back to page coordinates."""
    try:
        from ultralytics import YOLO
    except Exception as exc:  # pragma: no cover - optional runtime dependency
        raise RuntimeError("ultralytics is required for YOLO tiled note extraction.") from exc

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {Path(image_path)}")

    height, width = image.shape[:2]
    model = YOLO(str(checkpoint_path))
    names = model.names
    candidates: list[DetectionCandidate] = []
    source_index = 0
    for y0 in _axis_starts(height, tile_size, stride):
        for x0 in _axis_starts(width, tile_size, stride):
            tile = image[y0 : min(height, y0 + tile_size), x0 : min(width, x0 + tile_size)]
            result = model.predict(
                source=tile,
                imgsz=imgsz,
                conf=confidence,
                iou=0.5,
                max_det=max_det,
                device=device,
                verbose=False,
            )[0]
            for box in result.boxes:
                class_id = int(box.cls.item())
                if isinstance(names, dict):
                    class_name = str(names.get(class_id, class_id))
                else:
                    class_name = str(names[class_id])
                tx1, ty1, tx2, ty2 = [float(value) for value in box.xyxy[0].tolist()]
                x1 = max(0.0, min(float(width), tx1 + x0))
                y1 = max(0.0, min(float(height), ty1 + y0))
                x2 = max(0.0, min(float(width), tx2 + x0))
                y2 = max(0.0, min(float(height), ty2 + y0))
                if x2 <= x1 or y2 <= y1:
                    continue
                candidates.append(
                    DetectionCandidate(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=float(box.conf.item()),
                        bbox_xyxy=(x1, y1, x2, y2),
                        source=f"yolo_tiled_{source_index}",
                    )
                )
            source_index += 1
    return candidates


def yolo_note_candidates(
    image_path: str | Path,
    checkpoint_path: str | Path,
    *,
    confidence: float = 0.12,
    imgsz: int = 1472,
    max_det: int = 2000,
    device: str = "cpu",
) -> list[DetectionCandidate]:
    """Run YOLO and return notehead candidates only."""
    return [
        candidate
        for candidate in yolo_detection_candidates(
            image_path,
            checkpoint_path,
            confidence=confidence,
            imgsz=imgsz,
            max_det=max_det,
            device=device,
        )
        if is_notehead(candidate.class_name)
    ]


def cv_note_candidates(image: np.ndarray, staff_systems: list[StaffSystem]) -> list[DetectionCandidate]:
    """Return contour-based notehead candidates for clean printed single-staff pages."""
    height, width = image.shape[:2]
    if not staff_systems:
        return []
    median_spacing = float(np.median([staff.spacing for staff in staff_systems]))
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    without_lines = binary.copy()
    line_half_thickness = max(1, int(round(median_spacing * 0.06)))
    for staff in staff_systems:
        for y_value in staff.line_y:
            y = int(round(y_value))
            without_lines[
                max(0, y - line_half_thickness) : min(height, y + line_half_thickness + 1),
                :,
            ] = 0

    kernel_w = max(3, int(round(median_spacing * 0.25)))
    kernel_h = max(3, int(round(median_spacing * 0.25)))
    if kernel_w % 2 == 0:
        kernel_w += 1
    if kernel_h % 2 == 0:
        kernel_h += 1
    opening_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_w, kernel_h))
    opened = cv2.morphologyEx(without_lines, cv2.MORPH_OPEN, opening_kernel, iterations=1)
    close_size = max(3, int(round(median_spacing * 0.25)))
    if close_size % 2 == 0:
        close_size += 1
    close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_size, close_size))
    processed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, close_kernel, iterations=1)
    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates: list[DetectionCandidate] = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = float(cv2.contourArea(contour))
        if area < 8.0:
            continue
        x_center = x + w / 2.0
        y_center = y + h / 2.0
        staff = closest_staff(y_center, staff_systems)
        if staff is None or not staff.contains_y(y_center, ledger_margin_steps=5.5):
            continue
        if x_center < staff.start_x + staff.spacing * 4.0:
            continue
        if not (0.45 * median_spacing <= w <= 1.9 * median_spacing):
            continue
        if not (0.35 * median_spacing <= h <= 1.7 * median_spacing):
            continue
        aspect = w / max(h, 1)
        if not (0.55 <= aspect <= 2.5):
            continue
        crop = without_lines[y : y + h, x : x + w]
        density = float((crop > 0).mean()) if crop.size else 0.0
        if density < 0.14:
            continue
        candidates.append(
            DetectionCandidate(
                class_id=-1,
                class_name="noteheadCvCandidate",
                confidence=min(0.95, max(0.20, density)),
                bbox_xyxy=(float(x), float(y), float(x + w), float(y + h)),
                source="cv_fallback",
            )
        )
    return candidates


def cv_augmentation_dot_candidates(
    image: np.ndarray,
    staff_systems: list[StaffSystem],
) -> list[DetectionCandidate]:
    """Return tiny contour candidates that can act as augmentation dots."""
    height, _ = image.shape[:2]
    if not staff_systems:
        return []
    median_spacing = float(np.median([staff.spacing for staff in staff_systems]))
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    without_lines = binary.copy()
    line_half_thickness = max(1, int(round(median_spacing * 0.06)))
    for staff in staff_systems:
        for y_value in staff.line_y:
            y = int(round(y_value))
            without_lines[
                max(0, y - line_half_thickness) : min(height, y + line_half_thickness + 1),
                :,
            ] = 0

    contours, _ = cv2.findContours(without_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates: list[DetectionCandidate] = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if not (0.12 * median_spacing <= w <= 0.75 * median_spacing):
            continue
        if not (0.12 * median_spacing <= h <= 0.75 * median_spacing):
            continue
        aspect = w / max(h, 1)
        if not (0.45 <= aspect <= 2.2):
            continue
        crop = without_lines[y : y + h, x : x + w]
        density = float((crop > 0).mean()) if crop.size else 0.0
        if density < 0.35:
            continue
        x_center = x + w / 2.0
        y_center = y + h / 2.0
        staff = closest_staff(y_center, staff_systems)
        if staff is None or not staff.contains_y(y_center, ledger_margin_steps=5.5):
            continue
        if x_center < staff.start_x + staff.spacing * 4.0:
            continue
        candidates.append(
            DetectionCandidate(
                class_id=-2,
                class_name="augmentationDot",
                confidence=min(0.95, max(0.20, density)),
                bbox_xyxy=(float(x), float(y), float(x + w), float(y + h)),
                source="cv_dot",
            )
        )
    return candidates


def _dot_candidate_attaches_to_note(
    note: DetectionCandidate,
    dot: DetectionCandidate,
    staff: StaffSystem,
) -> bool:
    if dot.source == "cv_open_note_dot" and not is_open_notehead(note.class_name):
        return False
    _, _, x2, _ = note.bbox_xyxy
    if dot.x_center <= note.x_center:
        return False
    x_distance = dot.x_center - x2
    y_distance = abs(dot.y_center - note.y_center)
    return 0.0 <= x_distance <= staff.spacing * 2.8 and y_distance <= staff.spacing * 0.9


def cv_open_note_dot_candidates(
    image: np.ndarray,
    staff_systems: list[StaffSystem],
    note_candidates: list[DetectionCandidate],
) -> list[DetectionCandidate]:
    """Return CV dot candidates that tightly attach to open noteheads only."""
    open_notes = [candidate for candidate in note_candidates if is_open_notehead(candidate.class_name)]
    if not open_notes:
        return []
    dots: list[DetectionCandidate] = []
    for dot in cv_augmentation_dot_candidates(image, staff_systems):
        for note in open_notes:
            staff = closest_staff(note.y_center, staff_systems)
            if staff is None:
                continue
            if _dot_candidate_attaches_to_note(note, dot, staff):
                dots.append(
                    DetectionCandidate(
                        class_id=dot.class_id,
                        class_name=dot.class_name,
                        confidence=dot.confidence,
                        bbox_xyxy=dot.bbox_xyxy,
                        source="cv_open_note_dot",
                    )
                )
                break
    return dots


def closest_staff(y: float, staff_systems: list[StaffSystem]) -> StaffSystem | None:
    """Return the nearest staff system whose vertical range can contain y."""
    compatible = [staff for staff in staff_systems if staff.contains_y(y)]
    if not compatible:
        return None
    return min(compatible, key=lambda staff: abs(y - (staff.top_y + staff.bottom_y) / 2.0))


def _nearest_offset_with_parity(raw_offset: float, *, odd: bool) -> int:
    base = int(round(raw_offset))
    target_remainder = 1 if odd else 0
    if base % 2 == target_remainder:
        return base
    candidates = [base - 1, base + 1]
    return min(candidates, key=lambda value: (abs(raw_offset - value), abs(value)))


def _staff_position_offset(y: float, staff: StaffSystem, class_name: str | None = None) -> int:
    half_spacing = staff.spacing / 2.0
    raw_offset = (staff.bottom_y - y) / half_spacing
    lowered = (class_name or "").lower()
    if "notehead" in lowered and "inspace" in lowered:
        return _nearest_offset_with_parity(raw_offset, odd=True)
    if "notehead" in lowered and "online" in lowered:
        return _nearest_offset_with_parity(raw_offset, odd=False)
    return int(round(raw_offset))


def pitch_from_y(y: float, staff: StaffSystem, class_name: str | None = None) -> tuple[str, int, int]:
    """Map a notehead y coordinate to treble-clef pitch."""
    diatonic_offset = _staff_position_offset(y, staff, class_name)
    diatonic = TREBLE_BOTTOM_LINE_DIATONIC + diatonic_offset
    step = STEP_NAMES[diatonic % 7]
    octave = diatonic // 7
    midi_pitch = 12 * (octave + 1) + STEP_TO_SEMITONE[step]
    return step, octave, midi_pitch


def is_notehead(class_name: str) -> bool:
    return "notehead" in class_name.lower()


def is_open_notehead(class_name: str) -> bool:
    lowered = class_name.lower()
    return "notehead" in lowered and (
        "half" in lowered or "whole" in lowered or "doublewhole" in lowered
    )


def is_rest(class_name: str) -> bool:
    return class_name.lower().startswith("rest")


def is_slur(class_name: str) -> bool:
    return class_name.lower() == "slur"


def is_tie(class_name: str) -> bool:
    return class_name.lower() == "tie"


def is_curve_notation(class_name: str) -> bool:
    return is_slur(class_name) or is_tie(class_name)


def is_beam(class_name: str) -> bool:
    return class_name.lower() == "beam"


def is_stem(class_name: str) -> bool:
    return class_name.lower() == "stem"


def is_flag(class_name: str) -> bool:
    return class_name.lower().startswith("flag")


def is_augmentation_dot(class_name: str) -> bool:
    return class_name.lower() == "augmentationdot"


def is_key_signature_symbol(class_name: str) -> bool:
    return class_name.lower() in {"keyflat", "keysharp", "keynatural"}


def is_explicit_accidental(class_name: str) -> bool:
    lowered = class_name.lower()
    return lowered.startswith("accidental") and not lowered.endswith("small")


def is_pitch_modifier(class_name: str) -> bool:
    return is_key_signature_symbol(class_name) or is_explicit_accidental(class_name)


def is_thin_symbol_candidate(class_name: str) -> bool:
    """Return whether a tiled model candidate should augment full-page extraction."""
    return (
        is_beam(class_name)
        or is_stem(class_name)
        or is_flag(class_name)
        or is_augmentation_dot(class_name)
        or is_pitch_modifier(class_name)
        or is_rest(class_name)
        or is_curve_notation(class_name)
    )


def _thin_symbol_min_confidence(class_name: str) -> float:
    """Use stricter thresholds for symbols where false positives damage rhythm."""
    if is_stem(class_name):
        return 0.03
    if is_beam(class_name) or is_flag(class_name):
        return 0.05
    if is_augmentation_dot(class_name):
        return 0.22
    if is_pitch_modifier(class_name):
        return 0.08
    if is_rest(class_name):
        return 0.10
    if is_curve_notation(class_name):
        return 0.08
    return 0.10


def _symbol_family(class_name: str) -> str:
    lowered = class_name.lower()
    if is_stem(class_name):
        return "stem"
    if is_beam(class_name):
        return "beam"
    if is_flag(class_name):
        return lowered
    if is_augmentation_dot(class_name):
        return "augmentationdot"
    if is_key_signature_symbol(class_name):
        return lowered
    if is_explicit_accidental(class_name):
        return lowered
    if is_rest(class_name):
        return "rest"
    if is_curve_notation(class_name):
        return lowered
    return lowered


def _deduplicate_symbol_candidates(
    candidates: list[DetectionCandidate],
    *,
    spacing: float,
) -> list[DetectionCandidate]:
    """Deduplicate overlapping full-page and tiled symbols without mixing classes."""
    ordered = sorted(candidates, key=lambda item: item.confidence, reverse=True)
    kept: list[DetectionCandidate] = []
    for candidate in ordered:
        family = _symbol_family(candidate.class_name)
        duplicate = False
        for existing in kept:
            if _symbol_family(existing.class_name) != family:
                continue
            center_close = (
                abs(candidate.x_center - existing.x_center) <= spacing * 0.75
                and abs(candidate.y_center - existing.y_center) <= spacing * 0.75
            )
            if center_close or _bbox_iou(candidate.bbox_xyxy, existing.bbox_xyxy) > 0.35:
                duplicate = True
                break
        if not duplicate:
            kept.append(candidate)
    return sorted(kept, key=lambda item: (item.y_center, item.x_center, _symbol_family(item.class_name)))


def alter_for_pitch_modifier(class_name: str) -> int | None:
    lowered = class_name.lower()
    if "doubleflat" in lowered:
        return -2
    if "doublesharp" in lowered:
        return 2
    if "flat" in lowered:
        return -1
    if "sharp" in lowered:
        return 1
    if "natural" in lowered:
        return 0
    return None


def pitch_modifier_anchor_y(symbol: DetectionCandidate) -> float:
    """Return the staff-position anchor for an accidental/key-signature glyph."""
    _, y1, _, y2 = symbol.bbox_xyxy
    if "flat" in symbol.class_name.lower():
        return symbol.y_center + (y2 - y1) * 0.25
    return symbol.y_center


def quarter_length_for_class(class_name: str, default_quarter_length: float = 1.0) -> float:
    """Estimate base duration from notehead class before beams/flags/dots."""
    lowered = class_name.lower()
    if "doublewhole" in lowered:
        return 8.0
    if "whole" in lowered:
        return 4.0
    if "half" in lowered:
        return 2.0
    return default_quarter_length


def quarter_length_for_rest_class(class_name: str, default_quarter_length: float = 1.0) -> float:
    """Estimate rest duration from a detector class name."""
    lowered = class_name.lower()
    if "128th" in lowered:
        return 1.0 / 32.0
    if "64th" in lowered:
        return 1.0 / 16.0
    if "32nd" in lowered:
        return 1.0 / 8.0
    if "16th" in lowered:
        return 0.25
    if "8th" in lowered:
        return 0.5
    if "quarter" in lowered:
        return 1.0
    if "half" in lowered:
        return 2.0
    if "doublewhole" in lowered:
        return 8.0
    if "whole" in lowered:
        return 4.0
    return default_quarter_length


def _flag_quarter_length(class_name: str) -> float | None:
    lowered = class_name.lower()
    if "128th" in lowered:
        return 1.0 / 32.0
    if "64th" in lowered:
        return 1.0 / 16.0
    if "32nd" in lowered:
        return 1.0 / 8.0
    if "16th" in lowered:
        return 0.25
    if "8th" in lowered:
        return 0.5
    return None


def _symbol_staff_compatible(symbol: DetectionCandidate, staff: StaffSystem) -> bool:
    return staff.contains_y(symbol.y_center, ledger_margin_steps=9.0)


def _related_symbols_for_note(
    note: DetectionCandidate,
    relationships: list[CandidateRelationship] | None,
    *,
    relationship_type: str,
    symbol_predicate: Callable[[str], bool],
) -> list[DetectionCandidate]:
    if not relationships:
        return []
    related: list[DetectionCandidate] = []
    for relationship in relationships:
        if relationship.relationship_type != relationship_type:
            continue
        if relationship.source == note and symbol_predicate(relationship.target.class_name):
            related.append(relationship.target)
        elif relationship.target == note and symbol_predicate(relationship.source.class_name):
            related.append(relationship.source)
    return related


def _has_stem_relationship_for_note(
    note: DetectionCandidate,
    relationships: list[CandidateRelationship] | None,
) -> bool:
    return bool(
        _related_symbols_for_note(
            note,
            relationships,
            relationship_type="stem_notehead",
            symbol_predicate=is_stem,
        )
    )


def _beam_relationship_count_for_note(
    note: DetectionCandidate,
    relationships: list[CandidateRelationship] | None,
    staff: StaffSystem | None = None,
    rhythm_symbols: list[DetectionCandidate] | None = None,
) -> int:
    related = _related_symbols_for_note(
        note,
        relationships,
        relationship_type="beam_notegroup",
        symbol_predicate=is_beam,
    )
    if not related:
        return 0
    if staff is None:
        return _count_unique_beam_lanes(related, spacing=10.0)
    geometry_compatible_count = _beam_count_from_symbols(
        note,
        staff,
        related,
        rhythm_symbols=list(rhythm_symbols or []),
        relationships=relationships,
    )
    return geometry_compatible_count or _count_unique_beam_lanes(related, spacing=staff.spacing)


def _count_unique_beam_lanes(symbols: list[DetectionCandidate], *, spacing: float) -> int:
    """Count visually separate beam lanes while collapsing duplicate tiled boxes."""
    if not symbols:
        return 0
    centers = sorted(symbol.y_center for symbol in symbols)
    threshold = max(2.0, spacing * 0.28)
    lane_count = 0
    previous: float | None = None
    for center in centers:
        if previous is None or abs(center - previous) > threshold:
            lane_count += 1
            previous = center
            continue
        previous = (previous + center) / 2.0
    return lane_count


def _attached_stems_for_note(
    note: DetectionCandidate,
    staff: StaffSystem,
    rhythm_symbols: list[DetectionCandidate],
    relationships: list[CandidateRelationship] | None = None,
) -> list[DetectionCandidate]:
    """Return detected stems that plausibly attach to a notehead."""
    nx1, ny1, nx2, ny2 = note.bbox_xyxy
    note_side_x = (nx1, nx2)
    candidates: list[DetectionCandidate] = []
    candidates.extend(
        symbol
        for symbol in _related_symbols_for_note(
            note,
            relationships,
            relationship_type="stem_notehead",
            symbol_predicate=is_stem,
        )
        if _symbol_staff_compatible(symbol, staff)
    )
    for symbol in rhythm_symbols:
        if not is_stem(symbol.class_name) or not _symbol_staff_compatible(symbol, staff):
            continue
        sx1, sy1, sx2, sy2 = symbol.bbox_xyxy
        stem_height = sy2 - sy1
        stem_width = sx2 - sx1
        if stem_height < staff.spacing * 2.0 or stem_width > staff.spacing * 1.5:
            continue
        x_distance = min(abs(symbol.x_center - side_x) for side_x in note_side_x)
        y_overlaps_note = sy1 <= ny2 + staff.spacing * 0.75 and sy2 >= ny1 - staff.spacing * 0.75
        near_note_vertical = min(abs(sy1 - note.y_center), abs(sy2 - note.y_center)) <= staff.spacing * 7.0
        if x_distance <= staff.spacing * 1.2 and (y_overlaps_note or near_note_vertical):
            candidates.append(symbol)

    unique: list[DetectionCandidate] = []
    seen: set[tuple[float, float, float, float]] = set()
    for candidate in sorted(
        candidates,
        key=lambda item: (
            min(abs(item.x_center - side_x) for side_x in note_side_x),
            -item.confidence,
        ),
    ):
        key = tuple(round(value, 1) for value in candidate.bbox_xyxy)
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def _beam_count_from_symbols(
    note: DetectionCandidate,
    staff: StaffSystem,
    beam_symbols: list[DetectionCandidate],
    *,
    rhythm_symbols: list[DetectionCandidate],
    relationships: list[CandidateRelationship] | None = None,
) -> int:
    stems = _attached_stems_for_note(note, staff, rhythm_symbols, relationships)
    stem = stems[0] if stems else None
    probe_x = stem.x_center if stem is not None else note.x_center
    x_margin = staff.spacing * (0.45 if stem is not None else 0.75)
    compatible: list[DetectionCandidate] = []
    for symbol in beam_symbols:
        if not is_beam(symbol.class_name) or not _symbol_staff_compatible(symbol, staff):
            continue
        x1, y1, x2, y2 = symbol.bbox_xyxy
        if not (x1 - x_margin <= probe_x <= x2 + x_margin):
            continue
        if stem is not None:
            _, sy1, _, sy2 = stem.bbox_xyxy
            beam_near_stem = sy1 - staff.spacing * 1.5 <= symbol.y_center <= sy2 + staff.spacing * 1.5
            if not beam_near_stem:
                continue
        else:
            y_distance = min(abs(note.y_center - y1), abs(note.y_center - y2), abs(note.y_center - symbol.y_center))
            if y_distance > staff.spacing * 7.0:
                continue
        compatible.append(symbol)
    return _count_unique_beam_lanes(compatible, spacing=staff.spacing)


def _beam_count_for_note(
    note: DetectionCandidate,
    staff: StaffSystem,
    rhythm_symbols: list[DetectionCandidate],
) -> int:
    return _beam_count_from_symbols(
        note,
        staff,
        [symbol for symbol in rhythm_symbols if is_beam(symbol.class_name)],
        rhythm_symbols=rhythm_symbols,
    )


def _has_stem_for_note(
    note: DetectionCandidate,
    staff: StaffSystem,
    rhythm_symbols: list[DetectionCandidate],
    relationships: list[CandidateRelationship] | None = None,
) -> bool:
    """Return whether a detected stem is geometrically attached to a notehead."""
    if _has_stem_relationship_for_note(note, relationships):
        return True
    return bool(_attached_stems_for_note(note, staff, rhythm_symbols, relationships))


def _flag_duration_for_note(
    note: DetectionCandidate,
    staff: StaffSystem,
    rhythm_symbols: list[DetectionCandidate],
) -> float | None:
    durations: list[float] = []
    for symbol in rhythm_symbols:
        if not is_flag(symbol.class_name) or not _symbol_staff_compatible(symbol, staff):
            continue
        duration = _flag_quarter_length(symbol.class_name)
        if duration is None:
            continue
        x_distance = abs(symbol.x_center - note.x_center)
        y_distance = abs(symbol.y_center - note.y_center)
        if x_distance <= staff.spacing * 3.5 and y_distance <= staff.spacing * 8.0:
            durations.append(duration)
    return min(durations) if durations else None


def _has_augmentation_dot(
    note: DetectionCandidate,
    staff: StaffSystem,
    rhythm_symbols: list[DetectionCandidate],
) -> bool:
    best_distance: float | None = None
    for symbol in rhythm_symbols:
        if not is_augmentation_dot(symbol.class_name) or not _symbol_staff_compatible(symbol, staff):
            continue
        if not _dot_candidate_attaches_to_note(note, symbol, staff):
            continue
        _, _, x2, _ = note.bbox_xyxy
        distance = (symbol.x_center - x2) + abs(symbol.y_center - note.y_center)
        if best_distance is None or distance < best_distance:
            best_distance = distance
    return best_distance is not None


def rhythm_for_note(
    note: DetectionCandidate,
    staff: StaffSystem,
    rhythm_symbols: list[DetectionCandidate],
    *,
    default_quarter_length: float = 1.0,
    rhythm_relationships: list[CandidateRelationship] | None = None,
) -> tuple[float, bool, str, bool]:
    """Infer note duration from class plus nearby beams, flags, and dots."""
    duration = quarter_length_for_class(note.class_name, default_quarter_length)
    source = "notehead_class" if duration != default_quarter_length else "black_notehead_quarter_rule"
    stem_from_relationship = _has_stem_relationship_for_note(note, rhythm_relationships)
    stem_detected = stem_from_relationship or _has_stem_for_note(note, staff, rhythm_symbols)

    if "black" in note.class_name.lower() or note.source == "cv_fallback":
        flag_duration = _flag_duration_for_note(note, staff, rhythm_symbols)
        geometry_beam_count = _beam_count_for_note(note, staff, rhythm_symbols)
        relationship_beam_count = _beam_relationship_count_for_note(
            note,
            rhythm_relationships,
            staff=staff,
            rhythm_symbols=rhythm_symbols,
        )
        beam_count = geometry_beam_count if geometry_beam_count > 0 else relationship_beam_count
        if flag_duration is not None:
            duration = flag_duration
            source = "flag"
        elif beam_count > 0:
            duration = max(1.0 / 32.0, 1.0 / (2**beam_count))
            source = f"gnn_beam_x{beam_count}" if geometry_beam_count == 0 else f"beam_x{beam_count}"
        elif stem_detected:
            duration = default_quarter_length
            source = "gnn_stem_quarter" if stem_from_relationship else "stem_quarter"
        else:
            duration = default_quarter_length
            source = "black_notehead_quarter_rule_no_stem"

    dotted = _has_augmentation_dot(note, staff, rhythm_symbols)
    if dotted:
        duration *= 1.5
        source = f"{source}+augmentation_dot"
    return duration, dotted, source, stem_detected


def key_signatures_from_symbols(
    pitch_symbols: list[DetectionCandidate],
    staff_systems: list[StaffSystem],
    note_candidates: list[DetectionCandidate],
) -> dict[int, dict[str, int]]:
    """Infer per-staff key signatures from detected keyFlat/keySharp/keyNatural symbols."""
    first_note_x_by_staff: dict[int, float] = {}
    for candidate in note_candidates:
        staff = closest_staff(candidate.y_center, staff_systems)
        if staff is None:
            continue
        current = first_note_x_by_staff.get(staff.index)
        if current is None or candidate.x_center < current:
            first_note_x_by_staff[staff.index] = candidate.x_center

    key_signatures: dict[int, dict[str, int]] = {}
    best_by_staff_step: dict[tuple[int, str], tuple[float, int]] = {}
    for symbol in pitch_symbols:
        if not is_key_signature_symbol(symbol.class_name):
            continue
        alter = alter_for_pitch_modifier(symbol.class_name)
        if alter is None:
            continue
        symbol_pitch_y = pitch_modifier_anchor_y(symbol)
        staff = closest_staff(symbol_pitch_y, staff_systems)
        if staff is None or not _symbol_staff_compatible(symbol, staff):
            continue

        first_note_x = first_note_x_by_staff.get(staff.index)
        left_region_end = staff.start_x + staff.spacing * 24.0
        if first_note_x is not None:
            left_region_end = max(left_region_end, first_note_x - staff.spacing * 1.2)
        if symbol.x_center < staff.start_x - staff.spacing or symbol.x_center > left_region_end:
            continue

        step, _, _ = pitch_from_y(symbol_pitch_y, staff)
        key = (staff.index, step)
        existing = best_by_staff_step.get(key)
        if existing is None or symbol.confidence > existing[0]:
            best_by_staff_step[key] = (symbol.confidence, alter)

    for (staff_index, step), (_, alter) in best_by_staff_step.items():
        key_signatures.setdefault(staff_index, {})[step] = alter
    return key_signatures


def explicit_accidental_for_note(
    note: DetectionCandidate,
    staff: StaffSystem,
    pitch_symbols: list[DetectionCandidate],
    note_step: str,
) -> tuple[int, str] | None:
    """Return the nearest explicit accidental attached to a notehead, if any."""
    note_x1, _, _, _ = note.bbox_xyxy
    best: tuple[float, int, str] | None = None
    for symbol in pitch_symbols:
        if not is_explicit_accidental(symbol.class_name) or not _symbol_staff_compatible(symbol, staff):
            continue
        alter = alter_for_pitch_modifier(symbol.class_name)
        if alter is None:
            continue
        symbol_step, _, _ = pitch_from_y(pitch_modifier_anchor_y(symbol), staff)
        if symbol_step != note_step:
            continue
        _, _, symbol_x2, _ = symbol.bbox_xyxy
        x_distance = note_x1 - symbol_x2
        y_distance = abs(note.y_center - pitch_modifier_anchor_y(symbol))
        if not (0.0 <= x_distance <= staff.spacing * 4.0 and y_distance <= staff.spacing * 2.5):
            continue
        score = x_distance + y_distance * 0.5 - symbol.confidence
        if best is None or score < best[0]:
            best = (score, alter, symbol.class_name)
    if best is None:
        return None
    return best[1], f"explicit_accidental:{best[2]}"


def key_fifths_from_signature(signature: dict[str, int]) -> int:
    """Convert a simple standard key-signature map to MusicXML fifths."""
    altered = {step: alter for step, alter in signature.items() if alter != 0}
    if not altered:
        return 0
    if all(alter == -1 for alter in altered.values()):
        steps = set(altered)
        for count in range(1, len(FLAT_KEY_ORDER) + 1):
            if steps == set(FLAT_KEY_ORDER[:count]):
                return -count
    if all(alter == 1 for alter in altered.values()):
        steps = set(altered)
        for count in range(1, len(SHARP_KEY_ORDER) + 1):
            if steps == set(SHARP_KEY_ORDER[:count]):
                return count
    return 0


def document_key_fifths(key_signatures: dict[int, dict[str, int]]) -> int:
    """Return the most common MusicXML fifths value across detected staff signatures."""
    counts: dict[int, int] = {}
    for signature in key_signatures.values():
        fifths = key_fifths_from_signature(signature)
        counts[fifths] = counts.get(fifths, 0) + 1
    if not counts:
        return 0
    return max(counts.items(), key=lambda item: (item[1], -abs(item[0])))[0]


def _note_from_candidate(
    candidate: DetectionCandidate,
    staff: StaffSystem,
    *,
    rhythm_symbols: list[DetectionCandidate],
    rhythm_relationships: list[CandidateRelationship],
    pitch_symbols: list[DetectionCandidate],
    key_signatures: dict[int, dict[str, int]],
    default_quarter_length: float,
) -> ExtractedNote:
    step, octave, midi_pitch = pitch_from_y(candidate.y_center, staff, candidate.class_name)
    alter = 0
    pitch_source = "staff_geometry"
    explicit_accidental = explicit_accidental_for_note(candidate, staff, pitch_symbols, step)
    if explicit_accidental is not None:
        alter, pitch_source = explicit_accidental
    else:
        staff_signature = key_signatures.get(staff.index, {})
        if step in staff_signature:
            alter = int(staff_signature[step])
            pitch_source = f"key_signature:{'flat' if alter < 0 else 'sharp' if alter > 0 else 'natural'}"
    midi_pitch += alter
    quarter_length, dotted, rhythm_source, stem_detected = rhythm_for_note(
        candidate,
        staff,
        rhythm_symbols,
        default_quarter_length=default_quarter_length,
        rhythm_relationships=rhythm_relationships,
    )
    return ExtractedNote(
        event_type="note",
        order=0,
        staff_index=staff.index,
        x_center=float(candidate.x_center),
        y_center=float(candidate.y_center),
        bbox_xyxy=tuple(float(value) for value in candidate.bbox_xyxy),  # type: ignore[arg-type]
        class_name=candidate.class_name,
        confidence=float(candidate.confidence),
        source=candidate.source,
        step=step,
        octave=int(octave),
        midi_pitch=int(midi_pitch),
        alter=int(alter),
        quarter_length=quarter_length,
        onset_quarter=0.0,
        pitch_source=pitch_source,
        dotted=dotted,
        rhythm_source=rhythm_source,
        stem_detected=stem_detected,
    )


def _rest_from_candidate(
    candidate: DetectionCandidate,
    staff: StaffSystem,
    *,
    default_quarter_length: float,
) -> ExtractedRest:
    quarter_length = quarter_length_for_rest_class(candidate.class_name, default_quarter_length)
    return ExtractedRest(
        event_type="rest",
        order=0,
        staff_index=staff.index,
        x_center=float(candidate.x_center),
        y_center=float(candidate.y_center),
        bbox_xyxy=tuple(float(value) for value in candidate.bbox_xyxy),  # type: ignore[arg-type]
        class_name=candidate.class_name,
        confidence=float(candidate.confidence),
        source=candidate.source,
        quarter_length=quarter_length,
        onset_quarter=0.0,
        dotted=False,
        rhythm_source="rest_class",
    )


def _staff_by_candidate(
    candidate: DetectionCandidate,
    staff_systems: list[StaffSystem],
) -> StaffSystem | None:
    return closest_staff(candidate.y_center, staff_systems)


def _is_small_notehead_candidate(
    candidate: DetectionCandidate,
    median_area_by_staff: dict[int, float],
    staff: StaffSystem,
) -> bool:
    lowered = candidate.class_name.lower()
    if "small" in lowered or lowered.startswith("gracenote"):
        return True
    median_area = median_area_by_staff.get(staff.index)
    if not median_area:
        return False
    area = max(0.0, candidate.width) * max(0.0, candidate.height)
    return area < median_area * 0.58 and (
        candidate.width < staff.spacing * 0.92 or candidate.height < staff.spacing * 0.85
    )


def _is_annotation_notehead_candidate(
    candidate: DetectionCandidate,
    staff: StaffSystem,
    first_regular_x_by_staff: dict[int, float],
) -> bool:
    first_regular_x = first_regular_x_by_staff.get(staff.index)
    if first_regular_x is None:
        return False
    far_above_staff = candidate.y_center < staff.top_y - staff.spacing * 1.75
    before_first_staff_note = candidate.x_center < first_regular_x - staff.spacing * 1.4
    return far_above_staff and before_first_staff_note


def _filter_normal_notehead_candidates(
    candidates: list[DetectionCandidate],
    staff_systems: list[StaffSystem],
) -> list[DetectionCandidate]:
    """Remove notehead-like annotations and small cue/grace notes from normal rhythm."""
    by_staff: dict[int, list[DetectionCandidate]] = {}
    for candidate in candidates:
        staff = _staff_by_candidate(candidate, staff_systems)
        if staff is None:
            continue
        by_staff.setdefault(staff.index, []).append(candidate)

    first_regular_x_by_staff: dict[int, float] = {}
    median_area_by_staff: dict[int, float] = {}
    staff_by_index = {staff.index: staff for staff in staff_systems}
    for staff_index, staff_candidates in by_staff.items():
        staff = staff_by_index[staff_index]
        regular_vertical = [
            candidate
            for candidate in staff_candidates
            if staff.top_y - staff.spacing * 1.5 <= candidate.y_center <= staff.bottom_y + staff.spacing * 1.5
        ]
        if regular_vertical:
            first_regular_x_by_staff[staff_index] = min(candidate.x_center for candidate in regular_vertical)
        areas = [
            max(0.0, candidate.width) * max(0.0, candidate.height)
            for candidate in regular_vertical or staff_candidates
        ]
        if areas:
            median_area_by_staff[staff_index] = float(np.median(areas))

    filtered: list[DetectionCandidate] = []
    for candidate in candidates:
        staff = _staff_by_candidate(candidate, staff_systems)
        if staff is None:
            continue
        if _is_annotation_notehead_candidate(candidate, staff, first_regular_x_by_staff):
            continue
        if _is_small_notehead_candidate(candidate, median_area_by_staff, staff):
            continue
        filtered.append(candidate)
    return filtered


def _nearest_note_for_curve_endpoint(
    notes: list[ExtractedNote],
    *,
    staff: StaffSystem,
    x: float,
    y: float,
    prefer_left: bool,
) -> ExtractedNote | None:
    same_staff = [note for note in notes if note.staff_index == staff.index]
    if not same_staff:
        return None
    if prefer_left:
        directional = [note for note in same_staff if note.x_center <= x + staff.spacing * 3.0]
    else:
        directional = [note for note in same_staff if note.x_center >= x - staff.spacing * 3.0]
    candidates = directional or same_staff
    return min(
        candidates,
        key=lambda note: abs(note.x_center - x) + abs(note.y_center - y) * 0.15,
    )


def _attach_curve_notations(
    events: list[ExtractedMusicEvent],
    notation_symbols: list[DetectionCandidate],
    staff_systems: list[StaffSystem],
) -> list[ExtractedMusicEvent]:
    """Attach detected slur/tie boxes to nearby note endpoints."""
    notes = [event for event in events if isinstance(event, ExtractedNote)]
    if not notes or not notation_symbols:
        return events

    slur_starts: dict[int, list[int]] = {}
    slur_stops: dict[int, list[int]] = {}
    tie_starts: dict[int, list[int]] = {}
    tie_stops: dict[int, list[int]] = {}
    next_slur_id = 1
    next_tie_id = 1

    for symbol in sorted(notation_symbols, key=lambda item: (item.y_center, item.x_center, -item.confidence)):
        if not is_curve_notation(symbol.class_name):
            continue
        staff = closest_staff(symbol.y_center, staff_systems)
        if staff is None:
            continue
        x1, y1, x2, y2 = symbol.bbox_xyxy
        start_note = _nearest_note_for_curve_endpoint(
            notes,
            staff=staff,
            x=x1,
            y=(y1 + y2) / 2.0,
            prefer_left=True,
        )
        stop_note = _nearest_note_for_curve_endpoint(
            notes,
            staff=staff,
            x=x2,
            y=(y1 + y2) / 2.0,
            prefer_left=False,
        )
        if start_note is None or stop_note is None or start_note.order == stop_note.order:
            continue
        if abs(stop_note.x_center - start_note.x_center) < staff.spacing * 1.2:
            continue

        if is_tie(symbol.class_name):
            tie_id = next_tie_id
            next_tie_id += 1
            tie_starts.setdefault(start_note.order, []).append(tie_id)
            tie_stops.setdefault(stop_note.order, []).append(tie_id)
        else:
            slur_id = next_slur_id
            next_slur_id += 1
            slur_starts.setdefault(start_note.order, []).append(slur_id)
            slur_stops.setdefault(stop_note.order, []).append(slur_id)

    attached: list[ExtractedMusicEvent] = []
    for event in events:
        if not isinstance(event, ExtractedNote):
            attached.append(event)
            continue
        attached.append(
            replace(
                event,
                slur_starts=tuple(slur_starts.get(event.order, ())),
                slur_stops=tuple(slur_stops.get(event.order, ())),
                tie_starts=tuple(tie_starts.get(event.order, ())),
                tie_stops=tuple(tie_stops.get(event.order, ())),
            )
        )
    return attached


def _order_events(
    events: list[ExtractedMusicEvent],
    staff_systems: list[StaffSystem],
) -> list[ExtractedMusicEvent]:
    events.sort(key=lambda event: (event.staff_index, event.x_center, event.y_center))
    ordered: list[ExtractedMusicEvent] = []
    onset = 0.0
    previous_staff = None
    group_x: float | None = None
    group_duration = 0.0
    group_threshold_by_staff = {staff.index: staff.spacing * 1.15 for staff in staff_systems}
    for event in events:
        if previous_staff is None or event.staff_index != previous_staff:
            if previous_staff is not None:
                onset += group_duration
            group_x = None
            group_duration = 0.0
        elif group_x is None or abs(event.x_center - group_x) > group_threshold_by_staff[event.staff_index]:
            onset += group_duration
            group_x = None
            group_duration = 0.0

        if group_x is None:
            group_x = event.x_center
        ordered.append(replace(event, order=len(ordered) + 1, onset_quarter=onset))
        previous_staff = event.staff_index
        group_duration = max(group_duration, event.quarter_length)
    return ordered


def events_from_candidates(
    note_candidates: list[DetectionCandidate],
    staff_systems: list[StaffSystem],
    *,
    rest_candidates: list[DetectionCandidate] | None = None,
    notation_symbols: list[DetectionCandidate] | None = None,
    rhythm_symbols: list[DetectionCandidate] | None = None,
    rhythm_relationships: list[CandidateRelationship] | None = None,
    pitch_symbols: list[DetectionCandidate] | None = None,
    key_signatures: dict[int, dict[str, int]] | None = None,
    default_quarter_length: float = 1.0,
) -> list[ExtractedMusicEvent]:
    """Convert notehead and rest boxes into ordered musical events."""
    if not staff_systems:
        return []
    spacing = float(np.median([staff.spacing for staff in staff_systems]))
    note_candidates = _deduplicate_candidates(note_candidates, spacing=spacing)
    note_candidates = _filter_normal_notehead_candidates(note_candidates, staff_systems)
    rest_candidates = _deduplicate_symbol_candidates(list(rest_candidates or []), spacing=spacing)
    notation_symbols = _deduplicate_symbol_candidates(list(notation_symbols or []), spacing=spacing)
    rhythm_symbols = list(rhythm_symbols or [])
    rhythm_relationships = list(rhythm_relationships or [])
    pitch_symbols = list(pitch_symbols or [])
    key_signatures = dict(key_signatures or {})

    events: list[ExtractedMusicEvent] = []
    for candidate in note_candidates:
        staff = closest_staff(candidate.y_center, staff_systems)
        if staff is None:
            continue
        events.append(
            _note_from_candidate(
                candidate,
                staff,
                rhythm_symbols=rhythm_symbols,
                rhythm_relationships=rhythm_relationships,
                pitch_symbols=pitch_symbols,
                key_signatures=key_signatures,
                default_quarter_length=default_quarter_length,
            )
        )
    for candidate in rest_candidates:
        staff = closest_staff(candidate.y_center, staff_systems)
        if staff is None:
            continue
        events.append(
            _rest_from_candidate(
                candidate,
                staff,
                default_quarter_length=default_quarter_length,
            )
        )
    ordered = _order_events(events, staff_systems)
    return _attach_curve_notations(ordered, notation_symbols, staff_systems)


def notes_from_candidates(
    candidates: list[DetectionCandidate],
    staff_systems: list[StaffSystem],
    *,
    rhythm_symbols: list[DetectionCandidate] | None = None,
    rhythm_relationships: list[CandidateRelationship] | None = None,
    pitch_symbols: list[DetectionCandidate] | None = None,
    key_signatures: dict[int, dict[str, int]] | None = None,
    default_quarter_length: float = 1.0,
) -> list[ExtractedNote]:
    """Convert notehead boxes into ordered treble-clef note events."""
    return [
        event
        for event in events_from_candidates(
            candidates,
            staff_systems,
            notation_symbols=None,
            rhythm_symbols=rhythm_symbols,
            rhythm_relationships=rhythm_relationships,
            pitch_symbols=pitch_symbols,
            key_signatures=key_signatures,
            default_quarter_length=default_quarter_length,
        )
        if isinstance(event, ExtractedNote)
    ]


def _var_len(value: int) -> bytes:
    buffer = value & 0x7F
    value >>= 7
    while value:
        buffer <<= 8
        buffer |= ((value & 0x7F) | 0x80)
        value >>= 7
    output = bytearray()
    while True:
        output.append(buffer & 0xFF)
        if buffer & 0x80:
            buffer >>= 8
            continue
        break
    return bytes(output)


def write_midi(
    events: list[ExtractedMusicEvent],
    output_path: str | Path,
    *,
    tempo_bpm: int = 96,
    ticks_per_quarter: int = 480,
    velocity: int = 76,
    program: int = 40,
) -> None:
    """Write a simple Standard MIDI File with real note events."""
    midi_events: list[tuple[int, int, int, int]] = []
    for note in [event for event in events if isinstance(event, ExtractedNote)]:
        start = int(round(note.onset_quarter * ticks_per_quarter))
        duration = max(1, int(round(note.quarter_length * ticks_per_quarter)))
        midi_events.append((start, 0, note.midi_pitch, velocity))
        midi_events.append((start + duration, 1, note.midi_pitch, 0))
    midi_events.sort(key=lambda item: (item[0], 0 if item[1] == 1 else 1))

    mpqn = int(round(60_000_000 / max(1, tempo_bpm)))
    track = bytearray()
    track.extend(b"\x00\xff\x51\x03" + mpqn.to_bytes(3, "big"))
    track.extend(b"\x00" + bytes([0xC0, max(0, min(program, 127))]))
    last_tick = 0
    for tick, event_type, pitch, value in midi_events:
        track.extend(_var_len(max(0, tick - last_tick)))
        status = 0x80 if event_type == 1 else 0x90
        track.extend(bytes([status, max(0, min(pitch, 127)), max(0, min(value, 127))]))
        last_tick = tick
    track.extend(b"\x00\xff\x2f\x00")

    header = b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big")
    header += (1).to_bytes(2, "big") + ticks_per_quarter.to_bytes(2, "big")
    body = b"MTrk" + len(track).to_bytes(4, "big") + bytes(track)
    Path(output_path).write_bytes(header + body)


def write_musicxml(
    events: list[ExtractedMusicEvent],
    output_path: str | Path,
    *,
    title: str,
    key_fifths: int = 0,
) -> None:
    """Write compact MusicXML from extracted note and rest events."""
    divisions = 480
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<score-partwise version="3.1">',
        "  <work>",
        f"    <work-title>{_xml_escape(title)}</work-title>",
        "  </work>",
        "  <part-list>",
        '    <score-part id="P1"><part-name>Extracted Notes</part-name></score-part>',
        "  </part-list>",
        '  <part id="P1">',
    ]
    elapsed = 0.0
    measure_number = 1
    parts.extend(_measure_start(measure_number, divisions, include_attributes=True, key_fifths=key_fifths))
    previous_staff_index: int | None = None
    for event in events:
        staff_changed = previous_staff_index is not None and event.staff_index != previous_staff_index
        if staff_changed or elapsed >= 4.0:
            parts.append("    </measure>")
            measure_number += 1
            elapsed = 0.0
            parts.extend(
                _measure_start(
                    measure_number,
                    divisions,
                    include_attributes=False,
                    new_system=staff_changed,
                )
            )
        duration = max(1, int(round(event.quarter_length * divisions)))
        note_type = _musicxml_type(event.quarter_length)
        parts.append("      <note>")
        if isinstance(event, ExtractedRest):
            parts.append("        <rest/>")
        else:
            parts.extend(
                [
                    "        <pitch>",
                    f"          <step>{event.step}</step>",
                ]
            )
            if event.alter:
                parts.append(f"          <alter>{event.alter}</alter>")
            parts.extend(
                [
                    f"          <octave>{event.octave}</octave>",
                    "        </pitch>",
                ]
            )
            for _ in event.tie_stops:
                parts.append('        <tie type="stop"/>')
            for _ in event.tie_starts:
                parts.append('        <tie type="start"/>')
        parts.extend(
            [
                f"        <duration>{duration}</duration>",
                f"        <type>{note_type}</type>",
            ]
        )
        if event.dotted:
            parts.append("        <dot/>")
        if isinstance(event, ExtractedNote):
            notation_lines: list[str] = []
            for tie_id in event.tie_stops:
                notation_lines.append(f'          <tied type="stop" number="{tie_id}"/>')
            for tie_id in event.tie_starts:
                notation_lines.append(f'          <tied type="start" number="{tie_id}"/>')
            for slur_id in event.slur_stops:
                notation_lines.append(f'          <slur type="stop" number="{slur_id}"/>')
            for slur_id in event.slur_starts:
                notation_lines.append(f'          <slur type="start" number="{slur_id}"/>')
            if notation_lines:
                parts.append("        <notations>")
                parts.extend(notation_lines)
                parts.append("        </notations>")
        parts.append("      </note>")
        elapsed += event.quarter_length
        previous_staff_index = event.staff_index
    parts.extend(["    </measure>", "  </part>", "</score-partwise>"])
    Path(output_path).write_text("\n".join(parts) + "\n", encoding="utf-8")


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _measure_start(
    number: int,
    divisions: int,
    *,
    include_attributes: bool,
    key_fifths: int = 0,
    new_system: bool = False,
) -> list[str]:
    lines = [f'    <measure number="{number}">']
    if new_system:
        lines.append('      <print new-system="yes"/>')
    if include_attributes:
        lines.extend(
            [
                "      <attributes>",
                f"        <divisions>{divisions}</divisions>",
                f"        <key><fifths>{key_fifths}</fifths></key>",
                "        <time><beats>4</beats><beat-type>4</beat-type></time>",
                "        <clef><sign>G</sign><line>2</line></clef>",
                "      </attributes>",
            ]
        )
    return lines


def _musicxml_type(quarter_length: float) -> str:
    base_length = quarter_length / 1.5 if _is_dotted_length(quarter_length) else quarter_length
    if base_length >= 8.0:
        return "breve"
    if base_length >= 4.0:
        return "whole"
    if base_length >= 2.0:
        return "half"
    if base_length >= 1.0:
        return "quarter"
    if base_length >= 0.5:
        return "eighth"
    return "16th"


def _is_dotted_length(quarter_length: float) -> bool:
    for base in (4.0, 2.0, 1.0, 0.5, 0.25, 0.125):
        if abs(quarter_length - base * 1.5) < 1e-6:
            return True
    return False


def write_overlay(
    image: np.ndarray,
    staff_systems: list[StaffSystem],
    events: list[ExtractedMusicEvent],
    output_path: str | Path,
) -> None:
    """Write an image overlay showing staff geometry and extracted notes."""
    canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    for staff in staff_systems:
        for y_value in staff.line_y:
            y = int(round(y_value))
            cv2.line(canvas, (int(staff.start_x), y), (int(staff.end_x), y), (0, 160, 0), 1)
    for event in events:
        x1, y1, x2, y2 = [int(round(value)) for value in event.bbox_xyxy]
        color = (0, 120, 255) if isinstance(event, ExtractedRest) else (0, 0, 255)
        if not event.source.startswith("yolo"):
            color = (255, 0, 0)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        dot_suffix = "." if event.dotted else ""
        if isinstance(event, ExtractedRest):
            label = f"{event.order}:R/{event.quarter_length:g}{dot_suffix}"
        else:
            alter_suffix = "b" * abs(event.alter) if event.alter < 0 else "#" * event.alter
            label = f"{event.order}:{event.step}{alter_suffix}{event.octave}/{event.quarter_length:g}{dot_suffix}"
        cv2.putText(
            canvas,
            label,
            (x1, max(0, y1 - 4)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            color,
            1,
            cv2.LINE_AA,
        )
    cv2.imwrite(str(output_path), canvas)


def detector_payload_from_candidates(
    candidates: list[DetectionCandidate],
    *,
    image_width: int,
    image_height: int,
    run_id: str,
    model_id: str,
    source_image_uri: str | None = None,
) -> tuple[Any, list[DetectionCandidate]]:
    """Build a V2 detector payload from extraction candidates for relationship assembly."""
    from melodious_v2.contracts import (
        DetectionV2,
        DetectorPayloadV2,
        ImageSize,
        NormalizedBBox,
        PixelBBox,
    )
    from melodious_v2.taxonomies import DEEPSCORES_136_CLASS_NAMES, SEMANTIC_OMR_V2_CLASS_MAP

    detections: list[DetectionV2] = []
    payload_candidates: list[DetectionCandidate] = []
    for candidate in candidates:
        if candidate.class_name not in DEEPSCORES_136_CLASS_NAMES:
            continue
        x1, y1, x2, y2 = candidate.bbox_xyxy
        x1 = max(0.0, min(float(image_width), x1))
        x2 = max(0.0, min(float(image_width), x2))
        y1 = max(0.0, min(float(image_height), y1))
        y2 = max(0.0, min(float(image_height), y2))
        if x2 <= x1 or y2 <= y1:
            continue
        class_id = DEEPSCORES_136_CLASS_NAMES.index(candidate.class_name)
        detections.append(
            DetectionV2(
                class_id=class_id,
                class_name=candidate.class_name,
                semantic_group=SEMANTIC_OMR_V2_CLASS_MAP[candidate.class_name],
                confidence=max(0.0, min(1.0, candidate.confidence)),
                bbox=NormalizedBBox(
                    x_center=((x1 + x2) / 2.0) / image_width,
                    y_center=((y1 + y2) / 2.0) / image_height,
                    width=(x2 - x1) / image_width,
                    height=(y2 - y1) / image_height,
                ),
                bbox_pixels=PixelBBox(x1=x1, y1=y1, x2=x2, y2=y2),
            )
        )
        payload_candidates.append(candidate)

    payload = DetectorPayloadV2(
        run_id=run_id,
        model_id=model_id,
        taxonomy_id="deepscores_136",
        image_size=ImageSize(width=image_width, height=image_height),
        detections=detections,
        source_image_uri=source_image_uri,
    )
    return payload, payload_candidates


def assemble_candidate_relationships(
    candidates: list[DetectionCandidate],
    *,
    image_width: int,
    image_height: int,
    image_path: str | Path,
    checkpoint_path: str | Path,
) -> tuple[dict[str, Any], list[CandidateRelationship], Any]:
    """Run assembly/GNN on extraction candidates and map output back to candidates."""
    from melodious_v2.assembly.service import assemble_payload

    payload, payload_candidates = detector_payload_from_candidates(
        candidates,
        image_width=image_width,
        image_height=image_height,
        run_id=f"{Path(image_path).stem}_note_extraction",
        model_id="local_note_extraction_candidates",
        source_image_uri=str(image_path),
    )
    mode, relationships = assemble_payload(payload, requested_mode="gnn", checkpoint_path=str(checkpoint_path))
    candidate_relationships: list[CandidateRelationship] = []
    for relationship in relationships:
        if not (0 <= relationship.source_idx < len(payload_candidates)):
            continue
        if not (0 <= relationship.target_idx < len(payload_candidates)):
            continue
        candidate_relationships.append(
            CandidateRelationship(
                source=payload_candidates[relationship.source_idx],
                target=payload_candidates[relationship.target_idx],
                relationship_type=relationship.relationship_type,
                confidence=relationship.confidence,
            )
        )
    return asdict(mode), candidate_relationships, payload


def candidate_relationships_to_dict(relationships: list[CandidateRelationship]) -> list[dict[str, Any]]:
    """Return JSON-friendly relationship records with candidate metadata."""
    records: list[dict[str, Any]] = []
    for relationship in relationships:
        records.append(
            {
                "relationship_type": relationship.relationship_type,
                "confidence": relationship.confidence,
                "source": {
                    "class_name": relationship.source.class_name,
                    "confidence": relationship.source.confidence,
                    "bbox_xyxy": relationship.source.bbox_xyxy,
                    "source": relationship.source.source,
                },
                "target": {
                    "class_name": relationship.target.class_name,
                    "confidence": relationship.target.confidence,
                    "bbox_xyxy": relationship.target.bbox_xyxy,
                    "source": relationship.target.source,
                },
            }
        )
    return records


def extract_notes_from_image(
    image_path: str | Path,
    *,
    output_dir: str | Path,
    checkpoint_path: str | Path | None = None,
    thin_symbol_checkpoint_path: str | Path | None = None,
    gnn_checkpoint_path: str | Path | None = None,
    snapshot_live_checkpoint: bool = True,
    confidence: float = 0.12,
    imgsz: int = 1472,
    max_det: int = 2000,
    thin_confidence: float = 0.05,
    thin_imgsz: int = 1024,
    thin_max_det: int = 1000,
    thin_tile_size: int = 384,
    thin_tile_stride: int = 256,
    use_tiled_dots: bool = False,
    device: str = "cpu",
    default_quarter_length: float = 1.0,
    use_cv_fallback: bool = True,
    use_cv_dot_fallback: bool | None = None,
    title: str | None = None,
) -> ExtractionResult:
    """Extract approximate notes and write JSON, overlay, MusicXML, and MIDI."""
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = image_path.stem
    notes_json = output_dir / f"{stem}_notes.json"
    midi_path = output_dir / f"{stem}_notes.mid"
    musicxml_path = output_dir / f"{stem}_notes.musicxml"
    overlay_path = output_dir / f"{stem}_notes_overlay.png"
    detector_payload_json = output_dir / f"{stem}_detector_payload.json"
    relationships_json = output_dir / f"{stem}_relationships.json"
    image = read_grayscale_image(image_path)
    height, width = image.shape[:2]
    staff_systems = detect_staff_systems(image)
    warnings: list[str] = []

    candidates: list[DetectionCandidate] = []
    rest_candidates: list[DetectionCandidate] = []
    rhythm_symbols: list[DetectionCandidate] = []
    pitch_symbols: list[DetectionCandidate] = []
    notation_symbols: list[DetectionCandidate] = []
    checkpoint_snapshot: Path | None = None
    thin_checkpoint_snapshot: Path | None = None
    extractor_mode = "cv_fallback"
    checkpoint_for_result: str | None = None
    thin_checkpoint_for_result: str | None = None
    if checkpoint_path is not None:
        try:
            checkpoint_source = Path(checkpoint_path)
            checkpoint_for_inference = checkpoint_source
            if snapshot_live_checkpoint:
                checkpoint_snapshot = snapshot_checkpoint(checkpoint_source, output_dir)
                checkpoint_for_inference = checkpoint_snapshot
            all_candidates = yolo_detection_candidates(
                image_path,
                checkpoint_for_inference,
                confidence=confidence,
                imgsz=imgsz,
                max_det=max_det,
                device=device,
            )
            candidates = [candidate for candidate in all_candidates if is_notehead(candidate.class_name)]
            rest_candidates = [candidate for candidate in all_candidates if is_rest(candidate.class_name)]
            notation_symbols = [candidate for candidate in all_candidates if is_curve_notation(candidate.class_name)]
            rhythm_symbols = [
                candidate
                for candidate in all_candidates
                if is_beam(candidate.class_name)
                or is_stem(candidate.class_name)
                or is_flag(candidate.class_name)
                or is_augmentation_dot(candidate.class_name)
            ]
            pitch_symbols = [candidate for candidate in all_candidates if is_pitch_modifier(candidate.class_name)]
            extractor_mode = "yolo_notehead_staff_pitch"
            checkpoint_for_result = str(checkpoint_source)
        except Exception as exc:  # pragma: no cover - runtime dependency path
            warnings.append(f"YOLO note extraction failed: {exc}")
            candidates = []

    if thin_symbol_checkpoint_path is not None:
        try:
            thin_checkpoint_source = Path(thin_symbol_checkpoint_path)
            thin_checkpoint_for_inference = thin_checkpoint_source
            if snapshot_live_checkpoint:
                thin_checkpoint_snapshot = snapshot_checkpoint(
                    thin_checkpoint_source,
                    output_dir,
                    label="thin_symbols",
                )
                thin_checkpoint_for_inference = thin_checkpoint_snapshot
            thin_candidates = yolo_tiled_detection_candidates(
                image_path,
                thin_checkpoint_for_inference,
                confidence=thin_confidence,
                imgsz=thin_imgsz,
                max_det=thin_max_det,
                device=device,
                tile_size=thin_tile_size,
                stride=thin_tile_stride,
            )
            thin_symbols = [
                candidate
                for candidate in thin_candidates
                if is_thin_symbol_candidate(candidate.class_name)
                and candidate.confidence >= _thin_symbol_min_confidence(candidate.class_name)
                and (use_tiled_dots or not is_augmentation_dot(candidate.class_name))
                and not is_key_signature_symbol(candidate.class_name)
            ]
            rest_candidates.extend(candidate for candidate in thin_symbols if is_rest(candidate.class_name))
            notation_symbols.extend(candidate for candidate in thin_symbols if is_curve_notation(candidate.class_name))
            rhythm_symbols.extend(
                candidate
                for candidate in thin_symbols
                if is_beam(candidate.class_name)
                or is_stem(candidate.class_name)
                or is_flag(candidate.class_name)
                or is_augmentation_dot(candidate.class_name)
            )
            pitch_symbols.extend(candidate for candidate in thin_symbols if is_pitch_modifier(candidate.class_name))
            if thin_symbols:
                extractor_mode = (
                    f"{extractor_mode}+tiled_thin_symbols"
                    if extractor_mode != "cv_fallback"
                    else "tiled_thin_symbols"
                )
            else:
                warnings.append("Tiled thin-symbol checkpoint ran but returned no retained rhythm/pitch symbols.")
            thin_checkpoint_for_result = str(thin_checkpoint_source)
        except Exception as exc:  # pragma: no cover - runtime dependency path
            warnings.append(f"Tiled thin-symbol extraction failed: {exc}")

    if not candidates and use_cv_fallback:
        candidates = cv_note_candidates(image, staff_systems)
        extractor_mode = "cv_staff_notehead_pitch"
    elif not candidates:
        warnings.append("No note candidates were found.")

    if use_cv_dot_fallback is None:
        use_cv_dot_fallback = checkpoint_path is None or extractor_mode == "cv_staff_notehead_pitch"
    if use_cv_dot_fallback:
        rhythm_symbols.extend(cv_augmentation_dot_candidates(image, staff_systems))
    elif checkpoint_path is not None:
        rhythm_symbols.extend(cv_open_note_dot_candidates(image, staff_systems, candidates))
        warnings.append(
            "CV augmentation-dot fallback disabled except tight open-note dot recovery; "
            "black-note dots require detector-confirmed augmentationDot symbols."
        )
    if staff_systems:
        spacing = float(np.median([staff.spacing for staff in staff_systems]))
        rhythm_symbols = _deduplicate_symbol_candidates(rhythm_symbols, spacing=spacing)
        pitch_symbols = _deduplicate_symbol_candidates(pitch_symbols, spacing=spacing)
        rest_candidates = _deduplicate_symbol_candidates(rest_candidates, spacing=spacing)
        notation_symbols = _deduplicate_symbol_candidates(notation_symbols, spacing=spacing)

    key_signatures = key_signatures_from_symbols(pitch_symbols, staff_systems, candidates)
    key_fifths = document_key_fifths(key_signatures)

    assembly_mode: dict[str, Any] | None = None
    rhythm_relationships: list[CandidateRelationship] = []
    relationship_counts: dict[str, int] = {}
    detector_payload: Any | None = None
    if gnn_checkpoint_path is not None and candidates:
        try:
            assembly_mode, rhythm_relationships, detector_payload = assemble_candidate_relationships(
                candidates + rhythm_symbols,
                image_width=width,
                image_height=height,
                image_path=image_path,
                checkpoint_path=gnn_checkpoint_path,
            )
            relationship_counts = dict(Counter(rel.relationship_type for rel in rhythm_relationships))
        except Exception as exc:  # pragma: no cover - runtime dependency path
            warnings.append(f"GNN relationship assembly failed: {exc}")

    events = events_from_candidates(
        candidates,
        staff_systems,
        rest_candidates=rest_candidates,
        notation_symbols=notation_symbols,
        rhythm_symbols=rhythm_symbols,
        rhythm_relationships=rhythm_relationships,
        pitch_symbols=pitch_symbols,
        key_signatures=key_signatures,
        default_quarter_length=default_quarter_length,
    )
    notes = [event for event in events if isinstance(event, ExtractedNote)]
    if not notes:
        warnings.append("No notes were extracted into MIDI events.")

    run_title = title or stem

    write_midi(events, midi_path)
    write_musicxml(events, musicxml_path, title=run_title, key_fifths=key_fifths)
    write_overlay(image, staff_systems, events, overlay_path)
    detector_payload_path: str | None = None
    relationships_path: str | None = None
    if detector_payload is not None:
        detector_payload_json.write_text(
            json.dumps(detector_payload.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        detector_payload_path = str(detector_payload_json)
    if rhythm_relationships:
        relationships_json.write_text(
            json.dumps(candidate_relationships_to_dict(rhythm_relationships), indent=2),
            encoding="utf-8",
        )
        relationships_path = str(relationships_json)

    artifacts = ExtractionArtifacts(
        output_dir=str(output_dir),
        notes_json=str(notes_json),
        midi_path=str(midi_path),
        musicxml_path=str(musicxml_path),
        overlay_path=str(overlay_path),
        checkpoint_snapshot=str(checkpoint_snapshot) if checkpoint_snapshot else None,
        thin_symbol_checkpoint_snapshot=str(thin_checkpoint_snapshot) if thin_checkpoint_snapshot else None,
        detector_payload_json=detector_payload_path,
        relationships_json=relationships_path,
    )
    result = ExtractionResult(
        image_path=str(image_path),
        image_width=width,
        image_height=height,
        extractor_mode=extractor_mode,
        detector_checkpoint=checkpoint_for_result,
        thin_symbol_checkpoint=thin_checkpoint_for_result,
        gnn_checkpoint=str(gnn_checkpoint_path) if gnn_checkpoint_path else None,
        staff_systems=staff_systems,
        events=events,
        notes=notes,
        key_signatures=key_signatures,
        key_fifths=key_fifths,
        assembly_mode=assembly_mode,
        relationship_count=len(rhythm_relationships),
        relationship_counts=relationship_counts,
        notation_symbol_count=len(notation_symbols),
        artifacts=artifacts,
        warnings=warnings,
    )
    notes_json.write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")
    return result


def result_to_dict(result: ExtractionResult) -> dict[str, Any]:
    """Convert extraction result dataclasses into JSON-friendly dictionaries."""
    data = asdict(result)
    data["staff_count"] = len(result.staff_systems)
    data["event_count"] = len(result.events)
    data["note_count"] = len(result.notes)
    data["rest_count"] = sum(1 for event in result.events if isinstance(event, ExtractedRest))
    data["slur_count"] = sum(len(note.slur_starts) for note in result.notes)
    data["tie_count"] = sum(len(note.tie_starts) for note in result.notes)
    data["disclaimer"] = (
        "Demo note extraction: pitch is estimated from treble-clef staff geometry, "
        "rhythm is heuristic, and this is not an evaluation metric run."
    )
    return data
