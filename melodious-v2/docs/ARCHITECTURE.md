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
- `assembly`: relationship inference and fallback mode resolution.
- `export`: MusicXML/MIDI generation and validation.
- `api`: product service endpoints.
- `reports`: generated metric and experiment report helpers.

## Fallback Policy

Fallbacks are allowed for demo resilience but must be explicit:

- detector fallback: `detector_mode = "heuristic_bootstrap"`;
- assembly fallback: `applied_mode = "heuristic_fallback"`;
- unsupported GNN path never reports itself as active GNN inference.
