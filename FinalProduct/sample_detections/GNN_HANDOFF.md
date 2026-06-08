# GNN Assembler Handoff for Hassan

## Checkpoint Location

```
outputs/gnn_checkpoint.pt
```

## Model Architecture

- **Model class**: `melodious.gnn.GNNAssembler`
- **Parameters**: 606,553
- **Architecture**: 3-layer GAT (Graph Attention Network)
- **Attention heads**: 8 per layer
- **Hidden dimension**: 64
- **Input features**: 10-dimensional node features (class embedding 4d + spatial 5d + confidence 1d)
- **Output**: 5-class edge logits per candidate edge

## Training Summary

- **Dataset**: MUSCIMA++ v2.0, 140 annotated pages
- **Split**: 112 train / 28 val
- **Epochs**: 80 (best at epoch 79)
- **Training time**: ~4.5 minutes on RTX 3080
- **Final val accuracy**: 89.9%
- **Final val loss**: 0.2167

## Relationship Types (edge classes)

| ID | Name | Description | Val Precision | Val Recall | Val F1 |
|----|------|-------------|---------------|------------|--------|
| 0 | `no_relation` | No musical relationship | 0.992 | 0.891 | 0.939 |
| 1 | `stem_notehead` | Stem connects to notehead | 0.523 | 0.932 | 0.670 |
| 2 | `beam_notegroup` | Beam groups noteheads | 0.658 | 0.972 | 0.785 |
| 3 | `slur_phrase` | Slur spans a phrase | N/A (no training data) | N/A | N/A |
| 4 | `tie_sustained` | Tie links sustained notes | N/A (no training data) | N/A | N/A |

## Symbol Classes (15-class, matches detector output)

```python
SYMBOL_CLASSES = [
    'notehead-full', 'notehead-half', 'notehead-whole',
    'clefG', 'clefF', 'clefC',
    'rest-8th', 'rest-quarter', 'rest-half', 'rest-whole',
    'accidentalSharp', 'accidentalFlat', 'accidentalNatural',
    'beam', 'stem'
]
```

## Loading the Checkpoint

```python
import torch
from melodious.gnn import GNNAssembler

# Load
checkpoint = torch.load("outputs/gnn_checkpoint.pt", map_location="cpu")
config = checkpoint["config"]

# Reconstruct model
model = GNNAssembler(
    num_classes=config["num_classes"],        # 15
    hidden_dim=config["hidden_dim"],          # 64
    num_relationships=config["num_relationships"],  # 5
    num_gat_layers=config["num_gat_layers"],  # 3
    num_heads=config["num_heads"],            # 8
)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()
```

## Input/Output Contract

### Input (PyG Data object)

```python
from torch_geometric.data import Data

data = Data(
    x=node_features,      # [N, 10] float tensor - node features
    edge_index=edge_idx,   # [2, E] long tensor - candidate edges
    edge_type=edge_types,  # [E] long tensor - edge type (0=proximity, 1=staff, 2=vertical)
)
```

**Node features (10d):**
- `[0:4]` — Class embedding from NodeFeatureEncoder (4d)
- `[4]` — Normalized x center (0-1)
- `[5]` — Normalized y center (0-1)
- `[6]` — Normalized width (0-1)
- `[7]` — Normalized height (0-1)
- `[8]` — Confidence score (0-1)
- `[9]` — Staff index (normalized, 0-1)

**Edge types (for edge_type_embedding):**
- `0` — Proximity edge (k-NN based)
- `1` — Staff membership edge
- `2` — Vertical overlap edge

### Output

```python
edge_logits = model(data)  # [E, 5] float tensor - logits per relationship type
predictions = edge_logits.argmax(dim=-1)  # [E] long tensor - predicted relationship
```

## Inference Example

```python
from melodious.gnn import GNNAssembler, GraphConstructor, NodeFeatureEncoder, predict_relationships

# Given a list of Detection objects from the detector:
detections = [...]  # List[Detection] from melodious.gnn

# Build graph and predict
graph_constructor = GraphConstructor()
node_encoder = NodeFeatureEncoder(num_classes=15)
relationships = predict_relationships(model, detections, graph_constructor, node_encoder)
# Returns List[Relationship(source_idx, target_idx, rel_type, confidence)]
```

## Known Limitations

1. **slur_phrase and tie_sustained not trained** — MUSCIMA++ annotations did not map to these in our class taxonomy. These classes predict `no_relation` by default.
2. **stem_notehead precision** — ~52% precision means the model over-predicts stem-notehead connections. High recall (93%) means few are missed.
3. **Trained on ideal/clean data** — MUSCIMA++ is handwritten but clean scans. Performance on noisy or degraded scans is untested.

## Files

| File | Description |
|------|-------------|
| `outputs/gnn_checkpoint.pt` | Model weights + config |
| `outputs/gnn_training_results.json` | Full training history (loss, accuracy per epoch) |
| `melodious/gnn.py` | Model architecture (`GNNAssembler`, `GraphConstructor`, `NodeFeatureEncoder`) |
| `melodious/gnn_data_loader.py` | MUSCIMA++ data loading pipeline |
| `train_gnn_muscima.py` | Training script (CLI entry point) |
