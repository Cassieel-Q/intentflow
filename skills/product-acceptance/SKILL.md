---
name: product-acceptance
description: Use when a product feature needs executable checks derived from its requirement, prototype, or implementation before test handoff or release review.
---

# Product Acceptance

## Purpose and entry

Build a checkable product acceptance record in the same `requirements/<name>/` directory. Read the current `prd/PRD.md`, `acceptance.md`, design/prototype, flows, decisions, and implementation evidence. Confirmed decisions and the current PRD define expected behavior; a conflicting prototype is a drift finding, not a new requirement. Resolve missing or contradictory expectations through `personal-grill-me` or PRD revision before marking a case as pass.

## Derive cases

Create `qa/checklist.md` only when acceptance work starts. Map every current-scope behavior to one or more cases; include the ordinary user path, important failure and boundary paths, permissions, empty/loading states, persistence/retry, and visible content. Add visual fidelity and tracking checks when those are part of the agreed scope. Prefer one independently executable expectation per case.

Each case needs an ID, source behavior ID, priority, precondition, steps or action, expected observable result, status, and an optional note. Status is **未测 / 通过 / 失败 / 跳过**; start at 未测. A generated checklist is a test design, not a test result. The reviewer can change any status directly. Build version and note are optional; browser/device and evidence location are never required to change or save a status. See [references/checklist-records.md](./references/checklist-records.md).

## Execute and report

When reviewing or testing, append each status change to `qa/results.md`: time, case ID, status, optional build version, and optional note. Do not overwrite earlier entries. The latest entry determines the displayed status. On completion, report untested and failed critical cases, accepted deviations, and release readiness as a recommendation rather than an automatic approval.

Generate an interactive HTML checklist only when requested or useful. The HTML must reflect the Markdown case IDs and current results; each case exposes direct buttons for `未测` / `通过` / `失败` / `跳过`, the last column provides an editable note, and a top progress bar counts passed cases against the total. The optional build version field must not block a click. Include an `打开 PRD` action that opens the current `prd/PRD-review.html` when it exists. Browser state cannot silently become the only result store: status and notes must be persisted to `qa/results.md` through the local review service or exported for reconciliation. This skill does not replace the project's final-review decision.
