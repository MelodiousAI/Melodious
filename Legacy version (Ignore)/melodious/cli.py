"""End-to-end CLI: image → detection → MusicXML / MIDI.

Usage examples
--------------
    # Full pipeline (requires a trained checkpoint)
    python -m melodious.cli --input score.jpg --output score.mid

    # Export from existing detection JSON
    python -m melodious.cli --payload detections.json --output score.mid

    # Specify model type
    python -m melodious.cli --input score.jpg --model yolov8 --checkpoint runs/best.pt --output result.musicxml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional


def _detect(
    image_path: str,
    model_type: str,
    checkpoint: str,
    conf_thresh: float,
    device: str,
) -> Dict:
    """Run detection pipeline on a single image."""
    from .pipeline import DetectionPipeline

    pipe = DetectionPipeline(
        model_type=model_type,
        checkpoint=checkpoint,
        conf_thresh=conf_thresh,
        device=device,
    )
    return pipe.predict(image_path)


def _export(payload: Dict, output_path: str, title: Optional[str] = None) -> Path:
    """Export a payload to MusicXML or MIDI based on file extension."""
    from .musicxml_export import payload_to_midi, payload_to_musicxml

    ext = Path(output_path).suffix.lower()
    if ext in {".mid", ".midi"}:
        return payload_to_midi(payload, output_path, title=title)
    elif ext in {".musicxml", ".xml", ".mxl"}:
        return payload_to_musicxml(payload, output_path, title=title)
    else:
        print(f"Unknown extension '{ext}', defaulting to MIDI.", file=sys.stderr)
        return payload_to_midi(payload, output_path, title=title)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="melodious",
        description="Melodious OMR: image → sheet music detection → MusicXML / MIDI",
    )

    # Input options (one of these is required)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input", "-i",
        type=str,
        help="Path to a sheet music image (runs full detection pipeline)",
    )
    input_group.add_argument(
        "--payload", "-p",
        type=str,
        help="Path to an existing detection payload JSON (skips detection)",
    )

    # Output
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Output file path (.mid/.midi for MIDI, .musicxml/.xml for MusicXML)",
    )

    # Detection options
    parser.add_argument("--model", type=str, default="custom", choices=["custom", "yolov8"],
                        help="Detector model type (default: custom)")
    parser.add_argument("--checkpoint", "-c", type=str, default=None,
                        help="Path to model checkpoint (required for --input)")
    parser.add_argument("--conf", type=float, default=0.3,
                        help="Confidence threshold for detection (default: 0.3)")
    parser.add_argument("--device", type=str, default=None,
                        help="Device: cuda or cpu (auto-detected if omitted)")

    # Export options
    parser.add_argument("--title", type=str, default=None,
                        help="Score title for the exported file")
    parser.add_argument("--save-payload", type=str, default=None,
                        help="Also save the detection payload JSON to this path")

    args = parser.parse_args()

    # Resolve device
    if args.device is None:
        import torch
        args.device = "cuda" if torch.cuda.is_available() else "cpu"

    # Stage 1: Get detection payload
    if args.input:
        if args.checkpoint is None:
            parser.error("--checkpoint is required when using --input (detection mode)")
        print(f"Running detection on: {args.input}")
        payload = _detect(
            image_path=args.input,
            model_type=args.model,
            checkpoint=args.checkpoint,
            conf_thresh=args.conf,
            device=args.device,
        )
        n_dets = len(payload.get("detections", []))
        print(f"Detected {n_dets} symbols.")
    else:
        payload_path = Path(args.payload)
        with payload_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        n_dets = len(payload.get("detections", []))
        print(f"Loaded {n_dets} detections from: {payload_path}")

    # Optionally save the payload
    if args.save_payload:
        out_p = Path(args.save_payload)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with out_p.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"Saved payload: {out_p}")

    # Stage 2: Export to MusicXML / MIDI
    title = args.title or Path(args.input or args.payload).stem
    out = _export(payload, args.output, title=title)
    print(f"Exported: {out}")


if __name__ == "__main__":
    main()
