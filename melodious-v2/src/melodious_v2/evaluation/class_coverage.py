"""Class-coverage audit helpers for full-taxonomy detector experiments."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from melodious_v2.taxonomies import (
    DEEPSCORES_136_CLASS_NAMES,
    semantic_group_for_class,
)


SPLITS = ("train", "val", "test")
SMALL_SYMBOL_KEYWORDS = (
    "accidental",
    "augmentationdot",
    "flag",
    "fingering",
    "ornament",
    "staccato",
    "staccatissimo",
    "tenuto",
    "tremolo",
    "tuplet",
)


def utc_timestamp() -> str:
    """Return an ISO-8601 UTC timestamp for generated audit metadata."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a JSON mapping from disk."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def write_json(path: str | Path, payload: Any) -> None:
    """Write deterministic, strict JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False),
        encoding="utf-8",
    )


def _class_counts(payload: dict[str, Any], class_names: Iterable[str]) -> dict[str, int]:
    raw_counts = payload.get("class_counts")
    if not isinstance(raw_counts, dict):
        raise ValueError("Expected split manifest to contain a class_counts mapping.")
    return {class_name: int(raw_counts.get(class_name, 0) or 0) for class_name in class_names}


def _small_symbol(class_name: str) -> bool:
    lower = class_name.lower()
    return any(keyword in lower for keyword in SMALL_SYMBOL_KEYWORDS)


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _names(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row["class_name"]) for row in rows]


def build_class_coverage_audit(
    *,
    manifest_dir: str | Path,
    metrics_path: str | Path | None = None,
    evaluation_split: str = "val",
    class_names: Iterable[str] = DEEPSCORES_136_CLASS_NAMES,
    splits: Iterable[str] = SPLITS,
    rare_threshold: int = 10,
    high_support_threshold: int = 100,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a class-support audit for detector data and optional metrics.

    Ultralytics can emit per-class map values for all taxonomy classes even
    when a class has zero ground-truth instances in the evaluated split. This
    audit keeps those raw values visible but marks them inapplicable whenever
    the evaluated split has no support for the class.
    """
    class_name_list = list(class_names)
    split_list = tuple(splits)
    if evaluation_split not in split_list:
        raise ValueError(f"evaluation_split must be one of {split_list}: {evaluation_split}")

    manifest_root = Path(manifest_dir)
    split_counts: dict[str, dict[str, int]] = {}
    split_manifests: dict[str, dict[str, Any]] = {}
    split_manifest_paths: dict[str, str] = {}
    for split in split_list:
        split_path = manifest_root / f"{split}.json"
        payload = load_json(split_path)
        split_manifests[split] = payload
        split_manifest_paths[split] = split_path.resolve().as_posix()
        split_counts[split] = _class_counts(payload, class_name_list)

    metrics_payload: dict[str, Any] | None = None
    metrics: dict[str, Any] = {}
    per_class_map: dict[str, Any] = {}
    source_metrics_path: str | None = None
    if metrics_path is not None:
        source_metrics = Path(metrics_path)
        metrics_payload = load_json(source_metrics)
        source_metrics_path = source_metrics.resolve().as_posix()
        metrics = metrics_payload.get("metrics", {})
        if not isinstance(metrics, dict):
            raise ValueError(f"Expected metrics mapping in {metrics_path}")
        raw_per_class = metrics.get("per_class_mAP@0.5:0.95", {})
        per_class_map = raw_per_class if isinstance(raw_per_class, dict) else {}

    rows: list[dict[str, Any]] = []
    for class_id, class_name in enumerate(class_name_list):
        counts = {split: split_counts[split][class_name] for split in split_list}
        total_count = sum(counts.values())
        evaluation_support = counts[evaluation_split]
        raw_map_value = _float_or_none(per_class_map.get(class_name))
        metric_applicable = raw_map_value is not None and evaluation_support > 0
        metric_value = raw_map_value if metric_applicable else None
        row = {
            "class_id": class_id,
            "class_name": class_name,
            "semantic_group": semantic_group_for_class(class_name),
            "counts": counts,
            "total_count": total_count,
            "supported_splits": [split for split, count in counts.items() if count > 0],
            "present_in_train": counts.get("train", 0) > 0,
            "present_in_val": counts.get("val", 0) > 0,
            "present_in_test": counts.get("test", 0) > 0,
            "full_dataset_supported": total_count > 0,
            "small_symbol": _small_symbol(class_name),
            "evaluation_split": evaluation_split,
            "evaluation_support": evaluation_support,
            "metric_applicable": metric_applicable,
            "mAP@0.5:0.95": metric_value,
            "raw_mAP@0.5:0.95": raw_map_value,
            "raw_map_ignored_because_no_evaluation_support": raw_map_value is not None and evaluation_support == 0,
            "rare_on_evaluation_split": 0 < evaluation_support <= rare_threshold,
            "zero_map_on_evaluation_split": metric_applicable and metric_value == 0.0,
            "low_map_on_evaluation_split": metric_applicable and metric_value is not None and metric_value <= 0.1,
        }
        rows.append(row)

    absent_by_split = {
        split: [row for row in rows if row["counts"][split] == 0]
        for split in split_list
    }
    supported_by_split = {
        split: [row for row in rows if row["counts"][split] > 0]
        for split in split_list
    }
    zero_data_rows = [row for row in rows if row["total_count"] == 0]
    train_supported_val_absent = [
        row for row in rows if row["counts"].get("train", 0) > 0 and row["counts"].get("val", 0) == 0
    ]
    val_supported_train_absent = [
        row for row in rows if row["counts"].get("val", 0) > 0 and row["counts"].get("train", 0) == 0
    ]
    test_supported_train_absent = [
        row for row in rows if row["counts"].get("test", 0) > 0 and row["counts"].get("train", 0) == 0
    ]
    evaluation_supported = [row for row in rows if row["evaluation_support"] > 0]
    rare_evaluation_supported = [
        row for row in evaluation_supported if row["rare_on_evaluation_split"]
    ]
    zero_map_supported = [
        row for row in evaluation_supported if row["zero_map_on_evaluation_split"]
    ]
    low_map_supported = [
        row for row in evaluation_supported if row["low_map_on_evaluation_split"]
    ]
    high_support_zero_map_supported = [
        row
        for row in zero_map_supported
        if int(row["evaluation_support"]) >= high_support_threshold
    ]
    unsupported_with_raw_map = [
        row for row in rows if row["raw_map_ignored_because_no_evaluation_support"]
    ]

    sorted_zero_map = sorted(
        zero_map_supported,
        key=lambda row: (-int(row["evaluation_support"]), int(row["class_id"])),
    )
    sorted_low_map = sorted(
        low_map_supported,
        key=lambda row: (float(row["mAP@0.5:0.95"]), -int(row["evaluation_support"])),
    )

    summary = {
        "class_count": len(rows),
        "splits": {
            split: {
                "image_count": int(split_manifests[split].get("image_count", 0) or 0),
                "annotation_count": int(split_manifests[split].get("annotation_count", 0) or 0),
                "supported_class_count": len(supported_by_split[split]),
                "absent_class_count": len(absent_by_split[split]),
            }
            for split in split_list
        },
        "full_dataset_supported_class_count": len([row for row in rows if row["total_count"] > 0]),
        "zero_data_class_count": len(zero_data_rows),
        "zero_data_classes": _names(zero_data_rows),
        "train_supported_val_absent_count": len(train_supported_val_absent),
        "train_supported_val_absent_classes": _names(train_supported_val_absent),
        "val_supported_train_absent_count": len(val_supported_train_absent),
        "val_supported_train_absent_classes": _names(val_supported_train_absent),
        "test_supported_train_absent_count": len(test_supported_train_absent),
        "test_supported_train_absent_classes": _names(test_supported_train_absent),
        "evaluation_split": evaluation_split,
        "evaluation_supported_class_count": len(evaluation_supported),
        "evaluation_blind_spot_class_count": len(rows) - len(evaluation_supported),
        "rare_evaluation_supported_class_count": len(rare_evaluation_supported),
        "rare_threshold": rare_threshold,
        "high_support_threshold": high_support_threshold,
        "zero_map_supported_class_count": len(zero_map_supported),
        "zero_map_supported_classes": _names(sorted_zero_map),
        "high_support_zero_map_supported_class_count": len(high_support_zero_map_supported),
        "high_support_zero_map_supported_classes": _names(high_support_zero_map_supported),
        "low_map_supported_class_count": len(low_map_supported),
        "low_map_supported_classes": _names(sorted_low_map),
        "unsupported_metric_value_count": len(unsupported_with_raw_map),
        "unsupported_metric_values_are_ignored": bool(unsupported_with_raw_map),
    }
    if metrics_payload is not None:
        provenance = metrics_payload.get("provenance", {})
        summary["metrics"] = {
            "source_metrics": source_metrics_path,
            "run_id": provenance.get("run_id"),
            "split": provenance.get("split"),
            "artifact_sha256": provenance.get("artifact_sha256"),
            "primary_metric": metrics.get("primary_metric"),
            "primary_value": metrics.get(metrics.get("primary_metric")) if metrics.get("primary_metric") else None,
            "mAP@0.5": metrics.get("mAP@0.5"),
            "precision@0.5": metrics.get("precision@0.5"),
            "recall@0.5": metrics.get("recall@0.5"),
            "F1@0.5": metrics.get("F1@0.5"),
        }

    audit = {
        "audit_id": "detector_class_coverage",
        "generated_at": generated_at or utc_timestamp(),
        "manifest_dir": manifest_root.resolve().as_posix(),
        "split_manifest_paths": split_manifest_paths,
        "source_metrics": source_metrics_path,
        "summary": summary,
        "per_class": rows,
        "notes": [
            "Classes with zero support in the evaluated split are metric blind spots for that split.",
            "Raw per-class map values for unsupported classes are retained but ignored in summary counts.",
            "Fine-tuning can improve classes with training examples, but classes with zero training support need more data or a taxonomy decision.",
            "The test split should remain untouched until the model and inference configuration are frozen.",
        ],
    }
    return audit


def write_class_coverage_report(
    *,
    audit: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, str]:
    """Write JSON and Markdown coverage reports."""
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "class_coverage.json"
    md_path = output_root / "class_coverage.md"
    write_json(json_path, audit)

    summary = audit["summary"]
    split_lines = [
        (
            f"- `{split}`: `{values['supported_class_count']}` supported classes, "
            f"`{values['absent_class_count']}` absent classes, "
            f"`{values['image_count']}` images, `{values['annotation_count']}` annotations"
        )
        for split, values in summary["splits"].items()
    ]
    metrics = summary.get("metrics", {})
    metrics_lines = []
    if metrics:
        metrics_lines = [
            "",
            "## Evaluated Metrics Source",
            "",
            f"- Run id: `{metrics.get('run_id')}`",
            f"- Source: `{metrics.get('source_metrics')}`",
            f"- Split: `{metrics.get('split')}`",
            f"- Primary metric: `{metrics.get('primary_metric')}`",
            f"- Primary value: `{metrics.get('primary_value')}`",
            f"- `mAP@0.5`: `{metrics.get('mAP@0.5')}`",
            f"- `precision@0.5`: `{metrics.get('precision@0.5')}`",
            f"- `recall@0.5`: `{metrics.get('recall@0.5')}`",
            f"- `F1@0.5`: `{metrics.get('F1@0.5')}`",
        ]

    def list_block(title: str, values: list[str]) -> list[str]:
        if not values:
            return ["", f"## {title}", "", "- None."]
        return ["", f"## {title}", "", *[f"- `{value}`" for value in values]]

    lines = [
        "# Detector Class Coverage Audit",
        "",
        f"- Generated at: `{audit['generated_at']}`",
        f"- Manifest directory: `{audit['manifest_dir']}`",
        f"- Evaluation split: `{summary['evaluation_split']}`",
        f"- Taxonomy classes: `{summary['class_count']}`",
        f"- Classes with any local labels: `{summary['full_dataset_supported_class_count']}`",
        f"- Classes with zero labels across train/val/test: `{summary['zero_data_class_count']}`",
        f"- Evaluation-supported classes: `{summary['evaluation_supported_class_count']}`",
        f"- Evaluation blind spots: `{summary['evaluation_blind_spot_class_count']}`",
        f"- Zero-map supported classes: `{summary['zero_map_supported_class_count']}`",
        f"- High-support zero-map supported classes: `{summary['high_support_zero_map_supported_class_count']}`",
        "",
        "## Split Support",
        "",
        *split_lines,
        *metrics_lines,
        *list_block("Zero-Data Taxonomy Classes", summary["zero_data_classes"]),
        *list_block(
            "Train-Supported But Validation-Absent Classes",
            summary["train_supported_val_absent_classes"],
        ),
        *list_block(
            "Zero-Map Supported Validation Classes",
            summary["zero_map_supported_classes"],
        ),
        "",
        "## Interpretation",
        "",
        "- The detector head has 136 output classes, but coverage quality is constrained by the local labels.",
        "- Classes absent from `train` cannot be learned by another fine-tune on the same data.",
        "- Classes absent from `val` cannot be validated honestly on the current validation split.",
        "- The next fine-tune is still useful for supported classes, but final claims must separate supported-class metrics from full-taxonomy coverage limitations.",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "json": json_path.resolve().as_posix(),
        "markdown": md_path.resolve().as_posix(),
    }
