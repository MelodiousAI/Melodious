# Hasan's Experiment Documentation - Melodious OMR

> This file tracks the parser, graph, alignment, backend, export, and training-handoff work on Hasan's side of the project.

---

## 1. MUSCIMA++ Parsing and Reference Data Pipeline

### 1.1 MUSCIMA++ Parser

**Implementation:** `src/data_prep/parse_muscima.py`

Parses MUSCIMA++ XML annotations into JSON-friendly node and edge exports that can be reused by downstream graph code.

| Output | Status |
|-|-|
| Node export | [x] Implemented |
| Edge export | [x] Implemented |
| JSON-friendly structure | [x] Implemented |
| CLI entrypoint | [x] Implemented |

### 1.2 Class Mapping

**Implementation:** `src/data_prep/class_mapping.py`

Builds a stable class-name to class-id mapping so parsed annotations and detector payloads can share a consistent label space.

| Output | Status |
|-|-|
| Stable class mapping JSON | [x] Implemented |
| Class name to id conversion | [x] Implemented |
| Id to class name conversion | [x] Implemented |

### 1.3 MUSCIMA Reference Graph Builder

**Implementation:** `src/graph/muscima_graph_builder.py`

Builds document-level reference graph JSON files from MUSCIMA data. Current processed outputs include 140 per-document graph JSONs under `data/processed/graphs/`.

| Output | Value |
|-|-|
| Reference graph JSON files | 140 |
| Summary CSV | `data/processed/graphs/summary.csv` |
| Batch stats JSON | `data/processed/graphs/batch_stats.json` |

---

## 2. Staff Detection

**Implementation:** `src/data_prep/staff_detection.py`

Detects staff regions from grayscale score images and supports debug overlays for visual inspection.

| Feature | Status |
|-|-|
| Single-image CLI | [x] |
| Writer-folder CLI | [x] |
| Debug overlay export | [x] |
| Integration with graph builder helpers | [x] |

---

## 3. Detection-to-Graph Pipeline

### 3.1 PyTorch Geometric Graph Builder

**Implementation:** `src/graph/pyg_graph_builder.py`

Builds graph objects from detector payload dictionaries so symbol detections can be converted into GNN-ready inputs.

| Property | Current value |
|-|-|
| Input source | Detector-style JSON payloads |
| Node feature dimension | 10 |
| Edge feature dimension | 8 |
| Target use | PyTorch Geometric graph construction |

### 3.2 Detection Alignment

**Implementation:** `src/graph/detection_alignment.py`

Aligns detections back to MUSCIMA ground truth using greedy IoU matching.

| Feature | Status |
|-|-|
| IoU-based matching | [x] |
| Match / FP / FN summary | [x] |
| Precision / recall / F1 summary | [x] |
| CLI entrypoint | [x] |

---

## 4. MUSCIMA Reference Payload Integration

**Implementation:** `src/evaluation/muscima_reference_evaluation.py`

Runs graph building plus alignment on the shared MUSCIMA reference payloads to validate the detector-payload integration path end to end.

**Saved summary:** `outputs/muscima_reference_integration/summary.json`

### 4.1 Aggregate 5-page summary

| Metric | Value |
|-|-|
| Pages evaluated | 5 |
| Total payload detections | 1885 |
| Average integration F1 | 0.691588 |
| Average integration recall | 0.531545 |
| Average graph edges per page | 15024 |
| False positives in current run | 0 total across 5 pages |

### 4.2 Per-page integration results

| Document | Detections | Edges | Recall | F1 |
|-|-|-|-|-|
| `CVC-MUSCIMA_W-01_N-10_D-ideal` | 478 | 22290 | 0.592317 | 0.743969 |
| `CVC-MUSCIMA_W-01_N-14_D-ideal` | 366 | 16812 | 0.618243 | 0.764092 |
| `CVC-MUSCIMA_W-01_N-19_D-ideal` | 301 | 9052 | 0.517182 | 0.681767 |
| `CVC-MUSCIMA_W-02_N-06_D-ideal` | 401 | 14576 | 0.430720 | 0.602102 |
| `CVC-MUSCIMA_W-02_N-13_D-ideal` | 339 | 12390 | 0.499264 | 0.666012 |

---

## 5. Shared Detector Contract and Export Helpers

**Implementations:** `src/data_prep/shared_detection_contract.py`, `tools/export_muscima_detections.py`

Exports MUSCIMA XML annotations into the shared detector payload contract so backend and graph code can be tested before full model handoff.

| Asset | Status |
|-|-|
| MUSCIMA XML subset for tests | [x] Present |
| Reference payload exports | [x] Present |
| Contract-oriented helper script | [x] Implemented |

---

## 6. MUSCIMA Page-Level Training Export

**Implementations:** `src/evaluation/muscima_training_export.py`, `tools/export_muscima_training_data.py`

Exports one JSON per MUSCIMA page using the reduced shared detector taxonomy for nodes plus the candidate-edge and supervision-label format Ahmad requested for GNN training.

### 6.1 Export schema and vocabularies

Each page export contains:

| Field | Purpose |
|-|-|
| `page_id` | MUSCIMA document id such as `CVC-MUSCIMA_W-01_N-10_D-ideal` |
| `image_path` | Relative page image path |
| `image_size` | Page width and height |
| `nodes` | Reduced shared-taxonomy node records with stable `node_idx` and `node_id` |
| `edges` | Directed candidate edges with `source_idx`, `target_idx`, `edge_type`, and `edge_label` |

Current edge-type vocabulary:

| Edge type | Meaning |
|-|-|
| `knn` | k-nearest-neighbor geometric candidate edge |
| `same_staff_local` | local same-staff candidate edge |
| `vertical_overlap` | strong vertical-overlap candidate edge |
| `horizontal_neighbor` | immediate left-right same-staff candidate edge |

Current supervision-label vocabulary:

| Edge label | Meaning |
|-|-|
| `no_relation` | candidate edge with no positive supervision relation |
| `stem_notehead` | notehead-stem relation |
| `beam_notegroup` | notehead-beam relation |
| `slur_phrase` | notehead-notehead relation induced through a shared slur |
| `tie_sustained` | notehead-notehead relation induced through a shared tie |

### 6.2 Full batch export result

**Generated outputs:** `data/processed/training_exports/`

| Artifact | Value |
|-|-|
| Page JSON files | 140 |
| Total exported nodes | 58467 |
| Total exported edges | 2625480 |
| `stem_notehead` edges | 138456 |
| `beam_notegroup` edges | 42860 |
| `slur_phrase` edges | 30046 |
| `tie_sustained` edges | 2660 |
| `no_relation` edges | 2411458 |
| Summary CSV | `data/processed/training_exports/summary.csv` |
| Batch stats JSON | `data/processed/training_exports/batch_stats.json` |

This export uses one edge record per directed candidate-edge occurrence. If the same node pair appears under multiple candidate-edge builders, each `edge_type` is exported separately with its own `edge_label`.

---

## 7. Test and Repo Status

| Item | Status |
|-|-|
| `tests/data_prep/test_class_mapping.py` | [x] Present |
| `tests/graph/test_detection_alignment.py` | [x] Present |
| `tests/graph/test_muscima_graph_builder.py` | [x] Present |
| `tests/graph/test_pyg_graph_builder.py` | [x] Present |
| `tests/api/test_api_app.py` | [x] Present |
| `tests/export/test_heuristic_assembler.py` | [x] Present |
| `tests/export/test_musicxml_export.py` | [x] Present |
| `tests/evaluation/test_muscima_training_export.py` | [x] Present |
| `tests/inference/test_gnn_service.py` | [x] Present |
| Last reported full suite checkpoint | Ran 36 tests, OK |
| Repo cleanup completed | [x] |

The repo now uses `src/api/`, `src/graph/`, `src/data_prep/`, `src/evaluation/`, `src/inference/`, and `src/ui/`, grouped tests under `tests/`, status docs under `docs/status/`, and generated artifacts separated into `data/processed/`, `sample_detections/`, and `outputs/`.

---

## 8. Backend Service Layer, GNN Scaffold, and UI

**Implementations:** `src/api/models.py`, `src/api/service.py`, `src/api/app.py`, `src/inference/gnn_service.py`, `src/ui/streamlit_app.py`, `src/export/heuristic_assembler.py`, `src/export/musicxml_export.py`, `docker/Dockerfile.api`, `docker-compose.yml`

The backend still wraps existing graph, alignment, and export logic instead of duplicating it in route handlers. Week 4 extends that thin service layer with checkpoint readiness reporting, assembly-mode resolution, and a Streamlit client for demo use.

| Endpoint | Status | Notes |
|-|-|-|
| `GET /health` | [x] Implemented | Returns backend stage plus GNN checkpoint readiness |
| `POST /assemble` | [x] Implemented | Builds graph outputs and resolves `auto`, `heuristic`, or `gnn` assembly mode |
| `POST /midi` | [x] Implemented | Returns inline MusicXML or base64 MIDI and now carries Week 4 assembly-mode metadata |

### 8.1 Week 4 GNN runtime scaffold

**Implementation:** `src/inference/gnn_service.py`

The GNN runtime layer intentionally avoids guessing Ahmad's final model class. Instead it freezes the handoff surface around readiness and fallback behavior.

| Feature | Status |
|-|-|
| `MELODIOUS_GNN_CHECKPOINT` path resolution | [x] |
| Checkpoint existence reporting | [x] |
| Adapter readiness reporting | [x] |
| `auto -> gnn` when runtime is ready | [x] |
| `gnn -> heuristic` fallback when runtime is not ready | [x] |
| Attention-preview placeholder contract | [x] |

Current behavior:

* If no checkpoint path is configured, `/health` reports that the backend is waiting on Ahmad's checkpoint
* If `assembly_mode="gnn"` is requested before the runtime is ready, the backend returns `200` with a warning and a resolved mode of `heuristic`
* If a future adapter becomes ready and a checkpoint exists, `assembly_mode="auto"` is already prepared to promote requests to the GNN path

### 8.2 Current `/health` behavior

| Field group | Status |
|-|-|
| Base service status (`status`, `service`, `stage`) | [x] |
| Supported assembly modes | [x] |
| Default assembly mode | [x] |
| GNN checkpoint readiness block | [x] |

The Week 4 `/health` contract is the main status surface for the API and Streamlit MVP. It exposes whether the checkpoint is configured, whether it exists on disk, whether the adapter is ready, and whether the runtime is fully ready for inference.

### 8.3 Current `/assemble` behavior

| Feature | Status |
|-|-|
| Generic detector payload assembly | [x] |
| MUSCIMA reference payload auto-detection | [x] |
| Optional alignment summary | [x] |
| Optional serialized graph arrays in JSON | [x] |
| Serialized node row order matches input detection order | [x] |
| `edge_index` refers to the same serialized node row indices | [x] |
| Request validation through FastAPI/Pydantic | [x] |
| `assembly_mode` request field | [x] |
| Resolved assembly-mode response block | [x] |
| Stable heuristic summary block for current baseline output | [x] |
| Attention-preview placeholder block | [x] |

The Week 4 `/assemble` response now carries:

* `assembly_mode.requested_mode`
* `assembly_mode.applied_mode`
* `assembly_mode.fallback_applied`
* `assembly_mode.fallback_reason`
* `assembly_mode.checkpoint_ready`
* `assembly_summary`
* `attention_preview`

This freezes the contract the future GNN path is expected to honor even before the real checkpoint is available.

### 8.4 Current `/midi` behavior

| Feature | Status |
|-|-|
| Inline MusicXML response | [x] |
| Inline base64 MIDI response | [x] |
| Heuristic assembly summary in response | [x] |
| Repo-local temp rendering fallback | [x] |
| Week 4 `assembly_mode` request field | [x] |
| Week 4 resolved assembly-mode metadata in response | [x] |
| Attention-preview placeholder block | [x] |

Week 4 keeps the actual export generation heuristic-backed for now, but the export route is already carrying the same GNN readiness and fallback metadata as `/assemble`. This keeps the demo flow and future integration path consistent.

### 8.5 Streamlit MVP

**Implementation:** `src/ui/streamlit_app.py`

The Streamlit app is a thin client over the FastAPI backend rather than a second backend.

| Feature | Status |
|-|-|
| Upload detector payload JSON | [x] |
| Select bundled sample payloads | [x] |
| Call `/health` | [x] |
| Call `/assemble` | [x] |
| Call `/midi` | [x] |
| Show graph statistics | [x] |
| Show assembly-mode/fallback details | [x] |
| Download MusicXML | [x] |
| Download MIDI | [x] |
| Attention-visualization placeholder panel | [x] |

### 8.6 Docker verification and real YOLO payload validation

On **April 7, 2026**, the API Docker image built successfully after adding the OpenCV runtime libraries required by `opencv-python` on `python:3.13-slim`.

| Check | Result |
|-|-|
| `docker build -f docker/Dockerfile.api -t melodious-api-local .` | Succeeded |
| Container startup | Succeeded |
| `GET /health` in-container | `200` |
| `POST /assemble` in-container | `200` |
| `POST /midi` with `musicxml` in-container | `200` |
| `POST /midi` with `midi` in-container | `200` |

The containerized route checks were run using Ahmad's real YOLOv8 payload. The only remaining Docker-specific local issue is that `docker compose up --build` on the default host port can conflict with unrelated containers already using port `8000`.

On **April 7, 2026**, the representative Ahmad payload `lg-101766503886095953-aug-gonville--page-1.json` was validated locally against the backend.

| Route | Result |
|-|-|
| `POST /assemble` | `200`, `88` detections, `88` nodes, `1266` edges |
| `POST /midi` with `musicxml` | `200` |
| `POST /midi` with `midi` | `200` |

This confirmed that Ahmad's real YOLOv8 output matches the current detector payload contract and that the backend export route accepts it directly.

### 8.7 Reuse decision

The current repo still follows a selective adaptation strategy for Ahmad's older work:

| Candidate from Ahmad's branch | Decision | Rationale |
|-|-|-|
| `melodious/baselines/heuristic_assembler.py` | Reused and adapted | Small, portable, already matches the detector payload contract |
| `melodious/musicxml_export.py` | Reused and adapted | Export logic was portable after moving it behind the current `src/` layout |
| `melodious/cli.py` and `melodious/pipeline.py` | Not integrated | Depend on Ahmad's old package layout and detector runtime responsibilities |
| Week 4 GNN inference class internals | Not guessed | Wait for Ahmad's actual checkpoint wiring instead of hard-coding speculative model logic |

---

## 9. Decisions and Tradeoffs

| Decision | Alternatives considered | Rationale |
|-|-|-|
| Separate `muscima_graph_builder.py` from `pyg_graph_builder.py` | One combined graph builder | Reference-data graphs and detector-input graphs serve different stages |
| Keep outputs outside source directories | Mix generated files into source tree | Cleaner repo and easier handoff review |
| Use greedy IoU alignment for initial matching | More complex assignment methods | Simple, testable, and adequate for current integration work |
| Validate with shared MUSCIMA reference payloads first | Wait for final model outputs first | Lets backend and graph code progress before model handoffs arrive |
| Wrap existing graph code behind a small FastAPI service layer | Reimplement graph logic inside route handlers | Keeps API work thin and reduces duplication |
| Keep `/midi` as a stable route name from Week 2 into Week 3 and Week 4 | Rename the export route during integration | Preserves the agreed backend entrypoint while adding new capabilities incrementally |
| Selectively adapt Ahmad's Week 3 modules | Cherry-pick the old `melodious/` package or reimplement from scratch | Reuses proven logic without undoing the cleaned repo layout |
| Return inline MusicXML/base64 MIDI content from the API | Write export files directly on the server | Keeps the backend stateless and easier to test on shared sample payloads |
| Export one record per directed candidate-edge type | Collapse all candidate types for a node pair into one record | Keeps `edge_type` unambiguous and matches Ahmad's request that it be a separate input feature |
| Use the reduced shared detector taxonomy for training-export nodes | Export all 115 MUSCIMA classes directly | Keeps training artifacts aligned with the existing detector/backend contract |
| Derive `slur_phrase` and `tie_sustained` between noteheads through shared connector nodes | Require explicit slur/tie nodes in the reduced export | Preserves the requested supervision labels without expanding the node taxonomy beyond the shared detector set |
| Freeze `auto|heuristic|gnn` request handling before the real checkpoint exists | Wait for Ahmad's model and then redesign the contract | Lets Hasan-side API and UI progress now while minimizing later surface-area changes |
| Use explicit fallback metadata rather than returning an error when `gnn` is unavailable | Fail `400`/`503` on missing checkpoint | Keeps the Week 4 demo usable while making the degraded path visible to callers |
| Expose an attention-preview placeholder now | Omit explainability fields until the trained GAT arrives | Prevents the UI contract from changing again when attention becomes available |
| Use an env-var checkpoint path instead of embedding a guessed repo-local path | Hard-code a likely checkpoint filename | Keeps the handoff explicit and avoids silent path mismatches |

---

## 10. Known Issues and Next Work

| Item | Impact | Planned next step |
|-|-|-|
| The GNN runtime adapter is still a scaffold | The backend cannot execute real checkpoint inference yet | Replace the stub adapter once Ahmad shares the actual checkpoint and model-loading details |
| Export remains heuristic-only | MusicXML/MIDI quality may be limited on complex notation even though the API is GNN-ready | Decide whether to feed future GNN relationships into the export stage |
| Ahmad still needs to load the generated training exports on his side | Could reveal minor schema adjustments still needed for his trainer | Hand off one sample page JSON first, then the full directory if accepted |
| API returns inline content only | Large files or browser download flows may need a different contract later | Decide whether to keep inline responses or add file-oriented endpoints |
| `docker compose up --build` on host port `8000` can still fail locally | An unrelated local container may already own port `8000` | Change the compose host port or stop the conflicting local service when needed |
| Real attention weights are still unavailable | Streamlit can only show the placeholder explainability surface today | Wire attention outputs into the existing `attention_preview` contract once Ahmad's model exposes them |

---

## 11. Week 5 Public Frontend Integration

**Implementations:** `src/api/product_models.py`, `src/api/product_service.py`, `src/api/product_routes.py`, `frontend/`, `tests/api/test_product_routes.py`, `frontend/src/app/App.test.tsx`

Week 5 keeps the Week 4 engineering routes intact and adds a separate public layer for the polished musician-facing experience. The current checkpoint replaces the temporary React shell with the routed Lovable-derived public UI while preserving the same `/product/*` facade and backend service helpers.

### 11.1 Public product facade

| Route | Status | Notes |
|-|-|-|
| `GET /product/config` | [x] Implemented | Exposes stage, upload status message, and public feature flags |
| `GET /product/samples` | [x] Implemented | Lists curated MUSCIMA demo samples with titles, subtitles, and preview URLs |
| `GET /product/samples/{sample_id}/image` | [x] Implemented | Serves repo-local MUSCIMA grayscale page previews |
| `POST /product/transcribe` | [x] Implemented | Resolves one sample and returns a merged musician-facing response |
| `GET /product/samples/{sample_id}/downloads/{format}` | [x] Implemented | Returns MusicXML or MIDI exports without exposing internal route semantics |

The public contract intentionally hides `payload_kind`, `assembly_mode`, graph arrays, and other backend/debug details. Internally it still reuses the Week 4 service helpers and the existing heuristic-backed export path.

### 11.2 Public sample catalog decision

| Decision | Outcome |
|-|-|
| Public demo source | MUSCIMA reference payloads only |
| Reason | Repo-local MUSCIMA page images can be resolved deterministically from the document name |
| Deferred samples | `sample_detections/model_outputs_quick/` remains internal until matching local preview images are available |
| Sample metadata | `id`, `title`, `subtitle`, `document_name`, `preview_image_url`, `description`, `tags` |

### 11.3 Frontend integration

**Implementation:** `frontend/`

| Area | Status |
|-|-|
| Vite + React + TypeScript scaffold | [x] |
| Tailwind-based styling | [x] |
| Typed API client for `/product/*` | [x] |
| Mock fallback data for offline/frontend-only work | [x] |
| Lovable multi-page visual system adapted into repo-local components | [x] |
| Routed home page | [x] |
| Routed sample library page | [x] |
| Routed sample workspace page | [x] |
| Routed upload placeholder page | [x] |
| MusicXML / MIDI download actions | [x] |
| Confidence cue panel | [x] |
| Explainability placeholder panel | [x] |
| Future LLM/music explanation panel | [x] |
| MIDI playback area scaffold | [x] |
| Saved Lovable prompt | [x], `frontend/LOVABLE_PROMPT.md` |

The integrated frontend intentionally keeps the backend-facing code thin. The merge reuses the existing DTOs and `frontend/src/lib/api.ts` client, maps Lovable's home/library/workspace/upload information architecture onto the current sample-first public contract, and avoids importing unused mock-only pages or backend terminology into the user-facing experience.

### 11.4 Validation

On **April 11, 2026**, the following Lovable-integration checks passed locally:

| Check | Result |
|-|-|
| `.\.venv\Scripts\python.exe -m unittest tests\api\test_product_routes.py` | Passed, `5` tests |
| `npm test` in `frontend/` | Passed |
| `npm run build` in `frontend/` | Passed |
| `npm run lint` in `frontend/` | Passed |

### 11.5 Week 5 tradeoffs

| Decision | Alternatives considered | Rationale |
|-|-|-|
| Keep Streamlit as the internal tool | Replace Streamlit with React entirely | Preserves the existing debug surface and avoids mixing product UI with backend inspection |
| Add `/product/*` facade instead of calling `/assemble` and `/midi` directly from React | Let the public frontend call engineering routes directly | Keeps frontend code free of backend/debug terminology and stabilizes the future Lovable integration target |
| Make the public UI sample-first | Fake full image-upload transcription before detector integration exists | Keeps the demo honest while still delivering a polished user-facing experience now |
| Integrate only the Lovable routes that match the current backend reality | Copy every generated page and mock workflow verbatim | Avoids shipping unsupported projects/review/processing flows that the backend cannot currently honor |
| Use a separate `frontend/` app | Extend Streamlit for public polish | Better match for Lovable-generated React code and future product iteration |

---

*Last updated: April 11, 2026*
