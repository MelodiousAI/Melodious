"""Validate docs do not directly compare mAP to F1."""

from __future__ import annotations

import argparse
from pathlib import Path

from melodious_v2.reports import assert_no_cross_metric_claims


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=["README.md", "docs", "MODEL_CARD.md"])
    args = parser.parse_args()

    checked = 0
    for raw_path in args.paths:
        path = Path(raw_path)
        files = [path] if path.is_file() else sorted(path.glob("**/*.md"))
        for file_path in files:
            assert_no_cross_metric_claims(file_path.read_text(encoding="utf-8"))
            checked += 1
    print(f"Checked {checked} documentation files.")


if __name__ == "__main__":
    main()

