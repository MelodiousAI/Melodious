"""Evaluate a deterministic non-graph relationship baseline on MUSCIMA.

This is the graph-rubric comparison run: it uses the same fixed MUSCIMA split
and the same candidate edge list as the legacy GNN evaluation, but predicts
relationships with local geometry rules only. It therefore tests what the graph
model adds beyond a flat nearest-neighbor/proximity baseline.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from melodious_v2.assembly.legacy_gnn import (
    RELATIONSHIP_TYPES,
    build_muscima_page_graph,
)
from melodious_v2.contracts import MetricProvenance
from melodious_v2.metrics.classification import classification_report
from melodious_v2.reports import assert_no_cross_metric_claims, write_run_report


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ID = "graph_non_graph_heuristic_muscima_val_v1"
NOTEHEAD_CLASS_IDS = {0, 1, 2}
BEAM_CLASS_ID = 13
STEM_CLASS_ID = 14


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


def _vertical_overlap(a_y: float, a_h: float, b_y: float, b_h: float) -> float:
    a_min = a_y - a_h / 2
    a_max = a_y + a_h / 2
    b_min = b_y - b_h / 2
    b_max = b_y + b_h / 2
    return max(0.0, min(a_max, b_max) - max(a_min, b_min))


def _predict_edge(detections: list[Any], edge: tuple[int, int]) -> int:
    """Predict one legacy relationship label using only local geometry."""
    src = detections[edge[0]]
    tgt = detections[edge[1]]
    class_pair = {src.class_id, tgt.class_id}
    dx = abs(src.x - tgt.x)
    dy = abs(src.y - tgt.y)
    overlap = _vertical_overlap(src.y, src.h, tgt.y, tgt.h)

    if STEM_CLASS_ID in class_pair and class_pair & NOTEHEAD_CLASS_IDS:
        if dx <= 0.055 and (dy <= 0.13 or overlap > 0):
            return 1

    if BEAM_CLASS_ID in class_pair and class_pair & NOTEHEAD_CLASS_IDS:
        if dx <= 0.14 and dy <= 0.10:
            return 2

    return 0


def _write_report(run_dir: Path, run_id: str, metrics: dict[str, Any]) -> None:
    lines = [
        f"# Run {run_id}",
        "",
        "- Baseline: deterministic non-graph geometry rules",
        "- Input parity: same MUSCIMA split and same candidate edges as the GNN graph evaluation",
        "- Primary metric: `positive_macro_f1`",
        f"- Primary value: `{metrics['positive_macro_f1']}`",
        f"- Edge count: `{metrics['edge_count']}`",
        f"- Positive edge count: `{metrics['positive_edge_count']}`",
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
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This baseline does not perform message passing, attention, or learned edge classification.",
            "It only checks local spatial proximity between noteheads, stems, and beams.",
            "It is the required non-graph comparison for the graph-based project rubric.",
        ]
    )
    report = "\n".join(lines) + "\n"
    assert_no_cross_metric_claims(report)
    (run_dir / "report.md").write_text(report, encoding="utf-8")


def evaluate(args: argparse.Namespace) -> Path:
    manifest_root = args.manifest_root.resolve()
    split_path = manifest_root / f"{args.split}.json"
    root_manifest_path = manifest_root / "manifest.json"
    root_manifest = _load_json(root_manifest_path)
    split_manifest = _load_json(split_path)
    run_dir = args.output_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

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
        predictions = [_predict_edge(page_graph.detections, edge) for edge in page_graph.edges]
        y_true.extend(page_graph.edge_labels)
        y_pred.extend(predictions)
        page_summaries.append(
            {
                "page_id": page_graph.page_id,
                "source_path": str(source_path),
                "node_count": len(page_graph.detections),
                "edge_count": len(page_graph.edges),
                "positive_edge_count": sum(1 for label in page_graph.edge_labels if label > 0),
                "predicted_positive_edge_count": sum(1 for label in predictions if label > 0),
            }
        )

    if not y_true:
        raise RuntimeError("No graph edges were evaluated; check manifest paths.")

    metrics: dict[str, Any] = {
        **classification_report(y_true, y_pred, RELATIONSHIP_TYPES),
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
        "baseline": {
            "name": "non_graph_geometry_rules_v1",
            "uses_message_passing": False,
            "uses_learned_edge_classifier": False,
            "input_parity": "same_candidate_edges_as_graph_legacy_gnn_muscima_val_v1",
        },
        "positive_confusion_counts": _positive_confusion_counts(y_true, y_pred),
        "notes": [
            "This is a deterministic non-graph baseline on the same candidate edges as the GNN.",
            "It uses only local class pair and bbox geometry rules.",
            "It is intended for TM10G graph-vs-non-graph comparison.",
        ],
    }

    provenance = MetricProvenance(
        run_id=args.run_id,
        commit=_git_commit(),
        config_path=str(args.config),
        dataset_id=root_manifest.get("dataset_id", "muscima_graph_manifest"),
        split=args.split,
        taxonomy_id="semantic_omr_v2",
        artifact_sha256=None,
    )
    write_run_report(run_dir, provenance, metrics)
    _write_report(run_dir, args.run_id, metrics)

    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": args.run_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_manifest": str(root_manifest_path),
                "split_manifest": str(split_path),
                "split": args.split,
                "page_summaries": page_summaries,
                "skipped_pages": skipped_pages,
            },
            indent=2,
            allow_nan=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "artifacts.json").write_text(
        json.dumps(
            {
                "run_id": args.run_id,
                "metrics": str(run_dir / "metrics.json"),
                "report": str(run_dir / "report.md"),
                "manifest": str(run_dir / "manifest.json"),
            },
            indent=2,
            allow_nan=False,
        ),
        encoding="utf-8",
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
    parser.add_argument("--split", default="val", choices=["train", "val", "holdout"])
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "runs" / "graph")
    parser.add_argument("--config", default="configs/non_graph_muscima_heuristic.yaml")
    parser.add_argument("--k-neighbors", type=int, default=8)
    parser.add_argument("--num-staffs", type=int, default=4)
    args = parser.parse_args()
    run_dir = evaluate(args)
    print(f"Wrote non-graph baseline evaluation run to {run_dir}")


if __name__ == "__main__":
    main()
