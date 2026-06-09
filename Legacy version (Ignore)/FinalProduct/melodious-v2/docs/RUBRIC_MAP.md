# Rubric Evidence Map

Project type: Track A, applied/deployment.  
Graph project: yes.

## Problem and Fit

- Specific problem: README project summary and API contract.
- User/deployer: README, MODEL_CARD, AWS deployment docs.
- Why ML: M2 reduced-class detector reproduction in `runs/detection/detection_15class_repro_sample_v1/metrics.json`; M3 full-taxonomy smoke detector in `runs/detection/detection_136class_yolov8s_smoke_v1/metrics.json`; full YOLOv8m detector metrics in `runs/detection/detection_136class_yolov8m_v1/metrics.json`; improved validation inference metrics in `runs/detection/detection_136class_yolov8m_eval_img1472_maxdet2000_v1/metrics.json` and `runs/detection/detection_136class_yolov8m_eval_img1536_maxdet2000_v1/metrics.json`; M4 graph relationship metrics in `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`; M5 end-to-end export metrics in `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.
- Success criteria: docs/METRICS.md, generated run reports, and `docs/EXPERIMENTS.md`.

## Technical Rigor and Responsible ML

- Task and data: docs/DATA_CARD.md.
- Non-AI baseline: historical measured detector baselines in
  `../outputs/baseline_template_results.json` and
  `../outputs/baseline_hog_results.json`, plus the final-package baseline bridge
  document `docs/BASELINES_AND_GRAPH_COMPARISONS.md`.
- Method substance: detector, graph assembly, export, and deployment modules.
- Preprocessing/leakage: dataset conversion tests and manifests.
- Splits/metrics/protocol: docs/METRICS.md, dataset manifests, and run manifests.
- Error analysis: model card plus generated detector analysis at `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.json` and `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- Class coverage evidence: `runs/detection/detection_136class_class_coverage_audit_v1/class_coverage.json` and `class_coverage.md`; the audit separates supported classes, validation blind spots, zero-label taxonomy classes, and high-support zero-map classes.
- Metric improvement evidence: `docs/METRIC_IMPROVEMENT.md`, `configs/detection_136class_eval_resolution_sweep.yaml`, `runs/detection/detection_136class_yolov8m_eval_img1472_maxdet2000_v1/metrics.json`, and `runs/detection/detection_136class_yolov8m_eval_img1536_maxdet2000_v1/metrics.json`.
- End-to-end evidence: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`, `report.md`, `manifest.json`, and exported artifacts.
- Limitations/tradeoffs: MODEL_CARD.md.
- Graph core object: assembly module, legacy GNN adapter, relationship metrics, graph tests, and `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.
- Graph vs non-graph: same-candidate-edge comparison between
  `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json` and
  `runs/graph/graph_non_graph_heuristic_muscima_val_v1/metrics.json`; summary
  and fairness notes are in `docs/BASELINES_AND_GRAPH_COMPARISONS.md`.
- Responsible ML: model card, robustness scripts, privacy/deployment notes, and
  `docs/RESPONSIBLE_ML.md`.

## Deployment and Engineering

- Dockerized API: infra/docker/Dockerfile.api.
- Separation of concerns: package layout under `src/melodious_v2/`.
- Reproducible run path: README and scripts.
- UI/demo: frontend upload/results flow.
- Running artifact path: ECS/Fargate deployment template, ECR build/push commands, S3/CloudFront frontend publish commands, and shutdown controls in `infra/aws/README.md`.
- Public-demo smoke contract: `scripts/smoke_public_demo.py`, `src/melodious_v2/deployment/smoke.py`, `infra/aws/smoke_test.ps1`, and `tests/test_deployment_smoke.py`.
- Deployment caveat: public AWS smoke is pending because AWS CLI and account-local AWS values are not available in this workspace. Local smoke evidence is generated under ignored `runs/deploy/m6_local_smoke/smoke.json`.

## GitHub and Documentation

- Structure: README layout.
- Setup/run: README commands.
- Architecture/method: docs/ARCHITECTURE.md and module docs.
- Results/logs/ablations: docs/EXPERIMENTS.md from `runs/**/metrics.json`; current runs include `detection_15class_repro_sample_v1`, `detection_136class_yolov8s_smoke_v1`, `detection_136class_yolov8m_v1`, `detection_136class_yolov8m_eval_img1472_maxdet2000_v1`, `detection_136class_yolov8m_eval_img1536_maxdet2000_v1`, `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`, `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final`, `graph_legacy_gnn_muscima_val_v1`, `graph_non_graph_heuristic_muscima_val_v1`, and `e2e_muscima_holdout_xml_fixture_v1`.
- Training checkpoint evidence: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/metadata.json`, `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/metadata.json`, and `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json` document manual recovery points. Final detector evidence is `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `runs/detection/detection_136class_yolov8m_v1/analysis.json`, `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`. Graph checkpoint evidence is `..\outputs\gnn_checkpoint.pt` with SHA256 `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`, evaluated by `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.
- Data/limits/ethics/deployment: DATA_CARD, MODEL_CARD, infra docs.
- Final reviewer-facing report: `docs/FINAL_TECHNICAL_REPORT.md` and
  `docs/FINAL_RUBRIC_EVIDENCE.md`.

## Presentation and Creativity

- Headline improvements:
  - full 136-class detector path,
  - strict metric provenance,
  - reduced-class metric reproduction through V2 scoring code,
  - generated full-taxonomy detector smoke checkpoint and ONNX artifact,
  - full YOLOv8m 136-class detector checkpoint and ONNX artifact,
  - improved full YOLOv8m validation inference configuration at image size 1248,
  - detector class-coverage audit that prevents unsupported-class metric claims,
  - real legacy GNN assembly runtime with natural-distribution graph metrics,
  - fixed holdout MusicXML/MIDI export evaluation with generated artifacts,
  - public AWS deployment path with smoke tooling and cost-control runbook,
  - upload-to-artifact product flow,
  - graph-positive F1 metric policy.
