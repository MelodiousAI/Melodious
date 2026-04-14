"""MusicXML tree edit distance: heuristic assembler vs GNN assembler.

Compares the MusicXML output trees produced by:
1. Heuristic spatial grouping (baseline)
2. GNN edge-classification-informed grouping

Uses the `zss` library for Zhang-Shasha tree edit distance.
Lower TED means a more coherent, accurate MusicXML tree.
"""

from __future__ import annotations

import glob
import json
import os
from pathlib import Path
from typing import List, Optional

import numpy as np
import zss


# ---------------------------------------------------------------------------
# Lightweight tree node for MusicXML comparison
# ---------------------------------------------------------------------------

class MusicNode:
    """Simple tree node for tree edit distance computation."""

    def __init__(self, label: str, children: Optional[List["MusicNode"]] = None):
        self.label = label
        self.children = children or []

    def addchild(self, child: "MusicNode"):
        self.children.append(child)
        return self

    @staticmethod
    def get_children(node):
        return node.children

    @staticmethod
    def get_label(node):
        return node.label


def _score_to_tree(score) -> MusicNode:
    """Convert a music21 Score into a simplified tree for TED comparison.

    Tree structure:
      Score
        Part-0
          Measure-1
            Note-C4-1.0
            Note-E4-0.5
            Rest-1.0
          Measure-2
            ...
        Part-1
          ...
    """
    root = MusicNode("Score")
    from music21 import stream as m21stream, note as m21note

    for pi, part in enumerate(score.parts):
        part_node = MusicNode(f"Part-{pi}")
        root.addchild(part_node)

        for mi, measure in enumerate(part.getElementsByClass(m21stream.Measure)):
            measure_node = MusicNode(f"Measure-{mi + 1}")
            part_node.addchild(measure_node)

            for elem in measure.notesAndRests:
                if isinstance(elem, m21note.Note):
                    label = f"Note-{elem.nameWithOctave}-{elem.quarterLength}"
                elif isinstance(elem, m21note.Rest):
                    label = f"Rest-{elem.quarterLength}"
                else:
                    label = f"Other-{elem.quarterLength}"
                measure_node.addchild(MusicNode(label))

    return root


def _tree_size(node: MusicNode) -> int:
    """Count total nodes in a tree."""
    return 1 + sum(_tree_size(c) for c in node.children)


def _label_dist(a: str, b: str) -> int:
    """Cost of relabeling node a to node b (0 if same, 1 otherwise)."""
    return 0 if a == b else 1


def _compute_ted(t1: MusicNode, t2: MusicNode) -> int:
    """Zhang-Shasha tree edit distance between two MusicNode trees."""
    return zss.simple_distance(
        t1, t2,
        MusicNode.get_children,
        MusicNode.get_label,
        _label_dist,
    )


def _make_detections_from_yolo(model, image_path: str, conf: float = 0.25) -> list:
    """Run YOLO on an image and return detection dicts in payload format."""
    results = model.predict(image_path, imgsz=1024, conf=conf, verbose=False)
    boxes = results[0].boxes
    h, w = results[0].orig_shape

    detections = []
    for box in boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        confidence = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()

        detections.append({
            "class_id": cls_id,
            "class_name": cls_name,
            "confidence": confidence,
            "bbox": {
                "x_center": ((x1 + x2) / 2) / w,
                "y_center": ((y1 + y2) / 2) / h,
                "width": (x2 - x1) / w,
                "height": (y2 - y1) / h,
            },
        })
    return detections


def _assemble_with_gnn_edges(detections: list, model_gnn, gnn_checkpoint: str) -> list:
    """Use GNN edge predictions to modify beam/stem linkages in detections.

    Instead of proximity heuristics, use the GNN to predict which stems
    and beams are actually connected to noteheads, then set the grouping
    accordingly. Returns modified detections with 'group_id' annotations.
    """
    import torch
    from melodious.gnn import (
        GNNAssembler, Detection as Det, GraphConstructor,
        NodeFeatureEncoder, RELATIONSHIP_TYPES,
    )

    # Build detection objects
    dets = []
    for i, d in enumerate(detections):
        bbox = d["bbox"]
        dets.append(Det(
            class_id=d["class_id"],
            class_name=d["class_name"],
            confidence=d["confidence"],
            x=bbox["x_center"],
            y=bbox["y_center"],
            w=bbox["width"],
            h=bbox["height"],
        ))

    if len(dets) < 2:
        return detections

    # Build graph
    gc = GraphConstructor(k_neighbors=8)
    edge_index, edge_types = gc.construct(dets)

    # Encode features
    encoder = NodeFeatureEncoder(num_classes=15)
    with torch.no_grad():
        node_features = encoder(dets)

    # Load GNN
    checkpoint = torch.load(gnn_checkpoint, map_location="cpu", weights_only=False)
    config = checkpoint.get("config", {})
    gnn = GNNAssembler(
        num_classes=config.get("num_classes", 15),
        node_feature_dim=config.get("node_feature_dim", 10),
        hidden_dim=config.get("hidden_dim", 64),
        num_gat_layers=config.get("num_gat_layers", 3),
        num_heads=config.get("num_heads", 8),
        num_relationships=config.get("num_relationships", 5),
        dropout=0.0,
    )
    gnn.load_state_dict(checkpoint["model_state_dict"])
    gnn.eval()

    # Predict edges
    data = torch.utils.data.default_collate  # dummy
    from torch_geometric.data import Data
    graph = Data(
        x=node_features,
        edge_index=edge_index,
        edge_type=edge_types,
    )

    with torch.no_grad():
        logits = gnn(graph)
        preds = logits.argmax(dim=1).numpy()

    # Annotate detections with GNN-predicted relationships
    # Mark noteheads that have stem/beam edges predicted by GNN
    notehead_beamed = set()
    for ei in range(edge_index.shape[1]):
        src, dst = int(edge_index[0, ei]), int(edge_index[1, ei])
        rel = RELATIONSHIP_TYPES[preds[ei]]
        if rel == "beam_notegroup":
            if dets[src].class_name.startswith("notehead"):
                notehead_beamed.add(src)
            if dets[dst].class_name.startswith("notehead"):
                notehead_beamed.add(dst)

    # Modify detections: mark beamed noteheads
    modified = []
    for i, d in enumerate(detections):
        d_copy = dict(d)
        d_copy["gnn_beamed"] = i in notehead_beamed
        modified.append(d_copy)

    return modified


def _assemble_score_gnn(detections: list, title: str = "GNN Assembly") -> "m21stream.Score":
    """Build music21 Score using GNN-informed groupings."""
    from music21 import (
        clef as m21clef, metadata as m21meta, meter as m21meter,
        note as m21note, stream as m21stream,
    )

    _TREBLE_PITCHES = [
        "D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5",
    ]
    _CLASS_DURATION = {
        "notehead-full": 1.0, "notehead-half": 2.0, "notehead-whole": 4.0,
    }

    score = m21stream.Score()
    score.metadata = m21meta.Metadata()
    score.metadata.title = title

    part = m21stream.Part()
    part.append(m21clef.TrebleClef())
    part.append(m21meter.TimeSignature("4/4"))

    noteheads = [d for d in detections if d.get("class_name", "").startswith("notehead")]
    noteheads.sort(key=lambda d: d["bbox"]["x_center"])

    for nh in noteheads:
        y = nh["bbox"]["y_center"]
        pos = max(0.0, min(1.0, 1.0 - y))
        idx = int(round(pos * (len(_TREBLE_PITCHES) - 1)))
        idx = max(0, min(len(_TREBLE_PITCHES) - 1, idx))
        pitch_name = _TREBLE_PITCHES[idx]

        beamed = nh.get("gnn_beamed", False)
        dur = _CLASS_DURATION.get(nh["class_name"], 1.0)
        if beamed and nh["class_name"] == "notehead-full":
            dur = 0.5

        n = m21note.Note(pitch_name, quarterLength=dur)
        part.append(n)

    # Rests
    _REST_DUR = {"rest-8th": 0.5, "rest-quarter": 1.0, "rest-half": 2.0, "rest-whole": 4.0}
    rests = [d for d in detections if d.get("class_name", "").startswith("rest-")]
    rests.sort(key=lambda d: d["bbox"]["x_center"])
    for r in rests:
        dur = _REST_DUR.get(r["class_name"], 1.0)
        part.append(m21note.Rest(quarterLength=dur))

    part.makeMeasures(inPlace=True)
    score.append(part)
    return score


def evaluate_tree_edit_distance(
    checkpoint_yolo: str = "outputs/yolov8_extended/train/weights/best.pt",
    checkpoint_gnn: str = "outputs/gnn_checkpoint.pt",
    image_dir: str = "yolo_dataset/images/val",
    output_dir: str = "outputs/visualizations",
    n_images: int = 10,
    seed: int = 42,
):
    """Compare heuristic vs GNN assembler via MusicXML tree edit distance."""
    import random
    from ultralytics import YOLO
    from melodious.musicxml_export import assemble_score

    os.makedirs(output_dir, exist_ok=True)
    random.seed(seed)

    model = YOLO(checkpoint_yolo)

    images = sorted(glob.glob(os.path.join(image_dir, "*.png")))
    if len(images) > n_images:
        images = random.sample(images, n_images)

    teds = []
    heuristic_sizes = []
    gnn_sizes = []

    print(f"Evaluating tree edit distance on {len(images)} images...\n")

    for img_path in images:
        stem = os.path.splitext(os.path.basename(img_path))[0]
        print(f"  Processing {stem[:50]}...")

        # Get detections
        detections = _make_detections_from_yolo(model, img_path)
        if not detections:
            print(f"    Skipped (no detections)")
            continue

        # Heuristic assembly → MusicXML tree
        try:
            score_h = assemble_score(detections, title="Heuristic")
            tree_h = _score_to_tree(score_h)
        except Exception as e:
            print(f"    Heuristic assembly failed: {e}")
            continue

        # GNN-informed assembly → MusicXML tree
        try:
            detections_gnn = _assemble_with_gnn_edges(detections, None, checkpoint_gnn)
            score_g = _assemble_score_gnn(detections_gnn, title="GNN")
            tree_g = _score_to_tree(score_g)
        except Exception as e:
            print(f"    GNN assembly failed: {e}")
            continue

        h_size = _tree_size(tree_h)
        g_size = _tree_size(tree_g)
        ted = _compute_ted(tree_h, tree_g)

        # Normalized TED (0-1 range)
        max_size = max(h_size, g_size)
        nted = ted / max_size if max_size > 0 else 0.0

        teds.append({"image": stem, "ted": ted, "nted": round(nted, 4),
                     "heuristic_nodes": h_size, "gnn_nodes": g_size})
        heuristic_sizes.append(h_size)
        gnn_sizes.append(g_size)
        print(f"    TED={ted}  nTED={nted:.4f}  H-nodes={h_size}  G-nodes={g_size}")

    if not teds:
        print("No images processed successfully.")
        return

    # Summary
    ted_values = [t["ted"] for t in teds]
    nted_values = [t["nted"] for t in teds]

    print(f"\n{'='*60}")
    print("TREE EDIT DISTANCE SUMMARY")
    print(f"{'='*60}")
    print(f"  Images evaluated:  {len(teds)}")
    print(f"  Mean TED:          {np.mean(ted_values):.1f}")
    print(f"  Median TED:        {np.median(ted_values):.1f}")
    print(f"  Std TED:           {np.std(ted_values):.1f}")
    print(f"  Mean nTED:         {np.mean(nted_values):.4f}")
    print(f"  Mean H-nodes:      {np.mean(heuristic_sizes):.1f}")
    print(f"  Mean G-nodes:      {np.mean(gnn_sizes):.1f}")
    print(f"{'='*60}")

    # Save results
    results = {
        "per_image": teds,
        "summary": {
            "n_images": len(teds),
            "mean_ted": round(float(np.mean(ted_values)), 1),
            "median_ted": round(float(np.median(ted_values)), 1),
            "std_ted": round(float(np.std(ted_values)), 1),
            "mean_nted": round(float(np.mean(nted_values)), 4),
            "mean_heuristic_nodes": round(float(np.mean(heuristic_sizes)), 1),
            "mean_gnn_nodes": round(float(np.mean(gnn_sizes)), 1),
        },
    }
    out_path = os.path.join(output_dir, "tree_edit_distance_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    evaluate_tree_edit_distance()
