"""Detect staff regions in MUSCIMA grayscale page images.

This module is the image-processing side of the project. It takes one page
image, extracts a staff-line signal, builds staff candidates across overlapping
vertical slices, and returns final `(y_min, y_max)` staff regions that later
graph-building code can use.
"""

from pathlib import Path
import argparse
import csv

import cv2
import numpy as np
from scipy.signal import find_peaks


PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_ROOT = PROJECT_ROOT / "data" / "cvc-muscima" / "CVCMUSCIMA_WI" / "PNG_GT_Gray"


def group_nearby_values(values, max_gap):
    """Group sorted scalar values when consecutive gaps stay below `max_gap`."""
    # This is used repeatedly to merge noisy detections into more stable line or region groups.
    if not values:
        return []

    groups = [[values[0]]]

    for value in values[1:]:
        if value - groups[-1][-1] <= max_gap:
            groups[-1].append(value)
        else:
            groups.append([value])

    return groups


def merge_nearby_regions(regions, max_gap):
    """Merge vertically adjacent staff regions when the gap between them is small."""
    if not regions:
        return []

    regions = sorted(regions)
    merged_regions = [list(regions[0])]

    for y_min, y_max in regions[1:]:
        previous_y_min, previous_y_max = merged_regions[-1]

        if y_min <= previous_y_max + max_gap:
            merged_regions[-1][1] = max(previous_y_max, y_max)
        else:
            merged_regions.append([y_min, y_max])

    return [(int(y_min), int(y_max)) for y_min, y_max in merged_regions]


def split_tall_regions(regions, estimated_gap, image_height):
    """Split suspiciously tall regions that likely contain more than one merged staff."""
    if not regions:
        return []

    expected_staff_height = max(60, int(round(estimated_gap * 6.0)))
    max_single_staff_height = int(round(expected_staff_height * 1.65))
    split_regions = []

    for y_min, y_max in regions:
        region_height = y_max - y_min

        if region_height <= max_single_staff_height:
            split_regions.append((int(y_min), int(y_max)))
            continue

        split_count = max(2, int(round(region_height / expected_staff_height)))
        split_height = region_height / split_count
        overlap_margin = max(4, int(round(estimated_gap * 0.5)))

        for split_index in range(split_count):
            split_y_min = y_min + int(round(split_index * split_height))
            split_y_max = y_min + int(round((split_index + 1) * split_height))

            if split_index > 0:
                split_y_min -= overlap_margin

            if split_index < split_count - 1:
                split_y_max += overlap_margin

            split_y_min = max(0, split_y_min)
            split_y_max = min(image_height - 1, split_y_max)
            split_regions.append((int(split_y_min), int(split_y_max)))

    return sorted(split_regions)


def load_grayscale_image(image_path):
    """Load one page image as a single-channel grayscale array."""
    # cv2.imread(..., cv2.IMREAD_GRAYSCALE) means:
    # - open the image from disk
    # - return it as one gray channel instead of a color image
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    return image


def add_vertical_padding(image, vertical_padding):
    """Pad the image vertically so edge staffs are not cut off during detection."""
    # cv2.copyMakeBorder adds a border around the image.
    # We use white padding so staffs near the edge are easier to detect.
    return cv2.copyMakeBorder(
        image,
        vertical_padding,
        vertical_padding,
        0,
        0,
        borderType=cv2.BORDER_CONSTANT,
        value=255,
    )


def threshold_music_image(image, method="otsu"):
    """Convert a grayscale page to a binary foreground image using one thresholding path."""
    # cv2.GaussianBlur smooths the image and reduces tiny noise.
    blurred_image = cv2.GaussianBlur(image, (3, 3), 0)

    if method == "adaptive":
        # cv2.adaptiveThreshold chooses thresholds locally instead of one global cutoff.
        return cv2.adaptiveThreshold(
            blurred_image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            11,
        )

    # Default path: one global threshold chosen by Otsu.
    _, binary_image = cv2.threshold(
        blurred_image,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    return binary_image


def build_binary_variants(image):
    """Build several binary views of the same page so the detector can pick the strongest one."""
    otsu_binary = threshold_music_image(image, method="otsu")
    adaptive_binary = threshold_music_image(image, method="adaptive")

    # Combining both binaries lets us keep lines found by either thresholding path.
    combined_binary = cv2.bitwise_or(otsu_binary, adaptive_binary)

    return [
        ("otsu", otsu_binary),
        ("adaptive", adaptive_binary),
        ("combined", combined_binary),
    ]


def build_horizontal_lines_image(binary_image, image_width):
    """Extract a staff-line emphasis image with multi-scale horizontal morphology."""
    # Use more than one horizontal kernel width so we can keep both strong and broken staff lines.
    kernel_widths = sorted(
        {
            max(25, image_width // 12),
            max(25, image_width // 15),
            max(25, image_width // 20),
        }
    )

    horizontal_lines = np.zeros_like(binary_image)

    for kernel_width in kernel_widths:
        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (kernel_width, 1),
        )
        opened_lines = cv2.morphologyEx(
            binary_image,
            cv2.MORPH_OPEN,
            horizontal_kernel,
        )
        horizontal_lines = cv2.bitwise_or(horizontal_lines, opened_lines)

    return horizontal_lines


def estimate_skew_angle(horizontal_lines, image_width):
    """Estimate the dominant page skew from near-horizontal line segments."""
    # cv2.HoughLinesP finds line segments in a binary image.
    # We use it only on the horizontal-lines image so the staff lines dominate.
    lines = cv2.HoughLinesP(
        horizontal_lines,
        1,
        np.pi / 180,
        threshold=max(80, image_width // 20),
        minLineLength=max(150, image_width // 4),
        maxLineGap=20,
    )

    if lines is None:
        return 0.0

    angles = []

    for line in lines[:, 0]:
        x1, y1, x2, y2 = line
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))

        # Only keep nearly horizontal lines for skew estimation.
        if abs(angle) <= 15:
            angles.append(angle)

    if not angles:
        return 0.0

    return float(np.median(angles))


def rotate_image(image, angle_degrees):
    """Rotate an image by a small angle while keeping a white page background."""
    if abs(angle_degrees) < 0.05:
        return image

    image_height, image_width = image.shape
    image_center = (image_width / 2, image_height / 2)

    # cv2.getRotationMatrix2D creates the transform for image rotation.
    rotation_matrix = cv2.getRotationMatrix2D(image_center, angle_degrees, 1.0)

    # cv2.warpAffine applies that rotation to the whole image.
    return cv2.warpAffine(
        image,
        rotation_matrix,
        (image_width, image_height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=255,
    )


def detect_line_centers_in_slice(horizontal_slice):
    """Find candidate staff-line row centers inside one vertical slice."""
    # Sum the white pixels in each row of this slice.
    row_strengths = np.sum(horizontal_slice > 0, axis=1)

    if row_strengths.max() == 0:
        return []

    # find_peaks finds local high points in a 1D signal.
    # Here, a peak means a row that looks like a strong staff line.
    peak_indices, _ = find_peaks(
        row_strengths,
        height=max(10, int(row_strengths.max() * 0.35)),
        distance=6,
        prominence=20,
    )

    return peak_indices.tolist()


def build_overlapping_slice_ranges(image_width, number_of_slices=12, overlap_ratio=0.5):
    """Create overlapping vertical slice ranges across the page width."""
    # We use overlapping slices so a weak staff can still be found in a nearby slice.
    if number_of_slices <= 1:
        return [(0, image_width)]

    step = max(1, image_width // (number_of_slices + 1))
    slice_width = max(step + 1, int(round(step / (1.0 - overlap_ratio))))
    slice_width = min(image_width, slice_width)

    slice_ranges = []

    for slice_index in range(number_of_slices):
        x_start = slice_index * step
        x_end = min(image_width, x_start + slice_width)

        if x_end - x_start < 50:
            continue

        slice_ranges.append((x_start, x_end))

        if x_end == image_width:
            break

    if slice_ranges and slice_ranges[-1][1] < image_width:
        slice_ranges.append((max(0, image_width - slice_width), image_width))

    return slice_ranges


def collect_slice_peak_data(horizontal_lines, slice_ranges):
    """Collect raw line-center detections for every vertical slice."""
    slice_peak_data = []

    for slice_index, (x_start, x_end) in enumerate(slice_ranges):
        horizontal_slice = horizontal_lines[:, x_start:x_end]
        line_centers = detect_line_centers_in_slice(horizontal_slice)
        slice_peak_data.append(
            {
                "slice_index": slice_index,
                "x_start": x_start,
                "x_end": x_end,
                "line_centers": line_centers,
            }
        )

    return slice_peak_data


def estimate_staff_line_gap(slice_peak_data):
    """Estimate the typical spacing between neighboring staff lines on the page."""
    # Estimate the most common gap between neighboring staff lines.
    candidate_gaps = []

    for slice_data in slice_peak_data:
        line_centers = slice_data["line_centers"]

        if len(line_centers) < 2:
            continue

        line_gaps = np.diff(line_centers)

        for gap in line_gaps:
            if 6 <= gap <= 30:
                candidate_gaps.append(int(gap))

    if not candidate_gaps:
        return 12

    return int(np.median(candidate_gaps))


def build_staff_candidates_in_slice(line_centers, estimated_gap, slice_index):
    """Build 5-line staff candidates inside one slice from regular peak patterns."""
    # Look for a 5-line staff pattern with nearly regular spacing.
    if len(line_centers) < 5:
        return []

    tolerance = max(2, int(round(estimated_gap * 0.4)))
    candidates = []

    for start_index in range(len(line_centers)):
        group = [line_centers[start_index]]
        next_index = start_index + 1

        while len(group) < 5:
            target_y = group[-1] + estimated_gap
            best_match_index = None
            best_error = None

            for candidate_index in range(next_index, len(line_centers)):
                candidate_y = line_centers[candidate_index]

                if candidate_y < target_y - tolerance:
                    continue

                if candidate_y > target_y + tolerance:
                    break

                error = abs(candidate_y - target_y)

                if best_error is None or error < best_error:
                    best_match_index = candidate_index
                    best_error = error

            if best_match_index is None:
                break

            group.append(line_centers[best_match_index])
            next_index = best_match_index + 1

        if len(group) == 5:
            group_gaps = np.diff(group)
            local_gap = float(np.median(group_gaps))

            if np.max(np.abs(group_gaps - local_gap)) <= tolerance:
                candidates.append(
                    {
                        "slice_index": slice_index,
                        "top_y": int(group[0]),
                        "bottom_y": int(group[-1]),
                        "center_y": int(round((group[0] + group[-1]) / 2)),
                        "gap": float(local_gap),
                        "score": float(np.sum(np.abs(group_gaps - local_gap))),
                    }
                )

    deduplicated_candidates = []

    for candidate in sorted(candidates, key=lambda item: (item["center_y"], item["score"])):
        if not deduplicated_candidates:
            deduplicated_candidates.append(candidate)
            continue

        previous_candidate = deduplicated_candidates[-1]

        if abs(candidate["center_y"] - previous_candidate["center_y"]) <= estimated_gap:
            if candidate["score"] < previous_candidate["score"]:
                deduplicated_candidates[-1] = candidate
        else:
            deduplicated_candidates.append(candidate)

    return deduplicated_candidates


def build_all_staff_candidates(slice_peak_data, estimated_gap):
    """Build per-slice staff candidates and one flattened list across the page."""
    candidates_by_slice = []
    all_candidates = []

    for slice_data in slice_peak_data:
        slice_candidates = build_staff_candidates_in_slice(
            slice_data["line_centers"],
            estimated_gap,
            slice_data["slice_index"],
        )
        candidates_by_slice.append(slice_candidates)
        all_candidates.extend(slice_candidates)

    return candidates_by_slice, all_candidates


def build_staff_tracks(candidates_by_slice, estimated_gap):
    """Track staff candidates across neighboring slices to form page-level staffs."""
    # Connect staff candidates across neighboring slices if they look like the same staff.
    tracks = []
    max_center_difference = max(10, int(round(estimated_gap * 2.0)))
    max_gap_difference = max(3.0, estimated_gap * 0.5)
    max_slice_gap = 2

    for slice_index, slice_candidates in enumerate(candidates_by_slice):
        for track in tracks:
            track["matched_in_current_slice"] = False

        for candidate in sorted(slice_candidates, key=lambda item: item["center_y"]):
            best_track = None
            best_score = None

            for track in tracks:
                last_observation = track["observations"][-1]
                slice_gap = slice_index - last_observation["slice_index"]

                if slice_gap < 1 or slice_gap > max_slice_gap:
                    continue

                if track["matched_in_current_slice"]:
                    continue

                center_difference = abs(candidate["center_y"] - last_observation["center_y"])
                gap_difference = abs(candidate["gap"] - last_observation["gap"])

                if center_difference > max_center_difference:
                    continue

                if gap_difference > max_gap_difference:
                    continue

                score = center_difference + (gap_difference * 2) + (slice_gap - 1) * estimated_gap

                if best_score is None or score < best_score:
                    best_score = score
                    best_track = track

            if best_track is None:
                tracks.append(
                    {
                        "observations": [candidate.copy()],
                        "matched_in_current_slice": True,
                    }
                )
            else:
                best_track["observations"].append(candidate.copy())
                best_track["matched_in_current_slice"] = True

    for track in tracks:
        track.pop("matched_in_current_slice", None)

    return tracks


def interpolate_staff_track(track):
    """Fill short missing slice gaps inside one staff track by interpolation."""
    # Fill short gaps so one missed slice does not break the whole staff track.
    observations = sorted(track["observations"], key=lambda item: item["slice_index"])

    if not observations:
        return []

    filled_observations = [observations[0].copy()]

    for previous_observation, next_observation in zip(observations, observations[1:]):
        slice_gap = next_observation["slice_index"] - previous_observation["slice_index"]

        if 1 < slice_gap <= 3:
            for offset in range(1, slice_gap):
                interpolation_ratio = offset / slice_gap
                filled_observations.append(
                    {
                        "slice_index": previous_observation["slice_index"] + offset,
                        "top_y": int(round(previous_observation["top_y"] + interpolation_ratio * (next_observation["top_y"] - previous_observation["top_y"]))),
                        "bottom_y": int(round(previous_observation["bottom_y"] + interpolation_ratio * (next_observation["bottom_y"] - previous_observation["bottom_y"]))),
                        "center_y": int(round(previous_observation["center_y"] + interpolation_ratio * (next_observation["center_y"] - previous_observation["center_y"]))),
                        "gap": float(previous_observation["gap"] + interpolation_ratio * (next_observation["gap"] - previous_observation["gap"])),
                        "interpolated": True,
                    }
                )

        filled_observations.append(next_observation.copy())

    return filled_observations


def build_staff_regions_from_tracks(staff_tracks, image_height, vertical_padding, estimated_gap):
    """Convert tracked staff observations into final vertical staff regions."""
    if not staff_tracks:
        return []

    staff_regions = []

    for track in staff_tracks:
        observed_observations = sorted(track["observations"], key=lambda item: item["slice_index"])
        observed_count = len(observed_observations)

        if observed_count < 2:
            continue

        filled_observations = interpolate_staff_track(track)
        slice_span = filled_observations[-1]["slice_index"] - filled_observations[0]["slice_index"] + 1

        if slice_span < 2 and observed_count < 3:
            continue

        average_top_y = int(round(np.mean([observation["top_y"] for observation in filled_observations])))
        average_bottom_y = int(round(np.mean([observation["bottom_y"] for observation in filled_observations])))
        average_gap = float(np.mean([observation["gap"] for observation in filled_observations]))
        margin = max(8, int(round(average_gap)))

        y_min = max(0, average_top_y - margin - vertical_padding)
        y_max = min(image_height - 1, average_bottom_y + margin - vertical_padding)
        staff_regions.append((int(y_min), int(y_max)))

    return merge_nearby_regions(staff_regions, max_gap=max(8, int(round(estimated_gap))))


def merge_staff_candidates(staff_candidates, estimated_gap, minimum_votes):
    """Merge similar slice-level staff candidates when enough slices agree on them."""
    if not staff_candidates:
        return []

    sorted_candidates = sorted(staff_candidates, key=lambda item: item["center_y"])
    candidate_groups = [[sorted_candidates[0]]]
    max_center_gap = max(8, int(round(estimated_gap * 1.5)))

    for candidate in sorted_candidates[1:]:
        previous_candidate = candidate_groups[-1][-1]

        if candidate["center_y"] - previous_candidate["center_y"] <= max_center_gap:
            candidate_groups[-1].append(candidate)
        else:
            candidate_groups.append([candidate])

    merged_candidates = []

    for group in candidate_groups:
        unique_slice_indices = {candidate["slice_index"] for candidate in group}

        if len(unique_slice_indices) < minimum_votes:
            continue

        merged_candidates.append(
            {
                "top_y": int(round(np.mean([candidate["top_y"] for candidate in group]))),
                "bottom_y": int(round(np.mean([candidate["bottom_y"] for candidate in group]))),
                "center_y": int(round(np.mean([candidate["center_y"] for candidate in group]))),
                "gap": float(np.mean([candidate["gap"] for candidate in group])),
            }
        )

    return merged_candidates


def build_staff_regions_from_candidates(merged_candidates, image_height, vertical_padding):
    """Convert merged staff candidates into final vertical staff regions."""
    if not merged_candidates:
        return []

    staff_regions = []

    for candidate in sorted(merged_candidates, key=lambda item: item["center_y"]):
        margin = max(8, int(round(candidate["gap"])))
        y_min = max(0, candidate["top_y"] - margin - vertical_padding)
        y_max = min(image_height - 1, candidate["bottom_y"] + margin - vertical_padding)
        staff_regions.append((int(y_min), int(y_max)))

    return merge_nearby_regions(staff_regions, max_gap=8)


def collect_global_line_centers(slice_peak_data, minimum_votes):
    """Collect consensus line centers across slices for the fallback detector path."""
    # Merge similar line centers found in different vertical slices.
    all_centers = []

    for slice_data in slice_peak_data:
        all_centers.extend(slice_data["line_centers"])

    if not all_centers:
        return []

    grouped_centers = group_nearby_values(sorted(all_centers), max_gap=4)
    merged_centers = []

    for group in grouped_centers:
        if len(group) >= minimum_votes:
            merged_centers.append(int(round(sum(group) / len(group))))

    return merged_centers


def build_staff_regions_from_line_centers(line_centers, image_height, vertical_padding):
    """Build fallback staff regions directly from globally merged line centers."""
    # Turn detected staff-line centers into wider staff regions.
    if len(line_centers) < 3:
        return []

    line_centers = sorted(line_centers)

    if len(line_centers) >= 2:
        line_gaps = np.diff(line_centers)
        typical_gap = int(np.median(line_gaps))
    else:
        typical_gap = 12

    grouped_lines = group_nearby_values(line_centers, max_gap=max(12, typical_gap * 2))
    staff_regions = []

    for group in grouped_lines:
        group_top = group[0]
        group_bottom = group[-1]

        is_near_image_edge = (
            group_top < vertical_padding + 40
            or group_bottom > image_height + vertical_padding - 40
        )

        minimum_lines = 3 if is_near_image_edge else 4

        if len(group) >= minimum_lines:
            y_min = max(0, group_top - typical_gap - vertical_padding)
            y_max = min(image_height - 1, group_bottom + typical_gap - vertical_padding)
            staff_regions.append((int(y_min), int(y_max)))

    return merge_nearby_regions(staff_regions, max_gap=max(8, typical_gap))


def score_staff_regions(staff_regions, estimated_gap, slice_peak_data, all_staff_candidates):
    """Score one binary-variant result so the detector can choose the strongest page interpretation."""
    if not staff_regions:
        return -100.0

    score = 0.0
    region_count = len(staff_regions)
    zero_peak_slices = sum(1 for slice_data in slice_peak_data if not slice_data["line_centers"])
    score += region_count * 20.0
    score -= zero_peak_slices * 2.0
    score += min(len(all_staff_candidates), 30) * 1.5

    if 6 <= estimated_gap <= 24:
        score += 10.0
    else:
        score -= 10.0

    if region_count > 10:
        score -= (region_count - 10) * 10.0

    if region_count >= 2:
        centers = [0.5 * (y_min + y_max) for y_min, y_max in staff_regions]
        center_gaps = np.diff(sorted(centers))

        if len(center_gaps) > 0:
            average_gap = float(np.mean(center_gaps))
            gap_std = float(np.std(center_gaps))

            if average_gap > 0:
                score += 20.0 / (1.0 + gap_std / average_gap)

    return score


def detect_staff_regions_from_binary(binary_image, image_width, image_height, vertical_padding):
    """Run the full staff-detection pipeline for one binary page image."""
    horizontal_lines = build_horizontal_lines_image(binary_image, image_width)
    slice_ranges = build_overlapping_slice_ranges(image_width, number_of_slices=12, overlap_ratio=0.5)
    slice_peak_data = collect_slice_peak_data(horizontal_lines, slice_ranges)
    estimated_gap = estimate_staff_line_gap(slice_peak_data)
    candidates_by_slice, all_staff_candidates = build_all_staff_candidates(slice_peak_data, estimated_gap)

    staff_tracks = build_staff_tracks(candidates_by_slice, estimated_gap)
    track_staff_regions = build_staff_regions_from_tracks(
        staff_tracks,
        image_height,
        vertical_padding,
        estimated_gap,
    )

    minimum_candidate_votes = max(2, len(slice_ranges) // 4)
    merged_candidates = merge_staff_candidates(
        all_staff_candidates,
        estimated_gap,
        minimum_candidate_votes,
    )
    candidate_staff_regions = build_staff_regions_from_candidates(
        merged_candidates,
        image_height,
        vertical_padding,
    )

    minimum_center_votes = max(3, len(slice_ranges) // 3)
    global_line_centers = collect_global_line_centers(slice_peak_data, minimum_center_votes)
    fallback_staff_regions = build_staff_regions_from_line_centers(
        global_line_centers,
        image_height,
        vertical_padding,
    )

    if len(track_staff_regions) >= 2:
        final_staff_regions = track_staff_regions
    elif len(candidate_staff_regions) >= 2:
        final_staff_regions = candidate_staff_regions
    else:
        final_staff_regions = fallback_staff_regions

    final_staff_regions = split_tall_regions(
        final_staff_regions,
        estimated_gap,
        image_height,
    )

    score = score_staff_regions(
        final_staff_regions,
        estimated_gap,
        slice_peak_data,
        all_staff_candidates,
    )

    return {
        "staff_regions": final_staff_regions,
        "estimated_gap": estimated_gap,
        "score": score,
        "track_staff_regions": track_staff_regions,
        "candidate_staff_regions": candidate_staff_regions,
        "fallback_staff_regions": fallback_staff_regions,
    }


def choose_best_binary_variant(deskewed_image, image_width, image_height, vertical_padding):
    """Evaluate all binary variants and keep the one with the best structural score."""
    best_result = None

    for variant_name, binary_image in build_binary_variants(deskewed_image):
        result = detect_staff_regions_from_binary(
            binary_image,
            image_width,
            image_height,
            vertical_padding,
        )
        result["variant_name"] = variant_name

        if best_result is None or result["score"] > best_result["score"]:
            best_result = result

    return best_result


def detect_staff_lines(image_path):
    """Detect staff regions in one music-page image.

    Args:
        image_path: Path to one MUSCIMA page image.

    Returns:
        A list of `(y_min, y_max)` tuples, one per detected staff region.
    """
    image = load_grayscale_image(image_path)
    original_image_height, image_width = image.shape
    vertical_padding = 40

    padded_image = add_vertical_padding(image, vertical_padding)
    initial_binary_image = threshold_music_image(padded_image, method="otsu")
    initial_horizontal_lines = build_horizontal_lines_image(initial_binary_image, image_width)
    skew_angle = estimate_skew_angle(initial_horizontal_lines, image_width)
    deskewed_image = rotate_image(padded_image, -skew_angle)

    best_result = choose_best_binary_variant(
        deskewed_image,
        image_width,
        original_image_height,
        vertical_padding,
    )

    return best_result["staff_regions"]


def save_staff_debug_image(image_path, staff_regions, output_path):
    """Save a debug overlay showing detected staff regions on top of the page image."""
    # Load the image again so we can draw colored boxes on it.
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise FileNotFoundError(f"Could not load image for debug output: {image_path}")

    # cv2.cvtColor converts the grayscale image to BGR color.
    # We need this because red rectangles cannot be drawn on a 1-channel image.
    debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    image_height, image_width = image.shape

    for index, (y_min, y_max) in enumerate(staff_regions, start=1):
        cv2.rectangle(
            debug_image,
            (0, y_min),
            (image_width - 1, y_max),
            (0, 0, 255),
            2,
        )
        cv2.putText(
            debug_image,
            f"staff {index}",
            (5, max(20, y_min - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )

    # cv2.imwrite saves the final debug image to disk.
    cv2.imwrite(str(output_path), debug_image)


def parse_cli_args():
    """Parse command-line arguments for staff-detection runs."""
    parser = argparse.ArgumentParser(description="Run staff detection on one image or one writer folder.")
    parser.add_argument("--image", type=str, default=None, help="Path to one page image.")
    parser.add_argument("--writer", type=str, default=None, help="Writer folder name such as w-14.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for debug images and summaries. Required for --writer, optional for --image.",
    )
    return parser.parse_args()


def run_staff_detection_on_writer(writer_name, output_dir):
    """Run staff detection on every image in one writer folder and save debug outputs.

    This is the batch-debug entry point used when you want to inspect page-by-page
    overlays and a simple writer-level summary CSV.
    """
    input_dir = IMAGE_ROOT / writer_name

    if not input_dir.exists():
        raise FileNotFoundError(f"Writer folder not found: {input_dir}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for image_path in sorted(input_dir.glob("*.png")):
        staff_regions = detect_staff_lines(image_path)
        debug_path = output_dir / f"{image_path.stem}_staff_debug.png"
        save_staff_debug_image(image_path, staff_regions, debug_path)
        summary_rows.append({
            "image": image_path.name,
            "staff_count": len(staff_regions),
            "staff_regions": str(staff_regions),
        })

    summary_path = output_dir / f"{writer_name}_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["image", "staff_count", "staff_regions"])
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Saved writer debug outputs to: {output_dir}")
    print(f"Saved writer summary to: {summary_path}")


def main():
    """Run staff detection from the command line."""
    args = parse_cli_args()

    if args.image:
        image_path = Path(args.image)
        staff_regions = detect_staff_lines(image_path)
        print(f"Detected {len(staff_regions)} staff regions")
        print(staff_regions)

        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{image_path.stem}_staff_debug.png"
            save_staff_debug_image(image_path, staff_regions, output_path)
            print(f"Saved debug image to: {output_path}")
        return

    if args.writer:
        if not args.output_dir:
            raise ValueError("--output-dir is required when using --writer.")

        run_staff_detection_on_writer(args.writer, args.output_dir)
        return

    raise ValueError("Provide either --image or --writer.")


if __name__ == "__main__":
    main()
