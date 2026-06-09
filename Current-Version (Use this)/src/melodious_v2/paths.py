"""Shared project path helpers."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNS_DIR = PROJECT_ROOT / "runs"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

