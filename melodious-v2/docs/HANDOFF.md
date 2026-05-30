# Agent Handoff Log

Use this file at the end of every coding-agent session. The next agent must read it before coding.

## Current Handoff

Active milestone: M4 - Real Assembly Runtime is active. M1 - Dataset Manifests, M2 - Metric Reproduction, and M3 - Full 136-Class Detector are complete enough to hand off. The full configured YOLOv8m detector run `detection_136class_yolov8m_v1` completed 150 epochs, was finalized from `best.pt`, wrote project-standard V2 artifacts, exported ONNX, copied model metadata, and regenerated `docs/EXPERIMENTS.md`.

Current state:

- V2 foundation is implemented.
- Python tests pass.
- Frontend build passed in the previous implementation session.
- Detector payload JSON Schema exists at `docs/detector_payload_v2.schema.json`.
- DeepScores 136-class manifests exist locally under `runs/data/deepscores_136_manifest/`.
- MUSCIMA graph manifests exist locally under `runs/data/muscima_graph_manifest/`.
- DeepScores duplicate image-id and filename leakage checks passed.
- DeepScores inferred work-group leakage check is a warning with 202 repeated filename-inferred groups.
- MUSCIMA duplicate page-id leakage check passed.
- M2 reduced-class metric reproduction exists locally under `runs/detection/detection_15class_repro_sample_v1/`.
- `docs/EXPERIMENTS.md` was regenerated from `runs/**/metrics.json`.
- M3 materialized YOLO dataset exists under `runs/data/deepscores_136_yolo_materialized/`.
- M3 smoke run exists under `runs/detection/detection_136class_yolov8s_smoke_v1/`.
- M3 smoke model artifacts exist under `artifacts/models/detection_136class_yolov8s_smoke_v1/`.
- M3 full YOLOv8m run exists under `runs/detection/detection_136class_yolov8m_v1/`.
- M3 full YOLOv8m model artifacts exist under `artifacts/models/detection_136class_yolov8m_v1/`.
- Detailed milestone ledger exists at `docs/MILESTONE_HISTORY.md`.
- `yolov8m.pt` exists in the V2 workspace and is ignored by `.gitignore`.
- Full YOLOv8m training was first saved after epoch 20 completed and stopped during epoch 21.
- First manual recovery checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/`.
- Full YOLOv8m training was resumed from the epoch-20 manual checkpoint on 2026-05-21.
- The resumed run reached a clean completed epoch 74 before the user requested another save/stop.
- Previous manual recovery checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/`.
- The copied epoch-74 `last.pt` loaded successfully with Ultralytics: `task=detect`, `class_count=136`, first class `brace`, last class `ottavaBracket`.
- The epoch-74 manual checkpoint metadata JSON validates with `python -m json.tool` and includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- A post-stop process check showed no Python training process after stopping parent PID `30204` and child PIDs `35140` and `36816`.
- Full YOLOv8m training was resumed again from the epoch-74 checkpoint on 2026-05-22.
- The resumed run reached a clean completed epoch 95 before the user requested another save/stop.
- Current manual recovery checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/`.
- Current manual recovery checkpoint files: `last.pt`, `best.pt`, `results.csv`, `args.yaml`, `resume_epoch74_train_stdout.log`, `resume_epoch74_train_stderr.log`, `resume_epoch74_train.pid`, `metadata.json`, and `README.md`.
- The copied epoch-95 `last.pt` loaded successfully with Ultralytics: `task=detect`, `class_count=136`, first class `brace`, last class `ottavaBracket`.
- The epoch-95 manual checkpoint metadata JSON validates with `python -m json.tool` and includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- A post-stop process check showed no Python training process after stopping the live training wrapper and Python trainer.
- Full YOLOv8m training was resumed again from the epoch-95 checkpoint on 2026-05-26.
- Current resume PID file: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train.pid`, containing PID `30436` when launched.
- Current resume stdout log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stdout.log`.
- Current resume stderr log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stderr.log`.
- Current resume log evidence: Ultralytics reports `Resuming training ... from epoch 96 to 150 total epochs`, and epoch `96/150` is active.
- Full YOLOv8m training reached a clean completed epoch 124, then was found not running on 2026-05-28.
- Full YOLOv8m training was resumed again from the latest run checkpoint `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/last.pt` on 2026-05-28.
- Resume PID file: `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train.pid`, containing PID `24516` when launched.
- Resume stdout log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train_stdout.log`.
- Resume stderr log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train_stderr.log`.
- Resume log evidence: Ultralytics reports `Resuming training ... from epoch 125 to 150 total epochs`; the log later reaches epoch 150/150 and final validation output.
- Final selected checkpoint: `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`.
- Final V2 metrics: `runs/detection/detection_136class_yolov8m_v1/metrics.json`.
- Final V2 analysis: `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- Final ONNX parity: `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`.
- Final model metadata: `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.
- Full detector primary validation metric: `mAP@0.5:0.95` 0.4747370751116288.
- Full detector secondary validation metrics: `mAP@0.5` 0.5853211368313491, precision 0.8274236461250144, and recall 0.4909790740632496.
- Full detector secondary F1: `F1@0.5` 0.6162725385980492.
- Detector limitation evidence: 16 supported validation classes still have zero mAP, including `ledgerLine`, `stem`, and `ottavaBracket`.
- ONNX parity passed on one fixed validation image; PyTorch and ONNX both returned 300 boxes with identical class-count totals.
- M1 was re-verified on 2026-05-12 in this workspace. The manifest CLI completed against the local parent datasets and refreshed ignored `runs/data/` artifacts.
- `docs/AGENT_PROMPTS.md` now says the current active milestone is M4.

Next exact prompt:

- Use the active M4 prompt in `docs/AGENT_PROMPTS.md`.

Next exact implementation target:

1. Start M4 from the active prompt in `docs/AGENT_PROMPTS.md`.
2. Search the V2 repo and read-only parent workspace for an existing GNN/relationship checkpoint and graph feature contract.
3. Implement or wire the real assembly adapter under `src/melodious_v2/assembly/`.
4. Evaluate graph assembly on the fixed MUSCIMA graph manifest and write `runs/graph/{run_id}/metrics.json`.
5. Keep `no_relation` metrics separate and report positive-class macro F1 as the graph primary metric.
6. Add API mode tests so `applied_mode = "gnn"` is only returned when real checkpoint inference runs.
7. Optionally wire `artifacts/models/detection_136class_yolov8m_v1/best.onnx` into a non-bootstrap detector adapter; keep `heuristic_bootstrap` explicit until tested.

## 2026-05-30 - Agent Handoff - M3 Finalized and M4 Activated

Milestone worked:

- M3 - Full 136-Class Detector finalization
- M4 - Real Assembly Runtime handoff preparation

Files changed:

- `scripts/run_detection_136class_yolo.py`
- `src/melodious_v2/evaluation/full_detector.py`
- `tests/test_full_detector_m3.py`
- `README.md`
- `MODEL_CARD.md`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`

Commands run:

- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train.pid)` - returned no live process; training wrapper was no longer running.
- `Get-Content -Tail 120 runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train_stdout.log` - passed; stdout reached epoch 150/150 and final Ultralytics validation output.
- `Import-Csv runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; 150 completed rows, best CSV row by `mAP@0.5:0.95` was epoch 125 and final row was epoch 150.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py` - passed, 4 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 25 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py src\melodious_v2\evaluation\full_detector.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --finalize-existing-run --workers 0 --device 0` - passed; evaluated existing `best.pt`, exported ONNX, copied artifacts, wrote metrics/report/manifest/artifacts/analysis, and wrote ONNX parity evidence without retraining.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed; experiment index now includes `detection_136class_yolov8m_v1`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed; checked 12 documentation files.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json`
- `runs/detection/detection_136class_yolov8m_v1/report.md`
- `runs/detection/detection_136class_yolov8m_v1/manifest.json`
- `runs/detection/detection_136class_yolov8m_v1/artifacts.json`
- `runs/detection/detection_136class_yolov8m_v1/analysis.json`
- `runs/detection/detection_136class_yolov8m_v1/analysis.md`
- `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`
- `runs/detection/detection_136class_yolov8m_v1/config.yaml`
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.onnx`
- `artifacts/models/detection_136class_yolov8m_v1/best.pt`
- `artifacts/models/detection_136class_yolov8m_v1/best.onnx`
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json`

What is complete:

- The full configured YOLOv8m run completed all 150 epochs.
- A finalize-only mode now exists for CLI-resumed Ultralytics runs.
- `detection_136class_yolov8m_v1` has project-standard V2 metrics, report, manifest, artifacts, copied config, analysis, ONNX parity, and model metadata.
- `docs/EXPERIMENTS.md` includes the full YOLOv8m run.
- `docs/AGENT_PROMPTS.md` now points the next agent to M4.

Final detector metrics:

- Primary `mAP@0.5:0.95`: 0.4747370751116288.
- `mAP@0.5`: 0.5853211368313491.
- `precision@0.5`: 0.8274236461250144.
- `recall@0.5`: 0.4909790740632496.
- `F1@0.5`: 0.6162725385980492.

Important limitations:

- These are validation metrics, not final test metrics.
- 16 supported validation classes have zero mAP.
- `ledgerLine` and `stem` remain major detector failure classes despite high support.
- API upload inference still uses `heuristic_bootstrap`; the ONNX artifact is not wired into a non-bootstrap detector adapter yet.
- Local ONNX prediction fell back to CPU because `onnxruntime-gpu` is not installed.

What failed:

- The ONNX parity run triggered Ultralytics auto-install attempts for `onnxruntime-gpu`; those attempts failed, then ONNX Runtime CPU fallback succeeded.
- No blocking failure for M3 finalization.

Next exact step:

- Start M4 with the active prompt in `docs/AGENT_PROMPTS.md`. Search for a real GNN/relationship checkpoint, implement the V2 assembly adapter, evaluate on the fixed MUSCIMA graph manifest, write `runs/graph/{run_id}/metrics.json`, and keep `no_relation` separate from positive-class macro F1.

## 2026-05-28 - Agent Handoff - M3 Training Resumed from Epoch 124

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/HANDOFF.md`
- `docs/STATUS.md`

Commands run:

- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train.pid)` - returned no live process; the previous wrapper PID was no longer running.
- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - returned no live Python process; no active trainer was running.
- `Get-Content -Tail 10 runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; latest completed row was epoch 124.
- `Get-Item runs\detection\detection_136class_yolov8m_v1\ultralytics\train\weights\last.pt` - passed; `last.pt` was updated after the epoch-124 result.
- Escalated hidden `Start-Process` resume launch - passed; resumed YOLO training from `runs\detection\detection_136class_yolov8m_v1\ultralytics\train\weights\last.pt`.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train.pid` - passed; PID file contained `24516`.
- `Get-Content -Tail 100 runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train_stdout.log` - passed; showed the latest run checkpoint path, YOLOv8m configuration, `nc=136`, `epochs=150`, `imgsz=1024`, `batch=4`, and `Resuming training ... from epoch 125 to 150 total epochs`.
- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train.pid)` - passed; parent PowerShell PID `24516` was running.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train_stderr.log`

What is complete:

- Training has resumed from the latest run checkpoint after epoch 124 completed.
- Ultralytics confirmed the resumed schedule is epoch 125 through 150.
- The resumed process is running as a hidden background process with PID `24516`.
- Resume logs and PID file are recorded under the existing full-run directory.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- Nothing blocking. The previous resume process was no longer running, so the run was resumed from `ultralytics/train/weights/last.pt`.

Next exact step:

- Monitor training:
  `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train_stdout.log`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-26 - Agent Handoff - M3 Training Resumed from Epoch 95

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed before resume; showed two low-CPU Python processes, not an active high-CPU training run.
- `Get-ChildItem artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22` - passed; confirmed `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, PID file, README, and metadata existed.
- `python -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22\metadata.json` - passed; checkpoint metadata is strict JSON and records `last_completed_epoch = 95`.
- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed; returned `False`, confirming M3 was still incomplete before resume.
- Escalated hidden `Start-Process` resume launch - passed; resumed YOLO training from `artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22\last.pt`.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train.pid` - passed; PID file contained `30436`.
- `Get-Content -Tail 120 runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train_stdout.log` - passed; showed the epoch-95 checkpoint path, YOLOv8m configuration, `nc=136`, `epochs=150`, `imgsz=1024`, `batch=4`, and `Resuming training ... from epoch 96 to 150 total epochs`.
- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train.pid)` - passed; parent PowerShell PID `30436` was running.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe -m unittest discover tests` - passed after resume documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after resume documentation updates, checked 12 documentation files.
- Final live progress check - passed; PID `30436` was still running and stdout showed epoch `96/150` around batch `174/307`.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stderr.log`

What is complete:

- Training has resumed from the exact load-verified epoch-95 checkpoint.
- Ultralytics confirmed the resumed schedule is epoch 96 through 150.
- The resumed process is running as a hidden background process with PID `30436`.
- Resume logs and PID file are recorded under the existing full-run directory.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- `Get-CimInstance Win32_Process` failed with access denied while trying to inspect low-CPU Python command lines. This did not block resume because no high-CPU training process or final metrics were present.

Next exact step:

- Monitor training:
  `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train_stdout.log`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-22 - Agent Handoff - M3 Training Saved and Stopped at Epoch 95

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/README.md`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train.pid)` - passed before stop; parent PowerShell PID `14020` was running.
- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed before stop; Python training PIDs included `6096` and `21260`.
- `Get-Content -Tail 20 runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train_stdout.log` - passed; showed active epoch `96/150`.
- `Get-Content -Tail 3 runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; latest completed row was epoch 95.
- Checkpoint copy to `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/` - passed; copied `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, and PID file.
- Ultralytics load verification for copied `last.pt` - passed; printed `loaded=True`, `class_count=136`, `task=detect`, `first_class=brace`, and `last_class=ottavaBracket`. Ultralytics also printed non-blocking AppData settings/cache permission warnings.
- Stop command for parent PID `14020` and Python PIDs `6096`, `21260` - passed; one remaining Python process disappeared before the follow-up escalated stop could act on it.
- Post-stop process check - passed; no Python training process remained.
- Final checkpoint refresh after stop - passed; refreshed copied checkpoint/log files.
- Hash generation for copied artifacts - passed after splitting the large checkpoint hash step from an earlier metadata script that timed out.
- Strict JSON validation for `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json` - passed.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe -m unittest discover tests` - passed after documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after documentation updates, checked 12 documentation files.
- Final Python process check after verification commands exited - passed; no Python process remained.

Generated artifacts:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/last.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/best.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/results.csv`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/args.yaml`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/resume_epoch74_train_stdout.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/resume_epoch74_train_stderr.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/resume_epoch74_train.pid`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/README.md`

What is complete:

- The resumed YOLOv8m run was saved without discarding completed progress.
- The clean recovery point is the epoch-95 `last.pt` checkpoint.
- The copied checkpoint is loadable through Ultralytics and preserves the 136-class detection head.
- Manual checkpoint metadata includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- Training was stopped after load verification, and no Python training process remains.
- Documentation now points the next agent to the epoch-95 stopped-checkpoint state, not a live process.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- Two attempts to write metadata and hash all artifacts in one PowerShell script timed out. Hashing was split out, passed, and the final metadata JSON validates.
- PID `14020` was later observed reused by a Chrome process after the training wrapper stopped. Stop verification therefore relies on no remaining Python training process and not on PID reuse alone.

Next exact step:

- Resume from the saved checkpoint when training should continue:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\yolo.exe detect train resume=True model=.\artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22\last.pt`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-22 - Agent Handoff - M3 Training Resumed from Epoch 74

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed before resume; showed no active Python process.
- `Get-ChildItem artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch74_stop_2026-05-22` - passed; confirmed `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, PID file, README, and metadata existed.
- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed; returned `False`, confirming M3 was still incomplete before resume.
- `python -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch74_stop_2026-05-22\metadata.json` - passed; checkpoint metadata is strict JSON.
- Escalated hidden `Start-Process` resume launch - passed; resumed YOLO training from `artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch74_stop_2026-05-22\last.pt`.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train.pid` - passed; PID file contained `14020`.
- `Get-Content -Tail 100 runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train_stdout.log` - passed; showed the epoch-74 checkpoint path, YOLOv8m configuration, `nc=136`, `epochs=150`, `imgsz=1024`, `batch=4`, and `Resuming training ... from epoch 75 to 150 total epochs`.
- `Get-Content -Tail 40 runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train_stderr.log` - passed; log was empty during the resume check.
- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train.pid)` - passed; parent PowerShell PID `14020` was running.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe -m unittest discover tests` - passed after resume documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after resume documentation updates, checked 12 documentation files.
- Final live progress check - passed; PID `14020` was still running, stderr remained empty, and stdout showed epoch `75/150` around batch `186/307`.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train_stderr.log`

What is complete:

- Training has resumed from the exact load-verified epoch-74 checkpoint.
- Ultralytics confirmed the resumed schedule is epoch 75 through 150.
- The resumed process is running as a hidden background process with PID `14020`.
- Resume logs and PID file are recorded under the existing full-run directory.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- Three parallel checkpoint file probes initially hit a Windows sandbox `CreateProcessWithLogonW failed: 1056` issue. Sequential reruns passed and did not block the resume.

Next exact step:

- Monitor training:
  `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train_stdout.log`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-22 - Agent Handoff - M3 Training Saved and Stopped at Epoch 74

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/README.md`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/metadata.json`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- Training progress check - passed; `resume_train_stdout.log` showed epoch `74/150` completing and epoch `75/150` starting while the save/stop work was being prepared.
- Checkpoint copy to `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/` - passed; copied `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, and PID file.
- Ultralytics load verification for copied `last.pt` - passed; printed `loaded=True`, `class_count=136`, `task=detect`, `first_class=brace`, and `last_class=ottavaBracket`.
- Metadata generation for the epoch-74 checkpoint - passed after correcting a PowerShell `Add-Member` update issue.
- Stop command for parent PID `30204` and child PIDs `35140`, `36816` - passed after load verification.
- Post-stop process check - passed; no Python training process remained.
- Final checkpoint refresh after stop - passed; refreshed copied checkpoint/log files and rebuilt metadata with final hashes and stop verification.
- Strict JSON validation for `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/metadata.json` - passed.
- Checkpoint README correction and metadata README-hash refresh - passed; resume command now includes `$env:PYTHONPATH='src'`, and metadata records README SHA256 `539e110131972ecf8e1c364888e874c1151ed344e9cf087a2ced0cf5b8959567`.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe -m unittest discover tests` - passed after documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after documentation updates, checked 12 documentation files.
- First parallel post-verification process check showed only the verification Python interpreters because it ran concurrently with tests. A sequential rerun after verification exited passed and showed no Python process.

Generated artifacts:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/last.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/best.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/results.csv`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/args.yaml`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/resume_train_stdout.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/resume_train_stderr.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/resume_train.pid`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/metadata.json`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/README.md`

What is complete:

- The resumed YOLOv8m run was saved without discarding progress.
- The clean recovery point is the epoch-74 `last.pt` checkpoint.
- The copied checkpoint is loadable through Ultralytics and preserves the 136-class detection head.
- Manual checkpoint metadata includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- Training was stopped after load verification, and no Python training process remains.
- Documentation now points the next agent to the epoch-74 stopped-checkpoint state, not a live process.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- One metadata update attempt failed because PowerShell could not set a missing PSCustomObject property directly. The metadata write was rerun with `Add-Member -Force` and passed.

Next exact step:

- Resume from the saved checkpoint when training should continue:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\yolo.exe detect train resume=True model=.\artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch74_stop_2026-05-22\last.pt`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-21 - Agent Handoff - M3 Training Resumed

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed before resume; showed no active Python training process.
- `Get-ChildItem artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21` - passed; confirmed `last.pt`, `best.pt`, logs, `results.csv`, `args.yaml`, README, and metadata existed.
- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed; returned `False`, confirming M3 was still incomplete before resume.
- `Get-Content -Tail 3 runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; confirmed epoch 20 was still the last completed row before resume.
- Escalated hidden `Start-Process` resume launch - passed; resumed YOLO training from `artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\last.pt`.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\resume_train.pid` - passed; PID file contained `30204`.
- `Get-Content -Tail 100 runs\detection\detection_136class_yolov8m_v1\resume_train_stdout.log` - passed; showed `Resuming training ... from epoch 21 to 150 total epochs` and active epoch `21/150`.
- `Get-Content -Tail 40 runs\detection\detection_136class_yolov8m_v1\resume_train_stderr.log` - passed; log was empty during the resume check.
- `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits` - passed; showed about 16.1 GB of 16.4 GB GPU memory in use during resumed epoch 21.
- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_train.pid)` - passed after correcting an earlier PowerShell variable-name mistake; parent PowerShell PID `30204` was running.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed after resume documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after resume documentation updates, checked 12 documentation files.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\metadata.json` - passed after resume documentation updates.
- Final resume progress check - passed; stdout showed epoch `21/150` still active, around batch `207/307`, and the latest completed results row remained epoch 20.
- A final relative-path rerun of `..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` failed once because PowerShell did not resolve the venv path in that shell call; rerunning with absolute `C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe` passed and checked 12 documentation files.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/resume_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/resume_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/resume_train_stderr.log`

What is complete:

- Training has resumed from the exact load-verified epoch-20 checkpoint.
- Ultralytics confirmed the resumed schedule is epoch 21 through 150.
- The resumed process is running as a hidden background process with PID `30204`.
- Resume logs and PID file are recorded under the existing full-run directory.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- One process-check command attempted to assign to PowerShell's read-only `$PID` variable and printed an error. The corrected command using `$resumePid` passed and confirmed the resumed parent process.

Next exact step:

- Monitor training:
  `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_train_stdout.log`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-21 - Agent Handoff - M3 Training Saved and Stopped

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/README.md`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/metadata.json`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed; returned `False`, confirming no final project metric artifact exists.
- `Get-Content -Tail 5 runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; confirmed epoch 20 was the latest completed row before stopping.
- `Copy-Item` into `artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\` - passed; copied checkpoint, results, args, and logs.
- Manual metadata generation - initially failed once because of PowerShell here-string syntax, then passed after rewriting with explicit output lines.
- Metadata JSON validation - initially failed once because the file had a UTF-8 BOM, then passed after rewriting without BOM.
- `Stop-Process -Id 28848 -Force` - passed; stopped the full training process after the recovery files were copied.
- `Get-CimInstance Win32_Process` child-process inspection - failed with access denied, but this did not block stopping the known training process.
- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed after stop; showed no Python training process.
- Ultralytics load check for the copied `last.pt` - passed; printed `loaded=True`, `class_count=136`, `task=detect`, `first_class=brace`, and `last_class=ottavaBracket`.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\metadata.json` - passed after the no-BOM rewrite.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed after documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed after documentation updates.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after documentation updates, checked 12 documentation files.
- Final `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed; showed no Python training process after verification commands exited.

Generated artifacts:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/last.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/best.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/results.csv`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/args.yaml`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/full_train_stdout.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/full_train_stderr.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/metadata.json`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/README.md`

What is complete:

- The full YOLOv8m run was paused without discarding progress.
- The clean recovery point is the epoch-20 `last.pt` checkpoint.
- The copied checkpoint is loadable through Ultralytics and preserves the 136-class detection head.
- Manual checkpoint metadata includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- Documentation now points the next agent to the paused-checkpoint state, not a live process.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- PowerShell here-string metadata generation failed once before the metadata writer was corrected.
- The first strict JSON check failed because the metadata file had a UTF-8 BOM; it passed after rewriting without BOM.
- Child-process enumeration with `Get-CimInstance` failed with access denied, but `Stop-Process` on the known training PID succeeded and the post-stop Python process check was clean.

Next exact step:

- Resume from the saved checkpoint when training should continue:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\yolo.exe detect train resume=True model=.\artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\last.pt`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-21 - Agent Handoff - M3 Full YOLOv8m Run Launched

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed; no Python training process was alive at pickup.
- `Get-ChildItem -Recurse -Force runs\detection\detection_136class_yolov8m_preflight_v1` - passed; the interrupted YOLOv8m preflight had only setup artifacts and batch preview images, not `results.csv`, weights, or metrics.
- `Get-ChildItem -Path .. -Recurse -Filter best.pt` - passed; found legacy checkpoints and V2 smoke checkpoints.
- `Get-Content C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\yolo_dataset\data.yaml` - passed; confirmed legacy parent detector dataset is `nc: 15`, so those checkpoints cannot satisfy M3.
- `Get-Content -Tail 5 ..\outputs\yolov8_extended\train\results.csv` - passed; confirmed legacy reduced-class training history exists but is not the 136-class M3 artifact.
- Escalated hidden launch with `Start-Process` - passed; started full YOLOv8m training outside the sandbox so it can continue after agent/tool interruptions.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\full_train.pid` - passed; PID file contained `28848`.
- `Get-Process -Id 28848,23140` - passed; showed parent Python PID `28848` and child Python PID `23140`.
- `Get-Content -Tail 120 runs\detection\detection_136class_yolov8m_v1\full_train_stdout.log` - passed; stdout showed YOLOv8m training started with `nc=136`, 150 epochs, image size 1024, batch 4, and epoch `1/150`.
- `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits` - passed; showed training using roughly 13.9 GB of the 16 GB GPU during the live check.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed during live M3 training, 24 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed during live M3 training.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed during live M3 training, checked 12 documentation files.
- Waited for the first epoch boundary - passed; `results.csv`, `weights/best.pt`, and `weights/last.pt` exist, and stdout showed training continuing in epoch `2/150`.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/full_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/full_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/full_train_stderr.log`
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/` in progress
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/results.csv`
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/last.pt`

What is complete:

- M3 full YOLOv8m training has been launched with the governing config values: `epochs=150`, `imgsz=1024`, `batch=4`, `workers=0`, `device=0`, `taxonomy_id=deepscores_136`.
- The training log confirms Ultralytics overrides the pretrained COCO head to `nc=136` and trains on `runs/data/deepscores_136_yolo_materialized/dataset.yaml`.
- The parent legacy checkpoints were checked and are not valid M3 completion artifacts because their dataset YAML is 15-class.
- The live full run has passed the first epoch boundary and has a checkpoint recovery point.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- No full-run ONNX export has completed yet.
- No API detector artifact wiring has been done.
- `docs/AGENT_PROMPTS.md` must remain on M3 until the full run completes and the artifact is accepted.

What failed:

- The earlier YOLOv8m preflight run was interrupted before training metrics or checkpoints were written. It left only setup artifacts under `runs/detection/detection_136class_yolov8m_preflight_v1/`.
- Earlier sandboxed detached launches did not survive reliably. The successful live launch used an escalated hidden `Start-Process`.

Next exact step:

- Monitor the live run first: `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\full_train.pid)`.
- Then inspect progress: `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\full_train_stdout.log`.
- If `runs/detection/detection_136class_yolov8m_v1/metrics.json` appears, run the M3 verification/doc update sequence.
- If the process exits without `metrics.json`, inspect `runs/detection/detection_136class_yolov8m_v1/full_train_stderr.log`, `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/results.csv`, and `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/last.pt` before deciding whether to resume or relaunch.

## 2026-05-20 - Agent Handoff - M3 Full Detector Smoke

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `configs/detection_136class_yolov8m.yaml`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`
- `scripts/analyze_detection_136class_run.py`
- `scripts/run_detection_136class_yolo.py`
- `src/melodious_v2/evaluation/full_detector.py`
- `tests/test_full_detector_m3.py`

Commands run:

- `git switch -c phase-03-detector` - initially failed with sandbox permission denied, then passed with approval and created branch `phase-03-detector`.
- `$env:PYTHONPATH='src'; @' ... '@ | ..\.venv\Scripts\python.exe -` - passed; verified PyTorch, CUDA, Ultralytics, ONNX, ONNX Runtime, source image paths, and label counts.
- `nvidia-smi` - passed; detected NVIDIA GeForce RTX 3080 Laptop GPU with 16 GB VRAM.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed before M3 run, 23 tests; passed after analysis additions, 24 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --materialize-only` - passed; created `runs/data/deepscores_136_yolo_materialized/`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --smoke --epochs 1 --imgsz 640 --batch 2 --workers 0 --device 0` - passed; trained one-epoch full-taxonomy smoke model, validated on M1 validation split, exported ONNX.
- `Remove-Item -LiteralPath yolo11n.pt -Force` - passed; removed incidental Ultralytics AMP-check download from repo root.
- `..\.venv\Scripts\python.exe -m json.tool runs\detection\detection_136class_yolov8s_smoke_v1\metrics.json > $null` - passed; M3 metrics JSON is strict JSON.
- `..\.venv\Scripts\python.exe -m json.tool runs\detection\detection_136class_yolov8s_smoke_v1\manifest.json > $null` - passed.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\models\detection_136class_yolov8s_smoke_v1\metadata.json > $null` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\analyze_detection_136class_run.py` - passed; generated M3 analysis artifacts.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed; experiment index now includes M2 and M3 smoke runs.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 12 documentation files.

Generated artifacts:

- `runs/data/deepscores_136_yolo_materialized/dataset.yaml`
- `runs/data/deepscores_136_yolo_materialized/manifest.json`
- `runs/data/deepscores_136_yolo_materialized/images/{train,val,test}/`
- `runs/data/deepscores_136_yolo_materialized/labels/{train,val,test}/`
- `runs/detection/detection_136class_yolov8s_smoke_v1/metrics.json`
- `runs/detection/detection_136class_yolov8s_smoke_v1/report.md`
- `runs/detection/detection_136class_yolov8s_smoke_v1/manifest.json`
- `runs/detection/detection_136class_yolov8s_smoke_v1/artifacts.json`
- `runs/detection/detection_136class_yolov8s_smoke_v1/config.yaml`
- `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.json`
- `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.md`
- `runs/detection/detection_136class_yolov8s_smoke_v1/ultralytics/train/`
- `runs/detection/detection_136class_yolov8s_smoke_v1/ultralytics/val_val/`
- `artifacts/models/detection_136class_yolov8s_smoke_v1/best.pt`
- `artifacts/models/detection_136class_yolov8s_smoke_v1/best.onnx`
- `artifacts/models/detection_136class_yolov8s_smoke_v1/metadata.json`

What is complete:

- M1 prerequisite verified locally.
- M2 prerequisite verified locally.
- M3 environment preflight passed with CUDA, Ultralytics, ONNX, and ONNX Runtime available.
- M1 DeepScores labels/images were materialized into a YOLO-standard ignored dataset.
- A full 136-class YOLO training/evaluation/export pipeline now exists in code.
- A constrained one-epoch YOLOv8s full-taxonomy smoke run completed successfully.
- Checkpoint and ONNX artifacts were copied to `artifacts/models/detection_136class_yolov8s_smoke_v1/` with SHA256 metadata.
- Generated analysis records rare-class, small-symbol, zero-mAP, and confusion-matrix evidence.
- M1, M2, M3, and future milestones are now documented in detail in `docs/MILESTONE_HISTORY.md`.

What failed:

- Initial hardlink materialization was not permitted by the filesystem, so the materializer copied source images into ignored `runs/data/deepscores_136_yolo_materialized/`.
- The first `git switch -c phase-03-detector` attempt needed sandbox escalation. It succeeded after approval.

What is blocked:

- Full configured YOLOv8m 150-epoch training is not complete.
- The M3 smoke artifact is not wired into the API because it is smoke-quality and the non-bootstrap ONNX detector adapter has not been implemented.
- M4 should not start until the team either accepts an M3 detector artifact for integration or completes the full configured detector run.

Next exact step:

- Run the full configured detector command:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --model yolov8m.pt --epochs 150 --imgsz 1024 --batch 4 --workers 0 --device 0`

## 2026-05-20 - Agent Handoff - M2 Metric Reproduction

Milestone worked:

- M2 - Metric Reproduction

Files changed:

- `configs/detection_15class_repro.yaml`
- `docs/AGENT_PROMPTS.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_CARD.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`
- `scripts/run_detection_15class_repro.py`
- `src/melodious_v2/evaluation/__init__.py`
- `src/melodious_v2/evaluation/reduced_detection.py`
- `src/melodious_v2/metrics/detection.py`
- `src/melodious_v2/reports.py`
- `tests/test_detection_metrics.py`
- `tests/test_detection_repro.py`
- `tests/test_export_and_reports.py`

Commands run:

- `git switch -c phase/02-metrics` - failed because Git could not create `refs/heads/phase/02-metrics`; the ref layout blocks that slash name.
- `git switch -c phase-02-metrics` - initially failed with sandbox permission denied, then passed with approval and created branch `phase-02-metrics`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 21 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_15class_repro.py` - passed; generated the M2 run from five legacy sample prediction payloads and matching DeepScores annotations.
- `..\.venv\Scripts\python.exe -m json.tool runs\detection\detection_15class_repro_sample_v1\metrics.json > $null` - passed; `metrics.json` is strict JSON.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 11 documentation files.

Generated artifacts:

- `runs/detection/detection_15class_repro_sample_v1/metrics.json`
- `runs/detection/detection_15class_repro_sample_v1/report.md`
- `runs/detection/detection_15class_repro_sample_v1/manifest.json`
- `runs/detection/detection_15class_repro_sample_v1/artifacts.json`
- `runs/detection/detection_15class_repro_sample_v1/config.yaml`

What is complete:

- M2 reduced-class reproduction uses real legacy sample YOLOv8s payloads from `../sample_detections/model_outputs_quick/`.
- Matching DeepScores targets are derived from `../dataset_ds2_dense/deepscores_train.json` and `../dataset_ds2_dense/deepscores_test.json`.
- The run uses `deepscores_15_reduced` taxonomy and preserves checkpoint SHA256 provenance for `../outputs/yolov8_runs/train/weights/best.pt`.
- `docs/EXPERIMENTS.md` is generated from `runs/**/metrics.json`.
- `docs/AGENT_PROMPTS.md` now points the next agent to M3.

What failed:

- The requested `phase/02-metrics` branch name could not be created because of local Git ref layout.
- The first `phase-02-metrics` branch creation attempt needed sandbox escalation. It succeeded after approval.

What is blocked:

- Nothing for M2.
- M3 has not started. Full 136-class detector training still needs local training dependency/hardware verification.

Next exact step:

- Start M3 by verifying the DeepScores 136-class YOLO manifest and local YOLO/Ultralytics runtime, then train/evaluate through `configs/detection_136class_yolov8m.yaml` with metrics written to `runs/detection/{run_id}/metrics.json`.

## 2026-05-12 - Agent Handoff - M1 Reverification

Milestone worked:

- M1 - Dataset Manifests verification pass

Files changed:

- `docs/STATUS.md`
- `docs/HANDOFF.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe - <<'PY' ...` - failed before Python execution because PowerShell does not support Bash heredoc redirection.
- `$env:PYTHONPATH='src'; @' ... '@ | ..\.venv\Scripts\python.exe -` - passed; confirmed DeepScores top-level and split `class_count = 136`, DeepScores duplicate id/filename checks passed with work-group warning, and MUSCIMA page-id leakage passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 19 tests; rerun after documentation updates and still passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after documentation updates, checked 11 documentation files.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\build_dataset_manifests.py` - passed, regenerated DeepScores and MUSCIMA manifest runs from local parent datasets.

Generated artifacts:

- Refreshed ignored artifacts under `runs/data/deepscores_136_manifest/`.
- Refreshed ignored artifacts under `runs/data/muscima_graph_manifest/`.

What is complete:

- M1 remains complete.
- `runs/data/deepscores_136_manifest/manifest.json` and `leakage_report.json` exist.
- Every DeepScores split summary reports `class_count = 136`.
- DeepScores duplicate image-id and duplicate filename leakage checks passed.
- DeepScores inferred work-group leakage remains `warning` with 202 repeated filename-inferred groups.
- `runs/data/muscima_graph_manifest/manifest.json` exists.
- MUSCIMA train/val/holdout split leakage check passed with no duplicate page ids.

What failed:

- A non-blocking artifact-summary probe used Bash heredoc syntax in PowerShell and failed before Python ran. The equivalent PowerShell-compatible command passed.

What is blocked:

- None for M1.
- M2 has not started; no reduced-class V2 metric reproduction run exists yet.

Next exact step:

- Update `docs/AGENT_PROMPTS.md` to an M2 prompt, then start M2 by creating a reduced-class metric reproduction run that writes `runs/**/metrics.json` with required provenance.

## 2026-05-12 - Agent Handoff

Milestone worked:

- M1 - Dataset Manifests

Files changed:

- `src/melodious_v2/datasets/manifests.py`
- `scripts/build_dataset_manifests.py`
- `tests/test_dataset_manifests.py`
- `configs/detection_136class_yolov8m.yaml`
- `docs/DATA_CARD.md`
- `docs/STATUS.md`
- `docs/ROADMAP.md`
- `docs/HANDOFF.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 19 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\build_dataset_manifests.py` - passed, generated DeepScores and MUSCIMA manifest runs.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked documentation files.

Generated artifacts:

- `runs/data/deepscores_136_manifest/manifest.json`
- `runs/data/deepscores_136_manifest/train.json`
- `runs/data/deepscores_136_manifest/val.json`
- `runs/data/deepscores_136_manifest/test.json`
- `runs/data/deepscores_136_manifest/class_counts.json`
- `runs/data/deepscores_136_manifest/leakage_report.json`
- `runs/data/deepscores_136_manifest/yolo_dataset.yaml`
- `runs/data/deepscores_136_manifest/generated/labels/{train,val,test}/`
- `runs/data/deepscores_136_manifest/generated/image_lists/{train,val,test}.txt`
- `runs/data/muscima_graph_manifest/manifest.json`
- `runs/data/muscima_graph_manifest/train.json`
- `runs/data/muscima_graph_manifest/val.json`
- `runs/data/muscima_graph_manifest/holdout.json`
- `runs/data/muscima_graph_manifest/leakage_report.json`
- `runs/data/muscima_graph_manifest/class_summary.json`

What is complete:

- DeepScores source train/test separation is preserved.
- DeepScores source train split is deterministically split into 1226 train and 136 validation images with seed `42`.
- DeepScores test split has 352 images from the source test JSON.
- Every DeepScores split summary reports `class_count = 136`.
- YOLO labels were generated for all DeepScores splits under ignored `runs/`.
- MUSCIMA XML pages were split into 112 train, 14 validation, and 14 holdout pages with seed `42`.
- MUSCIMA class parsing produced `class_summary.json`.
- Tests cover deterministic splitting, DeepScores class-count summaries, duplicate DeepScores id leakage, and MUSCIMA page-id separation.

What is blocked:

- None for M1.
- DeepScores leakage status is `warning`, not failed, because filename-inferred work groups repeat across splits. Duplicate image ids and duplicate filenames both passed.

Next exact step:

- Begin M2 by creating a reduced-class metric reproduction run that writes `runs/**/metrics.json`, then regenerate `docs/EXPERIMENTS.md` from that artifact.

## Handoff Entry Template

When an agent finishes work, append a new section using this shape:

```markdown
## YYYY-MM-DD - Agent Handoff

Milestone worked:

- Mx - Name

Files changed:

- path

Commands run:

- command - result

Generated artifacts:

- path or none

What is complete:

- item

What is blocked:

- item or none

Next exact step:

- command or implementation task
```
