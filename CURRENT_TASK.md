# Current Task

## File to work on
`src/parse_muscima.py`

## Goal
Write a beginner-friendly parser for MUSCIMA++.

## Step 1
Load one XML file using the MUSCIMA / mung tools.

## Step 2
Print:
- number of nodes in the file
- first 3 nodes
- for each sample node, print:
  - node ID
  - class name
  - bounding box values
  - outlinks

## Step 3
Convert one file into:
- a list of node dictionaries
- a list of edge dictionaries

## Step 4
Later expand the script to loop over all XML files and save:
- `muscima_nodes.json`
- `muscima_edges.json`

## Constraints
- keep code simple
- add comments
- explain any library-specific function used
- avoid building the full graph pipeline yet
- do not jump to GNN code yet