# Project Context

## Project
Melodious is an optical music recognition (OMR) project.
The system takes a photo of sheet music, detects music symbols, builds graph representations of the notation, and later exports structured outputs such as MusicXML and MIDI.

## Team Split
My partner is mainly handling the YOLO / detection side.
I am mainly handling the data-preparation and graph side.

## My Responsibilities
1. Parse the MUSCIMA++ dataset
2. Extract music symbols as nodes
3. Extract symbol relationships as edges
4. Detect staff regions from score images
5. Build graph objects for GNN input
6. Align YOLO detections to MUSCIMA++ ground truth

## Current State
The following parts are already implemented:
- `src/parse_muscima.py`
- `src/class_mapping.py`
- `src/staff_detection.py`
- `src/muscima_graph_builder.py`
- `src/pyg_graph_builder.py`
- `src/detection_alignment.py`

## Dataset
We are using MUSCIMA++ v2.0.
Important raw-data locations include:
- annotation XML files under `data/raw/MUSCIMA-pp_raw-data-v2.0/`
- page images under `data/raw/Images/`

## Repo Rules
When suggesting or editing code:
- keep the structure simple
- avoid overengineering
- separate source code from generated outputs
- prefer small, testable steps
- explain changes clearly

## Repo Structure
- `src/` for source code
- `tests/` for actual test files
- `data/raw/` for raw dataset files
- `data/processed/` for processed JSON/graph outputs
- `outputs/` for generated debug images and summaries
