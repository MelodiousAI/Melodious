"""Build document-level graph dictionaries from parsed MUSCIMA++ data.

This file is the dataset-facing graph builder.
It works with parsed MUSCIMA++ node and edge JSON files, detects staff regions
for each page image, and saves one graph dictionary per document.
"""

from pathlib import Path
import argparse
import csv
import json
import re

import cv2
import numpy as np

from src.data_prep.staff_detection import detect_staff_lines


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NODES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "muscima_nodes.json"
EDGES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "muscima_edges.json"
IMAGE_ROOT = PROJECT_ROOT / "data" / "cvc-muscima" / "CVCMUSCIMA_WI" / "PNG_GT_Gray"
OUTPUT_GRAPHS_DIR = PROJECT_ROOT / "data" / "processed" / "graphs"
GENERATED_IMAGE_DIR = PROJECT_ROOT / "data" / "processed" / "generated_muscima_images"
OUTPUT_SUMMARY_CSV_PATH = OUTPUT_GRAPHS_DIR / "summary.csv"
OUTPUT_BATCH_STATS_JSON_PATH = OUTPUT_GRAPHS_DIR / "batch_stats.json"

# Set this to a number like 5 for a small test batch.
# Set it to None to build graphs for all documents.
DOCUMENT_LIMIT = None


def load_muscima_data():
    """Load the processed MUSCIMA node and edge JSON files.

    These files are produced by `parse_muscima.py` and act as the input for the
    document-level graph builder.
    """
    with open(NODES_JSON_PATH, "r", encoding="utf-8") as nodes_file:
        all_nodes = json.load(nodes_file)

    with open(EDGES_JSON_PATH, "r", encoding="utf-8") as edges_file:
        all_edges = json.load(edges_file)

    return all_nodes, all_edges


def get_document_names(all_nodes):
    """Collect the unique MUSCIMA document names in sorted order."""
    document_names = {node["document"] for node in all_nodes}
    return sorted(document_names)


def select_documents_to_build(document_names, document_limit):
    """Choose a small test batch or the full dataset.

    This keeps the same build logic usable for both quick debugging and larger
    batch runs.
    """
    if document_limit is None:
        return document_names

    return document_names[:document_limit]


def get_document_nodes(all_nodes, document_name):
    """Keep only the nodes that belong to one MUSCIMA document."""
    return [node for node in all_nodes if node["document"] == document_name]


def get_document_edges(all_edges, document_name):
    """Keep only the edges that belong to one MUSCIMA document."""
    return [edge for edge in all_edges if edge["document"] == document_name]


def get_image_path_from_document(document_name):
    """Convert a MUSCIMA document name into the matching image path.

    Example:
    `CVC-MUSCIMA_W-01_N-10_D-ideal`
    becomes:
    `data/cvc-muscima/CVCMUSCIMA_WI/PNG_GT_Gray/w-01/p010.png`
    """
    writer_match = re.search(r"W-(\d+)", document_name)
    page_match = re.search(r"N-(\d+)", document_name)

    if writer_match is None or page_match is None:
        raise ValueError(f"Could not parse writer/page from document name: {document_name}")

    writer_number = int(writer_match.group(1))
    page_number = int(page_match.group(1))

    writer_folder = f"w-{writer_number:02d}"
    image_name = f"p{page_number:03d}.png"

    return IMAGE_ROOT / writer_folder / image_name


def infer_image_size_from_nodes(document_nodes):
    """Infer a reasonable placeholder image size from parsed node boxes."""
    if not document_nodes:
        return 1600, 2200

    max_right = max(int(node["bounding_box"]["right"]) for node in document_nodes)
    max_bottom = max(int(node["bounding_box"]["bottom"]) for node in document_nodes)
    width = max(1200, max_right + 80)
    height = max(1200, max_bottom + 80)
    return width, height


def infer_staff_regions_from_nodes(document_nodes):
    """Build broad staff regions from node vertical extents when the page image is unavailable."""
    if not document_nodes:
        return [(120, 260), (360, 500), (600, 740), (840, 980)]

    y_min = min(int(node["bounding_box"]["top"]) for node in document_nodes)
    y_max = max(int(node["bounding_box"]["bottom"]) for node in document_nodes)
    return [(max(0, y_min - 40), y_max + 40)]


def create_placeholder_image(document_name, document_nodes=None):
    """Create a lightweight local placeholder page for tests when dataset PNGs are absent."""
    output_path = GENERATED_IMAGE_DIR / f"{document_name}.png"
    if output_path.exists():
        return output_path

    width, height = infer_image_size_from_nodes(document_nodes or [])
    image = np.full((height, width), 255, dtype=np.uint8)
    staff_regions = infer_staff_regions_from_nodes(document_nodes or [])

    for y_min, y_max in staff_regions:
        top = max(20, y_min + 20)
        bottom = min(height - 20, y_max - 20)
        if bottom <= top:
            continue

        for y in np.linspace(top, bottom, 5):
            cv2.line(image, (40, int(round(y))), (width - 40, int(round(y))), 0, 2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)
    return output_path


def ensure_document_image(document_name, document_nodes=None):
    """Return a real local MUSCIMA image, or generate a lightweight placeholder."""
    image_path = get_image_path_from_document(document_name)
    if image_path.exists():
        return image_path

    return create_placeholder_image(document_name, document_nodes=document_nodes)


def get_node_center_y(node_dict):
    """Compute the vertical center of a symbol from its bounding box."""
    top = node_dict["bounding_box"]["top"]
    bottom = node_dict["bounding_box"]["bottom"]
    return int(round((top + bottom) / 2))


def assign_node_to_staff(node_dict, staff_regions):
    """Assign one parsed MUSCIMA node to the most appropriate staff region.

    The first rule is exact containment: if the symbol center lies inside a
    staff region, use that staff. If not, use the closest staff center so the
    graph still captures a plausible staff membership.
    """
    center_y = get_node_center_y(node_dict)

    for staff_index, (y_min, y_max) in enumerate(staff_regions):
        if y_min <= center_y <= y_max:
            return staff_index

    if not staff_regions:
        return None

    closest_staff_index = None
    closest_distance = None

    for staff_index, (y_min, y_max) in enumerate(staff_regions):
        staff_center_y = (y_min + y_max) / 2
        distance = abs(center_y - staff_center_y)

        if closest_distance is None or distance < closest_distance:
            closest_distance = distance
            closest_staff_index = staff_index

    return closest_staff_index


def enrich_nodes_with_staff_info(document_nodes, staff_regions):
    """Add staff-related metadata to each node in one document graph.

    The graph keeps both the original parsed node data and two extra fields:
    - `center_y` for easier debugging and analysis
    - `staff_index` for staff-aware graph structure later on
    """
    enriched_nodes = []

    for node in document_nodes:
        enriched_node = dict(node)
        enriched_node["center_y"] = get_node_center_y(node)
        enriched_node["staff_index"] = assign_node_to_staff(node, staff_regions)
        enriched_nodes.append(enriched_node)

    return enriched_nodes


def build_graph_for_document(document_name, all_nodes, all_edges):
    """Build one complete graph dictionary for one MUSCIMA document.

    This is the main per-document pipeline:
    1. filter nodes and edges for one page
    2. find the matching page image
    3. detect staff regions on that image
    4. attach staff indices to the nodes
    5. return one graph dictionary
    """
    document_nodes = get_document_nodes(all_nodes, document_name)
    document_edges = get_document_edges(all_edges, document_name)
    image_path = get_image_path_from_document(document_name)

    if image_path.exists():
        staff_regions = detect_staff_lines(image_path)
    else:
        image_path = create_placeholder_image(document_name, document_nodes=document_nodes)
        staff_regions = infer_staff_regions_from_nodes(document_nodes)
    enriched_nodes = enrich_nodes_with_staff_info(document_nodes, staff_regions)

    graph_data = {
        "document": document_name,
        "image_path": str(image_path),
        "staff_regions": staff_regions,
        "nodes": enriched_nodes,
        "edges": document_edges,
    }

    return graph_data


def get_graph_output_path(document_name):
    """Return the output path for one document graph JSON file."""
    return OUTPUT_GRAPHS_DIR / f"{document_name}_graph.json"


def save_graph(graph_data, output_path):
    """Save one graph dictionary as readable JSON."""
    with open(output_path, "w", encoding="utf-8") as graph_file:
        json.dump(graph_data, graph_file, indent=2)


def count_unassigned_nodes(graph_data):
    """Count how many nodes still have no clear staff assignment."""
    return sum(1 for node in graph_data["nodes"] if node["staff_index"] is None)


def count_unique_node_classes(graph_data):
    """Count how many distinct symbol classes appear in one document graph."""
    return len({node["class_name"] for node in graph_data["nodes"]})


def build_nodes_per_staff(graph_data):
    """Count how many nodes were assigned to each detected staff region."""
    staff_counts = {staff_index: 0 for staff_index in range(len(graph_data["staff_regions"]))}

    for node in graph_data["nodes"]:
        staff_index = node["staff_index"]

        if staff_index is None:
            continue

        staff_counts[staff_index] = staff_counts.get(staff_index, 0) + 1

    return staff_counts


def compute_graph_statistics(graph_data):
    """Compute per-document statistics for inspection and batch summaries.

    These statistics are intentionally simple. They help answer whether the
    generated graph looks structurally plausible before the project moves on
    to alignment or model training.
    """
    node_count = len(graph_data["nodes"])
    edge_count = len(graph_data["edges"])
    staff_region_count = len(graph_data["staff_regions"])
    unassigned_node_count = count_unassigned_nodes(graph_data)
    assigned_node_count = node_count - unassigned_node_count
    unique_node_class_count = count_unique_node_classes(graph_data)
    nodes_per_staff = build_nodes_per_staff(graph_data)
    nodes_per_staff_values = list(nodes_per_staff.values())

    if staff_region_count > 0:
        average_nodes_per_staff = assigned_node_count / staff_region_count
        max_nodes_on_staff = max(nodes_per_staff_values) if nodes_per_staff_values else 0
        min_nodes_on_staff = min(nodes_per_staff_values) if nodes_per_staff_values else 0
    else:
        average_nodes_per_staff = 0.0
        max_nodes_on_staff = 0
        min_nodes_on_staff = 0

    if node_count > 1:
        edge_density = edge_count / (node_count * (node_count - 1))
    else:
        edge_density = 0.0

    if node_count > 0:
        assigned_node_ratio = assigned_node_count / node_count
    else:
        assigned_node_ratio = 0.0

    return {
        "document": graph_data["document"],
        "image_path": graph_data["image_path"],
        "graph_json_path": str(get_graph_output_path(graph_data["document"])),
        "staff_region_count": staff_region_count,
        "node_count": node_count,
        "edge_count": edge_count,
        "unique_node_class_count": unique_node_class_count,
        "unassigned_node_count": unassigned_node_count,
        "assigned_node_ratio": round(assigned_node_ratio, 6),
        "average_nodes_per_staff": round(average_nodes_per_staff, 3),
        "max_nodes_on_staff": max_nodes_on_staff,
        "min_nodes_on_staff": min_nodes_on_staff,
        "edge_density": round(edge_density, 8),
        "nodes_per_staff": nodes_per_staff,
    }


def build_summary_row(graph_data):
    """Build one CSV summary row for one document graph."""
    statistics = compute_graph_statistics(graph_data)

    return {
        "document": statistics["document"],
        "image_path": statistics["image_path"],
        "graph_json_path": statistics["graph_json_path"],
        "staff_region_count": statistics["staff_region_count"],
        "node_count": statistics["node_count"],
        "edge_count": statistics["edge_count"],
        "unique_node_class_count": statistics["unique_node_class_count"],
        "unassigned_node_count": statistics["unassigned_node_count"],
        "assigned_node_ratio": statistics["assigned_node_ratio"],
        "average_nodes_per_staff": statistics["average_nodes_per_staff"],
        "max_nodes_on_staff": statistics["max_nodes_on_staff"],
        "min_nodes_on_staff": statistics["min_nodes_on_staff"],
        "edge_density": statistics["edge_density"],
    }


def save_summary_csv(summary_rows, output_path):
    """Save the graph-build summary rows into one CSV file."""
    with open(output_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "document",
                "image_path",
                "graph_json_path",
                "staff_region_count",
                "node_count",
                "edge_count",
                "unique_node_class_count",
                "unassigned_node_count",
                "assigned_node_ratio",
                "average_nodes_per_staff",
                "max_nodes_on_staff",
                "min_nodes_on_staff",
                "edge_density",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)


def save_batch_statistics(summary_rows, output_path):
    """Save high-level batch statistics alongside the per-document CSV summary."""
    document_count = len(summary_rows)
    total_nodes = sum(row["node_count"] for row in summary_rows)
    total_edges = sum(row["edge_count"] for row in summary_rows)
    total_staff_regions = sum(row["staff_region_count"] for row in summary_rows)
    total_unassigned_nodes = sum(row["unassigned_node_count"] for row in summary_rows)

    if document_count > 0:
        average_nodes_per_document = total_nodes / document_count
        average_edges_per_document = total_edges / document_count
        average_staff_regions_per_document = total_staff_regions / document_count
    else:
        average_nodes_per_document = 0.0
        average_edges_per_document = 0.0
        average_staff_regions_per_document = 0.0

    worst_unassigned_documents = sorted(
        summary_rows,
        key=lambda row: (row["unassigned_node_count"], row["node_count"]),
        reverse=True,
    )[:5]

    batch_statistics = {
        "document_count": document_count,
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "total_staff_regions": total_staff_regions,
        "total_unassigned_nodes": total_unassigned_nodes,
        "average_nodes_per_document": round(average_nodes_per_document, 3),
        "average_edges_per_document": round(average_edges_per_document, 3),
        "average_staff_regions_per_document": round(average_staff_regions_per_document, 3),
        "worst_unassigned_documents": [
            {
                "document": row["document"],
                "unassigned_node_count": row["unassigned_node_count"],
                "node_count": row["node_count"],
            }
            for row in worst_unassigned_documents
        ],
    }

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(batch_statistics, json_file, indent=2)


def build_graphs_for_documents(document_names, all_nodes, all_edges):
    """Build and save graphs for multiple documents in one batch run."""
    OUTPUT_GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for document_name in document_names:
        print(f"Building graph for document: {document_name}")
        graph_data = build_graph_for_document(document_name, all_nodes, all_edges)
        output_path = get_graph_output_path(document_name)
        save_graph(graph_data, output_path)
        summary_rows.append(build_summary_row(graph_data))

    save_summary_csv(summary_rows, OUTPUT_SUMMARY_CSV_PATH)
    save_batch_statistics(summary_rows, OUTPUT_BATCH_STATS_JSON_PATH)
    return summary_rows




def parse_cli_args():
    """Parse command-line arguments for the MUSCIMA graph builder."""
    parser = argparse.ArgumentParser(description="Build MUSCIMA reference graph JSON files.")
    parser.add_argument(
        "--limit",
        type=int,
        default=DOCUMENT_LIMIT,
        help="Build only the first N documents. Omit to use the file default.",
    )
    parser.add_argument(
        "--document",
        type=str,
        default=None,
        help="Build only one specific MUSCIMA document name.",
    )
    return parser.parse_args()


def main():
    """Run the MUSCIMA graph builder from the command line."""
    args = parse_cli_args()
    if not NODES_JSON_PATH.exists():
        print(f"Nodes JSON not found: {NODES_JSON_PATH}")
        return

    if not EDGES_JSON_PATH.exists():
        print(f"Edges JSON not found: {EDGES_JSON_PATH}")
        return

    print("Loading parsed MUSCIMA data...")
    all_nodes, all_edges = load_muscima_data()
    document_names = get_document_names(all_nodes)

    if args.document is not None:
        documents_to_build = [args.document]
        print(f"Building graph for one document: {args.document}")
    else:
        documents_to_build = select_documents_to_build(document_names, args.limit)

        if args.limit is None:
            print(f"Building graphs for all {len(documents_to_build)} documents...")
        else:
            print(f"Building graphs for {len(documents_to_build)} documents...")

    summary_rows = build_graphs_for_documents(documents_to_build, all_nodes, all_edges)

    print()
    print(f"Saved graph JSON files to: {OUTPUT_GRAPHS_DIR}")
    print(f"Saved graph summary CSV to: {OUTPUT_SUMMARY_CSV_PATH}")
    print(f"Saved batch statistics JSON to: {OUTPUT_BATCH_STATS_JSON_PATH}")
    print()
    print("Graph build summary:")

    for row in summary_rows[:10]:
        print(f"Document: {row['document']}")
        print(f"  Staff regions: {row['staff_region_count']}")
        print(f"  Nodes: {row['node_count']}")
        print(f"  Edges: {row['edge_count']}")
        print(f"  Unassigned nodes: {row['unassigned_node_count']}")
        print()

    if len(summary_rows) > 10:
        print(f"Printed the first 10 summaries out of {len(summary_rows)} documents.")


if __name__ == "__main__":
    main()
