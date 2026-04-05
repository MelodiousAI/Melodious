# Hasan's Current Phase & Next Steps - Melodious OMR

> Drafted from the current desktop repo, the team slides, and Ahmad's handoff notes.

---

## Current Phase: Week 3 (v0.3) - Export Integration Layer

**Status:** Week 2 backend work is complete. The repo now includes the first Week 3 export path on Hasan's side and can return inline MusicXML or MIDI from the shared detector payload contract.

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

### Week 3 export checkpoint [x]

* [x] Heuristic notation assembler adapted into `src/export/heuristic_assembler.py`
* [x] MusicXML export adapted into `src/export/musicxml_export.py`
* [x] `/midi` route wired to real export behavior with `musicxml` and `midi` formats
* [x] Export route returns inline content plus heuristic assembly summary metadata
* [x] End-to-end `/midi` smoke check passed on shared sample payloads

### Still to build after this checkpoint

* [ ] Package MUSCIMA training artifacts if Ahmad still needs a more specific edge export
* [ ] Validate export quality on Ahmad's real detector outputs
* [ ] Decide whether export should stay heuristic-only or consume future graph/GNN relationships
* [ ] Decide whether inline export content is sufficient or whether file-oriented download endpoints are needed

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
| Last reported full test suite | Ran 25 tests, OK | Week 3 export checkpoint |

---

## Next Steps

### Immediate (post-checkpoint priorities)

1. **Run the export path on Ahmad's real detector outputs** - confirm the current heuristic export logic still behaves reasonably outside MUSCIMA reference samples
2. **Package MUSCIMA training artifacts if needed** - give Ahmad the exact graph/edge export his GNN trainer expects
3. **Decide whether export should use future graph/GNN relationships** - avoid hard-coding a heuristic-only path if a better assembly signal is coming
4. **Decide whether the API should keep inline export content** - confirm whether the current JSON response is sufficient for the demo and handoff flow

### Blocked or dependent items

* GNN training integration depends on Ahmad confirming the exact artifact format his trainer needs
* Full detector-to-backend export testing depends on Ahmad's real model output handoff
* Container runtime verification is blocked locally until Docker Desktop is available again

### Coordination notes

* The detector payload contract is now the main interface between Ahmad's side and Hasan's side
* The backend should be built to run first on shared sample payloads, not on a final trained model
* The current repo should remain the source of truth for MUSCIMA parsing, graph construction, backend integration, and Hasan-side export wiring
* Ahmad's older `melodious/` branch should be treated as a source of portable logic, not as a package layout to restore wholesale
* The API now exposes `/health`, `/assemble`, and a real `/midi` export route

---

*Last updated: April 5, 2026*
