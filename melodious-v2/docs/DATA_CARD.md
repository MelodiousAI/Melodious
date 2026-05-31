# Data Card

## Datasets

### DeepScores V2 Dense

- Role: detector training and evaluation.
- Target V2 use: full 136-class detection.
- Existing V1 use: reduced 15-class detector.
- M1 manifest output: `runs/data/deepscores_136_manifest/`.
- Source JSONs:
  - `../dataset_ds2_dense/deepscores_train.json`
  - `../dataset_ds2_dense/deepscores_test.json`
- Split policy:
  - preserve the existing DeepScores test JSON as `test`,
  - split the existing DeepScores train JSON deterministically with seed `42`,
  - use 90% of source train pages for `train` and 10% for `val`.
- Generated M1 artifacts:
  - `manifest.json`
  - `train.json`
  - `val.json`
  - `test.json`
  - `class_counts.json`
  - `leakage_report.json`
  - `yolo_dataset.yaml`
  - generated YOLO labels under `generated/labels/{train,val,test}/`.
- M3 materialized YOLO dataset:
  - output: `runs/data/deepscores_136_yolo_materialized/`,
  - dataset YAML: `runs/data/deepscores_136_yolo_materialized/dataset.yaml`,
  - layout: `images/{train,val,test}` and `labels/{train,val,test}`,
  - purpose: Ultralytics training expects images and labels in sibling split folders,
  - initial link strategy: hardlink requested; filesystem did not permit it, so images were copied into ignored `runs/data/`,
  - generated counts: train 1226 images/labels, validation 136 images/labels, test 352 images/labels.
- Latest local M1 counts:
  - `train`: 1226 images, 793828 raw annotations, 793514 YOLO labels, 115 classes with support.
  - `val`: 136 images, 96005 raw annotations, 95941 YOLO labels, 103 classes with support.
  - `test`: 352 images, 244335 raw annotations, 244255 YOLO labels, 110 classes with support.
- Leakage result:
  - duplicate image ids: passed,
  - duplicate filenames: passed,
  - inferred work-group repeats: warning, 202 repeated groups.
- M2 reduced-class evaluation sample:
  - output: `runs/detection/detection_15class_repro_sample_v1/`,
  - source predictions: `../sample_detections/model_outputs_quick/`,
  - matched ground truth: DeepScores train/test JSON annotations for the same five page filenames,
  - taxonomy: `deepscores_15_reduced`,
  - purpose: metric-pipeline reproduction before full 136-class training, not new model training.
- M3 full-taxonomy smoke sample:
  - output: `runs/detection/detection_136class_yolov8s_smoke_v1/`,
  - model artifacts: `artifacts/models/detection_136class_yolov8s_smoke_v1/`,
  - source labels/images: M3 materialized DeepScores 136-class dataset,
  - taxonomy: `deepscores_136`,
  - purpose: prove full 136-class training/evaluation/export plumbing before launching the full configured YOLOv8m run,
  - limitation: this is a one-epoch YOLOv8s smoke run, not the final detector.
- M3 full YOLOv8m run:
  - output directory: `runs/detection/detection_136class_yolov8m_v1/`,
  - first manual recovery checkpoint: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/`,
  - later manual recovery checkpoints: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/` and `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/`,
  - source labels/images: M3 materialized DeepScores 136-class dataset,
  - taxonomy: `deepscores_136`,
  - configured run shape: YOLOv8m, 150 epochs, image size 1024, batch size 4, validation split only for model selection,
  - launch status: started on 2026-05-21 as a long-running local process,
  - first pause status: manually saved after epoch 20 completed and stopped during epoch 21,
  - resume status: resumed on 2026-05-21 from the epoch-20 manual checkpoint,
  - second pause status: manually saved after epoch 74 completed and stopped during epoch 75 on 2026-05-22,
  - resume status: resumed again from epoch 75 on 2026-05-22,
  - third pause status: manually saved after epoch 95 completed and stopped during epoch 96 on 2026-05-22,
  - load status: `last.pt` from the epoch-95 manual checkpoint loaded successfully with 136 classes,
  - final resume status: resumed from the latest run checkpoint after completed epoch 124 on 2026-05-28, then completed all 150 configured epochs,
  - selected checkpoint: `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`,
  - final V2 run artifacts: `metrics.json`, `report.md`, `manifest.json`, `artifacts.json`, `analysis.json`, `analysis.md`, `onnx_parity.json`, and copied `config.yaml`,
  - model artifacts: `artifacts/models/detection_136class_yolov8m_v1/best.pt`, `best.onnx`, and `metadata.json`,
  - validation primary metric from `metrics.json`: `mAP@0.5:0.95` 0.4747370751116288,
  - validation secondary metrics from `metrics.json`: `mAP@0.5` 0.5853211368313491, precision 0.8274236461250144, and recall 0.4909790740632496,
  - validation secondary F1 from `metrics.json`: `F1@0.5` 0.6162725385980492,
  - analysis summary: 103 supported validation classes, 16 supported validation classes with zero mAP, 35 supported small-symbol classes, and small-symbol mean `mAP@0.5:0.95` 0.3194606161321027,
  - ONNX parity status: `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json` passed on one fixed validation image; PyTorch and ONNX both returned 300 boxes with identical class-count totals.
- M7 validation inference-resolution improvement:
  - best evaluation run: `runs/detection/detection_136class_yolov8m_eval_img1248_v1/`,
  - source checkpoint: `artifacts/models/detection_136class_yolov8m_v1/best.pt`,
  - split: validation,
  - inference image size: 1248,
  - validation primary metric from `metrics.json`: `mAP@0.5:0.95` 0.5058429013539956,
  - validation secondary metric from `metrics.json`: `mAP@0.5` 0.6069618791829888,
  - caveat: this is validation-time inference tuning on the existing checkpoint, not a newly trained model and not test-set performance.

The inferred DeepScores work-group check is heuristic. For standard names such as
`lg-<work>-aug-<style>--page-<n>.png`, the group is inferred as `lg-<work>`.
Repeated inferred groups are treated as warnings, not automatic failures, because
the source train/test split is preserved and page/font augmentation identity is
not fully explicit in separate metadata.

### MUSCIMA++ / CVC-MUSCIMA

- Role: symbol relationship graphs, graph assembly training, and handwritten/cross-domain checks.
- Target V2 use: graph supervision and robustness evaluation.
- M1 manifest output: `runs/data/muscima_graph_manifest/`.
- Source XML directory: `../data/muscima-pp/v2.0/data/annotations`.
- Split policy:
  - use all XML page filenames found in the annotation directory,
  - split deterministically with seed `42`,
  - use 80% `train`, 10% `val`, and 10% `holdout`.
- Generated M1 artifacts:
  - `manifest.json`
  - `train.json`
  - `val.json`
  - `holdout.json`
  - `leakage_report.json`
  - `class_summary.json`
- Latest local M1 counts:
  - `train`: 112 pages, 82206 parsed nodes.
  - `val`: 14 pages, 10509 parsed nodes.
  - `holdout`: 14 pages, 10199 parsed nodes.
- Leakage result:
  - duplicate page ids across train/val/holdout: passed.
- M4 graph evaluation:
  - output: `runs/graph/graph_legacy_gnn_muscima_val_v1/`,
  - split: M1 `val`,
  - checkpoint: `..\outputs\gnn_checkpoint.pt`,
  - checkpoint SHA256: `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`,
  - metric distribution: natural candidate-edge distribution with no negative subsampling,
  - candidate edges: 48174,
  - positive candidate edges: 6340,
  - primary graph metric: positive-class macro F1 0.7590456327823909,
  - limitation: legacy 15-class graph contract and reconstructed seed-42 node feature encoder.
- M5 end-to-end export evaluation:
  - output: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/`,
  - split: M1 `holdout`,
  - payload source: MUSCIMA XML-derived detector payload fixtures,
  - pages: 14,
  - mapped detections: 6348,
  - note-like symbols: 2563,
  - relationship outputs: 10637,
  - primary export metric: MusicXML validity rate 1.0,
  - MIDI generation success rate: 1.0,
  - limitation: this is export-validity evidence from fixed XML-derived payloads, not trained uploaded-image detector quality.

## Taxonomies

- `deepscores_136`: detector taxonomy with all 136 DeepScores classes.
- `semantic_omr_v2`: assembly/export grouping used to map detector classes into musical roles.

The detector must preserve the full class id/name. Semantic grouping is an additional field and must not overwrite the detector class.

## Leakage Policy

- Splits are manifest-based and committed as small text/JSON files.
- Pages from the same score/work should not cross train/validation/test when metadata allows grouping.
- Threshold tuning uses validation only.
- Test data is used for final evaluation, not iterative debugging.

## Data Limits

- Western staff notation dominates.
- Handwritten and printed notation differ materially.
- Rare symbols are expected to have unstable per-class metrics.
- Some semantic relationships require symbols that were not included in the V1 reduced taxonomy.
