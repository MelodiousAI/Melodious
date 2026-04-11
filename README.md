# Melodious

Melodious is an optical music recognition (OMR) project built around MUSCIMA++.

This repo currently focuses on:
- parsing MUSCIMA++ annotations
- detecting staff regions in score images
- building reference graphs from MUSCIMA ground truth
- building PyTorch Geometric graphs from detections
- aligning detections back to MUSCIMA ground truth
- validating MUSCIMA reference payload integration
- exposing backend routes for graph assembly, GNN-ready mode switching, and MusicXML/MIDI export
- exposing public product routes for a musician-facing Week 5 sample-first experience
- exporting page-level MUSCIMA training JSONs for GNN supervision
- providing a Streamlit MVP for internal/debug backend inspection
- shipping a separate React frontend for the Week 5 polished product UI

## What Is Implemented

- `src/data_prep/parse_muscima.py`
  Parses MUSCIMA++ XML annotations into JSON-friendly node and edge files.
- `src/data_prep/class_mapping.py`
  Builds and saves a stable class-name <-> class-id mapping for parsed MUSCIMA nodes.
- `src/data_prep/staff_detection.py`
  Detects staff regions from grayscale score images and can save debug overlays.
- `src/data_prep/shared_detection_contract.py`
  Stores the shared MUSCIMA-to-detector class mapping reused by payload and training exports.
- `src/graph/muscima_graph_builder.py`
  Builds document-level reference graph JSON files from MUSCIMA data.
- `src/graph/pyg_graph_builder.py`
  Builds GNN-ready graphs from detection dictionaries.
- `src/graph/detection_alignment.py`
  Aligns detections to MUSCIMA ground-truth nodes using greedy IoU matching.
- `src/evaluation/muscima_reference_evaluation.py`
  Runs graph building plus alignment on the shared MUSCIMA reference payloads.
- `src/evaluation/muscima_training_export.py`
  Exports one JSON per MUSCIMA page for GNN supervision with `edge_type` and `edge_label`.
- `src/api/models.py`
  Defines the FastAPI request and response contracts.
- `src/api/service.py`
  Wraps graph building, optional alignment, and export behind a small service layer.
- `src/api/app.py`
  Exposes `/health`, `/assemble`, `/midi`, and the public `/product/*` routes through FastAPI.
- `src/api/product_models.py`, `src/api/product_service.py`, `src/api/product_routes.py`
  Define the public Week 5 sample catalog, product-facing response contract, and download/image facade.
- `src/inference/gnn_service.py`
  Provides Week 4 checkpoint readiness, assembly-mode resolution, and GNN fallback scaffolding.
- `src/ui/streamlit_app.py`
  Provides the internal/debug Streamlit MVP for payload selection, backend status, assembly, and export handling.
- `frontend/`
  Provides the Week 5 React + Vite + Tailwind public product frontend built from the Lovable design integration.
- `tools/export_muscima_detections.py`
  Exports MUSCIMA XML annotations into the shared detector payload contract.
- `tools/export_muscima_training_data.py`
  CLI wrapper for generating page-level MUSCIMA training exports.

## Repo Structure

- `src/`
  Source packages grouped by API, graph, data-prep, and evaluation responsibilities.
- `tools/`
  Helper scripts for export and data workflow tasks.
- `tests/`
  Tests grouped by API, graph, data-prep, export, and evaluation areas.
- `docs/status/`
  Status and experiment documentation for Hasan's side of the project.
- `docker/`
  Docker build files for the backend service.
- `frontend/`
  The public Week 5 product UI, API client, mock data, and Lovable handoff prompt.
- `data/raw/`
  Raw MUSCIMA++ annotations and page images.
- `data/processed/`
  Processed outputs such as parsed JSON, class mappings, reference graph files, and training exports.
- `sample_detections/`
  Shared detector payload examples, MUSCIMA reference payloads, and the XML subset used for payload export tests.
- `outputs/`
  Generated debug images, summaries, and temporary export files.

## End-to-End Pipelines

### 1. Reference-data path

This path works from MUSCIMA ground truth and produces dataset-side reference graphs.

1. Run `src.data_prep.parse_muscima`
   Creates:
   - `data/processed/muscima_nodes.json`
   - `data/processed/muscima_edges.json`
2. Run `src.data_prep.class_mapping`
   Creates:
   - `data/processed/class_mapping.json`
3. Run `src.graph.muscima_graph_builder`
   Creates:
   - per-document graph JSON files under `data/processed/graphs/`
   - `data/processed/graphs/summary.csv`
   - `data/processed/graphs/batch_stats.json`

### 2. Detection/model path

This path works from detector outputs and produces model-ready graphs plus backend-visible exports.

1. Run or receive symbol detections from a detector.
2. Use `src.data_prep.staff_detection` to detect staff regions for the same page image.
3. Use `src.graph.pyg_graph_builder` to build a PyTorch Geometric `Data` graph from the detections.
4. Use `src.graph.detection_alignment` to compare detections against MUSCIMA ground truth.
5. Use `src.evaluation.muscima_reference_evaluation` to validate the integrated MUSCIMA reference payload path end to end.
6. Use the FastAPI backend to call `/health`, `/assemble`, or `/midi`.
7. Use the public `/product/*` routes for the musician-facing Week 5 sample flow.
8. Use `src.ui.streamlit_app` for the internal/debug backend flow.
9. Use `frontend/` for the polished public UI on top of the product routes.

### 3. MUSCIMA training-export path

This path works from MUSCIMA page graphs and produces one page-level JSON per score for GNN supervision.

1. Build or reuse the document graphs under `data/processed/graphs/`.
2. Run `src.evaluation.muscima_training_export`.
3. Collect:
   - one JSON per page under `data/processed/training_exports/`
   - `data/processed/training_exports/summary.csv`
   - `data/processed/training_exports/batch_stats.json`

## Main Commands

### Parsing and mapping

```powershell
.\.venv\Scripts\python.exe -m src.data_prep.parse_muscima
.\.venv\Scripts\python.exe -m src.data_prep.class_mapping
```

### Staff detection

```powershell
.\.venv\Scripts\python.exe -m src.data_prep.staff_detection --image data\raw\Images\PNG_GT_Gray\w-14\p001.png
.\.venv\Scripts\python.exe -m src.data_prep.staff_detection --image data\raw\Images\PNG_GT_Gray\w-14\p001.png --output-dir outputs\staff_detection\single_test
.\.venv\Scripts\python.exe -m src.data_prep.staff_detection --writer w-14 --output-dir outputs\staff_detection\w14_cli
```

### Reference graph building

```powershell
.\.venv\Scripts\python.exe -m src.graph.muscima_graph_builder
.\.venv\Scripts\python.exe -m src.graph.muscima_graph_builder --limit 5
.\.venv\Scripts\python.exe -m src.graph.muscima_graph_builder --document CVC-MUSCIMA_W-01_N-10_D-ideal
```

### PyG graph building

```powershell
.\.venv\Scripts\python.exe -m src.graph.pyg_graph_builder
```

### Alignment

```powershell
.\.venv\Scripts\python.exe -m src.graph.detection_alignment --document CVC-MUSCIMA_W-01_N-10_D-ideal --detections-json data\processed\sample_alignment_detections.json --iou-threshold 0.5
```

### MUSCIMA reference evaluation

```powershell
.\.venv\Scripts\python.exe -m src.evaluation.muscima_reference_evaluation
```

### MUSCIMA payload export helper

```powershell
.\.venv\Scripts\python.exe tools\export_muscima_detections.py
```

### MUSCIMA training export helper

```powershell
.\.venv\Scripts\python.exe -m src.evaluation.muscima_training_export
.\.venv\Scripts\python.exe tools\export_muscima_training_data.py --document CVC-MUSCIMA_W-01_N-10_D-ideal
```

### Backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
docker compose up --build
```

### Streamlit MVP (internal/debug)

```powershell
.\.venv\Scripts\python.exe -m streamlit run src\ui\streamlit_app.py
```

### Week 5 frontend

```powershell
cd frontend
npm install
npm run dev
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest tests\data_prep\test_class_mapping.py
.\.venv\Scripts\python.exe -m unittest tests\graph\test_pyg_graph_builder.py
.\.venv\Scripts\python.exe -m unittest tests\graph\test_detection_alignment.py
.\.venv\Scripts\python.exe -m unittest tests\graph\test_muscima_graph_builder.py
.\.venv\Scripts\python.exe -m unittest tests\api\test_api_app.py
.\.venv\Scripts\python.exe -m unittest tests\api\test_product_routes.py
.\.venv\Scripts\python.exe -m unittest tests\evaluation\test_muscima_training_export.py
.\.venv\Scripts\python.exe -m unittest tests\inference\test_gnn_service.py
.\.venv\Scripts\python.exe -m unittest discover tests
cd frontend
npm test
npm run build
```

## Current State

At the current checkpoint, the repo already has:
- parsed MUSCIMA node and edge exports
- a stable class mapping
- a stable staff detector
- full reference MUSCIMA graph generation
- a detection-to-PyG graph builder
- a detection-to-ground-truth alignment layer
- MUSCIMA reference payload integration checks
- a FastAPI backend for graph assembly, GNN-ready mode switching, and MusicXML/MIDI export
- a public Week 5 `/product/*` facade for sample catalog, preview images, downloads, and musician-facing transcription responses
- a Week 4 GNN inference scaffold with checkpoint readiness reporting and heuristic fallback
- a Streamlit MVP for payload upload/selection plus backend health, assembly, and export calls for internal/debug work
- a separate React + Vite + Tailwind frontend under `frontend/` for the polished Week 5 product layer
- a page-level MUSCIMA training export with candidate edges and supervision labels
- automated tests for graph, export, evaluation, API, inference scaffold modules, and the Week 5 product routes
- smoke tests for `/assemble` and `/midi`
- verified Docker image build for the API service
- verified containerized `/health`, `/assemble`, and `/midi` using Ahmad's real YOLOv8 payload

## Notes

- `data/raw/`, `data/processed/`, and `outputs/` are data/output folders, not hand-written source code.
- `sample_detections/` contains both real detector samples and MUSCIMA-specific reference payloads.
- `tools/` is for helper scripts that support the workflow but are not the core runtime modules.
- The project is intentionally kept simple: separate source code from outputs, keep modules focused, and add small testable steps.
- On this machine, `docker compose up --build` may still need a different host port than `8000` if another local project is already using that port.
