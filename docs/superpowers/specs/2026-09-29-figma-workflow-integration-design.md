# IntentFlow Figma Workflow Integration Design

## Status

Approved by the user on 2026-09-29. Implementation may proceed.

## Goal

Extend IntentFlow from a product-decision workspace into a product-to-Figma-to-code workflow while keeping the product context, API truth, and verification records in IntentFlow.

## Evidence

- `G:\myself\figwright\skills\figma-build`: Figma construction workflow with component, variable, style, motion, and screenshot guidance.
- `G:\myself\figwright\skills\figma-codegen`: Figma-to-code workflow with component maps, token maps, responsive handling, asset export, design diffs, and browser verification.
- `G:\myself\figwright`: MIT-licensed source project containing the Figwright MCP server, plugin, shared protocol, and skills.
- `G:\myself\figma-qa-native-v3-inner-final\77-2323.png` and `G:\myself\figma-qa-native-v3-phone-final\77-2136.png`: representative final visual QA evidence.

## Architecture

IntentFlow will own the workflow layer. Figwright remains an external tool source and is not copied as a second MCP application.

```text
product intent
  → personal-grill-me
  → figma-build / Figma design
  → figma-codegen / grounded code
  → figma-to-real-feature / API, route, state, and permission integration
  → browser and screenshot verification
```

## Changes

1. Add `skills/figma-build/` and `skills/figma-codegen/`, including the focused references required by each skill.
2. Add IntentFlow-specific integration guidance under `docs/figma/`.
3. Add third-party attribution for the copied MIT-licensed skill material.
4. Add the two representative QA screenshots as optional local examples, without copying browser caches or all historical snapshots.
5. Preserve `G:\myself\figwright` unchanged as the external source project.
6. Delete only the confirmed generated artifacts and redundant screenshot directories outside IntentFlow.

## Boundaries

- The new skills require a working Figwright MCP server and Figma plugin; the skills alone do not provide those tools.
- IntentFlow's existing `figma-to-real-feature` remains the product integration gate.
- Figma is a design input. Existing routes, components, API contracts, permissions, and acceptance criteria remain the implementation truth.
- Historical screenshots are evidence, not reusable UI specifications.

## Acceptance

- `figma-build` and `figma-codegen` are discoverable from `skills/README.md`.
- Each skill's referenced files resolve locally.
- `docs/figma/README.md` explains setup dependency, workflow order, and handoff to `figma-to-real-feature`.
- `THIRD_PARTY_NOTICES.md` records the Figwright source and MIT license.
- The two retained QA examples are linked from `docs/figma/qa-examples.md`.
- No generated `node_modules`, browser profiles, plugin bundles, or redundant historical screenshot directories are copied into IntentFlow.
- IntentFlow's Git worktree is clean after the integration commit.

## Cleanup policy

Delete after integration verification:

- `figwright-plugin-v0.5.0`
- `figwright-runtime`
- `html-capture-v2`
- `figma-qa-v1`
- `figma-qa-v2`
- `figma-qa-v2-overlays`
- `figma-qa-v2-refresh`
- `figma-qa-native-v3`
- `figma-qa-native-v3-phone`
- `figma-qa-html-v2`

Keep:

- `figwright`, as the external source project;
- `figma-qa-native-v3-inner-final` and `figma-qa-native-v3-phone-final` until their representative images are copied and verified.
