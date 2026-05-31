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

## Next High-Impact Experiment

The next experiment should be a real fine-tune from the selected YOLOv8m checkpoint using the best measured primary-metric scale and the corrected dense-page detection cap:

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

If the run is interrupted, preserve `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/last.pt` before stopping.

After training completes, finalize normally through the same script, regenerate `docs/EXPERIMENTS.md`, and compare only validation metrics until the model family is frozen.

## Presentation Guidance

Use this language:

- "Our best primary validation detector configuration uses the full 136-class YOLOv8m checkpoint at image size 1472 with a dense-page detection cap of 2000 and reaches `mAP@0.5:0.95 = 0.6204968163150985`."
- "For the more optimistic validation metric, the best current configuration reaches `mAP@0.5 = 0.7920129156176505` at image size 1536 with the same 2000 detection cap."

Avoid this language:

- Do not call the sweep a new trained model.
- Do not call the validation result a test result.
- Do not hide the `ledgerLine` and `stem` failures.
- Do not compare `mAP` directly to graph F1.
