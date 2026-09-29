# IntentFlow Foundation and Personal Grill-Me Implementation Plan

> **For agentic workers:** Follow the approved design in `docs/superpowers/specs/2026-09-29-intentflow-grill-me-design.md`. Execute each task with evidence and review before moving on.

**Goal:** Turn the empty IntentFlow repository into a personal AI product-workflow workspace based on the historical reference workflow, with a usable, durable `grill-me` skill.

**Architecture:** Keep the repository Markdown-first. The project README and status files route tasks; `requirements/` owns requirement records; `skills/personal-grill-me/` owns the one-question decision interview; existing engineering rules remain available as downstream workflows.

**Tech Stack:** Markdown, Git, PowerShell for local verification. No runtime dependency is required for the skill.

## Global Constraints

- The first release is a personal AI product-workflow system, not a public general-purpose framework.
- Ask one highest-priority product decision per turn.
- Discover repository facts before asking the user.
- Distinguish user-confirmed decisions, assistant recommendations, and unverified assumptions.
- Persist durable outcomes in the active `requirements/<name>/` record.
- Preserve the downloaded historical reference directory outside this repository.
- Do not push to GitHub as part of local implementation.

---

## Task 1: Establish the repository foundation

**Files:**
- Create: `README.md`, `00-项目索引.md`, `00-当前状态.md`, `DECISION_LOG.md`, `05-QA-Gate.md`
- Create: `docs/superpowers/specs/2026-09-29-intentflow-grill-me-design.md`
- Copy and adapt: `assistants/`, `codebase-analysis/`, `codebases/`, `requirements/`, `scripts/`, `skills/`, `todos/`, `.gitignore`

**Interface:** A new session can read the index and status, locate the relevant workflow, and identify current versus reference material.

- [ ] Verify the source file inventory and the empty target repository.
- [ ] Copy the reusable upstream folders without touching the source directory.
- [ ] Add the approved design document and personal project entry files.
- [ ] Verify the README, indexes, and links consistently identify this project as IntentFlow.
- [ ] Verify all expected files exist and no source files were overwritten.

## Task 2: Create and validate `personal-grill-me`

**Files:**
- Create: `skills/personal-grill-me/SKILL.md`
- Create: `skills/personal-grill-me/references/decision-tree.md`
- Create: `skills/personal-grill-me/references/output-records.md`
- Modify: `skills/README.md`, `requirements/README.md`, `requirements/common/templates.md`

**Interface:** Given an idea or draft, the skill reads local evidence, asks one consequential question, records the answer in requirement files, and hands off when the next workflow is ready.

- [ ] Run baseline pressure scenarios without the new skill and record observed failures.
- [ ] Write the smallest skill that addresses the observed failures and the approved design.
- [ ] Add decision-tree and durable-record references only where they reduce entrypoint size.
- [ ] Validate `SKILL.md` metadata and run the same scenarios with the skill.
- [ ] Inspect generated records for provenance and source-of-truth clarity.

## Task 3: Integrate and hand off

**Files:**
- Modify: `README.md`, `00-当前状态.md`, `05-QA-Gate.md`, `DECISION_LOG.md`
- Create or modify: `requirements/intentflow-foundation/` records for this decision

**Interface:** A user can start from the root README or index, invoke the decision workflow, and see where decisions and acceptance criteria are kept.

- [ ] Check links, file inventory, Markdown placeholders, and local script behavior where feasible.
- [ ] Compare the implementation against every design acceptance scenario.
- [ ] Review `git diff` and `git status` for accidental files or upstream changes.
- [ ] Commit the verified local result; leave publication to GitHub for a later step.

## Self-review

The three tasks cover the approved positioning, skill behavior, durable output,
repository routing, and verification. The plan has no unresolved implementation
placeholder. The only external action is cloning the user's empty repository;
publishing is outside this plan.
