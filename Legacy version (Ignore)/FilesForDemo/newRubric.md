# Project Rubric — Machine Learning Course
> Auto-calculated Gradebook | All scores are computed automatically from rubric inputs.

---

## Table of Contents

1. [Grading Categories Overview](#grading-categories-overview)
2. [Detailed Rubric Criteria](#detailed-rubric-criteria)
   - [Problem & Fit (15%)](#1-problem--fit-15)
   - [Technical Rigor & Responsible ML (30%)](#2-technical-rigor--responsible-ml-30)
   - [Deployment & Engineering (20%)](#3-deployment--engineering-20)
   - [GitHub & Documentation (15%)](#4-github--documentation-15)
   - [Presentation (10%)](#5-presentation-10)
   - [Creativity & Initiative (10%)](#6-creativity--initiative-10)
   - [Bonus Points (+3 max)](#7-bonus-points-3-max)
3. [Project Type Tracks](#project-type-tracks)
4. [Special Flags & Automatic Checks](#special-flags--automatic-checks)
5. [Team & Project Registry](#team--project-registry)
6. [Scoring Summary Formula](#scoring-summary-formula)

---

## Grading Categories Overview

| Category | Weight | Max Points (normalized) |
|---|---|---|
| Problem & Fit | 15% | 10 pts |
| Technical Rigor & Responsible ML | 30% | 10 pts |
| Deployment & Engineering | 20% | 10 pts |
| GitHub & Documentation | 15% | 10 pts |
| Presentation | 10% | 10 pts |
| Creativity & Initiative | 10% | 10 pts |
| **Base Total** | **100%** | **100 pts** |
| Bonus | +3 max | +3 pts |
| **Final Max** | — | **103 pts** |

---

## Detailed Rubric Criteria

---

### 1. Problem & Fit (15%)

> Evaluates whether the project addresses a clearly scoped, meaningful problem with a justified ML approach.

#### PF1 — Specific Problem / Question
- Is the problem statement precise and well-scoped?
- Is there a clear question the project aims to answer or solve?
- Vague or overly broad problem statements should be penalized.

#### PF2A — User / Decision / Deployer *(Track A only)*
- Who is the end user, decision-maker, or system deployer?
- Is the stakeholder context clearly articulated?
- Does the solution match the needs of the identified user?

#### PF2B — Research Question + Venue *(Track B only)*
- Is a formal research question stated?
- Is the target publication venue or conference identified and appropriate?
- Does the scope match what is expected for the venue?

#### PF3A — Why ML, Why Not Simpler *(Track A only)*
- Is there justification for using ML over simpler rule-based or statistical methods?
- Does the team demonstrate awareness of when ML is and isn't warranted?
- Penalty if a simpler solution would obviously suffice.

#### PF3B — Not Applicable + Publishable Scope *(Track B only)*
- Does the project meet the threshold for a publishable contribution?
- Is the scope neither too narrow (toy problem) nor too broad (unrealistic for course)?

#### PF4 — Impact / Significance
- Does the problem have real-world relevance?
- What is the potential impact if the solution succeeds?
- Is the significance clearly communicated?

#### PF5 — Type / Track Fit + Success Criteria
- Does the project clearly align with its declared track (A or B)?
- Are measurable success criteria defined upfront?
- Will a reviewer be able to determine at the end whether the project succeeded?

---

### 2. Technical Rigor & Responsible ML (30%)

> Evaluates the soundness of ML methodology, model development, and ethical considerations.

#### TM1 — Task + Data Formulation
- Is the ML task (classification, regression, generation, etc.) clearly defined?
- Is the dataset appropriate for the task?
- Are data sources identified and described?

#### TM2A — Non-AI Baseline *(Track A only)*
- Is there a meaningful non-ML or non-AI baseline (e.g., heuristic, rule-based, majority class)?
- Is the baseline fairly implemented and reported?
- Does the ML model demonstrate clear improvement over the baseline?

#### TM2B — Baseline / Prior Work Comparison *(Track B only)*
- Is the project compared against prior work or published baselines?
- Are citations and comparisons fair and rigorous?
- Are differences in setup clearly noted?

#### TM3 — Method Choice + Substance
- Is the chosen ML method appropriate for the task?
- Is there reasoning behind the method selection?
- Is the method implemented with sufficient depth (not just a default sklearn call)?

#### TM4 — Preprocessing / Features / Leakage
- Is data preprocessing documented and justified?
- Are features engineered thoughtfully?
- Is there evidence that **data leakage** has been checked for and avoided (e.g., no future data in training, no target in features)?

#### TM5 — Splits, Metrics, Protocol
- Are train/validation/test splits clearly defined and appropriate?
- Are evaluation metrics chosen with justification (e.g., why accuracy vs. F1 vs. AUC)?
- Is the evaluation protocol sound and reproducible?

#### TM6 — Error Analysis
- Does the team analyze *where* and *why* the model fails?
- Are failure modes identified (e.g., specific subgroups, edge cases)?
- Are visualizations or examples of errors provided?

#### TM7 — Limits + Trade-offs
- Does the team honestly discuss limitations of the approach?
- Are trade-offs between models, metrics, or design choices discussed?
- Is there acknowledgment of what the model cannot do?

#### TM8B — Research Artifact Depth *(Track B only)*
- Is the research contribution substantial (e.g., novel dataset, architecture, analysis)?
- Does it go beyond a course project level in depth?

#### TM9G — Graph Core Object *(Graph projects only)*
- Is the core data structure a graph (nodes + edges)?
- Is the graph formulation natural and justified for the problem?

#### TM10G — Graph vs. Non-Graph Justified *(Graph projects only)*
- Is there a comparison or argument showing why a graph approach outperforms or is more appropriate than a non-graph approach?
- Is this comparison empirical or theoretical?

---

#### Responsible ML (RM) Sub-criteria

> At least **3 of the 4 RM topics** must be meaningfully addressed. Fewer than 3 triggers an automatic flag.

#### RM1 — Explainability
- Is the model's decision-making interpretable?
- Are tools used (SHAP, LIME, attention maps, feature importance, etc.)?
- Is explainability appropriate for the stakeholder (e.g., end user vs. developer)?

#### RM2 — Fairness / Bias
- Does the project identify potential sources of bias in data or model?
- Are fairness metrics computed (e.g., demographic parity, equalized odds)?
- Are mitigation strategies discussed or implemented?

#### RM3 — Privacy / Leakage
- Does the project handle sensitive data with appropriate safeguards?
- Are there concerns about membership inference or model inversion?
- Is differential privacy, anonymization, or data minimization considered?

#### RM4 — Robustness / Distribution Shift
- Is the model tested against adversarial inputs, corrupted data, or out-of-distribution samples?
- Is there discussion of how the model might degrade in deployment?
- Are robustness-enhancing strategies implemented or discussed?

---

### 3. Deployment & Engineering (20%)

> Evaluates the production-readiness and engineering quality of the project.

#### EN1 — Dockerized API
- Is the model served via an API (REST, gRPC, etc.)?
- Is the service containerized with Docker?
- Does the container build and run cleanly from the provided instructions?

#### EN2 — Separation of Data / Model / Serving
- Is there a clean separation between data processing, model training, and inference/serving code?
- Are configuration and secrets managed separately from code?
- Follows software engineering best practices (e.g., no hardcoded paths, no training in the serving layer)?

#### EN3 — Reproducible Environment + Run Path
- Is a requirements file, conda env, or equivalent provided?
- Can a reviewer reproduce the environment and run the project from scratch?
- Are all steps from data → training → evaluation → serving documented?

#### EN4 — UI / Demo Flow
- Is there a user-facing interface (web app, CLI, notebook, etc.)?
- Is the demo flow intuitive and functional?
- Does it showcase the model's core capability clearly?

#### EN5 — Running Artifact / Service
- Does the deployed artifact actually run at demo time?
- Is there a live URL, video, or reproducible demo?
- Is the service stable (not crashing, erroring, or returning garbage)?

---

### 4. GitHub & Documentation (15%)

> Evaluates the quality of the repository and written documentation.

#### GD1 — Repo Structure
- Is the repository organized logically (e.g., `/data`, `/models`, `/src`, `/notebooks`)?
- Is the root clean and navigable?
- Are unnecessary files (e.g., large binaries, `.DS_Store`) excluded?

#### GD2 — README: Setup + Run
- Does the README contain clear installation instructions?
- Are run commands provided and tested?
- Can a new user get the project running from the README alone?

#### GD3 — Method / Architecture Docs
- Is the ML architecture or pipeline documented (diagram, description, or both)?
- Are design decisions explained in writing?
- Are non-obvious implementation choices annotated?

#### GD4 — Results / Logs / Ablations
- Are results logged and version-controlled (e.g., MLflow, W&B, CSV logs)?
- Are ablation studies or hyperparameter sweeps documented?
- Are final metrics clearly reported and traceable to a specific run?

#### GD5 — Data + Limits + Notes
- Is the dataset described (source, size, format, license)?
- Are known limitations of the data documented?
- Are any preprocessing quirks or gotchas noted for future users?

---

### 5. Presentation (10%)

> Evaluates the team's ability to communicate the project clearly and handle questions.

#### PR1 — Problem Clarity
- Is the problem explained clearly to a general technical audience?
- Is motivation established quickly and compellingly?

#### PR2 — Method Clarity
- Is the technical approach explained at the right level of abstraction?
- Are visuals, diagrams, or demos used to aid understanding?

#### PR3 — Results / Demo Clarity
- Are results presented clearly with appropriate visualizations?
- Is the live demo or video smooth and illustrative of the project's value?

#### PR4 — Q&A / Ownership
- Can all team members answer questions about the project?
- Do they demonstrate genuine understanding (not just rehearsed answers)?
- Are honest acknowledgments of limitations made when challenged?

---

### 6. Creativity & Initiative (10%)

> Rewards projects that go beyond the minimum requirements in meaningful ways.

#### CI1 — Originality
- Is the problem novel or approached in a non-obvious way?
- Does the project contribute something new (data, framing, method, application)?

#### CI2 — Design Trade-offs
- Does the team demonstrate thoughtful consideration of alternatives?
- Are design decisions made intentionally with pros/cons weighed?

#### CI3 — Beyond Minimum
- Does the project exceed course expectations in depth, scope, or polish?
- Is there evidence of extra effort (e.g., additional experiments, richer analysis)?

#### CI4 — Purposeful Extras
- Are extra features or experiments purposeful rather than superficial?
- Do extras add genuine value to the project's contribution?

---

### 7. Bonus Points (+3 max)

> Bonus points are additive and do not compensate for deficiencies in core categories.

#### BX1 — Edge / Mobile Deployment *(+1)*
- Is the model deployed on an edge device (Raspberry Pi, Jetson, mobile phone, browser via WASM/ONNX, etc.)?
- Is the deployment real and demonstrated, not just planned?

#### BX2 — Responsible ML Beyond Minimum *(+1)*
- Does the project address **all 4** RM topics (RM1–RM4) with depth?
- Are RM considerations integrated into the system, not bolted on?

#### BX3 — Exceptional Extension *(+1)*
- Has the team produced something truly exceptional in depth, impact, or novelty?
- Would this work stand out at a course showcase or in a portfolio?

---

## Project Type Tracks

| Track | Label | Description |
|---|---|---|
| **A** | Applied / Deployment | Industry-oriented. Must have non-AI baseline, real users, and deployed artifact. |
| **B** | Research | Research-oriented. Must have publishable scope, prior-work comparison, and research artifact. |

> **Important:** Project type must be set. `"Set type"` in the gradebook is an automatic flag indicating the team has not declared their track.

### Additional Flags

| Flag | Condition | Notes |
|---|---|---|
| `Graph? (Y/N)` | Uses graph ML as core approach | Triggers TM9G and TM10G rubric items |
| `Edge / Mobile? (Y/N)` | Deployed on edge/mobile | Enables BX1 bonus |
| `Type req flag` | Track not declared | Must be resolved before final grading |
| `Graph req flag` | Graph flag inconsistency | Graph rubric items must be scored if Y |
| `Responsible ML <3 topics` | Fewer than 3 RM criteria addressed | Automatic penalty flag |

---

## Special Flags & Automatic Checks

The gradebook automatically computes and flags the following:

| Check | Trigger Condition |
|---|---|
| **Applicable rubrics** | Count of rubric items relevant to the project (based on type + flags) |
| **Scored rubrics** | Count of rubric items that have been filled in |
| **Remaining blanks** | `Applicable − Scored` — must reach 0 before submission |
| **RML topics met** | Count of RM1–RM4 that are scored; flags if < 3 |
| **Type req flag** | Fires if project type (A/B) is not set |
| **Graph req flag** | Fires if Graph = Y but TM9G/TM10G are not scored (or vice versa) |

---

## Team & Project Registry

| # | Team Members | Project Title | Track | Graph | Edge/Mobile |
|---|---|---|---|---|---|
| 1 | Ahmad Abdellatif, Hatem Madi, Hassan Zuelghina | ShakeShield | — | — | — |
| 2 | Theodore Al Sammour, Joseph Chahine, Rawan El Anouti | Real-Time Interview Simulator | — | — | — |
| 3 | Ryan Masri, Omar Doughan | Pre-Launch Recommendation & Prediction System for Kickstarter Campaigns | — | — | — |
| 4 | Lucien Daher, Mamdouh Elzein | Forest Lens | — | — | — |
| 5 | Maroun El Hajj | Drought Early Warning | — | — | — |
| 6 | Mahdi Slim, Amir Darwich, Adam Al Khatib | 3D Printer Failure Detection | — | — | — |
| 7 | Ahmad Yateem, Hassan Nasrallah | Melodious | — | — | — |
| 8 | Sarah Tourbah, Leen Kahwaji | Interview Coach | — | — | — |
| 9 | Garod Bederian, Alex Dekermenjian, Ali Lakkis | AcademicPath | — | — | — |
| 10 | Abdel Rahman Habbal, Mohamad Daouk, Abderrahman Zeidan | Smart Home Energy Management System | — | — | — |
| 11 | Mohamad Hussein Karnib, Hassan Hijazi, Rana Ezzeddine | Ara-guard | — | — | — |
| 12 | Jad Al Lakkis, Ibrahim Khaled | Driver Specific Racing Optimization | — | — | — |
| 13 | Zeina Hammoud, Celine Sadaka, Raoul Saber | Edge AI Dementia Voice Early Detector | — | — | — |
| 14 | Marwa Deeb, Laure Mohsen | Application-Oriented Graph-Based ML on Cloud | — | — | — |
| 15 | Hiba Swaidan, Ayat Nassar, Fatima Al Amine | Small Business E-Commerce | — | — | — |
| 16 | Mohamad Al Aalami, Hasan Haidar, Mohamad Kassira | Graph-Structured Reinforcement Learning for Urban Traffic Signal Control | — | — | — |
| 17 | Ali Yaacoub, Ali Nasrallah, Malek Bakkar | Detecting Window Edges LIDAR | — | — | — |

> All scores currently show **0** — rubric items have not yet been filled in. All teams are flagged for: missing project type declaration and fewer than 3 Responsible ML topics addressed.

---

## Scoring Summary Formula

```
Problem Score  (out of 10)  = weighted avg of PF1–PF5
Tech Score     (out of 10)  = weighted avg of TM1–TM10G + RM1–RM4
Eng Score      (out of 10)  = weighted avg of EN1–EN5
Repo Score     (out of 10)  = weighted avg of GD1–GD5
Pres Score     (out of 10)  = weighted avg of PR1–PR4
Creativity     (out of 10)  = weighted avg of CI1–CI4

Base Grade (/100) =
  (Problem/10  × 15)
+ (Tech/10     × 30)
+ (Eng/10      × 20)
+ (Repo/10     × 15)
+ (Pres/10     × 10)
+ (Creativity/10 × 10)

Bonus (/3) = BX1 + BX2 + BX3  (each worth 1, max 3)

Final % = Base Grade + Bonus
```

> **Note:** Bonus points are capped at +3 and cannot substitute for core category scores. The Final % maximum is **103**.

---

*Last updated: May 2026 | Auto-calculated — do not manually edit score columns.*
