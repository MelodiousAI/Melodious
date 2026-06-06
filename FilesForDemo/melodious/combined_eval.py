"""End-to-end evaluation of the YOLO + GNN pipeline.

Evaluates the combined pipeline using MUSCIMA++ validation data:
1. Uses GT detections (simulating perfect YOLO detection) to measure GNN assembly quality
2. Combines with measured YOLO detection metrics for overall pipeline F1 estimate

The combined F1 is estimated as:
  F1_combined ≈ F1_detection × F1_assembly

This approximation is justified because detection errors propagate multiplicatively
through the assembly stage — a missed detection removes all its relationships.
"""

import json
import os
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import classification_report, f1_score
from torch_geometric.data import Data

from melodious.gnn import GNNAssembler, RELATIONSHIP_TYPES
from melodious.gnn_data_loader import load_muscima_dataset


def evaluate_gnn_on_val(
    model: GNNAssembler,
    val_data: list,
) -> dict:
    """Evaluate GNN edge classification on validation pages.

    Returns per-class precision, recall, F1 and overall metrics.
    """
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for data in val_data:
            edge_logits = model(data)
            preds = edge_logits.argmax(dim=1).cpu().numpy()
            labels = data.edge_label.cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels)

    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)

    # Per-class F1
    # Only evaluate classes that appear in the data
    present_classes = sorted(set(all_labels) | set(all_preds))
    target_names = [RELATIONSHIP_TYPES[i] for i in present_classes]

    report = classification_report(
        all_labels, all_preds,
        labels=present_classes,
        target_names=target_names,
        output_dict=True,
        zero_division=0,
    )

    # Overall metrics
    accuracy = (all_preds == all_labels).mean()
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    weighted_f1 = f1_score(all_labels, all_preds, average="weighted", zero_division=0)

    # Positive-only F1 (excluding no_relation)
    pos_mask = all_labels > 0
    if pos_mask.sum() > 0:
        pos_preds = all_preds[pos_mask]
        pos_labels = all_labels[pos_mask]
        pos_f1 = f1_score(pos_labels, pos_preds, average="weighted", zero_division=0)
        pos_accuracy = (pos_preds == pos_labels).mean()
    else:
        pos_f1 = 0.0
        pos_accuracy = 0.0

    return {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "positive_only_f1": float(pos_f1),
        "positive_only_accuracy": float(pos_accuracy),
        "per_class": report,
        "n_edges": len(all_preds),
        "n_positive": int(pos_mask.sum()),
    }


def estimate_combined_f1(
    detection_map50: float,
    assembly_weighted_f1: float,
) -> dict:
    """Estimate combined pipeline F1.

    The detection mAP50 measures how many symbols are correctly detected.
    The assembly F1 measures how well relationships are classified given detections.

    Combined F1 ≈ detection_quality × assembly_quality because:
    - Missed detections (1 - recall) remove all downstream relationships
    - False positives add noise edges (most classified as no_relation by GNN)
    """
    combined_f1 = detection_map50 * assembly_weighted_f1
    return {
        "detection_mAP50": detection_map50,
        "assembly_weighted_f1": assembly_weighted_f1,
        "estimated_combined_f1": combined_f1,
        "note": "Conservative lower bound — assumes detection errors fully propagate",
    }


def main():
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    xml_dir = Path("data/muscima-pp/v2.0/data/annotations")
    checkpoint_path = "outputs/gnn_checkpoint.pt"

    # Load model
    print("Loading GNN checkpoint...")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    config = checkpoint.get("config", {})

    model = GNNAssembler(
        num_classes=config.get("num_classes", 15),
        node_feature_dim=config.get("node_feature_dim", 10),
        hidden_dim=config.get("hidden_dim", 64),
        num_gat_layers=config.get("num_gat_layers", 3),
        num_heads=config.get("num_heads", 8),
        num_relationships=config.get("num_relationships", 5),
        dropout=0.0,
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model loaded - {n_params:,} parameters")

    # Load validation data
    print("\nLoading MUSCIMA++ validation data...")
    _, val_data = load_muscima_dataset(xml_dir, val_ratio=0.2, seed=42)
    print(f"  {len(val_data)} validation pages")

    # Evaluate GNN
    print("\nEvaluating GNN assembly on validation set...")
    gnn_results = evaluate_gnn_on_val(model, val_data)

    print(f"\n{'='*60}")
    print("GNN ASSEMBLY EVALUATION - MUSCIMA++ Val Set")
    print(f"{'='*60}")
    print(f"  Overall accuracy:      {gnn_results['accuracy']:.4f}")
    print(f"  Weighted F1:           {gnn_results['weighted_f1']:.4f}")
    print(f"  Macro F1:              {gnn_results['macro_f1']:.4f}")
    print(f"  Positive-only F1:      {gnn_results['positive_only_f1']:.4f}")
    print(f"  Total edges evaluated: {gnn_results['n_edges']}")
    print(f"  Positive edges:        {gnn_results['n_positive']}")

    print(f"\nPer-class breakdown:")
    for cls_name in RELATIONSHIP_TYPES:
        if cls_name in gnn_results["per_class"]:
            info = gnn_results["per_class"][cls_name]
            p = info.get("precision", 0)
            r = info.get("recall", 0)
            f = info.get("f1-score", 0)
            s = int(info.get("support", 0))
            print(f"  {cls_name:20s}  P={p:.3f}  R={r:.3f}  F1={f:.3f}  (n={s})")

    # Estimate combined F1
    print(f"\n{'='*60}")
    print("COMBINED PIPELINE F1 ESTIMATE")
    print(f"{'='*60}")

    # Using YOLOv8s best metrics
    detection_map50 = 0.652
    combined = estimate_combined_f1(detection_map50, gnn_results["weighted_f1"])

    print(f"  Detection mAP50 (YOLOv8s):    {combined['detection_mAP50']:.3f}")
    print(f"  Assembly weighted F1 (GNN):    {combined['assembly_weighted_f1']:.3f}")
    print(f"  Estimated combined F1:         {combined['estimated_combined_f1']:.3f}")
    print(f"  Target:                        >= 0.75")
    target_met = combined["estimated_combined_f1"] >= 0.75
    status_txt = "MET" if target_met else "Below target"
    print(f"  Status:                        {status_txt}")

    if not target_met:
        # Calculate what detection mAP50 would be needed
        needed_map = 0.75 / gnn_results["weighted_f1"] if gnn_results["weighted_f1"] > 0 else float("inf")
        print(f"\n  Note: To reach combined F1 >= 0.75, detection mAP50 would need to be >= {needed_map:.3f}")
        print(f"  Current gap: {0.75 - combined['estimated_combined_f1']:.3f}")

    # Save full results
    output_path = os.path.join(output_dir, "combined_eval_results.json")
    full_results = {
        "gnn_assembly": gnn_results,
        "combined_estimate": combined,
    }
    with open(output_path, "w") as f:
        json.dump(full_results, f, indent=2, default=str)
    print(f"\nFull results saved to {output_path}")


if __name__ == "__main__":
    main()
