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

## Interpretation

The professor-facing detector number should now use `detection_136class_yolov8m_eval_img1248_v1` when discussing validation-time inference quality. The model itself did not change, so this is best described as an improved inference configuration for the same full-taxonomy YOLOv8m checkpoint.

This is still not a test-set result. The test set should stay untouched until the team freezes the final model and inference configuration.

## Remaining Weaknesses

- `ledgerLine` and `stem` still have zero mAP despite high support.
- Several articulation and fingering classes remain weak.
- Higher resolution improves the headline metric but does not solve thin-symbol modeling.
- Validation-time augmentation did not help in this experiment.
- The uploaded-image API still uses `heuristic_bootstrap`; detector metric improvement and API detector wiring are separate tasks.

## Next High-Impact Experiment

The next experiment should be a real fine-tune from the selected YOLOv8m checkpoint using the best measured inference scale:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --run-id detection_136class_yolov8m_finetune_img1248_v1 `
  --model artifacts\models\detection_136class_yolov8m_v1\best.pt `
  --epochs 50 `
  --imgsz 1248 `
  --batch 2 `
  --workers 0 `
  --device 0 `
  --patience 15
```

If the run is interrupted, preserve `runs/detection/detection_136class_yolov8m_finetune_img1248_v1/ultralytics/train/weights/last.pt` before stopping.

After training completes, finalize normally through the same script, regenerate `docs/EXPERIMENTS.md`, and compare only validation metrics until the model family is frozen.

## Presentation Guidance

Use this language:

- "Our best validation detector configuration uses the full 136-class YOLOv8m checkpoint at 1248 inference size and reaches `mAP@0.5:0.95 = 0.5058429013539956` and `mAP@0.5 = 0.6069618791829888`."

Avoid this language:

- Do not call the sweep a new trained model.
- Do not call the validation result a test result.
- Do not hide the `ledgerLine` and `stem` failures.
- Do not compare `mAP` directly to graph F1.
