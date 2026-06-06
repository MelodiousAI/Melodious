"""Shared path helpers for the copied demo submission package.

The demo folder is a submission-oriented copy of the main repository. Large
processed datasets may live either inside the demo package itself or one level
up in the parent repository checkout. These helpers let runtime code prefer the
local demo copy while still falling back to the shared parent-repo assets when
they are intentionally not duplicated.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PARENT_REPO_ROOT = PROJECT_ROOT.parent


def get_asset_search_roots() -> list[Path]:
    """Return the roots searched for read-only assets."""
    search_roots = [PROJECT_ROOT]

    if PARENT_REPO_ROOT != PROJECT_ROOT and (PARENT_REPO_ROOT / ".git").exists():
        search_roots.append(PARENT_REPO_ROOT)

    return search_roots


def resolve_existing_asset_path(*relative_parts: str) -> Path:
    """Resolve an asset path from the demo package or parent repo.

    The first existing match wins. If nothing exists yet, return the demo-local
    path so callers that intend to create files still write inside `demo/`.
    """
    for root in get_asset_search_roots():
        candidate = root.joinpath(*relative_parts)
        if candidate.exists():
            return candidate

    return PROJECT_ROOT.joinpath(*relative_parts)
