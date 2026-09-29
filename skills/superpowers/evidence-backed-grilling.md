# Evidence-Backed Questions

## Purpose

Use evidence before asking a question, and ask only one question when the
answer could change the implementation or acceptance result.

## Trigger this workflow when

- The user-visible result is unclear.
- API, state, permission, ownership, or data source is uncertain.
- Multiple options would change behavior, compatibility, or verification.
- Requirement text, user intent, and code evidence conflict.
- A delegated assistant reaches a decision outside its scope.

## Do not trigger it for

- Facts already established by code or documents.
- Naming, formatting, or other local implementation details.
- Generic questions asked only to appear thorough.
- Several unrelated questions bundled together.

## Question format

Ask one question with:

```text
Evidence already confirmed:
Current disagreement:
What option A means:
What option B means:
Recommendation:
One-line confirmation needed:
```

If the decision does not require user authorization, choose from the evidence
and record the reason.

## Persistence

Write the answer to the document that owns the decision, such as a requirement
record, technical evidence note, assistant rule, or reusable skill. Keep the
evidence anchor with important conclusions.

## Delegation boundary

An assistant must report to the main session when it needs to change another
repository, a shared contract, a state, a permission, a route, an acceptance
rule, or any user-approved business decision.
