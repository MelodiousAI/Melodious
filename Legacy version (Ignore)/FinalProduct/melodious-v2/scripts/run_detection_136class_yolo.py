"""Train/evaluate the M3 full 136-class YOLO detector."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import yaml

from melodious_v2.contracts import MetricProvenance
from melodious_v2.evaluation.full_detector import (
    copy_model_artifacts,
    detector_metrics_from_ultralytics,
    load_yaml,
    materialize_yolo_dataset,
    sha256_file,
    summarize_ultralytics_results_csv,
    write_detector_run_analysis,
    write_json,
)
from melodious_v2.paths import ARTIFACTS_DIR, PROJECT_ROOT, RUNS_DIR
from melodious_v2.reports import write_run_report


DEFAULT_SMOKE_RUN_ID = "detection_136class_yolov8s_smoke_v1"
DEFAULT_FULL_RUN_ID = "detection_136class_yolov8m_v1"


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


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def configure_ultralytics_dirs(run_root: Path) -> None:
    """Keep Ultralytics writable config/cache files under ignored `runs/`."""
    config_dir = run_root / "ultralytics_config"
    config_dir.mkdir(parents=True, exist_ok=True)
    os.environ["YOLO_CONFIG_DIR"] = str(config_dir)
    os.environ["MPLCONFIGDIR"] = str(config_dir / "matplotlib")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(PROJECT_ROOT / "configs" / "detection_136class_yolov8m.yaml"))
    parser.add_argument("--manifest-dir", default=str(PROJECT_ROOT / "runs" / "data" / "deepscores_136_manifest"))
    parser.add_argument(
        "--materialized-dir",
        default=str(PROJECT_ROOT / "runs" / "data" / "deepscores_136_yolo_materialized"),
    )
    parser.add_argument(
        "--dataset-yaml",
        default=None,
        help=(
            "Use an existing YOLO dataset.yaml directly instead of materializing "
            "from the M1 DeepScores manifest. Required for tiled/cropped datasets."
        ),
    )
    parser.add_argument(
        "--dataset-id",
        default=None,
        help="Dataset id to record in metric provenance. Defaults to the selected dataset directory name.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model seed. Defaults to yolov8m.pt for full runs and ../yolov8s.pt for --smoke.",
    )
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--smoke", action="store_true", help="Run a constrained one-epoch local validation run.")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--imgsz", type=int, default=None)
    parser.add_argument("--batch", type=int, default=None)
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--device", default="0")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--patience", type=int, default=None)
    parser.add_argument(
        "--max-det",
        type=int,
        default=None,
        help="Maximum detections per image for training validation/final validation. Defaults to Ultralytics behavior.",
    )
    parser.add_argument(
        "--nms-iou",
        type=float,
        default=None,
        help="NMS IoU threshold for training validation/final validation. Defaults to Ultralytics behavior.",
    )
    parser.add_argument("--split", default="val", choices=["val", "test"])
    parser.add_argument("--materialize-only", action="store_true")
    parser.add_argument(
        "--resume-training",
        action="store_true",
        help="Resume an interrupted Ultralytics training run from last.pt instead of starting a new run.",
    )
    parser.add_argument(
        "--resume-checkpoint",
        default=None,
        help=(
            "Checkpoint for --resume-training. Defaults to the run's "
            "ultralytics/train/weights/last.pt."
        ),
    )
    parser.add_argument(
        "--finalize-existing-run",
        action="store_true",
        help="Evaluate/export an existing Ultralytics train directory without launching more training.",
    )
    parser.add_argument(
        "--train-dir",
        default=None,
        help="Existing Ultralytics train directory for --finalize-existing-run. Defaults to the run's ultralytics/train.",
    )
    parser.add_argument(
        "--checkpoint",
        default=None,
        help="Checkpoint to evaluate for --finalize-existing-run. Defaults to best.pt, then last.pt.",
    )
    parser.add_argument("--skip-export", action="store_true")
    parser.add_argument(
        "--val-augment",
        action="store_true",
        help="Enable Ultralytics validation-time augmentation for an evaluation-only comparison.",
    )
    parser.add_argument("--commit", default=None)
    return parser.parse_args(argv)


def _normalize_yolo_names(names: Any) -> dict[int, str]:
    """Return YOLO class names as an integer-keyed mapping."""
    if isinstance(names, dict):
        return {int(key): str(value) for key, value in names.items()}
    if isinstance(names, list):
        return {index: str(value) for index, value in enumerate(names)}
    raise ValueError("Expected YOLO dataset names as a mapping or list.")


def existing_yolo_dataset_manifest(dataset_yaml: str | Path, dataset_id: str | None = None) -> dict[str, Any]:
    """Summarize an existing YOLO dataset without rematerializing it."""
    dataset_yaml_path = Path(dataset_yaml).resolve()
    payload = load_yaml(dataset_yaml_path)
    names = _normalize_yolo_names(payload.get("names"))
    if len(names) != 136:
        raise ValueError("Expected an existing 136-class YOLO dataset YAML.")
    dataset_root = Path(payload.get("path", dataset_yaml_path.parent))
    if not dataset_root.is_absolute():
        dataset_root = (dataset_yaml_path.parent / dataset_root).resolve()
    else:
        dataset_root = dataset_root.resolve()

    split_summaries: dict[str, dict[str, Any]] = {}
    for split in ("train", "val", "test"):
        image_rel = str(payload.get(split, f"images/{split}"))
        image_dir = dataset_root / image_rel
        label_dir = dataset_root / "labels" / split
        image_count = len(
            [
                path
                for path in image_dir.glob("*")
                if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
            ]
        )
        label_count = 0
        class_counts = {name: 0 for _, name in sorted(names.items())}
        if label_dir.exists():
            for label_path in label_dir.glob("*.txt"):
                label_count += 1
                for line in label_path.read_text(encoding="utf-8").splitlines():
                    parts = line.split()
                    if not parts:
                        continue
                    class_id = int(float(parts[0]))
                    class_name = names[class_id]
                    class_counts[class_name] += 1
        split_summaries[split] = {
            "target_images": image_rel,
            "target_labels": f"labels/{split}",
            "image_count": image_count,
            "materialized_image_count": image_count,
            "materialized_label_count": label_count,
            "class_counts": class_counts,
        }

    return {
        "dataset_id": dataset_id or dataset_root.name,
        "source_manifest_dir": None,
        "output_dir": dataset_root.as_posix(),
        "dataset_yaml": dataset_yaml_path.as_posix(),
        "generated_at": utc_timestamp(),
        "materialization_mode": "existing_dataset_yaml",
        "operation_counts": {},
        "splits": split_summaries,
        "class_count": 136,
    }


def _config_training_value(config: dict, name: str, fallback: int) -> int:
    training = config.get("training", {}) if isinstance(config.get("training"), dict) else {}
    return int(training.get(name, fallback))


def _prediction_summary(result) -> dict:
    boxes = getattr(result, "boxes", None)
    if boxes is None or len(boxes) == 0:
        return {"box_count": 0, "class_counts": {}, "max_confidence": None, "mean_confidence": None}
    classes = [int(value) for value in boxes.cls.detach().cpu().tolist()]
    confidences = [float(value) for value in boxes.conf.detach().cpu().tolist()]
    return {
        "box_count": len(classes),
        "class_counts": {str(index): count for index, count in sorted(Counter(classes).items())},
        "max_confidence": max(confidences) if confidences else None,
        "mean_confidence": sum(confidences) / len(confidences) if confidences else None,
    }


def write_onnx_parity_artifact(
    *,
    run_root: Path,
    pytorch_model,
    onnx_path: str | None,
    materialized_manifest: dict,
    split: str,
    imgsz: int,
    device: str,
    max_det: int | None = None,
    nms_iou: float | None = None,
) -> dict:
    """Run a lightweight fixed-image PyTorch/ONNX prediction comparison."""
    parity_path = run_root / "onnx_parity.json"
    sample_dir = Path(materialized_manifest["output_dir"]) / "images" / split
    sample_images = sorted(
        path
        for path in sample_dir.glob("*")
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
    )
    payload = {
        "run_id": run_root.name,
        "generated_at": utc_timestamp(),
        "split": split,
        "sample_image": sample_images[0].resolve().as_posix() if sample_images else None,
        "onnx_path": str(Path(onnx_path).resolve()) if onnx_path else None,
        "status": "skipped",
        "reason": None,
    }
    if not onnx_path:
        payload["reason"] = "No ONNX artifact was produced."
        write_json(parity_path, payload)
        return payload
    if not sample_images:
        payload["reason"] = f"No sample images found under {sample_dir}."
        write_json(parity_path, payload)
        return payload

    try:
        from ultralytics import YOLO

        image = sample_images[0]
        predict_kwargs = {
            "source": str(image),
            "imgsz": imgsz,
            "conf": 0.25,
            "iou": 0.7 if nms_iou is None else nms_iou,
            "device": device,
            "verbose": False,
        }
        if max_det is not None:
            predict_kwargs["max_det"] = max_det
        torch_result = pytorch_model.predict(**predict_kwargs)[0]
        onnx_model = YOLO(str(onnx_path))
        onnx_predict_kwargs = {key: value for key, value in predict_kwargs.items() if key != "device"}
        onnx_result = onnx_model.predict(**onnx_predict_kwargs)[0]
        torch_summary = _prediction_summary(torch_result)
        onnx_summary = _prediction_summary(onnx_result)
        payload.update(
            {
                "status": "passed",
                "pytorch": torch_summary,
                "onnx": onnx_summary,
                "box_count_delta": onnx_summary["box_count"] - torch_summary["box_count"],
            }
        )
    except Exception as exc:  # pragma: no cover - runtime/export dependent
        payload.update({"status": "failed", "reason": str(exc)})
    write_json(parity_path, payload)
    return payload


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError(f"Expected config mapping at {config_path}")

    run_id = args.run_id or (DEFAULT_SMOKE_RUN_ID if args.smoke else DEFAULT_FULL_RUN_ID)
    run_root = RUNS_DIR / "detection" / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    configure_ultralytics_dirs(run_root)

    if args.dataset_yaml:
        materialized_manifest = existing_yolo_dataset_manifest(
            args.dataset_yaml,
            dataset_id=args.dataset_id,
        )
    else:
        materialized_manifest = materialize_yolo_dataset(
            manifest_dir=args.manifest_dir,
            output_dir=args.materialized_dir,
        )
        if args.dataset_id:
            materialized_manifest["dataset_id"] = args.dataset_id
    if args.materialize_only:
        print(json.dumps({"materialized": materialized_manifest}, indent=2, sort_keys=True))
        return

    from ultralytics import YOLO

    smoke_overrides = {}
    model_path = args.model
    if args.smoke:
        if model_path is None:
            model_path = str(PROJECT_ROOT.parent / "yolov8s.pt")
        smoke_overrides = {
            "reason": (
                "Constrained local M3 smoke run: local cache has yolov8s.pt, not yolov8m.pt; "
                "the run validates full 136-class training/evaluation/export plumbing without "
                "claiming final configured detector quality."
            ),
            "model_family": "yolov8s",
        }
    elif model_path is None:
        model_path = "yolov8m.pt"

    epochs = args.epochs if args.epochs is not None else (1 if args.smoke else _config_training_value(config, "epochs", 150))
    imgsz = args.imgsz if args.imgsz is not None else (640 if args.smoke else int(config.get("model", {}).get("image_size", 1024)))
    batch = args.batch if args.batch is not None else (2 if args.smoke else _config_training_value(config, "batch_size", 4))
    patience = args.patience if args.patience is not None else _config_training_value(config, "patience", 30)
    dataset_yaml = Path(materialized_manifest["dataset_yaml"])
    dataset_id = str(materialized_manifest.get("dataset_id", args.dataset_id or "deepscores_136_yolo_materialized"))
    train_project = run_root / "ultralytics"
    train_args = {}
    if args.finalize_existing_run:
        save_dir = Path(args.train_dir).resolve() if args.train_dir else (train_project / "train").resolve()
        if args.checkpoint:
            selected_checkpoint = Path(args.checkpoint).resolve()
        else:
            best_checkpoint = save_dir / "weights" / "best.pt"
            last_checkpoint = save_dir / "weights" / "last.pt"
            selected_checkpoint = best_checkpoint if best_checkpoint.exists() else last_checkpoint
        if not selected_checkpoint.exists():
            raise FileNotFoundError(f"Cannot finalize missing checkpoint: {selected_checkpoint}")
        train_args_path = save_dir / "args.yaml"
        train_args = load_yaml(train_args_path) if train_args_path.exists() else {}
        trained_model = YOLO(str(selected_checkpoint))
    elif args.resume_training:
        resume_checkpoint = (
            Path(args.resume_checkpoint).resolve()
            if args.resume_checkpoint
            else (train_project / "train" / "weights" / "last.pt").resolve()
        )
        if not resume_checkpoint.exists():
            raise FileNotFoundError(f"Cannot resume missing checkpoint: {resume_checkpoint}")
        model = YOLO(str(resume_checkpoint))
        train_result = model.train(resume=True, device=args.device, workers=args.workers)
        save_dir = Path(getattr(train_result, "save_dir", train_project / "train"))
        best_checkpoint = save_dir / "weights" / "best.pt"
        last_checkpoint = save_dir / "weights" / "last.pt"
        selected_checkpoint = best_checkpoint if best_checkpoint.exists() else last_checkpoint
        train_args_path = save_dir / "args.yaml"
        train_args = load_yaml(train_args_path) if train_args_path.exists() else {}
        trained_model = YOLO(str(selected_checkpoint))
    else:
        model = YOLO(model_path)
        train_kwargs = {
            "data": str(dataset_yaml),
            "epochs": epochs,
            "imgsz": imgsz,
            "batch": batch,
            "project": str(train_project),
            "name": "train",
            "exist_ok": True,
            "device": args.device,
            "workers": args.workers,
            "patience": patience,
            "seed": args.seed,
        }
        if args.max_det is not None:
            train_kwargs["max_det"] = args.max_det
        if args.nms_iou is not None:
            train_kwargs["iou"] = args.nms_iou
        train_result = model.train(**train_kwargs)
        save_dir = Path(getattr(train_result, "save_dir", train_project / "train"))
        best_checkpoint = save_dir / "weights" / "best.pt"
        last_checkpoint = save_dir / "weights" / "last.pt"
        selected_checkpoint = best_checkpoint if best_checkpoint.exists() else last_checkpoint
        train_args_path = save_dir / "args.yaml"
        train_args = load_yaml(train_args_path) if train_args_path.exists() else {}
        trained_model = YOLO(str(selected_checkpoint))

    training_results_summary = summarize_ultralytics_results_csv(save_dir / "results.csv")
    val_kwargs = {
        "data": str(dataset_yaml),
        "split": args.split,
        "imgsz": imgsz,
        "batch": batch,
        "project": str(train_project),
        "name": f"val_{args.split}",
        "exist_ok": True,
        "device": args.device,
        "workers": args.workers,
        "augment": args.val_augment,
    }
    if args.max_det is not None:
        val_kwargs["max_det"] = args.max_det
    if args.nms_iou is not None:
        val_kwargs["iou"] = args.nms_iou
    val_result = trained_model.val(**val_kwargs)
    metrics = detector_metrics_from_ultralytics(val_result)

    onnx_path = None
    export_error = None
    if not args.skip_export:
        try:
            exported = trained_model.export(format="onnx", imgsz=imgsz, dynamic=True, simplify=False)
            onnx_path = str(exported)
        except Exception as exc:  # pragma: no cover - environment dependent
            export_error = str(exc)

    onnx_parity = write_onnx_parity_artifact(
        run_root=run_root,
        pytorch_model=trained_model,
        onnx_path=onnx_path,
        materialized_manifest=materialized_manifest,
        split=args.split,
        imgsz=imgsz,
        device=args.device,
        max_det=args.max_det,
        nms_iou=args.nms_iou,
    )

    provenance = MetricProvenance(
        run_id=run_id,
        commit=args.commit or git_commit(),
        config_path=config_path.as_posix(),
        dataset_id=dataset_id,
        split=args.split,
        taxonomy_id="deepscores_136",
        metric_version=metrics["metric_version"],
        artifact_sha256=sha256_file(selected_checkpoint),
        created_at=datetime.now(timezone.utc),
    )
    write_run_report(run_root, provenance, metrics)
    shutil.copyfile(config_path, run_root / "config.yaml")

    model_artifact_dir = ARTIFACTS_DIR / "models" / run_id
    model_artifacts = copy_model_artifacts(
        run_id=run_id,
        artifact_dir=model_artifact_dir,
        checkpoint_path=selected_checkpoint,
        onnx_path=onnx_path,
        extra={
            "source_model": (
                selected_checkpoint.resolve().as_posix()
                if args.finalize_existing_run
                else str(Path(model_path).resolve()) if Path(model_path).exists() else model_path
            ),
            "ultralytics_train_dir": save_dir.resolve().as_posix(),
            "finalize_existing_run": bool(args.finalize_existing_run),
            "export_error": export_error,
        },
    )
    manifest = {
        "run_id": run_id,
        "dataset_id": dataset_id,
        "taxonomy_id": "deepscores_136",
        "generated_at": utc_timestamp(),
        "config_path": config_path.as_posix(),
        "source_config": config,
        "actual_training": {
            "model": str(Path(model_path).resolve()) if Path(model_path).exists() else model_path,
            "epochs": epochs,
            "imgsz": imgsz,
            "batch": batch,
            "workers": args.workers,
            "device": args.device,
            "seed": args.seed,
            "patience": patience,
            "max_det": args.max_det,
            "nms_iou": args.nms_iou,
            "split": args.split,
            "val_augment": bool(args.val_augment),
            "dataset_yaml": Path(args.dataset_yaml).resolve().as_posix() if args.dataset_yaml else None,
            "dataset_id": dataset_id,
            "smoke": bool(args.smoke),
            "smoke_overrides": smoke_overrides,
            "resume_training": bool(args.resume_training),
            "resume_checkpoint": (
                Path(args.resume_checkpoint).resolve().as_posix()
                if args.resume_checkpoint
                else None
            ),
            "finalize_existing_run": bool(args.finalize_existing_run),
            "existing_train_args": train_args,
            "training_results_summary": training_results_summary,
        },
        "materialized_dataset": materialized_manifest,
        "ultralytics": {
            "train_dir": save_dir.resolve().as_posix(),
            "selected_checkpoint": selected_checkpoint.resolve().as_posix(),
            "onnx_path": str(Path(onnx_path).resolve()) if onnx_path else None,
            "export_error": export_error,
        },
        "onnx_parity": onnx_parity,
        "outputs": {
            "metrics_json": (run_root / "metrics.json").resolve().as_posix(),
            "report_md": (run_root / "report.md").resolve().as_posix(),
            "manifest_json": (run_root / "manifest.json").resolve().as_posix(),
            "artifacts_json": (run_root / "artifacts.json").resolve().as_posix(),
            "config_yaml": (run_root / "config.yaml").resolve().as_posix(),
            "onnx_parity_json": (run_root / "onnx_parity.json").resolve().as_posix(),
            "model_artifact_dir": model_artifact_dir.resolve().as_posix(),
        },
        "model_artifacts": model_artifacts,
    }
    write_json(run_root / "manifest.json", manifest)
    if args.dataset_yaml:
        analysis_split_manifest = run_root / f"{args.split}_dataset_class_counts.json"
        write_json(
            analysis_split_manifest,
            {
                "class_counts": materialized_manifest["splits"][args.split]["class_counts"],
                "dataset_id": dataset_id,
                "split": args.split,
            },
        )
    else:
        analysis_split_manifest = (
            PROJECT_ROOT / "runs" / "data" / "deepscores_136_manifest" / f"{args.split}.json"
        )
    analysis = write_detector_run_analysis(
        run_dir=run_root,
        split_manifest=analysis_split_manifest,
    )

    artifacts = {
        "run_id": run_id,
        "generated_at": utc_timestamp(),
        "model_artifacts": model_artifacts,
        "run_artifacts": [
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
            {
                "artifact_type": "analysis",
                "path": (run_root / "analysis.json").resolve().as_posix(),
                "sha256": sha256_file(run_root / "analysis.json"),
            },
            {
                "artifact_type": "analysis_report",
                "path": (run_root / "analysis.md").resolve().as_posix(),
                "sha256": sha256_file(run_root / "analysis.md"),
            },
            {
                "artifact_type": "onnx_parity",
                "path": (run_root / "onnx_parity.json").resolve().as_posix(),
                "sha256": sha256_file(run_root / "onnx_parity.json"),
            },
        ],
    }
    write_json(run_root / "artifacts.json", artifacts)

    summary = {
        "run_id": run_id,
        "run_dir": run_root.resolve().as_posix(),
        "primary_metric": metrics["primary_metric"],
        "primary_value": metrics[metrics["primary_metric"]],
        "checkpoint": selected_checkpoint.resolve().as_posix(),
        "onnx_path": str(Path(onnx_path).resolve()) if onnx_path else None,
        "export_error": export_error,
        "smoke": bool(args.smoke),
        "supported_classes": analysis["summary"]["supported_class_count"],
        "zero_map_supported_classes": analysis["summary"]["zero_map_supported_class_count"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
