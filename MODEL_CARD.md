# Model Card — Melodious OMR

## Model Overview

| Field | Value |
|-------|-------|
| **Model name** | Melodious OMR Pipeline |
| **Version** | 1.0 |
| **Architecture** | YOLOv8s (detection) + GNNAssembler (relationship assembly) |
| **Task** | Optical Music Recognition — detect music symbols and assemble them into structured notation |
| **License** | Academic use |
| **Last updated** | April 14, 2026 |

---

## Components

### Detection Model (YOLOv8s)

| Property | Value |
|----------|-------|
| Base architecture | YOLOv8s (Ultralytics) with CSPDarknet backbone |
| Parameters | 11.1M |
| Input | RGB image, 640×640 pixels |
| Output | Bounding boxes + class probabilities for 15 symbol classes |
| Pretrained on | MS COCO (80-class object detection) |
| Fine-tuned on | DeepScores v2 (1,362 train / 352 val images) |
| Training | 100 epochs, AdamW, lr=0.01, mosaic + randaugment |
| Export formats | PyTorch (.pt), ONNX FP32 (42.7 MB), ONNX INT8 (11.0 MB) |

### Assembly Model (GNNAssembler)

| Property | Value |
|----------|-------|
| Architecture | 3-layer GAT, 8 attention heads, hidden_dim=64 |
| Parameters | 606K |
| Input | Node features [N, 10] + edge_index [2, E] + edge_type [E] |
| Output | Edge relationship logits [E, 5] |
| Trained on | MUSCIMA++ v2.0 (112 train / 28 val annotated pages) |
| Training | 80 epochs, AdamW, lr=0.001, negative sampling ratio 3:1 |

---

## Intended Use

- **Primary use:** Convert photographs or scans of printed sheet music into structured digital formats (MusicXML, MIDI).
- **Target users:** Musicians, music students, music educators, and music librarians digitizing printed scores.
- **Deployment:** Mobile-first (on-device detection, server-side assembly) or fully offline.
- **Input:** Photographs or high-quality scans of printed Western music notation on standard 5-line staves.

---

## Performance Metrics

### Detection (YOLOv8s on DeepScores v2 validation set)

| Metric | Value |
|--------|-------|
| mAP@0.5 | 0.652 |
| mAP@0.5:0.95 | 0.471 |
| Precision | 0.855 |
| Recall | 0.534 |

### Per-Class Detection (top/bottom 3)

| Class | mAP50 | Notes |
|-------|-------|-------|
| clefG | 0.994 | Near-perfect |
| clefF | 0.988 | Near-perfect |
| clefC | 0.972 | Strong |
| rest-half | 0.313 | Rare + small |
| rest-whole | 0.404 | Visually ambiguous |
| stem | 0.000 | Too thin at 640px |

### Assembly (GNNAssembler on MUSCIMA++ v2.0 validation set)

| Metric | Value |
|--------|-------|
| Overall accuracy | 89.9% |
| stem_notehead F1 | 0.670 |
| beam_notegroup F1 | 0.785 |
| no_relation F1 | 0.939 |

### Deployment

| Format | Size | mAP50 | Latency |
|--------|------|-------|---------|
| PyTorch FP32 | 21.5 MB | 0.652 | — |
| ONNX FP32 | 42.7 MB | 0.651 | 173.7ms |
| ONNX INT8 | 11.0 MB | 0.625 | 122.5ms |

---

## Robustness

Evaluated under three degradation types (50-image validation subset):

| Degradation | mAP50 | Drop |
|-------------|-------|------|
| Clean (baseline) | 0.653 | — |
| Gaussian noise σ=0.01 | 0.625 | -4.3% |
| Gaussian noise σ=0.05 | 0.596 | -8.7% |
| Gaussian noise σ=0.10 | 0.532 | -18.5% |
| JPEG Q=40 | 0.626 | -4.1% |

The model is robust to JPEG compression (important for scanned scores) but sensitive to heavy Gaussian noise (relevant for low-light photographs).

---

## Bias and Limitations

### Training Data Bias

Both training datasets (DeepScores v2 and MUSCIMA++ v2.0) contain exclusively **Western classical and contemporary art music notation**. The model has been trained only on:

- Standard 5-line staff notation
- Treble (G), bass (F), and C clefs
- Common note types (full, half, whole noteheads)
- Standard accidentals (sharp, flat, natural)
- Rest symbols, beams, and stems

### Excluded Notation Systems

The model has **zero training data** for and **cannot recognize**:

- **Turkish makam notation** — uses different accidental symbols and microtonal markers
- **Indian Carnatic sargam notation** — text-based system, fundamentally different representation
- **Chinese jianpu (numbered notation)** — digit-based, no staff lines
- **Byzantine notation** — neume-based, different symbol vocabulary
- **Experimental or non-standard notation** — graphic scores, extended techniques
- **Guitar tablature** — 6-line staff with numbers, different semantics

### Out-of-Distribution Warning

If the model encounters notation outside its training distribution, a high proportion of detections will fall below 0.5 confidence. The system flags this condition with a warning:

> "This score may use notation outside the system's training distribution. Results may be unreliable."

Users should not rely on outputs when this warning appears. The model will silently misclassify unfamiliar symbols as the nearest known class rather than abstaining.

### Other Limitations

- **Recall ceiling at 640px:** The model achieves only 53.4% recall due to small symbols being missed at 640px input resolution. Larger images or SAHI tiling would improve this.
- **Stem detection failure:** Stems (vertical lines connecting noteheads to beams) have 0% mAP50 because they are too thin (1-2px wide) at 640px resolution.
- **Handwritten music:** Trained on printed scores only. Performance on handwritten scores (e.g., MUSCIMA++) is expected to degrade significantly without fine-tuning.
- **Multi-page scores:** Each page is processed independently. Cross-page context (ties, repeats) is not modeled.

---

## Privacy

- **On-device detection:** The YOLO detection model runs entirely on the user's device. Raw score images never leave the phone.
- **Minimal data transmission:** Only structured JSON (bounding box coordinates + class labels) is sent to the server for GNN assembly. This contains zero pixel data.
- **No image storage:** The system does not store, log, or retain uploaded images or intermediate representations.
- **Offline mode:** The ONNX model supports fully offline inference for users who cannot share even structural data (e.g., composers with unpublished works under NDA).

---

## Ethical Considerations

- **Cultural representation:** The model perpetuates the dominance of Western music notation in digital tools. Expanding to non-Western systems requires dedicated dataset construction efforts and community partnerships.
- **Professional reliance:** While the model achieves strong precision (85.5%), it should not be used as the sole transcription tool for critical applications (e.g., publishing, legal archival). Human verification is recommended.
- **Accessibility:** The system assumes visual access to printed scores. It does not address accessibility needs for visually impaired musicians (e.g., Braille music notation).

---

## Recommended Citation

```
Melodious OMR Pipeline v1.0
Training data: DeepScores v2 (Tuggener et al., 2018), MUSCIMA++ v2.0 (Hajic & Pecina, 2017)
Architecture: YOLOv8s + GNNAssembler (3-layer GAT)
```

---

## Future Work

- Improve recall via YOLOv8m or SAHI (Slicing Aided Hyper Inference)
- Static INT8 quantization with calibration data for better accuracy-compression tradeoff
- Fine-tune on handwritten scores (MUSCIMA++ images) for cross-domain robustness
- Expand to non-Western notation systems with targeted dataset construction
- End-to-end combined F1 evaluation (YOLO detection + GNN assembly)
