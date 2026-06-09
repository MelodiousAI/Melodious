"""
Export MUSCIMA++ XML annotations as detection payloads in the agreed JSON contract.

Produces reference-ground-truth payloads (confidence=1.0) for MUSCIMA++ pages,
using only the 15 classes shared with our DeepScores detector.

Usage:
    python -m melodious.export_muscima_detections \
        --xml-dir MUSICMA_Sample \
        --output-dir sample_detections/muscima_reference
"""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional

from .detection_contract import build_detection_payload, build_detection_record, save_detection_payload


# MUSCIMA++ class name → our detector class ID (15-class schema)
# Classes not in this map are not in our shared schema and are skipped.
MUSCIMA_TO_CLASS_ID: Dict[str, int] = {
    "noteheadFull":       0,  # notehead-full
    "noteheadHalf":       1,  # notehead-half
    "noteheadWhole":      2,  # notehead-whole
    "gClef":              3,  # clefG
    "fClef":              4,  # clefF
    "cClef":              5,  # clefC
    "rest8th":            6,  # rest-8th
    "restQuarter":        7,  # rest-quarter
    "restHalf":           8,  # rest-half
    "restWhole":          9,  # rest-whole
    "accidentalSharp":   10,  # accidentalSharp
    "accidentalFlat":    11,  # accidentalFlat
    "accidentalNatural": 12,  # accidentalNatural
    "beam":              13,  # beam
    "stem":              14,  # stem
}


def estimate_page_size(xml_path: Path) -> tuple[int, int]:
    """Estimate image dimensions from the maximum annotation extent + 5% padding."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    max_x, max_y = 0, 0
    for node in root.findall("Node"):
        top = int(node.find("Top").text)
        left = int(node.find("Left").text)
        width = int(node.find("Width").text)
        height = int(node.find("Height").text)
        max_x = max(max_x, left + width)
        max_y = max(max_y, top + height)
    # Add 5% padding so normalized coords never reach exactly 1.0
    page_width = int(max_x * 1.05)
    page_height = int(max_y * 1.05)
    return page_width, page_height


def parse_muscima_xml(
    xml_path: Path,
    image_path: str,
    page_width: int,
    page_height: int,
) -> dict:
    """Parse one MUSCIMA++ XML file into a detection payload."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    records = []
    skipped = 0
    for node in root.findall("Node"):
        class_name = node.find("ClassName").text
        if class_name not in MUSCIMA_TO_CLASS_ID:
            skipped += 1
            continue

        class_id = MUSCIMA_TO_CLASS_ID[class_name]
        top = int(node.find("Top").text)
        left = int(node.find("Left").text)
        width = int(node.find("Width").text)
        height = int(node.find("Height").text)

        # Convert top-left + size to xyxy pixel coords
        x1, y1 = float(left), float(top)
        x2, y2 = float(left + width), float(top + height)

        record = build_detection_record(
            class_id=class_id,
            confidence=1.0,
            xyxy=[x1, y1, x2, y2],
            image_width=page_width,
            image_height=page_height,
        )
        records.append(record)

    payload = build_detection_payload(
        image_path=image_path,
        image_width=page_width,
        image_height=page_height,
        detections=records,
        model_type="reference-ground-truth",
        checkpoint=None,
    )
    return payload, len(records), skipped


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export MUSCIMA++ XML annotations as detection contract JSONs."
    )
    parser.add_argument(
        "--xml-dir",
        type=Path,
        default=Path("MUSICMA_Sample"),
        help="Directory containing MUSCIMA++ .xml files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("sample_detections/muscima_reference"),
        help="Output directory for JSON files",
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=None,
        help="Optional: directory where matching .png images would live. "
             "Used to set image_path in the payload. Defaults to --xml-dir.",
    )
    args = parser.parse_args()

    image_dir = args.image_dir or args.xml_dir
    xml_files = sorted(args.xml_dir.glob("*.xml"))

    if not xml_files:
        raise FileNotFoundError(f"No XML files found in {args.xml_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Exporting {len(xml_files)} MUSCIMA++ pages → {args.output_dir}")
    for xml_path in xml_files:
        page_width, page_height = estimate_page_size(xml_path)
        image_path = str(image_dir / (xml_path.stem + ".png"))

        payload, kept, skipped = parse_muscima_xml(
            xml_path=xml_path,
            image_path=image_path,
            page_width=page_width,
            page_height=page_height,
        )

        out_path = args.output_dir / (xml_path.stem + ".json")
        save_detection_payload(payload, out_path)

        print(
            f"  {xml_path.name}: {kept} detections kept, "
            f"{skipped} skipped (outside 15-class schema) → {out_path.name}"
        )


if __name__ == "__main__":
    main()
