# Omitted Files

The final package is curated. These files and folders were intentionally left
out to keep the submission clean and reviewable.

## Dependency and Cache Folders

| Omitted | Reason |
|---|---|
| `.venv/` | Local Python virtual environment, not submission material. |
| `node_modules/` | Recreated by `npm install`; too large and not source evidence. |
| `.pytest_cache/`, `__pycache__/`, `.mypy_cache/`, `.ruff_cache/` | Generated caches. |
| `frontend/tsconfig.tsbuildinfo` | Local TypeScript incremental build cache. |
| `logs/` | Local runtime logs, not stable evidence. |

## Raw or Large Dataset Materializations

| Omitted | Reason |
|---|---|
| Full YOLO image/label materializations under `runs/data/**/images` and `runs/data/**/labels` | Large generated dataset files; manifests and leakage reports are included instead. |
| Full tiled stem dataset materialization | Very large generated training data; pilot manifests and metrics are included. |
| Older root `data/`, `dataset_ds2_dense/`, `yolo_dataset/`, `MUSICMA_Sample/` trees | Legacy or raw data trees outside the final v2 evidence path. |

## Intermediate and Superseded Runs

| Omitted | Reason |
|---|---|
| Detector resolution-sweep runs not selected for final evidence | Superseded by the selected validation run and final test run. |
| Detector smoke/preflight runs | Useful during development but not final-grade evidence. |
| Duplicate weights inside selected run logs | The canonical checkpoints are included under `melodious-v2/artifacts/models/`. |
| Demo checkpoint snapshots such as `best_snapshot.pt` inside `runs/demo/` | Duplicate model files; demo outputs and centralized checkpoints are included. |
| Earlier demo attempts such as old Sad Romance, image, and Espresso retries | Superseded by the final selected demo runs. |

## Internal Agent and Handoff Notes

| Omitted | Reason |
|---|---|
| `melodious-v2/docs/AGENT_PROMPTS.md` | Internal coding-agent prompt history, not needed for grading. |
| `melodious-v2/docs/HANDOFF.md` | Internal handoff ledger, very large and not necessary once final evidence docs exist. |
| Some older root-level instructions/documentation files | Superseded by final v2 docs and package-level manifest. |

## Base Weights and Local Experiment Residue

| Omitted | Reason |
|---|---|
| `yolo11n.pt`, `yolov8s.pt`, `melodious-v2/yolo11n.pt`, `melodious-v2/yolov8m.pt` | Base/backbone weights, not the final trained artifacts. |
| Ad hoc debug scripts and sandbox files outside v2 | Not part of the final product path. |
| Full original `demo/` and `FilesForDemo/` copies | Older package attempts superseded by `FinalProduct/`. |

## Not Available in This Workspace

| Missing | Reason |
|---|---|
| Public AWS smoke result | AWS CLI access and account-local values were not available in this workspace. Local smoke evidence is included. |
| Account-local AWS identifiers | Region/profile, role ARNs, subnet IDs, security groups, target groups, S3 bucket names, CloudFront distribution IDs, and API host values should not be committed. |

The omitted items are not needed to inspect the final methodology, run the code,
review the selected artifacts, or verify the final rubric evidence.
