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
- Graph assembly supports explicit heuristic fallback metadata until a real GNN checkpoint is wired.

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
- The full YOLOv8m analysis shows 103 supported validation classes, 16 supported classes with zero mAP, and small-symbol mean `mAP@0.5:0.95 = 0.3194606161321027`. Problem classes include `ledgerLine`, `stem`, `ottavaBracket`, several articulation classes, and fingering classes. See `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- API inference still uses the bootstrap detector path until a selected ONNX artifact is intentionally wired into a non-bootstrap detector adapter.

## Bias and Fairness

The main data sources overrepresent Western classical and contemporary notation. V2 documents this as a cultural/domain bias and does not claim coverage for makam, Carnatic, jianpu, Byzantine, tablature, or graphic score systems.

## Privacy

The target deployment stores uploaded images only long enough to produce artifacts. Private S3 buckets and short-lived presigned URLs are used for cloud artifacts. No raw image should be committed to the repository.

## Robustness

Robustness must be evaluated under noise, JPEG compression, rotation/skew with label-preserving transforms, blur, and photographed-page lighting. Rotation metrics must rotate labels with images; otherwise the result is a measurement artifact.
