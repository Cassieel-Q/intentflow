# Acceptance records

## `qa/checklist.md`

List the source PRD version and relevant prototype references. Group cases by user journey or feature, then use:

| ID | Behavior ID | Priority | Precondition and action | Expected visible result | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| AC-01 | PRD behavior ID | P0/P1/P2 | Reproducible setup and action | One observable result | 未测 | — |

Use case IDs that survive reorder. Split separate results into separate cases. Include permissions, invalid input, network or dependency failure, retry, duplicate action, and state recovery when those risks exist. Do not pad the checklist with irrelevant generic cases. The interactive review renders four direct status buttons, an editable note field in the last column, a passed-case progress bar, and a link back to the PRD review page.

## `qa/results.md`

Append one row per status change: time, case ID, status, optional build version, optional note. All four statuses can be saved immediately, including when build version and note are blank. Keep previous rows readable and use the newest row per case for the current view.

The readiness summary counts all four statuses and names unresolved P0/P1 cases. A pass rate uses the explicit denominator of executed, applicable cases; report skipped and untested separately.
