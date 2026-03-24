# Melodious

Melodious is an optical music recognition (OMR) system that detects musical symbols in sheet music and assembles them into structured data using deep learning.

The project combines two main components:
1. **Detection** — A custom YOLO detector (trained from scratch) and a YOLOv8 fine-tuning pipeline for locating music notation symbols in page images.
2. **Graph Construction** — Staff detection, MUSCIMA++ parsing, and a GNN-based assembler that links detected symbols into musical structures.

## Repository Structure

```
melodious/              # Core detection package
  model.py              # Custom YOLO detector (12.9M params, 3-scale heads)
  train.py              # Training loop, loss functions, metrics
  dataset.py            # DeepScores v2 data loader (15 target classes)
  inference.py          # Model loading and single-image inference
  gnn.py                # GNN assembler (3-layer GAT, PyTorch Geometric)
  pipeline.py           # End-to-end detection pipeline
  export.py             # Checkpoint and ONNX export utilities
  detection_contract.py # Stable JSON contract for graph integration
  convert_dataset.py    # DeepScores -> YOLO format converter
  yolov8_detect.py      # YOLOv8 fine-tuning wrapper (Ultralytics)
  generate_detections.py        # Export detector outputs as JSON
  export_reference_detections.py # Export ground-truth as reference JSON
  baselines/            # Baseline comparison methods
    template_matching.py  # OpenCV template matching
    hog_svm.py            # HOG + linear SVM
    heuristic_assembler.py # Rule-based symbol grouping
src/                    # Graph construction modules
  parse_muscima.py      # MUSCIMA++ XML parser and JSON export
  staff_detection.py    # Staff line detection (OpenCV + scipy)
  graph_builder.py      # Compatibility wrapper for graph construction
sample_detections/      # Detection contract and sample outputs
  FORMAT.md             # JSON schema documentation
  class_mapping.json    # Class ID -> name mapping (15 classes)
  reference/            # Ground-truth reference payloads
main.py                 # CLI training entrypoint
Claude.md               # Agent workspace rules
```

## Target Classes (15)

| ID | Class | ID | Class |
|----|-------|----|-------|
| 0 | notehead-full | 8 | rest-half |
| 1 | notehead-half | 9 | rest-whole |
| 2 | notehead-whole | 10 | accidentalSharp |
| 3 | clefG | 11 | accidentalFlat |
| 4 | clefF | 12 | accidentalNatural |
| 5 | clefC | 13 | beam |
| 6 | rest-8th | 14 | stem |
| 7 | rest-quarter | | |

## Quick Start

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Train Custom YOLO

```bash
python main.py --epochs 50 --batch-size 4 --img-size 640 --lr 0.001
```

### Train YOLOv8

```bash
# Convert dataset to YOLO format first
python -m melodious.convert_dataset --dataset-root dataset_ds2_dense --output-root yolo_dataset

# Fine-tune YOLOv8
python -m melodious.yolov8_detect train --data yolo_dataset/data.yaml --epochs 50
```

### Export Detection Payloads

```bash
# From trained custom model
python -m melodious.generate_detections --model-type custom --checkpoint outputs/best.pth --image-dir dataset_ds2_dense/images --limit 5

# From ground-truth labels (for integration testing)
python -m melodious.export_reference_detections --limit 5
```

### Run Staff Detection

```bash
python tests/test_graph_builder.py
```

## Detection Contract

The detector outputs JSON files in a stable format that the graph/GNN side consumes. See [sample_detections/FORMAT.md](sample_detections/FORMAT.md) for the full schema.

Key fields per detection:
- `class_id` / `class_name` — symbol identity
- `confidence` — detector score
- `bbox` — normalised center-based box (`x_center`, `y_center`, `width`, `height`)
- `bbox_pixels` — pixel box for debugging (`x1`, `y1`, `x2`, `y2`)

## Dataset

- **DeepScores v2 Dense** — 1362 train / 352 test score images with COCO-format annotations, filtered to 15 target classes.
- **MUSCIMA++** — XML annotations and grayscale page images for staff detection and graph construction.

## Status

- Custom YOLO detector: implemented and training
- YOLOv8 pipeline: conversion and training wrappers ready
- GNN assembler: architecture implemented, awaiting trained detector outputs
- Staff detection: implemented and tested
- MUSCIMA++ parser: implemented and tested
- Detection contract: frozen and shared with graph side
