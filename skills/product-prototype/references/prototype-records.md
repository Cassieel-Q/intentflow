# Prototype records

## `design/state-map.md`

| State ID | PRD behavior ID | Route ID | Entry/trigger | Visible state | Available action | Next state | Prototype anchor/frame | Asset link | Data status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Use stable IDs across PRD references, HTML anchors, Figma frames, flow nodes and screenshots. `Pxx` is the state ID, `F-xx` the owning PRD behavior and `L-xx` the core route. When a state is not represented, state why it is outside the current review scope. Mark sample data and simulated backend behavior in both the map and the visible prototype.

When the interaction flow is rendered as a board, each `Pxx` entry must have a corresponding screen, iframe or thumbnail in the node. A state map alone does not satisfy the interaction-flow deliverable.

## `design/verification.md`

Record version, viewport/device, tested path, expected states, actual states, screenshot references, visual drift, interaction drift, and unresolved decisions. A Figma screenshot and an HTML screenshot can differ for legitimate platform reasons; state the reason instead of silently picking one as authoritative.
