from pathlib import Path
import csv

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = PROJECT_ROOT / "data" / "raw" / "Images" / "PNG_GT_Gray"
DEBUG_OUTPUT_DIR = PROJECT_ROOT / "tests" / "staff_debug"
SUMMARY_CSV_PATH = DEBUG_OUTPUT_DIR / "staff_debug_summary.csv"
SUSPICIOUS_TXT_PATH = DEBUG_OUTPUT_DIR / "suspicious_images.txt"
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
    # This helper puts nearby y-values into the same group.
    # Example: [100, 101, 103, 150, 151] becomes [[100, 101, 103], [150, 151]]
    if not values:
        return []

    groups = [[values[0]]]

    for value in values[1:]:
        if value - groups[-1][-1] <= max_gap:
            groups[-1].append(value)
        else:
            groups.append([value])

    return groups


def detect_staff_lines(image_path):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # `cv2.imread(..., cv2.IMREAD_GRAYSCALE)` loads the image as one channel
    # instead of a 3-channel color image.
    grayscale_image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if grayscale_image is None:
        raise ValueError(f"Could not read image: {image_path}")

    original_image_height = grayscale_image.shape[0]

    # `cv2.copyMakeBorder(...)` adds a white border around the image.
    # This helps when a staff is very close to the top or bottom edge.
    vertical_padding = 40
    grayscale_image = cv2.copyMakeBorder(
        grayscale_image,
        vertical_padding,
        vertical_padding,
        0,
        0,
        cv2.BORDER_CONSTANT,
        value=255,
    )

    # `cv2.GaussianBlur(...)` lightly smooths the image to reduce small noise.
    blurred_image = cv2.GaussianBlur(grayscale_image, (3, 3), 0)

    # `cv2.threshold(...)` converts the grayscale image into black/white.
    # `cv2.THRESH_BINARY_INV` makes dark staff lines become white pixels.
    # `cv2.THRESH_OTSU` automatically picks a threshold value for us.
    _, binary_image = cv2.threshold(
        blurred_image,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    image_height, image_width = binary_image.shape

    # `cv2.getStructuringElement(...)` creates a horizontal rectangle kernel.
    # A wide and short kernel helps us keep horizontal lines.
    horizontal_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (max(25, image_width // 15), 1),
    )

    # `cv2.morphologyEx(..., cv2.MORPH_OPEN, kernel)` keeps long horizontal
    # shapes and removes many small non-horizontal blobs.
    horizontal_lines_image = cv2.morphologyEx(
        binary_image,
        cv2.MORPH_OPEN,
        horizontal_kernel,
    )

    # Count how many white pixels appear in each row.
    # Rows with many white pixels are likely to contain staff lines.
    row_white_pixel_counts = np.count_nonzero(horizontal_lines_image, axis=1)

    # Instead of requiring a fixed fraction of the full image width,
    # use the strongest detected horizontal row in this image as a reference.
    # This is simpler and works better when staff lines do not span the full page width.
    maximum_row_response = int(row_white_pixel_counts.max())
    minimum_pixels_for_line = max(25, int(maximum_row_response * 0.40))

    candidate_line_rows = []
    for y, white_pixel_count in enumerate(row_white_pixel_counts):
        if white_pixel_count >= minimum_pixels_for_line:
            candidate_line_rows.append(y)

    if not candidate_line_rows:
        return []

    # Merge rows that belong to the same physical line.
    raw_line_groups = group_nearby_values(candidate_line_rows, max_gap=2)

    line_centers = []
    for group in raw_line_groups:
        line_center = int(round(sum(group) / len(group)))
        line_centers.append(line_center)

    if not line_centers:
        return []

    # Staff lines inside the same staff are close together.
    # We estimate a typical line spacing from the detected line centers.
    if len(line_centers) > 1:
        line_gaps = np.diff(line_centers)
        typical_gap = int(np.median(line_gaps))
    else:
        typical_gap = 10

    if typical_gap < 1:
        typical_gap = 10

    # Lines separated by a small gap belong to the same staff.
    staff_line_groups = group_nearby_values(
        line_centers,
        max_gap=max(12, typical_gap * 2),
    )

    staff_regions = []
    region_padding = max(5, typical_gap)
    original_top_in_padded_image = vertical_padding
    original_bottom_in_padded_image = vertical_padding + original_image_height - 1

    for group in staff_line_groups:
        # Real music staves usually contain 5 staff lines.
        # Keeping groups with at least 4 lines helps reject small false detections.
        # Near the image edges, a real staff may lose one line, so allow 3 there.
        near_top_edge = group[0] <= original_top_in_padded_image + (typical_gap * 2)
        near_bottom_edge = group[-1] >= original_bottom_in_padded_image - (typical_gap * 2)

        if len(group) < 4 and not (len(group) >= 3 and (near_top_edge or near_bottom_edge)):
            continue

        y_min = max(0, group[0] - region_padding - vertical_padding)
        y_max = min(original_image_height - 1, group[-1] + region_padding - vertical_padding)
        staff_regions.append((y_min, y_max))

    return staff_regions


def save_staff_debug_image(image_path, staff_regions, output_path):
    image_path = Path(image_path)
    output_path = Path(output_path)

    # `cv2.imread(...)` loads the image.
    # Here we load the original grayscale image so we can draw the detected regions on it.
    grayscale_image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if grayscale_image is None:
        raise ValueError(f"Could not read image: {image_path}")

    # `cv2.cvtColor(...)` converts the grayscale image into a 3-channel image.
    # We do this because colored drawing functions need 3 channels.
    debug_image = cv2.cvtColor(grayscale_image, cv2.COLOR_GRAY2BGR)

    image_width = debug_image.shape[1]

    for index, (y_min, y_max) in enumerate(staff_regions, start=1):
        # `cv2.rectangle(...)` draws a rectangle around one detected staff region.
        cv2.rectangle(debug_image, (0, y_min), (image_width - 1, y_max), (0, 0, 255), 2)

        # `cv2.putText(...)` writes a small label on the image.
        cv2.putText(
            debug_image,
            f"staff {index}",
            (10, max(20, y_min - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), debug_image)


def get_sample_image_paths(limit=10):
    # `rglob("*.png")` finds PNG images inside all writer folders.
    all_image_paths = sorted(IMAGE_ROOT.rglob("*.png"))
    return all_image_paths[:limit]


def is_suspicious_staff_count(staff_count):
    # These simple rules help us focus on images that may need manual review first.
    if staff_count == 0:
        return True

    if staff_count < 4:
        return True

    if staff_count > 8:
        return True

    return False


def save_batch_summary(summary_rows):
    DEBUG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(SUMMARY_CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["image_path", "staff_count", "staff_regions", "suspicious"])

        for row in summary_rows:
            writer.writerow(
                [
                    row["image_path"],
                    row["staff_count"],
                    row["staff_regions"],
                    row["suspicious"],
                ]
            )

    with open(SUSPICIOUS_TXT_PATH, "w", encoding="utf-8") as text_file:
        text_file.write("Suspicious staff detections\n")
        text_file.write("==========================\n\n")

        suspicious_rows = [row for row in summary_rows if row["suspicious"]]

        if not suspicious_rows:
            text_file.write("No suspicious images found.\n")
        else:
            for row in suspicious_rows:
                text_file.write(f"{row['image_path']}\n")
                text_file.write(f"staff_count = {row['staff_count']}\n")
                text_file.write(f"staff_regions = {row['staff_regions']}\n\n")


if __name__ == "__main__":
    if not TEST_IMAGE_PATH.exists():
        print(f"Test image not found: {TEST_IMAGE_PATH}")
    else:
        detected_staff_regions = detect_staff_lines(TEST_IMAGE_PATH)
        print(f"Image: {TEST_IMAGE_PATH}")
        print("Detected staff regions:")
        print(detected_staff_regions)

        single_output_path = DEBUG_OUTPUT_DIR / "single_test_debug.png"
        save_staff_debug_image(TEST_IMAGE_PATH, detected_staff_regions, single_output_path)
        print(f"Saved single debug image to: {single_output_path}")

        print()
        print("Saving batch debug images...")

        sample_image_paths = get_sample_image_paths(limit=BATCH_DEBUG_LIMIT)
        summary_rows = []

        for image_path in sample_image_paths:
            staff_regions = detect_staff_lines(image_path)
            staff_count = len(staff_regions)
            suspicious = is_suspicious_staff_count(staff_count)
            writer_folder = image_path.parent.name
            output_filename = f"{writer_folder}_{image_path.stem}_staff_debug.png"
            output_path = DEBUG_OUTPUT_DIR / output_filename

            save_staff_debug_image(image_path, staff_regions, output_path)

            summary_rows.append(
                {
                    "image_path": str(image_path),
                    "staff_count": staff_count,
                    "staff_regions": staff_regions,
                    "suspicious": suspicious,
                }
            )

            print(f"{image_path} -> {staff_count} staff regions")
            print(f"Saved: {output_path}")
            if suspicious:
                print("Flagged as suspicious for manual review.")

        save_batch_summary(summary_rows)

        suspicious_count = sum(row["suspicious"] for row in summary_rows)

        print()
        print(f"Saved batch summary to: {SUMMARY_CSV_PATH}")
        print(f"Saved suspicious image list to: {SUSPICIOUS_TXT_PATH}")
        print(f"Processed {len(summary_rows)} images.")
        print(f"Suspicious images: {suspicious_count}")
