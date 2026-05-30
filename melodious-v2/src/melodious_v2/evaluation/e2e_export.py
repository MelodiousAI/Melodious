"""End-to-end export evaluation helpers for fixed MUSCIMA fixtures."""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from melodious_v2.assembly.legacy_gnn import parse_muscima_xml
from melodious_v2.assembly.service import assemble_payload
from melodious_v2.contracts import (
    DetectionV2,
    DetectorPayloadV2,
    ImageSize,
    MetricProvenance,
    NormalizedBBox,
    PixelBBox,
)
from melodious_v2.export.musicxml import minimal_midi_base64, payload_to_musicxml, validate_musicxml
from melodious_v2.reports import assert_no_cross_metric_claims, write_run_report
from melodious_v2.taxonomies import DEEPSCORES_136_NAME_TO_ID
from melodious_v2.utils import sha256_bytes, sha256_file


MUSCIMA_TO_DEEPSCORES_136: dict[str, str] = {
    "noteheadFull": "noteheadBlackOnLine",
    "noteheadFullSmall": "noteheadBlackOnLineSmall",
    "noteheadHalf": "noteheadHalfOnLine",
    "noteheadHalfSmall": "noteheadHalfOnLineSmall",
    "noteheadWhole": "noteheadWholeOnLine",
    "gClef": "clefG",
    "fClef": "clefF",
    "cClef": "clefCAlto",
    "rest8th": "rest8th",
    "8thRest": "rest8th",
    "restQuarter": "restQuarter",
    "quarterRest": "restQuarter",
    "restHalf": "restHalf",
    "halfRest": "restHalf",
    "restWhole": "restWhole",
    "wholeRest": "restWhole",
    "accidentalSharp": "accidentalSharp",
    "accidentalFlat": "accidentalFlat",
    "accidentalNatural": "accidentalNatural",
    "beam": "beam",
    "stem": "stem",
    "slur": "slur",
    "tie": "tie",
}


@dataclass(frozen=True)
class PayloadBuildSummary:
    """Summary of one XML-to-payload conversion."""

    page_id: str
    source_xml: str
    parsed_node_count: int
    mapped_detection_count: int
    skipped_node_count: int
    mapped_class_counts: dict[str, int]
    skipped_class_counts: dict[str, int]


@dataclass(frozen=True)
class PageExportResult:
    """End-to-end result for one fixed page."""

    page_id: str
    source_xml: str
    detector_mode: str
    assembly_mode: dict[str, Any]
    detection_count: int
    note_like_count: int
    relationship_count: int
    musicxml_valid: bool
    midi_generated: bool
    page_success: bool
    failure_reasons: list[str]
    artifacts: dict[str, dict[str, Any]]
    payload_summary: dict[str, Any] = field(default_factory=dict)


def git_commit(repo_root: Path) -> str:
    """Return the short Git commit for the parent repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return "unknown"
    return result.stdout.strip()


def load_json(path: Path) -> dict[str, Any]:
    """Read a UTF-8 JSON file."""
    return json.loads(path.read_text(encoding="utf-8"))


def _increment(counter: dict[str, int], key: str) -> None:
    counter[key] = counter.get(key, 0) + 1


def muscima_xml_to_detector_payload(
    xml_path: Path,
    run_id: str,
    page_id: str | None = None,
    model_id: str = "muscima_xml_ground_truth_payload_fixture",
) -> tuple[DetectorPayloadV2, PayloadBuildSummary]:
    """Build a detector-like V2 payload from MUSCIMA XML annotations.

    This is an evaluation fixture path, not trained detector inference.
    """
    nodes = parse_muscima_xml(xml_path)
    page_name = page_id or xml_path.stem
    if nodes:
        max_x = max(node.left + node.width for node in nodes)
        max_y = max(node.top + node.height for node in nodes)
    else:
        max_x = max_y = 1
    page_width = max(int(max_x * 1.05), 1)
    page_height = max(int(max_y * 1.05), 1)

    detections: list[DetectionV2] = []
    mapped_counts: dict[str, int] = {}
    skipped_counts: dict[str, int] = {}
    for node in sorted(nodes, key=lambda item: (item.top, item.left, item.node_id)):
        class_name = MUSCIMA_TO_DEEPSCORES_136.get(node.class_name)
        if class_name is None:
            _increment(skipped_counts, node.class_name or "unknown")
            continue
        _increment(mapped_counts, class_name)
        x_center = (node.left + node.width / 2) / page_width
        y_center = (node.top + node.height / 2) / page_height
        width = max(node.width / page_width, 1e-6)
        height = max(node.height / page_height, 1e-6)
        detections.append(
            DetectionV2(
                class_id=DEEPSCORES_136_NAME_TO_ID[class_name],
                class_name=class_name,
                confidence=1.0,
                bbox=NormalizedBBox(
                    x_center=min(max(x_center, 0.0), 1.0),
                    y_center=min(max(y_center, 0.0), 1.0),
                    width=min(width, 1.0),
                    height=min(height, 1.0),
                ),
                bbox_pixels=PixelBBox(
                    x1=max(float(node.left), 0.0),
                    y1=max(float(node.top), 0.0),
                    x2=max(float(node.left + node.width), float(node.left) + 1.0),
                    y2=max(float(node.top + node.height), float(node.top) + 1.0),
                ),
            )
        )

    payload = DetectorPayloadV2(
        run_id=f"{run_id}:{page_name}",
        model_id=model_id,
        taxonomy_id="deepscores_136",
        image_size=ImageSize(width=page_width, height=page_height),
        detections=detections,
        source_image_uri=str(xml_path),
    )
    summary = PayloadBuildSummary(
        page_id=page_name,
        source_xml=str(xml_path),
        parsed_node_count=len(nodes),
        mapped_detection_count=len(detections),
        skipped_node_count=len(nodes) - len(detections),
        mapped_class_counts=dict(sorted(mapped_counts.items())),
        skipped_class_counts=dict(sorted(skipped_counts.items())),
    )
    return payload, summary


def evaluate_page_export(
    payload: DetectorPayloadV2,
    payload_summary: PayloadBuildSummary,
    page_dir: Path,
    requested_assembly_mode: str,
    checkpoint_path: Path | None,
) -> PageExportResult:
    """Run one detector payload through assembly, MusicXML, and MIDI export."""
    page_dir.mkdir(parents=True, exist_ok=True)
    failure_reasons: list[str] = []
    assembly_mode, relationships = assemble_payload(
        payload,
        requested_mode=requested_assembly_mode,
        checkpoint_path=str(checkpoint_path) if checkpoint_path else None,
    )

    musicxml = payload_to_musicxml(payload, relationships, title=payload_summary.page_id)
    musicxml_valid = validate_musicxml(musicxml)
    if not musicxml_valid:
        failure_reasons.append("musicxml_validation_failed")

    midi_bytes = b""
    midi_generated = False
    try:
        midi_bytes = base64.b64decode(minimal_midi_base64(), validate=True)
        midi_generated = bool(midi_bytes.startswith(b"MThd"))
    except Exception as exc:
        failure_reasons.append(f"midi_generation_failed: {exc}")
    if not midi_generated and not any(reason.startswith("midi_generation_failed") for reason in failure_reasons):
        failure_reasons.append("midi_generation_failed: invalid MIDI header")

    musicxml_path = page_dir / f"{payload_summary.page_id}.musicxml"
    midi_path = page_dir / f"{payload_summary.page_id}.mid"
    payload_path = page_dir / f"{payload_summary.page_id}.payload.json"
    relationships_path = page_dir / f"{payload_summary.page_id}.relationships.json"

    musicxml_path.write_text(musicxml, encoding="utf-8")
    midi_path.write_bytes(midi_bytes)
    payload_path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    relationships_payload = [asdict(relationship) for relationship in relationships]
    relationships_path.write_text(json.dumps(relationships_payload, indent=2), encoding="utf-8")

    artifacts = {
        "musicxml": {
            "path": str(musicxml_path),
            "sha256": sha256_bytes(musicxml.encode("utf-8")),
            "content_type": "application/vnd.recordare.musicxml+xml",
        },
        "midi": {
            "path": str(midi_path),
            "sha256": sha256_bytes(midi_bytes),
            "content_type": "audio/midi",
        },
        "payload": {
            "path": str(payload_path),
            "sha256": sha256_bytes(payload_path.read_bytes()),
            "content_type": "application/json",
        },
        "relationships": {
            "path": str(relationships_path),
            "sha256": sha256_bytes(relationships_path.read_bytes()),
            "content_type": "application/json",
        },
    }
    note_like_count = sum(
        1 for detection in payload.detections if detection.semantic_group in {"notehead", "rest"}
    )
    return PageExportResult(
        page_id=payload_summary.page_id,
        source_xml=payload_summary.source_xml,
        detector_mode=payload.model_id,
        assembly_mode=asdict(assembly_mode),
        detection_count=len(payload.detections),
        note_like_count=note_like_count,
        relationship_count=len(relationships),
        musicxml_valid=musicxml_valid,
        midi_generated=midi_generated,
        page_success=musicxml_valid and midi_generated,
        failure_reasons=failure_reasons,
        artifacts=artifacts,
        payload_summary=asdict(payload_summary),
    )


def summarize_page_results(page_results: list[PageExportResult]) -> dict[str, Any]:
    """Aggregate page-level M5 export metrics."""
    page_count = len(page_results)
    musicxml_valid_count = sum(1 for result in page_results if result.musicxml_valid)
    midi_success_count = sum(1 for result in page_results if result.midi_generated)
    page_success_count = sum(1 for result in page_results if result.page_success)
    gnn_pages = sum(1 for result in page_results if result.assembly_mode.get("applied_mode") == "gnn")
    total_relationships = sum(result.relationship_count for result in page_results)
    total_detections = sum(result.detection_count for result in page_results)
    total_note_like = sum(result.note_like_count for result in page_results)
    failures = [
        {
            "page_id": result.page_id,
            "failure_reasons": result.failure_reasons,
            "assembly_mode": result.assembly_mode,
        }
        for result in page_results
        if result.failure_reasons
    ]
    return {
        "primary_metric": "musicxml_validity_rate",
        "musicxml_validity_rate": musicxml_valid_count / page_count if page_count else 0.0,
        "midi_generation_success_rate": midi_success_count / page_count if page_count else 0.0,
        "page_success_rate": page_success_count / page_count if page_count else 0.0,
        "page_count": page_count,
        "musicxml_valid_count": musicxml_valid_count,
        "midi_success_count": midi_success_count,
        "page_success_count": page_success_count,
        "failure_count": len(failures),
        "detector_mode": "muscima_xml_ground_truth_payload_fixture",
        "assembly_gnn_page_rate": gnn_pages / page_count if page_count else 0.0,
        "assembly_gnn_page_count": gnn_pages,
        "relationship_count_total": total_relationships,
        "relationship_count_mean": total_relationships / page_count if page_count else 0.0,
        "detection_count_total": total_detections,
        "detection_count_mean": total_detections / page_count if page_count else 0.0,
        "note_like_count_total": total_note_like,
        "note_like_count_mean": total_note_like / page_count if page_count else 0.0,
        "metric_kind": "measured_export_validity_with_ground_truth_xml_payloads",
        "failures": failures,
        "notes": [
            "This M5 run measures export validity and artifact generation from MUSCIMA XML-derived detector payload fixtures.",
            "It is not a measured trained-detector uploaded-image run.",
            "Uploaded-image detector inference remains heuristic_bootstrap unless a tested ONNX adapter is added.",
        ],
    }


def write_e2e_run_outputs(
    run_dir: Path,
    provenance: MetricProvenance,
    metrics: dict[str, Any],
    page_results: list[PageExportResult],
    source_manifest_path: Path,
    split_manifest_path: Path,
    config_path: Path,
    upstream_artifacts: dict[str, Any],
) -> None:
    """Write standard M5 run files after page exports have been generated."""
    run_dir.mkdir(parents=True, exist_ok=True)
    write_run_report(run_dir, provenance, metrics)
    manifest = {
        "run_id": provenance.run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_manifest": str(source_manifest_path),
        "split_manifest": str(split_manifest_path),
        "split": provenance.split,
        "page_results": [asdict(result) for result in page_results],
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    artifacts = {
        "run_id": provenance.run_id,
        "metrics": str(run_dir / "metrics.json"),
        "report": str(run_dir / "report.md"),
        "manifest": str(run_dir / "manifest.json"),
        "exports_dir": str(run_dir / "exports"),
        "config": {
            "path": str(config_path),
            "sha256": sha256_file(config_path) if config_path.exists() else None,
            "copied_to": str(run_dir / "config.yaml"),
        },
        "upstream_artifacts": upstream_artifacts,
        "page_artifacts": {
            result.page_id: result.artifacts
            for result in page_results
        },
    }
    (run_dir / "artifacts.json").write_text(
        json.dumps(artifacts, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    if config_path.exists():
        shutil.copyfile(config_path, run_dir / "config.yaml")

    custom_report = [
        f"# Run {provenance.run_id}",
        "",
        "- Primary metric: `musicxml_validity_rate`",
        f"- Primary value: `{metrics['musicxml_validity_rate']}`",
        "- Metric kind: `measured_export_validity_with_ground_truth_xml_payloads`",
        f"- Dataset: `{provenance.dataset_id}`",
        f"- Split: `{provenance.split}`",
        f"- Page count: `{metrics['page_count']}`",
        f"- MusicXML valid pages: `{metrics['musicxml_valid_count']}`",
        f"- MIDI success pages: `{metrics['midi_success_count']}`",
        f"- Page success rate: `{metrics['page_success_rate']}`",
        f"- Assembly GNN pages: `{metrics['assembly_gnn_page_count']}`",
        f"- Relationship count total: `{metrics['relationship_count_total']}`",
        "",
        "## Scope",
        "",
        "This run uses MUSCIMA XML-derived detector payload fixtures. It measures export validity and artifact generation, not trained detector uploaded-image quality.",
        "",
        "## Failures",
        "",
    ]
    if metrics["failures"]:
        for failure in metrics["failures"]:
            custom_report.append(
                f"- `{failure['page_id']}`: `{'; '.join(failure['failure_reasons'])}`"
            )
    else:
        custom_report.append("- none")
    report_text = "\n".join(custom_report) + "\n"
    assert_no_cross_metric_claims(report_text)
    (run_dir / "report.md").write_text(report_text, encoding="utf-8")
