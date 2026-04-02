"""Create and load a stable class mapping for MUSCIMA symbol classes.

This module freezes one explicit mapping contract between:
- MUSCIMA class names from the parsed dataset
- integer class IDs used by later detection, alignment, and graph code

The mapping is deterministic: class names are sorted alphabetically before IDs
are assigned. That keeps regeneration stable and removes hidden assumptions
about class ordering.
"""

from pathlib import Path
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NODES_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "muscima_nodes.json"
CLASS_MAPPING_JSON_PATH = PROJECT_ROOT / "data" / "processed" / "class_mapping.json"


def load_muscima_nodes(nodes_json_path=NODES_JSON_PATH):
    """Load the parsed MUSCIMA node dictionaries from disk."""
    with open(nodes_json_path, "r", encoding="utf-8") as nodes_file:
        return json.load(nodes_file)


def build_class_name_to_id(nodes):
    """Build a deterministic class-name-to-ID mapping from parsed nodes.

    The mapping uses alphabetical ordering so the same parsed dataset always
    produces the same IDs.
    """
    class_names = sorted({node["class_name"] for node in nodes})
    return {class_name: index for index, class_name in enumerate(class_names)}


def invert_class_mapping(class_name_to_id):
    """Invert a class-name-to-ID mapping into an ID-to-class-name mapping."""
    return {str(class_id): class_name for class_name, class_id in class_name_to_id.items()}


def build_class_mapping_payload(nodes):
    """Build the full serializable payload stored on disk."""
    class_name_to_id = build_class_name_to_id(nodes)
    class_id_to_name = invert_class_mapping(class_name_to_id)

    return {
        "class_count": len(class_name_to_id),
        "class_name_to_id": class_name_to_id,
        "class_id_to_name": class_id_to_name,
    }


def save_class_mapping(payload, output_path=CLASS_MAPPING_JSON_PATH):
    """Save the generated mapping payload to JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, indent=2, sort_keys=True)


def load_class_mapping(mapping_json_path=CLASS_MAPPING_JSON_PATH):
    """Load the saved class mapping payload from disk."""
    with open(mapping_json_path, "r", encoding="utf-8") as mapping_file:
        return json.load(mapping_file)


def get_class_id(class_name, mapping_payload):
    """Look up the integer ID for one class name."""
    return mapping_payload["class_name_to_id"][class_name]


def get_class_name(class_id, mapping_payload):
    """Look up the class name for one integer ID."""
    return mapping_payload["class_id_to_name"][str(class_id)]


def main():
    """Generate and save the stable MUSCIMA class mapping."""
    if not NODES_JSON_PATH.exists():
        print(f"Nodes JSON not found: {NODES_JSON_PATH}")
        return

    nodes = load_muscima_nodes()
    mapping_payload = build_class_mapping_payload(nodes)
    save_class_mapping(mapping_payload)

    print(f"Saved class mapping to: {CLASS_MAPPING_JSON_PATH}")
    print(f"Class count: {mapping_payload['class_count']}")
    print("First 10 class mappings:")

    first_items = list(mapping_payload["class_name_to_id"].items())[:10]
    for class_name, class_id in first_items:
        print(f"  {class_id}: {class_name}")


if __name__ == "__main__":
    main()
