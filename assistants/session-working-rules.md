# Session Working Rules

## Durable context

Persist stable decisions, reusable commands, known pitfalls, ownership
boundaries, and verification evidence. Keep temporary exploration separate
from durable project records.

Reference documents provide context; they do not override an explicit user
request.

## TDD and temporary tests

Use TDD when the change risk and existing project conventions justify it.
Classify test artifacts as:

- retained tests,
- phase-specific tests,
- temporary probes or reproductions.

Temporary artifacts must be visibly marked and removed or promoted before
commit. Run the repository's temporary-artifact check when one exists.

## Assistant coordination

- Keep write scopes explicit and non-overlapping.
- Route cross-module contracts through the main session.
- Queue non-urgent updates instead of interrupting active work.
- Escalate ambiguity before encoding it in code.
- Record the evidence behind important conclusions.

## Verification

Verification should match risk. It may include focused tests, builds, smoke
checks, manual flows, visual review, or a final diff audit.

Before final acceptance, proactively propose full, lightweight, or no special
review. The user decides whether the additional review is needed and how deep
it should be.
