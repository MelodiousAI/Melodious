"""Evaluate a legacy GNN checkpoint on the fixed V2 MUSCIMA graph manifest."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from melodious_v2.assembly.legacy_gnn import (
    RELATIONSHIP_TYPES,
    LegacyGnnAdapter,
    build_muscima_page_graph,
    sha256_file,
)
from melodious_v2.contracts import MetricProvenance
from melodious_v2.metrics.classification import classification_report
from melodious_v2.reports import assert_no_cross_metric_claims, write_run_report


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ID = "graph_legacy_gnn_muscima_val_v1"


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT.parent,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _positive_confusion_counts(y_true: list[int], y_pred: list[int]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for truth, pred in zip(y_true, y_pred):
        if truth == 0 and pred == 0:
            continue
        key = f"{RELATIONSHIP_TYPES[truth]}->{RELATIONSHIP_TYPES[pred]}"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _write_graph_report(
    run_dir: Path,
    run_id: str,
    metrics: dict[str, Any],
    checkpoint_path: Path,
    checkpoint_hash: str,
    page_count: int,
) -> None:
    no_relation = metrics["no_relation"] or {}
    feature_encoder = metrics.get("feature_encoder", {})
    lines = [
        f"# Run {run_id}",
        "",
        "- Primary metric: `positive_macro_f1`",
        f"- Primary value: `{metrics['positive_macro_f1']}`",
        "- Metric distribution: `natural_candidate_edges`",
        f"- Page count: `{page_count}`",
        f"- Edge count: `{metrics['edge_count']}`",
        f"- Positive edge count: `{metrics['positive_edge_count']}`",
        f"- Checkpoint: `{checkpoint_path}`",
        f"- Checkpoint SHA256: `{checkpoint_hash}`",
        f"- Feature encoder: `{feature_encoder.get('source')}`",
        "",
        "## Separate no_relation Metrics",
        "",
        f"- precision: `{no_relation.get('precision')}`",
        f"- recall: `{no_relation.get('recall')}`",
        f"- f1: `{no_relation.get('f1')}`",
        f"- support: `{no_relation.get('support')}`",
        "",
        "## Positive Class Metrics",
        "",
        "| relationship | precision | recall | f1 | support |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in RELATIONSHIP_TYPES[1:]:
        class_metrics = metrics["per_class"][name]
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    str(class_metrics["precision"]),
                    str(class_metrics["recall"]),
                    str(class_metrics["f1"]),
                    str(class_metrics["support"]),
                ]
            )
            + " |"
        )
    report = "\n".join(lines) + "\n"
    assert_no_cross_metric_claims(report)
    (run_dir / "report.md").write_text(report, encoding="utf-8")


def evaluate(args: argparse.Namespace) -> Path:
    manifest_root = args.manifest_root.resolve()
    split_path = manifest_root / f"{args.split}.json"
    root_manifest_path = manifest_root / "manifest.json"
    checkpoint_path = args.checkpoint.resolve()
    config_path = args.config.resolve()
    run_dir = args.output_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    root_manifest = _load_json(root_manifest_path)
    split_manifest = _load_json(split_path)
    adapter = LegacyGnnAdapter(
        checkpoint_path=checkpoint_path,
        device=args.device,
        confidence_threshold=args.confidence_threshold,
        k_neighbors=args.k_neighbors,
        feature_encoder_seed=args.feature_encoder_seed,
    )

    y_true: list[int] = []
    y_pred: list[int] = []
    page_summaries: list[dict[str, Any]] = []
    skipped_pages: list[dict[str, Any]] = []

    for page in split_manifest.get("pages", []):
        source_path = Path(page["source_path"])
        if not source_path.exists():
            skipped_pages.append(
                {
                    "page_id": page.get("page_id", source_path.stem),
                    "reason": f"source XML not found: {source_path}",
                }
            )
            continue
        page_graph = build_muscima_page_graph(
            source_path,
            k_neighbors=args.k_neighbors,
            num_staffs=args.num_staffs,
        )
        prediction = adapter.predict_detections(page_graph.detections)
        if not prediction.inference_ran:
            skipped_pages.append(
                {
                    "page_id": page_graph.page_id,
                    "reason": "; ".join(prediction.warnings) or "no candidate edges",
                }
            )
            continue
        if prediction.edges != page_graph.edges:
            raise RuntimeError(f"Candidate-edge mismatch for page {page_graph.page_id}")

        y_true.extend(page_graph.edge_labels)
        y_pred.extend(prediction.predicted_labels)
        positive_count = sum(1 for label in page_graph.edge_labels if label > 0)
        page_summaries.append(
            {
                "page_id": page_graph.page_id,
                "source_path": str(source_path),
                "node_count": len(page_graph.detections),
                "skipped_node_count": page_graph.skipped_node_count,
                "edge_count": len(page_graph.edges),
                "positive_edge_count": positive_count,
                "predicted_positive_edge_count": sum(
                    1 for label in prediction.predicted_labels if label > 0
                ),
            }
        )

    if not y_true:
        raise RuntimeError("No graph edges were evaluated; check manifest paths and checkpoint.")

    report = classification_report(y_true, y_pred, RELATIONSHIP_TYPES)
    metrics: dict[str, Any] = {
        **report,
        "distribution": "natural_candidate_edges",
        "edge_count": len(y_true),
        "positive_edge_count": sum(1 for label in y_true if label > 0),
        "predicted_positive_edge_count": sum(1 for label in y_pred if label > 0),
        "page_count": len(page_summaries),
        "skipped_page_count": len(skipped_pages),
        "candidate_graph": {
            "builder": "legacy_gnn_k_nearest_plus_vertical_overlap",
            "k_neighbors": args.k_neighbors,
            "num_staffs": args.num_staffs,
            "negative_sampling": "none",
        },
        "checkpoint": {
            "path": str(checkpoint_path),
            "sha256": adapter.checkpoint_sha256,
            "epoch": adapter.checkpoint.get("epoch"),
            "config": adapter.config,
        },
        "feature_encoder": {
            "source": adapter.feature_encoder_source,
            "seed": adapter.feature_encoder_seed,
            "note": (
                "The legacy training data used a separate seeded node encoder. "
                "V2 reconstructs that encoder because the legacy checkpoint did not save it separately."
            ),
        },
        "positive_confusion_counts": _positive_confusion_counts(y_true, y_pred),
        "notes": [
            "This is the natural candidate-edge distribution for the legacy GNN graph builder.",
            "The legacy checkpoint was trained with negative subsampling, but this evaluation does not subsample negatives.",
            "The legacy 15-class GNN cannot represent every V2 detector class.",
            "The node feature encoder is reconstructed from the legacy training seed because it was not saved as a separate artifact.",
        ],
    }

    provenance = MetricProvenance(
        run_id=args.run_id,
        commit=_git_commit(),
        config_path=str(config_path.relative_to(REPO_ROOT) if config_path.is_relative_to(REPO_ROOT) else config_path),
        dataset_id=root_manifest.get("dataset_id", "muscima_graph_manifest"),
        split=args.split,
        taxonomy_id="semantic_omr_v2",
        artifact_sha256=adapter.checkpoint_sha256,
    )
    write_run_report(run_dir, provenance, metrics)
    _write_graph_report(
        run_dir=run_dir,
        run_id=args.run_id,
        metrics=metrics,
        checkpoint_path=checkpoint_path,
        checkpoint_hash=adapter.checkpoint_sha256,
        page_count=len(page_summaries),
    )

    run_manifest = {
        "run_id": args.run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_manifest": str(root_manifest_path),
        "split_manifest": str(split_path),
        "split": args.split,
        "page_summaries": page_summaries,
        "skipped_pages": skipped_pages,
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(run_manifest, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    artifacts = {
        "run_id": args.run_id,
        "checkpoint": {
            "path": str(checkpoint_path),
            "sha256": adapter.checkpoint_sha256,
        },
        "feature_encoder": {
            "source": adapter.feature_encoder_source,
            "seed": adapter.feature_encoder_seed,
        },
        "config": {
            "path": str(config_path),
            "sha256": sha256_file(config_path) if config_path.exists() else None,
            "copied_to": str(run_dir / "config.yaml"),
        },
        "metrics": str(run_dir / "metrics.json"),
        "report": str(run_dir / "report.md"),
        "manifest": str(run_dir / "manifest.json"),
    }
    (run_dir / "artifacts.json").write_text(
        json.dumps(artifacts, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    if config_path.exists():
        shutil.copyfile(config_path, run_dir / "config.yaml")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument(
        "--manifest-root",
        type=Path,
        default=REPO_ROOT / "runs" / "data" / "muscima_graph_manifest",
    )
    parser.add_argument("--split", default="val", choices=["train", "val", "holdout"])
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=REPO_ROOT.parent / "outputs" / "gnn_checkpoint.pt",
    )
    parser.add_argument("--config", type=Path, default=REPO_ROOT / "configs" / "gnn_curriculum.yaml")
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "runs" / "graph")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--k-neighbors", type=int, default=8)
    parser.add_argument("--num-staffs", type=int, default=4)
    parser.add_argument("--confidence-threshold", type=float, default=0.5)
    parser.add_argument("--feature-encoder-seed", type=int, default=42)
    args = parser.parse_args()
    run_dir = evaluate(args)
    print(f"Wrote graph evaluation run to {run_dir}")


if __name__ == "__main__":
    main()
