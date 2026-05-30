# Milestone History and Evidence Ledger

This ledger is the detailed cross-milestone handoff for Melodious V2. It records what each milestone proved, the exact artifacts that support the claim, known limitations, and the next command or implementation step. Metrics named here must be backed by generated `runs/**/metrics.json` files.

## Evidence Rules

- Treat `docs/METRICS.md` as the source of metric definitions.
- Treat `docs/DATA_CARD.md` as the source of dataset split and leakage policy.
- Treat `docs/EXPERIMENTS.md` as the generated metric index.
- Treat `docs/HANDOFF.md` as the chronological agent log.
- Do not report model quality without a run id, split, config path, artifact hash, and metrics JSON.
- Keep generated datasets, model checkpoints, logs, and run outputs out of Git. They live under ignored folders such as `runs/` and `artifacts/`.

## M0 - V2 Foundation

Status: done.

Purpose:

- Create a clean V2 workspace separate from the legacy parent project.
- Establish strict contracts, metric policy, API/UI scaffolding, and deployment scaffolding before adding new ML claims.

Main evidence:

- Package layout under `src/melodious_v2/`.
- Contract schema at `docs/detector_payload_v2.schema.json`.
- Metric definitions in `docs/METRICS.md`.
- API and frontend scaffolds under `src/melodious_v2/api/` and `frontend/`.
- AWS deployment path under `infra/`.

Known limits after M0:

- Detector runtime used bootstrap/heuristic integration paths.
- No full detector training had run in V2.
- No graph checkpoint was wired into the API.

## M1 - Dataset Manifests

Status: done.

Purpose:

- Make detector and graph data splits reproducible before training.
- Preserve DeepScores source train/test separation.
- Create deterministic train/validation split from the DeepScores source train JSON.
- Create deterministic MUSCIMA train/validation/holdout graph page split.
- Run leakage checks and write the ambiguity explicitly.

Source inputs:

- DeepScores source train JSON: `../dataset_ds2_dense/deepscores_train.json`.
- DeepScores source test JSON: `../dataset_ds2_dense/deepscores_test.json`.
- DeepScores source images: `../dataset_ds2_dense/images/`.
- MUSCIMA XML annotations: `../data/muscima-pp/v2.0/data/annotations/`.

Generated DeepScores artifacts:

- `runs/data/deepscores_136_manifest/manifest.json`.
- `runs/data/deepscores_136_manifest/train.json`.
- `runs/data/deepscores_136_manifest/val.json`.
- `runs/data/deepscores_136_manifest/test.json`.
- `runs/data/deepscores_136_manifest/class_counts.json`.
- `runs/data/deepscores_136_manifest/leakage_report.json`.
- `runs/data/deepscores_136_manifest/yolo_dataset.yaml`.
- `runs/data/deepscores_136_manifest/generated/labels/{train,val,test}/`.
- `runs/data/deepscores_136_manifest/generated/image_lists/{train,val,test}.txt`.

DeepScores split counts from the latest local manifest:

- Train: 1226 images, 793828 raw annotations, 793514 generated YOLO labels, 115 classes with support.
- Validation: 136 images, 96005 raw annotations, 95941 generated YOLO labels, 103 classes with support.
- Test: 352 images, 244335 raw annotations, 244255 generated YOLO labels, 110 classes with support.

DeepScores leakage result:

- Duplicate image ids across train/validation/test: passed.
- Duplicate filenames across train/validation/test: passed.
- Filename-inferred work-group repeats: warning.
- Warning detail: 202 inferred work groups repeat across splits.
- Interpretation: the work-group check is heuristic because the split metadata does not expose a stable score/work identifier independent of generated filename style and augmentation font. It is not treated as automatic failure because true duplicate image ids and filenames passed.

Generated MUSCIMA artifacts:

- `runs/data/muscima_graph_manifest/manifest.json`.
- `runs/data/muscima_graph_manifest/train.json`.
- `runs/data/muscima_graph_manifest/val.json`.
- `runs/data/muscima_graph_manifest/holdout.json`.
- `runs/data/muscima_graph_manifest/leakage_report.json`.
- `runs/data/muscima_graph_manifest/class_summary.json`.

MUSCIMA split counts from the latest local manifest:

- Train: 112 pages, 82206 parsed nodes.
- Validation: 14 pages, 10509 parsed nodes.
- Holdout: 14 pages, 10199 parsed nodes.

MUSCIMA leakage result:

- Duplicate page ids across train/validation/holdout: passed.

M1 commands that matter:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\build_dataset_manifests.py`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`.

M1 tests added:

- Deterministic splitting is repeatable.
- DeepScores manifest summaries report `class_count = 136`.
- Duplicate DeepScores ids across splits are caught.
- MUSCIMA page ids do not overlap across train/validation/holdout.

M1 remaining risk:

- DeepScores work-group leakage is warning-level because grouping is inferred from filenames.
- The M1 `yolo_dataset.yaml` keeps raw images outside the repo and lists source image paths. Ultralytics training needed M3 materialization into a standard `images/` and `labels/` layout.

## M2 - Metric Reproduction

Status: done.

Purpose:

- Prove the V2 detector metric code and report/provenance path before claiming new training results.
- Reuse legacy 15-class detector sample outputs when available instead of training a new model.

Source inputs:

- Legacy sample detector outputs: `../sample_detections/model_outputs_quick/`.
- Matching DeepScores train/test annotations: `../dataset_ds2_dense/deepscores_train.json` and `../dataset_ds2_dense/deepscores_test.json`.
- Legacy checkpoint hash source: `../outputs/yolov8_runs/train/weights/best.pt`.

Implemented code:

- `src/melodious_v2/evaluation/reduced_detection.py`.
- `scripts/run_detection_15class_repro.py`.
- Tests in `tests/test_detection_repro.py`.
- Strict JSON metric writing in `src/melodious_v2/reports.py`.

Generated run:

- Run id: `detection_15class_repro_sample_v1`.
- Run directory: `runs/detection/detection_15class_repro_sample_v1/`.
- Metrics: `runs/detection/detection_15class_repro_sample_v1/metrics.json`.
- Report: `runs/detection/detection_15class_repro_sample_v1/report.md`.
- Manifest: `runs/detection/detection_15class_repro_sample_v1/manifest.json`.
- Artifacts: `runs/detection/detection_15class_repro_sample_v1/artifacts.json`.
- Config copy: `runs/detection/detection_15class_repro_sample_v1/config.yaml`.

M2 run scope:

- Evaluated 5 legacy sample prediction payloads.
- Used 744 detector predictions.
- Matched against 2080 reduced-class DeepScores targets.
- Reduced full DeepScores annotations into `deepscores_15_reduced`.
- Wrote checkpoint SHA256 in metrics provenance.

M2 metric provenance:

- Primary metric and value are indexed in `docs/EXPERIMENTS.md`.
- Full metric payload lives in `runs/detection/detection_15class_repro_sample_v1/metrics.json`.
- The run is a reduced-class sample reproduction, not final detector quality for the 136-class system.

M2 commands that matter:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_15class_repro.py`.
- `..\.venv\Scripts\python.exe -m json.tool runs\detection\detection_15class_repro_sample_v1\metrics.json`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`.

M2 remaining risk:

- The run is intentionally small and reduced-class.
- It proves the scoring/report path, not the final model.
- It does not replace M3 full-taxonomy training.

## M3 - Full 136-Class Detector

Status: done. A constrained full-taxonomy smoke run proved the path, and the full configured 150-epoch YOLOv8m run `detection_136class_yolov8m_v1` now has V2 metric provenance, analysis artifacts, ONNX export, parity evidence, and copied model metadata.

Purpose:

- Train/evaluate a 136-class detector using the M1 DeepScores manifest.
- Produce deployable model artifacts and metric provenance.
- Surface class gaps, small-symbol behavior, and artifact hashes.

Environment verified on 2026-05-20:

- Python environment: `..\.venv\Scripts\python.exe`.
- PyTorch: installed.
- CUDA: available.
- GPU: NVIDIA GeForce RTX 3080 Laptop GPU, 16 GB VRAM.
- Ultralytics: installed.
- ONNX and ONNX Runtime: installed.
- `nvidia-smi`: passed.
- Generated M1 image lists: train/validation/test all point to existing image files.
- Generated M1 labels: train/validation/test label file counts match image list counts.

M3 materialization:

- Script: `scripts/run_detection_136class_yolo.py --materialize-only`.
- Helper: `src/melodious_v2/evaluation/full_detector.py`.
- Output dataset: `runs/data/deepscores_136_yolo_materialized/`.
- Output YAML: `runs/data/deepscores_136_yolo_materialized/dataset.yaml`.
- Purpose: convert M1 image lists and generated labels into Ultralytics' expected `images/{split}` and `labels/{split}` layout.
- Initial hardlink attempt was not permitted by the filesystem, so the materializer copied images into ignored `runs/data/deepscores_136_yolo_materialized/`.
- Later materialization runs see existing image and label files.
- Current materialized counts: train 1226 images/labels, validation 136 images/labels, test 352 images/labels.

M3 smoke run:

- Run id: `detection_136class_yolov8s_smoke_v1`.
- Command:
  - `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --smoke --epochs 1 --imgsz 640 --batch 2 --workers 0 --device 0`
- Model seed: local `../yolov8s.pt`.
- Reason for smoke constraint: the local cache had `yolov8s.pt`, not `yolov8m.pt`; the full 150-epoch YOLOv8m run is longer and should be launched intentionally.
- Training split: full 136-class train split from M1.
- Validation split: M1 validation split.
- Epochs: 1.
- Image size: 640.
- Batch size: 2.
- Workers: 0, chosen for Windows stability.
- Export: ONNX succeeded.

Generated M3 smoke run artifacts:

- `runs/detection/detection_136class_yolov8s_smoke_v1/metrics.json`.
- `runs/detection/detection_136class_yolov8s_smoke_v1/report.md`.
- `runs/detection/detection_136class_yolov8s_smoke_v1/manifest.json`.
- `runs/detection/detection_136class_yolov8s_smoke_v1/artifacts.json`.
- `runs/detection/detection_136class_yolov8s_smoke_v1/config.yaml`.
- `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.json`.
- `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.md`.
- `artifacts/models/detection_136class_yolov8s_smoke_v1/best.pt`.
- `artifacts/models/detection_136class_yolov8s_smoke_v1/best.onnx`.
- `artifacts/models/detection_136class_yolov8s_smoke_v1/metadata.json`.

M3 smoke artifact hashes:

- Checkpoint SHA256: `984adb77e0934940a2143e4a715a81302585d5cce5891a1fb215bc07496f7835`.
- ONNX SHA256: `7c73f314e4799b8dc71db2456a3126ffd052752877e23ae484ff76ffa10457cd`.

M3 smoke metric provenance:

- Primary metric and value are indexed in `docs/EXPERIMENTS.md`.
- Full metric payload lives in `runs/detection/detection_136class_yolov8s_smoke_v1/metrics.json`.
- The run is a smoke-quality full-taxonomy detector run and must not be presented as the final configured detector.

M3 smoke analysis:

- Analysis file: `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.json`.
- Supported validation classes: 103 of 136.
- Rare supported validation classes with support at or below 10: 14.
- Supported validation classes with zero mAP in this smoke run: 93.
- Small-symbol supported classes: 35.
- Small-symbol mean mAP in this smoke run: 0.0.
- Error artifacts saved by Ultralytics include confusion matrices, precision/recall curves, F1 curve, and validation batch prediction previews under `runs/detection/detection_136class_yolov8s_smoke_v1/ultralytics/val_val/`.

M3 full YOLOv8m final result:

- Run id: `detection_136class_yolov8m_v1`.
- Final metrics: `runs/detection/detection_136class_yolov8m_v1/metrics.json`.
- Final analysis: `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- Final ONNX parity: `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`.
- Final model metadata: `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.
- Selected checkpoint: `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`.
- Copied checkpoint: `artifacts/models/detection_136class_yolov8m_v1/best.pt`.
- Copied ONNX: `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.
- Checkpoint SHA256: `ea005a818902b3c14a12cc6594ef964e29eef99c771ac9a3238fc1d3ef8ce6ac`.
- ONNX SHA256: `008ac7c75b8cca5c1cd8346ad84a2b0e27204863fcff2ccb0d39f034ebe5d4cb`.
- Primary validation metric `mAP@0.5:0.95`: 0.4747370751116288.
- Secondary validation `mAP@0.5`: 0.5853211368313491.
- `precision@0.5`: 0.8274236461250144.
- `recall@0.5`: 0.4909790740632496.
- `F1@0.5`: 0.6162725385980492.
- Supported validation classes: 103 of 136.
- Supported validation classes with zero mAP: 16.
- Supported small-symbol classes: 35.
- Small-symbol mean `mAP@0.5:0.95`: 0.3194606161321027.
- ONNX parity passed on one fixed validation image; PyTorch and ONNX both returned 300 boxes with identical class-count totals.
- API detector wiring remains a follow-up: upload inference still uses `heuristic_bootstrap` until a non-bootstrap ONNX detector adapter is implemented and tested.

M3 full YOLOv8m resumed run:

- Run id: `detection_136class_yolov8m_v1`.
- Launch date: 2026-05-21.
- Launch mode: escalated hidden Windows `Start-Process`, because sandboxed detached launches were killed when the tool returned.
- PID file: `runs/detection/detection_136class_yolov8m_v1/full_train.pid`.
- PID observed at launch: `28848`; child Python PID observed: `23140`.
- Stdout log: `runs/detection/detection_136class_yolov8m_v1/full_train_stdout.log`.
- Stderr log: `runs/detection/detection_136class_yolov8m_v1/full_train_stderr.log`.
- Startup evidence: stdout showed Ultralytics YOLOv8m, CUDA on NVIDIA GeForce RTX 3080 Laptop GPU, `nc=136`, `epochs=150`, `imgsz=1024`, `batch=4`, `workers=0`, and training started at epoch `1/150`.
- GPU evidence: `nvidia-smi` showed roughly 13.9 GB of 16 GB GPU memory in use during the live check.
- Recovery evidence after epoch 1: `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/results.csv`, `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`, and `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/last.pt` exist.
- Later progress evidence: training reached epoch 21 after epoch 20 completed.
- Manual stop evidence: after the user requested a pause, the run was allowed to finish epoch 20, copied into a manual checkpoint folder, load-verified, and then stopped during epoch 21.
- Manual checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/`.
- Manual checkpoint files: `last.pt`, `best.pt`, `results.csv`, `args.yaml`, `full_train_stdout.log`, `full_train_stderr.log`, `metadata.json`, and `README.md`.
- Load verification: `last.pt` loaded through Ultralytics with `task=detect`, `class_count=136`, first class `brace`, and last class `ottavaBracket`.
- Resume date: 2026-05-21.
- Resume PID file: `runs/detection/detection_136class_yolov8m_v1/resume_train.pid`; launch value was `30204`.
- Resume stdout log: `runs/detection/detection_136class_yolov8m_v1/resume_train_stdout.log`.
- Resume stderr log: `runs/detection/detection_136class_yolov8m_v1/resume_train_stderr.log`.
- Resume evidence: stdout says `Resuming training ... from epoch 21 to 150 total epochs`; later progress reached a completed epoch 74 before the second manual stop.
- Resume GPU evidence: `nvidia-smi` showed about 16.1 GB of 16.4 GB GPU memory in use during the epoch 21 check.
- Last completed Ultralytics result row: `20,7127.23,0.88507,0.55,0.80892,0.70012,0.38238,0.44051,0.32645,0.85344,0.48277,0.78277,6.20966e-05,6.20966e-05,6.20966e-05`.
- Interpreted interim validation values from that row: epoch 20, precision 0.70012, recall 0.38238, `mAP@0.5` 0.44051, and `mAP@0.5:0.95` 0.32645.
- Strict JSON verification passed for the manual checkpoint metadata.
- Second manual stop date: 2026-05-22.
- Current manual checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/`.
- Current manual checkpoint files: `last.pt`, `best.pt`, `results.csv`, `args.yaml`, `resume_train_stdout.log`, `resume_train_stderr.log`, `resume_train.pid`, `metadata.json`, and `README.md`.
- Current checkpoint load verification: copied `last.pt` loaded through Ultralytics with `task=detect`, `class_count=136`, first class `brace`, and last class `ottavaBracket`.
- Current checkpoint stop verification: parent PID `30204` and child PIDs `35140` and `36816` were stopped, and a final Python process check showed no Python training process.
- Latest completed Ultralytics result row at the current recovery point: `74,42230.1,0.72343,0.40615,0.78015,0.79589,0.46394,0.55051,0.41922,0.72112,0.37745,0.76312,3.67922e-05,3.67922e-05,3.67922e-05`.
- Interpreted interim validation values from that row: epoch 74, precision 0.79589, recall 0.46394, `mAP@0.5` 0.55051, and `mAP@0.5:0.95` 0.41922.
- Best completed interim `mAP@0.5:0.95` so far: epoch 73 at 0.42645, with precision 0.82353, recall 0.46912, and `mAP@0.5` 0.55914.
- SHA256 hashes in current checkpoint metadata: `last.pt` = `4c066147ce044a953f9d8f8dd3d2f81c6dda964cdf7d30e75fee9d8ca94549b3`; `best.pt` = `afd434a4cf044b068b57266961cadf3da3baa4dc75a6ce6ce7a621397fd1b21c`; `results.csv` = `efe8bd70f5ecb8766dc9dc924ec513a05f8eec45671c6e4000d8c6742634d154`.
- Resume-from-epoch-74 date: 2026-05-22.
- Resume-from-epoch-74 PID file: `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train.pid`; launch value was `14020`.
- Resume-from-epoch-74 stdout log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train_stdout.log`.
- Resume-from-epoch-74 stderr log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train_stderr.log`.
- Resume-from-epoch-74 evidence: stdout confirms the epoch-74 checkpoint path, 136-class head, `epochs=150`, `imgsz=1024`, `batch=4`, materialized DeepScores dataset YAML, and `Resuming training ... from epoch 75 to 150 total epochs`.
- Third manual stop date: 2026-05-22.
- Current manual checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/`.
- Current manual checkpoint files: `last.pt`, `best.pt`, `results.csv`, `args.yaml`, `resume_epoch74_train_stdout.log`, `resume_epoch74_train_stderr.log`, `resume_epoch74_train.pid`, `metadata.json`, and `README.md`.
- Current checkpoint load verification: copied `last.pt` loaded through Ultralytics with `task=detect`, `class_count=136`, first class `brace`, and last class `ottavaBracket`.
- Current checkpoint stop verification: the live training wrapper and Python trainer were stopped; a final Python process check showed no Python training process.
- Latest completed Ultralytics result row at the current recovery point: `95,11161,0.69419,0.38338,0.7773,0.81908,0.47262,0.56329,0.43327,0.70427,0.36335,0.76162,2.69516e-05,2.69516e-05,2.69516e-05`.
- Interpreted interim validation values from that row: epoch 95, precision 0.81908, recall 0.47262, `mAP@0.5` 0.56329, and `mAP@0.5:0.95` 0.43327.
- Best completed interim `mAP@0.5:0.95` so far: epoch 90 at 0.44043, with precision 0.79210, recall 0.48034, and `mAP@0.5` 0.57137.
- SHA256 hashes in current checkpoint metadata: `last.pt` = `9e5f31e3ce3e7c7e43c2a4b19d3731ff8d33c8cf0f191017b6dcf632f39618e8`; `best.pt` = `a9097ae3ced563370e5094af9946ec1ff68c17f43605f6846f8343658e351204`; `results.csv` = `994906ca24b6b2e24d1b12cde36b8a5f68710db0e420132e5c5b70732e3f4995`.
- Resume-from-epoch-95 date: 2026-05-26.
- Resume-from-epoch-95 PID file: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train.pid`; launch value was `30436`.
- Resume-from-epoch-95 stdout log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stdout.log`.
- Resume-from-epoch-95 stderr log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stderr.log`.
- Resume-from-epoch-95 evidence: stdout confirms the epoch-95 checkpoint path, 136-class head, `epochs=150`, `imgsz=1024`, `batch=4`, materialized DeepScores dataset YAML, and `Resuming training ... from epoch 96 to 150 total epochs`.
- Resume-from-latest-checkpoint date: 2026-05-28.
- Resume-from-latest-checkpoint PID file: `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train.pid`; launch value was `24516`.
- Resume-from-latest-checkpoint evidence: stdout confirms `Resuming training ... from epoch 125 to 150 total epochs`.
- Final training evidence: `resume_epoch124_train_stdout.log` reaches epoch 150/150 and final Ultralytics validation output.
- V2 finalization command: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --finalize-existing-run --workers 0 --device 0`.
- Finalization added a reproducible finalize-only mode to `scripts/run_detection_136class_yolo.py`; it evaluates an existing Ultralytics train directory, exports ONNX, writes V2 metric/report/manifest/artifact files, copies model artifacts, and writes ONNX parity evidence without retraining.

M3 final verification commands:

```powershell
$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --finalize-existing-run --workers 0 --device 0
$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md
$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py
```

## M4 - Real Assembly Runtime

Status: done. M4 wired a real legacy MUSCIMA GNN checkpoint into the V2 assembly runtime, added explicit checkpoint/fallback metadata, evaluated the model on the fixed M1 MUSCIMA validation manifest, and regenerated the experiment index from the graph run.

Detailed goal:

- Replace graph/assembly scaffold risk with a real GNN adapter path.
- Load a checkpoint through a clearly documented configuration variable such as `MELODIOUS_GNN_CHECKPOINT`.
- Evaluate on the natural edge distribution.
- Report positive-class macro F1 as the graph primary metric.
- Keep `no_relation` precision, recall, F1, and support separate from the positive-class headline metric.

Source inputs:

- MUSCIMA validation manifest: `runs/data/muscima_graph_manifest/val.json`.
- MUSCIMA root manifest: `runs/data/muscima_graph_manifest/manifest.json`.
- Legacy checkpoint: `..\outputs\gnn_checkpoint.pt`.
- Legacy training summary: `..\outputs\gnn_training_results.json`.
- Legacy handoff: `..\sample_detections\GNN_HANDOFF.md`.

Implemented code:

- `src/melodious_v2/assembly/legacy_gnn.py`.
- `src/melodious_v2/assembly/service.py`.
- `scripts/evaluate_gnn_muscima.py`.
- `tests/test_assembly_gnn_runtime.py`.
- API metadata coverage in `tests/test_api.py`.
- Additional graph metric coverage in `tests/test_graph_metrics.py`.

Checkpoint contract:

- Model class: legacy 3-layer GAT edge classifier.
- Input symbol contract: 15 classes (`notehead-full`, `notehead-half`, `notehead-whole`, clefs, rests, accidentals, `beam`, `stem`).
- Relationship classes: `no_relation`, `stem_notehead`, `beam_notegroup`, `slur_phrase`, `tie_sustained`.
- Candidate graph: k-nearest plus vertical-overlap edges with `k_neighbors=8`.
- Checkpoint SHA256: `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`.
- Important feature-contract caveat: the legacy training data used a separate seeded node feature encoder that was not saved in the checkpoint. V2 reconstructs it from seed `42` and records this in metrics/artifacts. Using the checkpoint model's unused internal node encoder predicts only `no_relation`, so the reconstructed encoder is required for the legacy contract to be meaningful.

Generated run:

- Run id: `graph_legacy_gnn_muscima_val_v1`.
- Run directory: `runs/graph/graph_legacy_gnn_muscima_val_v1/`.
- Metrics: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.
- Report: `runs/graph/graph_legacy_gnn_muscima_val_v1/report.md`.
- Manifest: `runs/graph/graph_legacy_gnn_muscima_val_v1/manifest.json`.
- Artifacts: `runs/graph/graph_legacy_gnn_muscima_val_v1/artifacts.json`.
- Config copy: `runs/graph/graph_legacy_gnn_muscima_val_v1/config.yaml`.

M4 metric provenance:

- Commit in metrics: `ab2d550`.
- Dataset id: `muscima_graph_manifest`.
- Split: `val`.
- Taxonomy id: `semantic_omr_v2`.
- Metric version: `v2.0`.
- Artifact SHA256: `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`.

M4 graph metrics:

- Primary `positive_macro_f1`: 0.7590456327823909.
- Accuracy, reported only as a secondary diagnostic: 0.9049902436999211.
- Separate `no_relation` precision: 0.997066197258228.
- Separate `no_relation` recall: 0.8936271931921403.
- Separate `no_relation` F1: 0.9425171440096813.
- Separate `no_relation` support: 41834.
- `stem_notehead` precision: 0.5416510083928348.
- `stem_notehead` recall: 0.9736545823012835.
- `stem_notehead` F1: 0.6960721184803607.
- `stem_notehead` support: 4441.
- `beam_notegroup` precision: 0.7004078605858362.
- `beam_notegroup` recall: 0.9947340705634544.
- `beam_notegroup` F1: 0.8220191470844213.
- `beam_notegroup` support: 1899.
- `slur_phrase` and `tie_sustained` have zero validation support in this legacy 15-class graph contract.

M4 evaluated distribution:

- Distribution label: `natural_candidate_edges`.
- Negative sampling: none.
- Validation pages: 14.
- Candidate edges: 48174.
- Positive candidate edges: 6340.
- Predicted positive candidate edges: 10680.

API/runtime behavior:

- `MELODIOUS_GNN_CHECKPOINT` or an explicit checkpoint path enables the real adapter.
- `applied_mode = "gnn"` is returned only after checkpoint loading and inference both succeed.
- Missing checkpoint with requested `gnn` returns `applied_mode = "checkpoint_missing"` and heuristic fallback relationships.
- Bad checkpoint or inference failure returns `applied_mode = "heuristic_fallback"` with explicit reason text.
- API smoke with `MELODIOUS_GNN_CHECKPOINT=..\outputs\gnn_checkpoint.pt` returned `applied_mode=gnn`, `fallback_applied=False`, `checkpoint_ready=True`, `inference_ran=True`, `adapter_name=legacy_muscima_gat`, and `relationship_count=4`.

M4 verification commands:

```powershell
$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\evaluate_gnn_muscima.py --split val --device cpu
$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests
$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md
$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py
```

M4 remaining risk:

- The GNN is a legacy 15-class graph model, not a full 136-class V2 relationship model.
- The feature encoder reconstruction is deterministic and documented, but a future retrain should save a self-contained checkpoint that includes all feature-transform state.
- The graph result is a validation result on MUSCIMA-derived graph inputs, not a measured uploaded-image end-to-end result.

## M5 - End-to-End Export Quality

Status: active.

Detailed goal:

- Measure upload-to-MusicXML/MIDI quality on fixed holdout pages.
- Use real detector outputs and real assembly mode where available.
- Keep estimates separate from measured end-to-end results.

Implementation checklist:

- Define an end-to-end holdout manifest.
- Run detector, assembly, MusicXML export, and MIDI export on every holdout page.
- Validate MusicXML parseability.
- Generate MIDI smoke artifacts.
- Save example failures with root-cause notes.
- Write `runs/e2e/{run_id}/metrics.json`.
- Update frontend evidence if uploaded-image transcription is demonstrated end to end.

Main risk:

- MusicXML can be structurally valid while musically incomplete, so the report needs structure-level checks and examples, not only parse success.

## M6 - AWS Public Demo

Status: planned.

Detailed goal:

- Deploy the API and frontend publicly at low cost.
- Keep model artifacts private and serve generated outputs through controlled links.

Implementation checklist:

- Build and push API image to ECR.
- Deploy FastAPI on ECS Express Mode or ECS Fargate.
- Deploy frontend to S3 and CloudFront.
- Configure private artifact storage.
- Run public `/health`, `/version`, sample transcription, and uploaded-image smoke tests.
- Save smoke-test output as deployment evidence.
- Document shutdown and cost controls.

Main risk:

- Large detector artifacts and CPU inference latency may require ONNX optimization or constrained upload limits.

## M7 - Final Grading Package

Status: planned.

Detailed goal:

- Freeze the grading narrative and evidence map.
- Make every claim traceable to a run, test, artifact, or document.

Implementation checklist:

- Freeze `README.md`, `MODEL_CARD.md`, `docs/RUBRIC_MAP.md`, `docs/STATUS.md`, and `docs/EXPERIMENTS.md`.
- Add final demo script and Q&A prep.
- Add screenshots for UI, deployed API, generated artifacts, and metric reports.
- Document limitations honestly: rare classes, small symbols, handwritten transfer, graph errors, export limits, and deployment constraints.
- Confirm all tests pass.
- Confirm frontend build passes.
- Confirm metric-claim validator passes.
- Confirm public smoke passes or document the fallback runbook.

Main risk:

- The final package can become inconsistent if metrics are copied manually instead of regenerated from run artifacts.
