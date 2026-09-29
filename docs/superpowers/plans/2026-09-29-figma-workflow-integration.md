# IntentFlow Figma Workflow Integration Plan

> **For agentic workers:** Implement the approved design in `docs/superpowers/specs/2026-09-29-figma-workflow-integration-design.md` task by task and verify each boundary.

**Goal:** Add reusable Figwright-informed Figma skills, integration documentation, and representative QA evidence to IntentFlow, then clean generated artifacts.

**Architecture:** Copy only the two skill trees and their focused references into IntentFlow, add a thin IntentFlow integration layer, and keep the Figwright MCP/plugin source external. Store only two representative screenshots as examples.

**Tech Stack:** Markdown, PNG evidence, Git, PowerShell verification. No new runtime dependency in IntentFlow.

## Global Constraints

- Preserve `G:\myself\figwright` unchanged.
- Do not copy `node_modules`, browser profiles, plugin bundles, or generated runtime output.
- Keep MIT attribution for copied Figwright material.
- Keep `figma-to-real-feature` as the product/API integration gate.
- Delete only the directories listed in the approved cleanup policy.

---

## Task 1: Add the design record and Figwright-informed skills

**Files:**
- Create: `skills/figma-build/SKILL.md` and its four `references/*.md` files.
- Create: `skills/figma-codegen/SKILL.md` and its six `references/*.md` files.
- Modify: `skills/README.md`.

- [ ] Copy the two approved skill trees from `G:\myself\figwright\skills`.
- [ ] Add an IntentFlow ownership note to each skill entrypoint.
- [ ] Verify every relative reference resolves inside IntentFlow.
- [ ] Link both skills from `skills/README.md`.

## Task 2: Add integration docs, attribution, and QA examples

**Files:**
- Create: `docs/figma/README.md`.
- Create: `docs/figma/figwright-integration.md`.
- Create: `docs/figma/qa-examples.md`.
- Create: `docs/figma/qa-examples/native-v3-inner-final-77-2323.png`.
- Create: `docs/figma/qa-examples/native-v3-phone-final-77-2136.png`.
- Create: `THIRD_PARTY_NOTICES.md`.
- Modify: `00-项目索引.md`, `00-当前状态.md`, `DECISION_LOG.md`, `INTENTFLOW.md`.

- [ ] Document workflow order, MCP/plugin dependency, and handoff boundaries.
- [ ] Document the exact external source paths and license attribution.
- [ ] Copy and visually inspect the two representative screenshots.
- [ ] Add the Figma workflow to the project index and current state.

## Task 3: Verify and clean generated artifacts

**Files:**
- Delete only the approved external artifact directories listed in the design.
- Modify: `docs/superpowers/specs/2026-09-29-figma-workflow-integration-design.md` only if verification reveals a documented mismatch.

- [ ] Verify IntentFlow links, skill references, and image paths.
- [ ] Verify `figwright` is unchanged.
- [ ] Check the IntentFlow diff and Git status.
- [ ] Delete the approved generated and redundant directories.
- [ ] Re-check that the retained source and examples still exist.
