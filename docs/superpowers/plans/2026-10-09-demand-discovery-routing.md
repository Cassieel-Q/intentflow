# Demand Discovery Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 IntentFlow 按实际歧义和证据缺口选择意图澄清、公开证据挖掘或直接产出。

**Architecture:** 保留 `personal-grill-me` 专管决策澄清，新增 `demand-evidence-research` 专管来源可追溯的需求验证。项目入口负责路由，需求目录负责持久化。

**Tech Stack:** Markdown skills、项目文档、`quick_validate.py`、情景检查。

## Global Constraints

- 一次只问一个会改变后续工作的最高影响决策。
- 同一需求沿用同一个 `requirements/<name>/` 目录；按需建子目录。
- 模拟反馈不能作为真实用户证据；事实、推断、建议分层。
- 通用流程不预设具体需求的目标用户、场景或范围。

---

### Task 1: 记录基线与设计

**Files:** `docs/superpowers/specs/2026-10-09-demand-discovery-routing-design.md`

- [x] 运行四个路由场景的现有文档基线，记录具体缺口。
- [x] 写入用户确认的两部分设计和需求目录边界。

### Task 2: 编写证据 skill 与入口路由

**Files:** `skills/demand-evidence-research/SKILL.md`, `skills/demand-evidence-research/references/evidence-records.md`, `skills/personal-grill-me/SKILL.md`, `INTENTFLOW.md`, `00-项目索引.md`, `skills/README.md`

- [x] 编写独立证据工作流，明确输入、来源筛选、记录、推断、停止与交接。
- [x] 给 Grill-Me 加入条件触发和到证据工作的交接。
- [x] 同步所有项目入口的条件路由。

### Task 3: 验证与需求目录交接

**Files:** `requirements/<name>/`、`00-当前状态.md`、`DECISION_LOG.md`

- [x] 对两个 skill 运行 `quick_validate.py`。
- [x] 复测四个场景，确认路由、证据标注与停止条件。
- [x] 记录本次确认的工作流决策；具体需求的开放问题只保存在所属需求目录。
