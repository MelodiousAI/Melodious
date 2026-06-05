# Melodious V2

Melodious V2 is a clean rebuild of the original OMR project. It targets a full-grade applied/deployment project: full-taxonomy detection, measured graph assembly, real upload-to-export service behavior, and cloud-ready deployment.

## What Is New

- Full DeepScores 136-class taxonomy support instead of a fixed 15-class-only detector.
- Strict metric registry so `mAP`, `F1`, precision, and recall are never mixed.
- Versioned detector payload contract with taxonomy, run id, model id, and artifact hash provenance.
- FastAPI product service with sample and upload transcription routes.
- Checkpoint-gated legacy GNN assembly runtime with explicit fallback metadata.
- Local YOLO-backed clean-sheet note extraction demo script for testing actual
  note events and playable MIDI before the upload API is fully rewired.
- AWS ECS/Fargate deployment templates instead of local-only demo claims.
- Governance docs from day one: metrics, data card, experiments, rubric map, status, model card, and agent rules.

## Layout

- `src/melodious_v2/`: Python package.
- `configs/`: detector, graph, and deployment configs.
- `scripts/`: CLI helpers for data conversion, reports, and API startup.
- `tests/`: contract, metric, dataset, API, and export tests.
- `frontend/`: React/Vite upload and results UI.
- `infra/`: Docker and AWS deployment scaffolding.
- `docs/`: canonical documentation.
- `runs/`, `artifacts/`, `outputs/`, `data/`, `checkpoints/`: generated and ignored.

## Project Plan

- `docs/ROADMAP.md`: milestone plan, acceptance criteria, tracking rules, and weekly operating rhythm.
- `docs/STATUS.md`: current active milestone, blockers, and immediate next actions.
- `docs/AGENT_PROMPTS.md`: copy-paste prompts for coding agents.
- `docs/HANDOFF.md`: where each agent records progress and the next exact step.
- `docs/MILESTONE_HISTORY.md`: detailed milestone evidence ledger from M1 onward, including future milestone checklists.
- `docs/EXPERIMENTS.md`: generated index of run artifacts.
- `docs/RUBRIC_MAP.md`: rubric evidence map for grading.

## Local Setup

```powershell
cd melodious-v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run Tests

```powershell
python -m pytest
```

Without `pytest`:

```powershell
$env:PYTHONPATH="src"
python -m unittest discover tests
```

## Run API

```powershell
$env:PYTHONPATH="src"
python scripts/run_api.py
```

Open `http://127.0.0.1:8000/health`.

## Run Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects `VITE_API_BASE_URL=http://127.0.0.1:8000` by default.

## Detection Training Path

1. Reproduce the legacy 15-class baseline. Done for the M2 sample run under `runs/detection/detection_15class_repro_sample_v1/`.
2. Convert DeepScores to a 136-class YOLO dataset with fixed manifests.
3. Materialize the M1 manifest into a YOLO-standard ignored dataset under `runs/data/deepscores_136_yolo_materialized/`.
4. Train the full-class detector with validation-only threshold selection. Done for the full configured YOLOv8m run under `runs/detection/detection_136class_yolov8m_v1/`; it completed 150 epochs, selected `best.pt`, wrote V2 `metrics.json`, exported `best.onnx`, and copied artifact metadata to `artifacts/models/detection_136class_yolov8m_v1/`.
5. Evaluate with `mAP@0.5:0.95` as the primary detector metric.
6. Improve inference configuration only through validation-provenance runs. Current best primary validation inference run: `runs/detection/detection_136class_yolov8m_eval_img1472_maxdet2000_v1/metrics.json`, with `mAP@0.5:0.95 = 0.6204968163150985`. Current best secondary `mAP@0.5` validation run: `runs/detection/detection_136class_yolov8m_eval_img1536_maxdet2000_v1/metrics.json`, with `mAP@0.5 = 0.7920129156176505`.
7. Audit class coverage before claiming full-taxonomy quality. Current audit: `runs/detection/detection_136class_class_coverage_audit_v1/`; the model head has 136 classes, local labels support 115 classes across train/validation/test, and validation measures 103 classes.
8. Fine-tune with generated metric provenance. Completed run `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/metrics.json` reaches `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271`.
9. The completed follow-up fine-tune `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/metrics.json`, finalized with `imgsz=1536` and `max_det=2000`, has separate `F1@0.5 = 0.8318461933668392`. Its AP metrics are `mAP@0.5:0.95 = 0.707986237382828` and `mAP@0.5 = 0.8390674529615662`.
10. The `stem` class remains `0.0` AP after whole-page fine-tuning, so rhythm detection is still not solved.
11. Use the tiled thin-symbol path for stem improvement instead of blindly adding whole-page epochs. The tiled materializer is `scripts/materialize_tiled_yolo_dataset.py`; the runner can train from an existing tiled dataset with `scripts/run_detection_136class_yolo.py --dataset-yaml ... --dataset-id ...`.
12. The full tiled dataset is `runs/data/deepscores_136_yolo_tiled_stem_v1/`. It contains 88137 train tiles, 10709 validation tiles, 26019 test tiles, and 747473 retained stem labels across all splits.
13. The no-copy tiled pilot `detection_136class_yolov8m_tiled_stem_pilot_img1024_v1`, using `runs/data/deepscores_136_yolo_tiled_stem_pilot_v1/` with 12000 train, 2500 validation, and 2500 test tile paths, completed all 12 epochs and wrote `runs/detection/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/metrics.json`. On tiled validation it reaches AP metrics `mAP@0.5:0.95 = 0.8521207647641077` and `mAP@0.5 = 0.9082394885392849`.
    It also reaches `F1@0.5 = 0.8893154628249349` and `stem = 0.7345783859762263` mAP@0.5:0.95. This is tiled-validation pilot evidence, not original full-page validation evidence.
14. Store every run under `runs/detection/{run_id}/` with config, metrics JSON, plots, and artifact hashes.

## Graph Assembly Path

1. Load the legacy MUSCIMA GNN checkpoint from `..\outputs\gnn_checkpoint.pt` through `MELODIOUS_GNN_CHECKPOINT`.
2. Convert detector payloads into the legacy 15-class graph feature contract.
3. Return `applied_mode = "gnn"` only when checkpoint inference runs; missing or failed checkpoints return explicit fallback metadata.
4. Evaluate graph relationships with positive-class macro F1 on the natural candidate-edge distribution.
5. Current graph run: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.

## End-to-End Export Evaluation

1. Use the fixed MUSCIMA holdout split from `runs/data/muscima_graph_manifest/holdout.json`.
2. Build detector-like payload fixtures from MUSCIMA XML annotations.
3. Run assembly through the V2 assembly service.
4. Export MusicXML, MIDI, detector payload JSON, and relationship JSON artifacts.
5. Current end-to-end run: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.
6. Scope caveat: this measures export validity from XML-derived payload fixtures, not trained uploaded-image detector quality.

## Local Note Extraction Demo

The FastAPI uploaded-image route still reports `detector_mode = "heuristic_bootstrap"`.
For testing a clean sheet image with the trained detector checkpoint right now,
use the separate CLI demo path documented in `docs/NOTE_EXTRACTION_DEMO.md`.
When `--checkpoint` is omitted, the CLI uses the saved local full-page demo
checkpoint at `artifacts/models/note_extraction_default_fullpage/best.pt` if it
exists. That generated artifact is copied from the completed 1472 full-page
fine-tune checkpoint and is ignored by git like other model files.
When the saved tiled stem pilot checkpoint exists at
`artifacts/models/note_extraction_tiled_stem_pilot/best.pt`, the same CLI also
runs overlapping tiled inference for stems, beams, flags, and explicit
accidentals. When `..\outputs\gnn_checkpoint.pt` exists, it runs relationship
assembly and uses GNN `stem_notehead` / `beam_notegroup` relationships as rhythm
evidence before writing MusicXML. Tiled augmentation-dot detections are off by
default to avoid false dotted notes.

Example:

```powershell
$env:PYTHONPATH="src"
python scripts/extract_notes_from_image.py `
  --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png `
  --output-dir runs\demo\sad_romance_note_extraction_v3 `
  --device cpu `
  --conf 0.12 `
  --imgsz 1472 `
  --max-det 2000 `
  --default-quarter-length 1.0 `
  --title "Sad Romance"
```

This writes `*_notes.json`, `*_notes_overlay.png`, `*_notes.musicxml`, and
`*_notes.mid`. When GNN assembly runs, it also writes
`*_detector_payload.json` and `*_relationships.json`.

The latest default-checkpoint Sad Romance verification run under
`runs/demo/sad_romance_default_fullpage_20260605/` used
`extractor_mode = yolo_notehead_staff_pitch`, detected 9 staff systems, wrote
197 note events, inferred 3 detector-confirmed dotted notes, and produced
MusicXML with 3 `<dot/>` tags. The same run had 0 stem-confirmed notes because
the default full-page demo checkpoint did not return usable `stem` boxes on that
page. This is a demo
extraction artifact, not an evaluation metric.

The uploaded Arabic page check for
`C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png` is recorded
under `runs/demo/image_note_extraction_v5/`. After the light-staff detector and
key-signature fixes, it detected 9 staff systems, wrote 319 note events, inferred
38 dotted notes, detected `B: -1` key signatures on all 9 systems, produced
MusicXML with `<fifths>-1</fifths>` and 53 `<alter>-1</alter>` tags, and wrote a
2879-byte MIDI file. It still had 0 stem-confirmed notes, so rhythm quality is
limited by missing `stem` detections and the demo's fallback rhythm rules.
The newer `runs/demo/image_note_extraction_v6/` artifact disables CV
augmentation-dot guessing for YOLO-backed extraction; it keeps the same 319 note
events and key-signature behavior, but reduces dotted notes from 38 to 7 and
writes a 2871-byte MIDI file.

The latest Fur Elise local demo run with tiled stem inference and GNN rhythm
evidence is `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/`. Compared
with the staff-fixed full-page run, it keeps 9 staff systems and 256 note events,
keeps dotted notes at 3, and improves stem-confirmed notes from 0 to 171. It
writes MusicXML at
`runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/image(305)_notes.musicxml`.
This is a local demo transcription improvement, not an official detector metric
claim.

## Deployment Path

Backend deployment targets Dockerized FastAPI + CPU inference on ECS Express Mode or ECS Fargate with images in ECR. The frontend deploys to S3 + CloudFront. See `infra/aws/README.md` for the M6 runbook, public smoke commands, CORS configuration, `MELODIOUS_GNN_CHECKPOINT` guidance, and scale-to-zero shutdown steps.

Local deployment smoke:

```powershell
$env:PYTHONPATH="src"
python scripts/smoke_public_demo.py --local-testclient --output runs\deploy\m6_local_smoke\smoke.json
```

Public deployment smoke after AWS deploy:

```powershell
$env:PYTHONPATH="src"
python scripts/smoke_public_demo.py --api-base-url https://REPLACE_WITH_PUBLIC_API_HOST --output runs\deploy\m6_public_smoke\smoke.json
```

Current M6 status: deployment path and local smoke tooling are ready, but actual AWS public smoke is blocked until AWS CLI access and account-local ECS/ECR/S3/CloudFront values are provided. Uploaded images remain labeled `heuristic_bootstrap`.

## Current Status

This implementation provides the clean project foundation, strict contracts, metric code, M1 data manifests, M2 reduced-class metric reproduction, M3 full-taxonomy detector artifacts, M4 real graph assembly runtime, M5 end-to-end export evaluation, M6 deployment runbook/smoke tooling, M7 detector metric-improvement evidence, upload/sample API, frontend, tests, deployment templates, and a separate local note-extraction demo CLI. The full configured 136-class YOLOv8m run has generated metric provenance under `runs/detection/detection_136class_yolov8m_v1/` and model artifacts under `artifacts/models/detection_136class_yolov8m_v1/`. The current best completed original full-page detector is `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`, with separate validation `F1@0.5 = 0.8318461933668392`. Its validation AP metrics are `mAP@0.5:0.95 = 0.707986237382828` and `mAP@0.5 = 0.8390674529615662`. The current class-coverage audit is `detection_136class_class_coverage_audit_v1` and should be read before making all-136-class claims. The completed stem-specific tiled pilot is `detection_136class_yolov8m_tiled_stem_pilot_img1024_v1`, launched from the corrected v2 `best.pt` over sampled tile lists under `runs/data/deepscores_136_yolo_tiled_stem_pilot_v1/`; it writes metric provenance under `runs/detection/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/metrics.json` and improves tiled-validation `stem` to `0.7345783859762263`. The full tiled dataset exists under `runs/data/deepscores_136_yolo_tiled_stem_v1/`. The local demo CLI now combines full-page notehead detection, tiled thin-symbol inference, and GNN relationship-aware rhythm when local checkpoints are present; Fur Elise evidence is under `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/`. The legacy GNN assembly run has generated metric provenance under `runs/graph/graph_legacy_gnn_muscima_val_v1/`. The end-to-end export run has generated metric provenance under `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/`. The Sad Romance local note-extraction demo artifact is under `runs/demo/sad_romance_note_extraction_v3/`; the uploaded Arabic page local note-extraction demo artifact is under `runs/demo/image_note_extraction_v6/`; both are documented in `docs/NOTE_EXTRACTION_DEMO.md`.

Current active milestone: M7 - Detector Metric Improvement. See `docs/METRIC_IMPROVEMENT.md`, `docs/ROADMAP.md`, and `docs/MILESTONE_HISTORY.md` before starting new implementation work.
