# Hasan's Current Phase & Next Steps - Melodious OMR

> Drafted from the current repo state after the Week 5 Lovable-frontend integration checkpoint on April 11, 2026.

---

## Current Phase: Week 5 (v0.5) - Public Product Frontend Integration

**Status:** Hasan-side Week 5 frontend integration is now in place on top of the completed Week 4 backend. The repo keeps the existing GNN-ready FastAPI + Streamlit MVP intact, keeps the public `/product/*` facade stable for musician-facing flows, and now uses the Lovable-derived multi-page React frontend under `frontend/` as the public product layer.

---

## What's Done (Weeks 1-5)

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

### Week 4 [x]

* [x] GNN inference/runtime scaffold added under `src/inference/gnn_service.py`
* [x] `/health` now reports GNN checkpoint readiness plus supported assembly modes
* [x] `/assemble` now accepts `assembly_mode` with `auto`, `heuristic`, and `gnn`
* [x] `/assemble` now returns resolved mode, fallback metadata, heuristic assembly summary, and an attention-preview placeholder
* [x] `/midi` now accepts the same Week 4 assembly-mode contract and surfaces the same fallback/status metadata
* [x] Clean fallback behavior implemented when `gnn` is requested without a ready checkpoint
* [x] Streamlit MVP added under `src/ui/streamlit_app.py`
* [x] New API and inference-scaffold tests added for mode switching and missing-checkpoint behavior

### Week 5 [x] (integration checkpoint)

* [x] Public `/product/config`, `/product/samples`, `/product/samples/{sample_id}/image`, and `/product/transcribe` routes added
* [x] Public sample catalog curated from MUSCIMA reference payloads with repo-local image previews
* [x] Public download facade added for MusicXML and MIDI sample exports
* [x] Local CORS enabled for React frontend development on `http://localhost:5173`
* [x] Separate React + Vite + Tailwind frontend scaffolded under `frontend/`
* [x] Lovable-generated product UI integrated into the repo as a routed frontend with home, library, workspace, and upload placeholder pages
* [x] Lovable handoff prompt saved under `frontend/LOVABLE_PROMPT.md`
* [x] Existing typed `/product/*` client retained while the UI layer was replaced
* [x] New backend and frontend tests added for the Week 5 product layer
* [x] Frontend validation re-run on April 11, 2026 with `npm test`, `npm run build`, and `npm run lint`

### Remaining work after Hasan's Week 5 integration checkpoint

* [ ] Plug Ahmad's real trained GNN checkpoint into the Week 4 scaffold
* [ ] Implement the model-specific inference adapter once Ahmad shares checkpoint wiring details
* [ ] Keep the integrated `/product/*` contract stable while public UI polish continues
* [ ] Decide whether `/midi` should remain heuristic-driven or consume future GNN relation outputs
* [ ] Wire real attention weights into the existing explainability surface once Ahmad's checkpoint exposes them
* [ ] Capture final combined YOLO + GNN metrics once Ahmad's checkpoint is available

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
| Backend contract stage | `v0.4` core + `v0.5` product layer | `src/api/service.py`, `src/api/product_service.py` |
| Last reported full test suite | Ran 36 tests, OK | Week 5 prep checkpoint, plus targeted frontend validation on April 11 |

---

## Next Steps

### Immediate

1. **Keep the public `/product/*` contract stable** - let frontend polish continue without re-exposing backend/debug terminology
2. **Get Ahmad's checkpoint path and adapter expectations** - identify what his saved checkpoint requires beyond a path on disk
3. **Integrate the checkpoint into `src/inference/gnn_service.py`** - keep both the internal and public UI contracts stable while swapping the scaffold adapter for a real one
4. **Decide how GNN outputs should influence export quality** - confirm whether the future model path should remain heuristic-backed or feed downstream assembly/export

### Blocked or dependent items

* The real trained GNN checkpoint is still external
* Any checkpoint-specific tensor decoding or model-class loading details are still external
* Final combined YOLO + GNN metrics are still external
* Real attention weights still depend on Ahmad's trained model exposing them
* Public raw image upload is intentionally disabled until detector-side image ingestion exists in this repo

### Coordination notes

* The detector payload contract remains stable and unchanged from Week 3
* The Week 4 backend intentionally treats Ahmad's future checkpoint as a plug-in to an already-stable API and UI surface
* `assembly_mode="gnn"` currently falls back to `heuristic` with an explicit warning when no checkpoint is ready
* The Streamlit MVP remains the internal/debug tool and still consumes `/health`, `/assemble`, and `/midi`
* The React frontend is now the public/product-facing layer and talks only to `/product/*`
* On April 8, 2026, the full local Python test suite passed with 36 tests after the Week 5 prep layer landed
* On April 11, 2026, the routed Lovable-based frontend passed `npm test`, `npm run build`, and `npm run lint`

---

*Last updated: April 11, 2026*
