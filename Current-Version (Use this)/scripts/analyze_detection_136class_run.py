"""Generate M3 detector run analysis from metrics and the fixed val manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from melodious_v2.evaluation.full_detector import sha256_file, write_detector_run_analysis, write_json
from melodious_v2.paths import PROJECT_ROOT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-dir",
        default=str(PROJECT_ROOT / "runs" / "detection" / "detection_136class_yolov8s_smoke_v1"),
    )
    parser.add_argument(
        "--split-manifest",
        default=str(PROJECT_ROOT / "runs" / "data" / "deepscores_136_manifest" / "val.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    analysis = write_detector_run_analysis(
        run_dir=run_dir,
        split_manifest=args.split_manifest,
    )
    artifacts_path = run_dir / "artifacts.json"
    if artifacts_path.exists():
        artifacts = json.loads(artifacts_path.read_text(encoding="utf-8"))
        existing_paths = {
            item.get("path")
            for item in artifacts.get("run_artifacts", [])
            if isinstance(item, dict)
        }
        for artifact_type, filename in (("analysis", "analysis.json"), ("analysis_report", "analysis.md")):
            artifact_path = (run_dir / filename).resolve().as_posix()
            if artifact_path in existing_paths:
                continue
            artifacts.setdefault("run_artifacts", []).append(
                {
                    "artifact_type": artifact_type,
                    "path": artifact_path,
                    "sha256": sha256_file(run_dir / filename),
                }
            )
        write_json(artifacts_path, artifacts)
    print(
        json.dumps(
            {
                "run_id": analysis["run_id"],
                "analysis_json": str(run_dir / "analysis.json"),
                "supported_classes": analysis["summary"]["supported_class_count"],
                "rare_classes": analysis["summary"]["rare_class_count_support_lte_10"],
                "zero_map_supported_classes": analysis["summary"]["zero_map_supported_class_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
