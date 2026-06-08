# Melodious Final Product

This folder is the curated final submission package for the Melodious OMR
project. It contains the v2 source code, final rubric evidence, selected model
artifacts, selected experiment outputs, presentation material, sample inputs,
and legacy baseline evidence.

Final inventory: 453 files, about 548 MB. Most of the size comes from the
selected PT/ONNX model artifacts.

Start here:

1. Read `melodious-v2/docs/FINAL_RUBRIC_EVIDENCE.md`.
2. Read `melodious-v2/docs/FINAL_TECHNICAL_REPORT.md`.
3. Use `SUBMISSION_MANIFEST.md` to locate evidence by folder.
4. Use `OMITTED_FILES.md` to see what was deliberately left out of the package.

## Main Evidence

| Rubric need | Best evidence |
|---|---|
| Option A problem fit | `melodious-v2/README.md`, `melodious-v2/docs/FINAL_TECHNICAL_REPORT.md` |
| Non-AI baseline | `melodious-v2/docs/BASELINES_AND_GRAPH_COMPARISONS.md`, `legacy_evidence/baseline_template_results.json`, `legacy_evidence/baseline_hog_results.json` |
| Graph core and graph comparison | `melodious-v2/docs/BASELINES_AND_GRAPH_COMPARISONS.md`, `melodious-v2/runs/graph/` |
| Final detector metrics | `melodious-v2/runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2_test_final/metrics.json` |
| Responsible ML | `melodious-v2/docs/RESPONSIBLE_ML.md` |
| Deployment/API/UI | `melodious-v2/README.md`, `melodious-v2/infra/`, `melodious-v2/frontend/` |
| Presentation | `presentation/` |

## Run Locally

Backend:

```powershell
cd FinalProduct\melodious-v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python scripts\run_api.py
```

Frontend:

```powershell
cd FinalProduct\melodious-v2\frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` for the UI and
`http://127.0.0.1:8000/health` for the API.

Docker API:

```powershell
cd FinalProduct\melodious-v2
docker compose up --build
```

## Verification Commands

From `FinalProduct\melodious-v2`:

```powershell
$env:PYTHONPATH = "src"
python -m pytest -q
python scripts\validate_metric_claims.py
```

From `FinalProduct\melodious-v2\frontend`:

```powershell
npm run build
```

## Verification Results

Latest local checks from this workspace:

| Check | Location | Result |
|---|---|---|
| Python test suite | `FinalProduct\melodious-v2` | `72 passed`, one upstream `torch_geometric` deprecation warning |
| Metric-claim guardrail | `FinalProduct\melodious-v2` | Checked 16 packaged documentation files |
| Frontend production build | `melodious-v2\frontend`, then copied into `FinalProduct\melodious-v2\frontend\dist` | Passed |

## Important Caveats

- Public AWS smoke evidence is not included because AWS account-local values are
  not available in this workspace.
- The end-to-end export fixture run uses MUSCIMA XML-derived payloads. It proves
  graph/export integration and artifact generation, not arbitrary real-scan
  accuracy.
- The graph checkpoint is a legacy 15-class relationship model. The detector is
  the newer 136-class YOLOv8m model.
- Line-like classes such as `stem` and `ledgerLine` remain known detector
  limitations on full-page evaluation.
