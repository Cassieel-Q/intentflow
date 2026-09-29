# Design Document Sync

## Purpose

When an implementation changes design, flow, API, field meaning, configuration
behavior, or a security boundary, update the corresponding design record or
spec so the code and its explanation do not drift apart.

## Documents to keep aligned

- `requirements/`: requirements, decisions, contracts, and acceptance.
- `codebase-analysis/`: reusable technical evidence.
- `assistants/`: delegation and collaboration rules.
- `skills/`: reusable workflow rules.
- Project-local documentation such as `README`, `AGENTS`, and `docs`.

Reference documents may require access or user-provided exports. Do not bypass
permissions or request reusable cookies, sessions, or tokens.

## Changes that normally require an update

- API request or response fields.
- State machines, workflows, permissions, or configuration behavior.
- Field meaning, enum semantics, error text, or user-visible rules.
- Authentication, authorization, data isolation, or security boundaries.
- Contracts between modules or repositories.

## Update rules

- Put each fact in the document owned by the relevant scope.
- Do not duplicate large implementation details in requirements.
- Update version notes or changelogs when the document already uses them.
- Do not leave an important contract update only in chat.

## Completion report

After implementation, report:

```text
Documentation impact:
Documents updated:
Documents not updated and why:
```
