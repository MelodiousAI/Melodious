# Detector Class Coverage Audit

- Generated at: `2026-05-31T23:39:36Z`
- Manifest directory: `C:/Users/ahmad/OneDrive/Desktop/Melodious_Initial_Code/melodious-v2/runs/data/deepscores_136_manifest`
- Evaluation split: `val`
- Taxonomy classes: `136`
- Classes with any local labels: `115`
- Classes with zero labels across train/val/test: `21`
- Evaluation-supported classes: `103`
- Evaluation blind spots: `33`
- Zero-map supported classes: `7`
- High-support zero-map supported classes: `2`

## Split Support

- `train`: `115` supported classes, `21` absent classes, `1226` images, `793828` annotations
- `val`: `103` supported classes, `33` absent classes, `136` images, `96005` annotations
- `test`: `110` supported classes, `26` absent classes, `352` images, `244335` annotations

## Evaluated Metrics Source

- Run id: `detection_136class_yolov8m_eval_img1472_maxdet2000_v1`
- Source: `C:/Users/ahmad/OneDrive/Desktop/Melodious_Initial_Code/melodious-v2/runs/detection/detection_136class_yolov8m_eval_img1472_maxdet2000_v1/metrics.json`
- Split: `val`
- Primary metric: `mAP@0.5:0.95`
- Primary value: `0.6204968163150985`
- `mAP@0.5`: `0.7833788545364062`
- `precision@0.5`: `0.8166240104606699`
- `recall@0.5`: `0.7367130723503518`
- `F1@0.5`: `0.7746130448554269`

## Zero-Data Taxonomy Classes

- `clefUnpitchedPercussion`
- `noteheadBlackOnLineSmall`
- `noteheadBlackInSpaceSmall`
- `noteheadHalfOnLineSmall`
- `noteheadHalfInSpaceSmall`
- `noteheadWholeOnLineSmall`
- `noteheadWholeInSpaceSmall`
- `noteheadDoubleWholeOnLineSmall`
- `noteheadDoubleWholeInSpaceSmall`
- `tremolo5`
- `flag8thUpSmall`
- `flag8thDownSmall`
- `accidentalFlatSmall`
- `accidentalNaturalSmall`
- `accidentalSharpSmall`
- `restHNr`
- `graceNoteAcciaccaturaStemUp`
- `graceNoteAppoggiaturaStemUp`
- `graceNoteAcciaccaturaStemDown`
- `graceNoteAppoggiaturaStemDown`
- `tuplet2`

## Train-Supported But Validation-Absent Classes

- `timeSig5`
- `timeSig7`
- `tremolo1`
- `tremolo4`
- `flag32ndUp`
- `accidentalDoubleFlat`
- `articStaccatissimoBelow`
- `fingering5`
- `tuplet4`
- `tuplet7`
- `tuplet8`
- `tuplet9`

## Zero-Map Supported Validation Classes

- `stem`
- `ledgerLine`
- `articTenutoBelow`
- `dynamicR`
- `tremolo3`
- `tuplet1`
- `tuplet5`

## Interpretation

- The detector head has 136 output classes, but coverage quality is constrained by the local labels.
- Classes absent from `train` cannot be learned by another fine-tune on the same data.
- Classes absent from `val` cannot be validated honestly on the current validation split.
- The next fine-tune is still useful for supported classes, but final claims must separate supported-class metrics from full-taxonomy coverage limitations.
