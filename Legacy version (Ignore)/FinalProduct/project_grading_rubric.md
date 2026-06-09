# Project Grading Rubric

## 1. Problem & Fit - 15%

| Code | Criterion |
|---|---|
| PF1 | Specific problem / question |
| PF2A | **Type A:** User, decision-maker, or deployer |
| PF2B | **Type B:** Research question and venue |
| PF3A | **Type A:** Why machine learning is needed and why a simpler method is insufficient |
| PF3B | **Type B:** Not applicable and publishable scope |
| PF4 | Impact / significance |
| PF5 | Project type / track fit and success criteria |

## 2. Technical Rigor & Responsible ML - 30%

### Technical Rigor

| Code | Criterion |
|---|---|
| TM1 | Task and data formulation |
| TM2A | **Type A:** Non-AI baseline |
| TM2B | **Type B:** Baseline or prior-work comparison |
| TM3 | Method choice and technical substance |
| TM4 | Preprocessing, features, and leakage prevention |
| TM5 | Data splits, metrics, and evaluation protocol |
| TM6 | Error analysis |
| TM7 | Limitations and trade-offs |
| TM8B | **Type B:** Research artifact depth |
| TM9G | **Graph projects:** Graph is the core object |
| TM10G | **Graph projects:** Graph approach is justified against a non-graph approach |

### Responsible Machine Learning

| Code | Criterion |
|---|---|
| RM1 | Explainability |
| RM2 | Fairness / bias |
| RM3 | Privacy / leakage |
| RM4 | Robustness / distribution shift |

> The gradebook includes a flag when fewer than three Responsible ML topics are addressed.

## 3. Deployment & Engineering - 20%

| Code | Criterion |
|---|---|
| EN1 | Dockerized API |
| EN2 | Separation of data, model, and serving layers |
| EN3 | Reproducible environment and clear run path |
| EN4 | User interface / demo flow |
| EN5 | Running artifact or service |

## 4. GitHub & Documentation - 15%

| Code | Criterion |
|---|---|
| GD1 | Repository structure |
| GD2 | README with setup and run instructions |
| GD3 | Method / architecture documentation |
| GD4 | Results, logs, and ablations |
| GD5 | Data documentation, limitations, and notes |

## 5. Presentation - 10%

| Code | Criterion |
|---|---|
| PR1 | Problem clarity |
| PR2 | Method clarity |
| PR3 | Results / demo clarity |
| PR4 | Question-and-answer performance and project ownership |

## 6. Creativity & Initiative - 10%

| Code | Criterion |
|---|---|
| CI1 | Originality |
| CI2 | Design trade-offs |
| CI3 | Work beyond the minimum requirements |
| CI4 | Purposeful extra features or extensions |

## 7. Bonus - Up to +3 Points

| Code | Criterion |
|---|---|
| BX1 | Edge / mobile implementation |
| BX2 | Responsible ML work beyond the minimum |
| BX3 | Exceptional extension |

## Grade Calculation

| Category | Weight |
|---|---:|
| Problem & Fit | 15% |
| Technical Rigor & Responsible ML | 30% |
| Deployment & Engineering | 20% |
| GitHub & Documentation | 15% |
| Presentation | 10% |
| Creativity & Initiative | 10% |
| **Base Grade** | **100%** |
| Bonus | **Up to +3 points** |

## Project Classification and Requirement Checks

The gradebook also records:

- Project type: **Type A or Type B**
- Whether the project is graph-based
- Whether the project includes an edge or mobile component
- Applicable rubric criteria
- Number of scored criteria
- Remaining blank criteria
- Responsible ML topics met
- Type requirement flag
- Graph requirement flag
- Evidence / notes

---

# Course Project Requirements and Our Selected Track

## Our Project Classification

For this project, **we selected Option A: Application-Oriented ML Systems**.

Our specific classification is:

- **Primary track:** Option A — Application-Oriented ML System
- **Graph-based project:** Yes
- **Research track:** No; the project is not being submitted as Option B
- **Required comparison:** A graph-based ML approach must be compared fairly against a non-graph baseline using the same underlying raw data
- **Deployment expectation:** The final system must include a Dockerized API, reproducible experiments, a functional interface, and a running artifact or service
- **Responsible ML expectation:** At least three Responsible ML topics must be addressed explicitly
- **Edge/mobile component:** Optional bonus only, unless included and technically justified

Because we chose **Option A with a graph-based approach**, we must satisfy **all general Option A requirements** as well as **all additional graph-project requirements**. Calling the project graph-based is not enough by itself. The graph must be central to the modeling method.

## Course Project Context

- The project is worth **40% of the course grade**.
- It is treated as a **capstone-level deliverable**, not a small course assignment.
- The project should demonstrate real machine learning work rather than only showing that a model can run.
- The work should be strong enough to showcase to a hiring manager, research supervisor, internship program, or startup audience.
- Teams may contain up to three students.
- Expectations remain the same regardless of team size.
- Projects are graded competitively after the baseline requirements are met.

## Option A Requirements That Apply to Us

### Problem Definition and Fit

We must clearly define:

- The real-world problem being solved
- The exact decision being automated, supported, or augmented
- The realistic user, decision-maker, organization, or deployer
- Who would realistically use, deploy, or pay for the system
- Why the problem is important
- Measurable success criteria
- Why a non-AI solution is insufficient
- Why machine learning is appropriate beyond simply claiming that it improves accuracy

Vague descriptions such as “AI-powered,” “intelligent,” or “smart” without a concrete decision and measurable impact should be avoided.

### Technical Requirements

The project must include:

- At least one explicit **non-AI baseline**, such as:
  - Rules
  - Heuristics
  - Classical statistics
  - A simple deterministic method
- At least one **ML-based approach**
- A fair comparison between the baseline and ML method
- Justified evaluation metrics
- Proper train, validation, and test methodology where applicable
- Reproducible experiments
- Error analysis
- Failure-case analysis
- Honest limitations
- Discussion of technical and practical trade-offs
- Data preprocessing and leakage prevention
- Clear documentation of the data and task formulation

A pretrained model connected directly to a simple interface is not sufficient unless the project also includes meaningful baselines, evaluation, analysis, and engineering.

## Additional Graph-Based Requirements That Apply to Us

Since our Option A project is graph-based, we must also satisfy all of the following:

### Graph as a Core Modeling Object

The graph must be central to how the model represents and solves the problem. It cannot be used only for:

- Visualization
- Plotting
- Feature storage
- A post-processing step
- Trivial connectivity
- Decorative network diagrams

### Explicit Graph Definition

We must clearly define:

- What each **node** represents
- What each **edge** represents
- What relationships or edge types mean
- Whether the graph is directed or undirected
- Whether it is weighted or unweighted
- Whether it is static or dynamic
- What node, edge, and graph-level features are used
- What prediction or decision is produced from the graph

### Required Non-Graph Comparison

We must compare the graph method against a non-graph method operating on the **same underlying raw data**.

The comparison should make clear:

- What information both approaches receive
- What additional relational structure the graph model uses
- Whether the graph method provides a real performance or practical advantage
- Whether improvements come from graph structure rather than extra data or an unfair experimental setup

### Graph Justification

We must explicitly explain why the graph structure captures information that a flat representation cannot capture adequately.

This justification should connect the graph structure to the real problem, such as:

- Dependencies
- Relationships
- Interactions
- Connectivity
- Neighborhood effects
- Paths
- Communities
- Sequences of linked entities
- Higher-order relational patterns

Graph-based projects that genuinely meet these requirements may receive more lenient consideration because they are technically more complex, but all requirements still need to be demonstrated clearly.

## Responsible ML Requirements

We must explicitly address at least **three** of the following four areas:

1. **Explainability / interpretability**
   - How predictions or recommendations can be understood
   - Which inputs, nodes, edges, or relationships influenced the result
   - What explanations are shown to users

2. **Bias / fairness**
   - Possible unequal performance across groups or categories
   - Dataset imbalance
   - Representation bias
   - Fairness evaluation or mitigation

3. **Privacy / leakage**
   - Sensitive data handling
   - Data access and storage
   - Train-test leakage
   - Identity leakage
   - Privacy risks caused by graph relationships

4. **Robustness / distribution shift**
   - Performance on unseen or changing data
   - Missing or noisy nodes and edges
   - Adversarial or unusual cases
   - Changes in user behavior, data sources, or graph structure

To avoid the gradebook flag, the report and presentation should make the selected Responsible ML areas easy to locate and verify.

## Production and Engineering Requirements

The final system must include:

- A **Dockerized API**
- Clear separation between:
  - Data processing
  - Model logic
  - Serving / API logic
- A reproducible environment
- Clear installation and run instructions
- Reproducible experiments
- A minimal but functional user interface, such as Streamlit or Flask
- A coherent end-to-end demo flow
- A running artifact or deployed service
- A cloud deployment or another accessible running environment
- Evidence that the system works beyond a notebook

## GitHub and Documentation Requirements

The repository should include:

- A clean and logical folder structure
- A complete README
- Setup instructions
- Run instructions
- Environment and dependency details
- Architecture or method documentation
- Data documentation
- Experiment scripts
- Results and evaluation logs
- Baseline results
- Graph and non-graph comparison results
- Ablations where useful
- Failure cases
- Responsible ML discussion
- Limitations and known issues
- Deployment instructions
- API usage instructions
- Demo instructions

## Poster Session Requirements

At the mid-semester poster session, we should be ready to present:

- The problem definition
- The user or decision being supported
- The baseline strategy
- The ML approach
- The graph formulation
- The non-graph comparison
- The deployment plan
- The expected evaluation method
- The Responsible ML plan

Weak or unclear ideas may be rejected at this stage, so the problem, graph justification, baseline, and deployment plan should already be concrete.

## Final Deliverables

The final submission should include:

- A well-structured GitHub repository
- Reproducible experiments
- A running Dockerized API
- A deployed or otherwise accessible running artifact
- A minimal functional UI
- A final presentation
- A live or recorded demonstration as required
- A five-minute presentation followed by Q&A
- Clear evidence that team members understand and own the work

## Final Evaluation Priorities

The course document emphasizes the following:

1. **Problem quality**
   - Realism
   - Clarity
   - Relevance

2. **Baseline rigor**
   - Strength of the non-AI baseline
   - Fairness of comparisons
   - Proper graph versus non-graph comparison

3. **ML soundness**
   - Correct methodology
   - Appropriate evaluation
   - Error and failure analysis

4. **Production thinking**
   - Deployment
   - System structure
   - Reproducibility
   - Functional end-to-end workflow

5. **Critical thinking**
   - Limitations
   - Trade-offs
   - Responsible ML
   - Robustness and failure modes

## Important Grading Notes

- Meeting only the minimum requirements does not guarantee the highest grade.
- Projects are ranked relative to the strength of the cohort.
- A strong cohort may raise the grading threshold.
- Adding many features does not compensate for weak methodology, unclear results, poor robustness, or missing analysis.
- The project should prioritize a convincing problem, fair comparisons, technical rigor, reproducibility, and a working system.
- Our submission should consistently describe the project as **Option A, application-oriented, and graph-based**.
- We should not describe it as Option B unless the project is reformulated around a publishable research question and target venue.

