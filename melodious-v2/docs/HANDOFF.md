 # Agent Handoff Log

Use this file at the end of every coding-agent session. The next agent must read it before coding.

## Current Handoff

Active milestone: M7 - Detector Metric Improvement is active. M6 - AWS Public Demo is deployment-prepared, but actual public deployment remains blocked on AWS CLI/account values. M1 - Dataset Manifests, M2 - Metric Reproduction, M3 - Full 136-Class Detector, M4 - Real Assembly Runtime, and M5 - End-to-End Export Quality are complete enough to hand off. The full configured YOLOv8m detector run `detection_136class_yolov8m_v1` completed 150 epochs, was finalized from `best.pt`, wrote project-standard V2 artifacts, exported ONNX, copied model metadata, and regenerated `docs/EXPERIMENTS.md`.

M7 improved detector AP metrics by correcting dense-page inference settings and then completing `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`, which reaches `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271` on validation.
The same completed fine-tune has validation `F1@0.5 = 0.8082006373091581`. A follow-up run, `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`, was completed and finalized with corrected dense-page settings; its validation `F1@0.5 = 0.8318461933668392`, `mAP@0.5:0.95 = 0.707986237382828`, and `mAP@0.5 = 0.8390674529615662`. The tiled stem pilot `detection_136class_yolov8m_tiled_stem_pilot_img1024_v1` also completed, reaching tiled-validation `stem = 0.7345783859762263`, but that result is tiled-validation evidence and not an original full-page validation claim. A separate local note-extraction demo path exists for clean sheet images, but the FastAPI uploaded-image route is still `heuristic_bootstrap` unless intentionally rewired.

Local note-extraction default checkpoint:

- Default path used by `scripts/extract_notes_from_image.py` when `--checkpoint` is omitted: `artifacts/models/note_extraction_default_fullpage/best.pt`.
- Source checkpoint copied into that generated artifact: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/best.pt`.
- Local artifact metadata: `artifacts/models/note_extraction_default_fullpage/metadata.json`.
- Stable checkpoint SHA256: `8e4eb9f898c781c32d332b5c5b998a4882dbb343daa856563bf3b88ce6de211a`.
- Default tiled thin-symbol checkpoint path used by `scripts/extract_notes_from_image.py` when `--thin-symbol-checkpoint` is omitted: `artifacts/models/note_extraction_tiled_stem_pilot/best.pt`.
- Source tiled checkpoint copied into that generated artifact: `runs/detection/detection_136class_yolov8m_tiled_stem_pilot_img1024_v1/ultralytics/train/weights/best.pt`.
- Stable tiled checkpoint SHA256: `ab72ff42e5ecf916bd4768b3a6413d67059ff6b51d37588375d274bf4d1b5bef`.
- Sad Romance default-checkpoint retry artifact: `runs/demo/sad_romance_default_fullpage_20260605/`, with MusicXML at `runs/demo/sad_romance_default_fullpage_20260605/sad_romance_clearer_smooth_notes.musicxml`.
- Latest default-checkpoint Sad Romance extraction: `9` staff systems, `197` note events, `0` stem-confirmed notes, and `3` detector-confirmed dotted notes.
- The tiled stem pilot checkpoint is now used as a second tiled thin-symbol pass by default when the generated artifact exists. It does not replace the full-page notehead checkpoint.
- Latest Espresso rest/beam/slur/grace artifact: `runs/demo/espresso_screenshot_slur_gracefix_20260606/`, with MusicXML at `runs/demo/espresso_screenshot_slur_gracefix_20260606/Screenshot 2026-06-06 001627_notes.musicxml`.
- Latest Espresso extraction now reports `209` ordered events, `192` notes, `17` rest events, `17` MusicXML `<rest/>` tags, `186` stem-confirmed notes, `12` dotted notes, `19` slur starts, and `15` tie starts.
- Compared with `runs/demo/espresso_screenshot_tiled_gnn_20260606/`, very short durations improved from `0.0625:4` and `0.125:34` to `0.0625:2` and `0.125:5` after beam-lane deduplication and geometry-capped GNN beam relationships.
- Compared with `runs/demo/espresso_screenshot_rest_beamfix_20260606/`, notes changed from `197` to `192` because the tempo-like annotation notehead and very small cue/grace-sized noteheads are now filtered from the normal rhythmic timeline. The latest XML contains `38` `<slur ...>` tags, `30` `<tie ...>` tags, and `30` `<tied ...>` tags.

## 2026-06-06 - Agent Handoff - Espresso Slur/Annotation Fix

Milestone worked:

- M7 - Detector Metric Improvement / local note-extraction slur, tie, and annotation filtering.

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`

Commands run:

- Full-page detector probe on `Screenshot 2026-06-06 001627.png` - passed; the full-page checkpoint returned `24` `slur` boxes and `7` `tie` boxes at confidence `0.05`, proving the extractor was discarding available slur/tie detections.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py tests\test_note_extraction_cli.py -q` - passed, 21 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest -q` - passed, 63 tests, with one upstream `torch_geometric` deprecation warning.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image "C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\Screenshot 2026-06-06 001627.png" --output-dir runs\demo\espresso_screenshot_slur_gracefix_20260606 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --thin-conf 0.05 --thin-imgsz 1024 --thin-max-det 1000 --thin-tile-size 384 --thin-tile-stride 256 --default-quarter-length 1.0 --title "Espresso"` - passed.
- Espresso MusicXML count check - passed, `209` `<note>` elements, `17` `<rest/>` tags, `38` `<slur ...>` tags, `30` `<tie ...>` tags, and `30` `<tied ...>` tags.

Generated artifacts:

- `runs/demo/espresso_screenshot_slur_gracefix_20260606/Screenshot 2026-06-06 001627_notes.musicxml`
- `runs/demo/espresso_screenshot_slur_gracefix_20260606/Screenshot 2026-06-06 001627_notes.mid`
- `runs/demo/espresso_screenshot_slur_gracefix_20260606/Screenshot 2026-06-06 001627_notes_overlay.png`
- `runs/demo/espresso_screenshot_slur_gracefix_20260606/Screenshot 2026-06-06 001627_notes.json`
- `runs/demo/espresso_screenshot_slur_gracefix_20260606/Screenshot 2026-06-06 001627_detector_payload.json`
- `runs/demo/espresso_screenshot_slur_gracefix_20260606/Screenshot 2026-06-06 001627_relationships.json`

What is complete:

- Slur and tie detector boxes are retained as notation symbols instead of being discarded.
- Slur/tie endpoints are attached to nearby note events and written into MusicXML notations.
- Tempo-like annotation noteheads above the first staff and before the first regular staff note are filtered from the normal event stream.
- Very small cue/grace-sized noteheads are filtered from the normal rhythmic timeline so they do not consume beat duration as full notes.
- Regression coverage verifies annotation-note filtering, small-note filtering, and MusicXML slur/tie export.
- The uploaded Espresso page now starts with the real first score note (`E5`) rather than the tempo-marking quarter note.

What failed:

- A combined PowerShell summary command again hit a Windows access error while expanding paths. Smaller `-LiteralPath` summary commands passed and produced the counts recorded above.

What is blocked:

- Slur/tie endpoint pairing is heuristic and may not be musically perfect in dense passages.
- Grace notes are currently excluded from normal rhythm rather than exported as true MusicXML grace notes.
- Measure/barline-aware repair and voice separation remain incomplete.

Next exact step:

- Decide whether grace notes should be ignored for demo stability or exported as MusicXML `<grace/>` events; then re-run Sad Romance, Fur Elise, and the Arabic page with the latest extractor and inspect whether the annotation/small-note filters remove any legitimate notes.

## 2026-06-06 - Agent Handoff

Milestone worked:

- M7 - Detector Metric Improvement / local note-extraction rest and beam rhythm fix.

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py tests\test_note_extraction_cli.py -q` - passed, 18 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest -q` - passed, 60 tests, with one upstream `torch_geometric` deprecation warning.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image "C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\Screenshot 2026-06-06 001627.png" --output-dir runs\demo\espresso_screenshot_rest_beamfix_20260606 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --thin-conf 0.05 --thin-imgsz 1024 --thin-max-det 1000 --thin-tile-size 384 --thin-tile-stride 256 --default-quarter-length 1.0 --title "Espresso"` - passed.
- Espresso MusicXML/XML-count check - passed, `214` `<note>` elements, `17` `<rest/>` tags, and `12` `<dot/>` tags.

Generated artifacts:

- `runs/demo/espresso_screenshot_rest_beamfix_20260606/Screenshot 2026-06-06 001627_notes.musicxml`
- `runs/demo/espresso_screenshot_rest_beamfix_20260606/Screenshot 2026-06-06 001627_notes.mid`
- `runs/demo/espresso_screenshot_rest_beamfix_20260606/Screenshot 2026-06-06 001627_notes_overlay.png`
- `runs/demo/espresso_screenshot_rest_beamfix_20260606/Screenshot 2026-06-06 001627_notes.json`
- `runs/demo/espresso_screenshot_rest_beamfix_20260606/Screenshot 2026-06-06 001627_detector_payload.json`
- `runs/demo/espresso_screenshot_rest_beamfix_20260606/Screenshot 2026-06-06 001627_relationships.json`

What is complete:

- The local extraction contract now has an ordered `events` stream containing notes and rests while preserving the old `notes` list for compatibility.
- Full-page and tiled YOLO rest detections can now become real rest events.
- MusicXML writes `<rest/>` events and MIDI note onsets preserve silence from detected rests.
- Beam duration inference now counts deduplicated visual beam lanes at the attached stem x-position.
- When usable geometry exists, geometry caps GNN `beam_notegroup` over-attachment so mixed eighth/sixteenth groups are less likely to force every note to the shortest neighboring duration.
- Regression coverage verifies rest export/onset advancement and a mixed beam group where an eighth stays eighth while an adjacent sixteenth remains sixteenth.
- Espresso before/after evidence improved from `0` rests to `17` rests and sharply reduced very short duration artifacts.

What failed:

- A first summary/comparison PowerShell command hit a Windows access error while expanding paths. The run artifacts existed, and smaller `-LiteralPath` summary commands passed.

What is blocked:

- Ties, slurs, measure-level rhythm repair, voice separation, and barline-constrained duration normalization are still incomplete in the local demo path.
- The FastAPI upload route still uses `heuristic_bootstrap` unless the local YOLO/tiled/GNN extractor is intentionally wired behind an explicit mode.

Next exact step:

- Re-run Sad Romance, Fur Elise, and the Arabic page through the rest-aware beam-fixed extractor, compare MusicXML/MIDI quality against their previous artifacts, then implement barline-aware duration repair if measure totals still drift or if ties/slurs must be preserved for the demo.

## 2026-06-05 - Agent Handoff

Milestone worked:

- M7 - Detector Metric Improvement / local note-extraction default checkpoint.

Files changed:

- `scripts/extract_notes_from_image.py`
- `tests/test_note_extraction_cli.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `README.md`
- `MODEL_CARD.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile scripts\extract_notes_from_image.py tests\test_note_extraction_cli.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py tests\test_note_extraction_cli.py -q` - passed, 9 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 14 documentation files.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -c "from scripts.extract_notes_from_image import default_checkpoint; print(default_checkpoint())"` - passed, returned `artifacts\models\note_extraction_default_fullpage\best.pt`.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\models\note_extraction_default_fullpage\metadata.json` - initially failed because PowerShell wrote a UTF-8 BOM; metadata was rewritten without BOM and validation passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png --output-dir runs\demo\sad_romance_default_fullpage_20260605 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --default-quarter-length 1.0 --title "Sad Romance"` - passed, used `artifacts\models\note_extraction_default_fullpage\best.pt`.
- MusicXML count check for `runs\demo\sad_romance_default_fullpage_20260605\sad_romance_clearer_smooth_notes.musicxml` - passed, 197 `<note>` elements and 3 `<dot/>` tags.

Generated artifacts:

- `artifacts/models/note_extraction_default_fullpage/best.pt`
- `artifacts/models/note_extraction_default_fullpage/metadata.json`
- `runs/demo/sad_romance_default_fullpage_20260605/`

What is complete:

- The local note-extraction CLI has a stable default checkpoint path for full-page demo transcription when `--checkpoint` is omitted.
- The saved checkpoint copy was hash-verified against its source checkpoint.
- Documentation now names the default checkpoint path and keeps detector metric provenance tied to the original run-specific `metrics.json` files.
- The generated metadata JSON is strict JSON after the no-BOM rewrite.

What is blocked:

- Nothing is blocked for checkpoint pinning.
- The FastAPI uploaded-image route still uses `heuristic_bootstrap`; wiring this CLI into the API remains future integration work.

Next exact step:

- If improving demo transcription quality is the priority, implement and test a full-page tiled-inference merger that can use the tiled stem pilot for thin-symbol detections without losing full-page notehead/staff context.

## 2026-06-05 - Agent Handoff

Milestone worked:

- M7 - Detector Metric Improvement / local note-extraction demo robustness.

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image "C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image(305).png" --output-dir runs\demo\fur_elise_default_fullpage_20260605 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --default-quarter-length 1.0 --title "Fur Elise"` - passed, but detected only 8 staff systems and missed the dense system around measure 33.
- Staff detector probe for `image(305).png` - initially found the missed system line centers around `545.0, 551.0, 557.0, 563.0, 568.5`, but the old candidate rule rejected that group because mean spacing was below `6 px`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py tests\test_note_extraction_cli.py -q` - passed, 11 tests after adding compact-staff and overlapping-candidate merge regressions.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\omr\note_extraction.py tests\test_note_extraction_demo.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image "C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image(305).png" --output-dir runs\demo\fur_elise_default_fullpage_stafffix_20260605 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --default-quarter-length 1.0 --title "Fur Elise"` - passed, detected all 9 visible staff systems.

Generated artifacts:

- `runs/demo/fur_elise_default_fullpage_20260605/` - initial 8-staff output; keep only as comparison evidence.
- `runs/demo/fur_elise_default_fullpage_stafffix_20260605/` - corrected output with JSON, MusicXML, MIDI, overlay, and checkpoint snapshot.

What is complete:

- Compact staff spacing down to `5 px` is accepted by the staff detector.
- Overlapping staff candidates now prefer the wider five-line group when horizontal span is comparable, preventing a compact false group from replacing the real staff.
- Corrected Fur Elise output has `9` staff systems, `256` note events, `0` stem-confirmed notes, `3` dotted notes, and `36` MusicXML `<alter>` tags.

What is blocked:

- Nothing is blocked for staff detection on this page.
- Rhythm remains heuristic because the default full-page detector still returns no usable stem boxes on this demo page.

Next exact step:

- If Fur Elise quality is demo-critical, inspect `runs/demo/fur_elise_default_fullpage_stafffix_20260605/image(305)_notes_overlay.png` and compare the MIDI/MusicXML against the source page; remaining errors will likely require rhythm/stem post-processing rather than staff-line fixes.

## 2026-06-05 - Agent Handoff

Milestone worked:

- M7 - Detector Metric Improvement / Fur Elise GNN relationship trial.

Files changed:

- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `docs/NOTE_EXTRACTION_DEMO.md`

Commands run:

- `git status --short -- .; git log --oneline -3` - passed; the code/doc baseline was clean and previously committed as `2c2dd40 Improve compact staff detection for demos`.
- Fur Elise GNN relationship trial - passed; wrote artifacts under `runs/demo/fur_elise_gnn_relationship_trial_20260605/`.
- Trial summary check - passed; `applied_mode = gnn`, `inference_ran = true`, `fallback_applied = false`, and `checkpoint_ready = true`.
- XML/stat comparison against `runs/demo/fur_elise_default_fullpage_stafffix_20260605/` - passed; the MusicXML files are byte-identical with SHA256 `E97ECC091AAB109B7FC2C58C1D17DB661F5E93F0480C542489C0F2866EFCC126`.

Generated artifacts:

- `runs/demo/fur_elise_gnn_relationship_trial_20260605/image(305)_notes.musicxml`.
- `runs/demo/fur_elise_gnn_relationship_trial_20260605/image(305)_notes.mid`.
- `runs/demo/fur_elise_gnn_relationship_trial_20260605/image(305)_notes_overlay.png`.
- `runs/demo/fur_elise_gnn_relationship_trial_20260605/image(305)_notes.json`.
- `runs/demo/fur_elise_gnn_relationship_trial_20260605/gnn_trial_summary.json`.
- `runs/demo/fur_elise_gnn_relationship_trial_20260605/relationships.json`.
- `runs/demo/fur_elise_gnn_relationship_trial_20260605/detector_payload.json`.

What is complete:

- The legacy MUSCIMA GNN checkpoint was tested on the Fur Elise detector payload after the staff fix.
- The relationship runtime produced `695` relationships: `641` `stem_notehead` relationships and `54` `beam_notegroup` relationships.
- The extractor still reports `9` staff systems, `256` note events, `0` stem-confirmed notes, `3` dotted notes, and `36` MusicXML `<alter>` tags.

What is blocked:

- The GNN trial did not improve the Fur Elise MusicXML. The local note-extraction writer still builds MusicXML directly from detected notes and heuristic rhythm, and does not consume graph relationships to rewrite durations, voices, measures, or beams.
- The detector payload for this Fur Elise page has no actual `stem` class detections, so the emitted `stem_notehead` relationships are not sufficient evidence that stems were solved on the uploaded image.

Next exact step:

- Implement a tested rhythm-integration layer that consumes detector/GNN beam, flag, dot, and stem evidence before MusicXML export, or first wire tiled/thin-symbol inference into the local note-extraction CLI so true stem boxes exist on full-page demo images.

## 2026-06-05 - Agent Handoff

Milestone worked:

- M7 - Detector Metric Improvement / tiled thin-symbol + GNN local extraction integration.

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `scripts/extract_notes_from_image.py`
- `tests/test_note_extraction_demo.py`
- `tests/test_note_extraction_cli.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `README.md`
- `MODEL_CARD.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\omr\note_extraction.py scripts\extract_notes_from_image.py tests\test_note_extraction_demo.py tests\test_note_extraction_cli.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py tests\test_note_extraction_cli.py -q` - passed, 14 tests.
- `Copy-Item runs\detection\detection_136class_yolov8m_tiled_stem_pilot_img1024_v1\ultralytics\train\weights\best.pt artifacts\models\note_extraction_tiled_stem_pilot\best.pt` - passed after creating the generated artifact directory.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\models\note_extraction_tiled_stem_pilot\metadata.json` - passed after rewriting metadata without a UTF-8 BOM.
- Initial Fur Elise tiled+GNN run under `runs/demo/fur_elise_tiled_gnn_rhythm_20260605/` - passed, but produced too many dotted notes (`53`) because tiled `augmentationDot` detections were allowed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image "C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image(305).png" --output-dir runs\demo\fur_elise_tiled_gnn_rhythm_nodots_20260605 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --thin-conf 0.05 --thin-imgsz 1024 --thin-max-det 1000 --thin-tile-size 384 --thin-tile-stride 256 --default-quarter-length 1.0 --title "Fur Elise"` - passed after disabling tiled dots by default.
- Visual inspection of `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/image(305)_notes_overlay.png` - passed for notehead/staff alignment; overlay is text-dense.

Generated artifacts:

- `artifacts/models/note_extraction_tiled_stem_pilot/best.pt`
- `artifacts/models/note_extraction_tiled_stem_pilot/metadata.json`
- `runs/demo/fur_elise_tiled_gnn_rhythm_20260605/` - keep only as comparison evidence showing why tiled dots are disabled by default.
- `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/image(305)_notes.musicxml`
- `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/image(305)_notes.mid`
- `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/image(305)_notes_overlay.png`
- `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/image(305)_notes.json`
- `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/image(305)_detector_payload.json`
- `runs/demo/fur_elise_tiled_gnn_rhythm_nodots_20260605/image(305)_relationships.json`

What is complete:

- The local extraction CLI now auto-detects the saved tiled stem pilot checkpoint as a second inference pass.
- Tiled inference scans overlapping `384 x 384` source-pixel windows and maps detections back to page coordinates.
- The tiled pass contributes stems, beams, flags, and explicit accidentals while leaving full-page notehead detection intact.
- Tiled augmentation-dot detections are disabled by default because they over-dotted Fur Elise. Existing full-page detector-confirmed dots still count.
- Tiled key-signature glyphs are blocked from setting document key signatures to prevent inline accidentals from becoming false key signatures.
- The local extraction CLI now auto-detects `..\outputs\gnn_checkpoint.pt` and consumes GNN relationships in rhythm inference.
- Unit coverage now verifies relationship-driven `gnn_beam_x1` and `gnn_stem_quarter` rhythm sources.
- Fur Elise improved from `0` to `171` stem-confirmed notes while keeping dotted notes at `3`.
- Fur Elise GNN assembly ran with `applied_mode = gnn`, `relationship_count = 1259`, `stem_notehead = 950`, and `beam_notegroup = 309`.
- Fur Elise MusicXML changed from the staff-fixed output; new MusicXML SHA256 is `5E00C75335236D71F613F7D280B385CA3BC1460971DFF8BD3587B25C59F7943D`.

What is blocked:

- This is not an official detector metric. It is local demo transcription evidence using a second tiled inference path.
- Beam-count over-shortening still exists. The latest Fur Elise run has `0.0625:9` durations and some `gnn_beam_x4` / `beam_x4` rhythm sources, which may be too short for the target demo.
- Voices, measure reconstruction, barline-aware duration repair, ties, and measure-scoped accidental persistence remain incomplete.
- The FastAPI uploaded-image route still uses `heuristic_bootstrap`; the improved CLI is not yet wired into the product upload route.

Next exact step:

- Run the new default tiled+GNN local extractor on Sad Romance and `image.png` with tiled dots disabled, then compare stem-confirmed notes, dotted notes, MusicXML hashes, and subjective MIDI quality. After that, implement a beam-count normalization rule if over-shortened notes are still obvious.

## 2026-06-05 - Agent Handoff

Milestone worked:

- M7 - Detector Metric Improvement / Fur Elise pitch and accidental correction.

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`

Commands run:

- Internet research check - done. Relevant engineering direction: use staff-position-aware note primitives and relationships; Audiveris is a mature open-source OMR system for comparison, OpenCV line primitives remain appropriate for thin-line/stem fallback work, and MUSCIMA++ relationship modeling supports notehead-stem / beam-note grouping.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\omr\note_extraction.py tests\test_note_extraction_demo.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py tests\test_note_extraction_cli.py -q` - passed, 16 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image "C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image(305).png" --output-dir runs\demo\fur_elise_pitchfix_tiled_gnn_20260605 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --thin-conf 0.05 --thin-imgsz 1024 --thin-max-det 1000 --thin-tile-size 384 --thin-tile-stride 256 --default-quarter-length 1.0 --title "Fur Elise"` - passed; fixed the first note to E but exposed a false E-sharp on note 5 from loose accidental attachment.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image "C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image(305).png" --output-dir runs\demo\fur_elise_pitch_accidental_fix_tiled_gnn_20260605 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --thin-conf 0.05 --thin-imgsz 1024 --thin-max-det 1000 --thin-tile-size 384 --thin-tile-stride 256 --default-quarter-length 1.0 --title "Fur Elise"` - passed after accidental attachment was constrained to matching staff steps.

Generated artifacts:

- `runs/demo/fur_elise_pitchfix_tiled_gnn_20260605/` - intermediate comparison output; first note fixed but note 5 was falsely E-sharp.
- `runs/demo/fur_elise_pitch_accidental_fix_tiled_gnn_20260605/image(305)_notes.musicxml`
- `runs/demo/fur_elise_pitch_accidental_fix_tiled_gnn_20260605/image(305)_notes.mid`
- `runs/demo/fur_elise_pitch_accidental_fix_tiled_gnn_20260605/image(305)_notes_overlay.png`
- `runs/demo/fur_elise_pitch_accidental_fix_tiled_gnn_20260605/image(305)_notes.json`
- `runs/demo/fur_elise_pitch_accidental_fix_tiled_gnn_20260605/image(305)_detector_payload.json`
- `runs/demo/fur_elise_pitch_accidental_fix_tiled_gnn_20260605/image(305)_relationships.json`

What is complete:

- `notehead*InSpace` detections now quantize to staff spaces and `notehead*OnLine` detections now quantize to staff lines before pitch is computed.
- Explicit accidental attachment now requires the accidental's staff-position step to match the note's step.
- Regression tests cover both fixes.
- Latest Fur Elise opening phrase now extracts as `E5`, `D#5`, `E5`, `D#5`, `E5`, `B4`, `D5`, `C5`, `A4`.
- Latest Fur Elise output still has `9` staff systems, `256` note events, `171` stem-confirmed notes, `3` dotted notes, `1259` GNN relationships, and `applied_mode = gnn`.
- Latest Fur Elise MusicXML SHA256 is `0FEF8DA42F1B27B5EBF567AADEB1FD156EADFFD14CA62C7606E003FC23894430`.

What is blocked:

- Stem boxes are present in the new tiled+GNN output. The user's open file, `runs/demo/fur_elise_default_fullpage_stafffix_20260605/image(305)_notes.musicxml`, is an older artifact from before tiled stem inference and will still show no stem-confirmed evidence in its JSON.
- Beam-count over-shortening is still unresolved; the latest Fur Elise output still contains very short `0.0625` durations from `beam_x4` style sources.

Next exact step:

- Fix beam-count over-shortening by collapsing duplicate/stacked beam boxes per note group before duration assignment, then rerun Fur Elise and compare the duration distribution against `runs/demo/fur_elise_pitch_accidental_fix_tiled_gnn_20260605/`.

Current state:

- V2 foundation is implemented.
- Python tests pass.
- Frontend build passed in the previous implementation session.
- Detector payload JSON Schema exists at `docs/detector_payload_v2.schema.json`.
- DeepScores 136-class manifests exist locally under `runs/data/deepscores_136_manifest/`.
- MUSCIMA graph manifests exist locally under `runs/data/muscima_graph_manifest/`.
- DeepScores duplicate image-id and filename leakage checks passed.
- DeepScores inferred work-group leakage check is a warning with 202 repeated filename-inferred groups.
- MUSCIMA duplicate page-id leakage check passed.
- M2 reduced-class metric reproduction exists locally under `runs/detection/detection_15class_repro_sample_v1/`.
- `docs/EXPERIMENTS.md` was regenerated from `runs/**/metrics.json`.
- M3 materialized YOLO dataset exists under `runs/data/deepscores_136_yolo_materialized/`.
- M3 smoke run exists under `runs/detection/detection_136class_yolov8s_smoke_v1/`.
- M3 smoke model artifacts exist under `artifacts/models/detection_136class_yolov8s_smoke_v1/`.
- M3 full YOLOv8m run exists under `runs/detection/detection_136class_yolov8m_v1/`.
- M3 full YOLOv8m model artifacts exist under `artifacts/models/detection_136class_yolov8m_v1/`.
- Detailed milestone ledger exists at `docs/MILESTONE_HISTORY.md`.
- M4 legacy GNN checkpoint source: `..\outputs\gnn_checkpoint.pt`.
- M4 legacy GNN checkpoint SHA256: `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`.
- M4 runtime adapter: `src/melodious_v2/assembly/legacy_gnn.py`.
- M4 graph evaluation script: `scripts/evaluate_gnn_muscima.py`.
- M4 graph run: `runs/graph/graph_legacy_gnn_muscima_val_v1/`.
- M4 graph metrics: `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`.
- M4 graph primary metric: positive-class macro F1 `0.7590456327823909`.
- M4 graph separate `no_relation` F1: `0.9425171440096813` with support `41834`.
- M4 `stem_notehead` F1: `0.6960721184803607`; `beam_notegroup` F1: `0.8220191470844213`.
- M4 graph caveat: the legacy checkpoint did not save the separate seeded node feature encoder; V2 reconstructs it from seed `42` and records that in the graph run artifacts.
- M5 end-to-end run: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/`.
- M5 end-to-end metrics: `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`.
- M5 primary export metric: MusicXML validity rate `1.0`.
- M5 MIDI generation success rate: `1.0`.
- M5 page success rate: `1.0`.
- M5 generated artifacts: per-page MusicXML, MIDI, detector payload JSON, and relationship JSON for 14 MUSCIMA holdout pages.
- M5 caveat: this is export-validity evidence from MUSCIMA XML-derived payload fixtures, not trained uploaded-image detector quality.
- M6 deployment runbook: `infra/aws/README.md`.
- M6 local/public smoke CLI: `scripts/smoke_public_demo.py`.
- M6 smoke module: `src/melodious_v2/deployment/smoke.py`.
- M6 smoke test: `tests/test_deployment_smoke.py`.
- M6 PowerShell smoke script: `infra/aws/smoke_test.ps1`.
- M6 API CORS env var: `MELODIOUS_CORS_ORIGINS`.
- M6 GNN deployment env var: `MELODIOUS_GNN_CHECKPOINT`.
- M6 local smoke evidence path: `runs/deploy/m6_local_smoke/smoke.json` (ignored).
- M6 public deployment blocker: AWS CLI was not found locally, and account-specific ECR/ECS/S3/CloudFront values are unavailable and must not be committed.
- M7 metric improvement doc: `docs/METRIC_IMPROVEMENT.md`.
- M7 sweep config: `configs/detection_136class_eval_resolution_sweep.yaml`.
- M7 best primary validation detector run: `runs/detection/detection_136class_yolov8m_eval_img1472_maxdet2000_v1/`.
- M7 best primary `mAP@0.5:0.95`: `0.6204968163150985`.
- M7 best secondary validation detector run for `mAP@0.5`: `runs/detection/detection_136class_yolov8m_eval_img1536_maxdet2000_v1/`.
- M7 best secondary `mAP@0.5`: `0.7920129156176505`.
- M7 best `F1@0.5`: `0.7746130448554269`.
- M7 caveat: this is validation inference tuning on the existing checkpoint, not a newly trained model or test-set result.
- M7 class coverage audit: `runs/detection/detection_136class_class_coverage_audit_v1/class_coverage.json`.
- M7 class coverage finding: the detector head preserves 136 classes, but the local train/validation/test labels support 115 classes, validation supports 103 classes, and 21 taxonomy classes have zero local labels.
- M7 class coverage finding: no validation-supported or test-supported class is absent from training, but 12 train-supported classes are absent from validation.
- M7 class coverage finding: high-support zero-map validation classes remain `ledgerLine` and `stem`.
- M7 completed fine-tune: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/`.
- M7 first fine-tune launch: 2026-06-01 local time `02:46:32`, parent PID `34780`, active child PID observed after launch `23612`.
- M7 first fine-tune attempt stopped after seven completed epochs and while epoch 8 was in progress; it was later resumed and completed all 50 epochs.
- M7 first fine-tune clean checkpoint files: `ultralytics/train/weights/last.pt` and `best.pt`.
- M7 first fine-tune best completed primary training-row metric so far: epoch 7, `metrics/mAP50-95(B) = 0.6116`.
- M7 first fine-tune best completed `metrics/mAP50(B)` so far: epoch 6, `0.79679`.
- M7 resume support commit: `6636622`.
- M7 fine-tune resume launch: 2026-06-02 local time `01:05:09`, parent PID `35952`, active child PID `43740`.
- M7 fine-tune resume logs: `resume_epoch7_stdout.log`, `resume_epoch7_stderr.log`, `resume_epoch7.pid`, `resume_epoch7_child.pid`, and `resume_epoch7_launch_metadata.json` under the run directory.
- M7 completed fine-tune AP metrics: `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271`.
- M7 completed fine-tune threshold metrics: `precision@0.5 = 0.8457099520968777`, `recall@0.5 = 0.7738772781467206`, and `F1@0.5 = 0.8082006373091581`.
- M7 completed fine-tune caveat: `stem = 0.0` mAP and `ledgerLine = 0.0035627224962602928`, so rhythm extraction still needs targeted thin-symbol work.
- M7 active resumed follow-up fine-tune: `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/`.
- M7 active follow-up source checkpoint: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/best.pt`.
- M7 active follow-up launch: 2026-06-02 local time `23:11:35`, parent PID `34896`, Python child PID `28432`.
- M7 active follow-up files: `finetune_v2_retry.pid`, `finetune_v2_retry_child.pid`, `finetune_v2_retry_stdout.log`, `finetune_v2_retry_stderr.log`, `finetune_v2_retry_launch_command.txt`, and `finetune_v2_retry_launch_metadata.json`.
- M7 active follow-up settings: `epochs=50`, `imgsz=1536`, `batch=1`, `workers=0`, `device=0`, `patience=15`, `max_det=2000`.
- M7 active follow-up startup evidence: CUDA training reached epoch `1/50` on the RTX 3080 Laptop GPU.
- Ignore `finetune_v2_stdout.log` / `finetune_v2_stderr.log`; the first v2 launch failed before training because `$env:PYTHONPATH` was expanded incorrectly. The active run uses the `retry` files.
- M7 saved/stop status for follow-up: saved after clean completed epoch `22` on 2026-06-03, then parent PID `34896` and child PID `28432` were stopped and confirmed not running.
- M7 manual recovery checkpoint: `artifacts/manual_checkpoints/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/epoch22_stop_2026-06-03_021238/`.
- M7 manual recovery checkpoint files: `last.pt`, `best.pt`, `results.csv`, `args.yaml`, retry stdout/stderr logs, retry PID files, retry launch metadata, retry launch command, `metadata.json`, and `README.md`.
- M7 manual recovery checkpoint load verification: saved `last.pt` loaded with Ultralytics as `task = detect`, `class_count = 136`, first class `brace`, last class `ottavaBracket`.
- M7 manual recovery checkpoint SHA256 values: `last.pt = 8c0077eff5278e90fa4023f71b5858ab193c9500333839a1c479e2829010cd51`; `best.pt = 8c0077eff5278e90fa4023f71b5858ab193c9500333839a1c479e2829010cd51`.
- M7 latest follow-up interim CSV values at epoch 22: `metrics/precision(B) = 0.88232`, `metrics/recall(B) = 0.76779`, `metrics/mAP50(B) = 0.83573`, and `metrics/mAP50-95(B) = 0.65517`. These are not final V2 metric provenance.
- M7 active resume launch: 2026-06-03, PID `7052`, saved in `resume_epoch22.pid`.
- M7 active resume logs: `resume_epoch22_stdout.log` and `resume_epoch22_stderr.log`.
- M7 active resume evidence: Ultralytics reported resume from `epoch22_stop_2026-06-03_021238\last.pt` from epoch 23 to 50 total epochs and started epoch `23/50`.
- M7 stem diagnosis: local labels have abundant `stem` support, but whole-page training makes the median stem about `0.78` model pixels wide at `imgsz=1536`, and a sampled low-threshold validation probe returned zero stem predictions.
- M7 tiled stem dataset tooling: `src/melodious_v2/datasets/yolo_tiling.py` and `scripts/materialize_tiled_yolo_dataset.py`.
- M7 tiled stem smoke output: `runs/data/deepscores_136_yolo_tiled_stem_smoke_v1/`, with 222 train tiles, 229 validation tiles, 264 test tiles, 4361 retained stem labels, and projected median stem width `2.666645333333387` pixels at `target_imgsz=1024`.
- M7 existing tiled dataset runner support: `scripts/run_detection_136class_yolo.py --dataset-yaml ... --dataset-id ...`, with materialize-only check verified on the smoke tiled dataset.
- Local note extraction demo module: `src/melodious_v2/omr/note_extraction.py`.
- Local note extraction demo CLI: `scripts/extract_notes_from_image.py`.
- Local note extraction demo docs: `docs/NOTE_EXTRACTION_DEMO.md`.
- Local note extraction demo test: `tests/test_note_extraction_demo.py`.
- Sad Romance note extraction evidence: `runs/demo/sad_romance_note_extraction_v3/` with `extractor_mode = yolo_notehead_staff_pitch`, 9 staff systems, 197 extracted note events, 0 stem-confirmed notes, 17 dotted notes, duration distribution `0.25:1`, `0.5:80`, `0.75:7`, `1.0:71`, `1.5:8`, `2.0:23`, `3.0:2`, `4.0:5`, and an overlay image. This is an ignored demo artifact, not an official metric run.
- Sad Romance note extraction caveat: pitch is estimated from treble-clef staff geometry. Rhythm uses nearby stems, beams, flags, and augmentation dots when the detector returns them. On this page, the checkpoint returned no usable stem detections, so quarter notes are marked as `black_notehead_quarter_rule_no_stem`.
- Uploaded Arabic page note extraction evidence after key-signature support: `runs/demo/image_note_extraction_v5/` with `extractor_mode = yolo_notehead_staff_pitch`, 9 staff systems, 319 extracted note events, 0 stem-confirmed notes, 38 dotted notes, detected `B: -1` key signatures on all 9 systems, MusicXML `key_fifths = -1`, 53 B-flat notes from detected key signatures, 2 explicit sharp notes from detected inline accidentals, duration distribution `0.25:28`, `0.375:8`, `0.5:175`, `0.75:8`, `1.0:68`, `1.5:21`, `2.0:10`, `3.0:1`, MIDI size `2879` bytes, and MusicXML parse check `319` notes with `38` `<dot/>` tags, one `<fifths>-1</fifths>`, and `53` `<alter>-1</alter>` tags. This is an ignored demo artifact, not an official metric run.
- Uploaded Arabic page note extraction evidence after safer dot policy: `runs/demo/image_note_extraction_v6/` with `extractor_mode = yolo_notehead_staff_pitch`, 9 staff systems, 319 extracted note events, 0 stem-confirmed notes, 7 detector-confirmed dotted notes, detected `B: -1` key signatures on all 9 systems, MusicXML `key_fifths = -1`, 53 B-flat notes from detected key signatures, duration distribution `0.25:36`, `0.5:192`, `1.0:74`, `1.5:6`, `2.0:10`, `3.0:1`, MIDI size `2871` bytes, and MusicXML parse check `319` notes with `7` `<dot/>` tags, one `<fifths>-1</fifths>`, and `53` `<alter>-1</alter>` tags. This is an ignored demo artifact, not an official metric run.
- Uploaded Arabic page staff/key finding: the initial run detected only 4 staff systems and should be ignored. The fixed `v3` run detects all 9 visible systems by preserving lighter/antialiased staff lines before note-to-pitch mapping. The `v5` run adds detected key-signature application. This was not hard-coded to the page: YOLO emits `keyFlat`, the extractor maps each key-flat glyph to `B` by staff geometry, and then applies `B: -1` to matching notes.
- `yolov8m.pt` exists in the V2 workspace and is ignored by `.gitignore`.
- Full YOLOv8m training was first saved after epoch 20 completed and stopped during epoch 21.
- First manual recovery checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/`.
- Full YOLOv8m training was resumed from the epoch-20 manual checkpoint on 2026-05-21.
- The resumed run reached a clean completed epoch 74 before the user requested another save/stop.
- Previous manual recovery checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/`.
- The copied epoch-74 `last.pt` loaded successfully with Ultralytics: `task=detect`, `class_count=136`, first class `brace`, last class `ottavaBracket`.
- The epoch-74 manual checkpoint metadata JSON validates with `python -m json.tool` and includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- A post-stop process check showed no Python training process after stopping parent PID `30204` and child PIDs `35140` and `36816`.
- Full YOLOv8m training was resumed again from the epoch-74 checkpoint on 2026-05-22.
- The resumed run reached a clean completed epoch 95 before the user requested another save/stop.
- Current manual recovery checkpoint folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/`.
- Current manual recovery checkpoint files: `last.pt`, `best.pt`, `results.csv`, `args.yaml`, `resume_epoch74_train_stdout.log`, `resume_epoch74_train_stderr.log`, `resume_epoch74_train.pid`, `metadata.json`, and `README.md`.
- The copied epoch-95 `last.pt` loaded successfully with Ultralytics: `task=detect`, `class_count=136`, first class `brace`, last class `ottavaBracket`.
- The epoch-95 manual checkpoint metadata JSON validates with `python -m json.tool` and includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- A post-stop process check showed no Python training process after stopping the live training wrapper and Python trainer.
- Full YOLOv8m training was resumed again from the epoch-95 checkpoint on 2026-05-26.
- Current resume PID file: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train.pid`, containing PID `30436` when launched.
- Current resume stdout log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stdout.log`.
- Current resume stderr log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stderr.log`.
- Current resume log evidence: Ultralytics reports `Resuming training ... from epoch 96 to 150 total epochs`, and epoch `96/150` is active.
- Full YOLOv8m training reached a clean completed epoch 124, then was found not running on 2026-05-28.
- Full YOLOv8m training was resumed again from the latest run checkpoint `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/last.pt` on 2026-05-28.
- Resume PID file: `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train.pid`, containing PID `24516` when launched.
- Resume stdout log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train_stdout.log`.
- Resume stderr log: `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train_stderr.log`.
- Resume log evidence: Ultralytics reports `Resuming training ... from epoch 125 to 150 total epochs`; the log later reaches epoch 150/150 and final validation output.
- Final selected checkpoint: `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`.
- Final V2 metrics: `runs/detection/detection_136class_yolov8m_v1/metrics.json`.
- Final V2 analysis: `runs/detection/detection_136class_yolov8m_v1/analysis.json`.
- Final ONNX parity: `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`.
- Final model metadata: `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.
- Full detector primary validation metric: `mAP@0.5:0.95` 0.4747370751116288.
- Full detector secondary validation metrics: `mAP@0.5` 0.5853211368313491, precision 0.8274236461250144, and recall 0.4909790740632496.
- Full detector secondary F1: `F1@0.5` 0.6162725385980492.
- Detector limitation evidence: 16 supported validation classes still have zero mAP, including `ledgerLine`, `stem`, and `ottavaBracket`.
- ONNX parity passed on one fixed validation image; PyTorch and ONNX both returned 300 boxes with identical class-count totals.
- M1 was re-verified on 2026-05-12 in this workspace. The manifest CLI completed against the local parent datasets and refreshed ignored `runs/data/` artifacts.
- `docs/AGENT_PROMPTS.md` now says the current active milestone is M7.

Next exact prompt:

- Use the active M7 prompt in `docs/AGENT_PROMPTS.md`.

Next exact implementation target:

1. Continue M7 from `docs/METRIC_IMPROVEMENT.md`.
2. Monitor the active resumed `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` run using `resume_epoch22.pid` and `resume_epoch22_stdout.log`.
3. Keep test-set detector metrics untouched until the final model and inference configuration are frozen.
4. Keep uploaded-image detector mode labeled `heuristic_bootstrap` unless a tested ONNX detector adapter is intentionally added.
5. For immediate local note extraction testing, use `scripts/extract_notes_from_image.py` from `docs/NOTE_EXTRACTION_DEMO.md`. YOLO-backed runs now disable CV augmentation-dot fallback by default; add `--use-cv-dot-fallback` only for deliberate experiments.
6. For the next rhythm-quality step, target stem detection specifically: compare `stem` after v2 completes; if it remains near zero, generate the full tiled dataset and train from it through `--dataset-yaml` instead of blindly training more whole-page epochs.
7. If tiled detect-mode training still cannot localize stems, evaluate an OBB/segmentation side branch or add a clearly labeled demo-only CV stem-line attachment fallback with explicit provenance.

Monitor command for the active resumed v2 fine-tune:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$run='runs\detection\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2'
Get-Process -Id ([int](Get-Content "$run\resume_epoch22.pid")) -ErrorAction SilentlyContinue
Get-Content -Tail 80 "$run\resume_epoch22_stdout.log"
if (Test-Path "$run\ultralytics\train\results.csv") { Import-Csv "$run\ultralytics\train\results.csv" | Select-Object -Last 1 }
```

## 2026-06-03 - Agent Handoff - V2 Fine-Tune Resumed From Epoch 22

Milestone worked:

- M7 - Detector Metric Improvement / checkpoint resume

Files changed:

- `docs/METRIC_IMPROVEMENT.md`
- `docs/STATUS.md`
- `docs/HANDOFF.md`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `MODEL_CARD.md`
- `README.md`

Generated ignored evidence:

- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/resume_epoch22.pid`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/resume_epoch22_stdout.log`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/resume_epoch22_stderr.log`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/resume_epoch22_launch_command.txt`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/resume_epoch22_launch_metadata.json`

What happened:

- The user asked to carry on with what is needed.
- Confirmed old stopped PIDs `34896` and `28432` were not running.
- Confirmed no final `metrics.json` existed for `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`.
- Confirmed the saved manual checkpoint `artifacts/manual_checkpoints/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/epoch22_stop_2026-06-03_021238/last.pt` exists.
- Launched a hidden background resume process with PID `7052`.
- Saved fresh resume PID, stdout, stderr, command, and metadata files under the run directory.
- Verified startup logs show Ultralytics loading the epoch-22 manual checkpoint and resuming from epoch 23 to 50.
- Verified epoch `23/50` started.

Commands run:

- Read-only preflight check for checkpoint existence, old PID status, and missing final `metrics.json` - passed.
- Hidden `Start-Process` launch through `..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_finetune_img1536_maxdet2000_v2 --resume-training --resume-checkpoint artifacts\manual_checkpoints\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2\epoch22_stop_2026-06-03_021238\last.pt --device 0 --workers 0` - passed.
- Follow-up log check - passed; PID `7052` was running and stdout showed resume from epoch 23 to 50.

What is complete:

- The v2 1536 fine-tune is running again from the saved epoch-22 checkpoint.
- Resume provenance files exist under the run directory.
- Documentation now points to `resume_epoch22.pid` and `resume_epoch22_stdout.log`.

What is not complete:

- The resumed run has not finished.
- Final project `metrics.json` still does not exist.
- No final v2 metrics should be claimed yet.

Next exact step:

Monitor:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$run='runs\detection\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2'
Get-Process -Id ([int](Get-Content "$run\resume_epoch22.pid")) -ErrorAction SilentlyContinue
Get-Content -Tail 80 "$run\resume_epoch22_stdout.log"
if (Test-Path "$run\ultralytics\train\results.csv") { Import-Csv "$run\ultralytics\train\results.csv" | Select-Object -Last 1 }
```

If interrupted again, preserve the latest `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, PID file, launch command, and launch metadata before stopping or resuming.

## 2026-06-03 - Agent Handoff - V2 Fine-Tune Saved And Stopped At Epoch 22

Milestone worked:

- M7 - Detector Metric Improvement / checkpoint management

Files changed:

- `docs/METRIC_IMPROVEMENT.md`
- `docs/STATUS.md`
- `docs/HANDOFF.md`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `MODEL_CARD.md`
- `README.md`

Generated ignored evidence:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/epoch22_stop_2026-06-03_021238/`

What happened:

- The user asked to save the active v2 fine-tune and stop it for now.
- Before stopping, the latest clean completed row in `results.csv` was epoch `22`.
- The run had no final `metrics.json`; the saved values are interim training CSV values only.
- Copied `last.pt`, `best.pt`, `results.csv`, `args.yaml`, retry logs, retry PID files, retry launch metadata, and retry launch command into a manual checkpoint folder.
- Wrote `metadata.json` and `README.md` into the manual checkpoint folder.
- Rewrote `metadata.json` without UTF-8 BOM and validated it with `python -m json.tool`.
- Stopped child PID `28432` and parent PID `34896`.
- Confirmed both PIDs were no longer running.
- Loaded saved `last.pt` with Ultralytics; it reported `task = detect`, `class_count = 136`, first class `brace`, and last class `ottavaBracket`.

Saved checkpoint:

- Folder: `artifacts/manual_checkpoints/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/epoch22_stop_2026-06-03_021238/`.
- Latest completed epoch: `22`.
- Completed rows: `22`.
- `last.pt` SHA256: `8c0077eff5278e90fa4023f71b5858ab193c9500333839a1c479e2829010cd51`.
- `best.pt` SHA256: `8c0077eff5278e90fa4023f71b5858ab193c9500333839a1c479e2829010cd51`.
- Latest interim CSV row: `metrics/precision(B) = 0.88232`, `metrics/recall(B) = 0.76779`, `metrics/mAP50(B) = 0.83573`, and `metrics/mAP50-95(B) = 0.65517`.

Commands run:

- Check latest row and checkpoint files - passed; latest clean completed epoch was 22.
- Copy checkpoint, logs, and metadata to `artifacts/manual_checkpoints/.../epoch22_stop_2026-06-03_021238/` - passed.
- Stop child PID `28432` and parent PID `34896` - passed.
- Confirm both PIDs stopped - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -c "from ultralytics import YOLO; ..."` - passed; saved `last.pt` is loadable and has 136 classes.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2\epoch22_stop_2026-06-03_021238\metadata.json` - passed after removing UTF-8 BOM.

What is complete:

- The active v2 fine-tune is stopped.
- The latest clean epoch-22 checkpoint is copied to a manual recovery folder.
- The saved checkpoint is loadable.
- The exact resume command is documented.

What is not complete:

- `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` has not completed all configured epochs.
- It has no final project `metrics.json` yet.
- Do not claim final v2 metrics from the interim `results.csv`.

Next exact step:

Resume when requested:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --run-id detection_136class_yolov8m_finetune_img1536_maxdet2000_v2 `
  --resume-training `
  --resume-checkpoint artifacts\manual_checkpoints\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2\epoch22_stop_2026-06-03_021238\last.pt `
  --device 0 `
  --workers 0
```

## 2026-06-03 - Agent Handoff - Tiled Stem Dataset Path Added

Milestone worked:

- M7 - Detector Metric Improvement / stem and rhythm recovery

Files changed:

- `src/melodious_v2/datasets/yolo_tiling.py`
- `scripts/materialize_tiled_yolo_dataset.py`
- `scripts/run_detection_136class_yolo.py`
- `tests/test_yolo_tiling.py`
- `tests/test_full_detector_m3.py`
- `docs/METRIC_IMPROVEMENT.md`
- `docs/STATUS.md`
- `docs/HANDOFF.md`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/ARCHITECTURE.md`
- `MODEL_CARD.md`
- `README.md`

Generated ignored evidence:

- `runs/data/deepscores_136_yolo_tiled_stem_smoke_v1/`

What was found:

- The completed fine-tune improved headline validation metrics, but it still reports `stem = 0.0` AP.
- The issue is not lack of labels. The local DeepScores labels contain 210140 train `stem` labels, 25247 validation `stem` labels, and 65010 test `stem` labels.
- The issue is partly geometry. Whole-page `stem` boxes are extremely thin: median normalized width is about `0.0005102`, or roughly `0.78` model pixels at `imgsz=1536`.
- A sampled low-threshold probe on validation pages returned zero `stem` predictions, so simply lowering confidence is unlikely to fix note rhythm.
- The previous runner behavior would have rematerialized the original full-page dataset, so a tiled dataset needed explicit `--dataset-yaml` support before training could use it safely.

What changed:

- Added a tiled YOLO materializer for stem/ledger/dot/beam/flag-focused crops.
- Added a CLI for creating ignored tiled datasets under `runs/data/`.
- Added runner support for existing YOLO datasets through `--dataset-yaml` and `--dataset-id`.
- Added runner manifest counting for existing datasets so dataset provenance and class counts are recorded without touching the original full-page materializer.
- Hardened existing-dataset YAML parsing so YOLO `names` can be either a mapping or a list.
- Added tests for tiling behavior, runner argument parsing, existing-dataset manifest counting, and list-shaped YOLO names.

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\materialize_tiled_yolo_dataset.py --output-dir runs\data\deepscores_136_yolo_tiled_stem_smoke_v1 --tile-size 384 --stride 256 --target-imgsz 1024 --max-images-per-split 3` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_yolo_tiling.py -q` - passed, 3 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_full_detector_m3.py tests\test_yolo_tiling.py -q` - passed, 10 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --dataset-yaml runs\data\deepscores_136_yolo_tiled_stem_smoke_v1\dataset.yaml --dataset-id deepscores_136_yolo_tiled_stem_smoke_v1 --materialize-only` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest -q` - passed, 50 tests, with one upstream `torch_geometric` deprecation warning.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 14 documentation files.
- Active training status check for `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` - passed; parent PID `34896` and child PID `28432` were running, no final `metrics.json` existed, and the latest completed row was epoch 17.

Smoke tiled dataset result:

- Output: `runs/data/deepscores_136_yolo_tiled_stem_smoke_v1/`.
- Train tiles: 222.
- Validation tiles: 229.
- Test tiles: 264.
- Retained focus labels: `stem = 4361`, `ledgerLine = 749`, `augmentationDot = 211`, `beam = 1248`, `flag8thUp = 401`, `flag8thDown = 137`, `flag16thUp = 8`, and `flag16thDown = 10`.
- Projected `stem` width at tiled `target_imgsz=1024`: median `2.666645333333387` pixels.

What is complete:

- The tiled dataset generator exists, is tested, and has smoke evidence.
- The detector runner can consume a tiled dataset YAML without rematerializing the full-page dataset.
- Documentation now explains why the stem score is failing and how the project is fixing it.
- The active 1536 fine-tune was not interrupted by this work.

What is not complete:

- No tiled detector training run has completed.
- No tiled `metrics.json` exists yet.
- No claim should be made that tiling improved model metrics until a tiled run writes generated metric provenance.

Next exact step:

1. Keep monitoring `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`.
2. When it completes, inspect `metrics.json` and compare `stem`, `ledgerLine`, `augmentationDot`, `beam`, `flag8thUp`, `flag8thDown`, headline AP metrics, recall, and F1 against `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`.
3. If `stem` remains near zero, generate the full tiled dataset:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\materialize_tiled_yolo_dataset.py `
  --output-dir runs\data\deepscores_136_yolo_tiled_stem_v1 `
  --tile-size 384 `
  --stride 256 `
  --target-imgsz 1024
```

4. Verify the full tiled dataset before training:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --dataset-yaml runs\data\deepscores_136_yolo_tiled_stem_v1\dataset.yaml `
  --dataset-id deepscores_136_yolo_tiled_stem_v1 `
  --materialize-only
```

5. Launch tiled training only after the active v2 run is complete or cleanly stopped:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --run-id detection_136class_yolov8m_tiled_stem_img1024_v1 `
  --dataset-yaml runs\data\deepscores_136_yolo_tiled_stem_v1\dataset.yaml `
  --dataset-id deepscores_136_yolo_tiled_stem_v1 `
  --model runs\detection\detection_136class_yolov8m_finetune_img1536_maxdet2000_v2\ultralytics\train\weights\best.pt `
  --epochs 40 `
  --imgsz 1024 `
  --batch 4 `
  --workers 0 `
  --device 0 `
  --patience 10 `
  --max-det 2000
```

6. If the v2 checkpoint is not usable, use `runs\detection\detection_136class_yolov8m_finetune_img1472_maxdet2000_v1\ultralytics\train\weights\best.pt` in the tiled training command.

## 2026-06-02 - Agent Handoff - Dot Fallback Tightened And V2 Fine-Tune Launched

Milestone worked:

- M7 - Detector Metric Improvement / local note-extraction demo quality

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `scripts/extract_notes_from_image.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/ARCHITECTURE.md`
- `docs/METRIC_IMPROVEMENT.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Generated ignored evidence:

- `runs/demo/image_note_extraction_v6/best_snapshot.pt`
- `runs/demo/image_note_extraction_v6/image_notes.json`
- `runs/demo/image_note_extraction_v6/image_notes.mid`
- `runs/demo/image_note_extraction_v6/image_notes.musicxml`
- `runs/demo/image_note_extraction_v6/image_notes_overlay.png`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/finetune_v2_retry.pid`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/finetune_v2_retry_child.pid`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/finetune_v2_retry_stdout.log`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/finetune_v2_retry_stderr.log`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/finetune_v2_retry_launch_command.txt`
- `runs/detection/detection_136class_yolov8m_finetune_img1536_maxdet2000_v2/finetune_v2_retry_launch_metadata.json`

What changed:

- Confirmed the previous fine-tune `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1` had completed and generated final V2 artifacts.
- Recorded completed fine-tune AP metrics: `mAP@0.5:0.95 = 0.6777474953487629` and `mAP@0.5 = 0.8226206920791271`.
- Recorded completed fine-tune threshold metrics: `precision@0.5 = 0.8457099520968777`, `recall@0.5 = 0.7738772781467206`, and `F1@0.5 = 0.8082006373091581`.
- Recorded the critical rhythm limitation: completed fine-tune `stem = 0.0` mAP, while `beam = 0.7824341036579809`, `flag8thUp = 0.7196678490605957`, `flag8thDown = 0.8042434669433673`, and `augmentationDot = 0.25050444606568056`.
- Added `use_cv_dot_fallback` to `extract_notes_from_image()`. Default behavior now enables CV dot fallback only for CV-only extraction, not for YOLO-backed extraction.
- Added CLI flag `--use-cv-dot-fallback` so YOLO-backed runs can opt into the old contour-dot behavior deliberately.
- Added tests proving YOLO-backed extraction does not turn a nearby visual speck into a dotted note by default, while detector-confirmed `augmentationDot` boxes still produce dotted notes.
- Re-ran the uploaded Arabic page extraction as `runs/demo/image_note_extraction_v6/`.
- Launched active follow-up fine-tune `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` from the completed v1 fine-tune `best.pt`.

Uploaded Arabic page verification after safer dot policy:

- Command:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png --output-dir runs\demo\image_note_extraction_v6 --device cpu --title "Extracted Notes"`
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Extracted note events: `319`.
- Stem-confirmed notes: `0`.
- Dotted notes: `7`, down from `38` in `v5`.
- Key signatures: every staff system has `{"B": -1}`.
- MusicXML key fifths: `-1`.
- B-flat notes from detected key signature: `53`.
- Duration distribution: `0.25:36`, `0.5:192`, `1.0:74`, `1.5:6`, `2.0:10`, `3.0:1`.
- MusicXML parse check: `319` notes, `7` dot tags, one key fifths value `-1`, and `53` flat alters.
- MIDI path: `runs/demo/image_note_extraction_v6/image_notes.mid`.
- MIDI size: `2871` bytes.
- Warning in output: `CV augmentation-dot fallback disabled; only detector-confirmed augmentationDot symbols were used.`

Active follow-up fine-tune:

- Run id: `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2`.
- Source checkpoint: `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/best.pt`.
- First launch attempt failed before training because the PowerShell command expanded `$env:PYTHONPATH` incorrectly; this failed attempt is recorded in `finetune_v2_stdout.log` and `finetune_v2_stderr.log`.
- Corrected retry launch local time: 2026-06-02 `23:11:35`.
- Parent PID: `34896`, saved in `finetune_v2_retry.pid`.
- Python child PID: `28432`, saved in `finetune_v2_retry_child.pid`.
- Retry stdout log: `finetune_v2_retry_stdout.log`.
- Retry stderr log: `finetune_v2_retry_stderr.log`.
- Startup evidence: Ultralytics loaded the completed v1 fine-tune checkpoint, transferred 475/475 pretrained items, used CUDA on the RTX 3080 Laptop GPU, and reached epoch `1/50`.

Internet/source-backed training conclusion:

- DeepScores is a tiny-object music detection benchmark, so whole-page training can leave stems/ledger lines too small in model pixels.
- MUSCIMA++ models notation as primitives plus relationships, including notehead-stem and key-signature attachment edges; rhythm is therefore not solved by notehead labels alone.
- Ultralytics data augmentation and OBB docs support the next engineering direction: higher-resolution/tiled data, augmentation targeted at rare/thin symbols, and possibly OBB/segmentation for line-like objects.
- If `stem` remains near zero after the active v2 run, the next correct experiment is a tiled/cropped staff-system or measure-level dataset that remaps existing labels, plus separate threshold calibration for rhythm symbols. Blindly adding more whole-page epochs is not the best engineering bet.

Commands run:

- Fine-tune completion check for `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1` - passed; final `metrics.json` exists.
- Process check for old v1 PID files - passed; old parent/child PIDs are not running.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py -q` - passed, 8 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png --output-dir runs\demo\image_note_extraction_v6 --device cpu --title "Extracted Notes"` - passed.
- MusicXML/MIDI artifact check for `runs/demo/image_note_extraction_v6/` - passed; MIDI size `2871` bytes and MusicXML has `7` dot tags.
- GPU check with `nvidia-smi` - passed before launch; RTX 3080 Laptop GPU was available.
- Active v2 fine-tune launch - passed on retry; parent PID `34896`, child PID `28432`, epoch `1/50` in stdout.

Failures:

- First v2 launch attempt failed before training with `ModuleNotFoundError: No module named 'melodious_v2'` because the child PowerShell command expanded `$env:PYTHONPATH` while constructing the command string. This produced no training rows and is superseded by the retry launch.

Next exact step:

- Monitor `detection_136class_yolov8m_finetune_img1536_maxdet2000_v2` with the command in `docs/METRIC_IMPROVEMENT.md`. When it finishes, compare headline metrics and especially `stem`, `ledgerLine`, `augmentationDot`, `beam`, and `flag*` against the completed v1 fine-tune. If `stem` is still near zero, build a tiled/cropped thin-symbol dataset or add a clearly labeled CV stem attachment fallback before doing more whole-page training.

## 2026-06-02 - Agent Handoff - Key Signature Application Added

Milestone worked:

- M7 - Detector Metric Improvement / local demo rescue path

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/ARCHITECTURE.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `README.md`

Generated ignored evidence:

- `runs/demo/image_note_extraction_v5/best_snapshot.pt`
- `runs/demo/image_note_extraction_v5/image_notes.json`
- `runs/demo/image_note_extraction_v5/image_notes.mid`
- `runs/demo/image_note_extraction_v5/image_notes.musicxml`
- `runs/demo/image_note_extraction_v5/image_notes_overlay.png`

What changed:

- Added generic pitch-modifier support to the local note extraction demo.
- YOLO `keyFlat`, `keySharp`, and `keyNatural` detections are now mapped to per-staff key signatures by staff geometry.
- YOLO explicit `accidental*` detections now override the key signature for the attached note.
- Flat glyphs use a lower-bulb pitch anchor instead of the bbox center; this avoids mapping detected `keyFlat` glyphs to the wrong staff step.
- Extracted notes now record `alter` and `pitch_source`.
- Extraction results now record `key_signatures` and `key_fifths`.
- MusicXML now writes detected key fifths and per-note `<alter>` values.
- Overlay note labels show altered pitches with `b`/`#`.
- Added a regression test proving a detected `keyFlat` on B maps B4 to B-flat/MIDI 70 and writes `<fifths>-1</fifths>` plus `<alter>-1</alter>`.

Important diagnosis:

- The user's uploaded Arabic page already had high-confidence YOLO detections for `keyFlat`; the extractor was ignoring them because it only retained noteheads and rhythm symbols.
- This is not an immediate training failure for this page. The detector taxonomy separates key-signature symbols from inline accidentals: use `keyFlat` for the start-of-staff flat, not `accidentalFlat`.
- Existing validation evidence for key signatures is strong: `detection_136class_yolov8m_eval_img1472_maxdet2000_v1` reports `keyFlat` `mAP@0.5:0.95 = 0.8426791417729934`.

Uploaded Arabic page verification after key-signature support:

- Command:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png --output-dir runs\demo\image_note_extraction_v5 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --title "Tislam Alaina Alhawa"`
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Extracted note events: `319`.
- Stem-confirmed notes: `0`.
- Dotted notes: `38`.
- Key signatures: every staff system has `{"B": -1}`.
- MusicXML key fifths: `-1`.
- B-flat notes from detected key signature: `53`.
- Explicit sharp notes from detected inline accidentals: `2`.
- Duration distribution: `0.25:28`, `0.375:8`, `0.5:175`, `0.75:8`, `1.0:68`, `1.5:21`, `2.0:10`, `3.0:1`.
- Rhythm source distribution: `beam_x1:173`, `black_notehead_quarter_rule_no_stem:68`, `beam_x2:28`, `black_notehead_quarter_rule_no_stem+augmentation_dot:21`, `notehead_class:10`, `beam_x2+augmentation_dot:8`, `beam_x1+augmentation_dot:7`, `flag:2`, `notehead_class+augmentation_dot:1`, `flag+augmentation_dot:1`.
- Pitch source distribution: `staff_geometry:264`, `key_signature:flat:53`, `explicit_accidental:accidentalSharp:2`.
- MusicXML parse check: `319` notes, `38` dot tags, one `<fifths>-1</fifths>`, and `53` `<alter>-1</alter>` tags.
- MIDI path: `runs/demo/image_note_extraction_v5/image_notes.mid`.
- MIDI size: `2879` bytes.
- Overlay path: `runs/demo/image_note_extraction_v5/image_notes_overlay.png`.

Commands run:

- Probe current checkpoints on `C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png` for key/accidental predictions - passed; available checkpoints returned 9 high-confidence `keyFlat` boxes and 1 inline `accidentalSharp` box at `conf=0.12`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py -q` - passed, 6 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\omr\note_extraction.py scripts\extract_notes_from_image.py tests\test_note_extraction_demo.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png --output-dir runs\demo\image_note_extraction_v5 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --title "Tislam Alaina Alhawa"` - passed.
- MusicXML parse check for `runs/demo/image_note_extraction_v5/image_notes.musicxml` - passed, 319 notes, 38 dot tags, one key fifths value `-1`, and 53 flat alters.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest -q` - passed, 42 tests with 1 third-party deprecation warning from `torch_geometric`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 14 documentation files.
- Fine-tune process check - parent PID `35952` alive, child PID `43740` alive.
- Latest fine-tune `results.csv` check - latest completed row epoch `36`, `metrics/mAP50(B) = 0.81375`, `metrics/mAP50-95(B) = 0.63024`. Treat these as training-run validation CSV values, not final V2 metric provenance.

Limitations:

- This adds detected key-signature application, not full music-theory reconstruction.
- Measure-scoped accidental persistence/cancellation is still not implemented; explicit accidentals currently affect only the attached note.
- Rhythm remains the main demo weakness because this page still has `0` stem-confirmed notes.

Next exact step:

- Keep monitoring the fine-tune. For local demo quality, target stem detection next; for pitch quality, add measure-aware accidental persistence/cancellation after measure/barline reconstruction exists.

## 2026-06-02 - Agent Handoff - Uploaded Image Staff Detection Fixed

Milestone worked:

- M7 - Detector Metric Improvement / local demo rescue path

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/ARCHITECTURE.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `README.md`

Generated ignored evidence:

- `runs/demo/image_note_extraction_v3/best_snapshot.pt`
- `runs/demo/image_note_extraction_v3/image_notes.json`
- `runs/demo/image_note_extraction_v3/image_notes.mid`
- `runs/demo/image_note_extraction_v3/image_notes.musicxml`
- `runs/demo/image_note_extraction_v3/image_notes_overlay.png`

What changed:

- Staff detection now builds and merges candidate staff systems from dark-line, light-line, and adaptive horizontal masks.
- This fixes a concrete uploaded-image failure where `C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png` initially detected only 4 staff systems even though the page has 9 visible systems.
- A regression test now covers light staff lines so faded/antialiased staff strokes are not silently dropped.

Uploaded Arabic page verification:

- Command:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png --output-dir runs\demo\image_note_extraction_v3 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --title "Tislam Alaina Alhawa"`
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Extracted note events: `319`.
- Stem-confirmed notes: `0`.
- Dotted notes: `37`.
- Duration distribution: `0.25:29`, `0.375:7`, `0.5:178`, `0.75:9`, `1.0:65`, `1.5:20`, `2.0:10`, `3.0:1`.
- Rhythm source distribution: `beam_x1:176`, `black_notehead_quarter_rule_no_stem:65`, `beam_x2:29`, `black_notehead_quarter_rule_no_stem+augmentation_dot:20`, `notehead_class:10`, `beam_x1+augmentation_dot:8`, `beam_x2+augmentation_dot:7`, `flag:2`, `notehead_class+augmentation_dot:1`, `flag+augmentation_dot:1`.
- MusicXML parse check: `319` notes and `37` `<dot/>` tags.
- MIDI path: `runs/demo/image_note_extraction_v3/image_notes.mid`.
- MIDI size: `2878` bytes.
- Overlay path: `runs/demo/image_note_extraction_v3/image_notes_overlay.png`.

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest tests\test_note_extraction_demo.py -q` - passed, 5 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\omr\note_extraction.py scripts\extract_notes_from_image.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png --output-dir runs\demo\image_note_extraction_v3 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --title "Tislam Alaina Alhawa"` - passed.
- MusicXML parse check for `runs/demo/image_note_extraction_v3/image_notes.musicxml` - passed, 319 notes and 37 dot tags.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m pytest -q` - passed, 41 tests with 1 third-party deprecation warning from `torch_geometric`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 14 documentation files.
- Fine-tune process check - parent PID `35952` alive, child PID `43740` alive.
- Latest fine-tune `results.csv` check - latest completed row epoch `33`, `metrics/mAP50(B) = 0.81344`, `metrics/mAP50-95(B) = 0.63103`. Treat these as training-run validation CSV values, not final V2 metric provenance.

Limitations:

- The generated output is much more complete than the first uploaded-image run, but it is still a local demo artifact rather than a measured detector metric.
- The extractor still reports `0` stem-confirmed notes on this page. Quarter values without beams/flags still come from `black_notehead_quarter_rule_no_stem`, so rhythm is not yet trustworthy enough for final product claims.
- At this stage, pitch still assumed treble clef and did not reconstruct key signature accidentals, measures, ties, slurs, voices, or full graph assembly. This was later superseded by the key-signature support section above; measure-scoped accidental persistence/cancellation is still not implemented.

Next exact step:

- Keep monitoring the fine-tune. For local demo quality, target stem detection next with a separate stem threshold probe, a CV stem-line attachment fallback, or fine-tuning that improves thin-line/stem coverage.

## 2026-06-02 - Agent Handoff - Local Note Extraction Demo Added

Milestone worked:

- M7 - Detector Metric Improvement / local demo rescue path

Files changed:

- `src/melodious_v2/omr/__init__.py`
- `src/melodious_v2/omr/note_extraction.py`
- `scripts/extract_notes_from_image.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/ARCHITECTURE.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `README.md`

Generated ignored evidence:

- `runs/demo/sad_romance_note_extraction_v2/best_snapshot.pt`
- `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes.json`
- `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes.mid`
- `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes.musicxml`
- `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes_overlay.png`
- `runs/demo/sad_romance_note_extraction_v2_stdout.json`

What happened:

- The earlier API upload-to-MIDI test produced a bad toy output because the FastAPI upload route still uses `heuristic_bootstrap` and `minimal_midi_base64()`.
- A separate local note extraction demo path was added so the user can test actual note extraction from a clean sheet image without waiting for the full API rewrite.
- The new CLI snapshots the YOLO checkpoint before CPU inference, detects notehead boxes, detects staff geometry, maps noteheads to treble-clef pitch, infers simple rhythm from beams/flags/augmentation dots, and writes note JSON, overlay PNG, compact MusicXML, and real MIDI note events.
- The current API upload route remains unchanged and must still be labeled `heuristic_bootstrap`.

Sad Romance verification:

- Command:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png --output-dir runs\demo\sad_romance_note_extraction_v2 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --default-quarter-length 1.0 --title "Sad Romance"`
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Extracted note events: `197`.
- Dotted notes: `17`.
- Duration distribution: `0.25:1`, `0.5:80`, `0.75:7`, `1.0:71`, `1.5:8`, `2.0:23`, `3.0:2`, `4.0:5`.
- MusicXML parse check: `197` notes and `17` `<dot/>` tags.
- MIDI path: `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes.mid`.
- MIDI size: `1808` bytes.
- MIDI header: `MThd`.
- Overlay path: `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes_overlay.png`.

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png --output-dir runs\demo\sad_romance_note_extraction_v2 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --default-quarter-length 1.0 --title "Sad Romance"` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\omr\note_extraction.py scripts\extract_notes_from_image.py tests\test_note_extraction_demo.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_note_extraction_demo.py` - passed, 3 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after the final status/handoff wording update, checked 14 documentation files.
- `Get-Process -Id 35952,43740 -ErrorAction SilentlyContinue` - passed; the fine-tune parent and child processes were still alive after CPU note extraction.
- Latest fine-tune `results.csv` check after CPU note extraction - passed; latest completed row epoch `28`, `metrics/mAP50(B) = 0.81045`, `metrics/mAP50-95(B) = 0.6272`. Treat these as training-run validation CSV values, not final V2 metric provenance.

Limitations:

- This is not the API upload path yet.
- This is not an evaluation metric and must not be reported as detector `mAP`.
- The current pitch mapping assumes treble clef.
- The current rhythm model defaults unbeamed black noteheads to quarter notes and uses nearby beam/flag/dot detections, but it remains heuristic.
- At this stage, accidentals, key signature, ties, slurs, beams, measures, and full graph assembly were not reconstructed in this demo path. This was later superseded for detected key signatures and attached explicit accidentals only.

Next exact step:

- Keep monitoring the fine-tune. If the user wants product-demo upload behavior, wire `scripts/extract_notes_from_image.py` / `melodious_v2.omr.note_extraction` into the FastAPI upload route behind an explicit non-default mode, return `detector_mode = "yolo_note_demo"` or similar, and keep response warnings clear that rhythm/pitch reconstruction is heuristic.

## 2026-06-02 - Agent Handoff - Local Note Extraction Rhythm Improved

Milestone worked:

- M7 - Detector Metric Improvement / local demo rescue path

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `scripts/extract_notes_from_image.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/ARCHITECTURE.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `README.md`

Generated ignored evidence:

- `runs/demo/sad_romance_note_extraction_v2/best_snapshot.pt`
- `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes.json`
- `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes.mid`
- `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes.musicxml`
- `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes_overlay.png`
- `runs/demo/sad_romance_note_extraction_v2_stdout.json`

What changed:

- Black noteheads now default to quarter notes instead of eighth notes.
- YOLO rhythm symbols are retained alongside noteheads so nearby `beam`, `flag*`, and `augmentationDot` detections can adjust note duration.
- A CV augmentation-dot fallback was added because dots are tiny and the YOLO detector can miss them.
- MusicXML now writes `<dot/>` for dotted durations.
- MIDI event sorting now writes note-off events before note-on events at the same tick.

Sad Romance verification after rhythm update:

- Command:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png --output-dir runs\demo\sad_romance_note_extraction_v2 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --title "Sad Romance"`
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Extracted note events: `197`.
- Dotted notes: `17`.
- Duration distribution: `0.25:1`, `0.5:80`, `0.75:7`, `1.0:71`, `1.5:8`, `2.0:23`, `3.0:2`, `4.0:5`.
- Rhythm sources: `default_quarter:71`, `beam_x1:68`, `notehead_class:28`, `flag:13`, `default_quarter+augmentation_dot:8`, `beam_x1+augmentation_dot:4`, `flag+augmentation_dot:3`, `notehead_class+augmentation_dot:2`.
- MusicXML parse check: `197` notes and `17` `<dot/>` tags.
- MIDI path: `runs/demo/sad_romance_note_extraction_v2/sad_romance_clearer_smooth_notes.mid`.
- MIDI size: `1808` bytes.

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\omr\note_extraction.py scripts\extract_notes_from_image.py tests\test_note_extraction_demo.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_note_extraction_demo.py` - passed, 4 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png --output-dir runs\demo\sad_romance_note_extraction_v2 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --title "Sad Romance"` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 40 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 14 documentation files.

Limitations:

- Rhythm remains heuristic. It is better for quarters, beamed notes, flags, and visible augmentation dots, but it still does not reconstruct measures, ties, measure-scoped accidental persistence/cancellation, voices, or complete beaming semantics.

## 2026-06-02 - Agent Handoff - Stem-Aware Rhythm Labels Added

Milestone worked:

- M7 - Detector Metric Improvement / local demo rescue path

Files changed:

- `src/melodious_v2/omr/note_extraction.py`
- `tests/test_note_extraction_demo.py`
- `docs/NOTE_EXTRACTION_DEMO.md`
- `docs/ARCHITECTURE.md`
- `docs/HANDOFF.md`
- `docs/STATUS.md`
- `README.md`

Generated ignored evidence:

- `runs/demo/sad_romance_note_extraction_v3/best_snapshot.pt`
- `runs/demo/sad_romance_note_extraction_v3/sad_romance_clearer_smooth_notes.json`
- `runs/demo/sad_romance_note_extraction_v3/sad_romance_clearer_smooth_notes.mid`
- `runs/demo/sad_romance_note_extraction_v3/sad_romance_clearer_smooth_notes.musicxml`
- `runs/demo/sad_romance_note_extraction_v3/sad_romance_clearer_smooth_notes_overlay.png`
- `runs/demo/sad_romance_note_extraction_v3_stdout.json`

What changed:

- Stem detections are now carried into the local rhythm inference layer.
- `ExtractedNote` now records `stem_detected`.
- Black noteheads with nearby detected stems and no beam/flag are labeled `stem_quarter`.
- Black noteheads without nearby stem/beam/flag are labeled `black_notehead_quarter_rule_no_stem`, making it explicit that the quarter value came from notation fallback rather than a detected stem.

Sad Romance verification:

- Command:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png --output-dir runs\demo\sad_romance_note_extraction_v3 --device cpu --conf 0.12 --imgsz 1472 --max-det 2000 --title "Sad Romance"`
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Extracted note events: `197`.
- Stem-confirmed notes: `0`.
- Dotted notes: `17`.
- Duration distribution: `0.25:1`, `0.5:80`, `0.75:7`, `1.0:71`, `1.5:8`, `2.0:23`, `3.0:2`, `4.0:5`.
- Rhythm source distribution: `black_notehead_quarter_rule_no_stem:71`, `beam_x1:68`, `notehead_class:28`, `flag:13`, `black_notehead_quarter_rule_no_stem+augmentation_dot:8`, `beam_x1+augmentation_dot:4`, `flag+augmentation_dot:3`, `notehead_class+augmentation_dot:2`.
- MusicXML parse check: `197` notes and `17` `<dot/>` tags.

Key finding:

- The detector taxonomy includes `stem`, but the current Sad Romance checkpoint inference returned no usable stem boxes at the selected threshold. This is why the local extractor cannot truthfully claim stem-confirmed quarter notes on that page.

Next exact step:

- Improve stem detection or post-processing before expecting stem-confirmed rhythm. Practical options: evaluate the current/final fine-tuned checkpoint specifically for `stem`, lower the stem confidence threshold separately, add a CV stem-line fallback attached to noteheads, or train/fine-tune with stronger thin-line/stem coverage.

## 2026-06-02 - Agent Handoff - M7 Fine-Tune Interrupted And Resumed

Milestone worked:

- M7 - Detector Metric Improvement

Files changed:

- `scripts/run_detection_136class_yolo.py`
- `tests/test_full_detector_m3.py`
- `docs/HANDOFF.md`
- `docs/METRIC_IMPROVEMENT.md`
- `docs/STATUS.md`

Generated ignored evidence:

- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7_launch_command.txt`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7_launch_metadata.json`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7.pid`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7_child.pid`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7_stdout.log`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/resume_epoch7_stderr.log`

What happened:

- The fine-tune launched on 2026-06-01 did not complete.
- It stopped after seven completed epochs and while epoch 8 was in progress.
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/metrics.json` does not exist yet.
- `results.csv` has seven completed rows.
- Best completed primary training-row metric so far: epoch 7, `metrics/mAP50-95(B) = 0.6116`.
- Best completed training-row `metrics/mAP50(B)` so far: epoch 6, `0.79679`.
- Clean checkpoint files exist at `ultralytics/train/weights/last.pt` and `best.pt`, last updated after epoch 7.

Code change:

- Added `--resume-training` and `--resume-checkpoint` to `scripts/run_detection_136class_yolo.py`.
- The resume path uses `YOLO(last.pt).train(resume=True, device=..., workers=...)`, then continues through the normal V2 final validation/export/report flow when training completes.
- Focused detector tests now cover the resume arguments.

Commands run:

- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py tests\test_full_detector_m3.py` - passed.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py` - passed, 5 tests.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 36 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 13 documentation files.
- `git commit -m "Add detector training resume support"` - passed with commit `6636622`.
- Resume launch through `Start-Process -WindowStyle Hidden` - passed.
- `Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like '*detection_136class_yolov8m_finetune_img1472_maxdet2000_v1*' } | Format-List ProcessId,ParentProcessId,CommandLine` - passed; documented resume parent PID `35952` and child PID `43740`.

Resume status:

- Resume local launch time: `2026-06-02T01:05:09`.
- Resume command: `..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_finetune_img1472_maxdet2000_v1 --resume-training --resume-checkpoint runs\detection\detection_136class_yolov8m_finetune_img1472_maxdet2000_v1\ultralytics\train\weights\last.pt --epochs 50 --imgsz 1472 --batch 1 --workers 0 --device 0 --patience 15 --max-det 2000`.
- Ultralytics resume evidence: `Resuming training ... from epoch 8 to 50 total epochs`.
- Resume parent PID: `35952`.
- Resume active child PID: `43740`.

Monitor command:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$run='runs\detection\detection_136class_yolov8m_finetune_img1472_maxdet2000_v1'
Get-Process -Id ([int](Get-Content "$run\resume_epoch7.pid")) -ErrorAction SilentlyContinue
Get-Process -Id ([int](Get-Content "$run\resume_epoch7_child.pid")) -ErrorAction SilentlyContinue
Get-Content -Tail 80 "$run\resume_epoch7_stdout.log"
if (Test-Path "$run\ultralytics\train\results.csv") { Import-Csv "$run\ultralytics\train\results.csv" | Select-Object -Last 1 }
```

Next exact step:

- Keep the resumed fine-tune running unless the user explicitly asks to stop. When it completes, confirm `metrics.json` exists, regenerate `docs/EXPERIMENTS.md`, compare validation metrics against `detection_136class_yolov8m_eval_img1472_maxdet2000_v1`, update docs, run tests and `scripts/validate_metric_claims.py`, then commit the completed-result documentation.

## 2026-06-01 - Agent Handoff - M7 Fine-Tune Launched

Milestone worked:

- M7 - Detector Metric Improvement

Files changed:

- `docs/HANDOFF.md`
- `docs/METRIC_IMPROVEMENT.md`
- `docs/STATUS.md`

Generated ignored evidence:

- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_launch_command.txt`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_launch_metadata.json`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune.pid`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_child.pid`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_stdout.log`
- `runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/finetune_stderr.log`

Commands run:

- Fine-tune launch through `Start-Process -WindowStyle Hidden` - passed.
- `Get-Content -Path runs\detection\detection_136class_yolov8m_finetune_img1472_maxdet2000_v1\finetune_stdout.log -Tail 120` - passed; startup logs show CUDA on RTX 3080 Laptop GPU, 475/475 pretrained items transferred, and epoch `1/50` started.
- `Get-Content -Path runs\detection\detection_136class_yolov8m_finetune_img1472_maxdet2000_v1\finetune_stderr.log -Tail 120` - passed; no stderr output at startup.
- `Get-CimInstance Win32_Process -Filter "ProcessId = 34780 or ProcessId = 23612" | Format-List ProcessId,ParentProcessId,CommandLine` - passed; documented parent and active child command lines.

Fine-tune status:

- Run id: `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1`.
- Launch local time: `2026-06-01T02:46:32`.
- Parent PID at launch: `34780`.
- Active Python child PID observed after launch: `23612`.
- Command: `..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_finetune_img1472_maxdet2000_v1 --model artifacts\models\detection_136class_yolov8m_v1\best.pt --epochs 50 --imgsz 1472 --batch 1 --workers 0 --device 0 --patience 15 --max-det 2000`.
- Startup evidence: training reached epoch `1/50`; no completed epoch metric row had been documented yet in this handoff.

Monitor command:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$run='runs\detection\detection_136class_yolov8m_finetune_img1472_maxdet2000_v1'
Get-Process -Id ([int](Get-Content "$run\finetune.pid")) -ErrorAction SilentlyContinue
Get-Process -Id ([int](Get-Content "$run\finetune_child.pid")) -ErrorAction SilentlyContinue
Get-Content -Tail 80 "$run\finetune_stdout.log"
if (Test-Path "$run\ultralytics\train\results.csv") { Import-Csv "$run\ultralytics\train\results.csv" | Select-Object -Last 1 }
```

Next exact step:

- Keep monitoring the fine-tune. When it finishes, the runner should finalize the run by writing `metrics.json`, `report.md`, `manifest.json`, `analysis.json`, `artifacts.json`, model artifacts, and an ONNX/parity artifact unless export fails. Then regenerate `docs/EXPERIMENTS.md`, compare validation metrics against `detection_136class_yolov8m_eval_img1472_maxdet2000_v1`, and update docs.

## 2026-06-01 - Agent Handoff - M7 Class Coverage Audit

Milestone worked:

- M7 - Detector Metric Improvement

Files changed:

- `src/melodious_v2/evaluation/class_coverage.py`
- `scripts/audit_detector_class_coverage.py`
- `tests/test_detector_class_coverage.py`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/METRIC_IMPROVEMENT.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`

Generated ignored evidence:

- `runs/detection/detection_136class_class_coverage_audit_v1/class_coverage.json`
- `runs/detection/detection_136class_class_coverage_audit_v1/class_coverage.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\evaluation\class_coverage.py scripts\audit_detector_class_coverage.py tests\test_detector_class_coverage.py` - passed.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_detector_class_coverage.py` - passed, 2 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\audit_detector_class_coverage.py --metrics runs\detection\detection_136class_yolov8m_eval_img1472_maxdet2000_v1\metrics.json --output-dir runs\detection\detection_136class_class_coverage_audit_v1` - passed.
- `nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader` - passed; GPU is NVIDIA GeForce RTX 3080 Laptop GPU with 16384 MiB VRAM and 455 MiB used at check time.
- `Get-Process python -ErrorAction SilentlyContinue | Select-Object Id,ProcessName,CPU,WorkingSet,Path` - returned no active Python training process.
- `Test-Path runs\detection\detection_136class_yolov8m_finetune_img1472_maxdet2000_v1` - returned `False`.
- `Test-Path artifacts\models\detection_136class_yolov8m_v1\best.pt` - returned `True`.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 36 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 13 documentation files.

Coverage findings:

- Detector taxonomy/model head: 136 classes.
- Any local label support across train/validation/test: 115 classes.
- Zero-label taxonomy classes across all local splits: 21.
- Split support: train 115 classes, validation 103 classes, test 110 classes.
- Validation blind spots: 33 taxonomy classes.
- Training-supported but validation-absent classes: 12.
- Validation-supported classes absent from training: 0.
- Test-supported classes absent from training: 0.
- Best primary M7 validation run still has seven supported zero-map classes: `stem`, `ledgerLine`, `articTenutoBelow`, `dynamicR`, `tremolo3`, `tuplet1`, and `tuplet5`.
- High-support zero-map validation classes: `ledgerLine` and `stem`.

Engineering decision:

- Continue with `detection_136class_yolov8m_finetune_img1472_maxdet2000_v1` because GPU is available and the current best honest path for higher measured validation metrics is fine-tuning from the selected checkpoint using the corrected dense-page inference cap.
- Do not present the fine-tune as a fix for all 136 classes. Fine-tuning on the same labels can improve supported classes but cannot teach the 21 zero-label classes.
- Keep the test split untouched until the detector model and inference configuration are frozen.

Next exact step:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --run-id detection_136class_yolov8m_finetune_img1472_maxdet2000_v1 `
  --model artifacts\models\detection_136class_yolov8m_v1\best.pt `
  --epochs 50 `
  --imgsz 1472 `
  --batch 1 `
  --workers 0 `
  --device 0 `
  --patience 15 `
  --max-det 2000
```

## 2026-06-01 - Agent Handoff - M7 Dense-Page Metric Improvement

Milestone worked:

- M7 - Detector Metric Improvement

Files changed:

- `configs/detection_136class_eval_resolution_sweep.yaml`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/METRIC_IMPROVEMENT.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`
- `scripts/run_detection_136class_yolo.py`
- `tests/test_full_detector_m3.py`

Detector runs generated:

- `detection_136class_yolov8m_eval_img1248_maxdet2000_v1`
- `detection_136class_yolov8m_eval_img1248_maxdet3000_v1`
- `detection_136class_yolov8m_eval_img1280_maxdet2000_v1`
- `detection_136class_yolov8m_eval_img1344_maxdet2000_v1`
- `detection_136class_yolov8m_eval_img1408_maxdet2000_v1`
- `detection_136class_yolov8m_eval_img1472_maxdet2000_v1`
- `detection_136class_yolov8m_eval_img1536_maxdet2000_v1`
- `detection_136class_yolov8m_eval_img1536_maxdet2000_iou08_v1`

Commands run:

- Validation label-density PowerShell summary - passed; 136 validation images average 705.448529411765 labels, max 2011 labels, 109 pages above 300 labels, and 28 pages above 1000 labels.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py tests\test_full_detector_m3.py` - passed after fixing one indentation mistake introduced while adding `--nms-iou`.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py` - passed, 5 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_eval_img1248_maxdet2000_v1 --finalize-existing-run --checkpoint artifacts\models\detection_136class_yolov8m_v1\best.pt --imgsz 1248 --batch 2 --workers 0 --device 0 --skip-export --max-det 2000` - passed.
- Same command pattern for `imgsz 1248 --max-det 3000` - passed; no metric gain over 2000.
- Same command pattern for `imgsz 1280 --max-det 2000` - passed.
- Same command pattern for `imgsz 1344 --max-det 2000`, batch 1 - passed.
- Same command pattern for `imgsz 1408 --max-det 2000`, batch 1 - passed.
- Same command pattern for `imgsz 1472 --max-det 2000`, batch 1 - passed and produced the best primary metric.
- Same command pattern for `imgsz 1536 --max-det 2000`, batch 1 - passed and produced the best secondary `mAP@0.5`.
- Same command pattern for `imgsz 1536 --max-det 2000 --nms-iou 0.8`, batch 1 - passed; metric regressed against default NMS IoU.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 34 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 13 documentation files.

Best current primary result:

- Run id: `detection_136class_yolov8m_eval_img1472_maxdet2000_v1`.
- Metric source: `runs/detection/detection_136class_yolov8m_eval_img1472_maxdet2000_v1/metrics.json`.
- Primary `mAP@0.5:0.95`: `0.6204968163150985`.
- Secondary `mAP@0.5`: `0.7833788545364062`.
- `precision@0.5`: `0.8166240104606699`.
- `recall@0.5`: `0.7367130723503518`.
- `F1@0.5`: `0.7746130448554269`.
- Small-symbol mean `mAP@0.5:0.95`: `0.4832789581411164`.
- Supported validation classes with zero mAP: `7`.

Best current secondary `mAP@0.5` result:

- Run id: `detection_136class_yolov8m_eval_img1536_maxdet2000_v1`.
- Metric source: `runs/detection/detection_136class_yolov8m_eval_img1536_maxdet2000_v1/metrics.json`.
- Primary `mAP@0.5:0.95`: `0.6203204846063568`.
- Secondary `mAP@0.5`: `0.7920129156176505`.
- `precision@0.5`: `0.8107734656247262`.
- `recall@0.5`: `0.7331813762215841`.
- `F1@0.5`: `0.7700277096444413`.
- Small-symbol mean `mAP@0.5:0.95`: `0.4987375853530484`.
- Supported validation classes with zero mAP: `6`.

What improved:

- Best primary `mAP@0.5:0.95` improved by `0.1457597412034697` over the original M3 validation run.
- Best secondary `mAP@0.5` improved by `0.2066917787863014`.
- Best recall improved by `0.2625252988473996`.
- Best detector F1 improved by `0.1583405062573777`.
- Best small-symbol mean `mAP@0.5:0.95` improved by `0.1792769692209457`.
- Supported validation classes with zero mAP decreased from 16 to 6.

What failed or stayed weak:

- The requested absolute +0.2 precision gain is mathematically impossible from the original precision `0.8274236461250144` because precision is capped at 1.0.
- `max_det=3000` did not beat `max_det=2000` at image size 1248.
- NMS IoU 0.8 regressed at image size 1536.
- `ledgerLine` and `stem` remain high-support zero-mAP classes.
- This is not a new trained model and not a test-set result.

Next exact step:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --run-id detection_136class_yolov8m_finetune_img1472_maxdet2000_v1 `
  --model artifacts\models\detection_136class_yolov8m_v1\best.pt `
  --epochs 50 `
  --imgsz 1472 `
  --batch 1 `
  --workers 0 `
  --device 0 `
  --patience 15 `
  --max-det 2000
```

## 2026-05-31 - Agent Handoff - M7 Detector Metric Sweep Improved

Milestone worked:

- M7 - Detector Metric Improvement

Files changed:

- `configs/detection_136class_eval_resolution_sweep.yaml`
- `docs/AGENT_PROMPTS.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/METRIC_IMPROVEMENT.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`
- `scripts/run_detection_136class_yolo.py`
- `tests/test_full_detector_m3.py`

Detector runs generated:

- `detection_136class_yolov8m_eval_img1152_v1`
- `detection_136class_yolov8m_eval_img1248_v1`
- `detection_136class_yolov8m_eval_img1264_v1`; Ultralytics rounded 1264 to 1280.
- `detection_136class_yolov8m_eval_img1280_v1`
- `detection_136class_yolov8m_eval_img1536_v1`
- `detection_136class_yolov8m_eval_img1280_aug_v1`

Commands run:

- `nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader` - passed; GPU is NVIDIA GeForce RTX 3080 Laptop GPU with 16 GB VRAM.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -c "import torch; ..."` - passed; CUDA available.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_eval_img1280_v1 --finalize-existing-run --checkpoint artifacts\models\detection_136class_yolov8m_v1\best.pt --imgsz 1280 --batch 2 --workers 0 --device 0 --skip-export` - passed.
- Same command pattern for `imgsz 1536`, batch 1 - passed.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py tests\test_full_detector_m3.py` - passed.
- `$env:PYTHONPATH='src;.'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py` - passed, 5 tests.
- Same command pattern for `imgsz 1280 --val-augment`, batch 1 - passed; metric regressed.
- Same command pattern for `imgsz 1152`, batch 2 - passed.
- Same command pattern for `imgsz 1248`, batch 2 - passed and produced the best run.
- Same command pattern for `imgsz 1264`, batch 2 - passed, but Ultralytics rounded to 1280.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed.

Best result:

- Run id: `detection_136class_yolov8m_eval_img1248_v1`.
- Metric source: `runs/detection/detection_136class_yolov8m_eval_img1248_v1/metrics.json`.
- Primary `mAP@0.5:0.95`: `0.5058429013539956`.
- Secondary `mAP@0.5`: `0.6069618791829888`.
- `precision@0.5`: `0.8637798517406144`.
- `recall@0.5`: `0.4994362851193167`.
- `F1@0.5`: `0.6329194449061496`.

What improved:

- Primary `mAP@0.5:0.95` improved by `0.0311058262423668` over the original `detection_136class_yolov8m_v1` validation result.
- Secondary `mAP@0.5` improved by `0.0216407423516397`.
- `F1@0.5` improved by `0.0166469063081004`.
- Small-symbol mean `mAP@0.5:0.95` improved by `0.0227814799856731`.

What failed or stayed weak:

- 1536 inference size regressed.
- 1280 validation-time augmentation regressed.
- `ledgerLine` and `stem` remain zero-mAP high-support classes.
- This is not a new trained model and not a test-set result.

Next exact step:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py `
  --run-id detection_136class_yolov8m_finetune_img1248_v1 `
  --model artifacts\models\detection_136class_yolov8m_v1\best.pt `
  --epochs 50 `
  --imgsz 1248 `
  --batch 2 `
  --workers 0 `
  --device 0 `
  --patience 15
```

## 2026-05-31 - Agent Handoff - M6 Deployment Path Prepared

Milestone worked:

- M6 - AWS Public Demo

Files changed:

- `.env.example`
- `.gitignore`
- `README.md`
- `MODEL_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `infra/aws/README.md`
- `infra/aws/smoke_test.ps1`
- `infra/aws/task-definition.template.json`
- `scripts/smoke_public_demo.py`
- `src/melodious_v2/api/app.py`
- `src/melodious_v2/deployment/__init__.py`
- `src/melodious_v2/deployment/smoke.py`
- `tests/test_deployment_smoke.py`

Commits created:

- `c697a4d` - `Document M5 export evaluation completion`.
- `2c6f2bd` - `Add public demo smoke tooling`.

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 32 tests before M6 edits.
- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed.
- `Test-Path runs\graph\graph_legacy_gnn_muscima_val_v1\metrics.json` - passed.
- `Test-Path runs\e2e\e2e_muscima_holdout_xml_fixture_v1\metrics.json` - passed.
- API local smoke through FastAPI `TestClient` - passed; `/health` returned `ok`, `/version` returned schema `2.0`, sample transcription completed, detector mode was `sample_payload`, and artifact download returned 721 bytes.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\deployment\smoke.py scripts\smoke_public_demo.py src\melodious_v2\api\app.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_deployment_smoke.py` - passed, 1 test.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --local-testclient --output runs\deploy\m6_local_smoke\smoke.json` - passed; wrote ignored local smoke evidence.
- `Get-Command aws -ErrorAction SilentlyContinue` - returned no AWS CLI path.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 33 tests after M6 changes.
- `cd frontend; npm run build` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 12 documentation files.

What is complete:

- The API can be configured for a deployed frontend with `MELODIOUS_CORS_ORIGINS`.
- A Python smoke tester verifies `/health`, `/version`, `/samples`, sample transcription, MusicXML download, and MIDI download.
- The PowerShell AWS smoke script verifies the same public-demo path and can write JSON evidence.
- The AWS runbook documents backend image build/push, ECS task/service deployment, frontend S3/CloudFront publishing, smoke testing, and cost-control shutdown.
- Ignored generated deployment state is reserved under `infra/aws/generated/`.

What failed or is blocked:

- Actual public AWS deployment was not run because AWS CLI is not installed or not available in this workspace.
- Account-local values are not available and must not be committed: AWS profile/role, region, ECR repository state, ECS role ARNs, subnet IDs, security group IDs, ALB target group/listener, S3 frontend bucket, CloudFront distribution ID/domain, and public API host.
- Uploaded-image detector inference still uses `heuristic_bootstrap`.
- Durable private artifact storage is not implemented; current API artifact links are in-memory and suitable only for a short single-task demo.

Next exact step:

- From an AWS-enabled shell, run the M6 local smoke command, then follow `infra/aws/README.md` through public smoke. The first command is:

```powershell
cd C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\melodious-v2
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --local-testclient --output runs\deploy\m6_local_smoke\smoke.json
```

Then run the backend ECR/ECS and frontend S3/CloudFront sections in `infra/aws/README.md`, ending with:

```powershell
..\.venv\Scripts\python.exe scripts\smoke_public_demo.py --api-base-url https://REPLACE_WITH_PUBLIC_API_HOST --output runs\deploy\m6_public_smoke\smoke.json
```

## 2026-05-30 - Agent Handoff - M5 End-to-End Export Complete

Milestone worked:

- M5 - End-to-End Export Quality

Files changed:

- `configs/e2e_muscima_holdout.yaml`
- `scripts/run_e2e_export_eval.py`
- `src/melodious_v2/evaluation/e2e_export.py`
- `src/melodious_v2/export/musicxml.py`
- `tests/test_e2e_export.py`
- `tests/test_export_and_reports.py`
- `README.md`
- `MODEL_CARD.md`
- `docs/AGENT_PROMPTS.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_CARD.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\evaluation\e2e_export.py scripts\run_e2e_export_eval.py src\melodious_v2\export\musicxml.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_e2e_export.py` - passed, 1 test.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_export_and_reports.py` - passed, 4 tests.
- `git commit -m "Add M5 end-to-end export evaluator"` - passed with commit `9c0ddc9`.
- Prerequisite checks - passed; M3 metrics, M3 model metadata, M4 graph metrics, and `docs/EXPERIMENTS.md` graph row all exist.
- API local smoke - passed; `/health` returned `200 ok`, `/version` returned schema `2.0`, sample transcription returned `200 complete`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_e2e_export_eval.py --split holdout --assembly-mode gnn` - passed; wrote M5 run artifacts.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed; index includes `e2e_muscima_holdout_xml_fixture_v1`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 32 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 12 documentation files.

Generated artifacts:

- `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/metrics.json`
- `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/report.md`
- `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/manifest.json`
- `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/artifacts.json`
- `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/config.yaml`
- Per-page exports under `runs/e2e/e2e_muscima_holdout_xml_fixture_v1/exports/`

What is complete:

- A fixed end-to-end holdout run exists.
- MusicXML generation and validation are measured.
- MIDI generation is measured.
- Artifact hashes are recorded for MusicXML, MIDI, payload JSON, and relationship JSON.
- `docs/EXPERIMENTS.md` includes the M5 run.
- `docs/AGENT_PROMPTS.md` now points the next agent to M6.

Final M5 metrics:

- Primary `musicxml_validity_rate`: 1.0.
- `midi_generation_success_rate`: 1.0.
- `page_success_rate`: 1.0.
- `page_count`: 14.
- `failure_count`: 0.
- `relationship_count_total`: 10637.
- `detection_count_total`: 6348.
- `note_like_count_total`: 2563.

Important limitations:

- The run uses MUSCIMA XML-derived payload fixtures, not trained detector outputs.
- The exporter is syntactically valid but musically minimal. This does not prove complete pitch/rhythm/measure correctness.
- Uploaded-image detector inference still uses `heuristic_bootstrap`.

What failed:

- Nothing blocking. The main limitation is scope: M5 measures export validity, not trained detector uploaded-image quality.

Next exact step:

- Start M6 with the active prompt in `docs/AGENT_PROMPTS.md`. Prepare the AWS public demo path, document `/health`, `/version`, sample transcription, and artifact-download smoke commands, and include cost-control/shutdown steps.

## 2026-05-30 - Agent Handoff - M4 Real Assembly Runtime Complete

Milestone worked:

- M4 - Real Assembly Runtime

Files changed:

- `README.md`
- `MODEL_CARD.md`
- `docs/AGENT_PROMPTS.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `scripts/evaluate_gnn_muscima.py`
- `src/melodious_v2/api/models.py`
- `src/melodious_v2/assembly/legacy_gnn.py`
- `src/melodious_v2/assembly/service.py`
- `tests/test_api.py`
- `tests/test_assembly_gnn_runtime.py`
- `tests/test_graph_metrics.py`

Commands run:

- `git switch -c phase-04-assembly` - completed in an earlier step; current branch is `phase-04-assembly`.
- `git commit -m "Initialize Melodious V2 through M3 detector"` - completed in an earlier step with commit `085b049`, scoped to `melodious-v2`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -c "import torch; ... import torch_geometric"` - passed; torch `2.9.0+cu128`, torch_geometric `2.7.0`.
- Checkpoint inspection for `..\outputs\gnn_checkpoint.pt` - passed; SHA256 `065a6881645c080605eb58742cc3f004322b6fca3e712f8bb2953ddb7f038eab`, checkpoint keys `config`, `epoch`, `model_state_dict`, `train_acc`, `train_loss`, `val_acc`, `val_loss`, epoch `79`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile src\melodious_v2\assembly\legacy_gnn.py src\melodious_v2\assembly\service.py scripts\evaluate_gnn_muscima.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_assembly_gnn_runtime.py` - passed, 3 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_graph_metrics.py` - passed, 2 tests.
- `git commit -m "Add checkpoint-gated GNN assembly runtime"` - passed with commit `f1ab688`.
- Initial `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\evaluate_gnn_muscima.py --split val --device cpu` - produced a graph run but revealed a legacy feature-encoder mismatch because the checkpoint's internal unused encoder predicted only `no_relation`.
- Feature-encoder probe with a reconstructed seed-42 encoder - passed; positive-class macro F1 was `0.7590456327823909`.
- `git commit -m "Add MUSCIMA GNN evaluation pipeline"` - passed with commit `0f36b73`.
- API sample smoke with `$env:MELODIOUS_GNN_CHECKPOINT='..\outputs\gnn_checkpoint.pt'` - passed; `applied_mode=gnn`, `fallback_applied=False`, `checkpoint_ready=True`, `inference_ran=True`, `adapter_name=legacy_muscima_gat`, `relationship_count=4`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_api.py` - passed, 4 tests.
- `git commit -m "Test API GNN mode metadata"` - passed with commit `ab2d550`.
- Final `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\evaluate_gnn_muscima.py --split val --device cpu` - passed; metrics provenance commit is `ab2d550`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed; index includes `graph_legacy_gnn_muscima_val_v1`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 30 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 12 documentation files.

Generated artifacts:

- `runs/graph/graph_legacy_gnn_muscima_val_v1/metrics.json`
- `runs/graph/graph_legacy_gnn_muscima_val_v1/report.md`
- `runs/graph/graph_legacy_gnn_muscima_val_v1/manifest.json`
- `runs/graph/graph_legacy_gnn_muscima_val_v1/artifacts.json`
- `runs/graph/graph_legacy_gnn_muscima_val_v1/config.yaml`

What is complete:

- A real legacy GNN checkpoint is wired into the V2 assembly runtime.
- `applied_mode = "gnn"` is gated on actual checkpoint inference.
- Missing checkpoint and bad checkpoint paths return explicit fallback metadata.
- Graph evaluation runs on the fixed M1 MUSCIMA validation manifest and writes project-standard metrics.
- `no_relation` metrics are reported separately from the graph primary metric.
- `docs/EXPERIMENTS.md` includes the M4 graph run.
- `docs/AGENT_PROMPTS.md` now points the next agent to M5.

Final graph metrics:

- Primary `positive_macro_f1`: 0.7590456327823909.
- Separate `no_relation` F1: 0.9425171440096813.
- `stem_notehead` F1: 0.6960721184803607.
- `beam_notegroup` F1: 0.8220191470844213.
- Candidate edges: 48174.
- Positive candidate edges: 6340.

Important limitations:

- This is a validation graph result, not an end-to-end uploaded-image result.
- The GNN is a legacy 15-class relationship model, not a full 136-class relationship model.
- The legacy checkpoint did not save the separate node feature encoder used to build training tensors. V2 reconstructs it from seed `42`; this is documented in the metrics.
- API uploaded-image detector inference still uses `heuristic_bootstrap`.

What failed:

- The first graph evaluation using the checkpoint model's internal node encoder predicted only `no_relation`, giving positive-class macro F1 `0.0`. This exposed the legacy feature-encoder artifact gap. Reconstructing the legacy seed-42 feature encoder fixed the evaluated runtime path and is now documented.

Next exact step:

- Start M5 with the active prompt in `docs/AGENT_PROMPTS.md`. Build a fixed end-to-end evaluator that writes `runs/e2e/{run_id}/metrics.json`, validates MusicXML, writes MIDI artifacts, records export/relationship failures, and keeps uploaded-image detector mode labeled `heuristic_bootstrap` unless a tested ONNX detector adapter is added.

## 2026-05-30 - Agent Handoff - M3 Finalized and M4 Activated

Milestone worked:

- M3 - Full 136-Class Detector finalization
- M4 - Real Assembly Runtime handoff preparation

Files changed:

- `scripts/run_detection_136class_yolo.py`
- `src/melodious_v2/evaluation/full_detector.py`
- `tests/test_full_detector_m3.py`
- `README.md`
- `MODEL_CARD.md`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`

Commands run:

- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train.pid)` - returned no live process; training wrapper was no longer running.
- `Get-Content -Tail 120 runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train_stdout.log` - passed; stdout reached epoch 150/150 and final Ultralytics validation output.
- `Import-Csv runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; 150 completed rows, best CSV row by `mAP@0.5:0.95` was epoch 125 and final row was epoch 150.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests -p test_full_detector_m3.py` - passed, 4 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 25 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m py_compile scripts\run_detection_136class_yolo.py src\melodious_v2\evaluation\full_detector.py` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --finalize-existing-run --workers 0 --device 0` - passed; evaluated existing `best.pt`, exported ONNX, copied artifacts, wrote metrics/report/manifest/artifacts/analysis, and wrote ONNX parity evidence without retraining.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed; experiment index now includes `detection_136class_yolov8m_v1`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed; checked 12 documentation files.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json`
- `runs/detection/detection_136class_yolov8m_v1/report.md`
- `runs/detection/detection_136class_yolov8m_v1/manifest.json`
- `runs/detection/detection_136class_yolov8m_v1/artifacts.json`
- `runs/detection/detection_136class_yolov8m_v1/analysis.json`
- `runs/detection/detection_136class_yolov8m_v1/analysis.md`
- `runs/detection/detection_136class_yolov8m_v1/onnx_parity.json`
- `runs/detection/detection_136class_yolov8m_v1/config.yaml`
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.onnx`
- `artifacts/models/detection_136class_yolov8m_v1/best.pt`
- `artifacts/models/detection_136class_yolov8m_v1/best.onnx`
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json`

What is complete:

- The full configured YOLOv8m run completed all 150 epochs.
- A finalize-only mode now exists for CLI-resumed Ultralytics runs.
- `detection_136class_yolov8m_v1` has project-standard V2 metrics, report, manifest, artifacts, copied config, analysis, ONNX parity, and model metadata.
- `docs/EXPERIMENTS.md` includes the full YOLOv8m run.
- `docs/AGENT_PROMPTS.md` now points the next agent to M4.

Final detector metrics:

- Primary `mAP@0.5:0.95`: 0.4747370751116288.
- `mAP@0.5`: 0.5853211368313491.
- `precision@0.5`: 0.8274236461250144.
- `recall@0.5`: 0.4909790740632496.
- `F1@0.5`: 0.6162725385980492.

Important limitations:

- These are validation metrics, not final test metrics.
- 16 supported validation classes have zero mAP.
- `ledgerLine` and `stem` remain major detector failure classes despite high support.
- API upload inference still uses `heuristic_bootstrap`; the ONNX artifact is not wired into a non-bootstrap detector adapter yet.
- Local ONNX prediction fell back to CPU because `onnxruntime-gpu` is not installed.

What failed:

- The ONNX parity run triggered Ultralytics auto-install attempts for `onnxruntime-gpu`; those attempts failed, then ONNX Runtime CPU fallback succeeded.
- No blocking failure for M3 finalization.

Next exact step:

- Start M4 with the active prompt in `docs/AGENT_PROMPTS.md`. Search for a real GNN/relationship checkpoint, implement the V2 assembly adapter, evaluate on the fixed MUSCIMA graph manifest, write `runs/graph/{run_id}/metrics.json`, and keep `no_relation` separate from positive-class macro F1.

## 2026-05-28 - Agent Handoff - M3 Training Resumed from Epoch 124

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/HANDOFF.md`
- `docs/STATUS.md`

Commands run:

- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train.pid)` - returned no live process; the previous wrapper PID was no longer running.
- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - returned no live Python process; no active trainer was running.
- `Get-Content -Tail 10 runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; latest completed row was epoch 124.
- `Get-Item runs\detection\detection_136class_yolov8m_v1\ultralytics\train\weights\last.pt` - passed; `last.pt` was updated after the epoch-124 result.
- Escalated hidden `Start-Process` resume launch - passed; resumed YOLO training from `runs\detection\detection_136class_yolov8m_v1\ultralytics\train\weights\last.pt`.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train.pid` - passed; PID file contained `24516`.
- `Get-Content -Tail 100 runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train_stdout.log` - passed; showed the latest run checkpoint path, YOLOv8m configuration, `nc=136`, `epochs=150`, `imgsz=1024`, `batch=4`, and `Resuming training ... from epoch 125 to 150 total epochs`.
- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train.pid)` - passed; parent PowerShell PID `24516` was running.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch124_train_stderr.log`

What is complete:

- Training has resumed from the latest run checkpoint after epoch 124 completed.
- Ultralytics confirmed the resumed schedule is epoch 125 through 150.
- The resumed process is running as a hidden background process with PID `24516`.
- Resume logs and PID file are recorded under the existing full-run directory.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- Nothing blocking. The previous resume process was no longer running, so the run was resumed from `ultralytics/train/weights/last.pt`.

Next exact step:

- Monitor training:
  `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_epoch124_train_stdout.log`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-26 - Agent Handoff - M3 Training Resumed from Epoch 95

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed before resume; showed two low-CPU Python processes, not an active high-CPU training run.
- `Get-ChildItem artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22` - passed; confirmed `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, PID file, README, and metadata existed.
- `python -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22\metadata.json` - passed; checkpoint metadata is strict JSON and records `last_completed_epoch = 95`.
- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed; returned `False`, confirming M3 was still incomplete before resume.
- Escalated hidden `Start-Process` resume launch - passed; resumed YOLO training from `artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22\last.pt`.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train.pid` - passed; PID file contained `30436`.
- `Get-Content -Tail 120 runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train_stdout.log` - passed; showed the epoch-95 checkpoint path, YOLOv8m configuration, `nc=136`, `epochs=150`, `imgsz=1024`, `batch=4`, and `Resuming training ... from epoch 96 to 150 total epochs`.
- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train.pid)` - passed; parent PowerShell PID `30436` was running.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe -m unittest discover tests` - passed after resume documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after resume documentation updates, checked 12 documentation files.
- Final live progress check - passed; PID `30436` was still running and stdout showed epoch `96/150` around batch `174/307`.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch95_train_stderr.log`

What is complete:

- Training has resumed from the exact load-verified epoch-95 checkpoint.
- Ultralytics confirmed the resumed schedule is epoch 96 through 150.
- The resumed process is running as a hidden background process with PID `30436`.
- Resume logs and PID file are recorded under the existing full-run directory.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- `Get-CimInstance Win32_Process` failed with access denied while trying to inspect low-CPU Python command lines. This did not block resume because no high-CPU training process or final metrics were present.

Next exact step:

- Monitor training:
  `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_epoch95_train_stdout.log`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-22 - Agent Handoff - M3 Training Saved and Stopped at Epoch 95

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/README.md`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train.pid)` - passed before stop; parent PowerShell PID `14020` was running.
- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed before stop; Python training PIDs included `6096` and `21260`.
- `Get-Content -Tail 20 runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train_stdout.log` - passed; showed active epoch `96/150`.
- `Get-Content -Tail 3 runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; latest completed row was epoch 95.
- Checkpoint copy to `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/` - passed; copied `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, and PID file.
- Ultralytics load verification for copied `last.pt` - passed; printed `loaded=True`, `class_count=136`, `task=detect`, `first_class=brace`, and `last_class=ottavaBracket`. Ultralytics also printed non-blocking AppData settings/cache permission warnings.
- Stop command for parent PID `14020` and Python PIDs `6096`, `21260` - passed; one remaining Python process disappeared before the follow-up escalated stop could act on it.
- Post-stop process check - passed; no Python training process remained.
- Final checkpoint refresh after stop - passed; refreshed copied checkpoint/log files.
- Hash generation for copied artifacts - passed after splitting the large checkpoint hash step from an earlier metadata script that timed out.
- Strict JSON validation for `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json` - passed.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe -m unittest discover tests` - passed after documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after documentation updates, checked 12 documentation files.
- Final Python process check after verification commands exited - passed; no Python process remained.

Generated artifacts:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/last.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/best.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/results.csv`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/args.yaml`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/resume_epoch74_train_stdout.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/resume_epoch74_train_stderr.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/resume_epoch74_train.pid`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/metadata.json`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch95_stop_2026-05-22/README.md`

What is complete:

- The resumed YOLOv8m run was saved without discarding completed progress.
- The clean recovery point is the epoch-95 `last.pt` checkpoint.
- The copied checkpoint is loadable through Ultralytics and preserves the 136-class detection head.
- Manual checkpoint metadata includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- Training was stopped after load verification, and no Python training process remains.
- Documentation now points the next agent to the epoch-95 stopped-checkpoint state, not a live process.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- Two attempts to write metadata and hash all artifacts in one PowerShell script timed out. Hashing was split out, passed, and the final metadata JSON validates.
- PID `14020` was later observed reused by a Chrome process after the training wrapper stopped. Stop verification therefore relies on no remaining Python training process and not on PID reuse alone.

Next exact step:

- Resume from the saved checkpoint when training should continue:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\yolo.exe detect train resume=True model=.\artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch95_stop_2026-05-22\last.pt`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-22 - Agent Handoff - M3 Training Resumed from Epoch 74

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed before resume; showed no active Python process.
- `Get-ChildItem artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch74_stop_2026-05-22` - passed; confirmed `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, PID file, README, and metadata existed.
- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed; returned `False`, confirming M3 was still incomplete before resume.
- `python -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch74_stop_2026-05-22\metadata.json` - passed; checkpoint metadata is strict JSON.
- Escalated hidden `Start-Process` resume launch - passed; resumed YOLO training from `artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch74_stop_2026-05-22\last.pt`.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train.pid` - passed; PID file contained `14020`.
- `Get-Content -Tail 100 runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train_stdout.log` - passed; showed the epoch-74 checkpoint path, YOLOv8m configuration, `nc=136`, `epochs=150`, `imgsz=1024`, `batch=4`, and `Resuming training ... from epoch 75 to 150 total epochs`.
- `Get-Content -Tail 40 runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train_stderr.log` - passed; log was empty during the resume check.
- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train.pid)` - passed; parent PowerShell PID `14020` was running.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe -m unittest discover tests` - passed after resume documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after resume documentation updates, checked 12 documentation files.
- Final live progress check - passed; PID `14020` was still running, stderr remained empty, and stdout showed epoch `75/150` around batch `186/307`.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/resume_epoch74_train_stderr.log`

What is complete:

- Training has resumed from the exact load-verified epoch-74 checkpoint.
- Ultralytics confirmed the resumed schedule is epoch 75 through 150.
- The resumed process is running as a hidden background process with PID `14020`.
- Resume logs and PID file are recorded under the existing full-run directory.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- Three parallel checkpoint file probes initially hit a Windows sandbox `CreateProcessWithLogonW failed: 1056` issue. Sequential reruns passed and did not block the resume.

Next exact step:

- Monitor training:
  `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_epoch74_train_stdout.log`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-22 - Agent Handoff - M3 Training Saved and Stopped at Epoch 74

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/README.md`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/metadata.json`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- Training progress check - passed; `resume_train_stdout.log` showed epoch `74/150` completing and epoch `75/150` starting while the save/stop work was being prepared.
- Checkpoint copy to `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/` - passed; copied `last.pt`, `best.pt`, `results.csv`, `args.yaml`, resume logs, and PID file.
- Ultralytics load verification for copied `last.pt` - passed; printed `loaded=True`, `class_count=136`, `task=detect`, `first_class=brace`, and `last_class=ottavaBracket`.
- Metadata generation for the epoch-74 checkpoint - passed after correcting a PowerShell `Add-Member` update issue.
- Stop command for parent PID `30204` and child PIDs `35140`, `36816` - passed after load verification.
- Post-stop process check - passed; no Python training process remained.
- Final checkpoint refresh after stop - passed; refreshed copied checkpoint/log files and rebuilt metadata with final hashes and stop verification.
- Strict JSON validation for `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/metadata.json` - passed.
- Checkpoint README correction and metadata README-hash refresh - passed; resume command now includes `$env:PYTHONPATH='src'`, and metadata records README SHA256 `539e110131972ecf8e1c364888e874c1151ed344e9cf087a2ced0cf5b8959567`.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe -m unittest discover tests` - passed after documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after documentation updates, checked 12 documentation files.
- First parallel post-verification process check showed only the verification Python interpreters because it ran concurrently with tests. A sequential rerun after verification exited passed and showed no Python process.

Generated artifacts:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/last.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/best.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/results.csv`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/args.yaml`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/resume_train_stdout.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/resume_train_stderr.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/resume_train.pid`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/metadata.json`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch74_stop_2026-05-22/README.md`

What is complete:

- The resumed YOLOv8m run was saved without discarding progress.
- The clean recovery point is the epoch-74 `last.pt` checkpoint.
- The copied checkpoint is loadable through Ultralytics and preserves the 136-class detection head.
- Manual checkpoint metadata includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- Training was stopped after load verification, and no Python training process remains.
- Documentation now points the next agent to the epoch-74 stopped-checkpoint state, not a live process.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- One metadata update attempt failed because PowerShell could not set a missing PSCustomObject property directly. The metadata write was rerun with `Add-Member -Force` and passed.

Next exact step:

- Resume from the saved checkpoint when training should continue:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\yolo.exe detect train resume=True model=.\artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch74_stop_2026-05-22\last.pt`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-21 - Agent Handoff - M3 Training Resumed

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed before resume; showed no active Python training process.
- `Get-ChildItem artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21` - passed; confirmed `last.pt`, `best.pt`, logs, `results.csv`, `args.yaml`, README, and metadata existed.
- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed; returned `False`, confirming M3 was still incomplete before resume.
- `Get-Content -Tail 3 runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; confirmed epoch 20 was still the last completed row before resume.
- Escalated hidden `Start-Process` resume launch - passed; resumed YOLO training from `artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\last.pt`.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\resume_train.pid` - passed; PID file contained `30204`.
- `Get-Content -Tail 100 runs\detection\detection_136class_yolov8m_v1\resume_train_stdout.log` - passed; showed `Resuming training ... from epoch 21 to 150 total epochs` and active epoch `21/150`.
- `Get-Content -Tail 40 runs\detection\detection_136class_yolov8m_v1\resume_train_stderr.log` - passed; log was empty during the resume check.
- `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits` - passed; showed about 16.1 GB of 16.4 GB GPU memory in use during resumed epoch 21.
- `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\resume_train.pid)` - passed after correcting an earlier PowerShell variable-name mistake; parent PowerShell PID `30204` was running.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed after resume documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after resume documentation updates, checked 12 documentation files.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\metadata.json` - passed after resume documentation updates.
- Final resume progress check - passed; stdout showed epoch `21/150` still active, around batch `207/307`, and the latest completed results row remained epoch 20.
- A final relative-path rerun of `..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` failed once because PowerShell did not resolve the venv path in that shell call; rerunning with absolute `C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\.venv\Scripts\python.exe` passed and checked 12 documentation files.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/resume_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/resume_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/resume_train_stderr.log`

What is complete:

- Training has resumed from the exact load-verified epoch-20 checkpoint.
- Ultralytics confirmed the resumed schedule is epoch 21 through 150.
- The resumed process is running as a hidden background process with PID `30204`.
- Resume logs and PID file are recorded under the existing full-run directory.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- One process-check command attempted to assign to PowerShell's read-only `$PID` variable and printed an error. The corrected command using `$resumePid` passed and confirmed the resumed parent process.

Next exact step:

- Monitor training:
  `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\resume_train_stdout.log`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-21 - Agent Handoff - M3 Training Saved and Stopped

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/README.md`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/metadata.json`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Test-Path runs\detection\detection_136class_yolov8m_v1\metrics.json` - passed; returned `False`, confirming no final project metric artifact exists.
- `Get-Content -Tail 5 runs\detection\detection_136class_yolov8m_v1\ultralytics\train\results.csv` - passed; confirmed epoch 20 was the latest completed row before stopping.
- `Copy-Item` into `artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\` - passed; copied checkpoint, results, args, and logs.
- Manual metadata generation - initially failed once because of PowerShell here-string syntax, then passed after rewriting with explicit output lines.
- Metadata JSON validation - initially failed once because the file had a UTF-8 BOM, then passed after rewriting without BOM.
- `Stop-Process -Id 28848 -Force` - passed; stopped the full training process after the recovery files were copied.
- `Get-CimInstance Win32_Process` child-process inspection - failed with access denied, but this did not block stopping the known training process.
- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed after stop; showed no Python training process.
- Ultralytics load check for the copied `last.pt` - passed; printed `loaded=True`, `class_count=136`, `task=detect`, `first_class=brace`, and `last_class=ottavaBracket`.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\metadata.json` - passed after the no-BOM rewrite.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed after documentation updates, 24 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed after documentation updates.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after documentation updates, checked 12 documentation files.
- Final `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed; showed no Python training process after verification commands exited.

Generated artifacts:

- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/last.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/best.pt`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/results.csv`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/args.yaml`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/full_train_stdout.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/full_train_stderr.log`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/metadata.json`
- `artifacts/manual_checkpoints/detection_136class_yolov8m_v1/epoch20_stop_2026-05-21/README.md`

What is complete:

- The full YOLOv8m run was paused without discarding progress.
- The clean recovery point is the epoch-20 `last.pt` checkpoint.
- The copied checkpoint is loadable through Ultralytics and preserves the 136-class detection head.
- Manual checkpoint metadata includes SHA256 hashes for copied checkpoint, CSV, args, and log files.
- Documentation now points the next agent to the paused-checkpoint state, not a live process.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist.
- `runs/detection/detection_136class_yolov8m_v1/analysis.json` does not exist.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist.
- ONNX export for the full YOLOv8m artifact has not been produced.
- M3 remains active, and `docs/AGENT_PROMPTS.md` must not advance to M4 yet.

What failed:

- PowerShell here-string metadata generation failed once before the metadata writer was corrected.
- The first strict JSON check failed because the metadata file had a UTF-8 BOM; it passed after rewriting without BOM.
- Child-process enumeration with `Get-CimInstance` failed with access denied, but `Stop-Process` on the known training PID succeeded and the post-stop Python process check was clean.

Next exact step:

- Resume from the saved checkpoint when training should continue:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\yolo.exe detect train resume=True model=.\artifacts\manual_checkpoints\detection_136class_yolov8m_v1\epoch20_stop_2026-05-21\last.pt`
- After final training completes, run or implement a V2 finalize/evaluate/export path to write `runs/detection/detection_136class_yolov8m_v1/metrics.json`, `analysis.json`, ONNX export, and `artifacts/models/detection_136class_yolov8m_v1/metadata.json`.

## 2026-05-21 - Agent Handoff - M3 Full YOLOv8m Run Launched

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`

Commands run:

- `Get-Process | Where-Object { $_.ProcessName -like '*python*' }` - passed; no Python training process was alive at pickup.
- `Get-ChildItem -Recurse -Force runs\detection\detection_136class_yolov8m_preflight_v1` - passed; the interrupted YOLOv8m preflight had only setup artifacts and batch preview images, not `results.csv`, weights, or metrics.
- `Get-ChildItem -Path .. -Recurse -Filter best.pt` - passed; found legacy checkpoints and V2 smoke checkpoints.
- `Get-Content C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\yolo_dataset\data.yaml` - passed; confirmed legacy parent detector dataset is `nc: 15`, so those checkpoints cannot satisfy M3.
- `Get-Content -Tail 5 ..\outputs\yolov8_extended\train\results.csv` - passed; confirmed legacy reduced-class training history exists but is not the 136-class M3 artifact.
- Escalated hidden launch with `Start-Process` - passed; started full YOLOv8m training outside the sandbox so it can continue after agent/tool interruptions.
- `Get-Content runs\detection\detection_136class_yolov8m_v1\full_train.pid` - passed; PID file contained `28848`.
- `Get-Process -Id 28848,23140` - passed; showed parent Python PID `28848` and child Python PID `23140`.
- `Get-Content -Tail 120 runs\detection\detection_136class_yolov8m_v1\full_train_stdout.log` - passed; stdout showed YOLOv8m training started with `nc=136`, 150 epochs, image size 1024, batch 4, and epoch `1/150`.
- `nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits` - passed; showed training using roughly 13.9 GB of the 16 GB GPU during the live check.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed during live M3 training, 24 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed during live M3 training.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed during live M3 training, checked 12 documentation files.
- Waited for the first epoch boundary - passed; `results.csv`, `weights/best.pt`, and `weights/last.pt` exist, and stdout showed training continuing in epoch `2/150`.

Generated artifacts:

- `runs/detection/detection_136class_yolov8m_v1/full_train.pid`
- `runs/detection/detection_136class_yolov8m_v1/full_train_stdout.log`
- `runs/detection/detection_136class_yolov8m_v1/full_train_stderr.log`
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/` in progress
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/results.csv`
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/best.pt`
- `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/last.pt`

What is complete:

- M3 full YOLOv8m training has been launched with the governing config values: `epochs=150`, `imgsz=1024`, `batch=4`, `workers=0`, `device=0`, `taxonomy_id=deepscores_136`.
- The training log confirms Ultralytics overrides the pretrained COCO head to `nc=136` and trains on `runs/data/deepscores_136_yolo_materialized/dataset.yaml`.
- The parent legacy checkpoints were checked and are not valid M3 completion artifacts because their dataset YAML is 15-class.
- The live full run has passed the first epoch boundary and has a checkpoint recovery point.

What is not complete:

- `runs/detection/detection_136class_yolov8m_v1/metrics.json` does not exist yet.
- `artifacts/models/detection_136class_yolov8m_v1/metadata.json` does not exist yet.
- No full-run ONNX export has completed yet.
- No API detector artifact wiring has been done.
- `docs/AGENT_PROMPTS.md` must remain on M3 until the full run completes and the artifact is accepted.

What failed:

- The earlier YOLOv8m preflight run was interrupted before training metrics or checkpoints were written. It left only setup artifacts under `runs/detection/detection_136class_yolov8m_preflight_v1/`.
- Earlier sandboxed detached launches did not survive reliably. The successful live launch used an escalated hidden `Start-Process`.

Next exact step:

- Monitor the live run first: `Get-Process -Id (Get-Content runs\detection\detection_136class_yolov8m_v1\full_train.pid)`.
- Then inspect progress: `Get-Content -Tail 80 runs\detection\detection_136class_yolov8m_v1\full_train_stdout.log`.
- If `runs/detection/detection_136class_yolov8m_v1/metrics.json` appears, run the M3 verification/doc update sequence.
- If the process exits without `metrics.json`, inspect `runs/detection/detection_136class_yolov8m_v1/full_train_stderr.log`, `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/results.csv`, and `runs/detection/detection_136class_yolov8m_v1/ultralytics/train/weights/last.pt` before deciding whether to resume or relaunch.

## 2026-05-20 - Agent Handoff - M3 Full Detector Smoke

Milestone worked:

- M3 - Full 136-Class Detector

Files changed:

- `configs/detection_136class_yolov8m.yaml`
- `docs/AGENT_PROMPTS.md`
- `docs/DATA_CARD.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/MILESTONE_HISTORY.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`
- `scripts/analyze_detection_136class_run.py`
- `scripts/run_detection_136class_yolo.py`
- `src/melodious_v2/evaluation/full_detector.py`
- `tests/test_full_detector_m3.py`

Commands run:

- `git switch -c phase-03-detector` - initially failed with sandbox permission denied, then passed with approval and created branch `phase-03-detector`.
- `$env:PYTHONPATH='src'; @' ... '@ | ..\.venv\Scripts\python.exe -` - passed; verified PyTorch, CUDA, Ultralytics, ONNX, ONNX Runtime, source image paths, and label counts.
- `nvidia-smi` - passed; detected NVIDIA GeForce RTX 3080 Laptop GPU with 16 GB VRAM.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed before M3 run, 23 tests; passed after analysis additions, 24 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --materialize-only` - passed; created `runs/data/deepscores_136_yolo_materialized/`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --smoke --epochs 1 --imgsz 640 --batch 2 --workers 0 --device 0` - passed; trained one-epoch full-taxonomy smoke model, validated on M1 validation split, exported ONNX.
- `Remove-Item -LiteralPath yolo11n.pt -Force` - passed; removed incidental Ultralytics AMP-check download from repo root.
- `..\.venv\Scripts\python.exe -m json.tool runs\detection\detection_136class_yolov8s_smoke_v1\metrics.json > $null` - passed; M3 metrics JSON is strict JSON.
- `..\.venv\Scripts\python.exe -m json.tool runs\detection\detection_136class_yolov8s_smoke_v1\manifest.json > $null` - passed.
- `..\.venv\Scripts\python.exe -m json.tool artifacts\models\detection_136class_yolov8s_smoke_v1\metadata.json > $null` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\analyze_detection_136class_run.py` - passed; generated M3 analysis artifacts.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed; experiment index now includes M2 and M3 smoke runs.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 12 documentation files.

Generated artifacts:

- `runs/data/deepscores_136_yolo_materialized/dataset.yaml`
- `runs/data/deepscores_136_yolo_materialized/manifest.json`
- `runs/data/deepscores_136_yolo_materialized/images/{train,val,test}/`
- `runs/data/deepscores_136_yolo_materialized/labels/{train,val,test}/`
- `runs/detection/detection_136class_yolov8s_smoke_v1/metrics.json`
- `runs/detection/detection_136class_yolov8s_smoke_v1/report.md`
- `runs/detection/detection_136class_yolov8s_smoke_v1/manifest.json`
- `runs/detection/detection_136class_yolov8s_smoke_v1/artifacts.json`
- `runs/detection/detection_136class_yolov8s_smoke_v1/config.yaml`
- `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.json`
- `runs/detection/detection_136class_yolov8s_smoke_v1/analysis.md`
- `runs/detection/detection_136class_yolov8s_smoke_v1/ultralytics/train/`
- `runs/detection/detection_136class_yolov8s_smoke_v1/ultralytics/val_val/`
- `artifacts/models/detection_136class_yolov8s_smoke_v1/best.pt`
- `artifacts/models/detection_136class_yolov8s_smoke_v1/best.onnx`
- `artifacts/models/detection_136class_yolov8s_smoke_v1/metadata.json`

What is complete:

- M1 prerequisite verified locally.
- M2 prerequisite verified locally.
- M3 environment preflight passed with CUDA, Ultralytics, ONNX, and ONNX Runtime available.
- M1 DeepScores labels/images were materialized into a YOLO-standard ignored dataset.
- A full 136-class YOLO training/evaluation/export pipeline now exists in code.
- A constrained one-epoch YOLOv8s full-taxonomy smoke run completed successfully.
- Checkpoint and ONNX artifacts were copied to `artifacts/models/detection_136class_yolov8s_smoke_v1/` with SHA256 metadata.
- Generated analysis records rare-class, small-symbol, zero-mAP, and confusion-matrix evidence.
- M1, M2, M3, and future milestones are now documented in detail in `docs/MILESTONE_HISTORY.md`.

What failed:

- Initial hardlink materialization was not permitted by the filesystem, so the materializer copied source images into ignored `runs/data/deepscores_136_yolo_materialized/`.
- The first `git switch -c phase-03-detector` attempt needed sandbox escalation. It succeeded after approval.

What is blocked:

- Full configured YOLOv8m 150-epoch training is not complete.
- The M3 smoke artifact is not wired into the API because it is smoke-quality and the non-bootstrap ONNX detector adapter has not been implemented.
- M4 should not start until the team either accepts an M3 detector artifact for integration or completes the full configured detector run.

Next exact step:

- Run the full configured detector command:
  `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_136class_yolo.py --run-id detection_136class_yolov8m_v1 --model yolov8m.pt --epochs 150 --imgsz 1024 --batch 4 --workers 0 --device 0`

## 2026-05-20 - Agent Handoff - M2 Metric Reproduction

Milestone worked:

- M2 - Metric Reproduction

Files changed:

- `configs/detection_15class_repro.yaml`
- `docs/AGENT_PROMPTS.md`
- `docs/ARCHITECTURE.md`
- `docs/DATA_CARD.md`
- `docs/EXPERIMENTS.md`
- `docs/HANDOFF.md`
- `docs/ROADMAP.md`
- `docs/RUBRIC_MAP.md`
- `docs/STATUS.md`
- `MODEL_CARD.md`
- `README.md`
- `scripts/run_detection_15class_repro.py`
- `src/melodious_v2/evaluation/__init__.py`
- `src/melodious_v2/evaluation/reduced_detection.py`
- `src/melodious_v2/metrics/detection.py`
- `src/melodious_v2/reports.py`
- `tests/test_detection_metrics.py`
- `tests/test_detection_repro.py`
- `tests/test_export_and_reports.py`

Commands run:

- `git switch -c phase/02-metrics` - failed because Git could not create `refs/heads/phase/02-metrics`; the ref layout blocks that slash name.
- `git switch -c phase-02-metrics` - initially failed with sandbox permission denied, then passed with approval and created branch `phase-02-metrics`.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 21 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\run_detection_15class_repro.py` - passed; generated the M2 run from five legacy sample prediction payloads and matching DeepScores annotations.
- `..\.venv\Scripts\python.exe -m json.tool runs\detection\detection_15class_repro_sample_v1\metrics.json > $null` - passed; `metrics.json` is strict JSON.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\generate_experiment_index.py --runs-dir runs --output docs\EXPERIMENTS.md` - passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked 11 documentation files.

Generated artifacts:

- `runs/detection/detection_15class_repro_sample_v1/metrics.json`
- `runs/detection/detection_15class_repro_sample_v1/report.md`
- `runs/detection/detection_15class_repro_sample_v1/manifest.json`
- `runs/detection/detection_15class_repro_sample_v1/artifacts.json`
- `runs/detection/detection_15class_repro_sample_v1/config.yaml`

What is complete:

- M2 reduced-class reproduction uses real legacy sample YOLOv8s payloads from `../sample_detections/model_outputs_quick/`.
- Matching DeepScores targets are derived from `../dataset_ds2_dense/deepscores_train.json` and `../dataset_ds2_dense/deepscores_test.json`.
- The run uses `deepscores_15_reduced` taxonomy and preserves checkpoint SHA256 provenance for `../outputs/yolov8_runs/train/weights/best.pt`.
- `docs/EXPERIMENTS.md` is generated from `runs/**/metrics.json`.
- `docs/AGENT_PROMPTS.md` now points the next agent to M3.

What failed:

- The requested `phase/02-metrics` branch name could not be created because of local Git ref layout.
- The first `phase-02-metrics` branch creation attempt needed sandbox escalation. It succeeded after approval.

What is blocked:

- Nothing for M2.
- M3 has not started. Full 136-class detector training still needs local training dependency/hardware verification.

Next exact step:

- Start M3 by verifying the DeepScores 136-class YOLO manifest and local YOLO/Ultralytics runtime, then train/evaluate through `configs/detection_136class_yolov8m.yaml` with metrics written to `runs/detection/{run_id}/metrics.json`.

## 2026-05-12 - Agent Handoff - M1 Reverification

Milestone worked:

- M1 - Dataset Manifests verification pass

Files changed:

- `docs/STATUS.md`
- `docs/HANDOFF.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe - <<'PY' ...` - failed before Python execution because PowerShell does not support Bash heredoc redirection.
- `$env:PYTHONPATH='src'; @' ... '@ | ..\.venv\Scripts\python.exe -` - passed; confirmed DeepScores top-level and split `class_count = 136`, DeepScores duplicate id/filename checks passed with work-group warning, and MUSCIMA page-id leakage passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 19 tests; rerun after documentation updates and still passed.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed after documentation updates, checked 11 documentation files.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\build_dataset_manifests.py` - passed, regenerated DeepScores and MUSCIMA manifest runs from local parent datasets.

Generated artifacts:

- Refreshed ignored artifacts under `runs/data/deepscores_136_manifest/`.
- Refreshed ignored artifacts under `runs/data/muscima_graph_manifest/`.

What is complete:

- M1 remains complete.
- `runs/data/deepscores_136_manifest/manifest.json` and `leakage_report.json` exist.
- Every DeepScores split summary reports `class_count = 136`.
- DeepScores duplicate image-id and duplicate filename leakage checks passed.
- DeepScores inferred work-group leakage remains `warning` with 202 repeated filename-inferred groups.
- `runs/data/muscima_graph_manifest/manifest.json` exists.
- MUSCIMA train/val/holdout split leakage check passed with no duplicate page ids.

What failed:

- A non-blocking artifact-summary probe used Bash heredoc syntax in PowerShell and failed before Python ran. The equivalent PowerShell-compatible command passed.

What is blocked:

- None for M1.
- M2 has not started; no reduced-class V2 metric reproduction run exists yet.

Next exact step:

- Update `docs/AGENT_PROMPTS.md` to an M2 prompt, then start M2 by creating a reduced-class metric reproduction run that writes `runs/**/metrics.json` with required provenance.

## 2026-05-12 - Agent Handoff

Milestone worked:

- M1 - Dataset Manifests

Files changed:

- `src/melodious_v2/datasets/manifests.py`
- `scripts/build_dataset_manifests.py`
- `tests/test_dataset_manifests.py`
- `configs/detection_136class_yolov8m.yaml`
- `docs/DATA_CARD.md`
- `docs/STATUS.md`
- `docs/ROADMAP.md`
- `docs/HANDOFF.md`

Commands run:

- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe -m unittest discover tests` - passed, 19 tests.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\build_dataset_manifests.py` - passed, generated DeepScores and MUSCIMA manifest runs.
- `$env:PYTHONPATH='src'; ..\.venv\Scripts\python.exe scripts\validate_metric_claims.py` - passed, checked documentation files.

Generated artifacts:

- `runs/data/deepscores_136_manifest/manifest.json`
- `runs/data/deepscores_136_manifest/train.json`
- `runs/data/deepscores_136_manifest/val.json`
- `runs/data/deepscores_136_manifest/test.json`
- `runs/data/deepscores_136_manifest/class_counts.json`
- `runs/data/deepscores_136_manifest/leakage_report.json`
- `runs/data/deepscores_136_manifest/yolo_dataset.yaml`
- `runs/data/deepscores_136_manifest/generated/labels/{train,val,test}/`
- `runs/data/deepscores_136_manifest/generated/image_lists/{train,val,test}.txt`
- `runs/data/muscima_graph_manifest/manifest.json`
- `runs/data/muscima_graph_manifest/train.json`
- `runs/data/muscima_graph_manifest/val.json`
- `runs/data/muscima_graph_manifest/holdout.json`
- `runs/data/muscima_graph_manifest/leakage_report.json`
- `runs/data/muscima_graph_manifest/class_summary.json`

What is complete:

- DeepScores source train/test separation is preserved.
- DeepScores source train split is deterministically split into 1226 train and 136 validation images with seed `42`.
- DeepScores test split has 352 images from the source test JSON.
- Every DeepScores split summary reports `class_count = 136`.
- YOLO labels were generated for all DeepScores splits under ignored `runs/`.
- MUSCIMA XML pages were split into 112 train, 14 validation, and 14 holdout pages with seed `42`.
- MUSCIMA class parsing produced `class_summary.json`.
- Tests cover deterministic splitting, DeepScores class-count summaries, duplicate DeepScores id leakage, and MUSCIMA page-id separation.

What is blocked:

- None for M1.
- DeepScores leakage status is `warning`, not failed, because filename-inferred work groups repeat across splits. Duplicate image ids and duplicate filenames both passed.

Next exact step:

- Begin M2 by creating a reduced-class metric reproduction run that writes `runs/**/metrics.json`, then regenerate `docs/EXPERIMENTS.md` from that artifact.

## Handoff Entry Template

When an agent finishes work, append a new section using this shape:

```markdown
## YYYY-MM-DD - Agent Handoff

Milestone worked:

- Mx - Name

Files changed:

- path

Commands run:

- command - result

Generated artifacts:

- path or none

What is complete:

- item

What is blocked:

- item or none

Next exact step:

- command or implementation task
```
