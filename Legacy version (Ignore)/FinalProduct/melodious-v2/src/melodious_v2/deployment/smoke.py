"""Smoke-test helpers for local and public Melodious V2 API deployments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Protocol

import httpx
from fastapi.testclient import TestClient

from melodious_v2.api.app import app
from melodious_v2.utils import sha256_bytes


class ResponseLike(Protocol):
    status_code: int
    content: bytes
    headers: dict[str, str]

    def json(self) -> Any:
        ...


class ClientLike(Protocol):
    def get(self, url: str) -> ResponseLike:
        ...

    def post(self, url: str, *, json: dict[str, Any]) -> ResponseLike:
        ...


def _require_status(response: ResponseLike, expected: int, label: str) -> None:
    if response.status_code != expected:
        raise RuntimeError(f"{label} returned {response.status_code}, expected {expected}")


def _artifact_uri_for(payload: dict[str, Any], artifact_type: str) -> str:
    for artifact in payload.get("artifacts", []):
        if artifact.get("artifact_type") == artifact_type and artifact.get("uri"):
            return artifact["uri"]
    raise RuntimeError(f"Transcription response did not include a {artifact_type} artifact URI")


def run_api_smoke(
    client: ClientLike,
    *,
    api_base_url: str,
    sample_id: str | None = None,
    requested_assembly_mode: str = "auto",
    artifact_types: tuple[str, ...] = ("musicxml", "midi"),
) -> dict[str, Any]:
    """Run the public-demo API smoke contract against an HTTP-like client."""
    health_response = client.get("/health")
    _require_status(health_response, 200, "/health")
    health = health_response.json()
    if health.get("status") != "ok":
        raise RuntimeError(f"/health returned non-ok status: {health!r}")

    version_response = client.get("/version")
    _require_status(version_response, 200, "/version")
    version = version_response.json()
    if not version.get("schema_version"):
        raise RuntimeError("/version did not include schema_version")

    samples_response = client.get("/samples")
    _require_status(samples_response, 200, "/samples")
    samples = samples_response.json()
    if not samples:
        raise RuntimeError("/samples returned no sample records")
    selected_sample = sample_id or samples[0]["sample_id"]

    transcription_response = client.post(
        "/transcriptions",
        json={
            "sample_id": selected_sample,
            "requested_assembly_mode": requested_assembly_mode,
        },
    )
    _require_status(transcription_response, 200, "/transcriptions sample request")
    transcription = transcription_response.json()
    if transcription.get("status") != "complete":
        raise RuntimeError(f"Sample transcription did not complete: {transcription!r}")

    artifact_checks: list[dict[str, Any]] = []
    for artifact_type in artifact_types:
        artifact_uri = _artifact_uri_for(transcription, artifact_type)
        artifact_response = client.get(artifact_uri)
        _require_status(artifact_response, 200, f"artifact download {artifact_type}")
        if not artifact_response.content:
            raise RuntimeError(f"Downloaded {artifact_type} artifact was empty")
        artifact_checks.append(
            {
                "artifact_type": artifact_type,
                "uri": artifact_uri,
                "status_code": artifact_response.status_code,
                "content_type": artifact_response.headers.get("content-type"),
                "byte_count": len(artifact_response.content),
                "sha256": sha256_bytes(artifact_response.content),
            }
        )

    return {
        "api_base_url": api_base_url.rstrip("/") if api_base_url != "local-testclient" else api_base_url,
        "health": {
            "status": health.get("status"),
            "service": health.get("service"),
            "version": health.get("version"),
            "environment": health.get("environment"),
            "detector_modes": health.get("detector_modes", []),
            "assembly_modes": health.get("assembly_modes", []),
        },
        "version": {
            "version": version.get("version"),
            "schema_version": version.get("schema_version"),
            "detector_taxonomy": version.get("detector_taxonomy"),
            "semantic_taxonomy": version.get("semantic_taxonomy"),
        },
        "sample_transcription": {
            "sample_id": selected_sample,
            "job_id": transcription.get("job_id"),
            "status": transcription.get("status"),
            "detector_mode": transcription.get("detector_mode"),
            "assembly_mode": transcription.get("assembly_mode"),
            "detection_count": transcription.get("detection_count"),
            "relationship_count": transcription.get("relationship_count"),
            "warnings": transcription.get("warnings", []),
        },
        "artifact_downloads": artifact_checks,
        "passed": True,
    }


def run_local_testclient_smoke(
    *,
    sample_id: str | None = None,
    requested_assembly_mode: str = "auto",
) -> dict[str, Any]:
    """Run the smoke contract in-process without starting Uvicorn."""
    return run_api_smoke(
        TestClient(app),
        api_base_url="local-testclient",
        sample_id=sample_id,
        requested_assembly_mode=requested_assembly_mode,
    )


def run_http_smoke(
    api_base_url: str,
    *,
    sample_id: str | None = None,
    requested_assembly_mode: str = "auto",
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Run the smoke contract against a live API base URL."""
    with httpx.Client(base_url=api_base_url.rstrip("/"), timeout=timeout_seconds) as client:
        return run_api_smoke(
            client,
            api_base_url=api_base_url,
            sample_id=sample_id,
            requested_assembly_mode=requested_assembly_mode,
        )


def write_smoke_result(path: str | Path, result: dict[str, Any]) -> None:
    """Write smoke-test evidence as stable JSON."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-base-url", help="Live API base URL, for example https://api.example.com")
    parser.add_argument(
        "--local-testclient",
        action="store_true",
        help="Run against the FastAPI app in-process instead of a live URL.",
    )
    parser.add_argument("--sample-id", default=None)
    parser.add_argument(
        "--requested-assembly-mode",
        default="auto",
        choices=["auto", "heuristic", "gnn"],
    )
    parser.add_argument("--output", default=None, help="Optional JSON evidence path.")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if bool(args.api_base_url) == bool(args.local_testclient):
        raise SystemExit("Provide exactly one of --api-base-url or --local-testclient.")

    if args.local_testclient:
        result = run_local_testclient_smoke(
            sample_id=args.sample_id,
            requested_assembly_mode=args.requested_assembly_mode,
        )
    else:
        result = run_http_smoke(
            args.api_base_url,
            sample_id=args.sample_id,
            requested_assembly_mode=args.requested_assembly_mode,
        )

    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        write_smoke_result(args.output, result)
    print(text)


if __name__ == "__main__":
    main()

