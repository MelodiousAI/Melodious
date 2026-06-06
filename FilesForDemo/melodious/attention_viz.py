"""GAT attention weight visualization overlay on MUSCIMA++ pages.

Loads the trained GNN checkpoint, runs a forward pass on sample MUSCIMA++ pages
with attention weight extraction, and renders arrows between connected nodes
with thickness proportional to attention strength.
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import torch
from torch_geometric.data import Data

from melodious.gnn import GNNAssembler, NodeFeatureEncoder, RELATIONSHIP_TYPES
from melodious.gnn_data_loader import load_muscima_dataset


RELATIONSHIP_COLORS = {
    0: "#9E9E9E",    # no_relation — gray
    1: "#4CAF50",    # stem_notehead — green
    2: "#2196F3",    # beam_notegroup — blue
    3: "#FF9800",    # staff_symbol — orange
    4: "#9C27B0",    # accidental_note — purple
}


def extract_attention_weights(model: GNNAssembler, data: Data):
    """Run forward pass and extract GAT layer attention weights.

    Returns:
        edge_logits: (E, num_relationships) predicted relationship logits
        attention_weights: list of (edge_index_i, alpha_i) for each GAT layer
    """
    model.eval()
    attention_layers = []

    with torch.no_grad():
        x = data.x
        edge_index = data.edge_index

        # Project
        x = model.input_proj(x)

        # GAT layers with attention extraction
        for gat_layer in model.gat_layers:
            x, (ei, alpha) = gat_layer(x, edge_index, return_attention_weights=True)
            x = torch.nn.functional.elu(x)
            attention_layers.append((ei.cpu(), alpha.cpu()))

        # Get predicted relationships
        node_embeddings = model.node_proj(x)
        src_embeds = node_embeddings[data.edge_index[0]]
        tgt_embeds = node_embeddings[data.edge_index[1]]
        edge_type_embeds = model.edge_type_embedding(data.edge_type)
        rel_pos = torch.zeros((data.edge_index.shape[1], 4), device=x.device)
        edge_features = torch.cat([src_embeds, tgt_embeds, edge_type_embeds, rel_pos], dim=1)
        edge_logits = model.edge_classifier(edge_features).cpu()

    return edge_logits, attention_layers


def render_attention_overlay(
    data: Data,
    edge_logits: torch.Tensor,
    attention_layers: list,
    output_path: str,
    page_name: str = "MUSCIMA++ Page",
    top_k_edges: int = 50,
):
    """Render an attention overlay showing predicted relationships.

    Shows:
    - Nodes as circles (sized by detection confidence)
    - Predicted relationship arrows (colored by type, thickness by confidence)
    - Last-layer attention weights as background edges
    """
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # Extract node positions (x, y from features — positions 4,5 in encoded features)
    # Since we use NodeFeatureEncoder, x features are encoded. We need positions.
    # Use x_center, y_center from the original features if available
    if hasattr(data, 'positions') and data.positions is not None:
        positions = data.positions.numpy()
    else:
        # Approximate from node features (class_embed[4] + bbox[4] + conf[1] + staff[1])
        # bbox features are at indices 4,5,6,7 (x,y,w,h)
        positions = data.x[:, 4:6].numpy() if data.x.shape[1] >= 6 else np.random.rand(data.x.shape[0], 2)

    # Normalize positions for display
    if len(positions) > 0:
        pos_min = positions.min(axis=0)
        pos_max = positions.max(axis=0)
        pos_range = pos_max - pos_min
        pos_range[pos_range == 0] = 1
        positions = (positions - pos_min) / pos_range

    # --- Panel 1: Attention weights from last GAT layer ---
    ax = axes[0]
    ax.set_title(f"GAT Attention Weights (Last Layer)\n{page_name}", fontsize=12, fontweight="bold")

    last_ei, last_alpha = attention_layers[-1]
    # Average across heads
    avg_alpha = last_alpha.mean(dim=1).numpy()

    # Draw attention edges (only top-k by weight)
    sorted_indices = np.argsort(avg_alpha)[-top_k_edges:]
    max_alpha = avg_alpha[sorted_indices].max() if len(sorted_indices) > 0 else 1

    for idx in sorted_indices:
        src, tgt = int(last_ei[0, idx]), int(last_ei[1, idx])
        if src < len(positions) and tgt < len(positions):
            weight = avg_alpha[idx] / max_alpha
            ax.plot(
                [positions[src, 0], positions[tgt, 0]],
                [positions[src, 1], positions[tgt, 1]],
                color="#FF5722", alpha=float(weight * 0.7 + 0.1),
                linewidth=float(weight * 3 + 0.5),
            )

    # Draw nodes
    ax.scatter(positions[:, 0], positions[:, 1], s=30, c="#333333", zorder=5, edgecolors="white", linewidths=0.5)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(1.05, -0.05)  # Invert y for image-like coords
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.1)

    # --- Panel 2: Predicted relationships ---
    ax = axes[1]
    ax.set_title(f"Predicted Relationships\n{page_name}", fontsize=12, fontweight="bold")

    preds = edge_logits.argmax(dim=1).numpy()
    pred_conf = torch.softmax(edge_logits, dim=1).max(dim=1).values.numpy()

    # Draw predicted relationship edges (non-zero relationships only)
    for i in range(len(preds)):
        if preds[i] == 0:  # Skip no_relation
            continue
        src = int(data.edge_index[0, i])
        tgt = int(data.edge_index[1, i])
        if src < len(positions) and tgt < len(positions):
            color = RELATIONSHIP_COLORS.get(int(preds[i]), "#9E9E9E")
            conf = float(pred_conf[i])
            ax.annotate(
                "", xy=(positions[tgt, 0], positions[tgt, 1]),
                xytext=(positions[src, 0], positions[src, 1]),
                arrowprops=dict(
                    arrowstyle="->", color=color,
                    lw=conf * 2 + 0.5, alpha=conf * 0.7 + 0.2,
                ),
            )

    # Draw nodes
    ax.scatter(positions[:, 0], positions[:, 1], s=30, c="#333333", zorder=5, edgecolors="white", linewidths=0.5)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(1.05, -0.05)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.1)

    # Legend
    legend_handles = [
        mpatches.Patch(color=RELATIONSHIP_COLORS[i], label=RELATIONSHIP_TYPES[i])
        for i in range(1, 5)  # Skip no_relation
    ]
    ax.legend(handles=legend_handles, loc="lower right", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def main():
    output_dir = "outputs/visualizations"
    os.makedirs(output_dir, exist_ok=True)

    xml_dir = Path("data/muscima-pp/v2.0/data/annotations")
    checkpoint_path = "outputs/gnn_checkpoint.pt"

    # Load checkpoint
    print("Loading GNN checkpoint...")
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

    # Recreate model with config from checkpoint
    config = checkpoint.get("config", {})
    model = GNNAssembler(
        num_classes=config.get("num_classes", 15),
        node_feature_dim=config.get("node_feature_dim", 10),
        hidden_dim=config.get("hidden_dim", 64),
        num_gat_layers=config.get("num_gat_layers", 3),
        num_heads=config.get("num_heads", 8),
        num_relationships=config.get("num_relationships", 5),
        dropout=0.0,  # No dropout for inference
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    print("Model loaded successfully")

    # Load a few sample pages
    print("Loading MUSCIMA++ sample pages...")
    train_data, val_data = load_muscima_dataset(xml_dir, val_ratio=0.2, seed=42)

    # Use first 3 val pages
    sample_pages = val_data[:3]

    for i, data in enumerate(sample_pages):
        page_name = f"Val Page {i+1}"
        output_path = os.path.join(output_dir, f"gat_attention_page_{i+1}.png")
        print(f"Generating attention overlay for {page_name}...")

        edge_logits, attention_layers = extract_attention_weights(model, data)
        render_attention_overlay(
            data, edge_logits, attention_layers,
            output_path, page_name, top_k_edges=80,
        )
        print(f"  Saved to {output_path}")

    print(f"\nAll attention overlays saved to {output_dir}/")


if __name__ == "__main__":
    main()
