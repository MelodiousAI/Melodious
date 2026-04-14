# Data Split Manifest — Melodious OMR Project

This document records the exact train/validation/test splits used for
all experiments, ensuring reproducibility.

## YOLOv8s Detection — DeepScores v2 Dense

| Split  | Images | Source                      |
|--------|--------|-----------------------------|
| Train  | 1,362  | `yolo_dataset/images/train` |
| Val    | 352    | `yolo_dataset/images/val`   |

Split created by `setup_yolo_dataset.py` from `dataset_ds2_dense/`.
No separate held-out test set — the 352-image validation set serves as
the test set (standard DeepScores V2 practice; train/test listed in the
original JSON manifests `deepscores_train.json` / `deepscores_test.json`).

### File hashes (SHA-256)

```
train.txt  72f65a086817a8d1289d8d246e6ae8c83ea59af3273b3907068fb65278f822a3
test.txt   7cb77fed1a0c902bbc7ff4fca1c363d97a75a1c1aab72d10103b7ddbb0ef61df
```

### Class list (15 classes)

0: notehead-full, 1: notehead-half, 2: notehead-whole,
3: clefG, 4: clefF, 5: clefC,
6: rest-8th, 7: rest-quarter, 8: rest-half, 9: rest-whole,
10: accidentalSharp, 11: accidentalFlat, 12: accidentalNatural,
13: beam, 14: stem

## GNN Assembler — MUSCIMA++ v2.0

| Split | Pages | Source |
|-------|-------|--------|
| Train | 112   | `data/muscima-pp/v2.0/data/annotations/` |
| Val   | 28    | Same (80/20 split, `seed=42`) |

Split performed by `melodious/gnn_data_loader.py:load_muscima_dataset(val_ratio=0.2, seed=42)`.
Total: 140 annotated pages, filtered to 15-class subset.

## Cross-Domain Evaluation — CVC-MUSCIMA

| Dataset | Images | Source |
|---------|--------|--------|
| CVC-MUSCIMA WI | 1,000 (50 writers × 20 pages) | `data/cvc-muscima/CVCMUSCIMA_WI/PNG_GT_Gray/` |

Used for distribution-shift analysis (print → handwritten).
50 images sampled per domain per evaluation run (`seed=42`).

## Random Seeds

All experiments use `seed=42` unless otherwise noted.
Seed utility: `melodious/seed.py:set_seed(42)`.
