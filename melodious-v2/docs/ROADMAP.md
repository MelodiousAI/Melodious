# Roadmap and Milestone Tracker

This document is the project execution plan after the V2 foundation. It turns the rebuild plan into trackable milestones with evidence artifacts, acceptance criteria, and documentation updates.

## Tracking Rules

- Update `docs/STATUS.md` whenever a milestone starts, finishes, or gets blocked.
- Update `docs/HANDOFF.md` before ending every coding-agent session.
- Update `docs/EXPERIMENTS.md` only through generated run records from `runs/**/metrics.json`.
- Update `docs/RUBRIC_MAP.md` when a new milestone creates evidence for a rubric item.
- Update `docs/MILESTONE_HISTORY.md` with detailed milestone evidence, commands, artifacts, limits, and exact next steps.
- Do not claim a model result unless it has a run id, config, split, metric JSON, and artifact hash.
- Keep fallback paths explicit in API responses and docs.
- Keep all datasets, runs, outputs, checkpoints, AWS state, and debug residue out of Git.

## Big Milestones

| Milestone | Status | Purpose | Main Evidence |
|---|---|---|---|
| M0 - V2 Foundation | Done | Clean repo, contracts, docs, tests, API/UI scaffold, AWS templates | tests pass, schema generated, local API/UI smoke |
| M1 - Dataset Manifests | Done | Fixed DeepScores 136-class and MUSCIMA graph splits with leakage checks | manifest JSONs, class counts, leakage report |
| M2 - Metric Reproduction | Done | Reproduce reduced-class baseline with V2 metric code | `runs/detection/detection_15class_repro_sample_v1/metrics.json`, generated report |
| M3 - Full 136-Class Detector | Done | Train and evaluate full-taxonomy detector | `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, `onnx_parity.json`, model metadata |
| M4 - Real Assembly Runtime | Active | Wire trained GNN adapter and natural-distribution graph evaluation | graph metrics, adapter tests, API mode proof |
| M5 - End-to-End Export Quality | Planned | Measure upload-to-MusicXML/MIDI quality on fixed holdout pages | validity rate, structure metrics, artifact samples |
| M6 - AWS Public Demo | Planned | Deploy API and frontend publicly with smoke tests | ECS/ECR/S3/CloudFront evidence, smoke logs |
| M7 - Final Grading Package | Planned | Freeze narrative, evidence map, demo script, and limitations | final docs, rubric map, presentation assets |

## Completed M3 - Full 136-Class Detector

Goal: deliver the main detector-side ML improvement.

Final run:

- Run id: `detection_136class_yolov8m_v1`.
- Dataset: `deepscores_136_yolo_materialized`.
- Split used for reported metrics: validation.
- Taxonomy: `deepscores_136`.
- Model family: YOLOv8m.
- Training shape: 150 epochs, image size 1024, batch size 4, workers 0, device 0.
- Selected checkpoint: `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`.
- Copied checkpoint: `artifacts/models/detection_136class_yolov8m_v1/best.pt`.
- Copied ONNX: `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.
- Artifact metadata: `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

Final M3 evidence:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json`.
- `runs/detection/detection_136class_yolov8m_v1/report.md`.
- `runs/detection/detection_136class_yolov8m_v1/manifest.json`.
- `runs/detection/detection_136class_yolov8m_v1/artifacts.json`.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- `runs/detection/detection_136class_yolov8m_v1/analysis.md`.
- `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

Detector metrics from `metrics.json`:

- Primary `mAP@0.5:0.95`: 0.4747370751116288.
- Secondary `mAP@0.5`: 0.5853211368313491.
- `precision@0.5`: 0.8274236461250144.
- `recall@0.5`: 0.4909790740632496.
- `F1@0.5`: 0.6162725385980492.

Detector analysis:

- Validation-supported classes: 103 of 136.
- Rare supported classes with support <= 10: 14.
- Supported classes with zero mAP: 16.
- Supported small-symbol classes: 35.
- Small-symbol mean `mAP@0.5:0.95`: 0.3194606161321027.
- Important zero-mAP classes include `ledgerLine`, `stem`, and `ottavaBracket`; these should remain explicit limitations.

ONNX parity:

- `onnx_parity.json` passed on one fixed validation image.
- PyTorch and ONNX both returned 300 boxes with identical class-count totals.
- Local ONNX Runtime used CPU fallback because `onnxruntime-gpu` is not installed.

M3 acceptance status:

- Full configured detector `metrics.json` exists with provenance.
- Model artifact metadata and SHA256 hashes exist.
- ONNX export exists.
- Analysis artifacts exist.
- API detector wiring is still bootstrap/heuristic. This is documented as a follow-up because the M3 prompt allowed precise blocker documentation instead of forcing detector adapter work into the training milestone.

## Immediate Next Work

### M4 - Real Assembly Runtime

Goal: remove the current graph/assembly scaffold risk and prove a real relationship model path.

Implementation tasks:

- Read the MUSCIMA graph manifest generated in M1.
- Identify the available trained GNN checkpoint or legacy graph model in the parent workspace, if present.
- Define the V2 graph feature/input contract under `src/melodious_v2/assembly/`.
- Add model loading through a clear configuration path such as `MELODIOUS_GNN_CHECKPOINT`.
- Evaluate on the natural edge distribution.
- Report positive-class macro F1 as the primary graph metric.
- Keep `no_relation` metrics separate.
- Add API tests proving `applied_mode = "gnn"` only when real inference is active.
- Preserve explicit fallback metadata when no checkpoint is configured or loading fails.
- Write graph metrics to `runs/graph/{run_id}/metrics.json`.
- Regenerate `docs/EXPERIMENTS.md` from run artifacts.
- Update `MODEL_CARD.md`, `docs/RUBRIC_MAP.md`, `docs/MILESTONE_HISTORY.md`, `docs/STATUS.md`, and `docs/HANDOFF.md`.

Acceptance criteria:

- GNN mode no longer silently falls back when a valid checkpoint and adapter are configured.
- Graph evaluation emits `runs/graph/{run_id}/metrics.json`.
- API response includes relationship outputs and real mode metadata.
- `no_relation` is reported separately from positive-class macro F1.
- Tests and metric-claim validation pass.

Recommended optional detector follow-up during M4:

- Add a non-bootstrap ONNX detector adapter for `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.
- Keep `heuristic_bootstrap` as an explicit fallback.
- Smoke `/health`, `/version`, and uploaded-image inference after adapter wiring.
- Do not hide detector limitations: high precision with weaker recall, 16 supported zero-mAP classes, and weak ledger/stem behavior.

### M5 - End-to-End Export Quality

Goal: make the product claim measurable instead of sample-only.

Implementation tasks:

- Define a fixed end-to-end holdout manifest.
- Run detector, assembly, MusicXML export, and MIDI export on every holdout page.
- Validate MusicXML parseability.
- Generate MIDI smoke artifacts.
- Compute structure-level comparison where ground truth is available.
- Save representative artifacts for presentation.

Acceptance criteria:

- `runs/e2e/{run_id}/metrics.json` exists.
- MusicXML and MIDI generation success rates are reported.
- Failures include examples and root-cause notes.
- The frontend can show at least one uploaded-image result end to end.

### M6 - AWS Public Demo

Goal: satisfy deployment evidence with a stable, low-cost public system.

Implementation tasks:

- Create ECR repository and ECS service.
- Deploy FastAPI container with CPU ONNX inference.
- Deploy frontend to S3 and CloudFront.
- Configure private artifact storage with short-lived download links.
- Add CloudWatch logging and smoke-test script outputs.
- Document cost controls and shutdown steps.

Acceptance criteria:

- Public frontend URL loads.
- Public API `/health` and `/version` pass.
- Sample transcription completes through the public service.
- Uploaded-image transcription completes through the public service.
- Smoke-test output is saved as deployment evidence.

### M7 - Final Grading Package

Goal: make the professor see a coherent story and evidence trail.

Implementation tasks:

- Freeze `README.md`, `MODEL_CARD.md`, `docs/RUBRIC_MAP.md`, `docs/STATUS.md`, and `docs/EXPERIMENTS.md`.
- Add final demo script and Q&A prep.
- Add screenshots of AWS service, UI, metric reports, and artifacts.
- Write limitations honestly: full taxonomy, small symbols, handwritten transfer, graph errors, export limits, deployment constraints.
- Prepare a concise presentation narrative around V2 improvements over V1.

Acceptance criteria:

- All local tests pass.
- Frontend build passes.
- Metric-claim validator passes.
- Public demo smoke passes or a documented fallback runbook exists.
- Rubric evidence map points to concrete files, runs, tests, and artifacts.

## Decision Log

| Decision | Current Default | Reason |
|---|---|---|
| Project track | Track A applied/deployment | Best fit for AWS demo and product flow |
| Detector taxonomy | Full DeepScores 136 classes | Major improvement over V1 15-class limit |
| Current detector artifact | YOLOv8m full run `detection_136class_yolov8m_v1` | Full configured run has V2 metrics, ONNX, and artifact hashes |
| Assembly taxonomy | `semantic_omr_v2` grouping | Keeps MusicXML/GNN practical without losing detector detail |
| Detector primary metric | `mAP@0.5:0.95` | Standard object detection metric |
| Graph primary metric | positive-class macro F1 | Prevents `no_relation` inflation |
| Deployment path | ECS/Fargate/ECR, S3, CloudFront | Low-cost public demo path |
| Current upload detector | `heuristic_bootstrap` | Integration-only path until trained ONNX detector adapter is wired |

## Weekly Operating Rhythm

1. Start a milestone branch.
2. Update `docs/STATUS.md` with the active milestone.
3. Implement code and tests.
4. Generate run artifacts if the milestone involves metrics.
5. Regenerate `docs/EXPERIMENTS.md` from runs.
6. Update `docs/RUBRIC_MAP.md` if new grading evidence exists.
7. Run tests, frontend build when relevant, and metric-claim validation.
8. Record blockers and next steps in `docs/HANDOFF.md` before switching context.

## Agent Prompt Source

Use `docs/AGENT_PROMPTS.md` to start future coding-agent sessions. It contains the exact current M4 prompt and archived prompts for prior milestones. See `docs/MILESTONE_HISTORY.md` for detailed evidence and next-step context across M1 through M7.
