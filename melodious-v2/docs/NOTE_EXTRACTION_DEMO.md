# Note Extraction Demo Path

This document records the local demo path for testing note extraction from a
clean uploaded sheet image while the official upload API still uses
`heuristic_bootstrap`.

## Scope

The script `scripts/extract_notes_from_image.py` is a demo extractor, not a
metric run. It is meant to answer: "Can I upload a clean sheet image and get
actual extracted note events plus a playable MIDI artifact right now?"

It does the following:

1. Detects five-line staff systems from long horizontal staff strokes.
2. Uses a YOLO checkpoint, when available, to detect notehead, beam, flag, and
   augmentation-dot boxes.
3. Snapshots the checkpoint into the output directory before inference so a
   live training process can continue writing `best.pt` or `last.pt`.
4. Maps notehead vertical position to treble-clef pitch.
5. Infers simple rhythm:
   - black noteheads default to quarter notes;
   - nearby beams or flags shorten black noteheads to eighth/smaller values;
   - nearby augmentation dots multiply the duration by 1.5;
   - half/whole notehead classes set longer base durations.
6. Writes:
   - `*_notes.json` with note order, staff index, bounding box, pitch, MIDI
     pitch, confidence, duration, dotted flag, and rhythm source.
   - `*_notes_overlay.png` with staff lines and note labels.
   - `*_notes.musicxml` with compact extracted notes.
   - `*_notes.mid` with real MIDI note events.

## Limitations

- This is not the FastAPI upload route.
- This is not an official detector metric or test-set result.
- Rhythm is heuristic. Black noteheads default to quarter notes; beams, flags,
  and augmentation dots adjust duration when detected near the notehead.
- Pitch assumes treble clef and no key signature or accidental reconstruction.
- It does not yet reconstruct ties, slurs, voices, measures, accidentals, or
  expression markings. Beam detections are currently used only for duration,
  not for full notational grouping.
- The current script is best suited for clean single-staff examples like simple
  violin/piano treble pages.

## Command

Run from `melodious-v2`:

```powershell
$env:PYTHONPATH='src'
..\.venv\Scripts\python.exe scripts\extract_notes_from_image.py `
  --image C:\Users\ahmad\OneDrive\Desktop\Melodious_Initial_Code\sad_romance_clearer_smooth.png `
  --output-dir runs\demo\sad_romance_note_extraction_v2 `
  --device cpu `
  --conf 0.12 `
  --imgsz 1472 `
  --max-det 2000 `
  --default-quarter-length 1.0 `
  --title "Sad Romance"
```

Use `--device cpu` while fine-tuning is running so the GPU remains dedicated to
training.

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
  `default_quarter`, `beam_x1`, `flag`, or `default_quarter+augmentation_dot`.
- The MIDI file is playable and contains real note-on/note-off events, unlike
  the older API placeholder MIDI which was only a 26-byte empty MIDI container.

## Sad Romance Verification

Latest verified output:

- Output directory: `runs/demo/sad_romance_note_extraction_v2/`.
- Extractor mode: `yolo_notehead_staff_pitch`.
- Staff systems: `9`.
- Note events: `197`.
- Dotted notes: `17`.
- Duration distribution: `0.25:1`, `0.5:80`, `0.75:7`, `1.0:71`,
  `1.5:8`, `2.0:23`, `3.0:2`, `4.0:5`.
- Rhythm sources: `default_quarter:71`, `beam_x1:68`,
  `notehead_class:28`, `flag:13`, `default_quarter+augmentation_dot:8`,
  `beam_x1+augmentation_dot:4`, `flag+augmentation_dot:3`,
  `notehead_class+augmentation_dot:2`.
- MusicXML parse check passed with `197` notes and `17` `<dot/>` tags.

## Next Engineering Step

The next step is to wire this path into the upload API behind an explicit mode,
for example `MELODIOUS_UPLOAD_DETECTOR=yolo_note_demo`, and keep the response
warnings honest until accidentals, measures, ties, and graph assembly are more
complete.
