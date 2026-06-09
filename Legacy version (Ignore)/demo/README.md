# Melodious

Melodious is an optical music recognition (OMR) project built around MUSCIMA++.

This consolidation branch intentionally excludes the `feature/eval-improvements` branch family. It combines `origin/main` with Hasan's live `hassan/week-5` branch, which already contains `hassan/week-1` through `hassan/week-4`.

## What Is Implemented

- `src/data_prep/parse_muscima.py`: parses MUSCIMA++ XML annotations into JSON-friendly node and edge files.
- `src/data_prep/class_mapping.py`: builds and saves a stable class-name to class-id mapping for parsed MUSCIMA nodes.
- `src/data_prep/staff_detection.py`: detects staff regions from grayscale score images and can save debug overlays.
- `src/data_prep/shared_detection_contract.py`: stores the shared MUSCIMA-to-detector class mapping reused by payload and training exports.
- `src/graph/muscima_graph_builder.py`: builds document-level reference graph JSON files from MUSCIMA data.
- `src/graph/pyg_graph_builder.py`: builds GNN-ready graphs from detection dictionaries.
- `src/graph/detection_alignment.py`: aligns detections to MUSCIMA ground-truth nodes using greedy IoU matching.
- `src/evaluation/muscima_reference_evaluation.py`: runs graph building plus alignment on the shared MUSCIMA reference payloads.
- `src/evaluation/muscima_training_export.py`: exports one JSON per MUSCIMA page for GNN supervision with `edge_type` and `edge_label`.
- `src/api/`: FastAPI backend routes for health, graph assembly, MIDI export, and public product samples.
- `src/inference/gnn_service.py`: checkpoint-readiness and heuristic-fallback scaffolding for GNN mode.
- `src/ui/streamlit_app.py`: internal/debug Streamlit MVP.
- `frontend/`: React + Vite + Tailwind public product frontend.
- `tools/`: helper scripts for MUSCIMA payload and training-data export.

## Repo Structure

- `src/`: backend, data prep, graph, export, inference, and UI modules.
- `tools/`: workflow helper scripts.
- `tests/`: unit tests for API, graph, data prep, export, evaluation, and inference scaffold modules.
- `docs/status/`: Hasan-side status and experiment documentation.
- `docker/`: backend Docker build files.
- `frontend/`: public Week 5 product UI.
- `sample_detections/`: detector payload examples, MUSCIMA reference payloads, and XML samples.

## Local Data Layout

This checkout uses the local dataset layout already present on this machine:

- MUSCIMA++ XML annotations: `data/muscima-pp/v2.0/data/annotations`
- CVC-MUSCIMA grayscale images: `data/cvc-muscima/CVCMUSCIMA_WI/PNG_GT_Gray`
- Processed parsed JSONs: `data/processed/muscima_nodes.json` and `data/processed/muscima_edges.json`

The data and generated outputs are ignored by Git.

When `demo/` is nested inside the full repository, read-only MUSCIMA assets now
resolve from `demo/data/...` first and fall back to the parent checkout if the
copied package intentionally omits large processed files. Newly generated smoke
artifacts still write inside `demo/`.

## Main Commands

```powershell
.\.venv\Scripts\python.exe -m src.data_prep.parse_muscima --limit 5
.\.venv\Scripts\python.exe -m src.data_prep.class_mapping
.\.venv\Scripts\python.exe -m src.graph.muscima_graph_builder --limit 5
.\.venv\Scripts\python.exe -m src.evaluation.muscima_reference_evaluation
.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
cd frontend
npm test
npm run build
```

## Reproduce Results in 15 Minutes

Use this section as the canonical deterministic run path for checkpoint review and rubric grading.

1) **Create/activate environment (Windows PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) **Set deterministic seeds for local reruns**

```powershell
$env:PYTHONHASHSEED="42"
$env:CUBLAS_WORKSPACE_CONFIG=":16:8"
```

3) **Run core backend tests**

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
```

Expected: all discovered tests pass.

4) **Run frontend verification**

```powershell
cd frontend
npm install
npm test
npm run build
cd ..
```

Expected: test suite passes and production build succeeds.

5) **Run API smoke test**

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

Expected: `GET /health` returns service status JSON including assembly mode information.

6) **Run evaluation/export smoke**

```powershell
.\.venv\Scripts\python.exe -m src.evaluation.muscima_reference_evaluation
.\.venv\Scripts\python.exe -m src.evaluation.muscima_training_export --limit 5
```

Expected artifacts:

- `outputs/muscima_reference_integration/summary.json`
- `data/processed/training_exports/` (page-level training export JSON files)

## Verified Smoke Run

The following commands were re-run successfully on this machine on 2026-04-27
from the `demo/` package. The local verification reused the parent checkout's
virtual environment (`..\.venv`) instead of creating a second demo-local
environment, but the command sequence and outputs match the grader path.

- Backend tests: `..\.venv\Scripts\python.exe -m unittest discover tests`
  Result: `Ran 36 tests ... OK`
- Frontend verification:
  - `npm install`
  - `npm test`
  - `npm run build`
  Result: 1 frontend test passed and the Vite production build completed.
- API smoke:
  - `..\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000`
  - `GET /health` returned `status: ok`, `available_assembly_modes: ["auto", "heuristic", "gnn"]`
  - `GET /product/config` returned the public sample-first frontend config
  - `POST /product/transcribe` succeeded for `CVC-MUSCIMA_W-01_N-10_D-ideal`
    with `detection_count: 478` and both export downloads marked ready
- Evaluation/export smoke:
  - `..\.venv\Scripts\python.exe -m src.evaluation.muscima_reference_evaluation`
    saved `outputs/muscima_reference_integration/summary.json`
  - `..\.venv\Scripts\python.exe -m src.evaluation.muscima_training_export --limit 5`
    exported 5 page-level training JSON files under
    `data/processed/training_exports/`

Important deployment note: the public sample-first API and export flow are
working end to end. The backend still reports a truthful `checkpoint-scaffold`
status for the future live GNN runtime, so the repo does not pretend that the
API is already serving checkpoint-backed graph inference in production.

## Documentation Source of Truth

- Use `documentation.md` as the canonical experiment/results narrative.
- Use `MODEL_CARD.md` as the canonical Responsible ML and deployment risk narrative.
- Use `readme_correction.md` as the rubric-to-evidence grading map.
- `docs/status/Hasan_Documentation.md` is integration/handoff status evidence for backend and graph pipeline checks.

## Current Consolidation Notes

- `hassan/week-5` is the effective GitHub head for the non-eval line.
- The `feature/eval-improvements` branch family is intentionally excluded from this branch.
- No expensive model training or full dataset regeneration is required for normal smoke checks.
