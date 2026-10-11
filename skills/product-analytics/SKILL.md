---
name: product-analytics
description: Use when actual product data, experiment results, or metric exports need a reproducible product analysis and iteration recommendation.
---

# Product Analytics

## Purpose and entry

Analyze a defined question from actual data. Reuse the active `requirements/<name>/` directory; analysis may also start a named requirement when authorized. Read the current PRD goals, event definitions, source files, earlier reports, and version/status records. Ask for only a missing definition that would materially change a calculation; choose and label a reversible analytical convention when appropriate.

## Data contract

Before calculating, record source path/link, extraction date, observation window and timezone, unit of analysis (person/session/event), keys, duplicates, missingness, eligibility filters and exclusions. Preserve raw files; write transformations and derived tables separately. For each metric define numerator, denominator, population, time window, aggregation and baseline. If a field or denominator is absent, do not invent a percentage or chart. See [references/metric-records.md](./references/metric-records.md).

If person IDs are missing, do not calculate a person-level conversion rate from those records. A session- or event-level analysis is a different metric and needs its own valid key and label. If deduplication, stage order, or attribution window can materially change the conclusion and cannot be established from product definitions, show bounded alternatives or ask for the one decision; do not silently pick a convention and report one definitive rate.

## Analyze

Compute the requested KPI, trend, funnel, cohort or segment comparison only where data supports it. Verify that funnel stages use compatible populations and that counts, percentages and labels can be recomputed from the recorded inputs. Distinguish an observed change from a possible explanation. Examine alternative explanations such as instrumentation changes, traffic mix, seasonality, missing data and sample size. For experiments, state assignment and analysis population before interpreting differences.

Write `analytics/report.md` with question, data contract, formulas, tables/figures, observations, limits, 2–3 actionable options and the smallest next validation. Place reusable definitions in `analytics/metric-definitions.md`; register source identities in `source.md`. With no real data, produce only a visibly labelled format demonstration, never an apparent product result.

## Interactive analysis view

Markdown is the formal record; the interactive view is an optional, derived deliverable (default `analytics/report-review.html`, or a dedicated analytics dashboard). Build it when a reviewer benefits from exploring the analysis instead of only reading it. It must never replace or diverge from the Markdown numbers.

### Panel menu (recommended starting set, not a fixed template)

Choose panels from this menu according to the analysis question and what the data can support; add, drop, rename or reorder freely. Do not render a panel whose numbers cannot be computed.

1. **分析总览 Overview** — headline metric cards, sample size, observation window and timezone, material status (真实 / 模拟 / 不可计算), and a one-line conclusion.
2. **转化漏斗 Funnel** — ordered stages with counts and rates; toggle conversion base (相对首阶段 / 相对上一阶段); hover shows count and rate per stage. Only where stages share a compatible population and key.
3. **每日趋势 Trend** — daily or time-series metric line/bar; switchable metric and time range. Requires real timestamps; otherwise mark as 不可计算.
4. **分群诊断 Segments** — group comparison across one switchable dimension (错误簇 / 题型 / 提示使用 / 难度 etc.); show per-segment numerator, denominator and rate. Never infer a segment from an aggregate.
5. **洞察归因 Attribution** — separate 观察 (observed) from 解释 (hypothesis); expandable evidence chains, counter-patterns and alternative explanations. A change is an observation; a mechanism is a hypothesis until tested.
6. **行动建议 Actions** — prioritised, checkable recommendations, each labelled 助手建议·待用户确认; link each action to the observation it addresses.
7. **数据质量 Quality** — missing fields, deduplication, stage-order checks, eligibility, and a 可计算 / 不可计算 / 演示 marker per metric.

### Interaction and fidelity rules

- Interactions: filter (segment / metric / time), toggle (funnel base, metric, dimension), hover detail (rate, sample size), expand/collapse (evidence, counter-patterns), and status markers (可计算 / 不可计算, 真实 / 模拟).
- Every number, label and unit in the interactive view must be recomputable from the recorded inputs and identical to `report.md`; the HTML is a derived view and does not edit the formal record.
- Distinguish 真实数据 / 模拟材料 / 观察 / 推断 visually; recommendations stay assistant suggestions until the user confirms them.
- With no real data, render only a clearly labelled 演示/不可计算 format demonstration — never an apparent product result, ratio, trend or causal claim.

## Handoff

Return the strongest supported conclusion, what cannot be concluded, and the product decision the analysis informs. Recommendations remain assistant suggestions until the user confirms them. Do not present correlation or a dashboard annotation as established causation.
