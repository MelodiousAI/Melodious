"""Generate docs/EXPERIMENTS.md from run metric artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dir", default="runs")
    parser.add_argument("--output", default="docs/EXPERIMENTS.md")
    args = parser.parse_args()

    rows = []
    for metrics_path in sorted(Path(args.runs_dir).glob("**/metrics.json")):
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        provenance = payload.get("provenance", {})
        metrics = payload.get("metrics", {})
        primary = metrics.get("primary_metric", "unknown")
        rows.append(
            (
                provenance.get("run_id", metrics_path.parent.name),
                provenance.get("dataset_id", ""),
                provenance.get("split", ""),
                primary,
                metrics.get(primary, ""),
                str(metrics_path),
            )
        )

    lines = [
        "# Experiments",
        "",
        "Generated from `runs/**/metrics.json`. Do not hand-edit metric values.",
        "",
        "| run_id | dataset | split | primary metric | value | metrics file |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    if not rows:
        lines.append("| none | | | | | |")

    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

