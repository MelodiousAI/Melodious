"""Checkpoint-aware GNN inference scaffolding for Week 4 integration work.

This module intentionally stops short of hard-coding Ahmad's final model
architecture. It provides a stable runtime contract for:

- reporting checkpoint readiness to the API and UI
- resolving requested assembly modes (`auto`, `heuristic`, `gnn`)
- cleanly falling back when GNN inference is not yet available
- reserving a placeholder attention-preview surface for later visualization
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_ENV_VAR = "MELODIOUS_GNN_CHECKPOINT"


@dataclass(frozen=True)
class GnnRuntimeStatus:
    """Checkpoint and adapter readiness snapshot for API status endpoints."""

    adapter_name: str
    adapter_ready: bool
    checkpoint_configured: bool
    checkpoint_path: str | None
    checkpoint_exists: bool
    ready: bool
    message: str


@dataclass(frozen=True)
class AssemblyModeDecision:
    """Resolved backend mode for one request after readiness checks."""

    requested_mode: str
    applied_mode: str
    fallback_applied: bool
    fallback_reason: str | None
    checkpoint_ready: bool
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AttentionPreview:
    """Future-facing attention preview surface for the API/UI contract."""

    available: bool
    source: str
    message: str
    top_edges: list[dict[str, Any]] = field(default_factory=list)


class GnnAssemblyAdapter(Protocol):
    """Minimal adapter contract for Ahmad's future trained checkpoint."""

    name: str

    def is_ready(self) -> bool:
        """Return whether this adapter can execute live inference."""

    def predict(
        self,
        graph_data: Any,
        detection_sequence: list[dict[str, Any]],
        document_name: str | None = None,
    ) -> dict[str, Any]:
        """Return model outputs for one graph request."""


class StubGnnAssemblyAdapter:
    """Placeholder adapter until Ahmad's model-specific wiring lands."""

    name = "checkpoint-scaffold"

    def is_ready(self) -> bool:
        return False

    def predict(
        self,
        graph_data: Any,
        detection_sequence: list[dict[str, Any]],
        document_name: str | None = None,
    ) -> dict[str, Any]:
        raise RuntimeError(
            "The Week 4 GNN scaffold is present, but Ahmad's checkpoint-specific adapter is not integrated yet."
        )


class GnnAssemblyService:
    """Resolve GNN readiness and mode selection without hard-coding model internals."""

    def __init__(
        self,
        checkpoint_path: str | os.PathLike[str] | None = None,
        adapter: GnnAssemblyAdapter | None = None,
    ) -> None:
        self._checkpoint_path = checkpoint_path
        self._adapter = adapter or StubGnnAssemblyAdapter()

    def resolve_checkpoint_path(self) -> Path | None:
        """Resolve the configured checkpoint path relative to the repo when needed."""
        checkpoint_value = self._checkpoint_path

        if checkpoint_value is None:
            checkpoint_value = os.getenv(CHECKPOINT_ENV_VAR)

        if not checkpoint_value:
            return None

        checkpoint_path = Path(checkpoint_value).expanduser()

        if not checkpoint_path.is_absolute():
            checkpoint_path = PROJECT_ROOT / checkpoint_path

        return checkpoint_path

    def get_runtime_status(self) -> GnnRuntimeStatus:
        """Return current checkpoint and adapter readiness information."""
        checkpoint_path = self.resolve_checkpoint_path()
        checkpoint_configured = checkpoint_path is not None
        checkpoint_exists = bool(checkpoint_path and checkpoint_path.exists())
        adapter_ready = self._adapter.is_ready()
        ready = checkpoint_configured and checkpoint_exists and adapter_ready

        if ready:
            message = "GNN checkpoint and adapter are ready for inference."
        elif not checkpoint_configured:
            message = (
                f"GNN checkpoint not configured. Set {CHECKPOINT_ENV_VAR} once Ahmad provides a trained checkpoint."
            )
        elif not checkpoint_exists:
            message = f"Configured GNN checkpoint was not found at {checkpoint_path}."
        else:
            message = (
                "A checkpoint path is configured, but the model-specific adapter is still a scaffold."
            )

        return GnnRuntimeStatus(
            adapter_name=self._adapter.name,
            adapter_ready=adapter_ready,
            checkpoint_configured=checkpoint_configured,
            checkpoint_path=str(checkpoint_path) if checkpoint_path else None,
            checkpoint_exists=checkpoint_exists,
            ready=ready,
            message=message,
        )

    def resolve_assembly_mode(self, requested_mode: str) -> AssemblyModeDecision:
        """Resolve `auto`, `heuristic`, or `gnn` into the mode this backend can run."""
        status = self.get_runtime_status()
        warnings: list[str] = []

        if requested_mode == "heuristic":
            return AssemblyModeDecision(
                requested_mode=requested_mode,
                applied_mode="heuristic",
                fallback_applied=False,
                fallback_reason=None,
                checkpoint_ready=status.ready,
                warnings=warnings,
            )

        if requested_mode == "gnn":
            if status.ready:
                return AssemblyModeDecision(
                    requested_mode=requested_mode,
                    applied_mode="gnn",
                    fallback_applied=False,
                    fallback_reason=None,
                    checkpoint_ready=True,
                    warnings=warnings,
                )

            fallback_reason = status.message
            warnings.append(f"GNN mode requested but unavailable. Falling back to heuristic mode. {fallback_reason}")
            return AssemblyModeDecision(
                requested_mode=requested_mode,
                applied_mode="heuristic",
                fallback_applied=True,
                fallback_reason=fallback_reason,
                checkpoint_ready=False,
                warnings=warnings,
            )

        if status.ready:
            return AssemblyModeDecision(
                requested_mode=requested_mode,
                applied_mode="gnn",
                fallback_applied=False,
                fallback_reason=None,
                checkpoint_ready=True,
                warnings=warnings,
            )

        return AssemblyModeDecision(
            requested_mode=requested_mode,
            applied_mode="heuristic",
            fallback_applied=False,
            fallback_reason=None,
            checkpoint_ready=False,
            warnings=warnings,
        )

    def build_attention_preview(self, mode_decision: AssemblyModeDecision) -> AttentionPreview:
        """Return a stable attention-preview payload even before real GAT attention exists."""
        if mode_decision.applied_mode == "gnn" and mode_decision.checkpoint_ready:
            return AttentionPreview(
                available=False,
                source="placeholder",
                message=(
                    "The GNN path is enabled, but Ahmad's checkpoint adapter has not provided attention weights yet."
                ),
                top_edges=[],
            )

        if mode_decision.requested_mode == "gnn" and mode_decision.fallback_applied:
            return AttentionPreview(
                available=False,
                source="placeholder",
                message="Real GNN attention is unavailable because the request fell back to heuristic mode.",
                top_edges=[],
            )

        return AttentionPreview(
            available=False,
            source="placeholder",
            message="Attention preview is reserved for the future GNN checkpoint integration.",
            top_edges=[],
        )
