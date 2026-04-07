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
| Last reported full suite checkpoint | Ran 26 tests, OK |
| Repo cleanup completed | [x] |

The repo uses `src/api/`, `src/graph/`, `src/data_prep/`, `src/evaluation/`, grouped tests under `tests/`, status docs under `docs/status/`, and generated artifacts separated into `data/processed/`, `sample_detections/`, and `outputs/`.

---

## 8. Backend Service Layer and Export Routes

**Implementations:** `src/api/models.py`, `src/api/service.py`, `src/api/app.py`, `src/export/heuristic_assembler.py`, `src/export/musicxml_export.py`, `docker/Dockerfile.api`, `docker-compose.yml`

The backend wraps existing graph, alignment, and export logic instead of duplicating it in route handlers.

| Endpoint | Status | Notes |
|-|-|-|
| `GET /health` | [x] Implemented | Returns current backend stage |
| `POST /assemble` | [x] Implemented | Builds graph outputs from one detector payload |
| `POST /midi` | [x] Implemented | Returns inline MusicXML or base64 MIDI from one detector payload |

### 8.1 Current `/assemble` behavior

| Feature | Status |
|-|-|
| Generic detector payload assembly | [x] |
| MUSCIMA reference payload auto-detection | [x] |
| Optional alignment summary | [x] |
| Optional serialized graph arrays in JSON | [x] |
| Serialized node row order matches input detection order | [x] |
| `edge_index` refers to the same serialized node row indices | [x] |
| Request validation through FastAPI/Pydantic | [x] |

### 8.2 Current `/midi` behavior

| Feature | Status |
|-|-|
| Inline MusicXML response | [x] |
| Inline base64 MIDI response | [x] |
| Heuristic assembly summary in response | [x] |
| Repo-local temp rendering fallback | [x] |

### 8.3 Docker verification

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

### 8.4 Real YOLOv8 payload validation

On **April 7, 2026**, the representative Ahmad payload `lg-101766503886095953-aug-gonville--page-1.json` was validated locally against the current backend.

| Route | Result |
|-|-|
| `POST /assemble` | `200`, `88` detections, `88` nodes, `1266` edges |
| `POST /midi` with `musicxml` | `200` |
| `POST /midi` with `midi` | `200` |

This confirmed that Ahmad's real YOLOv8 output matches the current detector payload contract and that the backend export route accepts it directly.

### 8.5 Reuse decision

The current repo follows a selective adaptation strategy for Ahmad's Week 3 work:

| Candidate from Ahmad's branch | Decision | Rationale |
|-|-|-|
| `melodious/baselines/heuristic_assembler.py` | Reused and adapted | Small, portable, already matches the detector payload contract |
| `melodious/musicxml_export.py` | Reused and adapted | Export logic was portable after moving it behind the current `src/` layout |
| `melodious/cli.py` and `melodious/pipeline.py` | Not integrated | Depend on Ahmad's old package layout and detector runtime responsibilities |

---

## 9. Decisions and Tradeoffs

| Decision | Alternatives considered | Rationale |
|-|-|-|
| Separate `muscima_graph_builder.py` from `pyg_graph_builder.py` | One combined graph builder | Reference-data graphs and detector-input graphs serve different stages |
| Keep outputs outside source directories | Mix generated files into source tree | Cleaner repo and easier handoff review |
| Use greedy IoU alignment for initial matching | More complex assignment methods | Simple, testable, and adequate for current integration work |
| Validate with shared MUSCIMA reference payloads first | Wait for final model outputs first | Lets backend and graph code progress before model handoffs arrive |
| Wrap existing graph code behind a small FastAPI service layer | Reimplement graph logic inside route handlers | Keeps API work thin and reduces duplication |
| Keep `/midi` as a stable route name from Week 2 into Week 3 | Rename the export route during integration | Preserves the agreed backend entrypoint while adding real export behavior |
| Selectively adapt Ahmad's Week 3 modules | Cherry-pick the old `melodious/` package or reimplement from scratch | Reuses proven logic without undoing the cleaned repo layout |
| Return inline MusicXML/base64 MIDI content from the API | Write export files directly on the server | Keeps the backend stateless and easier to test on shared sample payloads |
| Export one record per directed candidate-edge type | Collapse all candidate types for a node pair into one record | Keeps `edge_type` unambiguous and matches Ahmad's request that it be a separate input feature |
| Use the reduced shared detector taxonomy for training-export nodes | Export all 115 MUSCIMA classes directly | Keeps training artifacts aligned with the existing detector/backend contract |
| Derive `slur_phrase` and `tie_sustained` between noteheads through shared connector nodes | Require explicit slur/tie nodes in the reduced export | Preserves the requested supervision labels without expanding the node taxonomy beyond the shared detector set |

---

## 10. Known Issues and Next Work

| Item | Impact | Planned next step |
|-|-|-|
| Export remains heuristic-only | MusicXML/MIDI quality may be limited on complex notation | Decide whether to feed future GNN relationships into the export stage |
| Ahmad still needs to load the generated training exports on his side | Could reveal minor schema adjustments still needed for his trainer | Hand off one sample page JSON first, then the full directory if accepted |
| API returns inline content only | Large files or browser download flows may need a different contract later | Decide whether to keep inline responses or add file-oriented endpoints |
| `docker compose up --build` on host port `8000` can still fail locally | An unrelated local container may already own port `8000` | Change the compose host port or stop the conflicting local service when needed |

---

*Last updated: April 7, 2026*
