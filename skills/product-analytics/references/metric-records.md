# Metric and report records

## `analytics/metric-definitions.md`

| Metric | Unit | Numerator | Denominator | Eligibility | Period/timezone | Deduplication | Source field/version | Baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

For a count, state the event/person/session key and deduplication. For a rate, define both counts and show their values. For a funnel, define stage order and whether conversion is relative to the previous stage or the first stage. If denominators differ by segment, show that explicitly.

Rows without a valid person ID may be reported as missing data, but they cannot silently join a person-level denominator. If no stable event ID exists, document any composite key and collision risk before deduplicating. Record the attribution window or present separate scenarios when it is undecided.

## `analytics/report.md`

1. Question and product decision informed.
2. Data source, extraction date, period, timezone, inclusion and quality checks.
3. Metric definitions and reproducible calculation method.
4. Results: table or figure with labels, units and source version.
5. Observations and counterpatterns.
6. Possible explanations and tests that would distinguish them.
7. Limits: missing fields, sample bias, instrumentation drift or small counts.
8. Recommended actions, status as assistant suggestion, and next validation.

Do not infer a customer segment from an aggregate statistic without segment data. A change in a metric is an observation; a product mechanism is a hypothesis until tested.

## Interactive analysis view panels

The interactive view (`analytics/report-review.html`) is optional and derived from `report.md`. Pick panels from this menu by the analysis question and data availability; never render a panel whose numbers cannot be computed.

| Panel | Shows | Needs | When to drop |
| --- | --- | --- | --- |
| 分析总览 Overview | headline cards, sample size, window, material status, one-line conclusion | any recorded inputs | rarely |
| 转化漏斗 Funnel | ordered stage counts/rates, switchable base | compatible stage population + key | stages lack a shared key or denominator |
| 每日趋势 Trend | daily/time-series metric, switchable metric/range | real timestamps | no real timestamps |
| 分群诊断 Segments | per-segment numerator/denominator/rate, switchable dimension | segment data | only aggregates, no segment field |
| 洞察归因 Attribution | observed vs hypothesis, expandable evidence, counter-patterns | observations + explicit hypotheses | none yet recorded |
| 行动建议 Actions | prioritised checkable actions, each labelled 助手建议·待用户确认 | ≥1 actionable option | no recommendations |
| 数据质量 Quality | missing fields, dedup, stage order, 可计算/不可计算/演示 marker | data contract | n/a — include when any metric is unavailable |

Rules: every number must match `report.md`; the HTML is a derived view and does not edit the formal record; distinguish 真实数据/模拟材料/观察/推断; with no real data render only a labelled 演示/不可计算 demonstration.
