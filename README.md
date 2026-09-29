# IntentFlow

IntentFlow is a personal workspace for turning product intent into clear
decisions, requirements, designs, implementation tasks, and verified results
with AI assistants.

It keeps decisions, implementation boundaries, verification evidence, and
follow-up work visible and reusable. The repository is based on the downloaded
Superflow workflow, adapted for one person's long-lived product work.

## Layout

```text
assistants/       collaboration roles and delegation rules
requirements/     requirement templates and decision records
skills/           reusable workflow skills
scripts/          small workspace maintenance scripts
todos/            active follow-up work
docs/             design documents and implementation plans

## Start a product idea

1. Create a requirement directory under `requirements/<name>/`.
2. Use `skills/personal-grill-me/` to clarify the highest-impact decision one
   question at a time.
3. Record decisions, open questions, and acceptance criteria in that directory.
4. Hand off to PRD, design, implementation, or verification workflows.
```

## Principles

- Separate user decisions from reference material.
- Clarify business meaning before implementation.
- Keep implementation ownership and write boundaries explicit.
- Prefer evidence-backed verification over assumptions.
- Use TDD when the change risk justifies it.
- Keep temporary experiments distinguishable from retained tests.
- Review the final change at the level of user-visible behavior.

The repository is intentionally personal rather than tied to one product.
Private project material should remain in its own requirement or project
workspace and should not be copied into public source without review.
