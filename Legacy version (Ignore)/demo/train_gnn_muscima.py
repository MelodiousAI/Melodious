"""
Train GNN Assembler on MUSCIMA++ Data

Entry point for training the GNNAssembler edge classifier on MUSCIMA++ pages.
Loads data via gnn_data_loader, trains using train_gnn() from gnn.py,
saves best checkpoint, and prints evaluation metrics.

Usage:
    # Train on the 5 sample XMLs (quick test)
    python train_gnn_muscima.py --xml-dir MUSICMA_Sample --epochs 30

    # Train on full MUSCIMA++ dataset
    python train_gnn_muscima.py --xml-dir data/raw/MUSCIMA-pp_v2.0/data/annotations --epochs 50

    # Resume from a checkpoint
    python train_gnn_muscima.py --xml-dir MUSICMA_Sample --resume outputs/gnn_checkpoint.pt
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from collections import Counter

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

from melodious.gnn import GNNAssembler, RELATIONSHIP_TYPES, SYMBOL_CLASSES
from melodious.gnn_data_loader import load_muscima_dataset


def compute_per_class_metrics(model, data_list, device):
    """Compute per-relationship-type precision, recall, F1 on a dataset."""
    model.eval()
    num_classes = len(RELATIONSHIP_TYPES)
    tp = [0] * num_classes
    fp = [0] * num_classes
    fn = [0] * num_classes

    with torch.no_grad():
        for data in data_list:
            data = data.to(device)
            edge_logits = model(data)
            preds = edge_logits.argmax(dim=-1)
            labels = data.edge_label

            for c in range(num_classes):
                pred_c = (preds == c)
                label_c = (labels == c)
                tp[c] += (pred_c & label_c).sum().item()
                fp[c] += (pred_c & ~label_c).sum().item()
                fn[c] += (~pred_c & label_c).sum().item()

    metrics = {}
    for c in range(num_classes):
        precision = tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) > 0 else 0.0
        recall = tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        metrics[RELATIONSHIP_TYPES[c]] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tp": tp[c],
            "fp": fp[c],
            "fn": fn[c],
        }
    return metrics


def _sample_edges(data: "Data", neg_ratio: float = 3.0) -> torch.Tensor:
    """Create an edge mask that keeps all positive edges and subsamples negatives.

    For training, we keep ALL positive edges (label > 0) and sample
    neg_ratio * num_positive negative edges (label == 0). This dramatically
    reduces the class imbalance from ~70:1 down to neg_ratio:1.

    Returns:
        Boolean mask of shape (num_edges,) indicating which edges to use.
    """
    labels = data.edge_label
    pos_mask = labels > 0
    neg_mask = labels == 0

    num_pos = pos_mask.sum().item()
    num_neg = neg_mask.sum().item()

    if num_pos == 0:
        # No positive edges — sample a small fixed number of negatives
        num_keep_neg = min(1000, num_neg)
        neg_indices = torch.where(neg_mask)[0]
        perm = torch.randperm(len(neg_indices))[:num_keep_neg]
        mask = torch.zeros_like(labels, dtype=torch.bool)
        mask[neg_indices[perm]] = True
        return mask

    # Keep all positives, subsample negatives
    num_keep_neg = min(int(num_pos * neg_ratio), num_neg)
    neg_indices = torch.where(neg_mask)[0]
    perm = torch.randperm(len(neg_indices))[:num_keep_neg]

    mask = pos_mask.clone()
    mask[neg_indices[perm]] = True
    return mask


def train_gnn_with_logging(
    model: GNNAssembler,
    train_data,
    val_data,
    epochs: int = 50,
    lr: float = 0.001,
    weight_decay: float = 1e-5,
    device: str = "cuda",
    save_dir: Path = Path("outputs"),
    patience: int = 10,
    neg_ratio: float = 3.0,
):
    """Train the GNN with detailed logging, checkpointing, and early stopping.

    Uses negative edge subsampling to handle the extreme class imbalance
    (typically >98% of candidate edges are no_relation). For each training
    page, all positive edges are kept while negative edges are subsampled
    to neg_ratio * num_positive.

    Args:
        model: GNNAssembler model
        train_data: List of PyG Data objects for training
        val_data: List of PyG Data objects for validation
        epochs: Number of training epochs
        lr: Learning rate
        weight_decay: L2 regularization
        device: Device to train on
        save_dir: Directory to save checkpoints and logs
        patience: Early stopping patience (epochs without val improvement)
        neg_ratio: Ratio of negative to positive edges during training

    Returns:
        Dictionary with training history and best metrics
    """
    save_dir.mkdir(parents=True, exist_ok=True)
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5, min_lr=1e-6
    )

    # Class weights: still helpful on top of subsampling to fine-tune balance
    class_weights = torch.tensor([0.5, 3.0, 4.0, 2.0, 2.0], device=device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    history = {
        "train_loss": [], "val_loss": [],
        "train_acc": [], "val_acc": [],
        "lr": [],
    }
    best_val_loss = float("inf")
    best_val_acc = 0.0
    best_epoch = 0
    epochs_no_improve = 0

    print(f"\n{'='*70}")
    print(f"Training GNN Assembler")
    print(f"  Model params:    {sum(p.numel() for p in model.parameters()):,}")
    print(f"  Train pages:     {len(train_data)}")
    print(f"  Val pages:       {len(val_data)}")
    print(f"  Device:          {device}")
    print(f"  Epochs:          {epochs}")
    print(f"  LR:              {lr}")
    print(f"  Class weights:   {class_weights.tolist()}")
    print(f"  Neg ratio:       {neg_ratio}")
    print(f"  Save dir:        {save_dir}")
    print(f"{'='*70}\n")

    start_time = time.time()

    for epoch in range(epochs):
        # --- Training ---
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for data in train_data:
            data = data.to(device)
            optimizer.zero_grad()

            edge_logits = model(data)

            # Negative edge subsampling: keep all positive, subsample negative
            mask = _sample_edges(data, neg_ratio=neg_ratio)
            masked_logits = edge_logits[mask]
            masked_labels = data.edge_label[mask]

            loss = criterion(masked_logits, masked_labels)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            train_loss += loss.item()
            preds = masked_logits.argmax(dim=-1)
            train_correct += (preds == masked_labels).sum().item()
            train_total += masked_labels.shape[0]

        # --- Validation ---
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for data in val_data:
                data = data.to(device)
                edge_logits = model(data)

                # Use same sampling for consistent val metrics
                mask = _sample_edges(data, neg_ratio=neg_ratio)
                masked_logits = edge_logits[mask]
                masked_labels = data.edge_label[mask]

                loss = criterion(masked_logits, masked_labels)

                val_loss += loss.item()
                preds = masked_logits.argmax(dim=-1)
                val_correct += (preds == masked_labels).sum().item()
                val_total += masked_labels.shape[0]

        avg_train_loss = train_loss / len(train_data)
        avg_val_loss = val_loss / len(val_data) if val_data else 0
        train_acc = train_correct / train_total if train_total > 0 else 0
        val_acc = val_correct / val_total if val_total > 0 else 0

        history["train_loss"].append(avg_train_loss)
        history["val_loss"].append(avg_val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)
        history["lr"].append(optimizer.param_groups[0]["lr"])

        scheduler.step(avg_val_loss)

        # Check for improvement
        improved = ""
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_val_acc = val_acc
            best_epoch = epoch + 1
            epochs_no_improve = 0
            improved = " ← BEST"

            # Save best checkpoint
            checkpoint = {
                "model_state_dict": model.state_dict(),
                "epoch": epoch + 1,
                "val_loss": avg_val_loss,
                "val_acc": val_acc,
                "train_loss": avg_train_loss,
                "train_acc": train_acc,
                "config": {
                    "num_classes": model.num_classes,
                    "hidden_dim": model.hidden_dim,
                    "num_relationships": model.num_relationships,
                    "num_gat_layers": len(model.gat_layers),
                    "num_heads": model.gat_layers[0].heads if model.gat_layers else 8,
                    "symbol_classes": SYMBOL_CLASSES,
                    "relationship_types": RELATIONSHIP_TYPES,
                },
            }
            torch.save(checkpoint, save_dir / "gnn_checkpoint.pt")
        else:
            epochs_no_improve += 1

        print(
            f"Epoch {epoch+1:3d}/{epochs} | "
            f"Train Loss: {avg_train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {avg_val_loss:.4f} Acc: {val_acc:.4f} | "
            f"LR: {optimizer.param_groups[0]['lr']:.1e}{improved}"
        )

        # Early stopping
        if epochs_no_improve >= patience:
            print(f"\nEarly stopping after {patience} epochs without improvement.")
            break

    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"Training complete in {elapsed:.1f}s")
    print(f"Best epoch: {best_epoch} (val_loss={best_val_loss:.4f}, val_acc={best_val_acc:.4f})")

    # Load best model for final evaluation
    best_ckpt = torch.load(save_dir / "gnn_checkpoint.pt", map_location=device, weights_only=False)
    model.load_state_dict(best_ckpt["model_state_dict"])

    # Per-class evaluation on val set
    print(f"\nPer-relationship metrics on validation set:")
    print(f"{'Relationship':<20s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s} {'TP':>8s} {'FP':>8s} {'FN':>8s}")
    print("-" * 70)

    val_metrics = compute_per_class_metrics(model, val_data, device)
    for rel_name, m in val_metrics.items():
        print(
            f"{rel_name:<20s} {m['precision']:>10.4f} {m['recall']:>10.4f} "
            f"{m['f1']:>10.4f} {m['tp']:>8d} {m['fp']:>8d} {m['fn']:>8d}"
        )

    # Also evaluate on train set
    print(f"\nPer-relationship metrics on training set:")
    print(f"{'Relationship':<20s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s}")
    print("-" * 50)

    train_metrics = compute_per_class_metrics(model, train_data, device)
    for rel_name, m in train_metrics.items():
        print(f"{rel_name:<20s} {m['precision']:>10.4f} {m['recall']:>10.4f} {m['f1']:>10.4f}")

    # Save training results
    results = {
        "history": history,
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "best_val_acc": best_val_acc,
        "val_metrics": val_metrics,
        "train_metrics": train_metrics,
        "elapsed_seconds": elapsed,
        "model_params": sum(p.numel() for p in model.parameters()),
    }
    with open(save_dir / "gnn_training_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nCheckpoint saved to: {save_dir / 'gnn_checkpoint.pt'}")
    print(f"Results saved to:    {save_dir / 'gnn_training_results.json'}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Train GNN Assembler on MUSCIMA++ data")
    parser.add_argument("--xml-dir", type=Path, default=Path("MUSICMA_Sample"),
                        help="Directory with MUSCIMA++ XML annotation files")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--hidden-dim", type=int, default=64, help="GNN hidden dimension")
    parser.add_argument("--num-layers", type=int, default=3, help="Number of GAT layers")
    parser.add_argument("--num-heads", type=int, default=8, help="Number of attention heads")
    parser.add_argument("--k", type=int, default=5, help="k for k-NN graph construction")
    parser.add_argument("--val-ratio", type=float, default=0.2, help="Validation split ratio")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda/cpu)")
    parser.add_argument("--save-dir", type=Path, default=Path("outputs"), help="Checkpoint dir")
    parser.add_argument("--resume", type=Path, default=None, help="Resume from checkpoint")
    parser.add_argument("--patience", type=int, default=10, help="Early stopping patience")
    parser.add_argument("--neg-ratio", type=float, default=3.0,
                        help="Ratio of negative to positive edges during training")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    # Set seeds for reproducibility
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    # Determine device
    if args.device:
        device = args.device
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    print(f"Using device: {device}")

    # Load dataset
    print(f"\nLoading MUSCIMA++ data from: {args.xml_dir}")
    train_data, val_data = load_muscima_dataset(
        args.xml_dir,
        val_ratio=args.val_ratio,
        k_neighbors=args.k,
        seed=args.seed,
    )

    # Create model
    model = GNNAssembler(
        num_classes=15,
        hidden_dim=args.hidden_dim,
        num_gat_layers=args.num_layers,
        num_heads=args.num_heads,
        num_relationships=5,
    )
    print(f"\nModel: GNNAssembler")
    print(f"  Parameters:      {sum(p.numel() for p in model.parameters()):,}")
    print(f"  Hidden dim:      {args.hidden_dim}")
    print(f"  GAT layers:      {args.num_layers}")
    print(f"  Attention heads: {args.num_heads}")

    # Resume from checkpoint if specified
    if args.resume and args.resume.exists():
        print(f"\nResuming from: {args.resume}")
        ckpt = torch.load(args.resume, map_location=device, weights_only=False)
        model.load_state_dict(ckpt["model_state_dict"])
        print(f"  Loaded epoch {ckpt['epoch']}, val_acc={ckpt.get('val_acc', 'N/A')}")

    # Train
    results = train_gnn_with_logging(
        model=model,
        train_data=train_data,
        val_data=val_data,
        epochs=args.epochs,
        lr=args.lr,
        device=device,
        save_dir=args.save_dir,
        patience=args.patience,
        neg_ratio=args.neg_ratio,
    )


if __name__ == "__main__":
    main()
