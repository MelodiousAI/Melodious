"""Export MUSCIMA pages into the page-level training format needed for GNN work."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

from src.data_prep.shared_detection_contract import MUSCIMA_TO_SHARED_DETECTION_CLASS
from src.graph.muscima_graph_builder import (
    OUTPUT_GRAPHS_DIR,
    get_document_names,
    get_graph_output_path,
    get_image_path_from_document,
    load_muscima_data,
)
from src.graph.pyg_graph_builder import (
    attach_staff_info,
    build_horizontal_neighbor_edges,
    build_knn_edges,
    build_same_staff_local_edges,
    build_vertical_overlap_edges,
    extract_payload_image_shape,
    load_image_shape,
    prepare_detections,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "training_exports"
DEFAULT_SUMMARY_CSV_PATH = DEFAULT_OUTPUT_DIR / "summary.csv"
DEFAULT_BATCH_STATS_JSON_PATH = DEFAULT_OUTPUT_DIR / "batch_stats.json"

TRAINING_EDGE_TYPES = (
    "knn",
    "same_staff_local",
    "vertical_overlap",
    "horizontal_neighbor",
)

TRAINING_EDGE_LABELS = (
    "no_relation",
    "stem_notehead",
    "beam_notegroup",
    "slur_phrase",
    "tie_sustained",
)

NOTEHEAD_CLASS_NAMES = {
    "noteheadFull",
    "noteheadHalf",
    "noteheadWhole",
    "noteheadFullSmall",
}


def load_graph_data_for_document(document_name: str) -> dict:
    """Load one existing document graph JSON from disk."""
    graph_path = get_graph_output_path(document_name)

    if not graph_path.exists():
        raise FileNotFoundError(
            f"Graph JSON for {document_name} was not found at {graph_path}. "
            "Build MUSCIMA graphs first before exporting training data."
        )

    return json.loads(graph_path.read_text(encoding="utf-8"))


def get_training_output_path(document_name: str, output_dir: Path = DEFAULT_OUTPUT_DIR) -> Path:
    """Return the target JSON path for one page-level training export."""
    return output_dir / f"{document_name}.json"


def convert_bbox_to_payload_shapes(bounding_box: dict, image_width: int, image_height: int) -> tuple[dict, dict]:
    """Convert MUSCIMA xyxy boxes into the shared normalized/pixel bbox format."""
    left = float(bounding_box["left"])
    top = float(bounding_box["top"])
    right = float(bounding_box["right"])
    bottom = float(bounding_box["bottom"])
    width = right - left
    height = bottom - top
    x_center = left + (width / 2.0)
    y_center = top + (height / 2.0)

    bbox = {
        "x_center": x_center / image_width,
        "y_center": y_center / image_height,
        "width": width / image_width,
        "height": height / image_height,
    }
    bbox_pixels = {
        "x1": left,
        "y1": top,
        "x2": right,
        "y2": bottom,
    }
    return bbox, bbox_pixels


def filter_shared_contract_nodes(document_graph: dict) -> list[dict]:
    """Keep only the MUSCIMA nodes that map into the shared detector taxonomy."""
    shared_nodes = [
        node
        for node in document_graph["nodes"]
        if node["class_name"] in MUSCIMA_TO_SHARED_DETECTION_CLASS
    ]
    return sorted(shared_nodes, key=lambda node: int(node["id"]))


def build_node_record(
    node: dict,
    node_idx: int,
    page_id: str,
    image_width: int,
    image_height: int,
) -> dict:
    """Build one exported node record using the agreed page-level schema."""
    class_id, class_name = MUSCIMA_TO_SHARED_DETECTION_CLASS[node["class_name"]]
    bbox, bbox_pixels = convert_bbox_to_payload_shapes(
        node["bounding_box"],
        image_width=image_width,
        image_height=image_height,
    )

    return {
        "node_idx": node_idx,
        "node_id": f"{page_id}::{node_idx}",
        "class_id": class_id,
        "class_name": class_name,
        "confidence": 1.0,
        "bbox": bbox,
        "bbox_pixels": bbox_pixels,
        "staff_index": node["staff_index"],
    }


def build_canonical_detection_for_node(node_record: dict, image_width: int, image_height: int) -> dict:
    """Convert an exported node record into the canonical detection format used by the graph builder."""
    bbox = node_record["bbox"]
    return {
        "class_id": node_record["class_id"],
        "bbox": [
            float(bbox["x_center"]) * image_width,
            float(bbox["y_center"]) * image_height,
            float(bbox["width"]) * image_width,
            float(bbox["height"]) * image_height,
        ],
        "conf": float(node_record["confidence"]),
    }


def build_processed_training_detections(node_records: list[dict], image_shape: tuple[int, int], staff_regions: list) -> list[dict]:
    """Prepare reduced MUSCIMA nodes for candidate-edge generation."""
    image_height, image_width = image_shape
    detections = [
        build_canonical_detection_for_node(node_record, image_width=image_width, image_height=image_height)
        for node_record in node_records
    ]
    processed_detections = prepare_detections(detections, image_shape)
    return attach_staff_info(processed_detections, staff_regions, image_shape)


def build_candidate_edge_sets(processed_detections: list[dict], image_shape: tuple[int, int]) -> dict[str, set[tuple[int, int]]]:
    """Build the four agreed candidate-edge families used in the training export."""
    return {
        "knn": build_knn_edges(processed_detections, image_shape),
        "same_staff_local": build_same_staff_local_edges(processed_detections),
        "vertical_overlap": build_vertical_overlap_edges(processed_detections),
        "horizontal_neighbor": build_horizontal_neighbor_edges(processed_detections),
    }


def build_raw_relation_maps(document_graph: dict, kept_raw_node_ids: set[int]) -> dict[str, set[frozenset[int]]]:
    """Project MUSCIMA raw edges into the compact supervision labels Ahmad requested."""
    nodes_by_raw_id = {int(node["id"]): node for node in document_graph["nodes"]}
    outlinks_by_raw_id = {
        int(node["id"]): {int(target_id) for target_id in node.get("outlinks", [])}
        for node in document_graph["nodes"]
    }

    relation_pairs = {
        "stem_notehead": set(),
        "beam_notegroup": set(),
        "slur_phrase": set(),
        "tie_sustained": set(),
    }

    for source_raw_id, outlinks in outlinks_by_raw_id.items():
        source_node = nodes_by_raw_id[source_raw_id]
        source_class_name = source_node["class_name"]

        for target_raw_id in outlinks:
            target_node = nodes_by_raw_id.get(target_raw_id)

            if target_node is None:
                continue

            target_class_name = target_node["class_name"]
            pair = frozenset({source_raw_id, target_raw_id})

            if (
                source_raw_id in kept_raw_node_ids
                and target_raw_id in kept_raw_node_ids
                and {source_class_name, target_class_name} <= (NOTEHEAD_CLASS_NAMES | {"stem"})
                and "stem" in {source_class_name, target_class_name}
            ):
                relation_pairs["stem_notehead"].add(pair)

            if (
                source_raw_id in kept_raw_node_ids
                and target_raw_id in kept_raw_node_ids
                and {source_class_name, target_class_name} <= (NOTEHEAD_CLASS_NAMES | {"beam"})
                and "beam" in {source_class_name, target_class_name}
            ):
                relation_pairs["beam_notegroup"].add(pair)

    for connector_class_name, label_name in (("slur", "slur_phrase"), ("tie", "tie_sustained")):
        connector_to_noteheads = defaultdict(set)

        for source_raw_id, outlinks in outlinks_by_raw_id.items():
            if source_raw_id not in kept_raw_node_ids:
                continue

            source_class_name = nodes_by_raw_id[source_raw_id]["class_name"]

            if source_class_name not in NOTEHEAD_CLASS_NAMES:
                continue

            for target_raw_id in outlinks:
                target_node = nodes_by_raw_id.get(target_raw_id)

                if target_node is None or target_node["class_name"] != connector_class_name:
                    continue

                connector_to_noteheads[target_raw_id].add(source_raw_id)

        for connected_noteheads in connector_to_noteheads.values():
            for source_raw_id, target_raw_id in itertools.combinations(sorted(connected_noteheads), 2):
                relation_pairs[label_name].add(frozenset({source_raw_id, target_raw_id}))

    return relation_pairs


def get_candidate_edge_label(source_raw_id: int, target_raw_id: int, relation_pairs: dict[str, set[frozenset[int]]]) -> str:
    """Assign the supervision label for one candidate edge record."""
    pair = frozenset({source_raw_id, target_raw_id})

    for label_name in ("stem_notehead", "beam_notegroup", "slur_phrase", "tie_sustained"):
        if pair in relation_pairs[label_name]:
            return label_name

    return "no_relation"


def build_edge_records(
    node_records: list[dict],
    candidate_edge_sets: dict[str, set[tuple[int, int]]],
    raw_node_ids_by_idx: dict[int, int],
    relation_pairs: dict[str, set[frozenset[int]]],
) -> list[dict]:
    """Build one edge record per directed candidate-edge occurrence."""
    edge_records = []

    for edge_type in TRAINING_EDGE_TYPES:
        for source_idx, target_idx in sorted(candidate_edge_sets[edge_type]):
            source_raw_id = raw_node_ids_by_idx[source_idx]
            target_raw_id = raw_node_ids_by_idx[target_idx]

            edge_records.append(
                {
                    "source_idx": source_idx,
                    "target_idx": target_idx,
                    "edge_type": edge_type,
                    "edge_label": get_candidate_edge_label(
                        source_raw_id,
                        target_raw_id,
                        relation_pairs=relation_pairs,
                    ),
                }
            )

    return edge_records


def build_document_training_export(document_name: str) -> dict:
    """Build the full page-level training export for one MUSCIMA document."""
    document_graph = load_graph_data_for_document(document_name)
    image_path = get_image_path_from_document(document_name)
    image_shape = load_image_shape(image_path)
    image_height, image_width = image_shape
    staff_regions = document_graph["staff_regions"]

    shared_nodes = filter_shared_contract_nodes(document_graph)
    node_records = [
        build_node_record(
            node,
            node_idx=node_idx,
            page_id=document_name,
            image_width=image_width,
            image_height=image_height,
        )
        for node_idx, node in enumerate(shared_nodes)
    ]

    raw_node_ids_by_idx = {
        node_idx: int(node["id"])
        for node_idx, node in enumerate(shared_nodes)
    }
    kept_raw_node_ids = set(raw_node_ids_by_idx.values())
    processed_detections = build_processed_training_detections(
        node_records,
        image_shape=image_shape,
        staff_regions=staff_regions,
    )
    candidate_edge_sets = build_candidate_edge_sets(processed_detections, image_shape)
    relation_pairs = build_raw_relation_maps(document_graph, kept_raw_node_ids=kept_raw_node_ids)
    edge_records = build_edge_records(
        node_records=node_records,
        candidate_edge_sets=candidate_edge_sets,
        raw_node_ids_by_idx=raw_node_ids_by_idx,
        relation_pairs=relation_pairs,
    )

    return {
        "page_id": document_name,
        "image_path": str(image_path.relative_to(PROJECT_ROOT)),
        "image_size": {
            "width": image_width,
            "height": image_height,
        },
        "nodes": node_records,
        "edges": edge_records,
    }


def save_document_training_export(training_export: dict, output_path: Path) -> None:
    """Write one page-level training export to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(training_export, indent=2), encoding="utf-8")


def build_summary_row(training_export: dict) -> dict:
    """Build one summary row for CSV and batch statistics."""
    edge_label_counts = Counter(edge["edge_label"] for edge in training_export["edges"])
    edge_type_counts = Counter(edge["edge_type"] for edge in training_export["edges"])

    return {
        "page_id": training_export["page_id"],
        "image_path": training_export["image_path"],
        "node_count": len(training_export["nodes"]),
        "edge_count": len(training_export["edges"]),
        "stem_notehead_count": edge_label_counts["stem_notehead"],
        "beam_notegroup_count": edge_label_counts["beam_notegroup"],
        "slur_phrase_count": edge_label_counts["slur_phrase"],
        "tie_sustained_count": edge_label_counts["tie_sustained"],
        "no_relation_count": edge_label_counts["no_relation"],
        "knn_count": edge_type_counts["knn"],
        "same_staff_local_count": edge_type_counts["same_staff_local"],
        "vertical_overlap_count": edge_type_counts["vertical_overlap"],
        "horizontal_neighbor_count": edge_type_counts["horizontal_neighbor"],
    }


def save_summary_csv(summary_rows: list[dict], output_path: Path) -> None:
    """Save per-page training-export statistics as CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "page_id",
                "image_path",
                "node_count",
                "edge_count",
                "stem_notehead_count",
                "beam_notegroup_count",
                "slur_phrase_count",
                "tie_sustained_count",
                "no_relation_count",
                "knn_count",
                "same_staff_local_count",
                "vertical_overlap_count",
                "horizontal_neighbor_count",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)


def save_batch_stats(summary_rows: list[dict], output_path: Path) -> None:
    """Save aggregate batch statistics for all exported MUSCIMA pages."""
    totals = Counter()

    for row in summary_rows:
        totals.update(
            {
                "node_count": row["node_count"],
                "edge_count": row["edge_count"],
                "stem_notehead_count": row["stem_notehead_count"],
                "beam_notegroup_count": row["beam_notegroup_count"],
                "slur_phrase_count": row["slur_phrase_count"],
                "tie_sustained_count": row["tie_sustained_count"],
                "no_relation_count": row["no_relation_count"],
            }
        )

    batch_stats = {
        "page_count": len(summary_rows),
        **totals,
        "edge_type_vocabulary": list(TRAINING_EDGE_TYPES),
        "edge_label_vocabulary": list(TRAINING_EDGE_LABELS),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(batch_stats, indent=2), encoding="utf-8")


def export_documents(document_names: list[str], output_dir: Path = DEFAULT_OUTPUT_DIR) -> list[dict]:
    """Export a list of MUSCIMA documents and return their summary rows."""
    summary_rows = []

    for document_name in document_names:
        training_export = build_document_training_export(document_name)
        save_document_training_export(
            training_export,
            get_training_output_path(document_name, output_dir=output_dir),
        )
        summary_rows.append(build_summary_row(training_export))

    return summary_rows


def parse_cli_args():
    """Parse CLI arguments for MUSCIMA training export runs."""
    parser = argparse.ArgumentParser(description="Export MUSCIMA pages into page-level GNN training JSON files.")
    parser.add_argument("--document", type=str, default=None, help="Optional single MUSCIMA document name.")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for quick local runs.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory to write page JSON files.")
    return parser.parse_args()


def main() -> None:
    """Export one or more MUSCIMA pages into the agreed training format."""
    args = parse_cli_args()
    all_nodes, _all_edges = load_muscima_data()
    document_names = get_document_names(all_nodes)

    if args.document:
        document_names = [args.document]
    elif args.limit is not None:
        document_names = document_names[: args.limit]

    summary_rows = export_documents(document_names, output_dir=args.output_dir)
    save_summary_csv(summary_rows, args.output_dir / DEFAULT_SUMMARY_CSV_PATH.name)
    save_batch_stats(summary_rows, args.output_dir / DEFAULT_BATCH_STATS_JSON_PATH.name)

    print(f"Exported {len(summary_rows)} MUSCIMA training pages to {args.output_dir}")
    for row in summary_rows[:5]:
        print(
            f"  {row['page_id']}: {row['node_count']} nodes, {row['edge_count']} edges, "
            f"{row['stem_notehead_count']} stem_notehead, {row['beam_notegroup_count']} beam_notegroup, "
            f"{row['slur_phrase_count']} slur_phrase, {row['tie_sustained_count']} tie_sustained"
        )


if __name__ == "__main__":
    main()
