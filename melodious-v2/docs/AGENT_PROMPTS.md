# Agent Prompts

Use this file when starting a new coding-agent session for Melodious V2. Copy the relevant prompt exactly, then paste it into the agent. The current active milestone is **M6 - AWS Public Demo**.

## Universal Rules For Every Agent Prompt

Every coding agent must obey these project rules:

- Work only in `C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2`.
- Do not edit the legacy parent project except to read source data or historical context.
- Read `AGENTS.md`, `docs/STATUS.md`, `docs/ROADMAP.md`, `docs/METRICS.md`, `docs/DATA_CARD.md`, and `docs/HANDOFF.md` before implementation.
- Keep generated datasets, labels, runs, outputs, checkpoints, logs, AWS state, and debug artifacts out of Git.
- Do not claim model performance without generated `runs/**/metrics.json` provenance.
- Never compare `mAP` to `F1`.
- Do not stop after partial code if the milestone acceptance criteria can still be completed.
- If blocked, write the blocker, exact attempted commands, and next command to `docs/HANDOFF.md` and `docs/STATUS.md`.
- Before ending, run relevant tests and documentation guards, then update `docs/HANDOFF.md`.

## Exact Prompt For Current Milestone: M6 - AWS Public Demo

Copy and paste this whole prompt into the next coding agent:

```text
You are the coding agent for Melodious V2. Work in this exact directory only:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2

The parent legacy workspace is read-only context:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code

Do not edit legacy files outside `melodious-v2`.

Current milestone: M6 - AWS Public Demo.

Before coding, read:

- AGENTS.md
- docs/STATUS.md
- docs/ROADMAP.md
- docs/METRICS.md
- docs/DATA_CARD.md
- docs/HANDOFF.md
- docs/EXPERIMENTS.md
- docs/RUBRIC_MAP.md
- docs/MILESTONE_HISTORY.md
- MODEL_CARD.md
- README.md
- infra/
- frontend/
- src/melodious_v2/api/
- runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json if it exists locally
- runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json if it exists locally
- runs/detection/detection_136class_yolov8m_v1/metrics.json if it exists locally

Goal:

Prepare and document a public demo deployment path for the FastAPI backend and frontend. The target is a low-cost AWS demo with clear smoke-test evidence, not new model training.

Current handoff:

- M3 detector run: `detection_136class_yolov8m_v1`.
- M3 detector metrics: `runs/detection/detection_136class_yolov8m_v1/metrics.json`.
- M4 graph run: `graph_legacy_gnn_muscima_val_v1`.
- M4 graph metrics: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.
- M5 end-to-end run: `e2e_muscima_holdout_xml_fixture_v1`.
- M5 end-to-end metrics: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.
- M5 measured `musicxml_validity_rate = 1.0` on 14 MUSCIMA holdout XML-derived payload fixtures.
- M5 measured `midi_generation_success_rate = 1.0`.
- M5 measured `page_success_rate = 1.0`.
- M5 scope caveat: this is export validity from ground-truth XML-derived payload fixtures, not trained uploaded-image detector quality.
- API uploaded-image detector inference still uses `heuristic_bootstrap` unless a tested ONNX detector adapter is added.
- M6 deployment path work has started.
- M6 local/public smoke tooling exists at `scripts/smoke_public_demo.py` and `src/melodious_v2/deployment/smoke.py`.
- M6 PowerShell smoke tooling exists at `infra/aws/smoke_test.ps1`.
- M6 AWS runbook exists at `infra/aws/README.md`.
- M6 local smoke evidence can be regenerated with `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --local-testclient --output runs\deploy\m6_local_smoke\smoke.json`.
- M6 public deployment is currently blocked in this workspace because AWS CLI was not found and account-local ECS/ECR/S3/CloudFront values are unavailable.
- Do not move the active prompt to M7 until public smoke evidence exists or the team intentionally accepts the documented AWS blocker as the final fallback.

Do all of the following:

1. Confirm prerequisites.
   - Verify tests pass locally before deployment changes.
   - Verify M3, M4, and M5 metrics exist locally.
   - Verify sample API transcription still works.
   - Verify frontend build works if frontend deployment files are touched.
   - Regenerate M6 local smoke evidence if continuing deployment from a new shell.

2. Inspect deployment scaffolding.
   - Read existing `infra/` files.
   - Do not commit AWS secrets, account IDs, presigned URLs, private bucket names, or `.env` files.
   - Keep generated deployment state outside Git.

3. Prepare a low-cost public demo path.
   - Prefer Dockerized FastAPI backend on ECS Express Mode or ECS Fargate with ECR.
   - Prefer frontend static deployment to S3 and CloudFront.
   - Keep model artifacts private and serve generated artifacts through controlled links or local API routes.
   - Document CPU inference and bootstrap detector limitations honestly.

4. Add or update deployment scripts/docs where useful.
   - Add smoke-test commands for `/health`, `/version`, sample transcription, and artifact download.
   - Add environment variable guidance for `MELODIOUS_GNN_CHECKPOINT`.
   - Add shutdown/cost-control steps.
   - If an actual AWS deploy is not run, document exactly what remains to run.
   - Preserve the existing smoke CLI and PowerShell smoke behavior unless replacing them with a tested better path.

5. Optional detector API wiring if time and scope allow.
   - Add a non-bootstrap ONNX detector adapter for `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.
   - Keep `heuristic_bootstrap` as an explicit fallback.
   - Smoke uploaded-image inference if this adapter is wired.
   - If deferred, document the exact reason and next step.

6. Update documentation before ending.
   - Update `docs/STATUS.md`, `docs/ROADMAP.md`, `docs/RUBRIC_MAP.md`, `docs/MILESTONE_HISTORY.md`, `MODEL_CARD.md`, and `docs/HANDOFF.md`.
   - If M6 completes, update `docs/AGENT_PROMPTS.md` so the next active prompt is M7 - Final Grading Package.
   - If M6 is blocked, document the exact blocker and next command/action.

Verification commands before ending:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`
- If frontend changed: `cd frontend; npm run build`
- If deployment changed: run the relevant local Docker/AWS smoke command and document the result.

Milestone acceptance criteria:

- Deployment path is concrete enough for a public demo or clearly blocked with exact next command/action.
- API `/health`, `/version`, and sample transcription smoke commands are documented.
- Frontend deployment path is documented.
- Cost-control and shutdown steps are documented.
- Tests and metric-claim validation pass.
```

## Archived Prompt: M5 - End-to-End Export Quality

Copy and paste this whole prompt into the next coding agent:

```text
You are the coding agent for Melodious V2. Work in this exact directory only:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2

The parent legacy workspace is read-only context:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code

Do not edit legacy files outside `melodious-v2`.

Current milestone: M5 - End-to-End Export Quality.

Before coding, read:

- AGENTS.md
- docs/STATUS.md
- docs/ROADMAP.md
- docs/METRICS.md
- docs/DATA_CARD.md
- docs/HANDOFF.md
- docs/EXPERIMENTS.md
- docs/RUBRIC_MAP.md
- docs/MILESTONE_HISTORY.md
- MODEL_CARD.md
- src/melodious_v2/api/service.py
- src/melodious_v2/assembly/
- src/melodious_v2/export/
- runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json if it exists locally
- runs/detection/detection_136class_yolov8m_v1/metrics.json if it exists locally
- artifacts/models/detection_136class_yolov8m_v1/metadata.json if it exists locally

Goal:

Measure and improve the real upload-to-export product path. M5 should produce a fixed end-to-end evaluation run that exercises detector payloads, assembly relationships, MusicXML export, and MIDI export with honest provenance and failure notes.

Current detector handoff:

- Full detector run id: `detection_136class_yolov8m_v1`.
- Detector metrics: `runs/detection/detection_136class_yolov8m_v1/metrics.json`.
- Detector model metadata: `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.
- Selected detector checkpoint: `artifacts/models/detection_136class_yolov8m_v1/best.pt`.
- Selected detector ONNX: `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.
- Detector validation `mAP@0.5:0.95 = 0.4747370751116288`.
- Detector validation `mAP@0.5 = 0.5853211368313491`.
- Detector validation `precision@0.5 = 0.8274236461250144`.
- Detector validation `recall@0.5 = 0.4909790740632496`.
- Detector validation `F1@0.5 = 0.6162725385980492`.
- API uploaded-image inference still uses `heuristic_bootstrap`; do not claim non-bootstrap uploaded-image detector inference unless a tested ONNX adapter is added.

Current assembly handoff:

- Real legacy GNN checkpoint source: `..\outputs\gnn_checkpoint.pt`.
- Checkpoint SHA256: `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`.
- Runtime adapter: `src/melodious_v2/assembly/legacy_gnn.py`.
- API mode gating: `src/melodious_v2/assembly/service.py`.
- Graph run id: `graph_legacy_gnn_muscima_val_v1`.
- Graph metrics: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.
- Graph primary validation metric: positive-class macro F1 `0.7590456327823909`.
- Graph no-relation F1: `0.9425171440096813`, reported separately.
- Stem-notehead F1: `0.6960721184803607`.
- Beam-notegroup F1: `0.8220191470844213`.
- The legacy GNN supports a 15-class graph contract and reconstructs the legacy training node encoder from seed `42` because that encoder was not saved as a separate artifact.

Do all of the following:

1. Confirm prerequisites.
   - Verify M3 detector artifacts exist locally.
   - Verify M4 graph metrics exist locally.
   - Verify `docs/EXPERIMENTS.md` includes `graph_legacy_gnn_muscima_val_v1`.
   - Verify API sample transcription still works.

2. Define a fixed end-to-end evaluation set.
   - Prefer the M1 MUSCIMA holdout split when using ground-truth XML-derived payloads.
   - If real uploaded-image detector inference is still bootstrap-only, keep the detector path labeled `heuristic_bootstrap` or use ground-truth-derived detector payload fixtures and label them as such.
   - Do not claim trained uploaded-image detector performance until a non-bootstrap ONNX detector adapter is wired and tested.

3. Implement an end-to-end evaluator under `scripts/` and reusable code under `src/melodious_v2/` as needed.
   - It should create detector-like payloads or use tested detector outputs.
   - It should run assembly through the V2 assembly service.
   - It should write MusicXML and MIDI artifacts.
   - It should validate MusicXML parseability.
   - It should record relationship counts, export success, failure reasons, and artifact hashes.

4. Write an end-to-end run under `runs/e2e/{run_id}/`.
   - Required files: `metrics.json`, `report.md`, `manifest.json`, `artifacts.json`, copied config, and representative exported artifacts.
   - Required provenance: run id, commit, config path, dataset id, split, taxonomy id, metric version, created-at timestamp, and upstream detector/GNN artifact hashes when used.
   - Primary metric should be a measured end-to-end quality/export metric, not an estimate. If only export validity is measured, label it honestly.

5. Add tests.
   - Test MusicXML validation failure/success handling.
   - Test end-to-end artifact manifest writing on a tiny fixture.
   - Preserve API, graph, detector metric, and contract tests.

6. Optional detector API wiring if time and scope allow.
   - Add a non-bootstrap ONNX detector adapter for `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.
   - Keep `heuristic_bootstrap` as an explicit fallback.
   - Smoke `GET /health`, `GET /version`, sample transcription, and uploaded-image inference if this is wired.
   - If deferred, document the exact reason and next step.

7. Update documentation before ending.
   - Regenerate `docs/EXPERIMENTS.md` from `runs/**/metrics.json`.
   - Update `docs/STATUS.md`, `docs/ROADMAP.md`, `docs/RUBRIC_MAP.md`, `docs/MILESTONE_HISTORY.md`, `MODEL_CARD.md`, and `docs/HANDOFF.md`.
   - If M5 completes, update `docs/AGENT_PROMPTS.md` so the next active prompt is M6 - AWS Public Demo.
   - If M5 is blocked, document the exact blocker and next command/action.

Verification commands before ending:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`
- If API changed, smoke `GET /health`, `GET /version`, sample transcription, and the relevant inference route.

Milestone acceptance criteria:

- A fixed end-to-end run emits `runs/e2e/{run_id}/metrics.json`.
- MusicXML and MIDI generation success are measured and backed by artifacts.
- Failure cases include root-cause notes.
- The frontend/API story can show at least one real sample-to-artifact path.
- Tests and metric-claim validation pass.
```

## Archived Prompt: M4 - Real Assembly Runtime

Copy and paste this whole prompt into the next coding agent:

```text
You are the coding agent for Melodious V2. Work in this exact directory only:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2

The parent legacy workspace is read-only context:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code

Do not edit legacy files outside `melodious-v2`.

Current milestone: M4 - Real Assembly Runtime.

Before coding, read:

- AGENTS.md
- docs/STATUS.md
- docs/ROADMAP.md
- docs/METRICS.md
- docs/DATA_CARD.md
- docs/HANDOFF.md
- docs/EXPERIMENTS.md
- docs/RUBRIC_MAP.md
- docs/MILESTONE_HISTORY.md
- MODEL_CARD.md
- src/melodious_v2/assembly/ if it exists
- src/melodious_v2/api/service.py
- src/melodious_v2/contracts.py
- runs/data/muscima_graph_manifest/manifest.json if it exists locally
- runs/detection/detection_136class_yolov8m_v1/metrics.json if it exists locally
- artifacts/models/detection_136class_yolov8m_v1/metadata.json if it exists locally

Goal:

Replace the current graph/assembly scaffold risk with a real assembly runtime path. The system must either load a real GNN/relationship checkpoint and evaluate it on the fixed MUSCIMA graph manifest, or document the exact checkpoint/data blocker and keep fallback behavior explicit.

Current detector handoff:

- M3 is complete enough for detector handoff.
- Full detector run id: `detection_136class_yolov8m_v1`.
- Full detector metrics: `runs/detection/detection_136class_yolov8m_v1/metrics.json`.
- Full detector analysis: `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- Full detector ONNX parity: `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`.
- Full detector model metadata: `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.
- Selected detector checkpoint: `artifacts/models/detection_136class_yolov8m_v1/best.pt`.
- Selected detector ONNX: `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.
- Detector primary validation metric: `mAP@0.5:0.95 = 0.4747370751116288`.
- Detector secondary validation metrics: `mAP@0.5 = 0.5853211368313491`, `precision@0.5 = 0.8274236461250144`, and `recall@0.5 = 0.4909790740632496`.
- Detector secondary F1: `F1@0.5 = 0.6162725385980492`.
- Detector limitations: validation recall is weaker than precision; 16 supported validation classes have zero mAP, including `ledgerLine`, `stem`, and `ottavaBracket`.
- API upload inference still uses `heuristic_bootstrap`; do not claim non-bootstrap uploaded-image inference until a tested ONNX detector adapter exists.

Do all of the following:

1. Confirm prerequisites.
   - Verify M1 MUSCIMA graph manifest exists under `runs/data/muscima_graph_manifest/`.
   - Verify M3 detector artifacts exist under `runs/detection/detection_136class_yolov8m_v1/` and `artifacts/models/detection_136class_yolov8m_v1/`.
   - Verify `docs/EXPERIMENTS.md` includes `detection_136class_yolov8m_v1`.

2. Locate or define the real assembly model source.
   - Search the V2 repo and read-only parent workspace for existing GNN/relationship checkpoint, graph model code, feature extraction code, or training outputs.
   - Do not edit legacy files.
   - If a usable checkpoint exists, document its source path, expected input features, class labels, and hash.
   - If no usable checkpoint exists, document that blocker precisely and implement only the safest reproducible evaluation scaffold needed for the next agent.

3. Implement the V2 assembly runtime boundary.
   - Keep detector payload contracts stable.
   - Add or update code under `src/melodious_v2/assembly/`.
   - Use explicit runtime modes such as `gnn`, `heuristic_fallback`, or `checkpoint_missing`.
   - Never allow the API to report `applied_mode = "gnn"` unless a real checkpoint was loaded and inference ran.
   - Preserve explicit warnings and fallback metadata when checkpoint loading or inference fails.

4. Evaluate graph assembly through V2 metric code.
   - Use the fixed MUSCIMA graph manifest.
   - Report graph primary metric as positive-class macro F1 on the natural edge distribution.
   - Report `no_relation` precision, recall, F1, and support separately.
   - Write `runs/graph/{run_id}/metrics.json` with required provenance: run id, commit, config path, dataset id, split, taxonomy id, metric version, created-at timestamp, and checkpoint hash when applicable.
   - Write `report.md`, `manifest.json`, `artifacts.json`, and copied config for the graph run.
   - Regenerate `docs/EXPERIMENTS.md` from `runs/**/metrics.json`.

5. Add tests.
   - Test graph metric math, especially positive-class macro F1 and separate `no_relation` reporting.
   - Test checkpoint loading/fallback behavior.
   - Test API mode metadata if the API route is wired.
   - Preserve existing detector and API tests.

6. Optional detector API wiring if time and scope allow.
   - Add a non-bootstrap ONNX detector adapter for `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.
   - Keep `heuristic_bootstrap` as an explicit fallback.
   - Smoke `GET /health`, `GET /version`, and uploaded-image inference only if this adapter is wired.
   - If this is deferred, document the exact reason and next step.

7. Update documentation before ending.
   - Update `docs/STATUS.md`, `docs/ROADMAP.md`, `docs/RUBRIC_MAP.md`, `docs/MILESTONE_HISTORY.md`, `MODEL_CARD.md`, and `docs/HANDOFF.md`.
   - If M4 completes, update `docs/AGENT_PROMPTS.md` so the next active prompt is M5 - End-to-End Export Quality.
   - If M4 is blocked, document the exact blocker and next command/action.

Verification commands before ending:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`
- If API changed, smoke `GET /health`, `GET /version`, and the relevant inference route.

Milestone acceptance criteria:

- Real GNN/relationship mode either runs from a verified checkpoint, or the exact missing-checkpoint/data blocker is documented.
- Graph evaluation emits `runs/graph/{run_id}/metrics.json` when model/evaluation inputs are available.
- API response includes relationship outputs and truthful runtime mode metadata.
- Positive-class macro F1 is the graph headline metric; `no_relation` is reported separately.
- Tests and metric-claim validation pass.
```

## Archived Prompt: M3 - Full 136-Class Detector

Copy and paste this whole prompt into the next coding agent:

```text
You are the coding agent for Melodious V2. Work in this exact directory only:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2

The parent legacy workspace is read-only context:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code

Do not edit legacy files outside `melodious-v2`.

Current milestone: M3 - Full 136-Class Detector.

Before coding, read:

- AGENTS.md
- docs/STATUS.md
- docs/ROADMAP.md
- docs/METRICS.md
- docs/DATA_CARD.md
- docs/HANDOFF.md
- docs/EXPERIMENTS.md
- docs/RUBRIC_MAP.md
- docs/MILESTONE_HISTORY.md
- MODEL_CARD.md
- configs/detection_136class_yolov8m.yaml
- configs/detection_15class_repro.yaml
- runs/data/deepscores_136_manifest/manifest.json if it exists locally
- runs/detection/detection_15class_repro_sample_v1/metrics.json if it exists locally
- runs/detection/detection_136class_yolov8s_smoke_v1/metrics.json if it exists locally
- artifacts/models/detection_136class_yolov8s_smoke_v1/metadata.json if it exists locally
- artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json if it exists locally

Goal:

Continue the main 136-class detector milestone. A constrained YOLOv8s smoke run exists; the remaining M3 target is to resume or finalize the full configured YOLOv8m run, or make a clearly documented decision that another artifact is accepted for integration.

Current resumed-run note:

- As of 2026-05-26, the full configured run `detection_136class_yolov8m_v1` was resumed again from the clean epoch-95 recovery point.
- The load-verified recovery checkpoint is `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/last.pt`.
- The recovery metadata is `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json`.
- Load verification confirmed `task=detect`, `class_count=136`, first class `brace`, and last class `ottavaBracket`.
- The current resume PID file is `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train.pid`; launch PID was `30436`.
- The current resume logs are `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stdout.log` and `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stderr.log`.
- Resume stdout confirmed `model=...epoch95_stop_2026-05-22\last.pt`, `nc=136`, `epochs=150`, `imgsz=1024`, `batch=4`, and `data=...deepscores_136_yolo_materialized\dataset.yaml`.
- Resume stdout says `Resuming training ... from epoch 96 to 150 total epochs` and shows active epoch `96/150`.
- The latest clean completed Ultralytics row is epoch 95 with precision 0.81908, recall 0.47262, `mAP@0.5` 0.56329, and `mAP@0.5:0.95` 0.43327. This is interim `results.csv` evidence, not final project `metrics.json`.
- The best completed interim `mAP@0.5:0.95` so far is epoch 90 at 0.44043, with precision 0.79210, recall 0.48034, and `mAP@0.5` 0.57137. This is still interim checkpoint evidence, not final V2 metric provenance.
- Before starting any new training, check whether the resumed process is still live and whether `runs/detection/detection_136class_yolov8m_v1/metrics.json` now exists.
- If the resumed process is live, monitor it instead of launching another process:
  `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train.pid)`
- If no final `metrics.json` exists and the resumed process is dead, inspect `resume_epoch95_train_stderr.log`, `resume_epoch95_train_stdout.log`, `ultralytics/train/results.csv`, and `ultralytics/train/weights/last.pt` before resuming again.

Do all of the following:

1. Confirm M1 and M2 prerequisites.
   - Verify the DeepScores 136-class manifest exists under `runs/data/deepscores_136_manifest/`.
   - Verify the M2 reduced-class metric reproduction run exists under `runs/detection/detection_15class_repro_sample_v1/`.
   - Verify whether the M3 smoke run exists under `runs/detection/detection_136class_yolov8s_smoke_v1/`.
   - If either is missing, regenerate it with the existing scripts before starting M3.

2. Train or evaluate the full 136-class detector only if the local environment has the required training dependencies and data.
   - Use `configs/detection_136class_yolov8m.yaml` as the governing config unless a documented local constraint requires a smaller smoke run.
   - Use validation-only threshold selection.
   - Do not claim test performance until a final configured run writes `runs/detection/{run_id}/metrics.json`.
   - If the resumed process is live, monitor it instead of launching another process:
     `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train_stdout.log`
   - If the epoch-95 checkpoint exists, the resumed process is dead, and no completed full run exists, resume from it rather than restarting:
     `$env:PYTHONPATH='src'; ..\.venv\Scripts\yolo.exe detect train resume=True model=.\artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22\last.pt`
   - If the checkpoint is missing or corrupt, document that blocker before considering a full restart with:
     `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --model yolov8m.pt --epochs 150 --imgsz 1024 --batch 4 --workers 0 --device 0`

3. Produce required detector artifacts.
   - Save metrics under `runs/detection/{run_id}/metrics.json` with required provenance.
   - Save `report.md`, `manifest.json`, `artifacts.json`, and copied `config.yaml`.
   - Export the selected model to ONNX when a trained checkpoint is available.
   - Record SHA256 hashes for evaluated checkpoints and exported artifacts.
   - If training was resumed through the Ultralytics CLI, add or run a V2 finalize/evaluate/export step afterward; the CLI alone will not create the project-standard `metrics.json`, `analysis.json`, or artifact metadata.

4. Analyze model behavior.
   - Include primary `mAP@0.5:0.95`.
   - Include secondary `mAP@0.5`, `precision@0.5`, `recall@0.5`, and `F1@0.5`.
   - Produce per-class AP/F1 evidence, confusion or error summary, rare-class notes, and small-symbol notes where practical.
   - Never compare `mAP` to `F1`.

5. Wire artifacts forward where safe.
   - Add or update detector artifact metadata used by the API only after the artifact exists.
   - Keep bootstrap detector fallback explicit until a real ONNX/checkpoint path is configured.

6. Update documentation before ending.
   - Regenerate `docs/EXPERIMENTS.md` from `runs/**/metrics.json`.
   - Update `docs/STATUS.md`, `docs/ROADMAP.md`, `docs/RUBRIC_MAP.md`, `docs/MILESTONE_HISTORY.md`, `MODEL_CARD.md`, and `docs/HANDOFF.md`.
   - If M3 completes, update `docs/AGENT_PROMPTS.md` so the next active prompt is M4 - Real Assembly Runtime.
   - If M3 is blocked, document the exact blocker and next command.

Verification commands before ending:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`
- If the detector artifact is wired into the API, smoke `GET /health`, `GET /version`, and the relevant inference route.

Milestone acceptance criteria:

- `runs/detection/{run_id}/metrics.json` exists with required provenance for the full 136-class detector.
- `artifacts/models/{run_id}/` contains model artifact metadata and SHA256 hashes.
- API can load the selected detector artifact behind a non-bootstrap detector mode, or the blocker is documented precisely.
- Model card documents remaining class gaps and failure modes.
- Tests and metric-claim validation pass.
```

## Archived Prompt: M2 - Metric Reproduction

Copy and paste this whole prompt into the next coding agent:

```text
You are the coding agent for Melodious V2. Work in this exact directory only:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2

The parent legacy workspace is read-only context:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code

Do not edit legacy files outside `melodious-v2`.

Current milestone: M2 - Metric Reproduction.

Before coding, read:

- AGENTS.md
- docs/STATUS.md
- docs/ROADMAP.md
- docs/METRICS.md
- docs/DATA_CARD.md
- docs/HANDOFF.md
- docs/EXPERIMENTS.md
- docs/RUBRIC_MAP.md
- src/melodious_v2/metrics/detection.py
- src/melodious_v2/reports.py
- configs/detection_15class_repro.yaml

Goal:

Prove the V2 detector metric pipeline before any new detector training result is claimed.

Do all of the following:

1. Reproduce a reduced-class detector evaluation through V2 metric code.
   - Prefer legacy sample predictions or reduced-class outputs from the parent workspace if available.
   - Do not train a new model.
   - If no usable predictions exist, create a clearly labeled deterministic metric fixture and document that it is a pipeline sanity run, not model performance.

2. Save the run under `runs/detection/`.
   - The run folder must include `metrics.json`, `report.md`, `manifest.json`, `artifacts.json`, and `config.yaml`.
   - Write metrics through `melodious_v2.reports.write_run_report`.
   - Include required provenance: run id, commit, config path, dataset id, split, taxonomy id, metric version, created-at timestamp, and model artifact hash when evaluating a checkpoint.

3. Use the metric definitions in `docs/METRICS.md`.
   - Detector primary metric is `mAP@0.5:0.95`.
   - Secondary metrics are `mAP@0.5`, `precision@0.5`, `recall@0.5`, and `F1@0.5`.
   - Never compare `mAP` to `F1`.

4. Add or update tests.
   - Golden detection metric tests must pass.
   - Add tests for any new reduced-class conversion, run manifest, or report behavior.

5. Regenerate documentation from artifacts.
   - Regenerate `docs/EXPERIMENTS.md` from `runs/**/metrics.json`.
   - Update `docs/STATUS.md`, `docs/ROADMAP.md`, `docs/RUBRIC_MAP.md`, and `docs/HANDOFF.md`.
   - Do not hand-write metric values into docs unless they are generated from `metrics.json`.

6. Before ending, update `docs/AGENT_PROMPTS.md` so the next active prompt is M3 - Full 136-Class Detector.

Verification commands before ending:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`

Milestone acceptance criteria:

- Golden metric tests pass.
- A reduced-class reproduction run has a complete `metrics.json`.
- `docs/EXPERIMENTS.md` is generated from the run artifact.
- `scripts/validate_metric_claims.py` passes.
- `docs/STATUS.md`, `docs/HANDOFF.md`, and `docs/AGENT_PROMPTS.md` point the next agent to M3.
```

## Archived Prompt: M1 - Dataset Manifests

Copy and paste this whole prompt into the next coding agent:

```text
You are the coding agent for Melodious V2. Work in this exact directory only:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2

The parent legacy workspace is:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code

You may read source datasets from the parent workspace, especially:

- C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\dataset_ds2_dense
- C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\data\muscima-pp\v2.0\data\annotations
- C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\data\cvc-muscima

Do not edit legacy files outside `melodious-v2`.

Current milestone: M1 - Dataset Manifests.

Before coding, read these files:

- AGENTS.md
- docs/STATUS.md
- docs/ROADMAP.md
- docs/METRICS.md
- docs/DATA_CARD.md
- docs/HANDOFF.md
- src/melodious_v2/datasets/deepscores.py
- src/melodious_v2/taxonomies.py
- configs/detection_136class_yolov8m.yaml

Goal:

Complete M1 so the project has reproducible DeepScores 136-class and MUSCIMA graph split manifests before any training starts.

Do all of the following:

1. Implement a robust dataset-manifest builder.
   - Add or extend code under `src/melodious_v2/datasets/`.
   - Add a CLI script, preferably `scripts/build_dataset_manifests.py`.
   - The script must read the parent DeepScores files:
     - `..\dataset_ds2_dense\deepscores_train.json`
     - `..\dataset_ds2_dense\deepscores_test.json`
   - It must read MUSCIMA XML pages from:
     - `..\data\muscima-pp\v2.0\data\annotations`

2. Generate DeepScores outputs under:
   - `runs/data/deepscores_136_manifest/`
   The run folder must include:
   - `manifest.json`
   - `train.json`
   - `val.json`
   - `test.json`
   - `class_counts.json`
   - `leakage_report.json`
   - `yolo_dataset.yaml`
   - generated YOLO labels under a generated/ignored directory, not committed

3. DeepScores split policy:
   - Preserve the existing DeepScores train/test separation.
   - Split the existing train set deterministically into train/val with seed `42`.
   - Default split ratio: 90% train, 10% val from the existing train JSON.
   - Keep the existing test JSON as test.
   - Each split manifest must include image id, filename, width, height, source JSON, annotation count, and class counts.
   - `manifest.json` must summarize all splits and include `taxonomy_id = "deepscores_136"`, `class_count = 136`, seed, split policy, source paths, and generated-at timestamp.

4. DeepScores leakage checks:
   - Check duplicate image ids across splits.
   - Check duplicate filenames across splits.
   - Check repeated score/work groups across splits when inferable from filename prefixes.
   - Do not hide ambiguity. If filename grouping is heuristic, say so in the leakage report.
   - Fail or mark `status = "failed"` for true duplicate image ids or duplicate filenames across splits.
   - Mark repeated inferred work groups as `warning`, not automatic failure unless clearly identical files.

5. YOLO labels:
   - Use all 136 DeepScores classes from `src/melodious_v2/taxonomies.py`.
   - Write YOLO label txt files for every split.
   - Create a `yolo_dataset.yaml` with `path`, `train`, `val`, `test`, `nc: 136`, and all class names.
   - Do not copy images into Git. If image paths are needed, write manifests or instructions only.

6. Generate MUSCIMA outputs under:
   - `runs/data/muscima_graph_manifest/`
   The run folder must include:
   - `manifest.json`
   - `train.json`
   - `val.json`
   - `holdout.json`
   - `leakage_report.json`
   - `class_summary.json` if class parsing is practical within this milestone

7. MUSCIMA split policy:
   - Deterministic seed `42`.
   - Use all XML page filenames found in `..\data\muscima-pp\v2.0\data\annotations`.
   - Split into 80% train, 10% val, 10% holdout.
   - Include page id, filename, inferred writer id if available from filename, source path, and node count if parsing is practical.
   - Check duplicate page ids across splits.

8. Tests:
   - Add unit tests for deterministic splitting.
   - Add tests that DeepScores manifest summaries report `class_count = 136`.
   - Add tests that duplicate ids across splits are caught by leakage checks.
   - Add tests that MUSCIMA split manifests have no duplicate page ids across train/val/holdout.

9. Documentation:
   - Update `docs/DATA_CARD.md` with the exact manifest outputs and split policy.
   - Update `docs/STATUS.md`:
     - If M1 is complete, mark M1 done and M2 next.
     - If blocked, keep M1 active and write the exact blocker.
   - Update `docs/HANDOFF.md` with:
     - what you changed,
     - files changed,
     - commands run,
     - generated artifacts,
     - tests passed/failed,
     - exact next step for the next agent.
   - Do not manually add model metric claims.

10. Verification commands to run before ending:
    - `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests`
    - `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`
    - Run your new manifest CLI once against the local parent datasets if the datasets exist.

Milestone acceptance criteria:

- `runs/data/deepscores_136_manifest/manifest.json` exists.
- `runs/data/deepscores_136_manifest/leakage_report.json` exists.
- Every DeepScores split summary reports `class_count = 136`.
- `runs/data/muscima_graph_manifest/manifest.json` exists.
- MUSCIMA train/val/holdout splits have no duplicate page ids.
- Tests pass.
- `docs/STATUS.md` and `docs/HANDOFF.md` tell the next agent exactly where to pick up.

Important:

- Do not train any model in M1.
- Do not claim detector performance in M1.
- Do not edit legacy files.
- Do not commit generated `runs/` artifacts unless the user explicitly asks. They are ignored outputs, but the script must generate them locally.
- If anything blocks completion, keep working around it if reasonable. Only stop after documenting the blocker and the next exact command in `docs/HANDOFF.md`.
```

## Reusable Prompt Template For Future Milestones

When M1 is done, replace the milestone-specific parts and paste this:

```text
You are the coding agent for Melodious V2. Work in this exact directory only:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2

The parent legacy workspace is read-only context:

C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code

Do not edit legacy files outside `melodious-v2`.

Before coding, read:

- AGENTS.md
- docs/STATUS.md
- docs/ROADMAP.md
- docs/METRICS.md
- docs/DATA_CARD.md
- docs/HANDOFF.md
- docs/EXPERIMENTS.md
- docs/RUBRIC_MAP.md

Current milestone:

[PASTE THE ACTIVE MILESTONE FROM docs/STATUS.md]

Goal:

[PASTE THE MILESTONE GOAL FROM docs/ROADMAP.md]

Acceptance criteria:

[PASTE THE ACCEPTANCE CRITERIA FROM docs/ROADMAP.md]

Implementation requirements:

- Stay inside `melodious-v2`.
- Prefer existing package patterns under `src/melodious_v2/`.
- Add or update tests for every new contract, metric, CLI, API, or artifact behavior.
- Generate run artifacts only under ignored folders such as `runs/`, `artifacts/`, or `outputs/`.
- Update `docs/STATUS.md` and `docs/HANDOFF.md` before ending.
- If this milestone creates metrics, write them through `runs/**/metrics.json` and regenerate `docs/EXPERIMENTS.md`; do not hand-write metric values into docs.
- Run `scripts/validate_metric_claims.py` before ending.

Verification commands before ending:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests`
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`
- If frontend changed: `cd frontend; npm run build`
- If API changed: smoke `GET /health`, `GET /version`, and the relevant route.
- If deployment changed: run the relevant local Docker/AWS smoke command and document the result.

Do not stop until:

- the active milestone is complete, OR
- a real blocker prevents completion and `docs/HANDOFF.md` explains exactly what failed, what was attempted, and the next command/action.
```
