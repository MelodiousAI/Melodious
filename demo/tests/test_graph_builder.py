from pathlib import Path
import csv
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from staff_detection import IMAGE_ROOT, detect_staff_lines, save_staff_debug_image

DEBUG_OUTPUT_DIR = PROJECT_ROOT / "tests" / "staff_debug_sample"
SUMMARY_CSV_PATH = DEBUG_OUTPUT_DIR / "staff_debug_summary.csv"
BATCH_DEBUG_LIMIT = 100
TEST_IMAGE_PATH = IMAGE_ROOT / "w-01" / "p010.png"


def get_sample_image_paths(limit=10):
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

    staff_regions = detect_staff_lines(TEST_IMAGE_PATH)

    print(f"Image: {TEST_IMAGE_PATH}")
    print("Detected staff regions:")
    print(staff_regions)

    DEBUG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    single_debug_path = DEBUG_OUTPUT_DIR / "single_test_debug.png"
    save_staff_debug_image(TEST_IMAGE_PATH, staff_regions, single_debug_path)
    print(f"Saved single debug image to: {single_debug_path}")

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
