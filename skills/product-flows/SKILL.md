---
name: product-flows
description: Use when a product requirement needs a business path, screen navigation, state transition, or implementation handoff diagram that must stay aligned with its PRD and prototype.
---

# Product Flows

## Entry

Read the current `prd/PRD.md`, `design/state-map.md` if present, confirmed decisions, and existing flows. Create only the diagram types that answer a real review question: business process for actor choices, screen flow for navigation, state diagram for lifecycle behavior, or sequence diagram for important cross-system handoff.

## Required review artifacts

For a reviewable PRD-to-prototype handoff, produce these two source files when the requirement has a user journey:

- `flows/business-flow.md`: actor and business outcome view, including entry, decision, success, failure and empty branches.
- `flows/interaction-flow.md`: one integrated screen/state map for every meaningful prototype state, with labelled arrows, back/return, retry, loop and error routes. The rendered board must include the actual operable prototype screen in an iframe or a screenshot/缩略图 generated from that prototype for each `Pxx` node; a text card, “演示原型” placeholder or node-only mind map is insufficient.

Additional state or sequence diagrams are optional when they answer a separate review question. Do not create decorative diagrams that have no traceable behavior.

## Draw

Store editable diagram source under `requirements/<name>/flows/` and link rendered output when needed. Use stable behavior/state IDs shared with PRD and prototype. Every core route receives an `L-xx` ID and every state receives a `Pxx` ID. The interaction flow must be the single navigable map used for prototype review: each node contains the corresponding screen or screenshot generated from the same `design/prototype.html`, state ID and a short interaction label. If it becomes unreadable, split the rendered view while keeping one source index and route list. A screen flow shows each important page/state and labelled transition; avoid treating decorative screens as separate process steps. A state diagram names allowed transitions, guards and terminal/retry states. A sequence diagram names real participants and messages but does not invent API fields.

Mermaid source is acceptable for compact diagrams; a larger screen canvas can be HTML/SVG when page thumbnails or zoom are useful. Keep the source text so it can be reviewed and revised. See [references/flow-records.md](./references/flow-records.md).

## Verify

Compare every core route with the PRD and prototype. Inspect the rendered diagram at actual reading size: text, arrows and labels must remain legible, within bounds and free of misleading overlap. Fix by changing layout, spacing or splitting diagrams; do not hide a branch to make the picture clean. Install Playwright and a supported browser when visual capture is unavailable, then run `py -3 scripts/intentflow.py capture --requirement requirements/<name> --html flows/interaction-flow.html --output flows/screenshots --page default`; record the viewport, screenshot path and result in `flows/verification.md`.

If a branch requires a product decision not in the PRD, return to `personal-grill-me` or PRD revision. Do not draw a guessed path as a confirmed flow.

The review page should expose business flow and interaction flow alongside the PRD. Each flow node or route must link back to its owning `F-xx` or `Pxx` entry, so a reviewer can open the corresponding prototype state.
