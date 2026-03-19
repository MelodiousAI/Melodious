# Melodious

Melodious is an optical music recognition (OMR) project built around MUSCIMA++.
The goal is to turn sheet music into structured data that can later be used for graph construction, alignment, and export formats such as MusicXML or MIDI.

At the current stage of the project, the implemented work focuses on:
- parsing MUSCIMA++ annotation XML files
- exporting simple node and edge data
- detecting staff regions from score images

## Current Scope

The repository currently contains two completed foundation steps:
- `src/parse_muscima.py`
  Loads MUSCIMA++ XML annotations, converts them into simple node and edge dictionaries, and saves JSON outputs.
- `src/staff_detection.py`
  Detects staff regions from MUSCIMA grayscale score images and returns them as `(y_min, y_max)` tuples.

The graph-construction stage itself is not implemented yet.
For that reason, `src/graph_builder.py` currently acts as a small compatibility wrapper while graph-building logic is developed later.

## Repository Structure

- `src/`
  Main source code.
- `src/parse_muscima.py`
  MUSCIMA++ XML parsing and JSON export.
- `src/staff_detection.py`
  Final staff-line detection implementation.
- `src/graph_builder.py`
  Compatibility wrapper for staff-detection imports; reserved for later graph construction work.
- `tests/test_graph_builder.py`
  Simple batch runner for staff-detection debugging.
- `data/raw/`
  Raw MUSCIMA++ annotations and image files.
- `data/processed/`
  Generated JSON outputs from parsing.
- `tests/`
  Test scripts and local debug outputs.

## Dataset

This project uses MUSCIMA++ v2.0 and related grayscale page images.
Important dataset contents include:
- annotation XML files
- page images used for staff detection

Typical image location used in this repo:
- `data/raw/Images/PNG_GT_Gray/`

## Implemented Features

### 1. MUSCIMA++ Parsing

`src/parse_muscima.py` can:
- load MUSCIMA++ XML files
- inspect their nodes
- convert nodes into simple dictionaries
- convert outlinks into edge dictionaries
- save:
  - `muscima_nodes.json`
  - `muscima_edges.json`

### 2. Staff Detection

`src/staff_detection.py` exposes:

```python
detect_staff_lines(image_path)
```

It returns a list of detected staff regions:

```python
[(y_min, y_max), (y_min, y_max), ...]
```

The detector currently uses:
- grayscale loading
- vertical padding near page edges
- skew estimation and correction
- multiple thresholding variants (`otsu`, `adaptive`, `combined`)
- multi-scale horizontal staff-line extraction
- overlapping vertical slices
- 5-line staff candidate detection
- cross-slice candidate tracking
- merged-region splitting for overly tall staff boxes

## Setup

The project is currently run from a local Python virtual environment.
A typical command format is:

```cmd
.\.venv\Scripts\python.exe <script>
```

## How To Run

### Run the MUSCIMA parser

```cmd
.\.venv\Scripts\python.exe src\parse_muscima.py
```

This will read the configured dataset files and save processed JSON outputs.

### Run the staff-detection test script

```cmd
.\.venv\Scripts\python.exe tests\test_graph_builder.py
```

This script will:
- test one known sample page
- run a small batch of images
- save debug overlays in `tests/staff_debug_sample/`
- save a summary CSV for that sample batch

## Example Output

A typical return value from `detect_staff_lines(image_path)` looks like:

```python
[(232, 404), (465, 640), (702, 876), (938, 1110)]
```

Each tuple represents one staff region in image coordinates.

## Notes On Generated Files

Generated debug folders and processed outputs are intentionally ignored by Git.
Examples include:
- sample debug overlays
- larger staff-detection debug batches
- processed JSON exports

These files are useful locally for validation, but they are not treated as source code.

## What Comes Next

Planned next work includes:
- actual graph construction from parsed music symbols
- connecting detected symbols to staff regions
- later alignment between external detections and MUSCIMA++ data
- later graph/GNN preparation

## Status

This repository is currently in the data preparation + staff detection stage.
The parser and staff detector are implemented and tested locally.
Graph construction is the next major development step.
