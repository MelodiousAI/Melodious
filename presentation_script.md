# Melodious Final Presentation Script (5 Minutes)

This script is aligned to rubric presentation criteria PR1–PR4.

## 0:00–0:45 — PR1 Problem Framing and Motivation

"Our project is Melodious, an end-to-end optical music recognition system. The goal is to convert score images into structured outputs that can be exported as MusicXML and MIDI. We focus on a realistic ML systems problem: dense symbol detection, relational assembly, and reproducible deployment."

Key points to say:

- Why this matters: practical score digitization and structured playback/editing.
- Why this is hard: dense symbols, class imbalance, and relational ambiguity.

## 0:45–2:00 — PR2 Method and Architecture

"The pipeline has two modeling stages and one serving stage. Stage 1 is YOLOv8 symbol detection. Stage 2 is a graph-based assembler that predicts symbol relationships. Stage 3 is export and serving through FastAPI plus frontend/demo surfaces."

Key points to say:

- Detection: YOLOv8s fine-tuned on DeepScores.
- Graph core: nodes are symbols, edges are candidate relations, edge labels are learned relationships.
- Deployment: Dockerized backend, product frontend, and testable API routes.

## 2:00–3:20 — PR3 Results, Visuals, and Honest Performance

"On detection, our best model reaches mAP@0.5 of 0.652, precision 0.855, and recall 0.534. For graph assembly training on MUSCIMA++, we reached strong class-level F1 on core relations in sampled settings, but the end-to-end combined estimate is still below our proposal target."

Key points to say:

- Detection improvements vs baseline are substantial.
- Robustness findings: JPEG robust, noise-sensitive at higher sigma.
- Honest gap: combined pipeline estimate (`~0.358`) is below target (`0.75`), with clear causes and next steps.

## 3:20–4:10 — PR3 Demo Flow

Demo sequence:

1. Open API health endpoint / product sample flow.
2. Show detection/assembly output path.
3. Show export path (MusicXML/MIDI).
4. Point to confidence/interpretability surfaces.

Fallback if live demo fails:

- Use pre-generated outputs in `outputs/` and documented logs in `documentation.md`.

## 4:10–5:00 — PR4 Ownership and Q&A Readiness

"We can defend each technical decision with evidence in the repository. We also documented failure modes and trade-offs instead of only reporting best-case numbers."

Q&A checklist:

- Why ML and not classical-only? (baseline evidence)
- Why graph is core? (node/edge/relationship learning and non-graph comparison)
- Why recall is the bottleneck? (small/rare symbol behavior, class imbalance)
- What is the reproducible run path? (README deterministic section)
- Responsible ML handling? (MODEL_CARD: bias, privacy, robustness, limitations)

## 30-Second Closing

"Melodious is not only a demo model; it is a reproducible system with measurable strengths, clearly documented limitations, and an explicit path for closing the remaining performance gap."
