# Rubric Evidence Map

Project type: Track A, applied/deployment.  
Graph project: yes.

## Problem and Fit

- Specific problem: README project summary and API contract.
- User/deployer: README, MODEL_CARD, AWS deployment docs.
- Why ML: M2 reduced-class detector reproduction in `runs/detection/detection_15class_repro_sample_v1/metrics.json`; M3 full-taxonomy smoke detector in `runs/detection/detection_136class_yolov8s_smoke_v1/metrics.json`; full YOLOv8m detector metrics in `runs/detection/detection_136class_yolov8m_v1/metrics.json`; graph baselines remain future generated reports.
- Success criteria: docs/METRICS.md, generated run reports, and `docs/EXPERIMENTS.md`.

## Technical Rigor and Responsible ML

- Task and data: docs/DATA_CARD.md.
- Non-AI baseline: baseline scripts and generated reports.
- Method substance: detector, graph assembly, export, and deployment modules.
- Preprocessing/leakage: dataset conversion tests and manifests.
- Splits/metrics/protocol: docs/METRICS.md, dataset manifests, and run manifests.
- Error analysis: model card plus generated detector analysis at `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.json` and `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- Limitations/tradeoffs: MODEL_CARD.md.
- Graph core object: assembly module, relationship metrics, graph tests.
- Graph vs non-graph: fixed same-input comparison planned in end-to-end holdout run.
- Responsible ML: model card, robustness scripts, privacy/deployment notes.

## Deployment and Engineering

- Dockerized API: infra/docker/Dockerfile.api.
- Separation of concerns: package layout under `src/melodious_v2/`.
- Reproducible run path: README and scripts.
- UI/demo: frontend upload/results flow.
- Running artifact: ECS/Fargate deployment templates and smoke tests.

## GitHub and Documentation

- Structure: README layout.
- Setup/run: README commands.
- Architecture/method: docs/ARCHITECTURE.md and module docs.
- Results/logs/ablations: docs/EXPERIMENTS.md from `runs/**/metrics.json`; current detector runs include `detection_15class_repro_sample_v1`, `detection_136class_yolov8s_smoke_v1`, and `detection_136class_yolov8m_v1`.
- Training checkpoint evidence: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/metadata.json`, `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/metadata.json`, and `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json` document manual recovery points. Final detector evidence is `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `runs/detection/detection_136class_yolov8m_v1/analysis.json`, `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.
- Data/limits/ethics/deployment: DATA_CARD, MODEL_CARD, infra docs.

## Presentation and Creativity

- Headline improvements:
  - full 136-class detector path,
  - strict metric provenance,
  - reduced-class metric reproduction through V2 scoring code,
  - generated full-taxonomy detector smoke checkpoint and ONNX artifact,
  - full YOLOv8m 136-class detector checkpoint and ONNX artifact,
  - public AWS deployment path,
  - upload-to-artifact product flow,
  - graph-positive F1 metric policy.
