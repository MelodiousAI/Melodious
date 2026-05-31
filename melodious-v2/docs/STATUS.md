# Status

## Current Phase

M6 - AWS Public Demo is active and deployment-prepared, but actual public deployment is blocked on account-local AWS values and AWS CLI availability in this workspace. M1 - Dataset Manifests, M2 - Metric Reproduction, M3 - Full 136-Class Detector, M4 - Real Assembly Runtime, and M5 - End-to-End Export Quality are complete enough to hand off. The full configured M3 detector run `detection_136class_yolov8m_v1` completed all 150 YOLOv8m epochs, was finalized from the selected `best.pt` checkpoint, wrote project-standard metric provenance, exported ONNX, copied model artifacts, and generated class/error analysis. M4 wired the legacy MUSCIMA GNN checkpoint into a V2 runtime adapter, added explicit checkpoint/fallback API metadata, and wrote a natural-candidate-edge graph evaluation run. M5 measured the fixed MUSCIMA holdout export path using XML-derived detector payload fixtures and wrote end-to-end artifact evidence.

The current detector artifact is ready for integration work, but the API still uses `heuristic_bootstrap` for uploaded images. M6 now has a concrete low-cost AWS runbook, environment-driven CORS for a deployed frontend, ECS task-template guidance, and reusable smoke tooling for `/health`, `/version`, sample transcription, and MusicXML/MIDI artifact download. The public URL smoke has not run because AWS CLI was not found locally and account-specific ECS/ECR/S3/CloudFront values are not available in the repository.

## Completed

- Clean V2 project structure created.
- Governance docs added from the start.
- Versioned detector payload contract generated at `docs/detector_payload_v2.schema.json`.
- Metric rules locked before training in `docs/METRICS.md`.
- Local API/UI scaffold verified with sample transcription.
- AWS deployment path selected: ECS Express Mode or ECS Fargate with ECR, S3, and CloudFront.
- DeepScores 136-class manifest run generated under `runs/data/deepscores_136_manifest/`.
- MUSCIMA graph page manifest run generated under `runs/data/muscima_graph_manifest/`.
- DeepScores duplicate image-id and filename leakage checks passed.
- DeepScores inferred work-group leakage check remains a warning with 202 repeated filename-inferred groups.
- MUSCIMA duplicate page-id leakage check passed.
- M2 reduced-class metric reproduction run generated under `runs/detection/detection_15class_repro_sample_v1/`.
- M3 materialized the M1 DeepScores YOLO dataset under `runs/data/deepscores_136_yolo_materialized/`.
- M3 smoke run generated under `runs/detection/detection_136class_yolov8s_smoke_v1/`.
- M3 smoke checkpoint and ONNX artifacts generated under `artifacts/models/detection_136class_yolov8s_smoke_v1/`.
- M3 full YOLOv8m training was launched on 2026-05-21, manually saved at clean epoch-20, epoch-74, and epoch-95 recovery points, resumed again, reached epoch 124, resumed from the latest run checkpoint on 2026-05-28, and completed epoch 150.
- M3 final run artifacts now exist under `runs/detection/detection_136class_yolov8m_v1/`: `metrics.json`, `report.md`, `manifest.json`, `artifacts.json`, `analysis.json`, `analysis.md`, `onnx_parity.json`, and copied `config.yaml`.
- M3 final model artifacts now exist under `artifacts/models/detection_136class_yolov8m_v1/`: `best.pt`, `best.onnx`, and `metadata.json`.
- `docs/EXPERIMENTS.md` was regenerated from `runs/**/metrics.json` and now includes the full YOLOv8m run.
- M4 legacy GNN checkpoint source was verified at `..\outputs\gnn_checkpoint.pt` with SHA256 `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`.
- M4 V2 GNN runtime adapter was added under `src/melodious_v2/assembly/legacy_gnn.py`.
- M4 API assembly mode metadata now includes checkpoint path, adapter name, and whether inference actually ran.
- M4 graph evaluation run exists under `runs/graph/graph_legacy_gnn_muscima_val_v1/`.
- `docs/EXPERIMENTS.md` includes `graph_legacy_gnn_muscima_val_v1`.
- M5 end-to-end run exists under `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/`.
- M5 exported MusicXML, MIDI, payload, and relationship artifacts for 14 MUSCIMA holdout XML-derived payload fixtures.
- `docs/EXPERIMENTS.md` includes `e2e_muscima_holdout_xml_fixture_v1`.
- `docs/AGENT_PROMPTS.md` now points the next agent to M6.
- M6 added environment-driven API CORS through `MELODIOUS_CORS_ORIGINS` for public frontend deployment.
- M6 added Python smoke tooling at `scripts/smoke_public_demo.py` and `src/melodious_v2/deployment/smoke.py`.
- M6 expanded `infra/aws/smoke_test.ps1` to verify sample transcription plus MusicXML/MIDI artifact downloads and optional JSON evidence output.
- M6 expanded `infra/aws/README.md` with ECR, ECS/Fargate, S3/CloudFront, smoke-test, and shutdown/cost-control commands.
- M6 updated `infra/aws/task-definition.template.json` with `MELODIOUS_CORS_ORIGINS` and `MELODIOUS_GNN_CHECKPOINT` placeholders.

## Latest Detector Result

Run id: `detection_136class_yolov8m_v1`.

Metric source: `runs/detection/detection_136class_yolov8m_v1/metrics.json`.

Evaluation split: `val` from `deepscores_136_yolo_materialized`.

Selected checkpoint: `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`.

Copied artifact: `artifacts/models/detection_136class_yolov8m_v1/best.pt`.

Copied ONNX: `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.

Checkpoint SHA256: `ea005a818902b3c14a12cc6594ef964e29eef99c771ac9a3238fc1d3ef8ce6ac`.

ONNX SHA256: `008ac7c75b8cca5c1cd8346ad84a2b0e27204863fcff2ccb0d39f034ebe5d4cb`.

Primary detector metric:

- `mAP@0.5:0.95`: 0.4747370751116288.

Secondary detector metrics:

- `mAP@0.5`: 0.5853211368313491.
- `precision@0.5`: 0.8274236461250144.
- `recall@0.5`: 0.4909790740632496.
- `F1@0.5`: 0.6162725385980492.

Training CSV summary from `manifest.json`:

- Completed rows: 150.
- Best training-row `mAP@0.5:0.95`: epoch 125 at 0.45579.
- Final epoch 150 training-row `mAP@0.5:0.95`: 0.44888.
- Final V2 validation pass on selected `best.pt`: `mAP@0.5:0.95` 0.4747370751116288.

Analysis summary from `analysis.json`:

- Validation classes with support: 103 of 136.
- Rare supported classes with support <= 10: 14.
- Supported validation classes with zero mAP: 16.
- Supported small-symbol classes: 35.
- Small-symbol mean `mAP@0.5:0.95`: 0.3194606161321027.
- Zero-mAP supported classes include `ledgerLine`, `stem`, `ottavaBracket`, several articulation classes, several fingering classes, `dynamicR`, `tremolo3`, `tuplet1`, and `tuplet5`.

ONNX parity:

- `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json` passed on fixed validation image `lg-10247684-aug-gonville--page-2.png`.
- PyTorch and ONNX both returned 300 boxes with identical class-count totals.
- Local ONNX inference fell back to CPU because `onnxruntime-gpu` is not installed.

## Latest Graph Result

Run id: `graph_legacy_gnn_muscima_val_v1`.

Metric source: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.

Evaluation split: `val` from `muscima_graph_manifest`.

Checkpoint source: `..\outputs\gnn_checkpoint.pt`.

Checkpoint SHA256: `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`.

Runtime adapter: `src/melodious_v2/assembly/legacy_gnn.py`.

Feature encoder: `reconstructed_training_node_encoder_seed_42`.

Primary graph metric:

- `positive_macro_f1`: 0.7590456327823909.

Required separate `no_relation` metrics:

- precision: 0.997066197258228.
- recall: 0.8936271931921403.
- F1: 0.9425171440096813.
- support: 41834.

Positive relationship metrics:

- `stem_notehead` F1: 0.6960721184803607 on 4441 validation candidate edges.
- `beam_notegroup` F1: 0.8220191470844213 on 1899 validation candidate edges.
- `slur_phrase` and `tie_sustained` have zero validation support in the legacy 15-class GNN contract.

Graph distribution:

- Natural candidate-edge distribution with no negative subsampling.
- 14 validation pages.
- 48174 candidate edges.
- 6340 positive candidate edges.
- 10680 predicted positive candidate edges.

Important graph caveat:

- The legacy checkpoint did not save the separate node feature encoder used to build training tensors. V2 reconstructs that encoder from seed `42`, matching the legacy training pipeline. This is documented in the run metrics and should be preserved until the graph model is retrained with a fully self-contained artifact.

## Latest End-to-End Export Result

Run id: `e2e_muscima_holdout_xml_fixture_v1`.

Metric source: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.

Evaluation split: `holdout` from `muscima_graph_manifest`.

Payload source: MUSCIMA XML-derived detector payload fixtures.

Assembly mode requested: `gnn`.

Primary end-to-end export metric:

- `musicxml_validity_rate`: 1.0.

Supporting export metrics:

- `midi_generation_success_rate`: 1.0.
- `page_success_rate`: 1.0.
- `page_count`: 14.
- `musicxml_valid_count`: 14.
- `midi_success_count`: 14.
- `failure_count`: 0.

Run volume:

- `detection_count_total`: 6348.
- `note_like_count_total`: 2563.
- `relationship_count_total`: 10637.
- `assembly_gnn_page_count`: 14.

Important end-to-end caveat:

- This is measured export validity and artifact generation from fixed ground-truth XML-derived payload fixtures. It is not trained detector uploaded-image quality. Uploaded-image detector inference remains `heuristic_bootstrap` until a tested ONNX detector adapter is added.

## Latest Verification

- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` with 32 tests before M6 deployment changes.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py src\melodious_v2\evaluation\full_detector.py`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --finalize-existing-run --workers 0 --device 0`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\evaluate_gnn_muscima.py --split val --device cpu`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_e2e_export_eval.py --split holdout --assembly-mode gnn`.
- Passed: API sample transcription smoke with `MELODIOUS_GNN_CHECKPOINT=..\outputs\gnn_checkpoint.pt`; response reported `applied_mode=gnn`, `fallback_applied=False`, `checkpoint_ready=True`, `inference_ran=True`, `adapter_name=legacy_muscima_gat`, and `relationship_count=4`.
- Passed: local API sample smoke without starting Uvicorn; `/health` returned `ok`, `/version` returned schema `2.0`, sample transcription completed, and the first artifact download returned 721 bytes.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\deployment\smoke.py scripts\smoke_public_demo.py src\melodious_v2\api\app.py`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_deployment_smoke.py`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --local-testclient --output runs\deploy\m6_local_smoke\smoke.json`; verified `/health`, `/version`, sample transcription, MusicXML download, and MIDI download.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` with 33 tests after M6 deployment changes.
- Passed: `cd frontend; npm run build`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`, checked 12 documentation files.

## Milestone Tracker

| Milestone | Status | Next Evidence |
|---|---|---|
| M0 - V2 Foundation | Done | Existing tests, schema, API/UI smoke |
| M1 - Dataset Manifests | Done | Manifest JSONs, class counts, leakage reports, tests |
| M2 - Metric Reproduction | Done | `runs/detection/detection_15class_repro_sample_v1/metrics.json`, generated experiment index |
| M3 - Full 136-Class Detector | Done | `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, `onnx_parity.json`, `artifacts/models/detection_136class_yolov8m_v1/metadata.json` |
| M4 - Real Assembly Runtime | Done | `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`, adapter tests, API mode proof |
| M5 - End-to-End Export Quality | Done | `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`, exported MusicXML/MIDI artifacts |
| M6 - AWS Public Demo | Active / blocked on AWS values | `infra/aws/README.md`, `scripts/smoke_public_demo.py`, local smoke evidence; public smoke pending |
| M7 - Final Grading Package | Planned | Frozen docs and presentation evidence |

## Active Blockers

- API detector runtime is still bootstrap/heuristic for uploaded images; the new YOLOv8m ONNX artifact exists but is not yet used by a non-bootstrap detector adapter.
- AWS resources are not provisioned from this workspace.
- AWS CLI was not found by `Get-Command aws -ErrorAction SilentlyContinue`, so no ECR/ECS/S3/CloudFront deployment command was run locally.
- Account-local AWS values are unavailable and must not be committed: region/profile, execution role ARN, task role ARN, subnet IDs, security group IDs, ALB target group/listener, S3 frontend bucket, CloudFront distribution ID, and public API host.
- DeepScores leakage report is `warning` because 202 filename-inferred work groups repeat across splits. Duplicate image ids and duplicate filenames passed.
- Full detector metrics are validation-split metrics. Test-set detector performance should be produced only after the team freezes the detector family and avoids iterative tuning on test data.
- Several high-support symbol classes still have zero detector mAP on validation, especially `ledgerLine` and `stem`; this is a real model limitation and should not be hidden in the final report.
- The M4 GNN is a legacy 15-class relationship model. It cannot represent every V2 detector class, and its feature encoder is reconstructed from seed `42` because the legacy checkpoint did not save that encoder as a separate artifact.
- The M5 end-to-end run measures export validity from XML-derived payload fixtures, not trained uploaded-image detector quality.

## Next Actions

1. Install/configure AWS CLI or run from an environment with AWS access.
2. Fill local generated deployment state from `infra/aws/task-definition.template.json`; keep it under ignored `infra/aws/generated/`.
3. Run the Backend Build And Push, ECS Task Definition, ECS Service, and Frontend Build And Publish sections in `infra/aws/README.md`.
4. Run `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --api-base-url https://REPLACE_WITH_PUBLIC_API_HOST --output runs\deploy\m6_public_smoke\smoke.json`.
5. Keep uploaded-image detector inference labeled `heuristic_bootstrap` unless a tested ONNX detector adapter is implemented.
6. After public smoke passes, update `docs/AGENT_PROMPTS.md` to M7 - Final Grading Package.

## Roadmap

See `docs/ROADMAP.md` for milestone definitions, acceptance criteria, and the weekly operating rhythm.
