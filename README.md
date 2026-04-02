# Melodious
Melodious is an optical music recognition (OMR) project built around MUSCIMA++.
This repo currently focuses on the data-preparation, graph-construction, and evaluation side of the pipeline:
- parsing MUSCIMA++ annotations
- detecting staff regions in score images
- building reference graphs from MUSCIMA ground truth
- building PyTorch Geometric graphs from detections
- aligning detections back to MUSCIMA ground truth
- validating MUSCIMA reference payload integration
## What Is Implemented
The main implemented modules are:
- src/parse_muscima.py
  Parses MUSCIMA++ XML annotations into JSON-friendly node and edge files.
- src/class_mapping.py
  Builds and saves a stable class-name <-> class-id mapping for parsed MUSCIMA nodes.
- src/staff_detection.py
  Detects staff regions from grayscale score images and can save debug overlays.
- src/muscima_graph_builder.py
  Builds document-level reference graph JSON files from MUSCIMA data.
- src/pyg_graph_builder.py
  Builds GNN-ready PyTorch Geometric graphs from detection dictionaries.
- src/detection_alignment.py
  Aligns detections to MUSCIMA ground-truth nodes using greedy IoU matching.
- src/muscima_reference_evaluation.py
  Runs graph building plus alignment on the shared MUSCIMA reference payloads.
- 	ools/export_muscima_detections.py
  Exports MUSCIMA XML annotations into the shared detector payload contract.
## Repo Structure
- src/
  Core source code for parsing, staff detection, graph building, and alignment.
- 	ools/
  Small helper scripts that are useful for data/export workflows but are not part of the main runtime pipeline.
- 	ests/
  Unit tests for the main graph, alignment, and mapping modules.
- data/raw/
  Raw MUSCIMA++ annotations and page images.
- data/processed/
  Processed outputs such as parsed JSON, class mappings, and reference graph files.
- sample_detections/
  Shared detector payload examples, MUSCIMA reference payloads, and the small XML subset used for payload export tests.
- outputs/
  Generated debug images and summary files for inspection.
## End-to-End Pipeline
The project currently has two related graph paths.
### 1. Reference-data path
This path works from MUSCIMA ground truth and produces the dataset-side reference graphs.
1. Run src/parse_muscima.py
   Creates:
   - data/processed/muscima_nodes.json
   - data/processed/muscima_edges.json
2. Run src/class_mapping.py
   Creates:
   - data/processed/class_mapping.json
3. Run src/muscima_graph_builder.py
   Creates:
   - per-document graph JSON files under data/processed/graphs/
   - data/processed/graphs/summary.csv
   - data/processed/graphs/batch_stats.json
### 2. Detection/model path
This path works from detector outputs and produces model-ready graphs.
1. Run or receive symbol detections from a detector.
2. Use src/staff_detection.py to detect staff regions for the same page image.
3. Use src/pyg_graph_builder.py to build a PyTorch Geometric Data graph from the detections.
4. Use src/detection_alignment.py to compare detections against MUSCIMA ground truth.
5. Use src/muscima_reference_evaluation.py to validate the integrated MUSCIMA reference payload path end to end.
## Why There Are Two Graph Builders
The two graph builders are separate on purpose:
- src/muscima_graph_builder.py
  builds reference graphs from MUSCIMA ground-truth annotations.
- src/pyg_graph_builder.py
  builds GNN-ready graphs from detections.
They are related, but they serve different stages of the project.
## Main Commands
### Parsing and mapping
`powershell
.\.venv\Scripts\python.exe src\parse_muscima.py
.\.venv\Scripts\python.exe src\class_mapping.py
`
### Staff detection
One image:
`powershell
.\.venv\Scripts\python.exe src\staff_detection.py --image data\raw\Images\PNG_GT_Gray\w-14\p001.png
`
One image with saved debug output:
`powershell
.\.venv\Scripts\python.exe src\staff_detection.py --image data\raw\Images\PNG_GT_Gray\w-14\p001.png --output-dir outputs\staff_detection\single_test
`
One writer folder:
`powershell
.\.venv\Scripts\python.exe src\staff_detection.py --writer w-14 --output-dir outputs\staff_detection\w14_cli
`
### Reference graph building
Full dataset:
`powershell
.\.venv\Scripts\python.exe src\muscima_graph_builder.py
`
Small batch:
`powershell
.\.venv\Scripts\python.exe src\muscima_graph_builder.py --limit 5
`
One document:
`powershell
.\.venv\Scripts\python.exe src\muscima_graph_builder.py --document CVC-MUSCIMA_W-01_N-10_D-ideal
`
### PyG graph building
Demo run:
`powershell
.\.venv\Scripts\python.exe src\pyg_graph_builder.py
`
### Alignment
`powershell
.\.venv\Scripts\python.exe src\detection_alignment.py --document CVC-MUSCIMA_W-01_N-10_D-ideal --detections-json data\processed\sample_alignment_detections.json --iou-threshold 0.5
`
### MUSCIMA reference evaluation
`powershell
.\.venv\Scripts\python.exe src\muscima_reference_evaluation.py
`
### MUSCIMA payload export helper
`powershell
.\.venv\Scripts\python.exe tools\export_muscima_detections.py
`
## Tests
`powershell
.\.venv\Scripts\python.exe -m unittest tests\test_class_mapping.py
.\.venv\Scripts\python.exe -m unittest tests\test_pyg_graph_builder.py
.\.venv\Scripts\python.exe -m unittest tests\test_detection_alignment.py
.\.venv\Scripts\python.exe -m unittest tests\test_muscima_graph_builder.py
.\.venv\Scripts\python.exe -m unittest discover tests
`
## Current State
At the current checkpoint, the repo already has:
- parsed MUSCIMA node and edge exports
- a stable class mapping
- a stable staff detector
- full reference MUSCIMA graph generation
- a detection-to-PyG graph builder
- a detection-to-ground-truth alignment layer
- MUSCIMA reference payload integration checks
- automated tests for the main graph, alignment, and mapping modules
## Notes
- data/raw/, data/processed/, and outputs/ are data/output folders, not hand-written source code.
- sample_detections/ contains both DeepScores-style detector samples and MUSCIMA-specific reference payloads.
- 	ools/ is for helper scripts that support the workflow but are not the core runtime modules.
- The project is intentionally kept simple: separate source code from outputs, keep modules focused, and add small testable steps.
