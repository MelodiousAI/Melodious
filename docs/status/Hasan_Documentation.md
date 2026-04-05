# Hasan's Experiment Documentation - Melodious OMR

> This file tracks the parser, graph, alignment, and integration work on Hasan's side of the project.
> It is intended to mirror Ahmad's documentation style for weekly coordination and handoffs.

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

Aligns detections back to MUSCIMA ground truth using greedy IoU matching. This provides a reusable comparison layer between detector outputs and dataset annotations.

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

**Interpretation:** This run validates the current reference payload path and graph/alignment integration. It is an integration checkpoint, not the final end-to-end project score.

---

## 5. Shared Detector Contract and Export Helper

**Implementation:** `tools/export_muscima_detections.py`

Exports MUSCIMA XML annotations into the shared detector payload contract so backend and graph code can be tested before full model handoff.

| Asset | Status |
|-|-|
| MUSCIMA XML subset for tests | [x] Present |
| Reference payload exports | [x] Present |
| Contract-oriented helper script | [x] Implemented |

---

## 6. Test and Repo Status

| Item | Status |
|-|-|
| `tests/data_prep/test_class_mapping.py` | [x] Present |
| `tests/graph/test_detection_alignment.py` | [x] Present |
| `tests/graph/test_muscima_graph_builder.py` | [x] Present |
| `tests/graph/test_pyg_graph_builder.py` | [x] Present |
| `tests/api/test_api_app.py` | [x] Present |
| `tests/export/test_heuristic_assembler.py` | [x] Present |
| `tests/export/test_musicxml_export.py` | [x] Present |
| Last reported full suite checkpoint | Ran 25 tests, OK |
| Repo cleanup completed | [x] |

The repo has been reorganized into a cleaner structure with `src/api/`, `src/graph/`, `src/data_prep/`, `src/evaluation/`, grouped tests under `tests/`, status docs under `docs/status/`, and generated artifacts separated into `data/processed/`, `sample_detections/`, and `outputs/`.

---

## 7. Backend Service Layer and Export Routes

**Implementations:** `src/api/models.py`, `src/api/service.py`, `src/api/app.py`, `src/export/heuristic_assembler.py`, `src/export/musicxml_export.py`, `docker/Dockerfile.api`, `docker-compose.yml`

The backend now wraps existing graph, alignment, and export logic instead of duplicating it in route handlers.

| Endpoint | Status | Notes |
|-|-|-|
| `GET /health` | [x] Implemented | Returns current backend stage |
| `POST /assemble` | [x] Implemented | Builds graph outputs from one detector payload |
| `POST /midi` | [x] Implemented | Returns inline MusicXML or base64 MIDI from one detector payload |

### 7.1 Current `/assemble` behavior

| Feature | Status |
|-|-|
| Generic detector payload assembly | [x] |
| MUSCIMA reference payload auto-detection | [x] |
| Optional alignment summary | [x] |
| Optional serialized graph arrays in JSON | [x] |
| Serialized node row order matches input detection order | [x] |
| `edge_index` refers to the same serialized node row indices | [x] |
| Request validation through FastAPI/Pydantic | [x] |

### 7.2 Container setup

| File | Purpose |
|-|-|
| `docker/Dockerfile.api` | Builds the backend service image |
| `docker-compose.yml` | Starts the API plus Redis for local development |
| `.dockerignore` | Keeps build context small and avoids copying local clutter |

### 7.3 Week 3 export integration

The Week 3 path reuses only the portable parts of Ahmad's older branch instead of importing the old package layout directly.

| Export asset | Status | Notes |
|-|-|-|
| Heuristic notation assembler | [x] Implemented | Adapted from Ahmad's baseline into `src/export/heuristic_assembler.py` |
| MusicXML renderer | [x] Implemented | Adapted into `src/export/musicxml_export.py` using `music21` |
| MIDI renderer | [x] Implemented | Returns base64 MIDI through `/midi` |
| `/midi` API response contract | [x] Implemented | Includes output metadata, content, and heuristic assembly counts |
| End-to-end API smoke check | [x] Verified | `POST /midi` returned `200` for both `musicxml` and `midi` formats through `TestClient` |

### 7.4 Reuse decision

The current repo now follows a selective adaptation strategy for Ahmad's Week 3 work:

| Candidate from Ahmad's branch | Decision | Rationale |
|-|-|-|
| `melodious/baselines/heuristic_assembler.py` | Reused and adapted | Small, portable, already matches the detector payload contract |
| `melodious/musicxml_export.py` | Reused and adapted | Export logic was portable after moving it behind the current `src/` layout |
| `melodious/cli.py` and `melodious/pipeline.py` | Not integrated yet | Depend on Ahmad's old package layout and detector runtime responsibilities |

---

## 8. Decisions and Tradeoffs

| Decision | Alternatives considered | Rationale |
|-|-|-|
| Separate `muscima_graph_builder.py` from `pyg_graph_builder.py` | One combined graph builder | Reference-data graphs and detector-input graphs serve different stages |
| Keep outputs outside source directories | Mix generated files into source tree | Cleaner repo and easier handoff review |
| Use greedy IoU alignment for initial matching | More complex assignment methods | Simple, testable, and adequate for current integration work |
| Validate with shared MUSCIMA reference payloads | Wait for final model outputs first | Lets backend and graph code progress before model handoffs arrive |
| Wrap existing graph code behind a small FastAPI service layer | Reimplement graph logic inside route handlers | Keeps API work thin and reduces duplication |
| Keep `/midi` as a stable route name from Week 2 into Week 3 | Rename the export route during integration | Preserves the agreed backend entrypoint while adding real export behavior |
| Selectively adapt Ahmad's Week 3 modules | Cherry-pick the old `melodious/` package or reimplement from scratch | Reuses proven logic without undoing the cleaned repo layout |
| Return inline MusicXML/base64 MIDI content from the API | Write export files directly on the server | Keeps the backend stateless and easier to test on shared sample payloads |

---

## 9. Known Issues and Next Work

| Item | Impact | Planned next step |
|-|-|-|
| Ahmad may still need a more specific graph/edge export | Could block GNN training on his side | Confirm exact artifact format and export it |
| Export remains heuristic-only | MusicXML/MIDI quality may be limited on complex notation | Decide whether to feed future GNN relationships into the export stage |
| Real detector payload handoff not wired into this repo yet | Full end-to-end export quality is still pending | Test `/assemble` and `/midi` on Ahmad's real outputs once shared |
| API returns inline content only | Large files or browser download flows may need a different contract later | Decide whether to keep inline responses or add file-oriented endpoints |
| Docker build could not be run on April 5, 2026 | Container image was not runtime-verified after the Week 3 changes | Re-run `docker build` or `docker compose up --build` when Docker Desktop is available |

---

*Last updated: April 5, 2026*
