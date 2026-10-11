# IntentFlow

IntentFlow 是我的个人 AI 产品工作台：把产品意图整理成清晰决策、需求、设计、实现任务和验证结果。

它用于长期保存产品上下文，减少重复沟通、隐含假设和版本混乱。

## 目录

```text
assistants/       主会话与专业助手协作规则
requirements/     需求、决策、开放问题和验收记录
skills/           可复用工作流 skill
scripts/          工作区维护脚本
todos/            当前待办
docs/             设计文档和实施计划
```

## 从一个产品想法开始

1. **项目进入**：确定当前需求并复用其 `requirements/<name>/` 目录，读取已有状态、决策、资料和历史产物；新需求开始时才创建独立目录。
2. **需求挖掘**：明确用户、场景、问题、影响和期望结果。关键产品选择尚不明确时使用 `skills/personal-grill-me/`；痛点或机会需要外部证据时使用 `skills/demand-evidence-research/`。两者按缺口切换，不是固定串行步骤。输出逐条反馈与来源、痛点聚类与归因、机会假设和待验证问题，并区分用户确认、外部证据、助手推断和未验证假设。
3. **需求闸门**：运行需求挖掘终审闸门。`ready` 才能进入正式 PRD，`provisional` 只能做探索性方案或演示，`blocked` 必须先补齐材料。需求挖掘阶段不提前决定页面、按钮、交互顺序或功能组合。
4. **PRD 产出与评审**：PRD 按统一模板写成正式 Markdown，并先生成只包含 PRD 内容的 `prd/PRD-review.html`，评审需求背景、目标、功能列表、详细说明、非功能需求和埋点口径；功能 ID、流程、数据策略和埋点口径要能被后续设计、开发、测试和数据复用。
5. **流程—原型—联动评审交付**：在 PRD 评审通过后，一次性产出业务流程图、由真实原型界面组成的交互流程图、`design/state-map.md` 和可操作原型，并重新生成同一个 `prd/PRD-review.html`。交互流程图的每个节点都要嵌入对应的可操作原型 iframe 或真实缩略图，再用箭头标注真实交互链路，不能只输出思维导图或占位卡片。PRD 每个 `F-xx` 的功能详情表要把功能流程、页面元素、交互、数据、边界、异常、依赖、成功/失败和埋点合并成分点说明；原型列使用 `[[prototype:Pxx]]`，联动 HTML 中必须展开为实际原型界面。嵌入原型必须声明或继承统一的基准画布尺寸（默认 `520x900`），表格内按比例整体缩放，禁止因窄列触发响应式重排、裁切或拉伸变形；缩略图仍须保持与可操作原型一致的宽高比。HTML 集成 PRD、两张流程图、功能详情和右侧原型预览；使用 `F-xx`（功能）、`Pxx`（原型状态）、`L-xx`（链路）、`EVT-xx`（事件）建立跨文档追踪。桌面端的章节导航只保留 PRD 的主要一级章节（如概述、背景目标、功能、非功能、埋点、附录），不把每个功能和子标题重复列入导航；左侧内容滚动或点击时切换右侧状态，右侧状态选择器可定位回左侧内容；缺少映射时必须显示缺口，不得自动猜测。
6. **验收**：根据 PRD、流程和原型生成验收清单，按用例直接修改“未测 / 通过 / 失败 / 跳过”状态；不要求先填写构建版本、浏览器/设备或证据位置。构建版本与备注均可留空，备注在最后一列填写。顶部显示通过进度；验收页提供“打开 PRD”入口回到上一步的联动 PRD 评审页。正式执行记录追加到 `qa/results.md`。
7. **数据复盘与归档**：按埋点和结果指标复盘，先记录数据契约、指标公式、可计算结果与证据边界；再将结论、未决问题、版本变化和下一步写入 `analytics/report.md`，把本阶段的材料快照和状态写入 `archive/<date>-<topic>.md`，并在需求目录 README 保留入口。没有真实数据时只能输出标明“演示/不可计算”的准备度复盘，不得虚构比例、趋势或效果结论。数据分析除正式 Markdown 外，可按需生成交互式分析视图（默认 `analytics/report-review.html`）：按分析问题和数据可得性从板块菜单选取（分析总览、转化漏斗、每日趋势、分群诊断、洞察归因、行动建议、数据质量等，可增删重排），支持筛选、切换口径、hover 详情、展开证据链和“可计算/不可计算/真实/模拟”标记；所有数字必须与 Markdown 一致，HTML 只是派生视图，不改正式记录。具体规范见 [Product Analytics](./skills/product-analytics/SKILL.md)。

PRD、验收清单和数据报告以 Markdown 为正式记录；需要浏览器评审时再生成交互式 HTML，保持与正式文件的版本关系。

原型评审交付契约见 [PRD—流程—原型联动设计](./docs/superpowers/specs/2026-10-09-prd-flow-prototype-review-design.md)。

需求挖掘路由与证据边界见 [需求挖掘路由设计](./docs/superpowers/specs/2026-10-09-demand-discovery-routing-design.md)。

## Figma 工作流

需要做 Figma 相关工作时，从 [docs/figma/README.md](./docs/figma/README.md) 进入：

```text
按需 personal-grill-me / demand-evidence-research
→ figma-build / figma-codegen
→ figma-to-real-feature
→ 浏览器和截图验证
```

## 我的工作原则

- 把用户确认、助手建议和未验证假设分开；
- 先确认业务目标，再进入实现；
- 明确每个会话和助手的写入边界；
- 用证据和可重复验证替代“应该可以”；
- 高风险行为优先采用测试驱动开发；
- 临时实验和正式测试分开；
- 最后从用户能看到的行为检查结果。

## 项目定位

IntentFlow 第一阶段只服务于我的个人产品工作流。它保留通用方法，但不把我的私有项目资料直接放进公共仓库。

## 当前入口

- [项目索引](./00-项目索引.md)
- [当前状态](./00-当前状态.md)
- [决策记录](./DECISION_LOG.md)
- [QA Gate](./05-QA-Gate.md)
- [Personal Grill-Me](./skills/personal-grill-me/SKILL.md)
- [Demand Evidence Research](./skills/demand-evidence-research/SKILL.md)
- [Product PRD](./skills/product-prd/SKILL.md)
- [Product Prototype](./skills/product-prototype/SKILL.md)
- [Product Flows](./skills/product-flows/SKILL.md)
- [Product Acceptance](./skills/product-acceptance/SKILL.md)
- [Product Analytics](./skills/product-analytics/SKILL.md)
