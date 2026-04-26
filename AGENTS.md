# AGENTS Workspace Rules

These rules apply to future agent work in this repository unless the user gives a more specific instruction.

## Git Workflow

* Work in the desktop repository at `C:\Users\hasan\Desktop\EECE490 project\Melodious`.
* Keep work aligned with the project checkpoint branches (`v0.1`, `v0.2`, etc.) and create a related branch before any meaningful implementation work if needed.
* Do not commit directly to `main` unless the user explicitly requests it.
* Commit only coherent units of work that match the current project phase.
* Do not push `docs/status/Hasan_Instructions.md` or `docs/status/Hasan_Documentation.md` unless the user explicitly asks for that.
* Do not commit temporary sandbox or debug artifacts such as ad hoc temp folders, generated caches, or local-only experiment residue.

## Code Quality

* Keep code clean, explicit, and well-organized.
* Add clear comments and docstrings for public functions, API boundaries, data contracts, and non-obvious graph logic.
* Prefer simple interfaces and predictable payload contracts over clever abstractions.
* Keep parsing, graph construction, alignment, backend, and export responsibilities separated by module.
* Preserve the cleaned repo layout: `src/` for source code, `tools/` for helper scripts, `tests/` for tests, and generated outputs outside the source tree.

## Documentation Discipline

* Update `docs/status/Hasan_Instructions.md` whenever the current phase, blockers, or next steps change.
* Update `docs/status/Hasan_Documentation.md` for every meaningful implementation checkpoint, integration result, or handoff-related finding.
* Before starting new work, check the relevant sections in `docs/status/Hasan_Documentation.md` to avoid duplicating discarded approaches or stale assumptions.
* Record integration outputs, artifact counts, contract changes, and backend milestones clearly enough to reuse in the final report.

## Analysis Expectations

* Prefer measured repo-side evidence over guesses.
* When reporting integration quality, separate true measured results from assumptions or projections.
* Track the exact payloads, graph artifacts, and summary files used to support conclusions.
* Keep enough technical detail in the documentation to justify design choices around parsing, graph construction, alignment, and backend integration.

## Collaboration Contract

* Hasan owns the MUSCIMA parsing, graph, alignment, and backend integration side of the project.
* Ahmad owns the detector, training, detector baselines, and model-side evaluation.
* Preserve the shared detector payload contract once sample payloads or handoff files are in use.
* Treat `sample_detections/`, MUSCIMA reference payloads, and agreed request/response schemas as stable interfaces unless both sides intentionally change them.
* If a contract changes, update code, tests, docs, and sample payloads together.
* Build backend and integration work so it can run on shared sample payloads first, then accept Ahmad's real outputs with minimal changes.
