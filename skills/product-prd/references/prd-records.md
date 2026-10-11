# PRD record shape

`requirements/<name>/prd/PRD.md` is the formal PRD. Keep a readable table of contents and stable section IDs so reviews and downstream artifacts can link to exact behavior. Do not precreate `prd/` before writing.

## Required sections

1. **文档概述**: title, version, author, date, status, audience, evidence state and change summary.
2. **需求背景和目标**: write the background with the formula “问题现状 + 数据佐证 + 归因分析 + 解决方案 + 产品价值”, then record user/business goals, metric formula and related materials.
3. **功能详细说明**: list features first, then assign an `F-xx` ID to each feature and describe name, flow, prototype, display/interaction/logic, data strategy, special cases and dependencies. Include observable success/failure and tracking references.
4. **非功能需求**: record operations/content support, performance, security, compatibility, availability, observability and other constraints. Unknowns name a verification method.
5. **数据埋点**: state the analysis question, then define parameter names, meanings, values, timing, trigger conditions, deduplication and metric mapping. Separate outcome metrics from process metrics.
6. **附录**: glossary, reference documents, schedule and open decisions that still affect behavior or acceptance.

Optional flow, experiment, technical and rollout sections need an inclusion decision. A rule shared across screens belongs in one shared-rule section and is referenced from each owning state. Do not leave behavior hidden in screenshots alone.

## `prd/validation.md`

Record date, PRD version, checked source/decision versions, included and omitted sections, findings, and pass/fail for:

- evidence and decision provenance;
- observable outcome and numerical metric definitions;
- scope and exclusions;
- core, empty, loading, error, permission and retry states where applicable;
- linked prototype/flow/acceptance consistency;
- unresolved items that would change the next deliverable.

A mechanical structure pass cannot certify that the product decision is right. Give the reviewer the exact location of any failure.
