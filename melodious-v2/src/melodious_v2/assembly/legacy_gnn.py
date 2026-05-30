"""Legacy GNN adapter for V2 relationship assembly.

The checkpoint available in the parent workspace was trained before the V2
package existed. This module keeps that legacy contract isolated while exposing
V2-friendly runtime and evaluation helpers.
"""

from __future__ import annotations

import hashlib
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # Optional at import time so heuristic fallback can still run.
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch_geometric.data import Data
    from torch_geometric.nn import GATConv
except Exception as exc:  # pragma: no cover - exercised only without ML deps.
    torch = None
    nn = None
    F = None
    Data = None
    GATConv = None
    TORCH_IMPORT_ERROR: Exception | None = exc
else:
    TORCH_IMPORT_ERROR = None

from melodious_v2.contracts import DetectionV2, DetectorPayloadV2


SYMBOL_CLASSES = [
    "notehead-full",
    "notehead-half",
    "notehead-whole",
    "clefG",
    "clefF",
    "clefC",
    "rest-8th",
    "rest-quarter",
    "rest-half",
    "rest-whole",
    "accidentalSharp",
    "accidentalFlat",
    "accidentalNatural",
    "beam",
    "stem",
]

RELATIONSHIP_TYPES = [
    "no_relation",
    "stem_notehead",
    "beam_notegroup",
    "slur_phrase",
    "tie_sustained",
]

MUSCIMA_CLASS_MAP: dict[str, int] = {
    "noteheadFull": 0,
    "noteheadHalf": 1,
    "noteheadWhole": 2,
    "noteheadFullSmall": 0,
    "noteheadHalfSmall": 1,
    "gClef": 3,
    "fClef": 4,
    "cClef": 5,
    "rest8th": 6,
    "restQuarter": 7,
    "restHalf": 8,
    "restWhole": 9,
    "8thRest": 6,
    "quarterRest": 7,
    "halfRest": 8,
    "wholeRest": 9,
    "accidentalSharp": 10,
    "accidentalFlat": 11,
    "accidentalNatural": 12,
    "beam": 13,
    "stem": 14,
}

NOTEHEAD_MUSCIMA_CLASSES = {
    "noteheadFull",
    "noteheadHalf",
    "noteheadWhole",
    "noteheadFullSmall",
    "noteheadHalfSmall",
}


@dataclass(frozen=True)
class LegacyGnnDetection:
    """Detection record in the 15-class legacy GNN feature contract."""

    class_id: int
    class_name: str
    x: float
    y: float
    w: float
    h: float
    confidence: float
    staff_index: int = 0
    original_idx: int | None = None
    node_id: int | None = None
    source_class_name: str | None = None


@dataclass(frozen=True)
class MuscimaNode:
    """Parsed MUSCIMA++ node needed for graph evaluation."""

    node_id: int
    class_name: str
    top: int
    left: int
    width: int
    height: int
    outlinks: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class CandidateGraph:
    """Candidate edge graph before tensor conversion."""

    edges: list[tuple[int, int]]
    edge_types: list[int]


@dataclass(frozen=True)
class MuscimaPageGraph:
    """One MUSCIMA page converted to the GNN candidate-edge contract."""

    page_id: str
    detections: list[LegacyGnnDetection]
    edges: list[tuple[int, int]]
    edge_types: list[int]
    edge_labels: list[int]
    skipped_node_count: int


@dataclass(frozen=True)
class LegacyGnnPrediction:
    """Raw edge predictions from a loaded legacy GNN checkpoint."""

    relationships: list[Any]
    edges: list[tuple[int, int]]
    predicted_labels: list[int]
    confidences: list[float]
    inference_ran: bool
    warnings: list[str] = field(default_factory=list)


def sha256_file(path: Path) -> str:
    """Return a SHA256 hex digest for a local file."""
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_torch() -> None:
    if TORCH_IMPORT_ERROR is not None or torch is None or nn is None or F is None or Data is None:
        raise RuntimeError(
            "Legacy GNN runtime requires torch and torch_geometric. "
            f"Import error: {TORCH_IMPORT_ERROR!r}"
        )


if nn is not None and GATConv is not None:

    class SymbolEmbedding(nn.Module):
        """Learnable embedding for legacy symbol classes."""

        def __init__(self, num_classes: int = 15, embed_dim: int = 4) -> None:
            super().__init__()
            self.embedding = nn.Embedding(num_classes, embed_dim)

        def forward(self, class_ids: "torch.Tensor") -> "torch.Tensor":
            return self.embedding(class_ids)


    class NodeFeatureEncoder(nn.Module):
        """Encode class, position, confidence, and staff features."""

        def __init__(self, num_classes: int = 15, embed_dim: int = 4) -> None:
            super().__init__()
            self.symbol_embedding = SymbolEmbedding(num_classes, embed_dim)
            self.feature_dim = embed_dim + 6

        def forward(self, detections: list[LegacyGnnDetection]) -> "torch.Tensor":
            if not detections:
                return torch.zeros((0, self.feature_dim), dtype=torch.float32)

            features = []
            for detection in detections:
                class_embed = self.symbol_embedding(
                    torch.tensor([detection.class_id], dtype=torch.long)
                ).squeeze(0)
                spatial = torch.tensor(
                    [
                        detection.x,
                        detection.y,
                        detection.w,
                        detection.h,
                        detection.confidence,
                        float(detection.staff_index),
                    ],
                    dtype=torch.float32,
                )
                features.append(torch.cat([class_embed, spatial]))
            return torch.stack(features)


    class GNNAssembler(nn.Module):
        """Legacy GAT edge classifier architecture used by the checkpoint."""

        def __init__(
            self,
            num_classes: int = 15,
            hidden_dim: int = 64,
            num_gat_layers: int = 3,
            num_heads: int = 8,
            num_relationships: int = 5,
            dropout: float = 0.1,
        ) -> None:
            super().__init__()
            self.num_classes = num_classes
            self.hidden_dim = hidden_dim
            self.num_relationships = num_relationships
            self.node_encoder = NodeFeatureEncoder(num_classes, embed_dim=4)
            self.input_proj = nn.Linear(self.node_encoder.feature_dim, hidden_dim)
            self.gat_layers = nn.ModuleList()
            for layer_index in range(num_gat_layers):
                in_channels = hidden_dim if layer_index == 0 else hidden_dim * num_heads
                self.gat_layers.append(
                    GATConv(
                        in_channels,
                        hidden_dim,
                        heads=num_heads,
                        dropout=dropout,
                        add_self_loops=True,
                        concat=True,
                    )
                )
            self.node_proj = nn.Linear(hidden_dim * num_heads, hidden_dim)
            self.edge_type_embedding = nn.Embedding(3, 8)
            self.edge_classifier = nn.Sequential(
                nn.Linear(hidden_dim * 2 + 8 + 4, hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim // 2, num_relationships),
            )

        def forward(self, data: "Data") -> "torch.Tensor":
            x = self.input_proj(data.x)
            for gat_layer in self.gat_layers:
                x = F.elu(gat_layer(x, data.edge_index))
            node_embeddings = self.node_proj(x)

            src_nodes = data.edge_index[0]
            tgt_nodes = data.edge_index[1]
            src_embeds = node_embeddings[src_nodes]
            tgt_embeds = node_embeddings[tgt_nodes]
            edge_type_embeds = self.edge_type_embedding(data.edge_type)
            rel_pos = self._compute_relative_positions(data.detections, src_nodes, tgt_nodes)
            edge_features = torch.cat([src_embeds, tgt_embeds, edge_type_embeds, rel_pos], dim=-1)
            return self.edge_classifier(edge_features)

        def _compute_relative_positions(
            self,
            detections: list[LegacyGnnDetection],
            src_nodes: "torch.Tensor",
            tgt_nodes: "torch.Tensor",
        ) -> "torch.Tensor":
            values = []
            for src_idx, tgt_idx in zip(src_nodes.cpu().tolist(), tgt_nodes.cpu().tolist()):
                src = detections[src_idx]
                tgt = detections[tgt_idx]
                values.append([tgt.x - src.x, tgt.y - src.y, tgt.w - src.w, tgt.h - src.h])
            return torch.tensor(values, dtype=torch.float32, device=src_nodes.device)

else:  # pragma: no cover - exercised only without ML deps.

    class GNNAssembler:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _require_torch()


def map_detector_detection_to_legacy(detection: DetectionV2) -> int | None:
    """Map a V2 136-class detection into the legacy 15-class GNN taxonomy."""
    class_name = detection.class_name
    if class_name.startswith("noteheadHalf"):
        return 1
    if class_name.startswith("noteheadWhole") or class_name.startswith("noteheadDoubleWhole"):
        return 2
    if class_name.startswith("notehead") or class_name.startswith("graceNote"):
        return 0
    if class_name == "clefG":
        return 3
    if class_name == "clefF":
        return 4
    if class_name in {"clefCAlto", "clefCTenor"}:
        return 5
    if class_name == "rest8th":
        return 6
    if class_name == "restQuarter":
        return 7
    if class_name == "restHalf":
        return 8
    if class_name in {"restWhole", "restDoubleWhole"}:
        return 9
    if class_name in {"accidentalSharp", "accidentalSharpSmall"}:
        return 10
    if class_name in {"accidentalFlat", "accidentalFlatSmall"}:
        return 11
    if class_name in {"accidentalNatural", "accidentalNaturalSmall"}:
        return 12
    if class_name == "beam":
        return 13
    if class_name == "stem":
        return 14
    return None


def payload_to_legacy_detections(payload: DetectorPayloadV2) -> list[LegacyGnnDetection]:
    """Convert a V2 detector payload into the legacy GNN detection list."""
    detections: list[LegacyGnnDetection] = []
    for original_idx, detection in enumerate(payload.detections):
        class_id = map_detector_detection_to_legacy(detection)
        if class_id is None:
            continue
        staff_index = max(0, min(3, int(detection.bbox.y_center * 4)))
        detections.append(
            LegacyGnnDetection(
                class_id=class_id,
                class_name=SYMBOL_CLASSES[class_id],
                x=detection.bbox.x_center,
                y=detection.bbox.y_center,
                w=detection.bbox.width,
                h=detection.bbox.height,
                confidence=detection.confidence,
                staff_index=staff_index,
                original_idx=original_idx,
                source_class_name=detection.class_name,
            )
        )
    return detections


def build_candidate_graph(
    detections: list[LegacyGnnDetection],
    k_neighbors: int = 8,
    max_x_dist: float = 0.15,
) -> CandidateGraph:
    """Build the checkpoint's natural candidate-edge graph without subsampling."""
    if len(detections) < 2:
        return CandidateGraph(edges=[], edge_types=[])

    edges: list[tuple[int, int]] = []
    edge_types: list[int] = []
    seen: set[tuple[int, int]] = set()

    for src_idx, source in enumerate(detections):
        neighbors: list[tuple[float, int]] = []
        for tgt_idx, target in enumerate(detections):
            if src_idx == tgt_idx:
                continue
            distance = math.sqrt((target.x - source.x) ** 2 + (target.y - source.y) ** 2)
            neighbors.append((distance, tgt_idx))
        for _, tgt_idx in sorted(neighbors)[:k_neighbors]:
            if abs(detections[tgt_idx].x - source.x) > max_x_dist:
                continue
            edge = (src_idx, tgt_idx)
            if edge not in seen:
                edges.append(edge)
                edge_types.append(0)
                seen.add(edge)

    interesting_classes = {0, 1, 2, 13, 14}
    for src_idx, source in enumerate(detections):
        if source.class_id not in interesting_classes:
            continue
        source_y_min = source.y - source.h / 2
        source_y_max = source.y + source.h / 2
        for tgt_idx, target in enumerate(detections):
            if src_idx == tgt_idx or target.class_id not in interesting_classes:
                continue
            edge = (src_idx, tgt_idx)
            if edge in seen:
                continue
            target_y_min = target.y - target.h / 2
            target_y_max = target.y + target.h / 2
            overlap = min(source_y_max, target_y_max) - max(source_y_min, target_y_min)
            if overlap > 0 and abs(source.x - target.x) < 0.05:
                edges.append(edge)
                edge_types.append(1)
                seen.add(edge)

    return CandidateGraph(edges=edges, edge_types=edge_types)


def classify_muscima_relationship(src_class: str, tgt_class: str) -> int:
    """Map a MUSCIMA outlink class pair to a legacy relationship class id."""
    if (src_class in NOTEHEAD_MUSCIMA_CLASSES and tgt_class == "stem") or (
        src_class == "stem" and tgt_class in NOTEHEAD_MUSCIMA_CLASSES
    ):
        return 1
    if (src_class in NOTEHEAD_MUSCIMA_CLASSES and tgt_class == "beam") or (
        src_class == "beam" and tgt_class in NOTEHEAD_MUSCIMA_CLASSES
    ):
        return 2
    if (src_class in NOTEHEAD_MUSCIMA_CLASSES and tgt_class == "slur") or (
        src_class == "slur" and tgt_class in NOTEHEAD_MUSCIMA_CLASSES
    ):
        return 3
    if (src_class in NOTEHEAD_MUSCIMA_CLASSES and tgt_class == "tie") or (
        src_class == "tie" and tgt_class in NOTEHEAD_MUSCIMA_CLASSES
    ):
        return 4
    return 0


def parse_muscima_xml(xml_path: Path) -> list[MuscimaNode]:
    """Parse the subset of MUSCIMA++ XML needed for graph evaluation."""
    root = ET.parse(xml_path).getroot()
    nodes: list[MuscimaNode] = []
    for node_elem in root.findall(".//Node"):
        outlinks_elem = node_elem.find("Outlinks")
        outlinks: list[int] = []
        if outlinks_elem is not None and outlinks_elem.text:
            outlinks = [int(value) for value in outlinks_elem.text.strip().split()]
        nodes.append(
            MuscimaNode(
                node_id=int(node_elem.findtext("Id", "0")),
                class_name=node_elem.findtext("ClassName", ""),
                top=int(node_elem.findtext("Top", "0")),
                left=int(node_elem.findtext("Left", "0")),
                width=int(node_elem.findtext("Width", "0")),
                height=int(node_elem.findtext("Height", "0")),
                outlinks=outlinks,
            )
        )
    return nodes


def _estimate_staff_index(y_center: float, page_height: float, num_staffs: int = 4) -> int:
    region_height = page_height / max(num_staffs, 1)
    return max(0, min(num_staffs - 1, int(y_center / region_height)))


def build_muscima_page_graph(
    xml_path: Path,
    k_neighbors: int = 8,
    num_staffs: int = 4,
) -> MuscimaPageGraph:
    """Convert one MUSCIMA page to natural candidate edges and labels."""
    nodes = parse_muscima_xml(xml_path)
    if not nodes:
        return MuscimaPageGraph(xml_path.stem, [], [], [], [], 0)

    max_x = max(node.left + node.width for node in nodes)
    max_y = max(node.top + node.height for node in nodes)
    page_width = max(max_x * 1.05, 1.0)
    page_height = max(max_y * 1.05, 1.0)

    node_by_id = {node.node_id: node for node in nodes}
    kept_node_ids: list[int] = []
    detections: list[LegacyGnnDetection] = []
    skipped = 0
    for node in nodes:
        class_id = MUSCIMA_CLASS_MAP.get(node.class_name, -1)
        if class_id < 0:
            skipped += 1
            continue
        x_center = (node.left + node.width / 2) / page_width
        y_center = (node.top + node.height / 2) / page_height
        detections.append(
            LegacyGnnDetection(
                class_id=class_id,
                class_name=SYMBOL_CLASSES[class_id],
                x=x_center,
                y=y_center,
                w=node.width / page_width,
                h=node.height / page_height,
                confidence=1.0,
                staff_index=_estimate_staff_index(node.top + node.height / 2, page_height, num_staffs),
                original_idx=len(detections),
                node_id=node.node_id,
                source_class_name=node.class_name,
            )
        )
        kept_node_ids.append(node.node_id)

    kept_id_to_idx = {node_id: idx for idx, node_id in enumerate(kept_node_ids)}
    positive_edges: dict[tuple[int, int], int] = {}
    for src_idx, node_id in enumerate(kept_node_ids):
        source_node = node_by_id[node_id]
        for target_id in source_node.outlinks:
            target_idx = kept_id_to_idx.get(target_id)
            if target_idx is None:
                continue
            rel_type = classify_muscima_relationship(
                source_node.class_name,
                node_by_id[target_id].class_name,
            )
            if rel_type > 0:
                positive_edges[(src_idx, target_idx)] = rel_type
                positive_edges[(target_idx, src_idx)] = rel_type

    candidate_graph = build_candidate_graph(detections, k_neighbors=k_neighbors)
    edge_labels = [positive_edges.get(edge, 0) for edge in candidate_graph.edges]
    return MuscimaPageGraph(
        page_id=xml_path.stem,
        detections=detections,
        edges=candidate_graph.edges,
        edge_types=candidate_graph.edge_types,
        edge_labels=edge_labels,
        skipped_node_count=skipped,
    )


class LegacyGnnAdapter:
    """Load and execute the legacy MUSCIMA relationship checkpoint."""

    name = "legacy_muscima_gat"

    def __init__(
        self,
        checkpoint_path: str | Path,
        device: str = "cpu",
        confidence_threshold: float = 0.5,
        k_neighbors: int = 8,
    ) -> None:
        _require_torch()
        self.checkpoint_path = Path(checkpoint_path).expanduser().resolve()
        self.device = torch.device(device)
        self.confidence_threshold = confidence_threshold
        self.k_neighbors = k_neighbors
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Legacy GNN checkpoint not found: {self.checkpoint_path}")
        self.checkpoint_sha256 = sha256_file(self.checkpoint_path)
        self.checkpoint = torch.load(self.checkpoint_path, map_location=self.device, weights_only=False)
        config = self.checkpoint.get("config", {})
        self.config = config
        self.model = GNNAssembler(
            num_classes=int(config.get("num_classes", 15)),
            hidden_dim=int(config.get("hidden_dim", 64)),
            num_relationships=int(config.get("num_relationships", 5)),
            num_gat_layers=int(config.get("num_gat_layers", 3)),
            num_heads=int(config.get("num_heads", 8)),
        ).to(self.device)
        self.model.load_state_dict(self.checkpoint["model_state_dict"])
        self.model.eval()

    def is_ready(self) -> bool:
        return True

    def predict_payload(self, payload: DetectorPayloadV2) -> LegacyGnnPrediction:
        detections = payload_to_legacy_detections(payload)
        return self.predict_detections(detections)

    def predict_detections(self, detections: list[LegacyGnnDetection]) -> LegacyGnnPrediction:
        from melodious_v2.assembly.service import Relationship

        candidate_graph = build_candidate_graph(detections, k_neighbors=self.k_neighbors)
        if len(detections) < 2 or not candidate_graph.edges:
            return LegacyGnnPrediction(
                relationships=[],
                edges=candidate_graph.edges,
                predicted_labels=[],
                confidences=[],
                inference_ran=False,
                warnings=["GNN checkpoint loaded but no candidate edges were available."],
            )

        edge_index = torch.tensor(candidate_graph.edges, dtype=torch.long, device=self.device).t().contiguous()
        edge_type = torch.tensor(candidate_graph.edge_types, dtype=torch.long, device=self.device)
        with torch.no_grad():
            node_features = self.model.node_encoder(detections).to(self.device)
            data = Data(x=node_features, edge_index=edge_index, edge_type=edge_type)
            data.detections = detections
            edge_logits = self.model(data)
            edge_probs = torch.softmax(edge_logits, dim=-1)
            predictions = edge_probs.argmax(dim=-1).cpu().tolist()
            confidences = edge_probs.max(dim=-1).values.cpu().tolist()

        relationships: list[Relationship] = []
        for (src_idx, tgt_idx), predicted_label, confidence in zip(
            candidate_graph.edges,
            predictions,
            confidences,
        ):
            if predicted_label <= 0 or confidence < self.confidence_threshold:
                continue
            source_original = detections[src_idx].original_idx
            target_original = detections[tgt_idx].original_idx
            relationships.append(
                Relationship(
                    source_idx=source_original if source_original is not None else src_idx,
                    target_idx=target_original if target_original is not None else tgt_idx,
                    relationship_type=RELATIONSHIP_TYPES[predicted_label],
                    confidence=float(confidence),
                )
            )

        return LegacyGnnPrediction(
            relationships=relationships,
            edges=candidate_graph.edges,
            predicted_labels=[int(label) for label in predictions],
            confidences=[float(value) for value in confidences],
            inference_ran=True,
            warnings=[],
        )
