# IntentFlow Content Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立 PRD、功能验收和数据复盘的独立内容技能，全部接入同一需求目录与证据/决策记录。

**Architecture:** 三个 skill 分别处理需求说明、上线前检查和上线后分析。它们依赖已存在的意图澄清与证据研究，先产出可审查的 Markdown；交互式 HTML 能力由后续运行层承接，正式格式选择确认后再固定回写接口。

**Tech Stack:** Markdown skills 与模板、`quick_validate.py`、情景验证。

## Global Constraints

- 不把助手建议、模拟反馈或猜测指标写成用户确认的事实。
- 同一需求始终复用 `requirements/<name>/`；不预建未使用的子目录。
- 产品业务说明与技术接口/字段细节分层；有技术内容时放在对应技术章节。
- 每个 skill 写清触发、输入、停止、产物和不适用情况。

---

### Task 1: 基线与目录契约

**Files:** `requirements/intentflow-lifecycle-2026-10-09/capability-map.md`, `requirements/common/templates.md`, `requirements/README.md`

- [x] 用“PRD、验收、数据复盘”三个场景观察当前规则缺口。
- [x] 固定三个阶段在同一需求目录中的按需产物位置和来源/决策引用规则。
- [x] 检查新目录规则不覆盖已有需求文件。

### Task 2: PRD 内容技能

**Files:** `skills/product-prd/SKILL.md`, `skills/product-prd/references/prd-records.md`, `skills/README.md`

- [x] 写明进入 PRD 前对用户、问题、结果、范围和材料的检查。
- [x] 规定背景证据、用户结果、范围、跨页面规则、详细行为、边界、按需埋点/时序和待确认事项的记录形状。
- [x] 规定章节裁剪、版本更新与一致性检查；运行 skill 格式校验和情景测试。

### Task 3: 验收技能

**Files:** `skills/product-acceptance/SKILL.md`, `skills/product-acceptance/references/checklist-records.md`, `skills/README.md`

- [x] 规定从同一需求的 PRD/原型拆出主路径、失败路径、权限、状态、视觉和按需埋点案例。
- [x] 每条案例含可执行步骤、预期、结果、证据及失败归属；未执行的案例不得标通过。
- [x] 运行 skill 格式校验和情景测试。

### Task 4: 数据分析技能

**Files:** `skills/product-analytics/SKILL.md`, `skills/product-analytics/references/metric-records.md`, `skills/README.md`

- [x] 规定输入数据、周期、指标分子/分母、漏斗、分群和基线检查。
- [x] 把观察、可能原因、反证和行动建议分层；无真实数据只做标明的格式演示。
- [x] 运行 skill 格式校验和情景测试。

### Task 5: 入口与状态

**Files:** `INTENTFLOW.md`, `00-项目索引.md`, `00-当前状态.md`, `DECISION_LOG.md`

- [x] 将三个技能接入按需路由，而非强制线性顺序。
- [x] 更新状态与剩余模块清单，标明本阶段的验证范围。
- [x] 运行相对链接检查、`git diff --check` 和最终情景复核。
