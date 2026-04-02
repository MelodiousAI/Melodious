"""Run graph building and alignment on MUSCIMA reference payloads."""

from pathlib import Path
import argparse
import json

from detection_alignment import MUSCIMA_SHARED_CLASS_NAME_TO_ID, align_document_detections, load_muscima_nodes
from muscima_graph_builder import get_image_path_from_document
from pyg_graph_builder import (
    build_graph_from_muscima_detection_json,
    build_graph_statistics,
    extract_payload_image_shape,
    load_detection_payload,
    load_image_shape,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE_DIR = PROJECT_ROOT / "sample_detections" / "muscima_reference"
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "outputs" / "muscima_reference_integration" / "summary.json"


def evaluate_muscima_reference_payloads(reference_dir=DEFAULT_REFERENCE_DIR):
    """Build graphs and alignment summaries for MUSCIMA reference payloads."""
    reference_dir = Path(reference_dir)

    if not reference_dir.exists():
        raise FileNotFoundError(f"Reference payload directory not found: {reference_dir}")

    payload_paths = sorted(reference_dir.glob("*.json"))

    if not payload_paths:
        raise FileNotFoundError(f"No MUSCIMA reference payloads found in: {reference_dir}")

    all_nodes = load_muscima_nodes()
    summary_rows = []

    for payload_path in payload_paths:
        payload = load_detection_payload(payload_path)
        document_name = payload_path.stem
        local_image_path = get_image_path_from_document(document_name)
        graph_data = build_graph_from_muscima_detection_json(payload_path)
        graph_stats = build_graph_statistics(graph_data)
        alignment_result = align_document_detections(
            document_name,
            payload,
            all_nodes,
            iou_threshold=0.5,
            class_name_to_id=MUSCIMA_SHARED_CLASS_NAME_TO_ID,
        )

        summary_rows.append(
            {
                "document": document_name,
                "payload_json": str(payload_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "local_image_path": str(local_image_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "payload_image_shape": list(extract_payload_image_shape(payload)),
                "local_image_shape": list(load_image_shape(local_image_path)),
                "payload_detection_count": len(payload["detections"]),
                "graph_stats": graph_stats,
                "alignment_summary": alignment_result["summary"],
            }
        )

    return summary_rows


def save_summary(summary_rows, output_json_path=DEFAULT_OUTPUT_JSON):
    """Save the MUSCIMA reference integration summary as JSON."""
    output_json_path = Path(output_json_path)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
    return output_json_path


def parse_cli_args():
    """Parse CLI arguments for the MUSCIMA reference evaluation script."""
    parser = argparse.ArgumentParser(description="Evaluate MUSCIMA reference payload integration.")
    parser.add_argument(
        "--reference-dir",
        type=str,
        default=str(DEFAULT_REFERENCE_DIR),
        help="Directory containing MUSCIMA reference payload JSON files.",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=str(DEFAULT_OUTPUT_JSON),
        help="Path to write the summary JSON artifact.",
    )
    return parser.parse_args()


def main():
    """Run MUSCIMA reference graph+alignment evaluation from the command line."""
    args = parse_cli_args()
    summary_rows = evaluate_muscima_reference_payloads(args.reference_dir)
    output_json_path = save_summary(summary_rows, args.output_json)

    print(f"Saved MUSCIMA reference integration summary to: {output_json_path}")

    for row in summary_rows:
        print(row["document"])
        print(f"  Detections: {row['payload_detection_count']}")
        print(f"  Graph nodes: {row['graph_stats']['num_nodes']}")
        print(f"  Graph edges: {row['graph_stats']['num_edges']}")
        print(f"  Matches: {row['alignment_summary']['match_count']}")
        print(f"  Precision: {row['alignment_summary']['precision']}")
        print(f"  Recall: {row['alignment_summary']['recall']}")
        print()


if __name__ == "__main__":
    main()
