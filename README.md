# Melodious

Optical music recognition (OMR) for sheet music: detect symbols, assemble relationships, and export MusicXML/MIDI with a polished web app.

## Start Here

| Path | What it is |
|------|------------|
| [`melodious-v2/`](melodious-v2/) | **Current product** — API, detector, graph assembly, React UI, tests, and docs |
| [`FinalProduct/`](FinalProduct/) | **Curated submission package** — rubric evidence, presentation, legacy baselines, and selected run artifacts |
| [`sample_detections/`](sample_detections/) | Shared detector payload contract examples |

The latest application code and light editorial UI live on the **`v2`** branch (now merged into **`main`**). Use `melodious-v2/` for development and `FinalProduct/README.md` for grading evidence.

## Quick Start (Melodious V2)

**Backend**

```powershell
cd melodious-v2
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python scripts\run_api.py
```

**Frontend**

```powershell
cd melodious-v2\frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173` for the UI and `http://127.0.0.1:8000/health` for the API.

## Legacy Code

Older consolidation branches (`src/`, root `frontend/`, `demo/`) remain in the repository for history. New work should target `melodious-v2/` only.

## Documentation

- [`melodious-v2/README.md`](melodious-v2/README.md) — setup, API, deployment
- [`melodious-v2/docs/FINAL_RUBRIC_EVIDENCE.md`](melodious-v2/docs/FINAL_RUBRIC_EVIDENCE.md) — rubric checklist
- [`melodious-v2/docs/FINAL_TECHNICAL_REPORT.md`](melodious-v2/docs/FINAL_TECHNICAL_REPORT.md) — technical report
- [`FinalProduct/SUBMISSION_MANIFEST.md`](FinalProduct/SUBMISSION_MANIFEST.md) — submission inventory
