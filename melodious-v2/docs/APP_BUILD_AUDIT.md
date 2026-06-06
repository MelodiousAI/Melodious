# App Build Audit

Date: 2026-06-06

Purpose: identify the newest frontend upload page, backend product routes, and missing work needed to turn Melodious V2 into a presentation-grade upload-to-MusicXML/MIDI application.

## Branches And Commits Checked

The repository remotes were fetched before this audit. The newest remote branch by date, `origin/cursor/upload-transcription-d2d5`, only contains test-skip changes and does not contain a newer app surface.

Useful app-related references:

| Reference | What It Contains | App Value |
| --- | --- | --- |
| `phase-04-assembly` at `245e3a6` | Current Melodious V2 package, metric documentation, FastAPI `/transcriptions`, simple React upload page, local YOLO/tiled/GNN note-extraction CLI | Best backend/model/export base |
| `caba712` (`feat: add product image upload transcription`) | Product upload frontend, workspace frontend, MIDI player component, product API models/routes/service, upload save/download flow | Best old product app source |
| `origin/hassan/week-5` at `1cd27c6` | Public product frontend with upload/workspace/library pages and product API facade | Best branch-head UI source |
| `origin/hassan/week-4` at `6b13ff6` | GNN-ready backend and Streamlit MVP | Useful historical GNN/backend context |
| `origin/consolidation/full-solution-no-eval` at `2c8e2af` | Consolidated legacy code before the V2 rebuild | Historical reference only |

## Best Available Frontend

The strongest upload/workspace frontend is from `caba712` / `origin/hassan/week-5`.

Important files:

- `frontend/src/pages/UploadPage.tsx`
- `frontend/src/pages/WorkspacePage.tsx`
- `frontend/src/components/MidiPlaybackCard.tsx`
- `frontend/src/components/UploadPanel.tsx`
- `frontend/src/components/StatusPanel.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/types/product.ts`
- `frontend/src/mocks/product.ts`

Capabilities already present in that old frontend:

- Drag-and-drop upload and file validation.
- Upload/camera segmented mode UI.
- Transcription success/error states.
- Download links for MusicXML and MIDI.
- Workspace-style result page with score preview, status metrics, confidence cue, playback panel, and result summary.
- `html-midi-player` based MIDI playback component.
- `lucide-react`, `framer-motion`, `react-router-dom`, Tailwind-based UI structure.

Why it should not be copied blindly:

- It targets the older `src.api` package layout, not `src/melodious_v2`.
- Some score preview pieces are illustrative placeholders rather than rendered output from the latest extractor.
- Its backend calls the older `src.inference.image_detector.build_detection_payload_for_image`, not the current V2 local note-extraction path.

## Best Available Backend

The safest backend base is the current `phase-04-assembly` V2 package, not the old product branch.

Current V2 backend strengths:

- Strict V2 detector payload contract.
- Metric provenance discipline.
- GNN checkpoint/fallback metadata.
- MusicXML and MIDI export functions.
- Local clean-sheet extraction CLI at `scripts/extract_notes_from_image.py`.
- Latest local extractor improvements for staff systems, rests, beams, slurs/ties, accidental attachment, open-note dots, tiled thin-symbol inference, and GNN relationship-aware rhythm.

Current V2 backend limitations for a real product app:

- `/transcriptions` accepts uploaded images as base64 JSON, but the upload path still uses `heuristic_bootstrap`.
- The trained YOLO/tiled/GNN note-extraction path is not wired into FastAPI upload.
- Jobs are stored in memory only.
- Artifacts are returned from memory for the simple route, not persisted as durable upload result files.
- Upload responses do not expose the generated overlay PNG, ordered events, note table, staff-system summary, or extraction warnings from the local CLI.
- The API has no multipart `/product/transcribe-image` endpoint in the current V2 package.
- `requirements.txt` currently does not list `python-multipart`, which FastAPI needs for direct browser file uploads through `UploadFile`.

## Missing For A Top-Tier App

Required core pieces:

- A V2 `/product/transcribe-image` endpoint that accepts `UploadFile`, saves the image, runs the real local extraction path, and returns persisted artifact URLs.
- Static artifact serving for original image, overlay PNG, MusicXML, MIDI, detector payload JSON, relationships JSON, and note-event JSON.
- A typed product response contract with note count, rest count, dotted-note count, slur/tie count, stem-confirmed count, staff-system count, model/checkpoint provenance, and warnings.
- Frontend workspace view that displays the uploaded image or overlay, MusicXML text, note/event table, downloads, warnings, and provenance.
- Real MIDI playback in the browser.
- Instrument choice. At minimum this can control client-side MIDI playback instrument; a stronger version also writes the selected General MIDI program into the exported MIDI.
- Clear result quality states so demo users understand when output is high confidence, needs review, or uses fallback heuristics.

Presentation-grade additions:

- Side-by-side original image and extracted overlay.
- MusicXML viewer panel with copy/download actions.
- Note/event table with pitch, accidental, duration, rest/note type, dotted flag, slur/tie flags, staff/system index, and evidence source.
- Playback controls with instrument selector, tempo multiplier, loop toggle, and download MIDI.
- Curated demo gallery for known-good examples, separate from arbitrary uploads.
- Processing progress timeline: upload, detect, assemble, export, render.
- Model provenance badge: full-page checkpoint, tiled checkpoint, GNN status, fallback status.
- Known-limitations panel that is honest but compact.
- Error recovery: unsupported file type, oversized image, missing model checkpoint, extraction timeout, and no-staff detected.

Deployment additions:

- Docker image that copies or mounts required model checkpoints.
- `MELODIOUS_MODEL_ROOT`, `MELODIOUS_GNN_CHECKPOINT`, upload artifact root, and CORS environment variables.
- S3-compatible artifact persistence if multiple backend tasks are used.
- Health endpoint that reports model artifact availability.
- Public smoke test that uploads an image and verifies MusicXML, MIDI, overlay, and result JSON downloads.

## Recommended Implementation Order

1. Keep `phase-04-assembly` as the base branch.
2. Add the V2 product upload endpoint and response models.
3. Wire the endpoint to `melodious_v2.omr.note_extraction`, not the old legacy image detector.
4. Persist generated artifacts under an ignored app run directory such as `runs/app/uploads/{job_id}/`.
5. Port the best frontend ideas from `caba712` into the current V2 frontend, adapted to the new V2 product response.
6. Add `lucide-react` and `html-midi-player` first; add animation only after the core workflow is stable.
7. Add the instrument selector and wire it to playback first, then extend server MIDI export if time allows.
8. Add API tests for upload, artifact downloads, and missing-checkpoint fallback.
9. Run frontend build, local backend smoke, and one real uploaded-image smoke before deploying.

## Current Local Run Target

Until the product endpoint is implemented, the app that can be run locally is the current V2 minimal frontend/backend:

- Backend: `python scripts/run_api.py`
- Frontend: `cd frontend; npm run dev`
- Frontend URL: `http://127.0.0.1:5173`
- Backend URL: `http://127.0.0.1:8000`

Important caveat: the current browser upload path is not the full trained YOLO/tiled/GNN extraction path yet. It is useful for validating the API/frontend shell, not for judging final transcription quality.

## Implementation Update (2026-06-06)

The recommended implementation order above is now done for the core product app. The browser upload path runs the real trained extraction pipeline.

What was built:

- Backend product contract: `src/melodious_v2/api/product_models.py` (typed `ProductTranscription`, `ProductCounts`, `ModelProvenance`, `ModelAvailability`, `QualitySummary`, `NoteEvent`, `ProductSample`).
- Backend product service: `src/melodious_v2/api/product_service.py`. It saves uploads under `runs/app/uploads/{job_id}/`, runs `melodious_v2.omr.note_extraction.extract_notes_from_image` in a background worker thread (serialized by a small semaphore), resolves the default full-page/tiled/GNN checkpoints (with `MELODIOUS_MODEL_ROOT` / `MELODIOUS_GNN_CHECKPOINT` / `MELODIOUS_APP_UPLOAD_ROOT` overrides), and serves persisted artifacts. It also re-renders MIDI per selected instrument + tempo.
- Backend routes added in `src/melodious_v2/api/app.py`: `POST /product/transcribe-image`, `POST /product/transcribe-sample`, `GET /product/jobs/{job_id}`, `GET /product/jobs/{job_id}/artifacts/{name}`, `GET /product/models`, `GET /product/samples`. Existing `/health`, `/version`, `/samples`, `/transcriptions` routes were left intact.
- `extract_notes_from_image` gained an optional, side-effect-free `progress_callback` so the API can report honest pipeline stages.
- Frontend rebuilt into a full app (`frontend/src/App.tsx` plus `frontend/src/components/*` and `frontend/src/lib/*`) using `lucide-react`, `framer-motion`, `html-midi-player`, and `opensheetmusicdisplay`.
- Tests: `tests/test_product_api.py` covers the upload lifecycle, artifact serving, instrument re-render, and validation using the offline CV fallback (checkpoint resolvers patched to `None`).

What is intentionally still pending:

- The real path runs CPU PyTorch via ultralytics (about a minute per page), not the ONNX detector adapter.
- Jobs and the result store are in-process memory; multi-worker/horizontal deployments would need shared storage.
- The legacy `/transcriptions` route still uses `heuristic_bootstrap`.

