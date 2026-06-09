# Demo Submission Guide (Strict Rubric-Oriented)

This `demo` folder is a copied, submission-oriented package. It is designed so a grader can quickly locate evidence for each rubric dimension.

## What This Package Contains

- Complete implementation folders: `src/`, `tests/`, `docker/`, `frontend/`, `tools/`, `sample_detections/`
- Core reports:
  - `README.md`
  - `readme_correction.md` (rubric-to-evidence map)
  - `documentation.md` (canonical experiment/results narrative)
  - `MODEL_CARD.md` (Responsible ML evidence)
  - `presentation_script.md` (PR1-PR4 aligned script)
- Deployment configs:
  - `docker-compose.yml`
  - `requirements.txt`
- Model artifacts and checkpoints under `outputs/` (including `gnn_checkpoint.pt`, YOLO runs, ONNX logs, robustness/eval logs)
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

## Fast Verification Commands

```powershell
# From demo folder
.\.venv\Scripts\python.exe -m unittest discover tests

cd frontend
npm install
npm test
npm run build
cd ..

.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

## Important Notes

- This package is built by **copying** source artifacts from the project root.
- If anything appears missing for a specific rubric criterion, check `readme_correction.md` first.
