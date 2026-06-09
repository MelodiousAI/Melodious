"""Audit detector class coverage across splits and optional metric output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from melodious_v2.evaluation.class_coverage import (
    build_class_coverage_audit,
    write_class_coverage_report,
)
from melodious_v2.paths import PROJECT_ROOT, RUNS_DIR


DEFAULT_METRICS = (
    RUNS_DIR
    / "detection"
    / "detection_136class_yolov8m_eval_img1472_maxdet2000_v1"
    / "metrics.json"
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest-dir",
        default=str(PROJECT_ROOT / "runs" / "data" / "deepscores_136_manifest"),
        help="Directory containing train.json, val.json, and test.json manifests.",
    )
    parser.add_argument(
        "--metrics",
        default=str(DEFAULT_METRICS),
        help="Optional detector metrics.json to join with split support.",
    )
    parser.add_argument(
        "--evaluation-split",
        default="val",
        choices=["train", "val", "test"],
        help="Split used to decide which per-class metric values are applicable.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(RUNS_DIR / "detection" / "detection_136class_class_coverage_audit_v1"),
        help="Ignored run directory for class_coverage.json and class_coverage.md.",
    )
    parser.add_argument(
        "--rare-threshold",
        type=int,
        default=10,
        help="Support threshold for rare evaluated classes.",
    )
    parser.add_argument(
        "--high-support-threshold",
        type=int,
        default=100,
        help="Support threshold for high-support zero-map classes.",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    metrics_path = Path(args.metrics) if args.metrics else None
    audit = build_class_coverage_audit(
        manifest_dir=args.manifest_dir,
        metrics_path=metrics_path,
        evaluation_split=args.evaluation_split,
        rare_threshold=args.rare_threshold,
        high_support_threshold=args.high_support_threshold,
    )
    outputs = write_class_coverage_report(audit=audit, output_dir=args.output_dir)
    print(
        json.dumps(
            {
                "outputs": outputs,
                "summary": audit["summary"],
            },
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )


if __name__ == "__main__":
    main()
