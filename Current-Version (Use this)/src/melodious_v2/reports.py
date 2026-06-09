"""Generated report helpers and metric-claim guardrails."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from melodious_v2.contracts import MetricProvenance


BAD_CROSS_METRIC_PATTERNS = [
    re.compile(r"mAP(?:@?50|@0\.5)?\s*[<>=]+\s*[^\n]*(?:F1|f1)", re.IGNORECASE),
    re.compile(r"(?:F1|f1)\s*[<>=]+\s*[^\n]*(?:mAP|map)", re.IGNORECASE),
]


def assert_no_cross_metric_claims(text: str) -> None:
    """Reject prose that compares mAP directly to F1."""
    for pattern in BAD_CROSS_METRIC_PATTERNS:
        match = pattern.search(text)
        if match:
            raise ValueError(f"Invalid cross-metric comparison: {match.group(0)!r}")


def write_run_report(
    run_dir: str | Path,
    provenance: MetricProvenance,
    metrics: dict[str, Any],
) -> None:
    """Write generated metrics and a compact Markdown report for one run."""
    root = Path(run_dir)
    root.mkdir(parents=True, exist_ok=True)
    metrics_payload = {
        "provenance": provenance.model_dump(mode="json"),
        "metrics": metrics,
    }
    (root / "metrics.json").write_text(
        json.dumps(metrics_payload, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    metric_name = metrics.get("primary_metric", "unknown")
    metric_value = metrics.get(metric_name, "n/a")
    secondary_metric_names = [
        "mAP@0.5",
        "precision@0.5",
        "recall@0.5",
        "F1@0.5",
    ]
    secondary_lines = [
        f"- `{name}`: `{metrics[name]}`"
        for name in secondary_metric_names
        if name in metrics and name != metric_name
    ]
    secondary_section = ""
    if secondary_lines:
        secondary_section = "\n## Secondary Metrics\n\n" + "\n".join(secondary_lines) + "\n"
    report = (
        f"# Run {provenance.run_id}\n\n"
        f"- Primary metric: `{metric_name}`\n"
        f"- Primary value: `{metric_value}`\n"
        f"- Dataset: `{provenance.dataset_id}`\n"
        f"- Split: `{provenance.split}`\n"
        f"- Config: `{provenance.config_path}`\n"
        f"- Taxonomy: `{provenance.taxonomy_id}`\n"
        f"{secondary_section}"
    )
    assert_no_cross_metric_claims(report)
    (root / "report.md").write_text(report, encoding="utf-8")
