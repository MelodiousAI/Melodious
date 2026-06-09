"""Run the M5 end-to-end export evaluation on fixed MUSCIMA pages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from melodious_v2.contracts import MetricProvenance
from melodious_v2.evaluation.e2e_export import (
    evaluate_page_export,
    git_commit,
    load_json,
    muscima_xml_to_detector_payload,
    summarize_page_results,
    write_e2e_run_outputs,
)
from melodious_v2.utils import sha256_file


REPO_ROOT = Path(__file__).resolve().parents[1]
PARENT_ROOT = REPO_ROOT.parent
DEFAULT_RUN_ID = "e2e_muscima_holdout_xml_fixture_v1"


def _relative_config_path(config_path: Path) -> str:
    try:
        return str(config_path.relative_to(REPO_ROOT))
    except ValueError:
        return str(config_path)


def run(args: argparse.Namespace) -> Path:
    manifest_root = args.manifest_root.resolve()
    root_manifest_path = manifest_root / "manifest.json"
    split_manifest_path = manifest_root / f"{args.split}.json"
    root_manifest = load_json(root_manifest_path)
    split_manifest = load_json(split_manifest_path)

    checkpoint_path = args.gnn_checkpoint.resolve() if args.gnn_checkpoint else None
    run_dir = args.output_root / args.run_id
    exports_dir = run_dir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)

    page_results = []
    for page in split_manifest.get("pages", []):
        source_xml = Path(page["source_path"])
        payload, payload_summary = muscima_xml_to_detector_payload(
            source_xml,
            run_id=args.run_id,
            page_id=page["page_id"],
        )
        page_results.append(
            evaluate_page_export(
                payload=payload,
                payload_summary=payload_summary,
                page_dir=exports_dir / page["page_id"],
                requested_assembly_mode=args.assembly_mode,
                checkpoint_path=checkpoint_path,
            )
        )

    metrics = summarize_page_results(page_results)
    upstream_artifacts: dict[str, Any] = {
        "detector_source": {
            "mode": "muscima_xml_ground_truth_payload_fixture",
            "note": "No trained uploaded-image detector inference is claimed by this run.",
        }
    }
    if args.detector_metrics.exists():
        detector_metrics = load_json(args.detector_metrics)
        upstream_artifacts["detector_metrics"] = {
            "path": str(args.detector_metrics.resolve()),
            "run_id": detector_metrics.get("provenance", {}).get("run_id"),
            "artifact_sha256": detector_metrics.get("provenance", {}).get("artifact_sha256"),
        }
    if args.graph_metrics.exists():
        graph_metrics = load_json(args.graph_metrics)
        upstream_artifacts["graph_metrics"] = {
            "path": str(args.graph_metrics.resolve()),
            "run_id": graph_metrics.get("provenance", {}).get("run_id"),
            "artifact_sha256": graph_metrics.get("provenance", {}).get("artifact_sha256"),
        }
    if checkpoint_path and checkpoint_path.exists():
        upstream_artifacts["gnn_checkpoint"] = {
            "path": str(checkpoint_path),
            "sha256": sha256_file(checkpoint_path),
        }

    provenance = MetricProvenance(
        run_id=args.run_id,
        commit=git_commit(PARENT_ROOT),
        config_path=_relative_config_path(args.config.resolve()),
        dataset_id=root_manifest.get("dataset_id", "muscima_graph_manifest"),
        split=args.split,
        taxonomy_id="deepscores_136_to_semantic_omr_v2",
        artifact_sha256=upstream_artifacts.get("gnn_checkpoint", {}).get("sha256"),
    )
    write_e2e_run_outputs(
        run_dir=run_dir,
        provenance=provenance,
        metrics=metrics,
        page_results=page_results,
        source_manifest_path=root_manifest_path,
        split_manifest_path=split_manifest_path,
        config_path=args.config.resolve(),
        upstream_artifacts=upstream_artifacts,
    )
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument(
        "--manifest-root",
        type=Path,
        default=REPO_ROOT / "runs" / "data" / "muscima_graph_manifest",
    )
    parser.add_argument("--split", default="holdout", choices=["train", "val", "holdout"])
    parser.add_argument(
        "--gnn-checkpoint",
        type=Path,
        default=PARENT_ROOT / "outputs" / "gnn_checkpoint.pt",
    )
    parser.add_argument(
        "--detector-metrics",
        type=Path,
        default=REPO_ROOT / "runs" / "detection" / "detection_136class_yolov8m_v1" / "metrics.json",
    )
    parser.add_argument(
        "--graph-metrics",
        type=Path,
        default=REPO_ROOT / "runs" / "graph" / "graph_legacy_gnn_muscima_val_v1" / "metrics.json",
    )
    parser.add_argument("--assembly-mode", default="gnn", choices=["auto", "heuristic", "gnn"])
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "configs" / "e2e_muscima_holdout.yaml")
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "runs" / "e2e")
    args = parser.parse_args()
    run_dir = run(args)
    print(f"Wrote end-to-end export evaluation run to {run_dir}")


if __name__ == "__main__":
    main()
