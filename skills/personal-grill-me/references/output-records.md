# Output Records Reference

The active requirement directory is the durable source of truth. Use the
smallest update that preserves provenance.

## `decisions.md`

```markdown
| 日期 | 决策 | 来源 | 状态 |
| --- | --- | --- | --- |
| YYYY-MM-DD | <user-confirmed choice> | 用户回答 / local evidence | 用户确认 |
```

Assistant recommendations belong in a clearly labelled note until the user
confirms them.

Before the user answers, the pending question and its recommendation may be
recorded in `grill-log.md` under `待确认`. After the answer, move the result to
the appropriate confirmed decision, assumption, or open-question section.

## `open-questions.md`

Record only unresolved questions that can still change behavior, scope, data,
permissions, cost, or acceptance. Include the dependency that blocks them.

If a requirement directory was created after the user supplied its name,
record that start decision in `decisions.md`; do not treat directory creation
as evidence that the product scope is settled.

## `acceptance.md`

Write observable outcomes, including important failure or boundary cases. Avoid
vague statements such as “works well” or “is user-friendly”.

Record deadlines as delivery constraints separately from evidence that the
product works or that users want it.

## `grill-log.md`

Keep a compact session summary with:

- intent;
- constraints;
- user-confirmed decisions;
- assistant recommendations;
- unverified assumptions;
- open questions;
- out-of-scope items;
- recommended next workflow.
