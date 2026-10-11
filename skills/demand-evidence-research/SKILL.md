---
name: demand-evidence-research
description: Use when a product opportunity, user pain point, competitor claim, or feature proposal needs verification through existing materials or publicly available evidence before requirements are drafted.
---

# Demand Evidence Research

## Purpose

Run a case-driven demand study with traceable evidence. Start from a concrete
domain and situation, collect real feedback or user-provided examples, group
the underlying difficulties, compare relevant alternatives, and identify the
smallest product decisions worth carrying forward. This skill investigates the
need; it does not decide the user's product intent or write a PRD.

## Route in

1. Find the active `requirements/<name>/` directory from the named requirement or current task. Reuse it across discovery and later outputs. Create it only when the user has authorized starting the requirement; create `research/` only when research starts.
2. Read the requirement records and existing sources. Create a research brief
with the domain, user/context, situation, research question, candidate source
channels, and what evidence would change the next action. Mark unknown items as
unknown. A concrete example can start research even when the long-term product
scope is open.
3. If an unknown product choice would materially change the search scope, use `personal-grill-me` for that one decision first. A bounded exploratory scan may proceed while the segment is open, but cannot establish a segment-specific conclusion.
4. If the evidence is already sufficient for the next deliverable, skip research and hand off.

## Investigate

- Prefer user-provided original materials and accessible primary sources: actual user feedback, app-store reviews, community discussions, product help/pricing pages, official statistics, or original research. Use secondary summaries only with their limits stated. Do not claim to have scraped a platform when access was unavailable.
- For each material claim, save a direct URL or local path, publisher/platform, original date when available, access date, population/context, collection method or sample size when known, and limitations. Follow [references/evidence-records.md](./references/evidence-records.md).
- Group observations by the underlying job or obstacle. Compare alternatives and counterevidence. Treat visible comments as a selected sample, not a population estimate; do not invent frequencies, market size, sentiment scores, or precise rankings.
- Keep **证据** (what the source shows), **推断** (what it may mean), and **建议** (a proposed product response) separate. Label each claim's confidence and applicable scope. Synthetic or simulated feedback is allowed only as a clearly labelled format demonstration; it never counts as user or market evidence.

For a case study, use the structure in [the demand discovery template](../../requirements/common/demand-discovery-template.md) and this order when the inputs support it:

1. **案例整理**：list the observed situation, user action, obstacle, consequence,
   and desired result for each example. Do not turn a single example into a
   population claim.
2. **痛点聚类**：group examples by the underlying obstacle. Report a count only
   when the collection scope and denominator are known; otherwise use a
   qualitative cluster label.
3. **替代方式对照**：compare the current workaround and relevant alternatives
   on the dimensions visible in the evidence. Do not invent competitor scores.
4. **机会判断**：write a few bounded opportunity hypotheses, each linked to
   the evidence and a validation question. These remain assistant suggestions.

If the user asks to test the workflow without real feedback, create a separate
`research/demo-inputs.md` file and label every row `模拟演示数据，不是用户证据`.
It may test clustering and report layout, but it cannot validate demand.

When an HTML review is useful, keep the formal eight-part findings record in
Markdown and derive the view with `scripts/intentflow.py demand-report`. The
optional `research/feedback.csv` separates `real` and `simulation` rows;
real rows require `source_id`. `research/products.csv` may hold public product
pages, observed capabilities and items that remain unverified. The generated
view should show evidence state, clusters, public references, opportunity
hypotheses and validation metrics, with filters and export controls. It must
not add a product decision that is absent from the Markdown record.

Before handing the work to `product-prd`, run `scripts/intentflow.py demand-gate`.
The gate returns three states:

- `ready`: traceable real feedback and the required discovery record are present; PRD work may begin.
- `provisional`: the record is structurally usable but relies on simulation or another non-blocking limitation; keep the next output exploratory.
- `blocked`: a required section, feedback file, or source link is missing or cannot be traced; fix it before product requirements are drafted.

The gate is a quality boundary, not a user decision. Keep its Markdown report
beside the research materials and preserve unresolved conclusions as open
questions.

## Record and hand off

Append source identities to `requirements/<name>/source.md` without overwriting existing material, write the brief to `requirements/<name>/research/demand-brief.md`, and write findings to `requirements/<name>/research/demand-findings.md`. An optional interactive view may be generated on request, but Markdown remains the formal record. Record contradictions and missing evidence. Preserve user-confirmed choices in `decisions.md`; research findings alone are not user-confirmed product decisions.

Return the question investigated, evidence with source links, inference, alternatives, gaps, and the next decision or deliverable. If research exposes a consequential product choice, hand it to `personal-grill-me`. Stop when further searching is unlikely to change the next deliverable; if evidence is weak, say so and recommend the smallest useful validation step.

## Red flags

- A polished insight card without source-level traceability.
- Simulated reviews presented as real feedback.
- A few public posts converted into prevalence or market-size claims.
- Asking the user to supply public facts that can be checked directly.
- Repeating broad searches after the decision can already be made.
