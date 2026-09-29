# Decision Tree Reference

Use a small decision tree rather than a flat questionnaire.

## Frontier rule

The frontier contains decisions whose prerequisites are settled. A decision
that depends on an unresolved audience, scope, or success definition belongs to
a later round. Do not guess the parent decision in order to ask a child
question.

## Priority rule

Rank frontier decisions by their effect on:

1. User-visible behavior;
2. Product scope and target user;
3. Data, permissions, or irreversible side effects;
4. Acceptance and measurable success;
5. Cost, schedule, and implementation complexity.

Ask the highest-ranked decision that cannot be discovered from local evidence.

## Example

```text
Target user → core problem → promised outcome → MVP boundary → acceptance
                  ↓
              data/permission constraints
```

If the target user is unknown, do not finalize an MVP or pricing model first.
If the promised outcome is unknown, do not turn a list of features into a PRD.
