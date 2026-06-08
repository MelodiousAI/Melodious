# Responsible ML

The rubric asks for at least three Responsible ML topics. This project addresses
all four: explainability, fairness/bias, privacy/leakage, and robustness.

## RM1 Explainability

Evidence:

- `MODEL_CARD.md`
- `docs/METRICS.md`
- `runs/detection/detection_136class_class_coverage_audit_v1/class_coverage.md`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final/metrics.json`
- `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`
- Product API and frontend confidence/explainability panels under `src/` and
  `frontend/`

The system exposes confidence and class-level detection metrics, graph
relationship labels, and an attention-preview contract for future graph
explanations. The most useful reviewer-facing explanation is the structured
pipeline itself: detector boxes become graph nodes, candidate edges become
relationship decisions, and accepted relationships become MusicXML/MIDI export
artifacts.

Known explainability limit: the final graph checkpoint evidence does not expose
human-readable attention weights as a validated metric. The UI and API have the
field surface for this, but the final report should describe current
explainability as confidence, class coverage, relationship outputs, and
per-class error reports rather than claiming production-grade attention
interpretability.

## RM2 Fairness and Bias

Evidence:

- `docs/DATA_CARD.md`
- `runs/detection/detection_136class_class_coverage_audit_v1/class_coverage.json`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final/metrics.json`
- `docs/BASELINES_AND_GRAPH_COMPARISONS.md`

The main fairness risk is representation bias across notation classes, fonts,
engraving styles, symbol sizes, and rare symbols. This is not demographic
fairness, but it is still an unequal-performance problem: common noteheads,
clefs, rests, and accidentals have much stronger support than rare articulation,
tuplet, tremolo, and line-like classes.

Mitigations already present:

- Class-coverage audit separates supported classes from zero-label or
  unsupported classes.
- Per-class metrics identify weak classes instead of hiding them behind an
  aggregate.
- Tiled stem pilot artifacts are retained because line-like symbols such as
  stems and ledger lines are known weaknesses.
- The model card records limits rather than claiming all notation styles are
  solved.

Presentation wording should be direct: the system is strongest on printed
Western notation similar to the training data and weaker on rare symbols,
handwritten notation, scans with layout distortions, and class types with poor
support.

## RM3 Privacy and Leakage

Evidence:

- `docs/DATA_CARD.md`
- `docs/METRICS.md`
- `infra/aws/README.md`
- Dataset manifests and split-specific metrics under `runs/`
- API/service code under `src/melodious_v2/`

Privacy risk is lower than in personal-data projects because the training data
and demo payloads are public or project-local sheet-music artifacts, not user
identity data. The deployed service still needs careful handling because user
uploads may contain copyrighted, unpublished, or personally identifying markings.

Controls and notes:

- The API is designed around request/response processing rather than permanent
  upload storage.
- Final submission metrics distinguish validation, test, and holdout fixture
  splits.
- The documentation separates generated outputs, source code, and model
  artifacts.
- Reproducible manifests reduce accidental leakage from mixing train, validation,
  and test evidence.

Known privacy/leakage limits:

- A real production deployment should add upload retention controls, logging
  redaction, and an explicit user-data policy.
- The final detector test run uses the same frozen checkpoint as the validation
  run; it should be described as final held-out evaluation of the selected model,
  not as a new model-selection pass.

## RM4 Robustness and Distribution Shift

Evidence:

- `../outputs/robustness/robustness_results.json`
- `../outputs/robustness/robustness_curves.png`
- `../outputs/robustness/robustness_per_class.png`
- `MODEL_CARD.md`
- `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`

The older robustness outputs test JPEG compression, Gaussian noise, and rotation
conditions. They show that compression and light noise are manageable for the
older detector baseline, while heavier noise and rotation-style perturbations
need caution. The rotation results should be discussed carefully because label
geometry was not rotated in the same way as the image perturbation, making those
numbers a stress-test artifact rather than a clean deployment estimate.

Additional robustness practices in v2:

- End-to-end export fixtures validate that the graph/export path can generate
  MusicXML and MIDI for 14 holdout MUSCIMA payload pages.
- Local deployment smoke tests exercise the public product API route and export
  flow.
- Model and data documentation record known failure modes: line-like objects,
  dense notation, rare classes, handwritten scores, degraded scans, and symbols
  outside the detector taxonomy.

## Responsible Deployment Summary

The final submission should claim these Responsible ML topics explicitly:

| Topic | Status | Short claim to use |
|---|---|---|
| Explainability | Addressed | Confidence, class coverage, graph relationships, and per-class reports make errors inspectable. |
| Fairness/bias | Addressed | The project audits class imbalance and identifies weak symbol groups. |
| Privacy/leakage | Addressed | Upload processing avoids permanent storage by design, and split-specific manifests reduce evaluation leakage. |
| Robustness | Addressed | Noise/compression stress tests, holdout export fixtures, and documented shift limits are included. |

Do not overclaim perfect safety. The strongest responsible-ML answer is that the
project measures and documents the limits a deployer would need before using the
system on arbitrary scores.
