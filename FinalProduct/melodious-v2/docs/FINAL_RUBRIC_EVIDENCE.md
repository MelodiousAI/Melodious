# Final Rubric Evidence

This is the short checklist to use when reviewing the final package against the
strict grading rubric.

| Code | Status | Evidence |
|---|---|---|
| PF1 | Ready | `README.md`, `docs/FINAL_TECHNICAL_REPORT.md` define printed-score transcription to MusicXML/MIDI. |
| PF2A | Ready | `README.md`, `MODEL_CARD.md`, and product docs identify musicians, educators, arrangers, and deployers. |
| PF3A | Ready | `docs/BASELINES_AND_GRAPH_COMPARISONS.md` includes template-matching and HOG/SVM baselines. |
| PF4 | Ready | `docs/FINAL_TECHNICAL_REPORT.md` explains editable/listenable score artifacts. |
| PF5 | Ready | `docs/FINAL_TECHNICAL_REPORT.md` states Option A, application-oriented, graph-based classification. |
| TM1 | Ready | `docs/DATA_CARD.md`, `docs/METRICS.md`, and run manifests define detector, graph, and export tasks. |
| TM2A | Ready | `../outputs/baseline_template_results.json`, `../outputs/baseline_hog_results.json`, and `docs/BASELINES_AND_GRAPH_COMPARISONS.md`. |
| TM3 | Ready | YOLO detector, graph relationship model, export code, API, and frontend are documented in `docs/ARCHITECTURE.md`. |
| TM4 | Ready | `docs/DATA_CARD.md`, dataset manifests, conversion scripts, and split-specific run provenance. |
| TM5 | Ready | `docs/METRICS.md`, `docs/EXPERIMENTS.md`, validation/test detector runs, graph validation run, and holdout export run. |
| TM6 | Ready | Detector analysis files, class coverage audit, `MODEL_CARD.md`, and `docs/FINAL_TECHNICAL_REPORT.md`. |
| TM7 | Ready | `MODEL_CARD.md`, `docs/RESPONSIBLE_ML.md`, and final report limitations. |
| TM9G | Ready | Graph nodes, edges, edge labels, and relationship prediction are described in `docs/BASELINES_AND_GRAPH_COMPARISONS.md`. |
| TM10G | Ready | `graph_legacy_gnn_muscima_val_v1` and `graph_non_graph_heuristic_muscima_val_v1` compare graph and non-graph methods on the same candidate edges. |
| RM1 | Ready | Confidence outputs, relationship labels, class coverage, and explanation panels; see `docs/RESPONSIBLE_ML.md`. |
| RM2 | Ready | Symbol-class imbalance and weak-class analysis; see `docs/RESPONSIBLE_ML.md`. |
| RM3 | Ready | Split provenance, upload-storage caveats, and leakage controls; see `docs/RESPONSIBLE_ML.md`. |
| RM4 | Ready | Robustness outputs and shift limitations; see `docs/RESPONSIBLE_ML.md`. |
| EN1 | Ready | `infra/docker/Dockerfile.api` and `docker-compose.yml`. |
| EN2 | Ready | `src/melodious_v2/`, `scripts/`, `configs/`, `frontend/`, and `infra/` separate data, model, and serving responsibilities. |
| EN3 | Ready | `README.md`, `requirements.txt`, `pyproject.toml`, scripts, and selected run configs. |
| EN4 | Ready | `frontend/` and product API routes. |
| EN5 | Mostly ready | Local smoke evidence exists; public cloud smoke depends on AWS account values. |
| GD1 | Ready | v2 repo layout is clean and documented. |
| GD2 | Ready | `README.md`. |
| GD3 | Ready | `docs/ARCHITECTURE.md`, `docs/DATA_CARD.md`, `docs/METRICS.md`. |
| GD4 | Ready | `docs/EXPERIMENTS.md`, selected run reports, baselines, and graph comparison docs. |
| GD5 | Ready | `docs/DATA_CARD.md`, `MODEL_CARD.md`, `docs/RESPONSIBLE_ML.md`. |
| PR1 | Ready | Final report and presentation technical review. |
| PR2 | Ready | Architecture, graph comparison, and technical review. |
| PR3 | Ready | Detector test metrics, graph comparison, e2e fixture exports, and demo outputs. |
| PR4 | Needs presenter prep | Be ready to explain why graph edges are central and why the non-graph comparison is fair. |
| CI1 | Ready | Full OMR pipeline with detector, graph relationship model, export, UI, and deployment path. |
| CI2 | Ready | Trade-offs documented in architecture/model card/final report. |
| CI3 | Ready | Test-set detector run, same-edge graph baseline, responsible-ML coverage, smoke tooling. |
| CI4 | Ready | Frontend, AWS runbook, ONNX artifacts, export artifacts, and demo outputs. |

## Remaining Grade Risks

| Risk | Severity | How to handle |
|---|---|---|
| Public AWS endpoint may not be live during grading. | Medium | Show Docker/local smoke evidence and AWS runbook. If time permits, deploy and record a public smoke result. |
| End-to-end export metric uses MUSCIMA XML-derived payload fixtures, not arbitrary uploaded images. | Medium | Say this directly. Do not claim full real-scan accuracy from the fixture run. |
| Line-like detector classes remain weak. | Medium | Acknowledge `stem` and `ledgerLine` as known limitations and show the tiled stem pilot as mitigation work. |
| Graph checkpoint is legacy 15-class while detector is 136-class. | Low to medium | Explain that the graph evidence evaluates relationships on MUSCIMA graph pages and that the detector evidence is separate. |
| Presentation Q&A could focus on graph validity. | Medium | Emphasize same candidate edges, same pages, same labels, and relationship prediction as the graph core. |

## Last-Minute Actions for Maximum Score

1. Run a local Docker smoke right before submission if Docker is available.
2. If AWS credentials are available, deploy once and save the public smoke result
   under `runs/deploy/`.
3. In the presentation, show the graph-vs-non-graph table before showing extra
   UI features.
4. Keep claims metric-specific: detector mAP for detector runs, relationship F1
   for graph runs, and validity/success rates for export runs.
