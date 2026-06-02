"""Clean-sheet note extraction helpers for local demos.

This module is intentionally separate from the official detector metric path.
It can use a YOLO checkpoint to detect notehead boxes, estimate pitch from staff
geometry, and infer simple rhythm from notehead/beam/flag/dot geometry.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import cv2
import numpy as np


STEP_NAMES = ["C", "D", "E", "F", "G", "A", "B"]
STEP_TO_SEMITONE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
TREBLE_BOTTOM_LINE_DIATONIC = 7 * 4 + STEP_NAMES.index("E")


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


@dataclass(frozen=True)
class ExtractedNote:
    """Pitch-level note extracted from an image."""

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
    dotted: bool = False
    rhythm_source: str = "default"


@dataclass(frozen=True)
class ExtractionArtifacts:
    """Paths written by an extraction run."""

    output_dir: str
    notes_json: str
    midi_path: str
    musicxml_path: str
    overlay_path: str
    checkpoint_snapshot: str | None = None


@dataclass(frozen=True)
class ExtractionResult:
    """Complete result for a note extraction run."""

    image_path: str
    image_width: int
    image_height: int
    extractor_mode: str
    detector_checkpoint: str | None
    staff_systems: list[StaffSystem]
    notes: list[ExtractedNote]
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


def detect_staff_systems(image: np.ndarray) -> list[StaffSystem]:
    """Detect five-line staff systems from long horizontal strokes."""
    height, width = image.shape[:2]
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(40, width // 45), 1))
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    row_counts = (horizontal > 0).sum(axis=1)
    rows = np.where(row_counts > max(120, int(width * 0.15)))[0]
    line_centers = [(start + end) / 2.0 for start, end in _group_runs(rows, max_gap=3)]

    systems: list[StaffSystem] = []
    i = 0
    while i <= len(line_centers) - 5:
        group = line_centers[i : i + 5]
        diffs = np.diff(group)
        if len(diffs) == 4 and float(np.std(diffs)) < 3.0 and 6.0 <= float(np.mean(diffs)) <= 30.0:
            spacing = float(np.mean(diffs))
            y0 = max(0, int(min(group)) - 3)
            y1 = min(height, int(max(group)) + 4)
            start_x, end_x = _largest_column_run(horizontal[y0:y1, :])
            systems.append(
                StaffSystem(
                    index=len(systems),
                    line_y=tuple(float(value) for value in group),  # type: ignore[arg-type]
                    spacing=spacing,
                    start_x=start_x,
                    end_x=end_x,
                )
            )
            i += 5
            continue
        i += 1

    return systems


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


def snapshot_checkpoint(checkpoint_path: str | Path, output_dir: str | Path) -> Path:
    """Copy a checkpoint before inference so live training can keep writing safely."""
    source = Path(checkpoint_path)
    if not source.exists():
        raise FileNotFoundError(f"Checkpoint not found: {source}")
    destination = Path(output_dir) / f"{source.stem}_snapshot{source.suffix}"
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


def closest_staff(y: float, staff_systems: list[StaffSystem]) -> StaffSystem | None:
    """Return the nearest staff system whose vertical range can contain y."""
    compatible = [staff for staff in staff_systems if staff.contains_y(y)]
    if not compatible:
        return None
    return min(compatible, key=lambda staff: abs(y - (staff.top_y + staff.bottom_y) / 2.0))


def pitch_from_y(y: float, staff: StaffSystem) -> tuple[str, int, int]:
    """Map a notehead y coordinate to treble-clef pitch."""
    half_spacing = staff.spacing / 2.0
    diatonic_offset = int(round((staff.bottom_y - y) / half_spacing))
    diatonic = TREBLE_BOTTOM_LINE_DIATONIC + diatonic_offset
    step = STEP_NAMES[diatonic % 7]
    octave = diatonic // 7
    midi_pitch = 12 * (octave + 1) + STEP_TO_SEMITONE[step]
    return step, octave, midi_pitch


def is_notehead(class_name: str) -> bool:
    return "notehead" in class_name.lower()


def is_beam(class_name: str) -> bool:
    return class_name.lower() == "beam"


def is_flag(class_name: str) -> bool:
    return class_name.lower().startswith("flag")


def is_augmentation_dot(class_name: str) -> bool:
    return class_name.lower() == "augmentationdot"


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


def _beam_count_for_note(
    note: DetectionCandidate,
    staff: StaffSystem,
    rhythm_symbols: list[DetectionCandidate],
) -> int:
    count = 0
    note_x = note.x_center
    for symbol in rhythm_symbols:
        if not is_beam(symbol.class_name) or not _symbol_staff_compatible(symbol, staff):
            continue
        x1, y1, x2, y2 = symbol.bbox_xyxy
        y_distance = min(abs(note.y_center - y1), abs(note.y_center - y2), abs(note.y_center - symbol.y_center))
        x_margin = staff.spacing * 0.75
        if x1 - x_margin <= note_x <= x2 + x_margin and y_distance <= staff.spacing * 7.0:
            count += 1
    return count


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
    x1, _, x2, _ = note.bbox_xyxy
    best_distance: float | None = None
    for symbol in rhythm_symbols:
        if not is_augmentation_dot(symbol.class_name) or not _symbol_staff_compatible(symbol, staff):
            continue
        if symbol.x_center <= note.x_center:
            continue
        x_distance = symbol.x_center - x2
        y_distance = abs(symbol.y_center - note.y_center)
        if 0.0 <= x_distance <= staff.spacing * 2.8 and y_distance <= staff.spacing * 0.9:
            distance = x_distance + y_distance
            if best_distance is None or distance < best_distance:
                best_distance = distance
    return best_distance is not None


def rhythm_for_note(
    note: DetectionCandidate,
    staff: StaffSystem,
    rhythm_symbols: list[DetectionCandidate],
    *,
    default_quarter_length: float = 1.0,
) -> tuple[float, bool, str]:
    """Infer note duration from class plus nearby beams, flags, and dots."""
    duration = quarter_length_for_class(note.class_name, default_quarter_length)
    source = "notehead_class" if duration != default_quarter_length else "default_quarter"

    if "black" in note.class_name.lower() or note.source == "cv_fallback":
        flag_duration = _flag_duration_for_note(note, staff, rhythm_symbols)
        beam_count = _beam_count_for_note(note, staff, rhythm_symbols)
        if flag_duration is not None:
            duration = flag_duration
            source = "flag"
        elif beam_count > 0:
            duration = max(1.0 / 32.0, 1.0 / (2**beam_count))
            source = f"beam_x{beam_count}"
        else:
            duration = default_quarter_length
            source = "default_quarter"

    dotted = _has_augmentation_dot(note, staff, rhythm_symbols)
    if dotted:
        duration *= 1.5
        source = f"{source}+augmentation_dot"
    return duration, dotted, source


def notes_from_candidates(
    candidates: list[DetectionCandidate],
    staff_systems: list[StaffSystem],
    *,
    rhythm_symbols: list[DetectionCandidate] | None = None,
    default_quarter_length: float = 1.0,
) -> list[ExtractedNote]:
    """Convert notehead boxes into ordered treble-clef note events."""
    if not staff_systems:
        return []
    spacing = float(np.median([staff.spacing for staff in staff_systems]))
    candidates = _deduplicate_candidates(candidates, spacing=spacing)
    rhythm_symbols = list(rhythm_symbols or [])
    notes: list[ExtractedNote] = []
    for candidate in candidates:
        staff = closest_staff(candidate.y_center, staff_systems)
        if staff is None:
            continue
        step, octave, midi_pitch = pitch_from_y(candidate.y_center, staff)
        quarter_length, dotted, rhythm_source = rhythm_for_note(
            candidate,
            staff,
            rhythm_symbols,
            default_quarter_length=default_quarter_length,
        )
        notes.append(
            ExtractedNote(
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
                quarter_length=quarter_length,
                onset_quarter=0.0,
                dotted=dotted,
                rhythm_source=rhythm_source,
            )
        )

    notes.sort(key=lambda note: (note.staff_index, note.x_center, note.y_center))
    ordered: list[ExtractedNote] = []
    onset = 0.0
    previous_staff = None
    group_x: float | None = None
    group_duration = 0.0
    group_threshold_by_staff = {staff.index: staff.spacing * 1.15 for staff in staff_systems}
    for note in notes:
        if previous_staff is None or note.staff_index != previous_staff:
            if previous_staff is not None:
                onset += group_duration
            group_x = None
            group_duration = 0.0
        elif group_x is None or abs(note.x_center - group_x) > group_threshold_by_staff[note.staff_index]:
            onset += group_duration
            group_x = None
            group_duration = 0.0

        if group_x is None:
            group_x = note.x_center
        ordered.append(
            ExtractedNote(
                order=len(ordered) + 1,
                staff_index=note.staff_index,
                x_center=note.x_center,
                y_center=note.y_center,
                bbox_xyxy=note.bbox_xyxy,
                class_name=note.class_name,
                confidence=note.confidence,
                source=note.source,
                step=note.step,
                octave=note.octave,
                midi_pitch=note.midi_pitch,
                quarter_length=note.quarter_length,
                onset_quarter=onset,
                dotted=note.dotted,
                rhythm_source=note.rhythm_source,
            )
        )
        previous_staff = note.staff_index
        group_duration = max(group_duration, note.quarter_length)
    return ordered


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
    notes: list[ExtractedNote],
    output_path: str | Path,
    *,
    tempo_bpm: int = 96,
    ticks_per_quarter: int = 480,
    velocity: int = 76,
    program: int = 40,
) -> None:
    """Write a simple Standard MIDI File with real note events."""
    events: list[tuple[int, int, int, int]] = []
    for note in notes:
        start = int(round(note.onset_quarter * ticks_per_quarter))
        duration = max(1, int(round(note.quarter_length * ticks_per_quarter)))
        events.append((start, 0, note.midi_pitch, velocity))
        events.append((start + duration, 1, note.midi_pitch, 0))
    events.sort(key=lambda item: (item[0], 0 if item[1] == 1 else 1))

    mpqn = int(round(60_000_000 / max(1, tempo_bpm)))
    track = bytearray()
    track.extend(b"\x00\xff\x51\x03" + mpqn.to_bytes(3, "big"))
    track.extend(b"\x00" + bytes([0xC0, max(0, min(program, 127))]))
    last_tick = 0
    for tick, event_type, pitch, value in events:
        track.extend(_var_len(max(0, tick - last_tick)))
        status = 0x80 if event_type == 1 else 0x90
        track.extend(bytes([status, max(0, min(pitch, 127)), max(0, min(value, 127))]))
        last_tick = tick
    track.extend(b"\x00\xff\x2f\x00")

    header = b"MThd" + (6).to_bytes(4, "big") + (0).to_bytes(2, "big")
    header += (1).to_bytes(2, "big") + ticks_per_quarter.to_bytes(2, "big")
    body = b"MTrk" + len(track).to_bytes(4, "big") + bytes(track)
    Path(output_path).write_bytes(header + body)


def write_musicxml(notes: list[ExtractedNote], output_path: str | Path, *, title: str) -> None:
    """Write compact MusicXML from extracted notes."""
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
    parts.extend(_measure_start(measure_number, divisions, include_attributes=True))
    for note in notes:
        if elapsed >= 4.0:
            parts.append("    </measure>")
            measure_number += 1
            elapsed = 0.0
            parts.extend(_measure_start(measure_number, divisions, include_attributes=False))
        duration = max(1, int(round(note.quarter_length * divisions)))
        note_type = _musicxml_type(note.quarter_length)
        parts.extend(
            [
                "      <note>",
                "        <pitch>",
                f"          <step>{note.step}</step>",
                f"          <octave>{note.octave}</octave>",
                "        </pitch>",
                f"        <duration>{duration}</duration>",
                f"        <type>{note_type}</type>",
            ]
        )
        if note.dotted:
            parts.append("        <dot/>")
        parts.append("      </note>")
        elapsed += note.quarter_length
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


def _measure_start(number: int, divisions: int, *, include_attributes: bool) -> list[str]:
    lines = [f'    <measure number="{number}">']
    if include_attributes:
        lines.extend(
            [
                "      <attributes>",
                f"        <divisions>{divisions}</divisions>",
                "        <key><fifths>0</fifths></key>",
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
    notes: list[ExtractedNote],
    output_path: str | Path,
) -> None:
    """Write an image overlay showing staff geometry and extracted notes."""
    canvas = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    for staff in staff_systems:
        for y_value in staff.line_y:
            y = int(round(y_value))
            cv2.line(canvas, (int(staff.start_x), y), (int(staff.end_x), y), (0, 160, 0), 1)
    for note in notes:
        x1, y1, x2, y2 = [int(round(value)) for value in note.bbox_xyxy]
        color = (0, 0, 255) if note.source == "yolo" else (255, 0, 0)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, 2)
        dot_suffix = "." if note.dotted else ""
        label = f"{note.order}:{note.step}{note.octave}/{note.quarter_length:g}{dot_suffix}"
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


def extract_notes_from_image(
    image_path: str | Path,
    *,
    output_dir: str | Path,
    checkpoint_path: str | Path | None = None,
    snapshot_live_checkpoint: bool = True,
    confidence: float = 0.12,
    imgsz: int = 1472,
    max_det: int = 2000,
    device: str = "cpu",
    default_quarter_length: float = 1.0,
    use_cv_fallback: bool = True,
    title: str | None = None,
) -> ExtractionResult:
    """Extract approximate notes and write JSON, overlay, MusicXML, and MIDI."""
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image = read_grayscale_image(image_path)
    height, width = image.shape[:2]
    staff_systems = detect_staff_systems(image)
    warnings: list[str] = []

    candidates: list[DetectionCandidate] = []
    rhythm_symbols: list[DetectionCandidate] = []
    checkpoint_snapshot: Path | None = None
    extractor_mode = "cv_fallback"
    checkpoint_for_result: str | None = None
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
            rhythm_symbols = [
                candidate
                for candidate in all_candidates
                if is_beam(candidate.class_name)
                or is_flag(candidate.class_name)
                or is_augmentation_dot(candidate.class_name)
            ]
            extractor_mode = "yolo_notehead_staff_pitch"
            checkpoint_for_result = str(checkpoint_source)
        except Exception as exc:  # pragma: no cover - runtime dependency path
            warnings.append(f"YOLO note extraction failed: {exc}")
            candidates = []

    if not candidates and use_cv_fallback:
        candidates = cv_note_candidates(image, staff_systems)
        extractor_mode = "cv_staff_notehead_pitch"
    elif not candidates:
        warnings.append("No note candidates were found.")

    rhythm_symbols.extend(cv_augmentation_dot_candidates(image, staff_systems))

    notes = notes_from_candidates(
        candidates,
        staff_systems,
        rhythm_symbols=rhythm_symbols,
        default_quarter_length=default_quarter_length,
    )
    if not notes:
        warnings.append("No notes were extracted into MIDI events.")

    stem = image_path.stem
    notes_json = output_dir / f"{stem}_notes.json"
    midi_path = output_dir / f"{stem}_notes.mid"
    musicxml_path = output_dir / f"{stem}_notes.musicxml"
    overlay_path = output_dir / f"{stem}_notes_overlay.png"
    run_title = title or stem

    write_midi(notes, midi_path)
    write_musicxml(notes, musicxml_path, title=run_title)
    write_overlay(image, staff_systems, notes, overlay_path)

    artifacts = ExtractionArtifacts(
        output_dir=str(output_dir),
        notes_json=str(notes_json),
        midi_path=str(midi_path),
        musicxml_path=str(musicxml_path),
        overlay_path=str(overlay_path),
        checkpoint_snapshot=str(checkpoint_snapshot) if checkpoint_snapshot else None,
    )
    result = ExtractionResult(
        image_path=str(image_path),
        image_width=width,
        image_height=height,
        extractor_mode=extractor_mode,
        detector_checkpoint=checkpoint_for_result,
        staff_systems=staff_systems,
        notes=notes,
        artifacts=artifacts,
        warnings=warnings,
    )
    notes_json.write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")
    return result


def result_to_dict(result: ExtractionResult) -> dict[str, Any]:
    """Convert extraction result dataclasses into JSON-friendly dictionaries."""
    data = asdict(result)
    data["staff_count"] = len(result.staff_systems)
    data["note_count"] = len(result.notes)
    data["disclaimer"] = (
        "Demo note extraction: pitch is estimated from treble-clef staff geometry, "
        "rhythm is heuristic, and this is not an evaluation metric run."
    )
    return data
