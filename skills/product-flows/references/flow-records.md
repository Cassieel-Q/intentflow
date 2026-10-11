# Flow records

Recommended files, created only when useful:

- `flows/business-flow.md`: actors, triggers, branch conditions, outcomes and Mermaid source.
- `flows/interaction-flow.md`: the integrated prototype-state map, route IDs, transition labels and Mermaid/HTML/SVG source link. The rendered board should place the corresponding prototype screen or thumbnail inside each state node.
- `flows/states.md`: object states, allowed transitions and guards.
- `flows/sequence.md`: participants, event order and failure/timeout handling.
- `flows/verification.md`: source version, rendered artifact, viewport, legibility, collision and PRD/prototype consistency checks.

Each node needs a corresponding PRD behavior ID or a note explaining why it is context-only. Use `F-xx` for PRD behavior, `Pxx` for prototype state and `L-xx` for core route. Each core PRD path needs a trace into the business flow, integrated interaction flow and applicable prototype state. Keep technical fields in contracts or a technical sequence note, not in product-facing behavior descriptions.
