# Personal Superflow `grill-me` Design

## Status

Design approved at the direction level. Interaction cadence: one question per
turn. Implementation has not started.

## Problem

The current Superflow repository has rules for requirements, collaboration,
contracts, debugging, TDD, and verification. It does not yet provide a complete
front door for turning a vague product idea into explicit decisions before
writing a PRD or implementation plan.

Without that front door, an AI assistant may begin proposing a solution too
early, treat assumptions as confirmed requirements, ask several unrelated
questions at once, or leave the important decisions only in chat history.

## Goal

Create a personal `grill-me` skill for the Superflow workspace that:

1. Uses a decision-tree model to identify the highest-leverage unresolved
   decision.
2. Asks exactly one question per turn by default.
3. Uses repository files and available evidence before asking the user for
   facts that can be discovered locally.
4. Records confirmed decisions, unresolved questions, and acceptance criteria
   in the active `requirements/<name>/` directory.
5. Stops when the idea is sufficiently decision-complete for the next workflow
   such as PRD writing, design, implementation, or verification.

## Non-goals

- It will not implement product code.
- It will not replace the existing requirements, TDD, debugging, or
  verification skills.
- It will not make irreversible product decisions without the user's answer.
- It will not initially become a general-purpose public plugin.
- It will not copy a third-party `grill-me` implementation unchanged.

## Positioning

Superflow is being optimized first as a personal AI product-workflow system.
The first release should favor clarity, durable records, low cognitive load,
and compatibility with the existing repository layout over broad framework
generality.

## Proposed location

```text
skills/
  personal-grill-me/
    SKILL.md
    references/
      decision-tree.md
      output-records.md
```

The skill will be based on two external ideas:

- Matt Pocock's decision-tree and dependency-aware questioning model.
- Satya's practice of saving a distilled session record rather than leaving
  the result only in the conversation.

The final instructions and output schema will be owned by this repository.

## Interaction contract

### Entry conditions

Use the skill when the user has a product idea, feature proposal, PRD draft,
workflow design, or implementation direction that still contains consequential
ambiguity.

Do not use it for facts that can be read from the repository, naming choices,
routine implementation details, or a completed decision that only needs normal
execution.

### Question loop

For each turn:

1. Read the active requirement and relevant project evidence.
2. Identify the decision frontier: unresolved decisions whose prerequisites
   are already known.
3. Select the single decision with the highest impact on user-visible behavior,
   scope, data, permissions, or acceptance.
4. Explain the evidence and the tradeoff briefly.
5. Give a recommended answer.
6. Ask one direct question and wait for the user's answer.
7. Update the appropriate requirement records after the answer is known.

The skill should not ask the user for repository facts that can be discovered
with local tools.

### Stop condition

Stop grilling when the remaining uncertainty cannot materially change the next
deliverable, or when the user explicitly chooses to proceed with a recorded
assumption. Summarize what is decided, what remains open, risks, and the next
recommended workflow.

## Durable outputs

The active requirement directory is the source of truth. The skill should
create or update only the files relevant to the session:

- `decisions.md`: confirmed product, scope, and technical decisions;
- `open-questions.md`: unresolved questions that still affect behavior or
  acceptance;
- `acceptance.md`: observable success criteria and important failure cases;
- `grill-log.md`: a concise session record containing intent, constraints,
  decisions, assumptions, open questions, and out-of-scope items.

The record must distinguish user-confirmed decisions from assistant
recommendations and unverified assumptions.

## Handoff contract

When the stop condition is reached, the skill returns:

```text
Decision status:
Confirmed decisions:
Recorded assumptions:
Open questions:
Acceptance criteria:
Main risks:
Recommended next workflow:
```

The next workflow may be requirements/PRD drafting, design analysis,
implementation planning, implementation, or verification.

## Acceptance scenarios

1. A vague product idea causes the skill to ask one consequential question,
   not a batch of unrelated questions.
2. A repository fact that can be read locally is discovered without asking the
   user.
3. A user answer is written to `decisions.md` and does not remain only in
   chat.
4. A rejected option or unresolved dependency is preserved in
   `open-questions.md` when it still affects the result.
5. The session produces acceptance criteria before handing off to planning or
   implementation.
6. The skill stops instead of continuing to ask low-value questions after the
   next action is clear.
7. The output never presents an assistant recommendation as a user-confirmed
   decision.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Too many questions slow down useful work | Select one highest-impact question and stop when the next action is clear |
| The skill becomes a generic interview script | Require evidence, decision impact, and a recommended answer for each question |
| Chat decisions are not persisted | Make requirement files the durable output contract |
| Third-party skill behavior conflicts with Superflow | Use external projects as references only; keep local instructions authoritative |
| Requirement directory is not known | Ask for the requirement name only when it cannot be inferred from the workspace |

## Verification plan

Before implementation, run baseline pressure scenarios without the new skill to
observe premature planning, multi-question behavior, assumption drift, and
missing records. After implementation, run the same scenarios with the skill,
validate the skill structure, and inspect the generated requirement artifacts.

## Documentation impact

Expected updates after implementation:

- Add the new skill to `skills/README.md`.
- Add its relationship to requirements and acceptance records to the relevant
  workflow documentation.
- Add a short usage example to the project README if the final invocation is
  stable.

No existing requirements or project-specific private material should be
overwritten.
