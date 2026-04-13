"""
MUSCIMA++ Data Loader for GNN Training

Loads MUSCIMA++ XML annotations and converts them into PyTorch Geometric
Data objects suitable for training the GNNAssembler edge classifier.

Pipeline:
  1. Parse MUSCIMA++ XML files (using xml.etree or mung)
  2. Filter to our 15-class symbol subset
  3. Create Detection objects from filtered symbols
  4. Build candidate edges via GraphConstructor (k-NN + staff + vertical overlap)
  5. Label each candidate edge by matching against ground-truth outlinks
  6. Package into PyG Data(x, edge_index, edge_type, edge_label) objects
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import random

import numpy as np
import torch
from torch_geometric.data import Data

from .gnn import (
    Detection,
    GraphConstructor,
    NodeFeatureEncoder,
    RELATIONSHIP_TYPES,
    SYMBOL_CLASSES,
)
from .export_muscima_detections import MUSCIMA_TO_CLASS_ID


def _build_training_edges(
    detections: List[Detection],
    k: int = 8,
    max_x_dist: float = 0.15,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Build a lean set of candidate edges optimised for GNN training.

    Compared to GraphConstructor (which adds ALL staff-pair edges and creates
    O(n²) graphs), this function constructs a much tighter graph:
      1. k-NN in Euclidean space (within the whole page, not just same staff)
      2. Vertical overlap edges for stem-notehead candidates
    This keeps edges at O(n·k) instead of O(n²), which drastically reduces
    the no_relation majority and helps the model learn.

    Returns:
        edge_index: (2, E) int64 tensor
        edge_type:  (E,)   int64 tensor  (0=proximity, 1=vertical_overlap)
    """
    n = len(detections)
    if n < 2:
        return torch.zeros((2, 0), dtype=torch.long), torch.zeros(0, dtype=torch.long)

    positions = np.array([[d.x, d.y] for d in detections])
    edges: List[Tuple[int, int]] = []
    edge_types: List[int] = []
    seen = set()

    # 1. k-NN by Euclidean distance (across all nodes, not limited to same staff)
    for i in range(n):
        dists = np.sqrt(((positions - positions[i]) ** 2).sum(axis=1))
        dists[i] = float("inf")
        nearest = np.argsort(dists)[: k]
        for j in nearest:
            j = int(j)
            # Optional: skip very far neighbors horizontally
            if abs(positions[j, 0] - positions[i, 0]) > max_x_dist:
                continue
            if (i, j) not in seen:
                edges.append((i, j))
                edge_types.append(0)  # proximity
                seen.add((i, j))

    # 2. Vertical overlap edges (stem ↔ notehead candidates)
    notehead_ids = {0, 1, 2}  # notehead-full, half, whole
    stem_id = 14
    beam_id = 13
    interesting = notehead_ids | {stem_id, beam_id}
    for i in range(n):
        if detections[i].class_id not in interesting:
            continue
        for j in range(n):
            if i == j or (i, j) in seen:
                continue
            if detections[j].class_id not in interesting:
                continue
            di, dj = detections[i], detections[j]
            y_min_i, y_max_i = di.y - di.h / 2, di.y + di.h / 2
            y_min_j, y_max_j = dj.y - dj.h / 2, dj.y + dj.h / 2
            overlap = min(y_max_i, y_max_j) - max(y_min_i, y_min_j)
            # Also check x proximity
            x_dist = abs(di.x - dj.x)
            if overlap > 0 and x_dist < 0.05:
                edges.append((i, j))
                edge_types.append(1)  # vertical overlap
                seen.add((i, j))

    if not edges:
        return torch.zeros((2, 0), dtype=torch.long), torch.zeros(0, dtype=torch.long)

    edge_index = torch.tensor(edges, dtype=torch.long).t().contiguous()
    edge_type_tensor = torch.tensor(edge_types, dtype=torch.long)
    return edge_index, edge_type_tensor


# Reverse map: MUSCIMA++ class name -> our 15-class ID
# Extended with additional MUSCIMA++ name variants
MUSCIMA_CLASS_MAP: Dict[str, int] = {
    **MUSCIMA_TO_CLASS_ID,
    # Additional MUSCIMA++ variants that map to our classes
    "noteheadFull":       0,
    "noteheadHalf":       1,
    "noteheadWhole":      2,
    "noteheadFullSmall":  0,   # grace notes → treat as full notehead
    "noteheadHalfSmall":  1,
    "gClef":              3,
    "fClef":              4,
    "cClef":              5,
    "rest8th":            6,
    "restQuarter":        7,
    "restHalf":           8,
    "restWhole":          9,
    "accidentalSharp":   10,
    "accidentalFlat":    11,
    "accidentalNatural": 12,
    "beam":              13,
    "stem":              14,
    # Alternate names found in some MUSCIMA++ versions
    "8thRest":            6,
    "quarterRest":        7,
    "halfRest":           8,
    "wholeRest":          9,
    "flag8thUp":         -1,   # not in our 15 classes, skip
    "flag8thDown":       -1,
}


# Map (source_class_name, target_class_name) pairs from MUSCIMA++ outlinks
# to our 5 relationship type indices (RELATIONSHIP_TYPES).
# This mapping considers both directions since outlinks in MUSCIMA++ can go
# notehead→stem or stem→notehead depending on annotation style.
def classify_relationship(src_class: str, tgt_class: str) -> int:
    """Determine relationship type index from source/target MUSCIMA++ class names.

    Returns:
        Index into RELATIONSHIP_TYPES: 0=no_relation, 1=stem_notehead,
        2=beam_notegroup, 3=slur_phrase, 4=tie_sustained
    """
    notehead_classes = {
        "noteheadFull", "noteheadHalf", "noteheadWhole",
        "noteheadFullSmall", "noteheadHalfSmall",
    }
    # stem ↔ notehead
    if (src_class in notehead_classes and tgt_class == "stem") or \
       (src_class == "stem" and tgt_class in notehead_classes):
        return 1  # stem_notehead

    # beam ↔ notehead
    if (src_class in notehead_classes and tgt_class == "beam") or \
       (src_class == "beam" and tgt_class in notehead_classes):
        return 2  # beam_notegroup

    # slur ↔ notehead
    if (src_class in notehead_classes and tgt_class == "slur") or \
       (src_class == "slur" and tgt_class in notehead_classes):
        return 3  # slur_phrase

    # tie ↔ notehead
    if (src_class in notehead_classes and tgt_class == "tie") or \
       (src_class == "tie" and tgt_class in notehead_classes):
        return 4  # tie_sustained

    return 0  # no_relation


class MUSCIMANode:
    """Parsed MUSCIMA++ node (symbol)."""
    __slots__ = ("node_id", "class_name", "top", "left", "width", "height", "outlinks")

    def __init__(self, node_id: int, class_name: str,
                 top: int, left: int, width: int, height: int,
                 outlinks: List[int]):
        self.node_id = node_id
        self.class_name = class_name
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.outlinks = outlinks


def parse_muscima_xml(xml_path: Path) -> List[MUSCIMANode]:
    """Parse a MUSCIMA++ XML annotation file into a list of MUSCIMANode objects."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    nodes: List[MUSCIMANode] = []
    for node_elem in root.findall(".//Node"):
        node_id = int(node_elem.find("Id").text)
        class_name = node_elem.find("ClassName").text

        top = int(node_elem.find("Top").text)
        left = int(node_elem.find("Left").text)
        width = int(node_elem.find("Width").text)
        height = int(node_elem.find("Height").text)

        outlinks_elem = node_elem.find("Outlinks")
        outlinks: List[int] = []
        if outlinks_elem is not None and outlinks_elem.text:
            outlinks = [int(x) for x in outlinks_elem.text.strip().split()]

        nodes.append(MUSCIMANode(node_id, class_name, top, left, width, height, outlinks))

    return nodes


def _estimate_staff_index(y_center: float, page_height: float, num_staffs: int = 4) -> int:
    """Simple heuristic: divide page height into equal regions for staff assignment."""
    region_height = page_height / max(num_staffs, 1)
    return min(int(y_center / region_height), num_staffs - 1)


def muscima_page_to_pyg_data(
    xml_path: Path,
    node_encoder: NodeFeatureEncoder,
    graph_constructor: Optional[GraphConstructor] = None,
    num_staffs: int = 4,
    k_neighbors: int = 8,
) -> Optional[Data]:
    """Convert one MUSCIMA++ XML page to a PyG Data object for GNN training.

    Steps:
      1. Parse XML → all nodes
      2. Filter to our 15-class subset
      3. Normalize bounding boxes and create Detection objects
      4. Build candidate edges (lean k-NN + vertical overlap)
      5. Label edges by matching against GT outlinks
      6. Encode node features
      7. Return Data(x, edge_index, edge_type, edge_label)
    """
    all_nodes = parse_muscima_xml(xml_path)
    if not all_nodes:
        return None

    # Find page extent for coordinate normalization
    max_x = max(n.left + n.width for n in all_nodes)
    max_y = max(n.top + n.height for n in all_nodes)
    page_width = max_x * 1.05
    page_height = max_y * 1.05

    # Filter to our 15-class subset and build Detection objects
    # Keep a map old_node_id → new_index for edge labeling
    id_to_node: Dict[int, MUSCIMANode] = {n.node_id: n for n in all_nodes}
    detections: List[Detection] = []
    kept_node_ids: List[int] = []  # original MUSCIMA++ IDs of kept nodes

    for node in all_nodes:
        class_id = MUSCIMA_CLASS_MAP.get(node.class_name, -1)
        if class_id < 0:
            continue  # skip classes not in our 15-class set

        # Normalize bbox to [0, 1]
        x_center = (node.left + node.width / 2) / page_width
        y_center = (node.top + node.height / 2) / page_height
        w_norm = node.width / page_width
        h_norm = node.height / page_height

        staff_idx = _estimate_staff_index(node.top + node.height / 2, page_height, num_staffs)
        class_name = SYMBOL_CLASSES[class_id]

        detections.append(Detection(
            class_id=class_id,
            class_name=class_name,
            x=x_center,
            y=y_center,
            w=w_norm,
            h=h_norm,
            confidence=1.0,  # ground truth
            staff_index=staff_idx,
        ))
        kept_node_ids.append(node.node_id)

    if len(detections) < 2:
        return None

    # Build a set of GT relationships between kept nodes (both directions)
    # Map: (kept_index_src, kept_index_tgt) → relationship_type_id
    kept_id_to_idx = {nid: idx for idx, nid in enumerate(kept_node_ids)}
    gt_edges: Dict[Tuple[int, int], int] = {}

    for idx, nid in enumerate(kept_node_ids):
        node = id_to_node[nid]
        for tgt_id in node.outlinks:
            tgt_idx = kept_id_to_idx.get(tgt_id)
            if tgt_idx is None:
                continue  # target not in our 15-class subset
            rel_type = classify_relationship(node.class_name, id_to_node[tgt_id].class_name)
            if rel_type > 0:  # only record non-trivial relationships
                gt_edges[(idx, tgt_idx)] = rel_type
                # Also store reverse direction for undirected matching
                gt_edges[(tgt_idx, idx)] = rel_type

    # Build candidate edges using lean construction for training
    edge_index, edge_type = _build_training_edges(detections, k=k_neighbors)

    if edge_index.shape[1] == 0:
        return None

    # Assign edge labels by matching candidate edges against GT
    num_edges = edge_index.shape[1]
    edge_labels = torch.zeros(num_edges, dtype=torch.long)

    for e in range(num_edges):
        src = edge_index[0, e].item()
        tgt = edge_index[1, e].item()
        edge_labels[e] = gt_edges.get((src, tgt), 0)

    # Encode node features
    with torch.no_grad():
        x = node_encoder(detections)

    # Also store spatial positions for relative position computation
    # Store as a tensor for efficiency during training
    positions = torch.tensor(
        [[d.x, d.y, d.w, d.h] for d in detections],
        dtype=torch.float32,
    )

    data = Data(
        x=x,
        edge_index=edge_index,
        edge_type=edge_type,
        edge_label=edge_labels,
    )
    # Attach detections list for relative position computation in forward()
    data.detections = detections
    data.positions = positions
    data.page_name = xml_path.stem

    return data


def load_muscima_dataset(
    xml_dir: Path,
    val_ratio: float = 0.2,
    k_neighbors: int = 5,
    num_staffs: int = 4,
    seed: int = 42,
) -> Tuple[List[Data], List[Data]]:
    """Load all MUSCIMA++ XML files and split into train/val PyG Data lists.

    Args:
        xml_dir: Directory containing MUSCIMA++ XML annotation files
        val_ratio: Fraction of pages for validation (default 0.2)
        k_neighbors: Number of k-NN neighbors for graph construction
        num_staffs: Estimated number of staves per page for staff assignment
        seed: Random seed for reproducible train/val split

    Returns:
        (train_data, val_data): Lists of PyG Data objects
    """
    xml_files = sorted(xml_dir.glob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"No XML files found in {xml_dir}")

    print(f"Found {len(xml_files)} MUSCIMA++ XML files in {xml_dir}")

    node_encoder = NodeFeatureEncoder(num_classes=15, embed_dim=4)

    all_data: List[Data] = []
    total_nodes = 0
    total_edges = 0
    total_positive_edges = 0

    for xml_path in xml_files:
        data = muscima_page_to_pyg_data(
            xml_path, node_encoder, num_staffs=num_staffs,
            k_neighbors=k_neighbors,
        )
        if data is not None:
            all_data.append(data)
            total_nodes += data.x.shape[0]
            total_edges += data.edge_index.shape[1]
            total_positive_edges += (data.edge_label > 0).sum().item()
            print(f"  {xml_path.stem}: {data.x.shape[0]} nodes, "
                  f"{data.edge_index.shape[1]} edges, "
                  f"{(data.edge_label > 0).sum().item()} positive")

    if not all_data:
        raise ValueError("No valid pages loaded - check XML files and class mapping")

    print(f"\nDataset summary:")
    print(f"  Pages:  {len(all_data)}")
    print(f"  Nodes:  {total_nodes}")
    print(f"  Edges:  {total_edges}")
    print(f"  Positive edges (non-no_relation): {total_positive_edges}")
    print(f"  Positive ratio: {total_positive_edges / max(total_edges, 1):.3f}")

    # Distribution of edge labels
    all_labels = torch.cat([d.edge_label for d in all_data])
    for i, name in enumerate(RELATIONSHIP_TYPES):
        count = (all_labels == i).sum().item()
        print(f"    {name}: {count} ({count / len(all_labels) * 100:.1f}%)")

    # Split into train/val
    random.seed(seed)
    indices = list(range(len(all_data)))
    random.shuffle(indices)
    val_count = max(1, int(len(all_data) * val_ratio))

    val_indices = set(indices[:val_count])
    train_data = [all_data[i] for i in range(len(all_data)) if i not in val_indices]
    val_data = [all_data[i] for i in val_indices]

    print(f"\nSplit: {len(train_data)} train, {len(val_data)} val")
    return train_data, val_data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Load MUSCIMA++ data for GNN training")
    parser.add_argument("--xml-dir", type=Path, default=Path("MUSICMA_Sample"),
                        help="Directory with MUSCIMA++ XML files")
    parser.add_argument("--k", type=int, default=5, help="k for k-NN graph")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Validation split ratio")
    args = parser.parse_args()

    train_data, val_data = load_muscima_dataset(
        args.xml_dir, val_ratio=args.val_ratio, k_neighbors=args.k
    )
    print(f"\nTrain sample shapes:")
    d = train_data[0]
    print(f"  x: {d.x.shape}")
    print(f"  edge_index: {d.edge_index.shape}")
    print(f"  edge_type: {d.edge_type.shape}")
    print(f"  edge_label: {d.edge_label.shape}")
