# Hasan's Current Phase & Next Steps - Melodious OMR

> Drafted from the current repo, Ahmad's integration replies, and the validated Week 3 checkpoint on April 7, 2026.

---

## Current Phase: Week 3 (v0.3) - Export and Training Handoff

**Status:** Hasan-side Week 3 deliverables are complete. The repo now includes backend export wiring, real-payload validation on Ahmad's YOLOv8 output, and a MUSCIMA page-level training export for GNN supervision.

---

## What's Done (Weeks 1-3)

### Week 1 [x]

* [x] MUSCIMA++ parser (`src/data_prep/parse_muscima.py`) exports node and edge data
* [x] Stable class mapping (`src/data_prep/class_mapping.py`)
* [x] Staff region detection (`src/data_prep/staff_detection.py`)
* [x] MUSCIMA reference graph builder (`src/graph/muscima_graph_builder.py`)
* [x] Core unit tests for graph, mapping, and alignment modules
* [x] Repo cleanup into a simple `src/`, `tools/`, `tests/`, `data/`, `sample_detections/`, `outputs/` layout

### Week 2 [x]

* [x] PyTorch Geometric graph builder from detector payloads (`src/graph/pyg_graph_builder.py`)
* [x] Detection-to-ground-truth alignment (`src/graph/detection_alignment.py`)
* [x] MUSCIMA detector-payload export helper (`tools/export_muscima_detections.py`)
* [x] MUSCIMA reference payload integration run on 5 shared pages
* [x] Saved integration summary under `outputs/muscima_reference_integration/summary.json`
* [x] Shared MUSCIMA samples under `sample_detections/muscima_reference/` and `sample_detections/muscima_xml/`
* [x] `/assemble` contract locked so serialized node rows preserve input detection order

### Week 3 [x]

* [x] Heuristic notation assembler adapted into `src/export/heuristic_assembler.py`
* [x] MusicXML export adapted into `src/export/musicxml_export.py`
* [x] `/midi` route wired to real export behavior with `musicxml` and `midi` formats
* [x] Export route returns inline content plus heuristic assembly summary metadata
* [x] `/midi` rendering hardened to avoid Windows temp-directory cleanup failures
* [x] Ahmad's representative YOLOv8 payload validated successfully through `/assemble` and `/midi`
* [x] MUSCIMA page-level training export implemented with `edge_type` and `edge_label`
* [x] Full training-export batch generated under `data/processed/training_exports/`

### Remaining work after Hasan's Week 3 closeout

* [ ] Hand the generated training exports to Ahmad and confirm they load cleanly into his trainer
* [ ] Decide whether export should stay heuristic-only or consume future graph/GNN relationships
* [ ] Decide whether inline export content is sufficient or whether file-oriented download endpoints are needed
* [ ] If needed for demo convenience, change the compose host port from `8000` when another local project is already using it

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
| MUSCIMA training export pages | 140 | `data/processed/training_exports/` |
| MUSCIMA training export nodes | 58467 | `data/processed/training_exports/batch_stats.json` |
| MUSCIMA training export edges | 2625480 | `data/processed/training_exports/batch_stats.json` |
| Last reported full test suite | Ran 26 tests, OK | Week 3 training-export checkpoint |

---

## Next Steps

### Immediate (post-closeout handoff)

1. **Hand Ahmad the MUSCIMA training export path and schema** - point him to `data/processed/training_exports/` and the `edge_type`/`edge_label` vocabulary
2. **Confirm trainer ingestion on Ahmad's side** - make sure the generated page JSONs load without schema changes
3. **Decide whether export should use future graph/GNN relationships** - avoid hard-coding a heuristic-only path if a better assembly signal is coming
4. **Decide whether the API should keep inline export content** - confirm whether the current JSON response is sufficient for the demo and handoff flow

### Blocked or dependent items

* Final GNN training integration depends on Ahmad loading the exported page JSONs successfully
* Any future graph-aware exporter depends on whether Ahmad wants to move beyond detection-payload-based export
* Full `docker compose up --build` on host port `8000` can still be blocked by unrelated local port usage

### Coordination notes

* The detector payload contract is now the main interface between Ahmad's side and Hasan's side
* On April 7, 2026, Ahmad's real YOLOv8 payload `lg-101766503886095953-aug-gonville--page-1.json` returned `200` on `/assemble`, `/midi` with `musicxml`, and `/midi` with `midi`
* On April 7, 2026, the API Docker image built successfully and the containerized backend returned `200` on `/health`, `/assemble`, and `/midi`
* The current repo should remain the source of truth for MUSCIMA parsing, graph construction, backend integration, and Hasan-side export wiring
* Ahmad's older `melodious/` branch should be treated as a source of portable logic, not as a package layout to restore wholesale
* The MUSCIMA training export uses one JSON per page with `edge_type` in `{knn, same_staff_local, vertical_overlap, horizontal_neighbor}` and `edge_label` in `{no_relation, stem_notehead, beam_notegroup, slur_phrase, tie_sustained}`
* The API exposes `/health`, `/assemble`, and a real `/midi` export route

---

*Last updated: April 7, 2026*
