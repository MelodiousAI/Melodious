
## `PROJECT_CONTEXT.md`

```md
# Project Context

## Project
Melodious is an optical music recognition (OMR) project.
The system takes a photo of sheet music, detects music symbols, builds a graph representation of the notation, and later exports structured results such as MusicXML and MIDI.

## Team split
My partner is mainly handling the YOLO / detection side.
I am mainly handling the data-preparation and graph side.

## My responsibilities
My tasks are:
1. Parse the MUSCIMA++ dataset
2. Extract music symbols as nodes
3. Extract symbol relationships as edges
4. Detect staff regions from score images
5. Build graph objects for GNN input
6. Later align YOLO detections to MUSCIMA++ ground truth

## Current focus
Ignore all timelines and deadlines.
Do not focus on deployment, UI, or final polishing.
Do not focus on advanced GNN theory right now.

The parsing step has already been completed.

Right now the only goal is:
- work in `src/graph_builder.py`
- implement `detect_staff_lines(image_path)`
- test it on one MUSCIMA++ image
- return staff regions as `(y_min, y_max)` tuples
- keep the implementation simple and beginner-friendly

## Dataset
We are using MUSCIMA++ v2.0.
Important folders include:
- `cropobject_lists/`
- `images/`

## Beginner note
Assume I am a beginner in this field.
When suggesting code:
- keep it simple
- explain clearly
- avoid overengineering
- prefer small steps
- test one thing at a time

## Desired immediate milestone
Current milestone:
- load one MUSCIMA++ image
- detect horizontal staff lines
- group nearby detections
- return staff regions in a simple format
- print the result for one test image

## What not to focus on yet
- do not start `build_graph()` yet
- do not start GNN code yet
- do not start alignment code yet
- do not add extra features unrelated to staff detection

## Repo structure
- `src/` for source code
- `data/raw/` for raw dataset
- `data/processed/` for processed outputs
- `tests/` for test files
- `outputs/` for generated/debug outputs