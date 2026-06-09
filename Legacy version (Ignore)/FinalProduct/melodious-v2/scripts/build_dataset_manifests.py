"""Build M1 DeepScores and MUSCIMA dataset manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from melodious_v2.datasets.manifests import (
    build_deepscores_manifest_run,
    build_muscima_manifest_run,
)
from melodious_v2.paths import PROJECT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--parent-root",
        default=str(PROJECT_ROOT.parent),
        help="Legacy parent workspace containing source datasets.",
    )
    parser.add_argument(
        "--output-root",
        default=str(PROJECT_ROOT / "runs" / "data"),
        help="Generated data-manifest output root.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-deepscores", action="store_true")
    parser.add_argument("--skip-muscima", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    parent_root = Path(args.parent_root).resolve()
    output_root = Path(args.output_root).resolve()

    summaries: dict[str, object] = {}
    if not args.skip_deepscores:
        train_json = parent_root / "dataset_ds2_dense" / "deepscores_train.json"
        test_json = parent_root / "dataset_ds2_dense" / "deepscores_test.json"
        image_root = parent_root / "dataset_ds2_dense" / "images"
        missing = [path for path in (train_json, test_json, image_root) if not path.exists()]
        if missing:
            missing_text = ", ".join(path.as_posix() for path in missing)
            raise FileNotFoundError(f"DeepScores source path(s) missing: {missing_text}")

        summaries["deepscores"] = build_deepscores_manifest_run(
            train_json=train_json,
            test_json=test_json,
            image_root=image_root,
            output_dir=output_root / "deepscores_136_manifest",
            seed=args.seed,
        )

    if not args.skip_muscima:
        annotations_dir = parent_root / "data" / "muscima-pp" / "v2.0" / "data" / "annotations"
        if not annotations_dir.exists():
            raise FileNotFoundError(f"MUSCIMA annotations path missing: {annotations_dir.as_posix()}")

        summaries["muscima"] = build_muscima_manifest_run(
            annotations_dir=annotations_dir,
            output_dir=output_root / "muscima_graph_manifest",
            seed=args.seed,
        )

    print(json.dumps(summaries, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
