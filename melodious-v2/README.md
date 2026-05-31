# Melodious V2

Melodious V2 is a clean rebuild of the original OMR project. It targets a full-grade applied/deployment project: full-taxonomy detection, measured graph assembly, real upload-to-export service behavior, and cloud-ready deployment.

## What Is New

- Full DeepScores 136-class taxonomy support instead of a fixed 15-class-only detector.
- Strict metric registry so `mAP`, `F1`, precision, and recall are never mixed.
- Versioned detector payload contract with taxonomy, run id, model id, and artifact hash provenance.
- FastAPI product service with sample and upload transcription routes.
- Checkpoint-gated legacy GNN assembly runtime with explicit fallback metadata.
- AWS ECS/Fargate deployment templates instead of local-only demo claims.
- Governance docs from day one: metrics, data card, experiments, rubric map, status, model card, and agent rules.

## Layout

- `src/melodious_v2/`: Python package.
- `configs/`: detector, graph, and deployment configs.
- `scripts/`: CLI helpers for data conversion, reports, and API startup.
- `tests/`: contract, metric, dataset, API, and export tests.
- `frontend/`: React/Vite upload and results UI.
- `infra/`: Docker and AWS deployment scaffolding.
- `docs/`: canonical documentation.
- `runs/`, `artifacts/`, `outputs/`, `data/`, `checkpoints/`: generated and ignored.

## Project Plan

- `docs/ROADMAP.md`: milestone plan, acceptance criteria, tracking rules, and weekly operating rhythm.
- `docs/STATUS.md`: current active milestone, blockers, and immediate next actions.
- `docs/AGENT_PROMPTS.md`: copy-paste prompts for coding agents.
- `docs/HANDOFF.md`: where each agent records progress and the next exact step.
- `docs/MILESTONE_HISTORY.md`: detailed milestone evidence ledger from M1 onward, including future milestone checklists.
- `docs/EXPERIMENTS.md`: generated index of run artifacts.
- `docs/RUBRIC_MAP.md`: rubric evidence map for grading.

## Local Setup

```powershell
cd melodious-v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run Tests

```powershell
python -m pytest
```

Without `pytest`:

```powershell
$env:PYTHONPATH="src"
python -m unittest discover tests
```

## Run API

```powershell
$env:PYTHONPATH="src"
python scripts/run_api.py
```

Open `http://127.0.0.1:8000/health`.

## Run Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects `VITE_API_BASE_URL=http://127.0.0.1:8000` by default.

## Detection Training Path

1. Reproduce the legacy 15-class baseline. Done for the M2 sample run under `runs/detection/detection_15class_repro_sample_v1/`.
2. Convert DeepScores to a 136-class YOLO dataset with fixed manifests.
3. Materialize the M1 manifest into a YOLO-standard ignored dataset under `runs/data/deepscores_136_yolo_materialized/`.
4. Train the full-class detector with validation-only threshold selection. Done for the full configured YOLOv8m run under `runs/detection/detection_136class_yolov8m_v1/`; it completed 150 epochs, selected `best.pt`, wrote V2 `metrics.json`, exported `best.onnx`, and copied artifact metadata to `artifacts/models/detection_136class_yolov8m_v1/`.
5. Evaluate with `mAP@0.5:0.95` as the primary detector metric.
6. Store every run under `runs/detection/{run_id}/` with config, metrics JSON, plots, and artifact hashes.

## Graph Assembly Path

1. Load the legacy MUSCIMA GNN checkpoint from `..\outputs\gnn_checkpoint.pt` through `MELODIOUS_GNN_CHECKPOINT`.
2. Convert detector payloads into the legacy 15-class graph feature contract.
3. Return `applied_mode = "gnn"` only when checkpoint inference runs; missing or failed checkpoints return explicit fallback metadata.
4. Evaluate graph relationships with positive-class macro F1 on the natural candidate-edge distribution.
5. Current graph run: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.

## End-to-End Export Evaluation

1. Use the fixed MUSCIMA holdout split from `runs/data/muscima_graph_manifest/holdout.json`.
2. Build detector-like payload fixtures from MUSCIMA XML annotations.
3. Run assembly through the V2 assembly service.
4. Export MusicXML, MIDI, detector payload JSON, and relationship JSON artifacts.
5. Current end-to-end run: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.
6. Scope caveat: this measures export validity from XML-derived payload fixtures, not trained uploaded-image detector quality.

## Deployment Path

Backend deployment targets Dockerized FastAPI + ONNX CPU inference on ECS Express Mode or ECS Fargate with images in ECR. The frontend deploys to S3 + CloudFront. See `infra/aws/README.md`.

## Current Status

This implementation provides the clean project foundation, strict contracts, metric code, M1 data manifests, M2 reduced-class metric reproduction, M3 full-taxonomy detector artifacts, M4 real graph assembly runtime, M5 end-to-end export evaluation, upload/sample API, frontend, tests, and deployment templates. The full configured 136-class YOLOv8m run now has generated metric provenance under `runs/detection/detection_136class_yolov8m_v1/` and model artifacts under `artifacts/models/detection_136class_yolov8m_v1/`. The legacy GNN assembly run has generated metric provenance under `runs/graph/graph_legacy_gnn_muscima_val_v1/`. The end-to-end export run has generated metric provenance under `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/`.

Current active milestone: M6 - AWS Public Demo. See `docs/ROADMAP.md` and `docs/MILESTONE_HISTORY.md` before starting new implementation work.
