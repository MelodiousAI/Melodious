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
4. Later help detect staff regions from score images
5. Later build graph objects for GNN input
6. Later align YOLO detections to MUSCIMA++ ground truth

## Current focus
Ignore all timelines and deadlines.
Do not focus on deployment, UI, or final polishing.
Do not focus on advanced GNN theory right now.

Right now the only goal is:
- start with `src/parse_muscima.py`
- successfully read one MUSCIMA++ XML annotation file
- inspect a few nodes
- then convert one file into node/edge dictionaries
- then later scale to all files

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
First milestone:
- load one XML file from MUSCIMA++
- print how many nodes it contains
- print the first 3 nodes with useful fields such as ID, class name, bounding box, and outlinks

## Repo structure
- `src/` for source code
- `data/raw/` for raw dataset
- `data/processed/` for processed outputs
- `tests/` for test files
- `outputs/` for generated/debug outputs