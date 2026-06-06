# FilesForDemo Submission Guide

This `FilesForDemo` folder is a clean, submission-oriented package. It is designed so a grader can quickly locate evidence for each rubric dimension without dependency dumps, caches, raw datasets, or debug residue.

## What This Package Contains

- Complete implementation folders: `src/`, `melodious/`, `tests/`, `docker/`, `frontend/`, `tools/`, `sample_detections/`
- Core reports:
  - `README.md`
  - `readme_correction.md` (rubric-to-evidence map)
  - `documentation.md` (canonical experiment/results narrative)
  - `MODEL_CARD.md` (Responsible ML evidence)
  - `presentation_script.md` (PR1-PR4 aligned script)
- Deployment configs:
  - `docker-compose.yml`
  - `requirements.txt`
- Final model artifacts and selected outputs under `outputs/` (including `gnn_checkpoint.pt`, final YOLOv8 extended metrics, ONNX/INT8 exports, robustness/eval logs, and visualizations)
- Live upload demo asset:
  - `demo_upload_images/printed_score_upload_demo.png`
- Rubric references:
  - `project_rubric_assessment_google_sheets (1).xlsm`
  - `project_rubric_assessment_csv_export/`

## Strict Grader Path (Recommended Order)

1. Open `readme_correction.md` for criterion-to-evidence pointers.
2. Verify reproducibility and run commands in `README.md` (`Reproduce Results in 15 Minutes` + `Verified Smoke Run`).
3. Verify technical depth and measured outcomes in `documentation.md`.
4. Verify Responsible ML coverage in `MODEL_CARD.md`.
5. Verify deployment and service structure in `docker-compose.yml` and `src/api/`.
6. Verify checkpoints/outputs in `outputs/`.
7. For live image classification, open `/upload` and use `demo_upload_images/printed_score_upload_demo.png` or a clear printed score photo.

## Fast Verification Commands

```powershell
# From FilesForDemo
.\.venv\Scripts\python.exe -m unittest discover tests

cd frontend
npm install
npm test
npm run build
cd ..

.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

## Important Notes

- This package is built from curated project artifacts, not by raw-copying the full repository.
- If anything appears missing for a specific rubric criterion, check `readme_correction.md` first.
