# Metrics Registry

This file is the authority for metric names, definitions, and allowed comparisons.

## Detector Metrics

Primary detector metric:

- `mAP@0.5:0.95`: mean average precision averaged over IoU thresholds `0.50, 0.55, ..., 0.95`.

Secondary detector metrics:

- `mAP@0.5`: mean average precision at IoU `0.50`.
- `precision@0.5`: micro precision after greedy confidence-sorted matching at IoU `0.50`.
- `recall@0.5`: micro recall after greedy confidence-sorted matching at IoU `0.50`.
- `F1@0.5`: harmonic mean of `precision@0.5` and `recall@0.5`.
- `per_class_ap@0.5`: AP at IoU `0.50` per class with ground-truth support.
- `per_class_f1@0.5`: matched F1 per class at IoU `0.50`.

Rules:

- `mAP` is not `F1`.
- `mAP@0.5` may be compared only to another `mAP@0.5`.
- `F1@0.5` may be compared only to another `F1@0.5`.
- Threshold selection must use validation data only.
- Test metrics are reported once per final model family.

## Graph Metrics

Primary graph metric:

- `positive_macro_f1`: macro F1 over relationship classes excluding `no_relation`, evaluated on natural edge distribution.

Required secondary graph metrics:

- `no_relation` precision, recall, F1, and support.
- Per-positive-class precision, recall, F1, and support.
- Positive-class confusion counts.

Rules:

- Overall accuracy cannot be the primary graph metric because `no_relation` dominates.
- Weighted F1 cannot be the headline graph metric if `no_relation` dominates.
- Negative subsampling metrics must be labeled `sampled_distribution`.
- Natural-distribution metrics must be labeled `natural_distribution`.

## End-to-End Metrics

Primary end-to-end metric:

- Measured relationship/export quality on fixed holdout pages with real detector outputs.

Allowed supporting metrics:

- MusicXML validity rate.
- MIDI generation success rate.
- Structure-level similarity such as tree edit distance.
- Latency percentiles for upload-to-artifact completion.

Rules:

- Multiplying detector and graph scores is an estimate, not a measured end-to-end result.
- Any estimate must include `metric_kind = "estimate"`.
- Any measured result must include the holdout manifest and run ids.

## Provenance Requirements

Every metric JSON must include:

- `run_id`
- `commit`
- `config_path`
- `dataset_id`
- `split`
- `taxonomy_id`
- `metric_version`
- `created_at`
- `artifact_sha256` when a model/checkpoint is evaluated

