"""Extract approximate notes from a clean sheet image and write MIDI artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from melodious_v2.omr.note_extraction import extract_notes_from_image, result_to_dict


DEFAULT_DEMO_CHECKPOINT = Path("artifacts/models/note_extraction_default_fullpage/best.pt")
DEFAULT_FINETUNE_CHECKPOINT = Path(
    "runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/"
    "ultralytics/train/weights/best.pt"
)
DEFAULT_BASE_CHECKPOINT = Path("artifacts/models/detection_136class_yolov8m_v1/best.pt")
DEFAULT_THIN_SYMBOL_CHECKPOINT = Path("artifacts/models/note_extraction_tiled_stem_pilot/best.pt")
DEFAULT_TILED_STEM_PILOT_CHECKPOINT = Path(
    "runs/detection/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/"
    "ultralytics/train/weights/best.pt"
)
DEFAULT_GNN_CHECKPOINT = Path("../outputs/gnn_checkpoint.pt")


def default_checkpoint() -> Path | None:
    """Return the stable local demo checkpoint when it exists."""
    for checkpoint in (
        DEFAULT_DEMO_CHECKPOINT,
        DEFAULT_FINETUNE_CHECKPOINT,
        DEFAULT_BASE_CHECKPOINT,
    ):
        if checkpoint.exists():
            return checkpoint
    return None


def default_thin_symbol_checkpoint() -> Path | None:
    """Return the tiled thin-symbol checkpoint when it exists."""
    for checkpoint in (
        DEFAULT_THIN_SYMBOL_CHECKPOINT,
        DEFAULT_TILED_STEM_PILOT_CHECKPOINT,
    ):
        if checkpoint.exists():
            return checkpoint
    return None


def default_gnn_checkpoint() -> Path | None:
    """Return the local legacy GNN checkpoint when it exists."""
    return DEFAULT_GNN_CHECKPOINT if DEFAULT_GNN_CHECKPOINT.exists() else None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="Input sheet image path.")
    parser.add_argument("--output-dir", required=True, help="Directory for JSON, overlay, MusicXML, and MIDI.")
    parser.add_argument(
        "--checkpoint",
        default=None,
        help="YOLO checkpoint. If omitted, the script uses the saved default local demo checkpoint when available.",
    )
    parser.add_argument("--no-yolo", action="store_true", help="Use only the CV fallback extractor.")
    parser.add_argument(
        "--no-snapshot-checkpoint",
        action="store_true",
        help="Read the checkpoint directly instead of copying a snapshot into the output directory.",
    )
    parser.add_argument(
        "--thin-symbol-checkpoint",
        default=None,
        help=(
            "Optional YOLO checkpoint for tiled stem/beam/flag/dot/accidental detection. "
            "If omitted, the saved tiled stem pilot checkpoint is used when available."
        ),
    )
    parser.add_argument(
        "--no-thin-symbols",
        action="store_true",
        help="Disable the tiled thin-symbol checkpoint pass.",
    )
    parser.add_argument(
        "--gnn-checkpoint",
        default=None,
        help=(
            "Optional GNN checkpoint for relationship-aware rhythm attachment. "
            "If omitted, ../outputs/gnn_checkpoint.pt is used when available."
        ),
    )
    parser.add_argument("--no-gnn", action="store_true", help="Disable GNN relationship assembly.")
    parser.add_argument("--conf", type=float, default=0.12, help="YOLO confidence threshold.")
    parser.add_argument("--imgsz", type=int, default=1472, help="YOLO inference image size.")
    parser.add_argument("--max-det", type=int, default=2000, help="YOLO max detections.")
    parser.add_argument("--thin-conf", type=float, default=0.05, help="Tiled thin-symbol YOLO confidence threshold.")
    parser.add_argument("--thin-imgsz", type=int, default=1024, help="Tiled thin-symbol YOLO inference image size.")
    parser.add_argument("--thin-max-det", type=int, default=1000, help="Tiled thin-symbol YOLO max detections per tile.")
    parser.add_argument("--thin-tile-size", type=int, default=384, help="Tiled thin-symbol crop size in source pixels.")
    parser.add_argument("--thin-tile-stride", type=int, default=256, help="Tiled thin-symbol crop stride in source pixels.")
    parser.add_argument(
        "--use-tiled-dots",
        action="store_true",
        help="Allow tiled augmentationDot detections to affect dotted rhythm. Off by default to avoid false dots.",
    )
    parser.add_argument("--device", default="cpu", help="YOLO device. Use cpu while training owns the GPU.")
    parser.add_argument(
        "--use-cv-dot-fallback",
        action="store_true",
        help=(
            "Also infer augmentation dots from tiny CV contours. YOLO-backed extraction leaves this off by "
            "default to avoid false dotted notes."
        ),
    )
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
    thin_symbol_checkpoint = None
    if not args.no_yolo and not args.no_thin_symbols:
        thin_symbol_checkpoint = (
            Path(args.thin_symbol_checkpoint) if args.thin_symbol_checkpoint else default_thin_symbol_checkpoint()
        )
    gnn_checkpoint = None
    if not args.no_gnn:
        gnn_checkpoint = Path(args.gnn_checkpoint) if args.gnn_checkpoint else default_gnn_checkpoint()
    result = extract_notes_from_image(
        image_path=args.image,
        output_dir=args.output_dir,
        checkpoint_path=checkpoint,
        thin_symbol_checkpoint_path=thin_symbol_checkpoint,
        gnn_checkpoint_path=gnn_checkpoint,
        snapshot_live_checkpoint=not args.no_snapshot_checkpoint,
        confidence=args.conf,
        imgsz=args.imgsz,
        max_det=args.max_det,
        thin_confidence=args.thin_conf,
        thin_imgsz=args.thin_imgsz,
        thin_max_det=args.thin_max_det,
        thin_tile_size=args.thin_tile_size,
        thin_tile_stride=args.thin_tile_stride,
        use_tiled_dots=args.use_tiled_dots,
        device=args.device,
        default_quarter_length=args.default_quarter_length,
        use_cv_fallback=True,
        use_cv_dot_fallback=True if args.use_cv_dot_fallback else None,
        title=args.title,
    )
    print(json.dumps(result_to_dict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
