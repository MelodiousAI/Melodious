# Submission Manifest

This manifest explains what is inside `FinalProduct/`.

## Top Level

| Path | Purpose |
|---|---|
| `README.md` | Start-here file for the final package. |
| `SUBMISSION_MANIFEST.md` | This file. |
| `OMITTED_FILES.md` | Explicit list of intentionally excluded files and folders. |
| `project_grading_rubric.md` | Rubric used to audit the project. |
| `presentation/` | Final presentation script, technical review TeX, slides, and proposal PDF. |
| `sample_inputs/` | Score images used for final local demo runs. |
| `sample_detections/` | Shared detector payload contract examples and MUSCIMA references. |
| `legacy_evidence/` | Original baseline, robustness, GNN checkpoint, and historical visualization evidence. |
| `melodious-v2/` | Curated v2 codebase and final evidence. |

## `melodious-v2/`

| Path | Purpose |
|---|---|
| `README.md` | Main setup, API, detector, graph, deployment, and demo instructions. |
| `MODEL_CARD.md` | Model limitations, intended use, and risk notes. |
| `requirements.txt`, `pyproject.toml` | Python dependency definitions. |
| `docker-compose.yml`, `.dockerignore`, `.env.example` | Local Docker/API environment files. |
| `src/` | Python package: API, OMR extraction, graph, export, evaluation, deployment smoke, and report code. |
| `scripts/` | Reproducible experiment, evaluation, API, extraction, and report scripts. |
| `configs/` | Detector, graph, and evaluation configs. |
| `tests/` | Python tests for contracts, graph/export logic, API, deployment smoke, and note extraction. |
| `frontend/` | React/Vite UI source plus built `dist/`, without `node_modules`. |
| `infra/` | Dockerfile, AWS deployment runbook, task template, and smoke helper. |
| `.github/` | CI and deployment workflow templates. |
| `docs/` | Curated final docs and evidence reports. |

## Final Docs

| Path | Purpose |
|---|---|
| `melodious-v2/docs/FINAL_RUBRIC_EVIDENCE.md` | Rubric-by-rubric checklist and remaining grade risks. |
| `melodious-v2/docs/FINAL_TECHNICAL_REPORT.md` | Compact final technical report. |
| `melodious-v2/docs/BASELINES_AND_GRAPH_COMPARISONS.md` | Non-AI baselines and graph-vs-non-graph comparison. |
| `melodious-v2/docs/RESPONSIBLE_ML.md` | Explainability, bias/fairness, privacy/leakage, and robustness coverage. |
| `melodious-v2/docs/EXPERIMENTS.md` | Generated run index from selected `runs/**/metrics.json`. |
| `melodious-v2/docs/RUBRIC_MAP.md` | Evidence map for grading. |
| `melodious-v2/docs/ARCHITECTURE.md` | System architecture. |
| `melodious-v2/docs/DATA_CARD.md` | Data documentation. |
| `melodious-v2/docs/METRICS.md` | Metric definitions and provenance policy. |
| `melodious-v2/docs/NOTE_EXTRACTION_DEMO.md` | Local note-extraction demo evidence. |
| `melodious-v2/docs/METRIC_IMPROVEMENT.md` | Detector improvement and tiled pilot notes. |

## Selected Model Artifacts

| Path | Purpose |
|---|---|
| `melodious-v2/artifacts/models/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/` | Best full-page detector PT/ONNX and metadata. |
| `melodious-v2/artifacts/models/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final/` | Final test-evaluation checkpoint metadata and PT copy. |
| `melodious-v2/artifacts/models/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/` | Tiled thin-symbol pilot PT/ONNX and metadata. |
| `melodious-v2/artifacts/models/note_extraction_default_fullpage/` | Local default note-extraction checkpoint. |
| `melodious-v2/artifacts/models/note_extraction_tiled_stem_pilot/` | Local tiled thin-symbol checkpoint. |
| `legacy_evidence/gnn_checkpoint.pt` | Legacy GNN checkpoint used for graph relationship evidence. |

## Selected Runs

| Path | Purpose |
|---|---|
| `melodious-v2/runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/` | Selected detector validation run. |
| `melodious-v2/runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final/` | Final held-out detector test run. |
| `melodious-v2/runs/detection/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/` | Tiled validation pilot for stems/thin symbols. |
| `melodious-v2/runs/detection/detection_136class_class_coverage_audit_v1/` | Class support and coverage audit. |
| `melodious-v2/runs/graph/graph_legacy_gnn_muscima_val_v1/` | Main graph relationship metric run. |
| `melodious-v2/runs/graph/graph_non_graph_heuristic_muscima_val_v1/` | Same-edge deterministic non-graph graph baseline. |
| `melodious-v2/runs/e2e/e2e_muscima_holdout_xml_fixture_v1/` | Holdout MusicXML/MIDI export fixture run. |
| `melodious-v2/runs/deploy/` | Local product API smoke evidence. |
| `melodious-v2/runs/demo/` | Final selected local demo artifacts. |
| `melodious-v2/runs/data/` | Dataset manifests and leakage reports only. |

## Legacy Evidence

| Path | Purpose |
|---|---|
| `legacy_evidence/baseline_template_results.json` | Non-AI template-matching detector baseline. |
| `legacy_evidence/baseline_hog_results.json` | HOG/SVM detector baseline. |
| `legacy_evidence/robustness/` | Historical robustness results and plots. |
| `legacy_evidence/visualizations/` | Historical baseline and graph visualizations. |
| `legacy_evidence/gnn_training_results.json` | Historical GNN training evidence. |

## Notes

- Selected run folders exclude duplicate `.pt` and `.onnx` files when the same
  model files are already centralized under `artifacts/models/`.
- The package excludes raw full datasets and dependency folders. See
  `OMITTED_FILES.md`.
