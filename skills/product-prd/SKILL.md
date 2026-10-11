---
name: product-prd
description: Use when a product requirement is ready to become a reviewable PRD and its audience, problem, intended outcome, and scope are sufficiently clear.
---

# Product PRD

## Purpose and entry

Turn confirmed product decisions into a reviewable behavior contract. Reuse the active `requirements/<name>/` directory. Read `decisions.md`, `open-questions.md`, `source.md`, `acceptance.md`, existing research, design, and older PRD versions before writing.

Check that the main user, situation, problem, desired user result, current scope, exclusions, constraints, and available materials are known. If a missing choice would change behavior or acceptance, use `personal-grill-me` for that decision. If a material claim needs verification, use `demand-evidence-research`. A user may choose to draft with a named assumption; label it and keep the dependency visible.

Before creating `prd/PRD.md`, read or run the research gate:
`py -3 scripts/intentflow.py demand-gate --requirement requirements/<name>`.
Proceed with a formal PRD only when the result is `ready`. A `provisional`
result may produce an explicitly exploratory draft if the user asks for one;
`blocked` requires the listed evidence or record gaps to be addressed first.

## Write

Create `prd/PRD.md` only when this stage is used. Use the [PRD template](../../requirements/common/prd-template.md) and keep the sections in this order:

1. **文档概述**：标题、版本号、作者、日期、状态、适用对象、证据状态和变更摘要。
2. **需求背景和目标**：用“问题现状 + 数据佐证 + 归因分析 + 解决方案 + 产品价值”组织背景；再写用户目标、业务/研究目标、指标口径和相关资料。
3. **功能详细说明**：先给功能列表，再按功能 ID 写一张三列表格：“序号与功能名称、原型图/状态、详细说明”。详细说明必须把功能名称、功能流程、展示/交互/逻辑、数据策略、特殊场景、依赖项、成功条件、失败条件和埋点关联合并成分点内容，避免表格与下方重复维护。原型列使用 `[[prototype:Pxx]]` 状态标记；生成联动 HTML 时必须替换成对应的可操作原型 iframe，不能只显示 `Pxx` 文本。功能列表至少使用“功能 ID、功能名称、功能流程、原型图/状态、功能描述、数据策略、特殊场景、依赖项”列。
4. **非功能需求**：写运营/内容支持、性能、安全、兼容、可用性、可观测性以及其他约束；未知项写验证方式，不编造参数。
5. **数据埋点**：先说明要回答的分析问题，再用表格定义参数名、参数说明、参数值、埋点时机、触发条件和关联指标。结果指标与过程指标分开，分子、分母、去重和时间维度必须能复算。
6. **附录**：术语表、参考文档、项目排期，以及仍会影响本期行为或验收的待确认事项。

需求背景中的五项组成**需求背景黄金公式**，不是五段泛泛描述：每一项都要标明证据、推断或建议的身份。公开产品页面只能说明观察到的机制，模拟反馈只能验证材料结构和流程展示。没有真实基线时写“尚无基线”，并把下一步验证写清楚。`非功能需求`和`数据埋点`不是装饰性附录，只有在本期确实需要时才省略并说明原因。

After drafting, run `py -3 scripts/intentflow.py validate --requirement requirements/<name> --kind prd`. This only checks structure and placeholders; `prd/validation.md` still records the evidence, decision and cross-artifact review.

Generate `prd/PRD-review.html` at this point for a PRD-only review. After the PRD is accepted and flows/prototype are produced, regenerate the same review artifact with the business flow, integrated interaction flow, feature mappings and right-side prototype preview. The HTML is a review projection; `prd/PRD.md` remains the formal source.

## Cross-artifact review contract

When the requirement proceeds to flow and prototype review, keep these stable IDs:

- `F-xx`: PRD behavior/function;
- `Pxx`: prototype page or meaningful state;
- `L-xx`: core interaction route;
- `EVT-xx`: tracking event.

The PRD must link to `flows/business-flow.md`, `flows/interaction-flow.md` and `design/state-map.md`. The review artifact is `prd/PRD-review.html`: it provides navigation for primary document sections only, a left document/flow pane and a right prototype pane on wide screens. The feature-detail table itself also embeds the actual `Pxx` prototype states; scrolling to a feature or clicking a flow/state link selects the mapped state. Embedded prototypes preserve the source prototype's canonical viewport and aspect ratio (default `520x900`, or an explicit `data-intentflow-viewport="WIDTHxHEIGHT"` on the prototype body); the whole canvas is scaled inside a table cell instead of reflowing, cropping or stretching to the narrow iframe. Changing the state in the right pane locates the mapped PRD feature. If a mapping is missing, show it as an explicit gap rather than inventing a screen.

The business flow describes actors, entry conditions, decisions, success, failure and empty outcomes. The interaction flow is one integrated map of all meaningful prototype states and labelled arrows, including return, retry, loop and error routes. A feature table row must expose its function name, user flow, prototype state and description so a reviewer can move from requirement to screen without guessing.

When a timing or follow-up rule is unspecified, record it as a decision. The workflow default is user-initiated re-entry with a configurable review window; do not silently turn a later action into an immediate trigger.

Keep business behavior readable to product reviewers. Put API fields and error codes in `contracts/` or a technical appendix, linked from the owning behavior. State which optional sections were included or omitted and why. See [references/prd-records.md](./references/prd-records.md).

## Review and handoff

Compare each PRD claim with confirmed decisions and cited evidence. Verify that a reviewer can identify every core state and an acceptance writer can derive observable checks without inventing rules. Record the check and remaining gaps in `prd/validation.md`. When an existing PRD changes, update its version and check linked prototype, flows, tracking, and acceptance for drift.

Hand off to design/prototype, flow, implementation planning, or acceptance only when remaining ambiguity cannot materially change that next artifact. Do not silently promote recommendations, research inference, or missing baseline to confirmed scope.

An unknown baseline does not by itself block a draft. Preserve a user-supplied target as a target, mark the baseline missing, and do not claim the target's feasibility or use an unconfirmed number as an acceptance gate.
