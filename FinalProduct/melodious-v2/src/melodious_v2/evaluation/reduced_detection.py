"""Reduced-class detector reproduction helpers for M2."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from melodious_v2.contracts import MetricProvenance
from melodious_v2.datasets.deepscores import deepscores_categories, load_coco_json
from melodious_v2.metrics.detection import DetectionPrediction, DetectionTarget, evaluate_detection_dataset
from melodious_v2.reports import write_run_report
from melodious_v2.taxonomies import DEEPSCORES_136_CLASS_NAMES


REDUCED_15_CLASS_NAMES = [
    "notehead-full",
    "notehead-half",
    "notehead-whole",
    "clefG",
    "clefF",
    "clefC",
    "rest-8th",
    "rest-quarter",
    "rest-half",
    "rest-whole",
    "accidentalSharp",
    "accidentalFlat",
    "accidentalNatural",
    "beam",
    "stem",
]

REDUCED_15_NAME_TO_ID = {name: index for index, name in enumerate(REDUCED_15_CLASS_NAMES)}

DEEPSCORES_TO_REDUCED_15 = {
    "noteheadBlackOnLine": "notehead-full",
    "noteheadBlackInSpace": "notehead-full",
    "noteheadHalfOnLine": "notehead-half",
    "noteheadHalfInSpace": "notehead-half",
    "noteheadWholeOnLine": "notehead-whole",
    "noteheadWholeInSpace": "notehead-whole",
    "clefG": "clefG",
    "clefF": "clefF",
    "clefCAlto": "clefC",
    "clefCTenor": "clefC",
    "rest8th": "rest-8th",
    "restQuarter": "rest-quarter",
    "restHalf": "rest-half",
    "restWhole": "rest-whole",
    "accidentalSharp": "accidentalSharp",
    "accidentalFlat": "accidentalFlat",
    "accidentalNatural": "accidentalNatural",
    "beam": "beam",
    "stem": "stem",
}

DEEPSCORES_TO_REDUCED_15_ID = {
    full_name: REDUCED_15_NAME_TO_ID[reduced_name]
    for full_name, reduced_name in DEEPSCORES_TO_REDUCED_15.items()
}


def utc_timestamp() -> str:
    """Return a compact UTC timestamp for generated run metadata."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: str | Path, payload: Any) -> None:
    """Write formatted JSON and create parent directories."""
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


def filename_from_path(raw_path: str) -> str:
    """Return a filename from either Windows or POSIX style paths."""
    return Path(raw_path.replace("\\", "/")).name


def _prediction_box(detection: dict[str, Any], image_size: dict[str, Any]) -> tuple[float, float, float, float]:
    bbox_pixels = detection.get("bbox_pixels")
    if bbox_pixels:
        return (
            float(bbox_pixels["x1"]),
            float(bbox_pixels["y1"]),
            float(bbox_pixels["x2"]),
            float(bbox_pixels["y2"]),
        )

    bbox = detection["bbox"]
    width = float(image_size["width"])
    height = float(image_size["height"])
    box_width = float(bbox["width"]) * width
    box_height = float(bbox["height"]) * height
    x_center = float(bbox["x_center"]) * width
    y_center = float(bbox["y_center"]) * height
    return (
        x_center - box_width / 2.0,
        y_center - box_height / 2.0,
        x_center + box_width / 2.0,
        y_center + box_height / 2.0,
    )


def _load_prediction_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "detections" not in payload or "image_path" not in payload:
        raise ValueError(f"Prediction payload is missing required fields: {path}")
    return payload


def legacy_predictions_from_dir(predictions_dir: str | Path) -> tuple[list[DetectionPrediction], list[dict[str, Any]]]:
    """Load legacy 15-class prediction payloads into V2 metric records."""
    predictions: list[DetectionPrediction] = []
    image_records: list[dict[str, Any]] = []

    for payload_path in sorted(Path(predictions_dir).glob("*.json")):
        payload = _load_prediction_payload(payload_path)
        filename = filename_from_path(str(payload["image_path"]))
        image_size = payload.get("image_size", {})
        before_count = len(predictions)
        ignored = 0

        for detection in payload.get("detections", []):
            class_id = int(detection.get("class_id", -1))
            if class_id < 0 or class_id >= len(REDUCED_15_CLASS_NAMES):
                ignored += 1
                continue
            predictions.append(
                DetectionPrediction(
                    image_id=filename,
                    box_xyxy=_prediction_box(detection, image_size),
                    class_id=class_id,
                    score=float(detection.get("confidence", 0.0)),
                )
            )

        image_records.append(
            {
                "filename": filename,
                "prediction_file": payload_path.resolve().as_posix(),
                "prediction_count": len(predictions) - before_count,
                "ignored_prediction_count": ignored,
                "model": payload.get("model", {}),
                "image_size": image_size,
            }
        )

    if not image_records:
        raise FileNotFoundError(f"No prediction JSON payloads found in {Path(predictions_dir).resolve()}")
    return predictions, image_records


def _index_deepscores_sources(
    source_jsons: list[Path],
) -> tuple[dict[str, tuple[Path, dict[str, Any], dict[str, Any]]], dict[Path, dict[str, int]]]:
    image_index: dict[str, tuple[Path, dict[str, Any], dict[str, Any]]] = {}
    category_maps: dict[Path, dict[str, int]] = {}

    for source_json in source_jsons:
        coco = load_coco_json(source_json)
        resolved = source_json.resolve()
        category_maps[resolved] = deepscores_categories(coco)
        for image_info in coco.get("images", []):
            image_index[filename_from_path(str(image_info["filename"]))] = (resolved, coco, image_info)

    return image_index, category_maps


def reduced_targets_from_deepscores(
    *,
    image_records: list[dict[str, Any]],
    train_json: str | Path,
    test_json: str | Path,
) -> tuple[list[DetectionTarget], list[dict[str, Any]]]:
    """Build reduced 15-class targets for the prediction image set."""
    source_jsons = [Path(train_json), Path(test_json)]
    image_index, category_maps = _index_deepscores_sources(source_jsons)
    targets: list[DetectionTarget] = []
    target_records: list[dict[str, Any]] = []

    for image_record in image_records:
        filename = image_record["filename"]
        indexed = image_index.get(filename)
        if indexed is None:
            raise KeyError(f"Prediction image {filename!r} was not found in DeepScores train/test JSONs")

        source_json, coco, image_info = indexed
        category_map = category_maps[source_json]
        annotations = coco.get("annotations", {})
        before_count = len(targets)
        ignored = 0
        class_counter: Counter[str] = Counter()

        for annotation_id in image_info.get("ann_ids", []):
            annotation = annotations.get(str(annotation_id))
            if not annotation:
                ignored += 1
                continue

            reduced_class_id = None
            full_class_name = None
            for raw_category_id in annotation.get("cat_id", []):
                full_class_id = category_map.get(str(raw_category_id))
                if full_class_id is None:
                    continue
                full_class_name = DEEPSCORES_136_CLASS_NAMES[full_class_id]
                reduced_class_id = DEEPSCORES_TO_REDUCED_15_ID.get(full_class_name)
                if reduced_class_id is not None:
                    break

            bbox = annotation.get("a_bbox")
            if reduced_class_id is None or not bbox or len(bbox) != 4:
                ignored += 1
                continue

            targets.append(
                DetectionTarget(
                    image_id=filename,
                    box_xyxy=tuple(float(value) for value in bbox),
                    class_id=reduced_class_id,
                )
            )
            class_counter[REDUCED_15_CLASS_NAMES[reduced_class_id]] += 1

        target_records.append(
            {
                "filename": filename,
                "image_id": image_info.get("id"),
                "source_json": source_json.as_posix(),
                "target_count": len(targets) - before_count,
                "ignored_annotation_count": ignored,
                "class_counts": dict(sorted(class_counter.items())),
            }
        )

    return targets, target_records


def build_reduced_repro_dataset(
    *,
    predictions_dir: str | Path,
    train_json: str | Path,
    test_json: str | Path,
) -> tuple[list[DetectionPrediction], list[DetectionTarget], dict[str, Any]]:
    """Load legacy predictions and matching DeepScores targets for M2."""
    predictions, image_records = legacy_predictions_from_dir(predictions_dir)
    targets, target_records = reduced_targets_from_deepscores(
        image_records=image_records,
        train_json=train_json,
        test_json=test_json,
    )

    targets_by_filename = {record["filename"]: record for record in target_records}
    images = []
    for image_record in image_records:
        target_record = targets_by_filename[image_record["filename"]]
        images.append({**image_record, **target_record})

    manifest = {
        "dataset_id": "legacy_deepscores_15class_sample",
        "split": "sample_quick",
        "taxonomy_id": "deepscores_15_reduced",
        "class_count": len(REDUCED_15_CLASS_NAMES),
        "class_names": REDUCED_15_CLASS_NAMES,
        "source_paths": {
            "predictions_dir": Path(predictions_dir).resolve().as_posix(),
            "train_json": Path(train_json).resolve().as_posix(),
            "test_json": Path(test_json).resolve().as_posix(),
        },
        "image_count": len(images),
        "prediction_count": len(predictions),
        "target_count": len(targets),
        "ignored_annotation_count": sum(image["ignored_annotation_count"] for image in images),
        "ignored_prediction_count": sum(image["ignored_prediction_count"] for image in images),
        "images": images,
        "notes": [
            "Legacy sample YOLOv8s predictions are evaluated against matching DeepScores annotations.",
            "This is an M2 metric-pipeline reproduction run, not new model training.",
            "DeepScores classes are reduced to the legacy 15-class detector taxonomy before scoring.",
        ],
    }
    return predictions, targets, manifest


def write_reduced_repro_run(
    *,
    run_dir: str | Path,
    run_id: str,
    config_path: str | Path,
    predictions_dir: str | Path,
    train_json: str | Path,
    test_json: str | Path,
    checkpoint_path: str | Path | None,
    commit: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Evaluate the reduced-class sample and write a complete M2 run directory."""
    generated_at = generated_at or utc_timestamp()
    run_root = Path(run_dir)
    run_root.mkdir(parents=True, exist_ok=True)

    predictions, targets, manifest = build_reduced_repro_dataset(
        predictions_dir=predictions_dir,
        train_json=train_json,
        test_json=test_json,
    )
    metrics = evaluate_detection_dataset(predictions, targets, REDUCED_15_CLASS_NAMES)
    artifact_sha256 = None
    resolved_checkpoint = Path(checkpoint_path).resolve() if checkpoint_path else None
    if resolved_checkpoint and resolved_checkpoint.exists():
        artifact_sha256 = sha256_file(resolved_checkpoint)

    provenance = MetricProvenance(
        run_id=run_id,
        commit=commit,
        config_path=Path(config_path).as_posix(),
        dataset_id=manifest["dataset_id"],
        split=manifest["split"],
        taxonomy_id=manifest["taxonomy_id"],
        metric_version=str(metrics["metric_version"]),
        artifact_sha256=artifact_sha256,
        created_at=datetime.fromisoformat(generated_at.replace("Z", "+00:00")),
    )
    write_run_report(run_root, provenance, metrics)

    shutil.copyfile(config_path, run_root / "config.yaml")
    manifest = {
        **manifest,
        "run_id": run_id,
        "generated_at": generated_at,
        "metric_version": metrics["metric_version"],
        "outputs": {
            "run_dir": run_root.resolve().as_posix(),
            "metrics_json": (run_root / "metrics.json").resolve().as_posix(),
            "report_md": (run_root / "report.md").resolve().as_posix(),
            "config_yaml": (run_root / "config.yaml").resolve().as_posix(),
            "artifacts_json": (run_root / "artifacts.json").resolve().as_posix(),
        },
    }
    write_json(run_root / "manifest.json", manifest)

    artifacts = {
        "run_id": run_id,
        "source_model": {
            "checkpoint_path": resolved_checkpoint.as_posix() if resolved_checkpoint else None,
            "checkpoint_exists": bool(resolved_checkpoint and resolved_checkpoint.exists()),
            "artifact_sha256": artifact_sha256,
        },
        "generated": [
            {
                "artifact_type": "metrics",
                "path": (run_root / "metrics.json").resolve().as_posix(),
                "sha256": sha256_file(run_root / "metrics.json"),
            },
            {
                "artifact_type": "report",
                "path": (run_root / "report.md").resolve().as_posix(),
                "sha256": sha256_file(run_root / "report.md"),
            },
            {
                "artifact_type": "manifest",
                "path": (run_root / "manifest.json").resolve().as_posix(),
                "sha256": sha256_file(run_root / "manifest.json"),
            },
            {
                "artifact_type": "config",
                "path": (run_root / "config.yaml").resolve().as_posix(),
                "sha256": sha256_file(run_root / "config.yaml"),
            },
        ],
    }
    write_json(run_root / "artifacts.json", artifacts)
    return {
        "manifest": manifest,
        "metrics": metrics,
        "artifacts": artifacts,
    }
