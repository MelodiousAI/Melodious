# Status

## Current Phase

M7 - Detector Metric Improvement is active. M6 - AWS Public Demo remains deployment-prepared, but actual public deployment is blocked on account-local AWS values and AWS CLI availability in this workspace. M1 - Dataset Manifests, M2 - Metric Reproduction, M3 - Full 136-Class Detector, M4 - Real Assembly Runtime, and M5 - End-to-End Export Quality are complete enough to hand off. The full configured M3 detector run `detection_136class_yolov8m_v1` completed all 150 YOLOv8m epochs, was finalized from the selected `best.pt` checkpoint, wrote project-standard metric provenance, exported ONNX, copied model artifacts, and generated class/error analysis. M4 wired the legacy MUSCIMA GNN checkpoint into a V2 runtime adapter, added explicit checkpoint/fallback API metadata, and wrote a natural-candidate-edge graph evaluation run. M5 measured the fixed MUSCIMA holdout export path using XML-derived detector payload fixtures and wrote end-to-end artifact evidence.

The current detector artifact is ready for integration work, but the API still uses `heuristic_bootstrap` for uploaded images. A separate local clean-sheet note extraction demo now exists at `scripts/extract_notes_from_image.py`; it snapshots a YOLO checkpoint, detects noteheads on CPU, estimates treble-clef pitch from staff geometry, applies detected key-signature and explicit-accidental symbols, and writes actual note JSON, overlay, MusicXML, and MIDI artifacts. This demo path is not a metric run and is not yet wired into the FastAPI upload route.

M7 improved the best validation detector configuration first by correcting dense-page inference settings for the selected YOLOv8m checkpoint, then by completing two real fine-tunes. The completed 1472 fine-tune run is `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`; its separate `F1@0.5` is `0.8082006373091581`, and its AP metrics are `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271`.
The completed follow-up run is `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`. It was resumed from the load-verified epoch-22 manual checkpoint, completed, then was re-finalized with the intended `imgsz=1536` and `max_det=2000` settings after an initial incorrect 1024/default-cap finalization was found. Corrected v2 `F1@0.5` is `0.8318461933668392`. Corrected v2 AP/threshold metrics are `mAP@0.5:0.95 = 0.707986237382828`, `mAP@0.5 = 0.8390674529615662`, `precision@0.5 = 0.8806427974719793`, and `recall@0.5 = 0.7881733414248919`.
M7 also added a detector class-coverage audit: the model head preserves the 136-class taxonomy, but the local DeepScores labels support 115 classes across train/validation/test, validation measures 103 classes, and 21 taxonomy classes have zero local labels. The best completed v2 fine-tune still leaves `stem = 0.0` AP and only modest `ledgerLine = 0.01106603897644983`, so rhythm extraction remains limited by thin-symbol detection.

M7 has now moved the `stem` fix from a vague "train more" idea to a concrete tiled-dataset path. The local labels contain abundant `stem` supervision, but whole-page training makes the median stem approximately `0.78` model pixels wide at `imgsz=1536`, and a low-threshold probe returned zero stem predictions on sampled validation pages. The new tiled materializer creates focus tiles around stems, ledger lines, dots, beams, and flags. The full tiled dataset under `runs/data/deepscores_136_yolo_tiled_stem_v1/` now contains 88137 train tiles, 10709 validation tiles, 26019 test tiles, and 747473 total retained stem labels. A sampled no-copy pilot dataset under `runs/data/deepscores_136_yolo_tiled_stem_pilot_v1/` points to 12000 train tiles, 2500 validation tiles, and 2500 test tiles from the full tiled set. Active tiled pilot training is `detection_136class_yolov8m_tiled_stem_pilot_img1024_v1`, launched from the corrected v2 `best.pt`; PID `6100` is saved in `tiled_pilot_train.pid`, and Windows worker PID `14544` was observed doing the actual training work. No final tiled detector metric has been claimed yet; the next official metric claim needs the pilot or full tiled run to complete and write `metrics.json`. As live evidence only, the epoch-8 training CSV row reports precision `0.87592`, recall `0.87927`, mAP@0.5 `0.89914`, and mAP@0.5:0.95 `0.83297`, and a 300-tile probe against the current pilot `best.pt` found `stem` mAP@0.5:0.95 approximately `0.6064`.

The 2026-06-04 GPU speed check found that the tiled pilot slowed to about `0.8 it/s` while Windows was using the `Balanced` power plan. Switching to the built-in `High performance` power plan and setting the active training worker PID `14544` to `AboveNormal` priority raised live throughput to about `2.6-2.7 it/s`. The RTX 3080 Laptop GPU was observed at about 6.5 GB VRAM used out of 16 GB, around `1770 MHz`, `81 W`, and `86 C` after the fix. LM Studio GPU processes were present; close them manually before long training if extra headroom is needed.

## Completed

- Clean V2 project structure created.
- Governance docs added from the start.
- Versioned detector payload contract generated at `docs/detector_payload_v2.schema.json`.
- Metric rules locked before training in `docs/METRICS.md`.
- Local API/UI scaffold verified with sample transcription.
- AWS deployment path selected: ECS Express Mode or ECS Fargate with ECR, S3, and CloudFront.
- DeepScores 136-class manifest run generated under `runs/data/deepscores_136_manifest/`.
- MUSCIMA graph page manifest run generated under `runs/data/muscima_graph_manifest/`.
- DeepScores duplicate image-id and filename leakage checks passed.
- DeepScores inferred work-group leakage check remains a warning with 202 repeated filename-inferred groups.
- MUSCIMA duplicate page-id leakage check passed.
- M2 reduced-class metric reproduction run generated under `runs/detection/detection_15class_repro_sample_v1/`.
- M3 materialized the M1 DeepScores YOLO dataset under `runs/data/deepscores_136_yolo_materialized/`.
- M3 smoke run generated under `runs/detection/detection_136class_yolov8s_smoke_v1/`.
- M3 smoke checkpoint and ONNX artifacts generated under `artifacts/models/detection_136class_yolov8s_smoke_v1/`.
- M3 full YOLOv8m training was launched on 2026-05-21, manually saved at clean epoch-20, epoch-74, and epoch-95 recovery points, resumed again, reached epoch 124, resumed from the latest run checkpoint on 2026-05-28, and completed epoch 150.
- M3 final run artifacts now exist under `runs/detection/detection_136class_yolov8m_v1/`: `metrics.json`, `report.md`, `manifest.json`, `artifacts.json`, `analysis.json`, `analysis.md`, `onnx_parity.json`, and copied `config.yaml`.
- M3 final model artifacts now exist under `artifacts/models/detection_136class_yolov8m_v1/`: `best.pt`, `best.onnx`, and `metadata.json`.
- `docs/EXPERIMENTS.md` was regenerated from `runs/**/metrics.json` and now includes the full YOLOv8m run.
- M4 legacy GNN checkpoint source was verified at `..\outputs\gnn_checkpoint.pt` with SHA256 `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`.
- M4 V2 GNN runtime adapter was added under `src/melodious_v2/assembly/legacy_gnn.py`.
- M4 API assembly mode metadata now includes checkpoint path, adapter name, and whether inference actually ran.
- M4 graph evaluation run exists under `runs/graph/graph_legacy_gnn_muscima_val_v1/`.
- `docs/EXPERIMENTS.md` includes `graph_legacy_gnn_muscima_val_v1`.
- M5 end-to-end run exists under `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/`.
- M5 exported MusicXML, MIDI, payload, and relationship artifacts for 14 MUSCIMA holdout XML-derived payload fixtures.
- `docs/EXPERIMENTS.md` includes `e2e_muscima_holdout_xml_fixture_v1`.
- `docs/AGENT_PROMPTS.md` now points the next agent to M6.
- M6 added environment-driven API CORS through `MELODIOUS_CORS_ORIGINS` for public frontend deployment.
- M6 added Python smoke tooling at `scripts/smoke_public_demo.py` and `src/melodious_v2/deployment/smoke.py`.
- M6 expanded `infra/aws/smoke_test.ps1` to verify sample transcription plus MusicXML/MIDI artifact downloads and optional JSON evidence output.
- M6 expanded `infra/aws/README.md` with ECR, ECS/Fargate, S3/CloudFront, smoke-test, and shutdown/cost-control commands.
- M6 updated `infra/aws/task-definition.template.json` with `MELODIOUS_CORS_ORIGINS` and `MELODIOUS_GNN_CHECKPOINT` placeholders.
- M7 added validation-time detector resolution sweep documentation at `docs/METRIC_IMPROVEMENT.md`.
- M7 added sweep config ledger at `configs/detection_136class_eval_resolution_sweep.yaml`.
- M7 added `--val-augment` support to `scripts/run_detection_136class_yolo.py`.
- M7 generated validation-only detector evaluation runs for image sizes 1152, 1248, 1280, 1536, plus a 1280 validation-augmentation comparison.
- M7 added `--max-det` and `--nms-iou` detector-runner controls and found the default 300 detection cap was too low for dense validation pages.
- M7 generated validation-only detector runs with `max_det=2000` for image sizes 1248, 1280, 1344, 1408, 1472, and 1536.
- M7 added reusable class-coverage audit tooling at `src/melodious_v2/evaluation/class_coverage.py` and `scripts/audit_detector_class_coverage.py`.
- M7 generated a class-coverage audit under `runs/detection/detection_136class_class_coverage_audit_v1/`.
- M7 verified that validation/test do not contain supported classes that are absent from training, but the current validation split cannot measure 33 taxonomy classes.
- M7 launched fine-tuning run `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1` from `artifacts/models/detection_136class_yolov8m_v1/best.pt` at image size 1472, batch 1, and `max_det=2000`.
- M7 added `--resume-training` and `--resume-checkpoint` to `scripts/run_detection_136class_yolo.py` after the fine-tune was interrupted mid-epoch.
- M7 resumed `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1` from `ultralytics/train/weights/last.pt`; Ultralytics reported `Resuming training ... from epoch 8 to 50 total epochs`.
- M7 completed `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`; generated `metrics.json`, `analysis.json`, `manifest.json`, `artifacts.json`, `report.md`, `config.yaml`, and `onnx_parity.json`.
- M7 launched follow-up fine-tune `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` from the completed fine-tune `best.pt` at image size 1536, batch 1, and `max_det=2000`.
- M7 added stem-focused tiled YOLO dataset generation in `src/melodious_v2/datasets/yolo_tiling.py` and `scripts/materialize_tiled_yolo_dataset.py`.
- M7 added existing-dataset runner support through `scripts/run_detection_136class_yolo.py --dataset-yaml ... --dataset-id ...`, so a tiled dataset can be used without rematerializing the original full-page DeepScores dataset.
- M7 generated a smoke tiled dataset under `runs/data/deepscores_136_yolo_tiled_stem_smoke_v1/` with 222 train tiles, 229 validation tiles, 264 test tiles, 4361 retained stem labels, and median projected stem width `2.666645333333387` pixels at `target_imgsz=1024`.
- M7 completed and corrected finalization of `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`; this is now the best completed validation detector metric.
- M7 generated the full tiled stem dataset under `runs/data/deepscores_136_yolo_tiled_stem_v1/` with 88137 train tiles, 10709 validation tiles, 26019 test tiles, and 747473 retained stem labels across all splits.
- M7 generated a no-copy sampled tiled pilot dataset under `runs/data/deepscores_136_yolo_tiled_stem_pilot_v1/` with 12000 train tile paths, 2500 validation tile paths, and 2500 test tile paths pointing into the full tiled dataset.
- M7 launched active tiled pilot fine-tune `detection_136class_yolov8m_tiled_stem_pilot_img1024_v1` from the corrected v2 `best.pt`.
- `docs/EXPERIMENTS.md` now includes the M7 detector evaluation runs.
- Added local note extraction demo tooling at `src/melodious_v2/omr/note_extraction.py` and `scripts/extract_notes_from_image.py`.
- Added focused note extraction tests in `tests/test_note_extraction_demo.py`.
- Added `docs/NOTE_EXTRACTION_DEMO.md` with the exact clean-sheet extraction command and caveats.
- Verified the Sad Romance local demo image through the YOLO-backed extraction CLI on CPU after adding stem-aware rhythm inference: `extractor_mode = yolo_notehead_staff_pitch`, staff systems `9`, note events `197`, stem-confirmed notes `0`, dotted notes `17`, duration distribution `0.25:1`, `0.5:80`, `0.75:7`, `1.0:71`, `1.5:8`, `2.0:23`, `3.0:2`, `4.0:5`, MusicXML `<dot/>` count `17`, output under `runs/demo/sad_romance_note_extraction_v3/`.
- Improved the local staff detector so uploaded clean pages with lighter/antialiased staff lines do not silently lose systems; the regression test now covers light staff lines.
- Verified `C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png` through the YOLO-backed extraction CLI on CPU after the staff-detector and key-signature fixes: output under `runs/demo/image_note_extraction_v5/`, `extractor_mode = yolo_notehead_staff_pitch`, staff systems `9`, note events `319`, stem-confirmed notes `0`, dotted notes `38`, detected `B: -1` key signatures on all 9 systems, MusicXML `key_fifths = -1`, `53` B-flat notes from detected key signature, `2` explicit sharp notes from detected inline accidentals, duration distribution `0.25:28`, `0.375:8`, `0.5:175`, `0.75:8`, `1.0:68`, `1.5:21`, `2.0:10`, `3.0:1`, MIDI size `2879` bytes, and MusicXML parse check `319` notes with `38` `<dot/>` tags, one `<fifths>-1</fifths>`, and `53` `<alter>-1</alter>` tags.
- Disabled CV augmentation-dot fallback by default for YOLO-backed note extraction; detector-confirmed `augmentationDot` boxes still count, but tiny CV contour specks are no longer silently converted into dotted rhythms.
- Re-verified `C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png` after the safer dot policy: output under `runs/demo/image_note_extraction_v6/`, `extractor_mode = yolo_notehead_staff_pitch`, staff systems `9`, note events `319`, stem-confirmed notes `0`, dotted notes `7`, detected `B: -1` key signatures on all 9 systems, MusicXML `key_fifths = -1`, `53` B-flat notes from detected key signature, duration distribution `0.25:36`, `0.5:192`, `1.0:74`, `1.5:6`, `2.0:10`, `3.0:1`, MIDI size `2871` bytes, and MusicXML parse check `319` notes with `7` `<dot/>` tags, one `<fifths>-1</fifths>`, and `53` `<alter>-1</alter>` tags.

## Latest Detector Result

Best completed validation detector run id: `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`.

Metric source: `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/metrics.json`.

Evaluation split: `val` from `deepscores_136_yolo_materialized`.

Checkpoint: `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/ultralytics/train/weights/best.pt`.

Inference image size: 1536.

Maximum detections per image: 2000.

Validation augmentation: disabled.

Primary detector metric:

- `mAP@0.5:0.95`: 0.707986237382828.

Secondary detector metrics:

- `mAP@0.5`: 0.8390674529615662.
- `precision@0.5`: 0.8806427974719793.
- `recall@0.5`: 0.7881733414248919.
- `F1@0.5`: 0.8318461933668392.

Class-analysis summary:

- Supported validation classes: 103.
- Supported zero-mAP classes: 6.
- Small-symbol mean `mAP@0.5:0.95`: 0.5870386050344123.
- Rhythm-adjacent per-class results: `stem = 0.0`, `ledgerLine = 0.01106603897644983`, `augmentationDot = 0.26796388729163445`, `beam = 0.8011588011549605`, `flag8thUp = 0.7470091255390053`, `flag8thDown = 0.8207040444816455`, `flag16thUp = 0.7792069978265269`, and `flag16thDown = 0.8260426843009119`.

Measured gain over the previous completed 1472 fine-tune:

- Primary `mAP@0.5:0.95`: +0.0302387420340651.
- Secondary `mAP@0.5`: +0.0164467608824391.
- Precision: +0.0349328453751016.
- Recall: +0.0142960632781713.
- `F1@0.5`: +0.0236455560576811.
- Small-symbol mean `mAP@0.5:0.95`: +0.0224205492332619.
- Supported zero-mAP classes changed from 5 to 6, so the headline gain did not solve every class.

Important detector-result caveat:

- This is still validation-set performance, not test-set performance.
- The run initially had an incorrect finalization with `imgsz=1024` and the default detection cap. That incorrect finalization was replaced by the corrected `imgsz=1536`, `max_det=2000` finalization listed above.
- The class-coverage audit shows the local labels support 115 of 136 taxonomy classes across all splits, 21 taxonomy classes have zero local labels, and validation measures 103 classes. Fine-tuning on the same labels can improve supported classes but cannot teach zero-label classes.
- `stem` remains `0.0`, so rhythm extraction cannot honestly be called solved.

Previous completed fine-tune:

- Run id: `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`.
- Final primary `mAP@0.5:0.95`: 0.6777474953487629.
- Final secondary `mAP@0.5`: 0.8226206920791271.
- Final `precision@0.5`: 0.8457099520968777.
- Final `recall@0.5`: 0.7738772781467206.
- Final `F1@0.5`: 0.8082006373091581.
- Important per-class caveat: `stem = 0.0`, `ledgerLine = 0.0035627224962602928`, `augmentationDot = 0.25050444606568056`, `beam = 0.7824341036579809`, `flag8thUp = 0.7196678490605957`, and `flag8thDown = 0.8042434669433673`.

Stem-focused tiled dataset path:

- Smoke output: `runs/data/deepscores_136_yolo_tiled_stem_smoke_v1/`, with 222 train tiles, 229 validation tiles, 264 test tiles, 4361 retained stem labels, and median projected `stem` width `2.666645333333387` pixels at `target_imgsz=1024`.
- Full tiled output: `runs/data/deepscores_136_yolo_tiled_stem_v1/`.
- Full tiled counts: 88137 train tiles, 10709 validation tiles, 26019 test tiles, 523424 train stem labels, 62411 validation stem labels, 161638 test stem labels, and 747473 total retained stem labels.
- Full tiled preflight passed through `scripts/run_detection_136class_yolo.py --dataset-yaml runs\data\deepscores_136_yolo_tiled_stem_v1\dataset.yaml --dataset-id deepscores_136_yolo_tiled_stem_v1 --materialize-only`.
- Sampled pilot output: `runs/data/deepscores_136_yolo_tiled_stem_pilot_v1/`.
- Sampled pilot lists point into the full tiled dataset without copying images or labels: 12000 train tiles, 2500 validation tiles, and 2500 test tiles; all sampled images had matching labels.
- Active tiled pilot training: `runs/detection/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/`.
- Active tiled pilot PID file: `runs/detection/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/tiled_pilot_train.pid`, containing PID `6100`.
- Active tiled pilot source checkpoint: corrected v2 `best.pt`.
- Active tiled pilot settings: `epochs=12`, `imgsz=1024`, `batch=4`, `workers=0`, `device=0`, `patience=5`, `max_det=2000`.
- Metric status: no tiled detector metric exists yet. The pilot must complete and write `metrics.json` before any tiled improvement claim is made.

Original M3 training run id: `detection_136class_yolov8m_v1`.

Metric source: `runs/detection/detection_136class_yolov8m_v1/metrics.json`.

Evaluation split: `val` from `deepscores_136_yolo_materialized`.

Selected checkpoint: `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`.

Copied artifact: `artifacts/models/detection_136class_yolov8m_v1/best.pt`.

Copied ONNX: `artifacts/models/detection_136class_yolov8m_v1/best.onnx`.

Checkpoint SHA256: `ea005a818902b3c14a12cc6594ef964e29eef99c771ac9a3238fc1d3ef8ce6ac`.

ONNX SHA256: `008ac7c75b8cca5c1cd8346ad84a2b0e27204863fcff2ccb0d39f034ebe5d4cb`.

Primary detector metric:

- `mAP@0.5:0.95`: 0.4747370751116288.

Secondary detector metrics:

- `mAP@0.5`: 0.5853211368313491.
- `precision@0.5`: 0.8274236461250144.
- `recall@0.5`: 0.4909790740632496.
- `F1@0.5`: 0.6162725385980492.

Training CSV summary from `manifest.json`:

- Completed rows: 150.
- Best training-row `mAP@0.5:0.95`: epoch 125 at 0.45579.
- Final epoch 150 training-row `mAP@0.5:0.95`: 0.44888.
- Final V2 validation pass on selected `best.pt`: `mAP@0.5:0.95` 0.4747370751116288.

Analysis summary from `analysis.json`:

- Validation classes with support: 103 of 136.
- Rare supported classes with support <= 10: 14.
- Supported validation classes with zero mAP: 16.
- Supported small-symbol classes: 35.
- Small-symbol mean `mAP@0.5:0.95`: 0.3194606161321027.
- Zero-mAP supported classes include `ledgerLine`, `stem`, `ottavaBracket`, several articulation classes, several fingering classes, `dynamicR`, `tremolo3`, `tuplet1`, and `tuplet5`.

ONNX parity:

- `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json` passed on fixed validation image `lg-10247684-aug-gonville--page-2.png`.
- PyTorch and ONNX both returned 300 boxes with identical class-count totals.
- Local ONNX inference fell back to CPU because `onnxruntime-gpu` is not installed.

## Latest Graph Result

Run id: `graph_legacy_gnn_muscima_val_v1`.

Metric source: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.

Evaluation split: `val` from `muscima_graph_manifest`.

Checkpoint source: `..\outputs\gnn_checkpoint.pt`.

Checkpoint SHA256: `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`.

Runtime adapter: `src/melodious_v2/assembly/legacy_gnn.py`.

Feature encoder: `reconstructed_training_node_encoder_seed_42`.

Primary graph metric:

- `positive_macro_f1`: 0.7590456327823909.

Required separate `no_relation` metrics:

- precision: 0.997066197258228.
- recall: 0.8936271931921403.
- F1: 0.9425171440096813.
- support: 41834.

Positive relationship metrics:

- `stem_notehead` F1: 0.6960721184803607 on 4441 validation candidate edges.
- `beam_notegroup` F1: 0.8220191470844213 on 1899 validation candidate edges.
- `slur_phrase` and `tie_sustained` have zero validation support in the legacy 15-class GNN contract.

Graph distribution:

- Natural candidate-edge distribution with no negative subsampling.
- 14 validation pages.
- 48174 candidate edges.
- 6340 positive candidate edges.
- 10680 predicted positive candidate edges.

Important graph caveat:

- The legacy checkpoint did not save the separate node feature encoder used to build training tensors. V2 reconstructs that encoder from seed `42`, matching the legacy training pipeline. This is documented in the run metrics and should be preserved until the graph model is retrained with a fully self-contained artifact.

## Latest End-to-End Export Result

Run id: `e2e_muscima_holdout_xml_fixture_v1`.

Metric source: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.

Evaluation split: `holdout` from `muscima_graph_manifest`.

Payload source: MUSCIMA XML-derived detector payload fixtures.

Assembly mode requested: `gnn`.

Primary end-to-end export metric:

- `musicxml_validity_rate`: 1.0.

Supporting export metrics:

- `midi_generation_success_rate`: 1.0.
- `page_success_rate`: 1.0.
- `page_count`: 14.
- `musicxml_valid_count`: 14.
- `midi_success_count`: 14.
- `failure_count`: 0.

Run volume:

- `detection_count_total`: 6348.
- `note_like_count_total`: 2563.
- `relationship_count_total`: 10637.
- `assembly_gnn_page_count`: 14.

Important end-to-end caveat:

- This is measured export validity and artifact generation from fixed ground-truth XML-derived payload fixtures. It is not trained detector uploaded-image quality. Uploaded-image detector inference remains `heuristic_bootstrap` until a tested ONNX detector adapter is added.

## Latest Verification

- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` with 32 tests before M6 deployment changes.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py src\melodious_v2\evaluation\full_detector.py`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --finalize-existing-run --workers 0 --device 0`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\evaluate_gnn_muscima.py --split val --device cpu`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_e2e_export_eval.py --split holdout --assembly-mode gnn`.
- Passed: API sample transcription smoke with `MELODIOUS_GNN_CHECKPOINT=..\outputs\gnn_checkpoint.pt`; response reported `applied_mode=gnn`, `fallback_applied=False`, `checkpoint_ready=True`, `inference_ran=True`, `adapter_name=legacy_muscima_gat`, and `relationship_count=4`.
- Passed: local API sample smoke without starting Uvicorn; `/health` returned `ok`, `/version` returned schema `2.0`, sample transcription completed, and the first artifact download returned 721 bytes.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\deployment\smoke.py scripts\smoke_public_demo.py src\melodious_v2\api\app.py`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_deployment_smoke.py`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --local-testclient --output runs\deploy\m6_local_smoke\smoke.json`; verified `/health`, `/version`, sample transcription, MusicXML download, and MIDI download.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` with 33 tests after M6 deployment changes.
- Passed: `cd frontend; npm run build`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`, checked 12 documentation files.
- Passed: `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py tests\test_full_detector_m3.py` after adding `--max-det` and `--nms-iou`.
- Passed: `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py`, 5 tests.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` after the dense-page sweep.
- Passed: `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests`, 34 tests.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`, checked 13 documentation files.
- Passed: fine-tune launch command for `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`; startup logs show CUDA training reached epoch `1/50`.
- Passed: `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py tests\test_full_detector_m3.py` after adding resume support.
- Passed: `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py`, 5 tests.
- Passed: `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests`, 36 tests.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`, checked 13 documentation files.
- Passed: resume launch for `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`; startup logs show training resumed from epoch 8 to 50.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\evaluation\class_coverage.py scripts\audit_detector_class_coverage.py tests\test_detector_class_coverage.py`.
- Passed: `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_detector_class_coverage.py`, 2 tests.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\audit_detector_class_coverage.py --metrics runs\detection\detection_136class_yolov8m_eval_img1472_maxdet2000_v1\metrics.json --output-dir runs\detection\detection_136class_class_coverage_audit_v1`.
- Passed: `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests`, 36 tests.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`, checked 13 documentation files.
- Passed: completed fine-tune finalization for `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`; generated `metrics.json` with AP metrics `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271`.
- Passed: same fine-tune threshold `F1@0.5 = 0.8082006373091581`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py -q`, 8 tests after disabling YOLO-mode CV dot fallback by default.
- Passed: local extraction command for `C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png` to `runs\demo\image_note_extraction_v6`; generated JSON, overlay, MusicXML, and MIDI with 319 notes and 7 MusicXML `<dot/>` tags.
- Passed: active background launch for `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`; startup logs show CUDA training reached epoch `1/50`, parent PID `34896`, and child PID `28432`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_yolo_tiling.py -q`, 3 tests.
- Passed: smoke tiled materialization command for `runs\data\deepscores_136_yolo_tiled_stem_smoke_v1`; generated 222 train tiles, 229 validation tiles, and 264 test tiles.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_full_detector_m3.py tests\test_yolo_tiling.py -q`, 10 tests after adding existing-dataset runner support.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --dataset-yaml runs\data\deepscores_136_yolo_tiled_stem_smoke_v1\dataset.yaml --dataset-id deepscores_136_yolo_tiled_stem_smoke_v1 --materialize-only`; runner recorded `materialization_mode = existing_dataset_yaml`.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest -q`, 50 tests, with one upstream `torch_geometric` deprecation warning.
- Passed: `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py`, checked 14 documentation files.
- Passed: active fine-tune status check for `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`; parent PID `34896` and child PID `28432` were running, final `metrics.json` was absent, and latest completed row was epoch 17.
- Passed: manual checkpoint snapshot for `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` at clean completed epoch 22 under `artifacts/manual_checkpoints/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/epoch22_stop_2026-06-03_021238/`.
- Passed: stopped parent PID `34896` and child PID `28432`, then confirmed both were no longer running.
- Passed: load verification for saved `last.pt`; Ultralytics reported `task=detect`, `class_count=136`, first class `brace`, last class `ottavaBracket`.
- Passed: saved checkpoint `metadata.json` validation with `python -m json.tool` after rewriting without UTF-8 BOM.
- Passed: resumed `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` from the epoch-22 manual checkpoint; new PID `7052` was running and stdout showed resume from epoch 23 to 50.
- Passed: live status check on 2026-06-04 for resumed run; PID `7052` was running, final `metrics.json` was absent, and latest completed row was epoch 39.
- Passed: corrected finalization for `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` at `imgsz=1536` and `max_det=2000`; final `F1@0.5` is `0.8318461933668392`, and AP metrics are `mAP@0.5:0.95 = 0.707986237382828` and `mAP@0.5 = 0.8390674529615662`.
- Passed: full tiled stem dataset materialization at `runs/data/deepscores_136_yolo_tiled_stem_v1/`; generated 88137 train tiles, 10709 validation tiles, 26019 test tiles, and 747473 total retained stem labels.
- Passed: materialize-only runner preflight for `runs\data\deepscores_136_yolo_tiled_stem_v1\dataset.yaml`.
- Passed: sampled no-copy tiled pilot manifest at `runs/data/deepscores_136_yolo_tiled_stem_pilot_v1/`; generated text lists for 12000 train, 2500 validation, and 2500 test tiles with zero missing labels.
- Passed: materialize-only runner preflight for `runs\data\deepscores_136_yolo_tiled_stem_pilot_v1\dataset.yaml`.
- Passed: active tiled pilot launch for `detection_136class_yolov8m_tiled_stem_pilot_img1024_v1`; PID `6100` is saved in `tiled_pilot_train.pid`, latest live check showed stdout in epoch `3/12`, and `results.csv` had completed through epoch `2`.

## Milestone Tracker

| Milestone | Status | Next Evidence |
|---|---|---|
| M0 - V2 Foundation | Done | Existing tests, schema, API/UI smoke |
| M1 - Dataset Manifests | Done | Manifest JSONs, class counts, leakage reports, tests |
| M2 - Metric Reproduction | Done | `runs/detection/detection_15class_repro_sample_v1/metrics.json`, generated experiment index |
| M3 - Full 136-Class Detector | Done | `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, `onnx_parity.json`, `artifacts/models/detection_136class_yolov8m_v1/metadata.json` |
| M4 - Real Assembly Runtime | Done | `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`, adapter tests, API mode proof |
| M5 - End-to-End Export Quality | Done | `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`, exported MusicXML/MIDI artifacts |
| M6 - AWS Public Demo | Prepared / blocked on AWS values | `infra/aws/README.md`, `scripts/smoke_public_demo.py`, local smoke evidence; public smoke pending |
| M7 - Detector Metric Improvement | Active | `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/metrics.json`, active `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/`, `docs/METRIC_IMPROVEMENT.md` |
| M8 - Final Grading Package | Planned | Frozen docs and presentation evidence |

## Active Blockers

- API detector runtime is still bootstrap/heuristic for uploaded images; the new YOLOv8m ONNX artifact exists but is not yet used by a non-bootstrap detector adapter.
- AWS resources are not provisioned from this workspace.
- AWS CLI was not found by `Get-Command aws -ErrorAction SilentlyContinue`, so no ECR/ECS/S3/CloudFront deployment command was run locally.
- Account-local AWS values are unavailable and must not be committed: region/profile, execution role ARN, task role ARN, subnet IDs, security group IDs, ALB target group/listener, S3 frontend bucket, CloudFront distribution ID, and public API host.
- DeepScores leakage report is `warning` because 202 filename-inferred work groups repeat across splits. Duplicate image ids and duplicate filenames passed.
- Full detector metrics are validation-split metrics. Test-set detector performance should be produced only after the team freezes the detector family and avoids iterative tuning on test data.
- Several high-support symbol classes still have zero detector mAP on validation, especially `ledgerLine` and `stem`; this is a real model limitation and should not be hidden in the final report.
- The improved M7 detector metric is validation-only inference tuning. Test-set detector performance remains intentionally unreported.
- Twenty-one detector taxonomy classes have zero labels across the local train/validation/test manifests, so training on the same local dataset cannot teach those classes.
- The validation split has 33 taxonomy-class blind spots; validation-selected settings do not prove all 136 classes work.
- The M4 GNN is a legacy 15-class relationship model. It cannot represent every V2 detector class, and its feature encoder is reconstructed from seed `42` because the legacy checkpoint did not save that encoder as a separate artifact.
- The M5 end-to-end run measures export validity from XML-derived payload fixtures, not trained uploaded-image detector quality.

## Next Actions

1. Monitor active tiled pilot run `detection_136class_yolov8m_tiled_stem_pilot_img1024_v1` using `tiled_pilot_train.pid` and `tiled_pilot_train_stdout.log`.
2. If the pilot is interrupted, preserve the latest `last.pt`, `best.pt`, `results.csv`, logs, PID file, command, and launch metadata before stopping or resuming.
3. When the pilot completes, inspect `metrics.json`, `analysis.json`, and per-class AP for `stem`, `ledgerLine`, `augmentationDot`, `beam`, and `flag*`; compare against corrected v2, but label it as a tiled-validation pilot unless evaluated back on the original full-page validation set.
4. If the pilot moves `stem` meaningfully, decide whether to launch a longer/full tiled run from the pilot `best.pt` or evaluate the pilot checkpoint on the full-page validation split to check regression.
5. If the pilot still has `stem = 0.0`, do not spend days on the full tiled run without a new idea. Evaluate OBB/segmentation for thin symbols, a verified synthetic stem/dot supplement, or a clearly labeled demo-only CV stem-line attachment fallback with explicit `rhythm_source` provenance.
6. Keep test-set detector metrics untouched until the team freezes the final model and inference configuration.
7. Keep uploaded-image detector inference labeled `heuristic_bootstrap` unless a tested ONNX detector adapter is implemented.
8. After detector metrics are frozen, return to M6 public deployment or move to M8 final grading package depending on professor priorities.

## Roadmap

See `docs/ROADMAP.md` for milestone definitions, acceptance criteria, and the weekly operating rhythm.
