# AGENTS Workspace Rules - Melodious V2

These rules apply to all future work in this repository.

## Git Workflow

- Work in this clean V2 repository, not in the legacy Melodious checkout.
- Create a phase branch before meaningful work: `phase/01-contracts`, `phase/02-metrics`, etc.
- Do not commit generated datasets, checkpoints, model caches, ad hoc debug folders, or AWS secrets.
- Commit coherent units only: contracts, metrics, detector training, graph assembly, API, UI, deploy.

## Metric Discipline

- Never compare `mAP50` to an `F1` target. They are different metrics.
- Never hand-edit final metric numbers into docs. Metrics must come from `runs/**/metrics.json`.
- Every reported claim must include a `run_id`, config path, checkpoint/artifact hash, and evaluation split.
- Detector primary metric is `mAP@0.5:0.95`; detector secondary metrics are `mAP@0.5`, precision, recall, and `F1@IoU=0.5`.
- Graph primary metric is positive-class macro F1 on the natural edge distribution. Report `no_relation` separately.
- End-to-end quality must be measured on fixed holdout pages. Estimates must be labeled `estimate`, not `measured`.

## Code Quality

- Keep data prep, training, metrics, assembly, export, API, frontend, and deployment separated.
- Use typed payload contracts at API and artifact boundaries.
- Add tests for metric math before trusting any experiment output.
- Keep fallback paths explicit in code and response metadata.

## Documentation Discipline

- `docs/STATUS.md` records current phase, blockers, and next action.
- `docs/EXPERIMENTS.md` is an index of generated run artifacts, not a place to invent numbers.
- `docs/RUBRIC_MAP.md` maps rubric claims to exact repo evidence.
- `docs/METRICS.md` is the authority for metric definitions.
- `MODEL_CARD.md` is the authority for limitations, bias, privacy, robustness, and deployment risks.

## AWS and Secrets

- Use GitHub Actions OIDC or local AWS profiles. Do not commit AWS access keys.
- Do not commit presigned URLs, private bucket names, account IDs, or `.env` files.
- Prefer low-cost CPU ONNX serving on ECS Express Mode or ECS Fargate.
- Do not use AWS App Runner for new accounts because AWS stopped accepting new App Runner customers on April 30, 2026.

