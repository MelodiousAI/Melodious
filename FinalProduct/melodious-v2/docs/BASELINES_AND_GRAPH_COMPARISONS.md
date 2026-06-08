# Baselines and Graph Comparisons

This document collects the baseline evidence needed for the strict Option A and
graph-project rubric checks.

## Baseline Roles

The project has two distinct baseline questions.

| Requirement | Baseline evidence | Purpose |
|---|---|---|
| Option A non-AI baseline | `../outputs/baseline_template_results.json` and `../outputs/baseline_hog_results.json` | Shows that simple visual recognition pipelines are not enough for reliable notation detection. |
| Graph-project non-graph comparison | `runs/graph/graph_non_graph_heuristic_muscima_val_v1/metrics.json` | Compares graph relationship modeling against deterministic local geometry rules on the same MUSCIMA candidate edges. |

These should not be merged into one claim. The first baseline addresses the
application-level need for ML-based symbol recognition. The second baseline
addresses the graph-specific requirement that a graph model be justified against
a non-graph method using the same underlying raw data.

## Non-AI Detection Baselines

Historical root-repo outputs preserve two measured non-AI/classical baselines.

| Method | Evidence file | IoU threshold | Precision | Recall | F1 |
|---|---|---:|---:|---:|---:|
| Template matching | `../outputs/baseline_template_results.json` | 0.50 | 0.1593 | 0.1705 | 0.1647 |
| HOG + SVM | `../outputs/baseline_hog_results.json` | 0.50 | 0.0246 | 0.0014 | 0.0026 |

Interpretation: these baselines are useful as simple-method controls, but their
measured detection quality is not reliable enough for an OMR system that must
build symbolic scores. The final trained detector is therefore evaluated with
the detector metrics in the v2 run folders instead of reusing these F1 values as
the primary detector metric.

Key trained-detector evidence:

| Run | Split | Evidence file | Primary metric | Value | Secondary checks |
|---|---|---|---|---:|---|
| `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` | validation | `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/metrics.json` | mAP@0.5:0.95 | 0.707986237382828 | mAP@0.5 0.8390674529615662, precision@0.5 0.8806427974719793, recall@0.5 0.7881733414248919, F1@0.5 0.8318461933668392 |
| `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final` | test | `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final/metrics.json` | mAP@0.5:0.95 | 0.7070089366721093 | mAP@0.5 0.852207159642617, precision@0.5 0.88660192437495, recall@0.5 0.7956273543690356, F1@0.5 0.8386546975280545 |

## Graph Formulation

The graph task predicts semantic relationships between notation objects.

| Graph component | Definition |
|---|---|
| Node | A detected or MUSCIMA-derived notation object, such as notehead, stem, beam, rest, clef, accidental, or staff-related symbol. |
| Candidate edge | A directed candidate relation proposed by the same local geometric candidate builder. |
| Edge labels | `no_relation`, `stem_notehead`, `beam_notegroup`, `slur_phrase`, `tie_sustained`. |
| Features | Node class/geometry features plus edge geometry and candidate-type features. |
| Prediction | Edge relationship class used by assembly/export logic. |
| Evaluation distribution | Natural candidate-edge distribution, with no negative subsampling at evaluation time. |

The graph is not only a visualization. Relationship prediction is the modeling
task that turns independent detections into structured music notation.

## Graph vs Non-Graph Comparison

Both runs below evaluate the same 14 validation pages, the same 48,174 candidate
edges, the same 6,340 positive edges, and the same candidate-graph builder
configuration. This keeps the comparison focused on relational modeling rather
than extra data.

| Method | Evidence file | Uses message passing | Uses learned edge classifier | Positive macro F1 | Accuracy |
|---|---|---:|---:|---:|---:|
| Legacy GNN relationship model | `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json` | yes | yes | 0.7590456327823909 | 0.9049902436999211 |
| Deterministic local geometry rules | `runs/graph/graph_non_graph_heuristic_muscima_val_v1/metrics.json` | no | no | 0.621796846824738 | 0.7601818408270021 |

Per-class relationship evidence:

| Method | `stem_notehead` F1 | `beam_notegroup` F1 |
|---|---:|---:|
| Legacy GNN relationship model | 0.6960721184803607 | 0.8220191470844213 |
| Deterministic local geometry rules | 0.45783505154639176 | 0.7857586421030842 |

Interpretation: the deterministic baseline has high recall because broad local
rules over-predict positive relationships. The graph model keeps the same
candidate edge universe but uses relational features and learned decision
boundaries, improving the relationship metric that is central to the graph
track.

## Reproduction Commands

From `melodious-v2/`:

```powershell
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\evaluate_non_graph_muscima.py
```

Detector final test evaluation, using the frozen best checkpoint:

```powershell
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --run-id detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final `
  --finalize-existing-run `
  --train-dir runs\detection\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2\ultralytics\train `
  --checkpoint runs\detection\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2\ultralytics\train\weights\best.pt `
  --split test --imgsz 1536 --batch 1 --workers 0 --device 0 --max-det 2000 --skip-export
```

## Limitations

- The graph validation split has no support for `slur_phrase` and
  `tie_sustained`, so the main graph comparison is strongest for
  `stem_notehead` and `beam_notegroup`.
- The GNN checkpoint is a legacy 15-class relationship model evaluated through
  the v2 graph/evaluation code. The detector is the newer 136-class model.
- End-to-end export validity in
  `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json` uses MUSCIMA
  XML-derived payload fixtures. It proves graph/export integration and artifact
  generation, but it is not a full uploaded-image detector-to-export test.
