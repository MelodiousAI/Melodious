"""Export MUSCIMA++ XML annotations as detection payload JSON files."""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path


MUSCIMA_TO_CLASS = {
    "noteheadFull": (0, "notehead-full"),
    "noteheadHalf": (1, "notehead-half"),
    "noteheadWhole": (2, "notehead-whole"),
    "gClef": (3, "clefG"),
    "fClef": (4, "clefF"),
    "cClef": (5, "clefC"),
    "rest8th": (6, "rest-8th"),
    "restQuarter": (7, "rest-quarter"),
    "restHalf": (8, "rest-half"),
    "restWhole": (9, "rest-whole"),
    "accidentalSharp": (10, "accidentalSharp"),
    "accidentalFlat": (11, "accidentalFlat"),
    "accidentalNatural": (12, "accidentalNatural"),
    "beam": (13, "beam"),
    "stem": (14, "stem"),
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_XML_DIR = PROJECT_ROOT / "sample_detections" / "muscima_xml"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "sample_detections" / "muscima_reference"


def estimate_page_size(xml_path: Path) -> tuple[int, int]:
    """Estimate image dimensions from annotation extents plus small padding."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    max_x = 0
    max_y = 0

    for node in root.findall("Node"):
        top = int(node.find("Top").text)
        left = int(node.find("Left").text)
        width = int(node.find("Width").text)
        height = int(node.find("Height").text)
        max_x = max(max_x, left + width)
        max_y = max(max_y, top + height)

    return int(max_x * 1.05), int(max_y * 1.05)


def build_detection_record(class_id: int, class_name: str, xyxy: list[float], image_width: int, image_height: int) -> dict:
    """Build one detection record in the agreed JSON contract."""
    x1, y1, x2, y2 = xyxy
    width = x2 - x1
    height = y2 - y1
    x_center = x1 + (width / 2.0)
    y_center = y1 + (height / 2.0)
    return {
        "class_id": class_id,
        "class_name": class_name,
        "confidence": 1.0,
        "bbox": {
            "x_center": x_center / image_width,
            "y_center": y_center / image_height,
            "width": width / image_width,
            "height": height / image_height,
        },
        "bbox_pixels": {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
        },
    }


def build_detection_payload(image_path: str, image_width: int, image_height: int, detections: list[dict]) -> dict:
    """Build the top-level detection payload."""
    return {
        "image_path": image_path,
        "image_size": {"width": image_width, "height": image_height},
        "model": {"type": "reference-ground-truth", "checkpoint": None},
        "detections": detections,
    }


def parse_muscima_xml(xml_path: Path, image_path: str, page_width: int, page_height: int) -> tuple[dict, int, int]:
    """Convert one MUSCIMA XML file into the shared detector payload format."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    detections = []
    skipped = 0

    for node in root.findall("Node"):
        class_name = node.find("ClassName").text

        if class_name not in MUSCIMA_TO_CLASS:
            skipped += 1
            continue

        class_id, detector_class_name = MUSCIMA_TO_CLASS[class_name]
        top = int(node.find("Top").text)
        left = int(node.find("Left").text)
        width = int(node.find("Width").text)
        height = int(node.find("Height").text)
        record = build_detection_record(
            class_id=class_id,
            class_name=detector_class_name,
            xyxy=[float(left), float(top), float(left + width), float(top + height)],
            image_width=page_width,
            image_height=page_height,
        )
        detections.append(record)

    payload = build_detection_payload(
        image_path=image_path,
        image_width=page_width,
        image_height=page_height,
        detections=detections,
    )
    return payload, len(detections), skipped


def save_detection_payload(payload: dict, output_path: Path) -> None:
    """Save one detection payload as JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_cli_args():
    """Parse command-line arguments for MUSCIMA payload export."""
    parser = argparse.ArgumentParser(description="Export MUSCIMA XML files as detector payload JSONs.")
    parser.add_argument("--xml-dir", type=Path, default=DEFAULT_XML_DIR, help="Directory containing MUSCIMA XML files.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory to write payload JSON files.")
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=None,
        help="Optional directory to use in payload image_path fields. Defaults to --xml-dir.",
    )
    return parser.parse_args()


def main() -> None:
    """Export all XML files in a directory into detector payload JSONs."""
    args = parse_cli_args()
    xml_files = sorted(args.xml_dir.glob("*.xml"))

    if not xml_files:
        raise FileNotFoundError(f"No XML files found in {args.xml_dir}")

    image_dir = args.image_dir or args.xml_dir
    args.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Exporting {len(xml_files)} MUSCIMA pages to {args.output_dir}")

    for xml_path in xml_files:
        page_width, page_height = estimate_page_size(xml_path)
        payload, kept_count, skipped_count = parse_muscima_xml(
            xml_path=xml_path,
            image_path=str(image_dir / f"{xml_path.stem}.png"),
            page_width=page_width,
            page_height=page_height,
        )
        output_path = args.output_dir / f"{xml_path.stem}.json"
        save_detection_payload(payload, output_path)
        print(
            f"  {xml_path.name}: {kept_count} detections kept, "
            f"{skipped_count} skipped -> {output_path.name}"
        )


if __name__ == "__main__":
    main()
