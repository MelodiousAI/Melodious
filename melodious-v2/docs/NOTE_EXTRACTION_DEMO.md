# Note Extraction Demo Path

This document records the local demo path for testing note extraction from a
clean uploaded sheet image while the official upload API still uses
`heuristic_bootstrap`.

## Scope

The script `scripts/extract_notes_from_image.py` is a demo extractor, not a
metric run. It is meant to answer: "Can I upload a clean sheet image and get
actual extracted note events plus a playable MIDI artifact right now?"

## Default Checkpoint

When `--checkpoint` is omitted, the CLI now looks first for the saved local
full-page demo checkpoint:

`artifacts/models/note_extraction_default_fullpage/best.pt`

That generated artifact is copied from:

`runs/detection/detection_136class_yolov8m_finetune_img1472_maxdet2000_v1/ultralytics/train/weights/best.pt`

The stable artifact copy is intentionally ignored by git, like every model
checkpoint. Its local metadata is stored at
`artifacts/models/note_extraction_default_fullpage/metadata.json`. If the saved
artifact is missing, the CLI falls back to the source run checkpoint above, and
then to the original M3 full-detector artifact.

The detector metric docs remain tied to their own `runs/**/metrics.json` files.
This demo checkpoint selection is a local transcription/demo choice, not a new
metric result.

It does the following:

1. Detects five-line staff systems from long horizontal staff strokes, using
   dark-line, light-line, and adaptive masks so faded/antialiased staff lines
   are not silently dropped.
2. Uses a YOLO checkpoint, when available, to detect notehead, stem, beam,
   flag, augmentation-dot, key-signature, and explicit-accidental boxes.
3. Snapshots the checkpoint into the output directory before inference so a
   live training process can continue writing `best.pt` or `last.pt`.
4. Maps notehead vertical position to treble-clef pitch.
5. Applies detected `keyFlat`, `keySharp`, and `keyNatural` symbols to matching
   note steps on the same staff; detected explicit accidentals override the key
   signature for the attached note.
6. Infers simple rhythm:
   - black noteheads default to quarter notes;
   - nearby stems confirm unbeamed black noteheads as quarter notes;
   - nearby beams or flags shorten black noteheads to eighth/smaller values;
   - nearby detector-confirmed augmentation dots multiply the duration by 1.5;
   - half/whole notehead classes set longer base durations.
7. Writes:
   - `*_notes.json` with note order, staff index, bounding box, pitch, MIDI
     pitch, confidence, duration, dotted flag, and rhythm source.
   - `*_notes_overlay.png` with staff lines and note labels.
   - `*_notes.musicxml` with compact extracted notes.
   - `*_notes.mid` with real MIDI note events.

## Limitations

- This is not the FastAPI upload route.
- This is not an official detector metric or test-set result.
- Rhythm is heuristic. Stems, beams, flags, and augmentation dots adjust
  duration when detected near the notehead. If a black notehead has no detected
  stem, beam, or flag, the extractor marks it as
  `black_notehead_quarter_rule_no_stem` instead of pretending the detector found
  a complete duration label.
- YOLO-backed extraction now leaves the old CV augmentation-dot fallback off by
  default. This prevents tiny specks, staff artifacts, or non-dot marks from
  being silently converted into dotted rhythms. Detector-confirmed
  `augmentationDot` boxes still count. Use `--use-cv-dot-fallback` only for
  deliberate experiments where false dotted notes are acceptable.
- Pitch assumes treble clef. Basic detected key signatures and explicit
  accidentals are applied when YOLO returns `keyFlat`, `keySharp`,
  `keyNatural`, or `accidental*` boxes.
- It does not yet reconstruct ties, slurs, voices, measures, measure-scoped
  accidental persistence/cancellation, or expression markings. Beam detections
  are currently used only for duration, not for full notational grouping.
- The current script is best suited for clean treble-clef pages. It can now
  handle dense multi-system pages when staff lines are visible, but rhythm
  remains the weakest part of the demo.

## Command

Run from `melodious-v2`:

```powershell
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py `
  --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png `
  --output-dir runs\demo\sad_romance_note_extraction_v3 `
  --device cpu `
  --conf 0.12 `
  --imgsz 1472 `
  --max-det 2000 `
  --default-quarter-length 1.0 `
  --title "Sad Romance"
```

Use `--device cpu` while fine-tuning is running so the GPU remains dedicated to
training. Add `--use-cv-dot-fallback` only if you explicitly want contour-based
augmentation-dot guesses in addition to YOLO detections.

Because the saved full-page demo checkpoint is the default, the command above
does not need an explicit `--checkpoint` argument unless you want to compare
another checkpoint.

## Interpreting Output

- `extractor_mode = yolo_notehead_staff_pitch` means the YOLO checkpoint was
  used for notehead boxes and the staff geometry layer estimated pitches.
- `extractor_mode = cv_staff_notehead_pitch` means the checkpoint was missing
  or YOLO failed, so the contour fallback was used.
- `note_count` is the number of note events written to MIDI.
- `quarter_length` is the extracted duration in quarter-note units:
  `1.0` is quarter, `0.5` is eighth, `1.5` is dotted quarter, and
  `0.75` is dotted eighth.
- `rhythm_source` explains why that duration was chosen, for example
  `stem_quarter`, `black_notehead_quarter_rule_no_stem`, `beam_x1`, `flag`, or
  `black_notehead_quarter_rule_no_stem+augmentation_dot`.
- `stem_detected` records whether a nearby detected `stem` box was attached to
  the notehead.
- `key_signatures` records detected per-staff key signature maps, for example
  `{"B": -1}` for one detected B-flat key signature.
- `key_fifths` is the MusicXML fifths value inferred from the detected key
  signatures, for example `-1` for one flat.
- `alter` records the semitone pitch alteration applied to one note. `-1` is a
  flat and `1` is a sharp.
- `pitch_source` explains whether a pitch came from raw staff geometry,
  detected key signature, or detected explicit accidental.
- The MIDI file is playable and contains real note-on/note-off events, unlike
  the older API placeholder MIDI which was only a 26-byte empty MIDI container.

## Sad Romance Verification

Latest default-checkpoint output:

- Output directory: `runs/demo/sad_romance_default_fullpage_20260605/`.
- Checkpoint: `artifacts/models/note_extraction_default_fullpage/best.pt` when
  the stable copy exists, otherwise the source 1472 full-page fine-tune path.
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Note events: `197`.
- Stem-confirmed notes: `0`.
- Dotted notes: `3`.
- Duration distribution: `0.25:1`, `0.5:82`, `0.75:1`, `1.0:78`,
  `1.5:2`, `2.0:28`, `4.0:5`.
- MusicXML path:
  `runs/demo/sad_romance_default_fullpage_20260605/sad_romance_clearer_smooth_notes.musicxml`.
- MusicXML parse check passed with `197` notes and `3` `<dot/>` tags.

Earlier saved comparison output:

- Output directory: `runs/demo/sad_romance_note_extraction_v3/`.
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Note events: `197`.
- Stem-confirmed notes: `0`.
- Dotted notes: `17`.
- MusicXML parse check passed with `197` notes and `17` `<dot/>` tags.

The `0` stem-confirmed note count is important. The DeepScores detector head
has a `stem` class, but the default Sad Romance checkpoint inference did not
return usable stem boxes at the selected threshold. Quarter notes are therefore
inferred from black noteheads that have no nearby beam/flag, which is a notation
rule fallback rather than direct stem evidence.

## Uploaded Arabic Page Verification

User image:
`C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png`.

Command:

```powershell
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py `
  --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image.png `
  --output-dir runs\demo\image_note_extraction_v6 `
  --device cpu `
  --conf 0.12 `
  --imgsz 1472 `
  --max-det 2000 `
  --title "Tislam Alaina Alhawa"
```

Latest verified output:

- Output directory: `runs/demo/image_note_extraction_v6/`.
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Note events: `319`.
- Stem-confirmed notes: `0`.
- Dotted notes: `7`.
- Key signatures: each of the 9 staff systems has detected `{"B": -1}`.
- MusicXML key fifths: `-1`.
- B-flat notes from detected key signature: `53`.
- Duration distribution: `0.25:36`, `0.5:192`, `1.0:74`, `1.5:6`,
  `2.0:10`, `3.0:1`.
- Pitch sources: `staff_geometry:264`, `key_signature:flat:53`,
  `explicit_accidental:accidentalSharp:2`.
- Warning: `CV augmentation-dot fallback disabled; only detector-confirmed augmentationDot symbols were used.`
- MIDI path: `runs/demo/image_note_extraction_v6/image_notes.mid`.
- MIDI size: `2871` bytes.
- MusicXML path: `runs/demo/image_note_extraction_v6/image_notes.musicxml`.
- Overlay path: `runs/demo/image_note_extraction_v6/image_notes_overlay.png`.
- MusicXML parse check passed with `319` notes, `7` `<dot/>` tags,
  one `<fifths>-1</fifths>` key signature, and `53` `<alter>-1</alter>` tags.

Important history: the first run on this image only detected `4` staff systems
and should not be used as demo evidence. The corrected `v3` run detected all
`9` visible staff systems by preserving lighter staff lines before note-to-pitch
mapping. The later `v5` run adds detected key-signature application. This is not
hard-coded to the page: YOLO emits `keyFlat`, the extractor maps each key-flat
glyph to `B` by staff geometry, and then applies `B: -1` to matching notes.
The `v6` run keeps the same note count and key-signature behavior but disables
CV dot guessing, reducing dotted notes from `38` to `7`. Any remaining false
dots must now be handled by detector calibration/training or stricter
`augmentationDot` post-processing.

## Fur Elise Verification

User image:
`C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image(305).png`.

Command:

```powershell
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py `
  --image "C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\image(305).png" `
  --output-dir runs\demo\fur_elise_default_fullpage_stafffix_20260605 `
  --device cpu `
  --conf 0.12 `
  --imgsz 1472 `
  --max-det 2000 `
  --default-quarter-length 1.0 `
  --title "Fur Elise"
```

Latest verified output:

- Output directory: `runs/demo/fur_elise_default_fullpage_stafffix_20260605/`.
- Checkpoint: `artifacts/models/note_extraction_default_fullpage/best.pt`.
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Note events: `256`.
- Stem-confirmed notes: `0`.
- Dotted notes: `3`.
- Explicit accidentals written as MusicXML `<alter>` tags: `36`.
- Duration distribution: `0.125:62`, `0.25:130`, `0.375:1`,
  `0.5:51`, `0.75:2`, `1.0:10`.
- MusicXML path:
  `runs/demo/fur_elise_default_fullpage_stafffix_20260605/image(305)_notes.musicxml`.
- MIDI path:
  `runs/demo/fur_elise_default_fullpage_stafffix_20260605/image(305)_notes.mid`.
- Overlay path:
  `runs/demo/fur_elise_default_fullpage_stafffix_20260605/image(305)_notes_overlay.png`.
- Warning: `CV augmentation-dot fallback disabled; only detector-confirmed augmentationDot symbols were used.`

Important history: the first Fur Elise run detected only `8` staff systems and
missed the dense system around measure `33`. The staff detector was adjusted to
allow compact low-resolution staff spacing down to `5 px`, and duplicate
candidate merging now prefers the wider five-line group when overlapping
candidates have comparable horizontal span. The corrected run detects all `9`
visible systems.

### Fur Elise GNN Relationship Trial

A follow-up trial ran the corrected Fur Elise detector output through the legacy
MUSCIMA GNN relationship runtime:

- Output directory: `runs/demo/fur_elise_gnn_relationship_trial_20260605/`.
- MusicXML path:
  `runs/demo/fur_elise_gnn_relationship_trial_20260605/image(305)_notes.musicxml`.
- MIDI path:
  `runs/demo/fur_elise_gnn_relationship_trial_20260605/image(305)_notes.mid`.
- Relationship summary:
  `runs/demo/fur_elise_gnn_relationship_trial_20260605/relationships.json`.
- Trial summary:
  `runs/demo/fur_elise_gnn_relationship_trial_20260605/gnn_trial_summary.json`.
- Assembly metadata: `applied_mode = gnn`, `inference_ran = true`,
  `fallback_applied = false`, `checkpoint_ready = true`.
- Relationship counts: `641` `stem_notehead`, `54` `beam_notegroup`, total
  `695`.
- Note-extraction counts remained `9` staff systems, `256` note events,
  `0` stem-confirmed notes, `3` dotted notes, and `36` MusicXML `<alter>` tags.

This trial did not improve the exported Fur Elise MusicXML. The GNN-trial
MusicXML is byte-identical to the staff-fixed MusicXML, with SHA256
`E97ECC091AAB109B7FC2C58C1D17DB661F5E93F0480C542489C0F2866EFCC126`. The reason
is architectural: `scripts/extract_notes_from_image.py` currently writes
MusicXML from detected note events and simple rhythm rules, while the graph
relationships are saved as evidence but are not yet consumed to rewrite
durations, voices, beams, or measures. Also, this Fur Elise detector payload has
no actual `stem` class detections, so GNN relationships alone cannot prove that
stem detection has been solved on full-page uploaded images.

## Next Engineering Step

The next product step is to wire this path into the upload API behind an
explicit mode, for example `MELODIOUS_UPLOAD_DETECTOR=yolo_note_demo`, and keep
the response warnings honest until measures, ties, and graph assembly are more
complete. The next rhythm-quality step is to either add a full-page tiled
inference merger so thin-symbol detections such as stems become available, or
add a tested rhythm-integration layer that consumes detector/GNN beam, flag,
dot, and stem evidence before MusicXML export.
