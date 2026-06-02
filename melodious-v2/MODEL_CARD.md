# Model Card - Melodious V2

## Overview

Melodious V2 is an optical music recognition system for scanned or photographed Western staff notation. It is designed to detect symbols, assemble musical relationships, and export MusicXML/MIDI artifacts through a deployed API.

## Intended Use

- Musicians, students, and researchers converting printed scores into editable digital formats.
- Course demo and grading evaluation of an applied ML system with a real service surface.
- Not intended as a fully autonomous archival transcription system without human review.

## Current Implementation Status

- The API and UI can process sample payloads and uploaded images through a clearly labeled bootstrap detector path.
- M2 has reproduced a reduced-class legacy detector sample through the V2 metric pipeline with generated run provenance.
- The production detector target is a full DeepScores 136-class model.
- M3 produced a constrained full 136-class detector smoke run with checkpoint and ONNX artifacts under `artifacts/models/detection_136class_yolov8s_smoke_v1/`.
- The full configured YOLOv8m, 150-epoch detector completed in this V2 workspace under `runs/detection/detection_136class_yolov8m_v1/`. It was finalized from the selected `best.pt` checkpoint, exported to ONNX, and copied to `artifacts/models/detection_136class_yolov8m_v1/`.
- The current full detector validation metrics are recorded in `runs/detection/detection_136class_yolov8m_v1/metrics.json`.
- Primary detector metric: `mAP@0.5:0.95 = 0.4747370751116288`.
- Secondary detector metrics: `mAP@0.5 = 0.5853211368313491`, `precision@0.5 = 0.8274236461250144`, and `recall@0.5 = 0.4909790740632496`.
- Secondary detector F1: `F1@0.5 = 0.6162725385980492`.
- The best current primary validation inference configuration for the same checkpoint is `runs/detection/detection_136class_yolov8m_eval_img1472_maxdet2000_v1/metrics.json`.
- Best current validation detector metric: `mAP@0.5:0.95 = 0.6204968163150985`.
- Best current validation secondary detector `mAP@0.5 = 0.7833788545364062`.
- Best current validation precision and recall at IoU 0.5: `precision@0.5 = 0.8166240104606699`, `recall@0.5 = 0.7367130723503518`.
- Best current validation detector `F1@0.5 = 0.7746130448554269`.
- The best current secondary `mAP@0.5` validation configuration is `runs/detection/detection_136class_yolov8m_eval_img1536_maxdet2000_v1/metrics.json`, with `mAP@0.5 = 0.7920129156176505`.
- The M7 class coverage audit is recorded under `runs/detection/detection_136class_class_coverage_audit_v1/`; it shows that the model head preserves the 136-class taxonomy, but local labels contain support for 115 classes across train/validation/test and validation measures 103 classes.
- The completed M7 fine-tune `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1` is recorded in `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/metrics.json`.
- Completed fine-tune AP metrics: `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271`.
- Completed fine-tune threshold metrics: `precision@0.5 = 0.8457099520968777`, `recall@0.5 = 0.7738772781467206`, and `F1@0.5 = 0.8082006373091581`.
- A follow-up background fine-tune, `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`, was launched from the completed fine-tune `best.pt` at image size 1536 with `max_det=2000`; it has no final `metrics.json` until the runner completes.
- Graph assembly now has a real legacy GNN runtime path. With `MELODIOUS_GNN_CHECKPOINT=..\outputs\gnn_checkpoint.pt`, the API sample path can report `applied_mode = "gnn"` only after checkpoint inference runs.
- The current graph evaluation run is `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.
- Primary graph metric: `positive_macro_f1 = 0.7590456327823909`.
- Separate graph `no_relation` F1: `0.9425171440096813`.
- Positive relationship F1 values: `stem_notehead = 0.6960721184803607`, `beam_notegroup = 0.8220191470844213`.
- The current end-to-end export run is `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.
- M5 measured `musicxml_validity_rate = 1.0`, `midi_generation_success_rate = 1.0`, and `page_success_rate = 1.0` on 14 MUSCIMA holdout XML-derived payload fixtures.
- M6 prepared the public demo deployment path with Dockerized FastAPI, ECS/Fargate guidance, S3/CloudFront frontend guidance, environment-driven CORS, and local/public smoke tooling.
- The public AWS demo has not been deployed from this workspace because AWS CLI and account-local AWS resource values are unavailable locally.

## Metrics Policy

- Detector primary: `mAP@0.5:0.95`.
- Detector secondary: `mAP@0.5`, precision, recall, `F1@IoU=0.5`, per-class AP/F1.
- Graph primary: positive-class macro F1 on natural edge distribution.
- End-to-end: measured relationship/export quality on fixed holdout pages.
- Estimates are labeled as estimates and are never presented as measured results.

## Limitations

- Western staff notation remains the core target distribution.
- Handwritten notation, non-Western notation, tablature, and experimental notation require separate datasets and evaluation.
- Small symbols such as dots, stems, flags, and accidentals need high-resolution or tiled inference.
- MusicXML export can be structurally valid while musically incomplete if relationship assembly is weak.
- Bootstrap detector results are for system integration only and must not be reported as trained model performance.
- The M2 reduced-class sample is a metric-pipeline reproduction run and should not be treated as a final full-taxonomy detector result.
- The M3 YOLOv8s smoke artifact proves the full-taxonomy training/evaluation/export path, but it is superseded by the full YOLOv8m detector for detector-quality claims.
- The full YOLOv8m detector is a validation-split artifact. Test-set detector performance has not been reported yet and should be produced only once the team freezes the model family.
- The `detection_136class_yolov8m_eval_img1472_maxdet2000_v1` and `detection_136class_yolov8m_eval_img1536_maxdet2000_v1` results are validation-time inference tuning on the existing checkpoint. They are not newly trained models and must not be reported as test performance.
- The full YOLOv8m analysis shows 103 supported validation classes, 16 supported classes with zero mAP, and small-symbol mean `mAP@0.5:0.95 = 0.3194606161321027`. Problem classes include `ledgerLine`, `stem`, `ottavaBracket`, several articulation classes, and fingering classes. See `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- The completed fine-tune improved the headline validation metrics and reduced supported zero-mAP classes to 5, but `stem` remains `0.0` mAP and `ledgerLine` is only `0.0035627224962602928`. Rhythm extraction on uploaded sheet demos therefore remains limited by missing stem detections.
- The local note-extraction demo disables CV augmentation-dot guessing for YOLO-backed runs by default. This reduces false dotted notes but does not solve detector-confirmed false `augmentationDot` predictions or missing stem detections.
- The local DeepScores labels do not cover all 136 taxonomy classes: 21 classes have zero labels across train/validation/test. Another fine-tune on the same labels cannot teach those classes; future full-taxonomy improvement needs added labels, external data, synthetic-but-verified examples, or a narrower supported-class claim.
- Current validation metrics are blind to 33 taxonomy classes because those classes have zero validation support. Validation-selected settings must not be presented as proof that every class works.
- API inference still uses the bootstrap detector path until a selected ONNX artifact is intentionally wired into a non-bootstrap detector adapter.
- The current GNN is a legacy 15-class relationship model. It does not cover every V2 detector class and has zero validation support for `slur_phrase` and `tie_sustained` in the current graph evaluation.
- The legacy GNN checkpoint did not save the separate node feature encoder used to build training tensors. V2 reconstructs that encoder from seed `42`; this is documented in `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json` and should be replaced by a self-contained graph artifact in a future retrain.
- The M5 end-to-end result measures export validity from ground-truth XML-derived payload fixtures. It does not prove trained detector uploaded-image transcription quality.
- Public demo smoke has local evidence only until an AWS-enabled environment runs the ECR/ECS/S3/CloudFront steps in `infra/aws/README.md`.
- The API stores transcription jobs in memory. Artifact URLs are suitable for a single-task short demo but not durable multi-task production storage.

## Bias and Fairness

The main data sources overrepresent Western classical and contemporary notation. V2 documents this as a cultural/domain bias and does not claim coverage for makam, Carnatic, jianpu, Byzantine, tablature, or graphic score systems.

## Privacy

The target deployment stores uploaded images only long enough to produce artifacts. Private S3 buckets and short-lived presigned URLs are used for cloud artifacts. No raw image should be committed to the repository.

## Deployment Notes

- API CORS origins are controlled by `MELODIOUS_CORS_ORIGINS`; include the CloudFront frontend origin for public browser demos.
- Graph assembly can use `MELODIOUS_GNN_CHECKPOINT` only if the private checkpoint is mounted or copied into the container at that path.
- Public smoke should run `scripts/smoke_public_demo.py --api-base-url ...` and verify `/health`, `/version`, sample transcription, MusicXML download, and MIDI download.
- The current public-demo path is deployment-prepared but blocked on AWS CLI/account values, not on model training.

## Robustness

Robustness must be evaluated under noise, JPEG compression, rotation/skew with label-preserving transforms, blur, and photographed-page lighting. Rotation metrics must rotate labels with images; otherwise the result is a measurement artifact.
