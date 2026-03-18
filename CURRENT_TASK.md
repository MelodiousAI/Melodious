# Current Task

## File to work on
`src/graph_builder.py`

## Goal
Implement a beginner-friendly function called `detect_staff_lines(image_path)`.

## Purpose
This function should take the path to a sheet music image and return the detected staff regions in the image.

A staff region should be represented as:
- `(y_min, y_max)`

This will later help determine which music symbols belong to which staff.

## Scope for this task only
For now, only focus on staff-line detection.
Do not move on to graph construction, GNN code, or alignment yet.

## What the function should do
1. Load one sheet music image from a file path.
2. Convert it to grayscale.
3. Apply light blur if needed.
4. Detect horizontal lines that likely belong to musical staves.
5. Group nearby horizontal line detections together.
6. Convert those grouped lines into staff regions.
7. Return a list of staff regions as `(y_min, y_max)` tuples.

## Expected output
Example of expected return format:

```python
[(45, 95), (140, 190), (240, 290)]