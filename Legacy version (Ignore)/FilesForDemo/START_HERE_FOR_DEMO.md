# Melodious Demo Start Here

This folder is the clean demo/submission package. It contains runnable source, tests, final artifacts, rubric evidence, slides, sample payloads, and selected outputs. It intentionally excludes raw datasets, dependency folders, caches, duplicate checkpoints, and debug residue.

## Rubric Metadata

| Item | Value |
|---|---|
| Project type | Track A: Applied / Deployment |
| Graph project | Yes |
| Edge/mobile bonus | No, unless separately demonstrated on a real edge/mobile target |
| Main rubric map | `readme_correction.md` |
| Main technical report | `documentation.md` |
| Responsible ML report | `MODEL_CARD.md` |
| Demo script | `presentation_script.md` |

## Demo Order

1. Open `readme_correction.md` to show rubric-to-evidence coverage.
2. Open `documentation.md` for final metrics, baselines, robustness, graph evidence, and limitations.
3. Open `MODEL_CARD.md` for explainability, bias/fairness, privacy, robustness, and deployment limits.
4. Start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

If using the parent checkout's environment, run:

```powershell
..\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 127.0.0.1 --port 8000
```

5. Verify live endpoints:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/product/config
Invoke-RestMethod http://127.0.0.1:8000/product/samples
```

6. Run the frontend in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the desktop site at `http://127.0.0.1:5173`.

## Phone / Camera Demo

Use this when you want to open the website on your phone and take a picture.

1. Put your laptop and phone on the same Wi-Fi network.
2. Find your laptop IPv4 address:

```powershell
ipconfig
```

Look for the Wi-Fi adapter `IPv4 Address`, for example `192.168.1.42`.

3. Start the backend so other devices can reach it:

```powershell
..\.venv\Scripts\python.exe -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

4. Start the frontend with the backend URL set to your laptop IP:

```powershell
cd frontend
npm install
$env:VITE_API_BASE_URL="http://YOUR_LAPTOP_IP:8000"
npm run dev -- --host 0.0.0.0
```

5. On your phone, open:

```text
http://YOUR_LAPTOP_IP:5173/upload
```

6. Tap `Take a picture`, photograph a printed Western score, and wait for the YOLOv8 symbol detections.

If the phone cannot connect, allow Node/Vite and Python/Uvicorn through Windows Firewall, then reload the phone page.

For a reliable live upload test, use `demo_upload_images/printed_score_upload_demo.png`. It returned 87 detections at confidence `0.25` in local verification.

## Verification Commands

From `FilesForDemo/`:

```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
```

or, when using the parent environment:

```powershell
..\.venv\Scripts\python.exe -m unittest discover tests
```

Frontend checks:

```powershell
cd frontend
npm install
npm test
npm run lint
npm run build
cd ..
```

Docker checks:

```powershell
docker compose config
docker build -f docker/Dockerfile.api -t melodious-api-demo .
```

## What To Submit

Submit this `FilesForDemo/` folder as the package. The most important files for graders are:

- `README.md`
- `START_HERE_FOR_DEMO.md`
- `readme_correction.md`
- `documentation.md`
- `MODEL_CARD.md`
- `presentation_script.md`
- `docs/Melodious_Team_Slides.pptx`
- `newRubric.md`
- `MANIFEST_SHA256.txt`

## Honest Full-Grade Risks

These are the items that cannot be fixed by packaging alone:

- Combined YOLO+GNN estimate is `0.358`, below the proposal target of `0.75`.
- The live upload/camera path runs YOLOv8 symbol detection and classification. Full MusicXML/MIDI export for arbitrary uploaded images is not enabled; export remains available through curated sample payloads.
- The API reports the GNN runtime honestly as scaffold/fallback unless a model-specific checkpoint adapter is wired.
- Do not claim the edge/mobile bonus unless you separately demonstrate a real mobile/browser/edge deployment.
