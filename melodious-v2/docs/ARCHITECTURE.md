# Architecture

## Data Flow

1. User uploads a score image or selects a sample.
2. Detector produces a `DetectorPayloadV2`.
3. Assembly maps full detector classes into semantic roles.
4. Graph or heuristic assembly predicts musical relationships.
5. Export creates MusicXML and MIDI artifacts.
6. API returns artifact links, metrics provenance, warnings, and mode metadata.

## Subsystems

- `contracts`: Pydantic payload and API boundary models.
- `taxonomies`: DeepScores full taxonomy and semantic OMR grouping.
- `metrics`: detector and graph metric implementations.
- `evaluation`: reproducible milestone evaluation pipelines that convert source artifacts into metric records.
- `datasets`: DeepScores conversion and leakage checks.
- `detector`: inference adapters and bootstrap detector.
- `assembly`: relationship inference, checkpoint-gated legacy GNN runtime, and fallback mode resolution.
- `export`: MusicXML/MIDI generation and validation.
- `evaluation.e2e_export`: fixed holdout export evaluation using detector payload fixtures.
- `api`: product service endpoints.
- `reports`: generated metric and experiment report helpers.

## Fallback Policy

Fallbacks are allowed for demo resilience but must be explicit:

- detector fallback: `detector_mode = "heuristic_bootstrap"`;
- assembly fallback: `applied_mode = "heuristic_fallback"`;
- missing GNN checkpoint: `applied_mode = "checkpoint_missing"`;
- unsupported GNN path never reports itself as active GNN inference;
- `applied_mode = "gnn"` is allowed only when a real checkpoint loads and inference runs.

## Current Graph Runtime

- Adapter: `src/melodious_v2/assembly/legacy_gnn.py`.
- Checkpoint source: `..\outputs\gnn_checkpoint.pt`.
- Configuration: set `MELODIOUS_GNN_CHECKPOINT` or pass an explicit checkpoint path.
- Evaluation: `scripts/evaluate_gnn_muscima.py`.
- Current graph run: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.
- Limitation: the legacy model uses a 15-class graph contract and reconstructs the legacy training node encoder from seed `42`.

## Current End-to-End Evaluation

- Evaluator: `scripts/run_e2e_export_eval.py`.
- Reusable code: `src/melodious_v2/evaluation/e2e_export.py`.
- Input split: `runs/data/muscima_graph_manifest/holdout.json`.
- Payload source: MUSCIMA XML-derived detector payload fixtures.
- Current run: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.
- Limitation: this measures export validity and artifact generation, not trained uploaded-image detector quality.
