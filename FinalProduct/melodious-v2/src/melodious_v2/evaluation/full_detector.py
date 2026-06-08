"""Full-taxonomy detector training and artifact helpers for M3."""

from __future__ import annotations

import hashlib
import csv
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


SPLITS = ("train", "val", "test")


def utc_timestamp() -> str:
    """Return a compact UTC timestamp for generated artifact metadata."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: str | Path, payload: Any) -> None:
    """Write strict formatted JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False),
        encoding="utf-8",
    )


def sha256_file(path: str | Path) -> str:
    """Compute a SHA256 digest for a local artifact."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML mapping from disk."""
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML mapping at {path}")
    return payload


def _relative_to(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _link_or_copy_file(source: Path, target: Path, mode: str) -> str:
    """Materialize one file and return the operation that was used."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return "existing"
    if mode == "hardlink":
        try:
            os.link(source, target)
            return "hardlink"
        except OSError:
            shutil.copy2(source, target)
            return "copy_after_hardlink_failed"
    if mode == "copy":
        shutil.copy2(source, target)
        return "copy"
    raise ValueError(f"Unsupported materialization mode: {mode}")


def materialize_yolo_dataset(
    *,
    manifest_dir: str | Path,
    output_dir: str | Path,
    mode: str = "hardlink",
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build a YOLO-standard full-taxonomy dataset from M1 manifests.

    M1 keeps raw image paths outside the V2 source tree and stores generated
    labels under `runs/`. Ultralytics expects split-local `images/` and
    `labels/` directories, so M3 materializes ignored hardlinks for images and
    copies the generated labels next to them.
    """
    generated_at = generated_at or utc_timestamp()
    source_root = Path(manifest_dir).resolve()
    target_root = Path(output_dir).resolve()
    source_yaml = load_yaml(source_root / "yolo_dataset.yaml")
    names = source_yaml.get("names")
    if not isinstance(names, dict) or len(names) != 136:
        raise ValueError("M3 requires a 136-class YOLO dataset YAML.")

    split_summaries: dict[str, dict[str, Any]] = {}
    operation_counts: dict[str, int] = {}
    for split in SPLITS:
        image_list_path = source_root / "generated" / "image_lists" / f"{split}.txt"
        source_label_dir = source_root / "generated" / "labels" / split
        target_image_dir = target_root / "images" / split
        target_label_dir = target_root / "labels" / split
        image_paths = [
            Path(line.strip())
            for line in image_list_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        materialized_images = 0
        materialized_labels = 0
        missing_images: list[str] = []
        missing_labels: list[str] = []
        for source_image in image_paths:
            if not source_image.exists():
                missing_images.append(source_image.as_posix())
                continue
            target_image = target_image_dir / source_image.name
            operation = _link_or_copy_file(source_image, target_image, mode)
            operation_counts[operation] = operation_counts.get(operation, 0) + 1
            materialized_images += 1

            source_label = source_label_dir / f"{source_image.stem}.txt"
            if not source_label.exists():
                missing_labels.append(source_label.as_posix())
                continue
            target_label = target_label_dir / source_label.name
            label_operation = _link_or_copy_file(source_label, target_label, "copy")
            operation_counts[f"label_{label_operation}"] = operation_counts.get(
                f"label_{label_operation}",
                0,
            ) + 1
            materialized_labels += 1

        split_summaries[split] = {
            "source_image_list": image_list_path.as_posix(),
            "target_images": _relative_to(target_image_dir, target_root),
            "target_labels": _relative_to(target_label_dir, target_root),
            "image_count": len(image_paths),
            "materialized_image_count": materialized_images,
            "materialized_label_count": materialized_labels,
            "missing_images": missing_images,
            "missing_labels": missing_labels,
        }

    dataset_yaml = {
        "path": target_root.as_posix(),
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        "nc": 136,
        "names": {int(index): name for index, name in names.items()},
    }
    dataset_yaml_path = target_root / "dataset.yaml"
    dataset_yaml_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_yaml_path.write_text(yaml.safe_dump(dataset_yaml, sort_keys=False), encoding="utf-8")

    manifest = {
        "dataset_id": "deepscores_136_yolo_materialized",
        "source_manifest_dir": source_root.as_posix(),
        "output_dir": target_root.as_posix(),
        "dataset_yaml": dataset_yaml_path.as_posix(),
        "generated_at": generated_at,
        "materialization_mode": mode,
        "operation_counts": operation_counts,
        "splits": split_summaries,
        "class_count": 136,
    }
    write_json(target_root / "manifest.json", manifest)
    return manifest


def metric_from_results_dict(results: dict[str, Any], *candidates: str) -> float:
    """Fetch a metric value from Ultralytics' results dictionary."""
    for candidate in candidates:
        if candidate in results:
            return float(results[candidate])
    raise KeyError(f"Missing metric; tried {', '.join(candidates)}")


def detector_metrics_from_ultralytics(result: Any) -> dict[str, Any]:
    """Normalize Ultralytics validation output to Melodious metric keys."""
    results_dict = dict(getattr(result, "results_dict", {}) or {})
    precision = metric_from_results_dict(results_dict, "metrics/precision(B)", "precision")
    recall = metric_from_results_dict(results_dict, "metrics/recall(B)", "recall")
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    metrics = {
        "metric_version": "ultralytics_detection_v2.0",
        "primary_metric": "mAP@0.5:0.95",
        "mAP@0.5:0.95": metric_from_results_dict(
            results_dict,
            "metrics/mAP50-95(B)",
            "mAP50-95",
        ),
        "mAP@0.5": metric_from_results_dict(results_dict, "metrics/mAP50(B)", "mAP50"),
        "precision@0.5": precision,
        "recall@0.5": recall,
        "F1@0.5": f1,
    }
    box = getattr(result, "box", None)
    names = getattr(result, "names", None) or {}
    maps = getattr(box, "maps", None) if box is not None else None
    if maps is not None:
        metrics["per_class_mAP@0.5:0.95"] = {
            str(names.get(index, index)): float(value)
            for index, value in enumerate(list(maps))
        }
    return metrics


def summarize_ultralytics_results_csv(path: str | Path) -> dict[str, Any]:
    """Summarize an Ultralytics training `results.csv` file."""
    csv_path = Path(path)
    if not csv_path.exists():
        return {"path": csv_path.resolve().as_posix(), "exists": False}

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [
            {str(key).strip(): str(value).strip() for key, value in row.items()}
            for row in reader
        ]

    def as_float(row: dict[str, str], key: str) -> float | None:
        value = row.get(key)
        if value in (None, ""):
            return None
        return float(value)

    def as_int(row: dict[str, str], key: str) -> int | None:
        value = as_float(row, key)
        return int(value) if value is not None else None

    def metric_summary(row: dict[str, str]) -> dict[str, float | int | None]:
        return {
            "epoch": as_int(row, "epoch"),
            "precision@0.5": as_float(row, "metrics/precision(B)"),
            "recall@0.5": as_float(row, "metrics/recall(B)"),
            "mAP@0.5": as_float(row, "metrics/mAP50(B)"),
            "mAP@0.5:0.95": as_float(row, "metrics/mAP50-95(B)"),
            "train/box_loss": as_float(row, "train/box_loss"),
            "train/cls_loss": as_float(row, "train/cls_loss"),
            "train/dfl_loss": as_float(row, "train/dfl_loss"),
            "val/box_loss": as_float(row, "val/box_loss"),
            "val/cls_loss": as_float(row, "val/cls_loss"),
            "val/dfl_loss": as_float(row, "val/dfl_loss"),
        }

    rows_with_primary = [
        row
        for row in rows
        if as_float(row, "metrics/mAP50-95(B)") is not None
    ]
    best_row = (
        max(rows_with_primary, key=lambda row: as_float(row, "metrics/mAP50-95(B)") or 0.0)
        if rows_with_primary
        else None
    )
    last_row = rows[-1] if rows else None
    return {
        "path": csv_path.resolve().as_posix(),
        "exists": True,
        "row_count": len(rows),
        "last_completed": metric_summary(last_row) if last_row else None,
        "best_by_mAP@0.5:0.95": metric_summary(best_row) if best_row else None,
    }


def copy_model_artifacts(
    *,
    run_id: str,
    artifact_dir: str | Path,
    checkpoint_path: str | Path | None,
    onnx_path: str | Path | None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Copy available model artifacts into `artifacts/models/{run_id}`."""
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []

    for artifact_type, raw_path in (("checkpoint", checkpoint_path), ("onnx", onnx_path)):
        if raw_path is None:
            continue
        source = Path(raw_path)
        if not source.exists():
            records.append(
                {
                    "artifact_type": artifact_type,
                    "source_path": source.as_posix(),
                    "exists": False,
                }
            )
            continue
        target = root / source.name
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        records.append(
            {
                "artifact_type": artifact_type,
                "source_path": source.resolve().as_posix(),
                "path": target.resolve().as_posix(),
                "exists": True,
                "sha256": sha256_file(target),
                "bytes": target.stat().st_size,
            }
        )

    metadata = {
        "run_id": run_id,
        "generated_at": utc_timestamp(),
        "artifacts": records,
        "extra": extra or {},
    }
    write_json(root / "metadata.json", metadata)
    return metadata


SMALL_SYMBOL_KEYWORDS = (
    "accidental",
    "augmentationDot",
    "flag",
    "fingering",
    "ornament",
    "staccato",
    "staccatissimo",
    "tenuto",
    "tremolo",
    "tuplet",
)


def write_detector_run_analysis(
    *,
    run_dir: str | Path,
    split_manifest: str | Path,
) -> dict[str, Any]:
    """Write class-support and error-analysis artifacts for a detector run."""
    root = Path(run_dir)
    metrics_payload = json.loads((root / "metrics.json").read_text(encoding="utf-8"))
    metrics = metrics_payload["metrics"]
    split_payload = json.loads(Path(split_manifest).read_text(encoding="utf-8"))
    support_by_class = split_payload.get("class_counts", {})
    per_class_map = metrics.get("per_class_mAP@0.5:0.95", {})

    rows = []
    for class_name, support in support_by_class.items():
        value = per_class_map.get(class_name)
        rows.append(
            {
                "class_name": class_name,
                "support": int(support),
                "mAP@0.5:0.95": value,
                "small_symbol": any(keyword.lower() in class_name.lower() for keyword in SMALL_SYMBOL_KEYWORDS),
            }
        )

    supported_rows = [row for row in rows if row["support"] > 0]
    rare_rows = [row for row in supported_rows if row["support"] <= 10]
    zero_map_rows = [
        row
        for row in supported_rows
        if row["mAP@0.5:0.95"] is not None and float(row["mAP@0.5:0.95"]) == 0.0
    ]
    small_rows = [row for row in supported_rows if row["small_symbol"]]
    small_values = [
        float(row["mAP@0.5:0.95"])
        for row in small_rows
        if row["mAP@0.5:0.95"] is not None
    ]
    error_artifact_dir = root / "ultralytics" / "val_val"
    error_artifacts = [
        path.resolve().as_posix()
        for path in sorted(error_artifact_dir.glob("*"))
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}
    ]

    analysis = {
        "run_id": metrics_payload["provenance"]["run_id"],
        "dataset_id": metrics_payload["provenance"]["dataset_id"],
        "split": metrics_payload["provenance"]["split"],
        "taxonomy_id": metrics_payload["provenance"]["taxonomy_id"],
        "generated_at": utc_timestamp(),
        "source_metrics": (root / "metrics.json").resolve().as_posix(),
        "source_split_manifest": Path(split_manifest).resolve().as_posix(),
        "summary": {
            "class_count": len(rows),
            "supported_class_count": len(supported_rows),
            "rare_class_count_support_lte_10": len(rare_rows),
            "zero_map_supported_class_count": len(zero_map_rows),
            "small_symbol_supported_class_count": len(small_rows),
            "small_symbol_mean_mAP@0.5:0.95": (
                sum(small_values) / len(small_values) if small_values else None
            ),
            "primary_metric": metrics["primary_metric"],
            "primary_value": metrics[metrics["primary_metric"]],
            "mAP@0.5": metrics.get("mAP@0.5"),
            "precision@0.5": metrics.get("precision@0.5"),
            "recall@0.5": metrics.get("recall@0.5"),
            "F1@0.5": metrics.get("F1@0.5"),
        },
        "best_supported_classes_by_mAP": sorted(
            [
                row
                for row in supported_rows
                if row["mAP@0.5:0.95"] is not None and float(row["mAP@0.5:0.95"]) > 0.0
            ],
            key=lambda row: float(row["mAP@0.5:0.95"]),
            reverse=True,
        )[:20],
        "rare_supported_classes": rare_rows,
        "zero_map_supported_classes": zero_map_rows,
        "small_symbol_classes": small_rows,
        "per_class": rows,
        "error_artifacts": error_artifacts,
        "notes": [
            "This analysis is generated from metrics.json and the fixed split manifest.",
            "Per-class mAP is available from Ultralytics validation output.",
            "Per-class F1 is not written into metrics.json by the current M3 wrapper; use the saved BoxF1 curve and future prediction exports for deeper threshold-specific per-class F1.",
            "The current run is a constrained smoke run unless the run manifest says smoke=false.",
        ],
    }
    write_json(root / "analysis.json", analysis)

    lines = [
        f"# Detector Run Analysis: {analysis['run_id']}",
        "",
        f"- Dataset: `{analysis['dataset_id']}`",
        f"- Split: `{analysis['split']}`",
        f"- Taxonomy: `{analysis['taxonomy_id']}`",
        f"- Primary metric: `{analysis['summary']['primary_metric']}`",
        f"- Primary value: `{analysis['summary']['primary_value']}`",
        f"- Supported classes in split: `{analysis['summary']['supported_class_count']}` of `{analysis['summary']['class_count']}`",
        f"- Rare supported classes (`support <= 10`): `{analysis['summary']['rare_class_count_support_lte_10']}`",
        f"- Supported classes with zero mAP in this run: `{analysis['summary']['zero_map_supported_class_count']}`",
        f"- Small-symbol supported classes: `{analysis['summary']['small_symbol_supported_class_count']}`",
        "",
        "## Best Supported Classes By mAP",
        "",
    ]
    for row in analysis["best_supported_classes_by_mAP"][:10]:
        lines.append(f"- `{row['class_name']}`: support `{row['support']}`, mAP `{row['mAP@0.5:0.95']}`")
    lines.extend(
        [
            "",
            "## Error Artifacts",
            "",
        ]
    )
    for artifact in error_artifacts:
        lines.append(f"- `{artifact}`")
    (root / "analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return analysis
