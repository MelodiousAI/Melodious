# Strict Grade Risk Checklist

This checklist is intentionally strict. It highlights items that can still cost points even with a strong repository.

## Likely Remaining Risk Areas

- **Combined target gap:** end-to-end combined YOLO+GNN estimate is still below the proposal target.
- **Graph fairness proof quality:** ensure demo clearly explains same-input parity between graph and non-graph comparisons.
- **Deployment interpretation:** if grader expects publicly hosted service (not only local/docker), this may reduce EN5.
- **Presentation score dependency:** PR1–PR4 still depends heavily on live delivery and Q&A ownership.

## Pre-Submission Actions (High Priority)

1. Rehearse `presentation_script.md` end-to-end with a timer.
2. Keep one canonical narrative: use `documentation.md` for results, avoid citing old checklist text.
3. During presentation, explicitly acknowledge failure modes and target gaps before being asked.
4. If possible, show a running API demo live from this package (`uvicorn` + endpoint check).

## Grader-Facing Honesty Statement

If asked about unmet targets, use this framing:

- We met many core engineering and modeling deliverables with reproducible evidence.
- We did not fully close the end-to-end performance target.
- We provide concrete analysis of why, and a technically realistic plan for closing the gap.
