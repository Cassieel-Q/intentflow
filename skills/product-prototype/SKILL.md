---
name: product-prototype
description: Use when a product requirement needs an operable prototype, page-state demonstration, or consistency check between PRD and design before implementation or review.
---

# Product Prototype

## Entry and choice

Use the active `requirements/<name>/` directory. Read confirmed decisions, `prd/PRD.md`, existing design assets, and flows. Choose the smallest reviewable form: connected Figma design through `figma-build`, a standalone HTML prototype, or both when the handoff requires it. Reuse existing design tokens and components when present. A prototype demonstrates behavior; it cannot create new product scope by itself.

## State contract

Before drawing screens, list each meaningful page/state in `design/state-map.md`: stable `Pxx` ID, entry condition, visible content, available action, destination or state change, relevant PRD `F-xx` behavior ID, route `L-xx` IDs, prototype anchor/hash or frame link, and variant (empty/loading/success/failure/permission). Keep only states needed to understand the current-scope behavior. See [references/prototype-records.md](./references/prototype-records.md).

The state map is the bridge between the PRD, interaction flow and prototype. A state omitted from the prototype must say why it is out of scope. Every feature in the PRD feature table must either map to one or more `Pxx` states or explicitly say “尚未创建”.

For an HTML path, write `design/prototype.html` as a locally openable artifact with navigation and working interaction for the agreed paths. Use stable page IDs and hash navigation when useful. Mocked backend responses and sample data must be visibly identified; do not imply real integration. Keep preview/embed behavior isolated from the formal Markdown PRD. If using `postMessage`, validate sender origin and message shape.

The generated PRD review page must provide a dual-pane preview: the left side contains the PRD, primary-section navigation and flow boards, and the right side contains the prototype state selected from the state map. PRD headings, feature rows and flow nodes carry their `F-xx`/`Pxx` mapping. The feature-detail table itself must expand `[[prototype:Pxx]]` markers into the corresponding operable prototype iframe; a plain `Pxx` label is not an acceptable visual substitute. Each prototype declares a canonical viewport with `data-intentflow-viewport="WIDTHxHEIGHT"` on its body when it differs from the default `520x900`; table embeds scale that whole canvas proportionally and must not trigger responsive reflow, crop or distortion. Scrolling or clicking on the left selects the right state; the state selector on the right can locate the mapped PRD section. The interaction-flow board itself must contain the corresponding actual prototype screen or screenshot in each state node; the right pane is an additional focused preview. The preview must support state hash navigation, zoom and an explicit unmapped-state message.

For a Figma path, follow `figma-build` and keep node/frame links in the state map. An additional design tool is optional and must not become a mandatory dependency of IntentFlow.

## Verify and hand off

Walk the main path and each important failure/empty state. Check click targets, text, keyboard basics, viewport behavior, and consistency with the PRD's visible result. When capture dependencies are missing, install Playwright and a supported browser before declaring visual review unavailable. Compare screenshots at the intended size; record the viewport, screenshot path, observed mismatch and decision owner in `design/verification.md`. A screenshot captures one state, so it does not replace interaction testing. If the design exposes a missing product rule, return it to `personal-grill-me` or PRD revision before implementation.
