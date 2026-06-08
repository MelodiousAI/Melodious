# Final Technical Report

## Classification

Melodious is an Option A application-oriented ML system and a graph-based
project. It transcribes printed sheet-music images into structured symbolic
outputs, primarily MusicXML and MIDI, for musicians, educators, arrangers, and
software tools that need editable score artifacts rather than only page images.

The graph component is central: independent detector boxes are converted into a
notation graph, and a relationship model predicts semantic edges needed for
assembly and export.

## Problem and Success Criteria

The practical problem is optical music recognition for printed scores. The
decision supported by the system is: given a score image, identify notation
objects, infer their musical relationships, and return editable/listenable score
artifacts.

Success criteria used in the project:

- Symbol detection quality on DeepScores 136-class validation and test splits.
- Relationship prediction quality on MUSCIMA graph validation pages.
- MusicXML/MIDI artifact generation on MUSCIMA holdout payload fixtures.
- Reproducible API, Docker, frontend, and smoke-test flow.
- Clear documentation of limitations, class coverage, and responsible-ML risks.

## Why Machine Learning Is Needed

Simple visual baselines were measured and preserved as evidence:

| Method | Evidence | IoU threshold | F1 |
|---|---|---:|---:|
| Template matching | `../outputs/baseline_template_results.json` | 0.50 | 0.1647 |
| HOG + SVM | `../outputs/baseline_hog_results.json` | 0.50 | 0.0026 |

These results show that hand-built appearance matching is too brittle for the
symbol-recognition part of the application. The final system therefore uses a
trained detector for symbol localization and a graph relationship model for
notation structure.

## Data and Task Formulation

| Component | Dataset/source | Task |
|---|---|---|
| Detector | DeepScores 136-class materialized YOLO data | Multi-class object detection for notation symbols. |
| Graph model | MUSCIMA graph manifest | Edge classification over candidate notation-object relationships. |
| End-to-end export | MUSCIMA XML-derived payload fixtures | Validate graph/export integration and generated MusicXML/MIDI artifacts. |
| Product demo | Uploaded or sample score images | API and frontend flow from image/sample to artifacts. |

The documentation and manifests separate training, validation, test, and holdout
fixture evidence. The final detector test run evaluates the frozen selected
checkpoint.

## Architecture

The v2 system is separated into data/model/serving layers:

- `src/melodious_v2/`: API, contracts, detector runtime, graph logic, export
  logic, deployment smoke helpers, and report utilities.
- `scripts/`: reproducible experiment and evaluation entrypoints.
- `configs/`: detector, graph, and evaluation configuration files.
- `tests/`: unit and integration checks for contracts, API routes, graph/export,
  and smoke behavior.
- `frontend/`: Vite/React product UI for upload/sample transcription flow.
- `infra/docker/` and `docker-compose.yml`: Dockerized API path.
- `infra/aws/`: ECS/Fargate and frontend deployment runbook/templates.
- `runs/` and `artifacts/`: measured evidence and deployable model artifacts.

## Main Results

| Area | Evidence | Split | Primary metric | Value |
|---|---|---|---|---:|
| Detector, selected model | `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/metrics.json` | validation | mAP@0.5:0.95 | 0.707986237382828 |
| Detector, final frozen model | `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final/metrics.json` | test | mAP@0.5:0.95 | 0.7070089366721093 |
| Graph relationship model | `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json` | validation | positive_macro_f1 | 0.7590456327823909 |
| Non-graph relationship baseline | `runs/graph/graph_non_graph_heuristic_muscima_val_v1/metrics.json` | validation | positive_macro_f1 | 0.621796846824738 |
| End-to-end export fixture | `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json` | holdout | musicxml_validity_rate | 1.0 |

Important secondary detector evidence:

- Final test mAP@0.5: 0.852207159642617.
- Final test precision@0.5: 0.88660192437495.
- Final test recall@0.5: 0.7956273543690356.
- Final test F1@0.5: 0.8386546975280545.

End-to-end fixture evidence:

- 14 holdout MUSCIMA payload fixture pages.
- MusicXML validity rate: 1.0.
- MIDI generation success rate: 1.0.
- Page success rate: 1.0.

## Graph Justification

Flat symbol detection is not enough for OMR because musical meaning depends on
relations between symbols: stems attach to noteheads, beams group notes, ties and
slurs connect note events, and accidentals or key signatures affect nearby
pitches. A graph is a natural representation because nodes are symbols and edges
are candidate musical relationships.

The graph comparison is fair for the rubric because both the GNN and the
non-graph rule baseline evaluate the same 14 pages, same candidate-edge builder,
same 48,174 candidate edges, and same 6,340 positive edges. The non-graph method
uses local class-pair and bounding-box rules. The GNN uses learned relationship
classification over graph features.

Detailed evidence is in `docs/BASELINES_AND_GRAPH_COMPARISONS.md`.

## Error Analysis and Limitations

Detector:

- Stronger classes include many clefs, rests, accidentals, noteheads, beams,
  ties, and dynamics.
- Known weak classes include `stem`, `ledgerLine`, several articulations,
  tuplets, rare tremolos, and rare small variants.
- The final test run reports `stem` per-class mAP@0.5:0.95 as 0.0 and
  `ledgerLine` as 0.018274217207904963, so line-like classes remain a major
  limitation.

Graph:

- The graph validation split has support for `stem_notehead` and
  `beam_notegroup`; it has zero support for `slur_phrase` and `tie_sustained` in
  the measured split.
- The legacy GNN is evaluated through v2 code, but the checkpoint itself remains
  a legacy 15-class relationship model.

End-to-end:

- The holdout export run uses MUSCIMA XML-derived detector payload fixtures. It
  validates graph/export integration and artifact creation, but it is not a
  measured full uploaded-image detector/export benchmark.
- Product upload uses the trained local extraction path, but arbitrary real
  scans still need more measured deployment testing.

## Responsible ML

The final submission addresses all four responsible-ML categories:

| Topic | Evidence |
|---|---|
| Explainability | Confidence outputs, class-coverage audit, graph relationship labels, model card, frontend/API explanation panels. |
| Fairness/bias | Per-class metrics, class-coverage audit, data-card discussion of symbol imbalance and notation-style limits. |
| Privacy/leakage | Split-specific manifests, no permanent upload-storage assumption, deployment/privacy caveats. |
| Robustness | Historical noise/compression stress tests, documented rotation caveat, holdout fixture export run, model-card limits. |

Detailed evidence is in `docs/RESPONSIBLE_ML.md`.

## Deployment and Engineering

The submission includes:

- Dockerized FastAPI API in `infra/docker/Dockerfile.api`.
- `docker-compose.yml` for local API startup.
- Vite/React frontend in `frontend/`.
- Product API routes for config, samples, upload transcription, exports, and
  smoke testing.
- AWS ECS/Fargate and S3/CloudFront runbook in `infra/aws/README.md`.
- Local smoke evidence in `runs/deploy/m6_local_smoke/smoke.json` and
  `runs/deploy/m6_local_smoke_20260606/smoke.json`.

The current workspace has local verification evidence. Public AWS smoke remains
environment-dependent because account-local AWS values and CLI access are not
available in this workspace.

## Presentation Points

For a strict professor, lead with these points:

1. The project is Option A and graph-based, not a research-only Option B claim.
2. Non-AI detection baselines exist and are measured.
3. The graph-vs-non-graph comparison uses the same candidate edges and pages.
4. The best detector was evaluated on a final held-out test split.
5. The system is not only a notebook: it has API, Docker, frontend, deployment
   runbook, smoke tooling, tests, and exported artifacts.
6. Limitations are explicit: line-like classes, rare symbols, fixture-based
   end-to-end export evidence, and deployment shift.

## Final Evidence Index

| Rubric area | Best file to show first |
|---|---|
| Problem and fit | `README.md`, `MODEL_CARD.md`, this report |
| Non-AI baseline | `docs/BASELINES_AND_GRAPH_COMPARISONS.md` |
| Graph core and non-graph comparison | `docs/BASELINES_AND_GRAPH_COMPARISONS.md` |
| Splits and metrics | `docs/METRICS.md`, `docs/EXPERIMENTS.md`, selected `runs/**/metrics.json` |
| Error analysis | `MODEL_CARD.md`, detector `analysis.md`, class coverage audit |
| Responsible ML | `docs/RESPONSIBLE_ML.md` |
| Deployment | `README.md`, `infra/docker/Dockerfile.api`, `infra/aws/README.md` |
| UI/demo | `frontend/`, `docs/NOTE_EXTRACTION_DEMO.md`, demo run folders |
| Presentation | `docs/PRESENTATION_TECHNICAL_REVIEW.tex`, root `presentation_script.md` |
