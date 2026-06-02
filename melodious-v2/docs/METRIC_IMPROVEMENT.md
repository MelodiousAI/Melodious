# Detector Metric Improvement Sprint

This document tracks deliberate attempts to improve measured detector metrics without losing provenance. It should be read before launching more detector experiments.

## Current Problem

The original full YOLOv8m detector result was acceptable as an engineering milestone but weak for presentation:

- Run id: `detection_136class_yolov8m_v1`.
- Split: validation.
- Primary `mAP@0.5:0.95`: 0.4747370751116288.
- Secondary `mAP@0.5`: 0.5853211368313491.
- `F1@0.5`: 0.6162725385980492.
- Supported validation classes with zero mAP: 16.

The main visible weaknesses are small symbols and thin/line-like classes. High-support classes such as `ledgerLine` and `stem` still have zero mAP.

## Inference Resolution Sweep

The first improvement attempt reused the exact selected YOLOv8m checkpoint from M3 and changed only validation inference settings. No new model was trained.

Base checkpoint:

- `artifacts/models/detection_136class_yolov8m_v1/best.pt`.
- Checkpoint SHA256 from M3: `ea005a818902b3c14a12cc6594ef964e29eef99c771ac9a3238fc1d3ef8ce6ac`.

Config ledger:

- `configs/detection_136class_eval_resolution_sweep.yaml`.

Sweep results:

| Run id | Image size | Validation augmentation | Primary `mAP@0.5:0.95` | `mAP@0.5` | `F1@0.5` | Small-symbol mean `mAP@0.5:0.95` | Notes |
|---|---:|---|---:|---:|---:|---:|---|
| `detection_136class_yolov8m_v1` | 1024 | false | 0.4747370751116288 | 0.5853211368313491 | 0.6162725385980492 | 0.3194606161321027 | Original M3 result |
| `detection_136class_yolov8m_eval_img1152_v1` | 1152 | false | 0.491592825206654 | 0.6019533363518853 | 0.6247138913843666 | 0.3239846960537755 | Better secondary metrics |
| `detection_136class_yolov8m_eval_img1248_v1` | 1248 | false | 0.5058429013539956 | 0.6069618791829888 | 0.6329194449061496 | 0.34224209611777584 | Best primary metric |
| `detection_136class_yolov8m_eval_img1280_v1` | 1280 | false | 0.49475049942969357 | 0.5954148845918089 | 0.6161631790766333 | 0.3222766300526699 | Improved but below 1248 |
| `detection_136class_yolov8m_eval_img1536_v1` | 1536 | false | 0.4801245622281405 | 0.5782295362640006 | 0.6108658316146373 | 0.32582402598014537 | Regressed |
| `detection_136class_yolov8m_eval_img1280_aug_v1` | 1280 | true | 0.46735702840326376 | 0.590822879087476 | 0.626829539709963 | 0.3096585062438863 | Validation augmentation regressed |

Best measured validation configuration:

- Run id: `detection_136class_yolov8m_eval_img1248_v1`.
- Primary `mAP@0.5:0.95`: 0.5058429013539956.
- Secondary `mAP@0.5`: 0.6069618791829888.
- `precision@0.5`: 0.8637798517406144.
- `recall@0.5`: 0.4994362851193167.
- `F1@0.5`: 0.6329194449061496.
- Small-symbol mean `mAP@0.5:0.95`: 0.34224209611777584.

Measured gain over original M3 validation:

- Primary `mAP@0.5:0.95` increased by 0.0311058262423668.
- Secondary `mAP@0.5` increased by 0.0216407423516397.
- `F1@0.5` increased by 0.0166469063081004.
- Small-symbol mean `mAP@0.5:0.95` increased by 0.0227814799856731.

## Dense Page Detection-Cap Sweep

The second improvement attempt found a much larger evaluator issue. Ultralytics defaults to `max_det = 300` detections per image, but the DeepScores validation pages are dense music pages:

- Validation images: 136.
- Average validation labels per image: 705.448529411765.
- Maximum validation labels on one image: 2011.
- Validation pages above 300 labels: 109.
- Validation pages above 1000 labels: 28.

That means the default cap can truncate predictions before evaluation on most validation pages. The next sweep reused the same checkpoint and changed only inference/evaluation settings. No new model was trained.

| Run id | Image size | Max detections | NMS IoU | Primary `mAP@0.5:0.95` | `mAP@0.5` | Precision | Recall | `F1@0.5` | Zero-mAP supported classes | Small-symbol mean `mAP@0.5:0.95` | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `detection_136class_yolov8m_v1` | 1024 | default | default | 0.4747370751116288 | 0.5853211368313491 | 0.8274236461250144 | 0.4909790740632496 | 0.6162725385980492 | 16 | 0.3194606161321027 | Original M3 result |
| `detection_136class_yolov8m_eval_img1248_v1` | 1248 | default | default | 0.5058429013539956 | 0.6069618791829888 | 0.8637798517406144 | 0.4994362851193167 | 0.6329194449061496 | 16 | 0.34224209611777584 | Resolution-only best |
| `detection_136class_yolov8m_eval_img1248_maxdet2000_v1` | 1248 | 2000 | default | 0.5963368958356667 | 0.7633185873939334 | 0.8083822251900022 | 0.7148959622497416 | 0.7587703854856837 | 7 | not selected | Major gain from fixing cap |
| `detection_136class_yolov8m_eval_img1248_maxdet3000_v1` | 1248 | 3000 | default | 0.5961042813834952 | 0.7632340648788607 | not selected | not selected | not selected | not selected | not selected | No gain over 2000 |
| `detection_136class_yolov8m_eval_img1280_maxdet2000_v1` | 1280 | 2000 | default | 0.6015765296461454 | 0.7681227034894664 | 0.8061667690022291 | 0.7082872461030865 | 0.7540640191398675 | not selected | not selected | Improved but below later scales |
| `detection_136class_yolov8m_eval_img1344_maxdet2000_v1` | 1344 | 2000 | default | 0.6117073791668945 | 0.773833639576536 | 0.802002845541006 | 0.7196616240704183 | 0.7586043859965066 | not selected | not selected | Better primary |
| `detection_136class_yolov8m_eval_img1408_maxdet2000_v1` | 1408 | 2000 | default | 0.6171871717140972 | 0.7855287823250787 | 0.7878240947679479 | 0.7535043729106492 | 0.7702821467848316 | 7 | 0.4876218654337952 | Best F1; crosses +0.2 on `mAP@0.5` |
| `detection_136class_yolov8m_eval_img1472_maxdet2000_v1` | 1472 | 2000 | default | 0.6204968163150985 | 0.7833788545364062 | 0.8166240104606699 | 0.7367130723503518 | 0.7746130448554269 | 7 | 0.4832789581411164 | Best primary metric |
| `detection_136class_yolov8m_eval_img1536_maxdet2000_v1` | 1536 | 2000 | default | 0.6203204846063568 | 0.7920129156176505 | 0.8107734656247262 | 0.7331813762215841 | 0.7700277096444413 | 6 | 0.4987375853530484 | Best `mAP@0.5`; fewest zero-mAP supported classes |
| `detection_136class_yolov8m_eval_img1536_maxdet2000_iou08_v1` | 1536 | 2000 | 0.8 | 0.6192197532779491 | 0.7886280842894071 | not selected | not selected | not selected | 6 | not selected | Looser NMS regressed |

Best current primary validation configuration:

- Run id: `detection_136class_yolov8m_eval_img1472_maxdet2000_v1`.
- Primary `mAP@0.5:0.95`: 0.6204968163150985.
- Secondary `mAP@0.5`: 0.7833788545364062.
- Precision at IoU 0.5: 0.8166240104606699.
- Recall at IoU 0.5: 0.7367130723503518.
- `F1@0.5`: 0.7746130448554269.
- Small-symbol mean `mAP@0.5:0.95`: 0.4832789581411164.
- Supported validation classes with zero mAP: 7.

Best current secondary `mAP@0.5` validation configuration:

- Run id: `detection_136class_yolov8m_eval_img1536_maxdet2000_v1`.
- Primary `mAP@0.5:0.95`: 0.6203204846063568.
- Secondary `mAP@0.5`: 0.7920129156176505.
- Precision at IoU 0.5: 0.8107734656247262.
- Recall at IoU 0.5: 0.7331813762215841.
- `F1@0.5`: 0.7700277096444413.
- Small-symbol mean `mAP@0.5:0.95`: 0.4987375853530484.
- Supported validation classes with zero mAP: 6.

Measured gain over original M3 validation:

- Best primary `mAP@0.5:0.95` increased by 0.1457597412034697.
- Best secondary `mAP@0.5` increased by 0.2066917787863014.
- Best recall increased by 0.2625252988473996.
- Best detector F1 increased by 0.1583405062573777.
- Best small-symbol mean `mAP@0.5:0.95` increased by 0.1792769692209457.
- Supported validation classes with zero mAP decreased from 16 to 6.

Precision did not improve by 0.2 because the original precision was already 0.8274236461250144, so an absolute +0.2 precision increase would require a value above 1.0, which is impossible. The dense-page fix trades some precision for substantially better recall, AP, and F1.

## Interpretation

The professor-facing detector result should now use `detection_136class_yolov8m_eval_img1472_maxdet2000_v1` for the official primary validation metric and `detection_136class_yolov8m_eval_img1536_maxdet2000_v1` when discussing the more optimistic `mAP@0.5` validation metric. The model itself did not change, so this is best described as a corrected dense-page inference/evaluation configuration for the same full-taxonomy YOLOv8m checkpoint.

This is still not a test-set result. The test set should stay untouched until the team freezes the final model and inference configuration.

## Class Coverage Audit

Before launching another fine-tune, M7 added and ran a class-coverage audit so the metric-improvement work does not hide rare-class or unsupported-class issues.

Audit command:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\audit_detector_class_coverage.py --metrics runs\detection\detection_136class_yolov8m_eval_img1472_maxdet2000_v1\metrics.json --output-dir runs\detection\detection_136class_class_coverage_audit_v1
```

Generated audit artifacts:

- `runs/detection/detection_136class_class_coverage_audit_v1/class_coverage.json`.
- `runs/detection/detection_136class_class_coverage_audit_v1/class_coverage.md`.

Main findings:

- The detector taxonomy and model head still contain all 136 classes.
- The local DeepScores labels contain support for 115 of 136 taxonomy classes across train/validation/test.
- `train` supports 115 classes, `val` supports 103 classes, and `test` supports 110 classes.
- The validation split has 33 taxonomy-class blind spots, so it cannot honestly measure all 136 classes.
- No validation-supported or test-supported class is absent from training, which means validation/test are not evaluating classes the model never saw in train.
- Twelve training-supported classes are absent from validation: `timeSig5`, `timeSig7`, `tremolo1`, `tremolo4`, `flag32ndUp`, `accidentalDoubleFlat`, `articStaccatissimoBelow`, `fingering5`, `tuplet4`, `tuplet7`, `tuplet8`, and `tuplet9`.
- Twenty-one taxonomy classes have zero local labels across train/validation/test: `clefUnpitchedPercussion`, `noteheadBlackOnLineSmall`, `noteheadBlackInSpaceSmall`, `noteheadHalfOnLineSmall`, `noteheadHalfInSpaceSmall`, `noteheadWholeOnLineSmall`, `noteheadWholeInSpaceSmall`, `noteheadDoubleWholeOnLineSmall`, `noteheadDoubleWholeInSpaceSmall`, `tremolo5`, `flag8thUpSmall`, `flag8thDownSmall`, `accidentalFlatSmall`, `accidentalNaturalSmall`, `accidentalSharpSmall`, `restHNr`, `graceNoteAcciaccaturaStemUp`, `graceNoteAppoggiaturaStemUp`, `graceNoteAcciaccaturaStemDown`, `graceNoteAppoggiaturaStemDown`, and `tuplet2`.
- The best primary M7 run still has seven validation-supported zero-map classes: `stem`, `ledgerLine`, `articTenutoBelow`, `dynamicR`, `tremolo3`, `tuplet1`, and `tuplet5`.
- The high-support zero-map validation failures are `ledgerLine` and `stem`.
- Raw per-class map values for validation-unsupported classes are ignored by the audit because Ultralytics can emit placeholder values for classes with zero ground-truth support in the evaluated split.

Engineering decision:

- Fine-tuning from the selected checkpoint at image size 1472 with `max_det=2000` is still the best next experiment for improving supported-class validation metrics.
- Fine-tuning on the same local data cannot make the 21 zero-data classes learned classes. Improving full 136-class coverage later requires adding or generating real training labels for those classes, or explicitly narrowing the supported-class claim while preserving the 136-class output contract.
- The test split must remain untouched until the final model and inference configuration are frozen.

## Remaining Weaknesses

- `ledgerLine` and `stem` still have zero mAP despite high support.
- Several articulation and fingering classes remain weak.
- Higher resolution and a realistic detection cap improve the headline metric but do not solve thin-symbol modeling.
- Validation-time augmentation did not help in this experiment.
- The uploaded-image API still uses `heuristic_bootstrap`; detector metric improvement and API detector wiring are separate tasks.
- Twenty-one taxonomy classes have no local labels, so another fine-tune on the same data cannot teach those classes.
- Current validation metrics only measure 103 of 136 classes because 33 taxonomy classes are absent from validation.

## First High-Impact Fine-Tune

The next experiment was a real fine-tune from the selected YOLOv8m checkpoint using the best measured primary-metric scale and the corrected dense-page detection cap:

Launch status:

- Run id: `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`.
- Launched on 2026-06-01 at local time `02:46:32`.
- Parent PID at launch: `34780`, saved in `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune.pid`.
- Active Python child PID observed after launch: `23612`, saved in `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_child.pid`.
- Stdout log: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_stdout.log`.
- Stderr log: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_stderr.log`.
- Launch metadata: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_launch_metadata.json`.
- Startup evidence: Ultralytics loaded `artifacts/models/detection_136class_yolov8m_v1/best.pt`, transferred 475/475 pretrained items, used CUDA on the RTX 3080 Laptop GPU, and started epoch `1/50`.

Interruption, resume, and completion status:

- The first launch stopped after seven completed epochs and while epoch 8 was in progress.
- The run was resumed from the clean epoch-7 `last.pt` checkpoint and later completed all 50 epochs.
- Final V2 `metrics.json`, `analysis.json`, `manifest.json`, `artifacts.json`, `report.md`, `config.yaml`, and `onnx_parity.json` now exist for `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`.
- The clean epoch-7 checkpoint files exist at `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/last.pt` and `best.pt`.
- Completed rows in `results.csv`: 7.
- Best completed primary training-row metric so far: epoch 7, `metrics/mAP50-95(B) = 0.6116`.
- Best completed training-row `metrics/mAP50(B)` so far: epoch 6, `0.79679`.
- These training-row values do not replace the generated V2 validation metric. The run is not complete until the project runner writes `metrics.json`.
- Resume support was added to `scripts/run_detection_136class_yolo.py` in commit `6636622`.
- Resume launch local time: 2026-06-02 `01:05:09`.
- Resume parent PID: `35952`, saved in `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7.pid`.
- Resume active child PID: `43740`, saved in `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7_child.pid`.
- Resume stdout log: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7_stdout.log`.
- Resume stderr log: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7_stderr.log`.
- Resume evidence: Ultralytics reported `Resuming training ... from epoch 8 to 50 total epochs`.
- Final generated AP metrics: `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271`.
- Final generated threshold metrics: `precision@0.5 = 0.8457099520968777`, `recall@0.5 = 0.7738772781467206`, and `F1@0.5 = 0.8082006373091581`.
- Final class analysis: 103 validation-supported classes, 5 supported zero-mAP classes, and small-symbol mean `mAP@0.5:0.95 = 0.5646180558011504`.
- Important per-class result for rhythm: `beam = 0.7824341036579809`, `flag8thUp = 0.7196678490605957`, `flag8thDown = 0.8042434669433673`, and `augmentationDot = 0.25050444606568056`, but `stem = 0.0`. This explains why local demos can often find noteheads/beams/flags/key signatures but still cannot reliably distinguish all stemmed quarters from beamed notes from detector output alone.

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --run-id detection_136class_yolov8m_finetune_img1472_maxdet2000_v1 `
  --model artifacts\models\detection_136class_yolov8m_v1\best.pt `
  --epochs 50 `
  --imgsz 1472 `
  --batch 1 `
  --workers 0 `
  --device 0 `
  --patience 15 `
  --max-det 2000
```

Monitor command:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$run='runs\detection\detection_136class_yolov8m_finetune_img1472_maxdet2000_v1'
Get-Process -Id ([int](Get-Content "$run\resume_epoch7.pid")) -ErrorAction SilentlyContinue
Get-Process -Id ([int](Get-Content "$run\resume_epoch7_child.pid")) -ErrorAction SilentlyContinue
Get-Content -Tail 80 "$run\resume_epoch7_stdout.log"
if (Test-Path "$run\ultralytics\train\results.csv") { Import-Csv "$run\ultralytics\train\results.csv" | Select-Object -Last 1 }
```

If the run is interrupted, first wait for a completed epoch row in `results.csv`, then preserve `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/last.pt`, `best.pt`, `results.csv`, `args.yaml`, `finetune_stdout.log`, `finetune_stderr.log`, `finetune.pid`, `finetune_child.pid`, and `finetune_launch_metadata.json` before stopping.

The completed fine-tune is now the best generated validation detector metric, but it does not solve `stem`.

## Active Follow-Up Fine-Tune

Because `stem` remained at `0.0` after the completed 1472 run, a follow-up run was launched from the completed fine-tune `best.pt` at the stronger 1536 scale:

- Run id: `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`.
- Run directory: `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/`.
- Source checkpoint: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/best.pt`.
- Launch local time: 2026-06-02 `23:11:35`.
- Active parent PID: `34896`, saved in `finetune_v2_retry.pid`.
- Active Python child PID: `28432`, saved in `finetune_v2_retry_child.pid`.
- Stdout log: `finetune_v2_retry_stdout.log`.
- Stderr log: `finetune_v2_retry_stderr.log`.
- Launch metadata: `finetune_v2_retry_launch_metadata.json`.
- Launch settings: `epochs=50`, `imgsz=1536`, `batch=1`, `workers=0`, `device=0`, `patience=15`, `max_det=2000`.
- Startup evidence: Ultralytics loaded the completed fine-tune checkpoint, transferred 475/475 pretrained items, used CUDA on the RTX 3080 Laptop GPU, and reached epoch `1/50`.
- First launch attempt files `finetune_v2_stdout.log` and `finetune_v2_stderr.log` show a pre-training failure caused by incorrect PowerShell expansion of `$env:PYTHONPATH`; ignore that failed attempt and use the `retry` PID/log files.

Monitor command:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$run='runs\detection\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2'
Get-Process -Id ([int](Get-Content "$run\finetune_v2_retry.pid")) -ErrorAction SilentlyContinue
Get-Process -Id ([int](Get-Content "$run\finetune_v2_retry_child.pid")) -ErrorAction SilentlyContinue
Get-Content -Tail 80 "$run\finetune_v2_retry_stdout.log"
if (Test-Path "$run\ultralytics\train\results.csv") { Import-Csv "$run\ultralytics\train\results.csv" | Select-Object -Last 1 }
```

If interrupted, preserve `ultralytics/train/weights/last.pt`, `best.pt`, `results.csv`, `args.yaml`, the retry stdout/stderr logs, the retry PID files, and retry launch metadata before stopping. Resume with `--resume-training --resume-checkpoint runs\detection\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2\ultralytics\train\weights\last.pt`.

## Stem/Rhythm Training Plan

Internet/source-backed guidance points to a targeted thin-symbol plan rather than generic epoch increases:

- DeepScores exists specifically as a tiny-object music-recognition benchmark; DeepScoresV2 stores dense music-object labels and benchmark artifacts. This supports higher-resolution, crop/tile, or small-object-focused experiments instead of relying on whole-page low-scale training.
- MUSCIMA++ defines notation as primitives plus relationships: noteheads, stems, beams, key signatures, and attachment edges. This matches the engineering need for `stem_notehead` and `beam_notegroup` relationships after detection, not just isolated symbol labels.
- Ultralytics documents data augmentation controls such as mosaic and scale, and notes copy-paste is useful for rare objects in segmentation tasks. For this project, copy-paste is not directly available for detect-mode boxes, but the same idea applies to a future synthetic/verified stem-dot dataset or a segmentation/OBB branch.
- Ultralytics OBB docs describe rotated boxes that more tightly enclose objects with orientation. Stems and ledger lines are thin line-like objects where axis-aligned boxes can be weak supervision, so an OBB or segmentation branch is a plausible next experiment if the active detect-mode fine-tune does not move `stem`.

Next concrete experiment after the active v2 run:

1. Evaluate `stem`, `ledgerLine`, `augmentationDot`, `beam`, and `flag*` per-class AP from `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/metrics.json` when it completes.
2. If `stem` remains near zero, generate a tiled/cropped DeepScores training set where each staff-system or measure crop is resized to 1024-1536, remapping existing YOLO labels into tile coordinates. This makes stems and dots larger in model pixels and reduces dense-page object caps.
3. Add a detector-threshold calibration for rhythm symbols separate from notehead thresholding. The note extractor can use a lower confidence for `stem`/`augmentationDot` only if validation/hard-negative checks keep false positives controlled.
4. Add a clean-page CV stem-line attachment fallback as a demo-only bridge while training catches up. It should record `rhythm_source = cv_stem_quarter` so it is never confused with detector evidence.
5. Consider an OBB or segmentation side branch for `stem`/`ledgerLine` if the tiled detect-mode run still cannot localize thin symbols.

## Presentation Guidance

Use this language:

- "Our best completed validation detector is the M7 fine-tuned YOLOv8m run `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`, which reaches `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271` on validation."
- "The earlier dense-page inference sweep on the original full YOLOv8m checkpoint found that `imgsz=1472` and `max_det=2000` were necessary for fair validation on dense music pages."
- "The remaining detector weakness is specific: `stem` remains at `0.0` AP after fine-tuning, so rhythm extraction needs targeted thin-symbol/stem work."

Avoid this language:

- Do not call the sweep a new trained model.
- Do not call the validation result a test result.
- Do not hide the `ledgerLine` and `stem` failures.
- Do not compare `mAP` directly to graph F1.
