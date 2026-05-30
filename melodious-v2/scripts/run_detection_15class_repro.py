"""Run the M2 legacy 15-class detector metric reproduction."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from melodious_v2.evaluation.reduced_detection import write_reduced_repro_run
from melodious_v2.paths import PROJECT_ROOT


DEFAULT_RUN_ID = "detection_15class_repro_sample_v1"


def git_commit() -> str:
    """Return the current Git commit hash, or `unknown` outside Git."""
    try:
        return subprocess.check_output(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parent_root = PROJECT_ROOT.parent
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--parent-root", default=str(parent_root))
    parser.add_argument("--config", default=str(PROJECT_ROOT / "configs" / "detection_15class_repro.yaml"))
    parser.add_argument(
        "--predictions-dir",
        default=str(parent_root / "sample_detections" / "model_outputs_quick"),
    )
    parser.add_argument(
        "--train-json",
        default=str(parent_root / "dataset_ds2_dense" / "deepscores_train.json"),
    )
    parser.add_argument(
        "--test-json",
        default=str(parent_root / "dataset_ds2_dense" / "deepscores_test.json"),
    )
    parser.add_argument(
        "--checkpoint",
        default=str(parent_root / "outputs" / "yolov8_runs" / "train" / "weights" / "best.pt"),
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "runs" / "detection" / DEFAULT_RUN_ID),
    )
    parser.add_argument("--commit", default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = write_reduced_repro_run(
        run_dir=args.output_dir,
        run_id=args.run_id,
        config_path=args.config,
        predictions_dir=args.predictions_dir,
        train_json=args.train_json,
        test_json=args.test_json,
        checkpoint_path=args.checkpoint,
        commit=args.commit or git_commit(),
    )
    summary = {
        "run_id": args.run_id,
        "run_dir": str(Path(args.output_dir).resolve()),
        "primary_metric": result["metrics"]["primary_metric"],
        "primary_value": result["metrics"][result["metrics"]["primary_metric"]],
        "image_count": result["manifest"]["image_count"],
        "prediction_count": result["manifest"]["prediction_count"],
        "target_count": result["manifest"]["target_count"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
