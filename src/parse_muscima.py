"""Parse MUSCIMA++ XML annotations into simple node and edge JSON files.

This file is the dataset-parsing stage of the project.
Its job is to turn MUSCIMA++ XML annotation files into plain Python-friendly
JSON outputs that later code can load without needing to work directly with XML
or `mung` Node objects.
"""

from pathlib import Path
import json
import sys

try:
    # `read_nodes_from_file` is the main MUSCIMA++ loader from the `mung` library.
    # It reads one XML annotation file and returns a Python list of `Node` objects.
    from mung.io import read_nodes_from_file
except ImportError:
    print("Could not import 'mung'.")
    print("Activate the project virtual environment, or install the requirements first.")
    print(r"Example: .\.venv\Scripts\python.exe src\parse_muscima.py")
    sys.exit(1)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# This is the folder that contains all MUSCIMA++ annotation XML files.
ANNOTATIONS_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "MUSCIMA-pp_raw-data-v2.0"
    / "data"
    / "annotations"
)

# Save processed outputs in `data/processed` so later scripts can reuse them.
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
NODES_JSON_PATH = OUTPUT_DIR / "muscima_nodes.json"
EDGES_JSON_PATH = OUTPUT_DIR / "muscima_edges.json"


def main():
    """Parse all MUSCIMA++ XML files and export simple node/edge JSON files.

    The script does two things in one run:
    1. inspect one sample XML file so the user can understand the data shape
    2. process all XML files into simple node and edge dictionaries
    """
    # Fail early if the annotations folder is missing.
    # It is much easier to debug a wrong path here than later in the loop.
    if not ANNOTATIONS_DIR.exists():
        print(f"Annotations folder not found: {ANNOTATIONS_DIR}")
        sys.exit(1)

    # `glob("*.xml")` finds all XML annotation files in the folder.
    xml_files = sorted(ANNOTATIONS_DIR.glob("*.xml"))

    if not xml_files:
        print(f"No XML files found in: {ANNOTATIONS_DIR}")
        sys.exit(1)

    print(f"Found {len(xml_files)} XML files.")
    print()

    # Load one file first so the data is still easy to inspect by eye.
    # This is useful for learning what a MUSCIMA `Node` contains before moving
    # to the full-dataset conversion step.
    sample_xml_file = xml_files[0]
    sample_nodes = read_nodes_from_file(str(sample_xml_file))

    if sample_nodes is None:
        print(f"Could not load sample XML file: {sample_xml_file}")
        sys.exit(1)

    print(f"Sample XML file: {sample_xml_file.name}")
    print(f"Number of nodes in sample file: {len(sample_nodes)}")
    print()
    print("First 3 nodes from the sample file:")

    # Print the first 3 nodes from one file so the user can inspect:
    # - the MUSCIMA node ID
    # - the symbol class name
    # - the bounding box
    # - the outgoing links to other symbols
    for index, node in enumerate(sample_nodes[:3], start=1):
        # `node.id` is the node ID inside one MUSCIMA++ document.
        # `node.class_name` is the symbol label.
        # `node.bounding_box` is a `mung` property that returns:
        # (top, left, bottom, right)
        # `node.outlinks` is the list of node IDs this node points to.
        print(f"Node {index}")
        print(f"  ID: {node.id}")
        print(f"  Class name: {node.class_name}")
        print(f"  Bounding box (top, left, bottom, right): {node.bounding_box}")
        print(f"  Outlinks: {node.outlinks}")
        print()

    # Build a quick lookup table so outlink IDs can be turned into readable
    # target class names. This makes the XML relationships easier to understand.
    sample_nodes_by_id = {}
    for node in sample_nodes:
        sample_nodes_by_id[node.id] = node

    # Use the first sample node as a simple relationship example.
    sample_node = sample_nodes[0]

    print("Target class names for the first sample node:")
    print(f"Source node ID: {sample_node.id}")
    print(f"Source class name: {sample_node.class_name}")

    # For each outlink, look up the target node and print its class name.
    # This shows that XML links are not just IDs; they represent symbol-to-symbol
    # relationships such as notehead-to-stem or notehead-to-staff.
    for target_node_id in sample_node.outlinks:
        target_node = sample_nodes_by_id.get(target_node_id)

        if target_node is None:
            print(f"  {target_node_id} -> target node not found")
        else:
            print(f"  {target_node_id} -> {target_node.class_name}")

    print()

    # These lists will collect data from every XML file in a JSON-friendly form.
    all_node_dicts = []
    all_edge_dicts = []

    print("Processing all XML files...")

    # Loop through every MUSCIMA++ XML file and convert library objects into
    # plain dictionaries. This keeps later code simple because it no longer has
    # to depend on XML parsing or `mung` internals.
    for xml_file in xml_files:
        nodes = read_nodes_from_file(str(xml_file))

        if nodes is None:
            print(f"Skipping unreadable file: {xml_file}")
            continue

        # Each XML file is one MUSCIMA++ document.
        document_name = xml_file.stem

        # Convert each `Node` object into a plain Python dictionary.
        for node in nodes:
            # Node IDs repeat across files, so `node_key` makes the node unique
            # across the whole dataset.
            node_key = f"{document_name}::{node.id}"

            node_dict = {
                "document": document_name,
                "id": node.id,
                "node_key": node_key,
                "class_name": node.class_name,
                "bounding_box": {
                    "top": node.top,
                    "left": node.left,
                    "bottom": node.bottom,
                    "right": node.right,
                },
                "outlinks": node.outlinks,
            }
            all_node_dicts.append(node_dict)

            # Build one edge dictionary for each outlink.
            # Storing both raw IDs and unique node keys makes the output useful
            # both for quick inspection and for later graph-building code.
            for target_node_id in node.outlinks:
                edge_dict = {
                    "document": document_name,
                    "source_id": node.id,
                    "target_id": target_node_id,
                    "source_node_key": f"{document_name}::{node.id}",
                    "target_node_key": f"{document_name}::{target_node_id}",
                }
                all_edge_dicts.append(edge_dict)

    # Make sure the output folder exists before saving JSON files.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # `json.dump(...)` writes Python lists/dictionaries to a JSON file.
    # `indent=2` makes the result easy to inspect and debug.
    with open(NODES_JSON_PATH, "w", encoding="utf-8") as nodes_file:
        json.dump(all_node_dicts, nodes_file, indent=2)

    with open(EDGES_JSON_PATH, "w", encoding="utf-8") as edges_file:
        json.dump(all_edge_dicts, edges_file, indent=2)

    print()
    print(f"Total node dictionaries: {len(all_node_dicts)}")
    print(f"Total edge dictionaries: {len(all_edge_dicts)}")
    print()
    print(f"Saved nodes JSON to: {NODES_JSON_PATH}")
    print(f"Saved edges JSON to: {EDGES_JSON_PATH}")
    print()
    print("First 3 saved node dictionaries:")
    for node_dict in all_node_dicts[:3]:
        print(node_dict)
    print()
    print("First 3 saved edge dictionaries:")
    for edge_dict in all_edge_dicts[:3]:
        print(edge_dict)


if __name__ == "__main__":
    main()
