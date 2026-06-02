"""Extract approximate notes from a clean sheet image and write MIDI artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from melodious_v2.omr.note_extraction import extract_notes_from_image, result_to_dict


DEFAULT_FINETUNE_CHECKPOINT = Path(
    "runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/"
    "ultralytics/train/weights/best.pt"
)
DEFAULT_BASE_CHECKPOINT = Path("artifacts/models/detection_136class_yolov8m_v1/best.pt")


def default_checkpoint() -> Path | None:
    """Prefer the current fine-tune checkpoint if it exists."""
    if DEFAULT_FINETUNE_CHECKPOINT.exists():
        return DEFAULT_FINETUNE_CHECKPOINT
    if DEFAULT_BASE_CHECKPOINT.exists():
        return DEFAULT_BASE_CHECKPOINT
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="Input sheet image path.")
    parser.add_argument("--output-dir", required=True, help="Directory for JSON, overlay, MusicXML, and MIDI.")
    parser.add_argument(
        "--checkpoint",
        default=None,
        help="YOLO checkpoint. If omitted, the script uses the current fine-tune best.pt when available.",
    )
    parser.add_argument("--no-yolo", action="store_true", help="Use only the CV fallback extractor.")
    parser.add_argument(
        "--no-snapshot-checkpoint",
        action="store_true",
        help="Read the checkpoint directly instead of copying a snapshot into the output directory.",
    )
    parser.add_argument("--conf", type=float, default=0.12, help="YOLO confidence threshold.")
    parser.add_argument("--imgsz", type=int, default=1472, help="YOLO inference image size.")
    parser.add_argument("--max-det", type=int, default=2000, help="YOLO max detections.")
    parser.add_argument("--device", default="cpu", help="YOLO device. Use cpu while training owns the GPU.")
    parser.add_argument(
        "--default-quarter-length",
        type=float,
        default=1.0,
        help="Fallback rhythm length for un-beamed black noteheads. 1.0 means quarter notes.",
    )
    parser.add_argument("--title", default=None, help="MusicXML title.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checkpoint = None
    if not args.no_yolo:
        checkpoint = Path(args.checkpoint) if args.checkpoint else default_checkpoint()
    result = extract_notes_from_image(
        image_path=args.image,
        output_dir=args.output_dir,
        checkpoint_path=checkpoint,
        snapshot_live_checkpoint=not args.no_snapshot_checkpoint,
        confidence=args.conf,
        imgsz=args.imgsz,
        max_det=args.max_det,
        device=args.device,
        default_quarter_length=args.default_quarter_length,
        use_cv_fallback=True,
        title=args.title,
    )
    print(json.dumps(result_to_dict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
