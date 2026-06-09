"""Reproducible dataset manifest builders for detector and graph data."""

from __future__ import annotations

import json
import random
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence, TypeVar

from melodious_v2.datasets.deepscores import (
    deepscores_categories,
    labels_for_image,
    load_coco_json,
)
from melodious_v2.taxonomies import DEEPSCORES_136_CLASS_NAMES


T = TypeVar("T")


def utc_timestamp() -> str:
    """Return a stable UTC timestamp format for generated manifest metadata."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: str | Path, payload: Any) -> None:
    """Write formatted JSON, creating parent directories as needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _path_text(path: str | Path) -> str:
    return Path(path).resolve().as_posix()


def ratio_counts(total: int, ratios: Sequence[tuple[str, float]]) -> dict[str, int]:
    """Convert split ratios into deterministic integer counts that sum to total."""
    if total < 0:
        raise ValueError("total must be non-negative")
    if not ratios:
        raise ValueError("at least one split ratio is required")
    if len({name for name, _ratio in ratios}) != len(ratios):
        raise ValueError("split names must be unique")
    if any(ratio < 0.0 for _name, ratio in ratios):
        raise ValueError("split ratios must be non-negative")

    ratio_sum = sum(ratio for _name, ratio in ratios)
    if ratio_sum <= 0.0:
        raise ValueError("split ratios must sum to a positive value")

    exact_counts = [(name, total * ratio / ratio_sum) for name, ratio in ratios]
    counts = {name: int(exact) for name, exact in exact_counts}
    remainder = total - sum(counts.values())
    fractions = sorted(
        ((exact - int(exact), index, name) for index, (name, exact) in enumerate(exact_counts)),
        key=lambda item: (-item[0], item[1]),
    )
    for _fraction, _index, name in fractions[:remainder]:
        counts[name] += 1
    return counts


def deterministic_split(
    items: Iterable[T],
    ratios: Sequence[tuple[str, float]],
    seed: int,
    key: Callable[[T], Any],
) -> dict[str, list[T]]:
    """Split items deterministically after sorting them by a stable key."""
    ordered = sorted(list(items), key=key)
    random.Random(seed).shuffle(ordered)
    counts = ratio_counts(len(ordered), ratios)

    splits: dict[str, list[T]] = {}
    start = 0
    for name, _ratio in ratios:
        end = start + counts[name]
        splits[name] = sorted(ordered[start:end], key=key)
        start = end
    return splits


def image_sort_key(image_info: dict[str, Any]) -> tuple[int, int | str]:
    """Sort DeepScores images by id, keeping non-numeric ids deterministic."""
    image_id = image_info.get("id")
    try:
        return (0, int(image_id))
    except (TypeError, ValueError):
        return (1, str(image_id))


def nonzero_class_counts(counter: Counter[int]) -> dict[str, int]:
    """Return non-zero class counts in taxonomy order."""
    return {
        class_name: int(counter[index])
        for index, class_name in enumerate(DEEPSCORES_136_CLASS_NAMES)
        if counter[index] > 0
    }


def full_class_counts(counter: Counter[int]) -> dict[str, int]:
    """Return all 136 class counts in taxonomy order."""
    return {
        class_name: int(counter[index])
        for index, class_name in enumerate(DEEPSCORES_136_CLASS_NAMES)
    }


def _image_path(image_root: Path, filename: str) -> str:
    return (image_root / filename).resolve().as_posix()


def build_deepscores_split_manifest(
    *,
    split_name: str,
    images: Sequence[dict[str, Any]],
    coco: dict[str, Any],
    source_json: str | Path,
    output_dir: str | Path,
    image_root: str | Path,
) -> dict[str, Any]:
    """Write labels and return a manifest payload for one DeepScores split."""
    source_path = Path(source_json).resolve()
    run_dir = Path(output_dir)
    label_dir = run_dir / "generated" / "labels" / split_name
    label_dir.mkdir(parents=True, exist_ok=True)
    image_list_path = run_dir / "generated" / "image_lists" / f"{split_name}.txt"
    image_list_path.parent.mkdir(parents=True, exist_ok=True)

    annotations = coco.get("annotations", {})
    category_map = deepscores_categories(coco)
    split_counter: Counter[int] = Counter()
    raw_annotation_count = 0
    label_count = 0
    image_entries: list[dict[str, Any]] = []
    image_list_lines: list[str] = []
    used_label_names: Counter[str] = Counter()

    for image_info in sorted(images, key=image_sort_key):
        filename = str(image_info["filename"])
        labels = labels_for_image(image_info, annotations, category_map)
        image_counter: Counter[int] = Counter(label.class_id for label in labels)
        split_counter.update(image_counter)
        raw_count = len(image_info.get("ann_ids", []))
        raw_annotation_count += raw_count
        label_count += len(labels)

        base_label_name = f"{Path(filename).stem}.txt"
        used_label_names[base_label_name] += 1
        label_name = base_label_name
        if used_label_names[base_label_name] > 1:
            label_name = f"{image_info.get('id')}_{base_label_name}"
        label_path = label_dir / label_name
        label_text = "\n".join(label.to_line() for label in labels)
        if label_text:
            label_text += "\n"
        label_path.write_text(label_text, encoding="utf-8")

        image_list_lines.append(_image_path(Path(image_root), filename))
        image_entries.append(
            {
                "image_id": image_info.get("id"),
                "filename": filename,
                "width": int(image_info["width"]),
                "height": int(image_info["height"]),
                "source_json": source_path.as_posix(),
                "annotation_count": raw_count,
                "label_count": len(labels),
                "class_counts": nonzero_class_counts(image_counter),
                "label_file": label_path.resolve().as_posix(),
            }
        )

    image_list_path.write_text("\n".join(image_list_lines) + ("\n" if image_list_lines else ""), encoding="utf-8")

    split_summary = {
        "split": split_name,
        "taxonomy_id": "deepscores_136",
        "class_count": len(DEEPSCORES_136_CLASS_NAMES),
        "source_json": source_path.as_posix(),
        "image_count": len(image_entries),
        "annotation_count": raw_annotation_count,
        "label_count": label_count,
        "classes_with_support": sum(1 for count in split_counter.values() if count > 0),
        "class_counts": full_class_counts(split_counter),
        "label_dir": label_dir.resolve().as_posix(),
        "image_list": image_list_path.resolve().as_posix(),
    }
    return {
        **split_summary,
        "images": image_entries,
    }


def summarize_deepscores_split(split_manifest: dict[str, Any]) -> dict[str, Any]:
    """Return the compact summary recorded in the top-level DeepScores manifest."""
    return {
        "split": split_manifest["split"],
        "taxonomy_id": split_manifest["taxonomy_id"],
        "class_count": split_manifest["class_count"],
        "source_json": split_manifest["source_json"],
        "image_count": split_manifest["image_count"],
        "annotation_count": split_manifest["annotation_count"],
        "label_count": split_manifest["label_count"],
        "classes_with_support": split_manifest["classes_with_support"],
        "label_dir": split_manifest["label_dir"],
        "image_list": split_manifest["image_list"],
    }


DEEPSCORES_WORK_RE = re.compile(r"^(?P<work>lg-[^-]+)-aug-[^-]+--page-\d+$")


def infer_deepscores_work_group(filename: str) -> str | None:
    """Infer a score/work group from common DeepScores generated filenames."""
    stem = Path(filename).stem
    match = DEEPSCORES_WORK_RE.match(stem)
    if match:
        return match.group("work")
    if "--page-" in stem:
        return stem.split("--page-", 1)[0]
    if "-page-" in stem:
        return stem.split("-page-", 1)[0]
    return None


def _duplicates_across_splits(
    split_manifests: dict[str, dict[str, Any]],
    value_getter: Callable[[dict[str, Any]], str | None],
) -> list[dict[str, Any]]:
    value_to_splits: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for split_name, manifest in split_manifests.items():
        for image in manifest.get("images", []):
            value = value_getter(image)
            if value is None:
                continue
            value_to_splits[str(value)].setdefault(split_name, []).append(str(image.get("filename")))
    return [
        {
            "value": value,
            "splits": {split: sorted(filenames) for split, filenames in sorted(split_map.items())},
        }
        for value, split_map in sorted(value_to_splits.items())
        if len(split_map) > 1
    ]


def build_deepscores_leakage_report(split_manifests: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Check DeepScores split leakage and describe heuristic work-group overlap."""
    duplicate_ids = _duplicates_across_splits(
        split_manifests,
        lambda image: str(image.get("image_id")) if image.get("image_id") is not None else None,
    )
    duplicate_filenames = _duplicates_across_splits(
        split_manifests,
        lambda image: str(image.get("filename")).casefold() if image.get("filename") else None,
    )
    repeated_work_groups = _duplicates_across_splits(
        split_manifests,
        lambda image: infer_deepscores_work_group(str(image.get("filename"))),
    )

    status = "passed"
    if duplicate_ids or duplicate_filenames:
        status = "failed"
    elif repeated_work_groups:
        status = "warning"

    return {
        "dataset_id": "deepscores_136_manifest",
        "status": status,
        "checks": {
            "duplicate_image_ids": {
                "status": "failed" if duplicate_ids else "passed",
                "count": len(duplicate_ids),
                "duplicates": duplicate_ids,
            },
            "duplicate_filenames": {
                "status": "failed" if duplicate_filenames else "passed",
                "count": len(duplicate_filenames),
                "duplicates": duplicate_filenames,
            },
            "repeated_inferred_work_groups": {
                "status": "warning" if repeated_work_groups else "passed",
                "count": len(repeated_work_groups),
                "duplicates": repeated_work_groups,
                "heuristic": (
                    "DeepScores work groups are inferred from filename stems. "
                    "For names like lg-<work>-aug-<style>--page-<n>.png, the group is lg-<work>. "
                    "Other page-style names fall back to the prefix before a page marker."
                ),
            },
        },
    }


def write_yolo_dataset_yaml(output_dir: str | Path) -> Path:
    """Write a YOLO dataset YAML pointing at generated split image lists."""
    run_dir = Path(output_dir).resolve()
    yaml_path = run_dir / "yolo_dataset.yaml"
    lines = [
        f"path: {json.dumps(run_dir.as_posix())}",
        "train: generated/image_lists/train.txt",
        "val: generated/image_lists/val.txt",
        "test: generated/image_lists/test.txt",
        "nc: 136",
        "names:",
    ]
    for index, name in enumerate(DEEPSCORES_136_CLASS_NAMES):
        lines.append(f"  {index}: {json.dumps(name)}")
    lines.extend(
        [
            "label_note: "
            + json.dumps(
                "YOLO labels are generated under generated/labels/{split}. "
                "Raw images remain in the parent DeepScores dataset and are not copied into this repo."
            ),
        ]
    )
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def build_deepscores_manifest_run(
    *,
    train_json: str | Path,
    test_json: str | Path,
    output_dir: str | Path,
    image_root: str | Path,
    seed: int = 42,
    train_ratio: float = 0.9,
    val_ratio: float = 0.1,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build the full DeepScores 136-class manifest run."""
    run_dir = Path(output_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or utc_timestamp()

    source_train = Path(train_json).resolve()
    source_test = Path(test_json).resolve()
    train_coco = load_coco_json(source_train)
    test_coco = load_coco_json(source_test)

    split_images = deterministic_split(
        train_coco.get("images", []),
        (("train", train_ratio), ("val", val_ratio)),
        seed,
        image_sort_key,
    )
    split_images["test"] = sorted(test_coco.get("images", []), key=image_sort_key)

    split_manifests = {
        "train": build_deepscores_split_manifest(
            split_name="train",
            images=split_images["train"],
            coco=train_coco,
            source_json=source_train,
            output_dir=run_dir,
            image_root=image_root,
        ),
        "val": build_deepscores_split_manifest(
            split_name="val",
            images=split_images["val"],
            coco=train_coco,
            source_json=source_train,
            output_dir=run_dir,
            image_root=image_root,
        ),
        "test": build_deepscores_split_manifest(
            split_name="test",
            images=split_images["test"],
            coco=test_coco,
            source_json=source_test,
            output_dir=run_dir,
            image_root=image_root,
        ),
    }

    for split_name, manifest in split_manifests.items():
        write_json(run_dir / f"{split_name}.json", manifest)

    class_count_payload = {
        "dataset_id": "deepscores_136_manifest",
        "taxonomy_id": "deepscores_136",
        "class_count": len(DEEPSCORES_136_CLASS_NAMES),
        "splits": {
            split_name: {
                "image_count": manifest["image_count"],
                "annotation_count": manifest["annotation_count"],
                "label_count": manifest["label_count"],
                "classes_with_support": manifest["classes_with_support"],
                "class_counts": manifest["class_counts"],
            }
            for split_name, manifest in split_manifests.items()
        },
    }
    total_counter: Counter[str] = Counter()
    for split_payload in class_count_payload["splits"].values():
        total_counter.update(split_payload["class_counts"])
    class_count_payload["total"] = {
        class_name: int(total_counter[class_name]) for class_name in DEEPSCORES_136_CLASS_NAMES
    }
    write_json(run_dir / "class_counts.json", class_count_payload)

    leakage_report = build_deepscores_leakage_report(split_manifests)
    write_json(run_dir / "leakage_report.json", leakage_report)
    yolo_yaml = write_yolo_dataset_yaml(run_dir)

    manifest = {
        "dataset_id": "deepscores_136_manifest",
        "taxonomy_id": "deepscores_136",
        "class_count": len(DEEPSCORES_136_CLASS_NAMES),
        "seed": seed,
        "generated_at": generated_at,
        "split_policy": {
            "policy": "Preserve existing DeepScores test JSON; split existing train JSON into train/val.",
            "train_source_split": "deepscores_train.json",
            "test_source_split": "deepscores_test.json",
            "train_ratio_from_source_train": train_ratio,
            "val_ratio_from_source_train": val_ratio,
            "test_policy": "unchanged existing test JSON",
        },
        "source_paths": {
            "train_json": source_train.as_posix(),
            "test_json": source_test.as_posix(),
            "image_root": Path(image_root).resolve().as_posix(),
        },
        "outputs": {
            "run_dir": run_dir.resolve().as_posix(),
            "train_manifest": (run_dir / "train.json").resolve().as_posix(),
            "val_manifest": (run_dir / "val.json").resolve().as_posix(),
            "test_manifest": (run_dir / "test.json").resolve().as_posix(),
            "class_counts": (run_dir / "class_counts.json").resolve().as_posix(),
            "leakage_report": (run_dir / "leakage_report.json").resolve().as_posix(),
            "yolo_dataset_yaml": yolo_yaml.resolve().as_posix(),
            "generated_labels_root": (run_dir / "generated" / "labels").resolve().as_posix(),
        },
        "splits": {
            split_name: summarize_deepscores_split(split_manifest)
            for split_name, split_manifest in split_manifests.items()
        },
        "leakage_status": leakage_report["status"],
    }
    write_json(run_dir / "manifest.json", manifest)
    return manifest


MUSCIMA_WRITER_RE = re.compile(r"(W-\d+)")


def infer_muscima_writer_id(filename: str) -> str | None:
    """Infer MUSCIMA writer id from standard CVC-MUSCIMA filenames."""
    match = MUSCIMA_WRITER_RE.search(Path(filename).stem)
    return match.group(1) if match else None


def parse_muscima_page(path: str | Path) -> dict[str, Any]:
    """Parse lightweight MUSCIMA XML page metadata for manifesting."""
    xml_path = Path(path)
    page_id = xml_path.stem
    payload: dict[str, Any] = {
        "page_id": page_id,
        "filename": xml_path.name,
        "writer_id": infer_muscima_writer_id(xml_path.name),
        "source_path": xml_path.resolve().as_posix(),
        "node_count": None,
        "class_counts": {},
    }
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError as exc:
        payload["parse_error"] = str(exc)
        return payload

    class_counts: Counter[str] = Counter()
    for node in root.findall(".//Node"):
        class_name_node = node.find("ClassName")
        if class_name_node is not None and class_name_node.text:
            class_counts[class_name_node.text] += 1
        else:
            class_counts["<missing>"] += 1
    payload["node_count"] = int(sum(class_counts.values()))
    payload["class_counts"] = dict(sorted(class_counts.items()))
    return payload


def page_sort_key(page: dict[str, Any]) -> str:
    return str(page["page_id"])


def _compact_muscima_page(page: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "page_id": page["page_id"],
        "filename": page["filename"],
        "writer_id": page.get("writer_id"),
        "source_path": page["source_path"],
        "node_count": page.get("node_count"),
    }
    if page.get("parse_error"):
        compact["parse_error"] = page["parse_error"]
    return compact


def build_muscima_leakage_report(split_manifests: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Check duplicate MUSCIMA page ids across graph splits."""
    page_to_splits: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for split_name, manifest in split_manifests.items():
        for page in manifest.get("pages", []):
            page_to_splits[str(page["page_id"])][split_name].append(str(page["filename"]))
    duplicates = [
        {
            "page_id": page_id,
            "splits": {split: sorted(filenames) for split, filenames in sorted(split_map.items())},
        }
        for page_id, split_map in sorted(page_to_splits.items())
        if len(split_map) > 1
    ]
    return {
        "dataset_id": "muscima_graph_manifest",
        "status": "failed" if duplicates else "passed",
        "checks": {
            "duplicate_page_ids": {
                "status": "failed" if duplicates else "passed",
                "count": len(duplicates),
                "duplicates": duplicates,
            }
        },
    }


def build_muscima_manifest_run(
    *,
    annotations_dir: str | Path,
    output_dir: str | Path,
    seed: int = 42,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    holdout_ratio: float = 0.1,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Build the MUSCIMA graph page split manifest run."""
    source_dir = Path(annotations_dir).resolve()
    run_dir = Path(output_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    generated_at = generated_at or utc_timestamp()

    xml_paths = sorted(source_dir.glob("*.xml"), key=lambda path: path.name)
    pages = [parse_muscima_page(path) for path in xml_paths]
    split_pages = deterministic_split(
        pages,
        (("train", train_ratio), ("val", val_ratio), ("holdout", holdout_ratio)),
        seed,
        page_sort_key,
    )

    split_manifests: dict[str, dict[str, Any]] = {}
    for split_name in ("train", "val", "holdout"):
        split_records = [_compact_muscima_page(page) for page in split_pages[split_name]]
        node_total = sum(page.get("node_count") or 0 for page in split_records)
        manifest = {
            "dataset_id": "muscima_graph_manifest",
            "split": split_name,
            "seed": seed,
            "source_dir": source_dir.as_posix(),
            "page_count": len(split_records),
            "node_count": int(node_total),
            "pages": split_records,
        }
        split_manifests[split_name] = manifest
        write_json(run_dir / f"{split_name}.json", manifest)

    class_counter: Counter[str] = Counter()
    parse_errors: list[dict[str, str]] = []
    for page in pages:
        class_counter.update(page.get("class_counts", {}))
        if page.get("parse_error"):
            parse_errors.append({"page_id": page["page_id"], "parse_error": page["parse_error"]})
    class_summary = {
        "dataset_id": "muscima_graph_manifest",
        "source_dir": source_dir.as_posix(),
        "page_count": len(pages),
        "total_node_count": int(sum(class_counter.values())),
        "class_count": len(class_counter),
        "classes": dict(sorted(class_counter.items())),
        "parse_errors": parse_errors,
    }
    write_json(run_dir / "class_summary.json", class_summary)

    leakage_report = build_muscima_leakage_report(split_manifests)
    write_json(run_dir / "leakage_report.json", leakage_report)

    manifest = {
        "dataset_id": "muscima_graph_manifest",
        "seed": seed,
        "generated_at": generated_at,
        "split_policy": {
            "policy": "Use all MUSCIMA XML pages and split deterministically into train/val/holdout.",
            "train_ratio": train_ratio,
            "val_ratio": val_ratio,
            "holdout_ratio": holdout_ratio,
        },
        "source_paths": {"annotations_dir": source_dir.as_posix()},
        "outputs": {
            "run_dir": run_dir.resolve().as_posix(),
            "train_manifest": (run_dir / "train.json").resolve().as_posix(),
            "val_manifest": (run_dir / "val.json").resolve().as_posix(),
            "holdout_manifest": (run_dir / "holdout.json").resolve().as_posix(),
            "class_summary": (run_dir / "class_summary.json").resolve().as_posix(),
            "leakage_report": (run_dir / "leakage_report.json").resolve().as_posix(),
        },
        "splits": {
            split_name: {
                "split": split_manifest["split"],
                "page_count": split_manifest["page_count"],
                "node_count": split_manifest["node_count"],
            }
            for split_name, split_manifest in split_manifests.items()
        },
        "page_count": len(pages),
        "class_summary_available": True,
        "leakage_status": leakage_report["status"],
    }
    write_json(run_dir / "manifest.json", manifest)
    return manifest
