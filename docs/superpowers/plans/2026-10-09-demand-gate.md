# Demand Discovery Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reproducible pre-PRD gate that distinguishes ready, provisional and blocked demand-discovery results.

**Architecture:** A small pure-Python evaluator reads the formal findings Markdown, feedback CSV, product reference CSV and root source register. It returns structured checks and renders a Markdown gate report. The CLI exposes the evaluator without changing any formal findings; tests cover the three outcomes and the CLI path.

**Tech Stack:** Python 3.11+, `csv`, `pathlib`, existing IntentFlow CLI and pytest.

## Global Constraints

- Markdown remains the formal record; the gate report is a derived review artifact.
- Real feedback requires `source_id`; simulated feedback cannot produce `ready`.
- The gate must be case-agnostic and must not add product decisions.
- Missing optional public product references produce a warning unless a required check is explicitly requested.

---

### Task 1: Define the gate contract with failing tests

**Files:**
- Create: `scripts/intentflow_runtime/demand_gate.py`
- Test: `tests/test_runtime_demand_gate.py`

**Interfaces:**
- Produce `evaluate_demand_gate(requirement: Path, feedback_path: Path, findings_path: Path, source_path: Path, products_path: Path | None = None) -> dict[str, object]`.
- Return `status` (`ready`, `provisional`, or `blocked`), `ready_for_prd` (`bool`), `checks` (list of check records), `blockers`, `warnings`, and `next_action`.

- [x] **Step 1: Write failing tests** for a complete traceable case, a simulation-only case, and a missing findings section.
- [x] **Step 2: Run `py -3 -m pytest -q tests/test_runtime_demand_gate.py`** and confirm failure because the evaluator does not exist.

### Task 2: Implement the evaluator

**Files:**
- Modify: `scripts/intentflow_runtime/demand_gate.py`
- Test: `tests/test_runtime_demand_gate.py`

**Rules:**
- Required findings headings are the eight names in `requirements/common/demand-discovery-template.md`.
- A real feedback row without `source_id`, or with a source ID absent from `source.md`, is a blocker.
- A missing required findings section or empty feedback file is a blocker.
- Simulation-only input is `provisional`, never `ready`.
- Missing product references and non-empty open-question content are warnings.

- [x] **Step 1: Implement Markdown heading extraction and CSV/source checks.**
- [x] **Step 2: Implement status calculation and next-action text.**
- [x] **Step 3: Run the focused tests and confirm they pass.**
- [x] **Step 4: Refactor only after the focused tests are green.**

### Task 3: Add CLI and derived Markdown report

**Files:**
- Modify: `scripts/intentflow.py`
- Modify: `scripts/README.md`
- Create: `tests/test_runtime_cli.py` test case

**Interface:**
- Command: `demand-gate --requirement <dir> [--feedback ...] [--findings ...] [--source ...] [--products ...] [--output ...]`.
- Default output: `research/demand-gate.md`.
- Exit code is `0` for `ready` and `provisional`; exit code is `2` for `blocked` while still writing the report.

- [x] **Step 1: Add the failing CLI test for a blocked gate and preserved report.**
- [x] **Step 2: Add parser and report rendering.**
- [x] **Step 3: Run the CLI test and then the full suite.**

### Task 4: Document the workflow boundary

**Files:**
- Modify: `INTENTFLOW.md`
- Modify: `skills/demand-evidence-research/SKILL.md`
- Modify: `requirements/common/templates.md`
- Modify: `requirements/intentflow-lifecycle-2026-10-09/qa-report.md`

- [x] **Step 1: Document that the gate runs before PRD and does not replace user confirmation.**
- [x] **Step 2: Record the three statuses and their allowed next actions.**
- [x] **Step 3: Run the full suite and `git diff --check`.**
