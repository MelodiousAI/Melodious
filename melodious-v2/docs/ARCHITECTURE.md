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
- `omr`: local clean-sheet note extraction helpers that combine detector
  notehead boxes with staff geometry and write demo MIDI/MusicXML artifacts.
- `api`: product service endpoints.
- `deployment`: local/public smoke-test helpers for the API deployment contract.
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

## Local Note Extraction Demo

- CLI: `scripts/extract_notes_from_image.py`.
- Reusable code: `src/melodious_v2/omr/note_extraction.py`.
- Primary mode: `yolo_notehead_staff_pitch`.
- Fallback mode: `cv_staff_notehead_pitch`.
- Purpose: local testing of clean sheet image note extraction before the
  FastAPI upload path is rewired away from `heuristic_bootstrap`.
- Output artifacts: note JSON, overlay PNG, compact MusicXML, and playable MIDI
  with actual note events.
- Current Sad Romance verification output:
  `runs/demo/sad_romance_note_extraction_v1/`.
- Verification summary: 9 detected staff systems, 197 note events, and a
  1,809-byte MIDI file with `MThd` header.
- Limitation: pitch assumes treble clef; rhythm is heuristic; accidentals,
  ties, slurs, beams, measures, and full graph assembly are not reconstructed.

## Deployment Architecture

- Backend image: `infra/docker/Dockerfile.api`.
- Backend target: ECS Express Mode or ECS Fargate with an ECR image and one CPU task for the public demo.
- Frontend target: static Vite build on S3 behind CloudFront.
- CORS: API origins are controlled by `MELODIOUS_CORS_ORIGINS`; local defaults remain `http://localhost:5173` and `http://127.0.0.1:5173`.
- Graph checkpoint: `MELODIOUS_GNN_CHECKPOINT` must point to a private checkpoint path inside the container or mounted storage; otherwise the API reports fallback metadata.
- Smoke contract: `scripts/smoke_public_demo.py` verifies `/health`, `/version`, sample transcription, MusicXML download, and MIDI download.
- Deployment runbook: `infra/aws/README.md`.
- Current deployment blocker: public AWS smoke has not run because AWS CLI and account-local resource values are unavailable in this workspace.
