---
name: personal-grill-me
description: Use when a product idea, feature proposal, PRD, workflow, or design still contains consequential ambiguity and needs one focused decision clarified before planning or implementation.
---

# Personal Grill-Me

## Purpose

Turn an unclear product intention into a decision-ready handoff for IntentFlow.
The skill is a decision clarifier, not a PRD writer, implementation planner, or
bug reviewer.

## Route in

Use this skill only when an unresolved product choice could materially change
the next research question or deliverable. If the audience, problem, and scope
are clear but the claimed pain or opportunity lacks evidence, use
`demand-evidence-research`. If both decisions and evidence are sufficient,
proceed to the relevant delivery workflow. Do not ask a question merely to run
Grill-Me. An evidence scan can happen before or after a clarification when its
scope is clear; it cannot silently decide an unknown audience for the user.

## Core rule

Ask **one** highest-impact question per turn. Do not write a full solution to
avoid asking. Do not present an assistant recommendation as a user-confirmed
decision.

When the user explicitly asks for all questions at once, switch to a single
structured discovery questionnaire. Group only questions about the need itself:
who encounters the situation, what they are trying to do, what is difficult,
how they handle it today, what the impact is, what result they want, what
evidence or examples exist, and what constraints apply. Do not turn the
questionnaire into a list of page, button, interaction order, trigger,
algorithm, or feature-choice questions. Those belong to PRD or design after the
need is clear.

For a demand-discovery example, record the questionnaire answers as evidence
about the problem and desired outcome. Keep any previously volunteered product
preferences in a clearly marked deferred-design note; do not use them to claim
that the underlying need has been validated.

## Start

1. Locate the active `requirements/<name>/` directory in this order: an
   explicitly named requirement, the current task context, or a single
   matching directory. If none can be inferred, ask only for the requirement
   name. After the user supplies a name, create the standard requirement files
   only if the user has authorized starting that requirement.
2. Read the relevant requirement files and local evidence before asking for a
   fact that can be discovered locally.
3. Build the decision frontier: unresolved decisions whose prerequisites are
   already known.
4. Choose the frontier decision with the largest effect on user-visible
   behavior, scope, data, permissions, cost, or acceptance.

If the user gives a broad label such as “大学生” but says the exact target is
undecided, treat the segment as an unverified assumption. Do not finalize an
MVP, pricing model, or success metric on that label alone.

## Question format

Use this compact shape:

```text
已确认证据：<what the files or prior answers establish>
当前决策：<the one unresolved choice>
选项 A：<visible consequence>
选项 B：<visible consequence>
推荐：<best current choice and why>
请确认：<one direct question>
```

Use open-ended wording when fixed options would hide an important possibility,
but keep it focused on the same single decision rather than asking for a broad
brief.
Ask the next question only after the user answers the current one.

## After each answer

Update the active requirement records:

- `decisions.md`: user-confirmed decisions, with date and evidence;
- `open-questions.md`: unresolved dependencies or explicitly deferred choices;
- `acceptance.md`: observable success and important failure conditions;
- `grill-log.md`: concise intent, constraints, assumptions, decisions, and
  out-of-scope items.

Keep three labels separate: **用户确认**, **助手建议**, **未验证假设**.
Do not silently promote a recommendation or a convenient default to a decision.
Use [references/output-records.md](./references/output-records.md) for the
record shape.

If the user delegates a choice such as “商业模式你自己定”, propose a default
and record it as **助手建议** or **未验证假设**. Ask for confirmation before
using it as a hard acceptance condition or irreversible scope decision.

If the user says “不要问太多”, keep the one-question rule, choose only the
highest-impact unresolved decision, and stop as soon as a useful next
deliverable can be produced. Do not invent a fixed question quota.

## Stop

Stop when the remaining uncertainty cannot materially change the next
deliverable, or when the user explicitly chooses to proceed with a named
recorded assumption. A vague deferral such as “以后再说” remains an open
question when it changes scope, audience, pricing, or acceptance.
Return:

```text
Decision status:
Confirmed decisions:
Recorded assumptions:
Open questions:
Acceptance criteria:
Main risks:
Recommended next workflow:
```

The next workflow may be `demand-evidence-research`, PRD drafting, design
analysis, implementation planning, implementation, or verification.

When the user supplied a deadline, carry the wording into the handoff as a
delivery constraint. Preserve relative wording such as “月底前” unless a
calendar date is explicitly known; do not invent a date or treat the deadline
itself as evidence that the product outcome is validated.

## Red flags

- Drafting a complete PRD before resolving the highest-impact decision.
- Asking several unrelated questions in one turn.
- Asking the user for a repository fact that local inspection can answer.
- Treating "暂定", "以后再说", or an assistant default as confirmed.
- Continuing to ask low-value questions after the next action is clear.

For the dependency model, read [references/decision-tree.md](./references/decision-tree.md).
