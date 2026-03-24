# Hasan Meeting Handoff

This folder contains the detector-side handoff package for graph integration.

## What Is Ready

- Contract definition: `sample_detections/FORMAT.md`
- Class mapping: `sample_detections/class_mapping.json`
- Export helper for real detector outputs: `melodious/generate_detections.py`
- Export helper for reference payloads from labeled pages: `melodious/export_reference_detections.py`

## Payload Files

- Reference payloads: `sample_detections/reference/` — ground-truth annotations from labeled DeepScores test pages
- Model outputs: `sample_detections/model_outputs_quick/` — real YOLOv8s inference outputs
- Each JSON file corresponds to one real DeepScores page image
- `image_path` points to the matching source page

### Included Right Now

- 5 reference payloads from labeled test pages (ground-truth, confidence=1.0)
- 5 real detector payloads from YOLOv8s (mAP50=0.584) trained 30 epochs on DeepScores v2 Dense
- Model: `outputs/yolov8_runs/train/weights/best.pt`
- Pages: 5 different pages from `dataset_ds2_dense/images/lg-101766503886095953-*`

## Stable Contract

- Confidence field name: `confidence`
- Normalized bbox convention: center-based
- Normalized bbox keys: `x_center`, `y_center`, `width`, `height`
- Debug pixel bbox keys: `x1`, `y1`, `x2`, `y2`
- Class IDs must match `sample_detections/class_mapping.json`

## Important Distinction

- `reference-ground-truth` payloads are exported from dataset annotations (confidence=1.0), safe for graph integration testing
- `yolov8` payloads are from the real trained detector (mAP50=0.584) and are the primary integration target

## Matching Image Path Rule

- Use the top-level `image_path` in each JSON as the canonical page path
- Do not infer image locations from JSON filenames alone

## Next Command For Real Detector Outputs

When a stronger valid checkpoint exists:

```powershell
C:/Users/ahmad/OneDrive/Desktop/Melodious_Initial_Code/.venv/Scripts/python.exe -m melodious.generate_detections --model-type custom --checkpoint outputs/yolo_epoch_8.pth --image-dir dataset_ds2_dense/images --output-dir sample_detections/model_outputs --limit 5 --conf-thresh 0.3 --img-size 640
```

## Meeting Recommendation

- Use `sample_detections/reference/` to let Hassan start graph parsing and schema integration immediately
- Show `sample_detections/model_outputs_quick/` only as proof that the export path works end to end from a real checkpoint
- Do not present the quick checkpoint as a meaningful detector baseline