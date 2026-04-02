# Hasan's Current Phase & Next Steps - Melodious OMR

> Drafted from the current desktop repo, the team slides, and Ahmad's handoff notes.

---

## Current Phase: Week 2 (v0.2) - Backend and Integration Layer

**Status:** Week 1 data and graph deliverables are complete. The repo is ready to move from standalone graph utilities into the backend and handoff stage.

---

## What's Done (Weeks 1-2)

### Week 1 [x]

* [x] MUSCIMA++ parser (`src/data_prep/parse_muscima.py`) exports node and edge data
* [x] Stable class mapping (`src/data_prep/class_mapping.py`)
* [x] Staff region detection (`src/data_prep/staff_detection.py`)
* [x] MUSCIMA reference graph builder (`src/graph/muscima_graph_builder.py`)
* [x] Core unit tests for graph, mapping, and alignment modules
* [x] Repo cleanup into a simple `src/`, `tools/`, `tests/`, `data/`, `sample_detections/`, `outputs/` layout

### Week 2 prep [x]

* [x] PyTorch Geometric graph builder from detector payloads (`src/graph/pyg_graph_builder.py`)
* [x] Detection-to-ground-truth alignment (`src/graph/detection_alignment.py`)
* [x] MUSCIMA detector-payload export helper (`tools/export_muscima_detections.py`)
* [x] MUSCIMA reference payload integration run on 5 shared pages
* [x] Saved integration summary under `outputs/muscima_reference_integration/summary.json`
* [x] Shared MUSCIMA samples under `sample_detections/muscima_reference/` and `sample_detections/muscima_xml/`

### Still to build for v0.2

* [x] FastAPI backend skeleton
* [x] Docker Compose setup
* [x] API request/response contracts for `/health`, `/assemble`, and `/midi`
* [x] Service-layer smoke tests using sample payloads
* [ ] Package MUSCIMA training artifacts if Ahmad still needs a more specific edge export

---

## Key Status Summary

| Metric | Value | Source |
|-|-|-|
| Processed reference graph JSONs | 140 | `data/processed/graphs/` |
| Shared MUSCIMA reference payloads | 5 | `sample_detections/muscima_reference/` |
| 5-page integration detections | 1885 | `outputs/muscima_reference_integration/summary.json` |
| Average integration F1 | 0.691588 | 5-page MUSCIMA reference run |
| Average integration recall | 0.531545 | 5-page MUSCIMA reference run |
| Average graph edges per page | 15024 | 5-page MUSCIMA reference run |
| Last reported full test suite | Ran 20 tests, OK | Repo checkpoint before Week 2 work |

---

## Next Steps

### Immediate (Week 2 priorities)

1. **Verify the backend on real local runs** - start the FastAPI app and confirm the routes behave correctly outside unit tests
2. **Package MUSCIMA training artifacts if needed** - give Ahmad the exact graph/edge export his GNN trainer expects
3. **Decide the `/assemble` response shape for Ahmad's side** - keep the current contract stable before further integration
4. **Prepare the Week 3 export wiring** - keep `/midi` as the reserved integration point for MusicXML/MIDI work

### Blocked or dependent items

* GNN training integration depends on Ahmad confirming the exact artifact format his trainer needs
* Full detector-to-backend testing depends on Ahmad's real model output handoff
* Final GNN inference wiring depends on Ahmad's trained checkpoint handoff

### Coordination notes

* The detector payload contract is now the main interface between Ahmad's side and Hasan's side
* The backend should be built to run first on shared sample payloads, not on a final trained model
* The current repo should remain the source of truth for MUSCIMA parsing, graph construction, and integration logic
* The current Week 2 API exposes `/health`, `/assemble`, and a placeholder `/midi` route

---

*Last updated: April 2, 2026*
