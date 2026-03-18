from pathlib import Path
import csv

import cv2
import numpy as np
from scipy.signal import find_peaks


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = PROJECT_ROOT / "data" / "raw" / "Images" / "PNG_GT_Gray"
DEBUG_OUTPUT_DIR = PROJECT_ROOT / "tests" / "staff_debug"
SUMMARY_CSV_PATH = DEBUG_OUTPUT_DIR / "staff_debug_summary.csv"
BATCH_DEBUG_LIMIT = 100

# This test image matches annotation `CVC-MUSCIMA_W-01_N-10_D-ideal.xml`.
TEST_IMAGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "Images"
    / "PNG_GT_Gray"
    / "w-01"
    / "p010.png"
)


def group_nearby_values(values, max_gap):
    # This helper puts nearby values into the same group.
    if not values:
        return []

    groups = [[values[0]]]

    for value in values[1:]:
        if value - groups[-1][-1] <= max_gap:
            groups[-1].append(value)
        else:
            groups.append([value])

    return groups


def detect_line_centers_in_slice(horizontal_slice):
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


def collect_global_line_centers(slice_line_centers, minimum_votes):
    # Merge similar line centers found in different vertical slices.
    all_centers = []

    for centers in slice_line_centers:
        all_centers.extend(centers)

    if not all_centers:
        return []

    grouped_centers = group_nearby_values(sorted(all_centers), max_gap=4)
    merged_centers = []

    for group in grouped_centers:
        if len(group) >= minimum_votes:
            merged_centers.append(int(round(sum(group) / len(group))))

    return merged_centers


def build_staff_regions_from_line_centers(line_centers, image_height, vertical_padding):
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

    return staff_regions


def detect_staff_lines(image_path):
    # Load the image directly as grayscale.
    # cv2.imread(..., cv2.IMREAD_GRAYSCALE) means:
    # - open the image from disk
    # - return it as one gray channel instead of a color image
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    original_image_height, image_width = image.shape
    vertical_padding = 40

    # Add white space above and below the image.
    # cv2.copyMakeBorder adds a border around the image.
    # We use white padding so a staff near the edge is easier to detect.
    padded_image = cv2.copyMakeBorder(
        image,
        vertical_padding,
        vertical_padding,
        0,
        0,
        borderType=cv2.BORDER_CONSTANT,
        value=255,
    )

    # Slight blur helps reduce tiny noise before thresholding.
    # cv2.GaussianBlur smooths the image with a Gaussian filter.
    blurred_image = cv2.GaussianBlur(padded_image, (3, 3), 0)

    # Convert to a black/white image where dark markings become white.
    # cv2.threshold with THRESH_BINARY_INV + THRESH_OTSU means:
    # - choose a threshold automatically (Otsu)
    # - invert it so dark lines become white on black background
    _, binary_image = cv2.threshold(
        blurred_image,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    # Build a wide horizontal kernel.
    # cv2.getStructuringElement creates the shape used by morphology.
    horizontal_kernel_width = max(25, image_width // 15)
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (horizontal_kernel_width, 1),
    )

    # Keep only long horizontal structures.
    # cv2.morphologyEx(..., cv2.MORPH_OPEN, kernel) erodes then dilates,
    # which removes small non-horizontal shapes and keeps long lines.
    horizontal_lines = cv2.morphologyEx(
        binary_image,
        cv2.MORPH_OPEN,
        horizontal_kernel,
    )

    # Split the page into vertical slices so we detect lines locally.
    number_of_slices = 8
    slice_width = image_width // number_of_slices
    slice_line_centers = []

    for slice_index in range(number_of_slices):
        x_start = slice_index * slice_width

        if slice_index == number_of_slices - 1:
            x_end = image_width
        else:
            x_end = (slice_index + 1) * slice_width

        horizontal_slice = horizontal_lines[:, x_start:x_end]
        line_centers = detect_line_centers_in_slice(horizontal_slice)
        slice_line_centers.append(line_centers)

    # Keep line centers that appear in several slices.
    minimum_votes = max(3, number_of_slices // 2)
    global_line_centers = collect_global_line_centers(slice_line_centers, minimum_votes)

    # Group nearby staff lines into full staff regions.
    staff_regions = build_staff_regions_from_line_centers(
        global_line_centers,
        original_image_height,
        vertical_padding,
    )

    return staff_regions


def save_staff_debug_image(image_path, staff_regions, output_path):
    # Load the image again so we can draw colored boxes on it.
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise FileNotFoundError(f"Could not load image for debug output: {image_path}")

    # cv2.cvtColor converts the grayscale image to BGR color.
    # We need this because red rectangles cannot be drawn on a 1-channel image.
    debug_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    image_height, image_width = image.shape

    for index, (y_min, y_max) in enumerate(staff_regions, start=1):
        # cv2.rectangle draws the red box around each detected staff region.
        cv2.rectangle(
            debug_image,
            (0, y_min),
            (image_width - 1, y_max),
            (0, 0, 255),
            2,
        )

        # cv2.putText writes a small label so we know which staff is which.
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


def get_sample_image_paths(limit=10):
    # Collect a small batch of real MUSCIMA images for testing.
    image_paths = sorted(IMAGE_ROOT.glob("w-*/*.png"))
    return image_paths[:limit]


def save_batch_summary(summary_rows):
    DEBUG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(SUMMARY_CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["image", "staff_count", "staff_regions"])

        for row in summary_rows:
            writer.writerow(row)


def main():
    if not TEST_IMAGE_PATH.exists():
        print(f"Test image not found: {TEST_IMAGE_PATH}")
        return

    # Single-image test.
    staff_regions = detect_staff_lines(TEST_IMAGE_PATH)

    print(f"Image: {TEST_IMAGE_PATH}")
    print("Detected staff regions:")
    print(staff_regions)

    DEBUG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    single_debug_path = DEBUG_OUTPUT_DIR / "single_test_debug.png"
    save_staff_debug_image(TEST_IMAGE_PATH, staff_regions, single_debug_path)
    print(f"Saved single debug image to: {single_debug_path}")

    # Batch test on more images.
    sample_image_paths = get_sample_image_paths(limit=BATCH_DEBUG_LIMIT)
    summary_rows = []

    for image_path in sample_image_paths:
        staff_regions = detect_staff_lines(image_path)
        staff_count = len(staff_regions)
        image_name = f"{image_path.parent.name}/{image_path.name}"
        debug_name = f"{image_path.parent.name}_{image_path.stem}_staff_debug.png"
        debug_output_path = DEBUG_OUTPUT_DIR / debug_name

        save_staff_debug_image(image_path, staff_regions, debug_output_path)
        summary_rows.append((image_name, staff_count, staff_regions))

    save_batch_summary(summary_rows)

    print(f"Processed {len(summary_rows)} images.")
    print(f"Saved batch debug images to: {DEBUG_OUTPUT_DIR}")
    print(f"Saved summary CSV to: {SUMMARY_CSV_PATH}")


if __name__ == "__main__":
    main()
