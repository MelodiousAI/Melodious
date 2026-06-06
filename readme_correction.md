# Melodious Grading Map (`readme_correction.md`)

This file maps the rubric criteria to exact repository evidence so grading can be done quickly and consistently.

## Project Metadata

- **Project type:** Option A (applied/deployable ML system)
- **Graph project:** Yes (graph is a core modeling component, not only visualization)
- **Canonical technical report:** `documentation.md`
- **Canonical responsible ML report:** `MODEL_CARD.md`

## Rubric Evidence Map

### Problem & Fit

- **PF1 (specific problem):** `README.md`, `documentation.md` (Project Overview, Step 12 objective and end-to-end framing).
- **PF2A (user/decision/deployer):** `MODEL_CARD.md` (Intended Use, target users, deployment mode), `README.md` (`src/api/`, `frontend/`).
- **PF3A (why ML vs non-AI):** `documentation.md` (Baselines + architecture comparison; YOLO/GNN rationale and baseline underperformance).
- **PF4 (impact/significance):** `MODEL_CARD.md` (Intended Use + limitations/ethics), `documentation.md` (project goal and motivation).
- **PF5 (track fit/success criteria):** `documentation.md` (Results Summary, deployment metrics, end-to-end pipeline evaluation).

### Technical Rigor & Responsible ML

- **TM1 (task/data visibility):** `documentation.md` (dataset, split, metrics, training/evaluation steps), `README.md` (data layout).
- **TM2A (non-AI baseline):** `documentation.md` (Baseline Comparison table: template matching, HOG+SVM).
- **TM3 (method choice/substantive contribution):** `documentation.md` (YOLOv8 transfer learning, GNN training, combined pipeline).
- **TM4 (preprocessing/leakage control):** `documentation.md` (dataset conversion, split usage, augmentation pipeline, evaluation setup).
- **TM5 (protocol/splits/metrics):** `documentation.md` (112/28 MUSCIMA split, 1362/352 DeepScores split, mAP/F1/P/R reporting).
- **TM6 (error analysis/failure modes):** `documentation.md` (Challenges & Solutions, gap analysis in Step 12, robustness findings).
- **TM7 (limitations/trade-offs):** `MODEL_CARD.md` (Bias and Limitations), `documentation.md` (trade-offs and ceilings).
- **TM9G (graph as core model):** `src/graph/pyg_graph_builder.py`, `src/evaluation/muscima_training_export.py`, `documentation.md` (Step 9/12).
- **TM10G (graph justification + non-graph baseline):** `documentation.md` baseline and architecture sections, and graph-baseline section added for rubric traceability.
- **RM1 (explainability):** `MODEL_CARD.md` (confidence/uncertainty policy), `documentation.md` (attention visualization mention), `src/ui/streamlit_app.py`.
- **RM2 (bias/fairness):** `MODEL_CARD.md` (Western-notation bias, excluded notation systems, OOD warning).
- **RM3 (privacy/leakage risks):** `MODEL_CARD.md` (on-device detection, minimal transmission, no image storage).
- **RM4 (robustness/distribution shift):** `documentation.md` (Step 11 degradation analysis), robustness artifacts in `outputs/robustness/`.

### Deployment & Engineering

- **EN1 (Dockerized API):** `docker/Dockerfile.api`, `docker-compose.yml`, `src/api/app.py`, `docs/status/Hasan_Documentation.md` (build/run checks).
- **EN2 (separation of concerns):** `src/data_prep/`, `src/graph/`, `src/inference/`, `src/export/`, `src/api/`.
- **EN3 (reproducible run path):** `README.md` (main commands/tests + deterministic runbook section).
- **EN4 (functional demo/UI):** `frontend/` app and `src/ui/streamlit_app.py`; product routes in `src/api/product_routes.py`.
- **EN5 (stable service setup):** `README.md` run commands, `docker-compose.yml`, API health/assemble/midi endpoints.

### GitHub & Documentation

- **GD1 (repo structure):** `README.md` (Repo Structure), top-level directory layout.
- **GD2 (README setup/run):** `README.md` commands for backend/frontend/tests and reproducibility runbook.
- **GD3 (method/architecture docs):** `documentation.md`, `MODEL_CARD.md`, `sample_detections/GNN_HANDOFF.md`.
- **GD4 (results/logs/experiments):** `documentation.md` tables + `outputs/` artifacts.
- **GD5 (data/limitations/ethics/deployment notes):** `MODEL_CARD.md`, `README.md`, `documentation.md`.

### Presentation & Creativity (repo-supporting evidence)

- **PR1/PR2/PR3 support:** `documentation.md` summary tables and pipeline narrative; `frontend/` and API for demo.
- **PR4 preparation:** `presentation_script.md` (5-minute script + Q&A ownership checklist).
- **CI1–CI4 support:** `documentation.md` (YOLO + GNN integration, extended experiments, robustness, export benchmarks).

## Quick Verification Commands (for grader)

```powershell
# 1) Backend tests
.\.venv\Scripts\python.exe -m unittest discover tests

# 2) Frontend checks
cd frontend
npm test
npm run build

# 3) API smoke run
cd ..
.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

## Notes for Grading

- If a criterion depends on live presentation quality (PR1–PR4), use this file as supporting technical evidence and confirm verbally during demo/Q&A.
- If graph-specific criteria are considered not applicable by instructor policy, skip TM9G/TM10G rather than assigning 0.
