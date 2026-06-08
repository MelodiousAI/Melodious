"""Convert DeepScores COCO JSON into full-taxonomy YOLO labels."""

from __future__ import annotations

import argparse
import json

from melodious_v2.datasets.deepscores import write_yolo_split


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coco-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--split", required=True)
    args = parser.parse_args()

    manifest = write_yolo_split(args.coco_json, args.output_dir, args.split)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

