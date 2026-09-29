# Main Session and Assistant Collaboration

## Roles

The main session owns requirement framing, task decomposition, delegation,
cross-task coordination, verification summaries, and durable workflow rules.

Specialized assistants may investigate, implement, or verify a bounded task.
They must report their assumptions, evidence, changed files, validation, and
remaining risks.

## Default flow

1. Clarify the user-visible goal and boundaries.
2. Split work by ownership and file scope.
3. Let assistants investigate or implement in parallel only when their write
   scopes do not overlap.
4. Keep shared contracts and conflicting conclusions under main-session
   control.
5. Verify the result at both code and user-behavior levels.
6. Record stable conclusions where the next session can find them.

## Messaging

- Messages that do not change the current implementation direction enter a
  queue and should not interrupt an active task.
- A message is urgent only when continuing could cause a materially wrong
  implementation, data/security risk, or violation of an approval gate.
- Before sending a message, check whether the target is actively working.
  Do not terminate an active task merely to deliver a non-urgent update.
- Shared contracts are broadcast by the main session; assistants should not
  assume another assistant's implementation details.

## Lifecycle

Every delegated thread is either `persistent` or `one-off`.

- `persistent` is for durable roles or workstreams that need future context.
- `one-off` is for a bounded investigation, probe, or verification.
- The creator records the lifecycle, archive owner, and archive condition.
- A completed `one-off` thread is archived after its result is consumed and
  any durable evidence is recorded.
- Archiving must never interrupt a task that is still running.

## Implementation gates

- If business meaning is unclear, stop and present the question, impact,
  options, and recommendation.
- Before changing behavior, state the intended design, affected interfaces or
  data, state transitions, tests, validation, and risks.
- Approval-sensitive changes remain read-only until the required approval is
  recorded.
- A local implementation may be simple, but it must not silently redefine a
  shared contract.

## Final review proposal

Before final acceptance, the main session must propose an appropriate review
depth and let the user choose:

- Full review for broad or high-risk changes.
- Lightweight review for bounded changes that still benefit from a summary.
- No special review for low-risk changes such as isolated copy or styling.

The proposal is mandatory; full review is not. Normal build, test, and
acceptance checks still apply.
