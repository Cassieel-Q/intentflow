# IntentFlow

> 个人 AI 产品工作台 —— 把产品意图整理成清晰决策、需求、设计、实现任务和验证结果。

IntentFlow 是一条**可复用的产品工作流**。它把"一个产品想法"到"可验证的交付物"的完整链路固化下来：每一步的产出格式、ID 约定、验证方式和归档方式都是固定的，保证每次做产品时，交付物**格式一致、可追溯、可复用**。

---

## 它解决什么

- **减少重复沟通** —— 产品上下文长期保存，不用每次重新解释背景。
- **消除隐含假设** —— 把「用户确认 / 外部证据 / 助手推断 / 未验证假设」显式分层，不把推断写成事实。
- **避免版本混乱** —— PRD、验收清单、数据报告以 Markdown 为正式记录，交互式 HTML 只是派生视图，永不反向修改正式文件。

## 工作流

```
需求挖掘 → 需求闸门 → PRD → 流程 + 原型 + 联动评审 → 验收 → 数据复盘 → 归档
```

| 阶段 | 产出 | 说明 |
| --- | --- | --- |
| 1. 项目进入 | `requirements/<name>/` 目录 | 复用已有状态、决策、资料；新需求才建独立目录 |
| 2. 需求挖掘 | 逐条反馈、痛点聚类、机会假设 | 按需路由 `personal-grill-me`（澄清）与 `demand-evidence-research`（证据） |
| 3. 需求闸门 | `research/demand-gate.md` | `ready` / `provisional` / `blocked`，只有 `ready` 才能进正式 PRD |
| 4. PRD 评审 | `prd/PRD.md` + `PRD-review.html` | 统一模板 + 结构校验 + 联动评审页 |
| 5. 流程与原型 | `flows/` + `design/prototype.html` | 业务流程图、嵌入真实原型的交互流程图、状态映射、可操作原型 |
| 6. 验收 | `qa/checklist.md` + `qa/results.md` | 每条用例「未测 / 通过 / 失败 / 跳过」四状态，可直接点选保存 |
| 7. 数据复盘 | `analytics/report.md` + 交互式视图 | 指标定义、数据契约、可计算性、交互式分析仪表盘 |

## 核心设计

- **跨文档追踪**：`F-xx`（功能）、`Pxx`（原型状态）、`L-xx`（链路）、`EVT-xx`（埋点事件）贯通 PRD、流程、原型、验收和数据分析。
- **正式记录与派生视图分离**：Markdown 是唯一正式源；PRD 评审页、验收页、交互式数据复盘页都是按需生成的 HTML，数字与 Markdown 严格一致。
- **证据分层**：模拟反馈 ≠ 用户证据，公开产品页 ≠ 效果证明，观察 ≠ 归因。没有真实数据时只输出标注「演示 / 不可计算」的格式演示，绝不虚构比例、趋势或因果。

## 交付物

每个需求目录按需产出（只有进入该阶段才创建对应目录）：

```text
requirements/<name>/
  research/   需求证据、反馈 CSV、需求洞察 HTML、闸门报告
  prd/        正式 PRD、校验记录、联动评审 HTML
  flows/      业务流程图、交互流程图
  design/     状态映射、可操作原型
  qa/         验收清单、执行记录
  analytics/  指标定义、数据复盘报告、交互式数据复盘视图
  archive/    日期化阶段归档
```

## 快速开始

环境要求：Python 3.11+，Node 22+（可选，用于浏览器校验）。

```powershell
# 全量自动化测试
py -3 -m pytest -q

# 新建需求目录（只补齐缺失的起始文件，不覆盖已有记录）
py -3 scripts/intentflow.py init --requirement requirements/<name>

# 校验 PRD 结构
py -3 scripts/intentflow.py validate --requirement requirements/<name> --kind prd

# 生成联动评审 HTML
py -3 scripts/intentflow.py render --requirement requirements/<name> --kind prd
py -3 scripts/intentflow.py render --requirement requirements/<name> --kind acceptance
py -3 scripts/intentflow.py render --requirement requirements/<name> --kind analytics

# 启动本地评审服务（保存验收状态 / Markdown 时使用）
py -3 scripts/intentflow.py serve --requirement requirements/<name> --kind acceptance
```

## 技能（Skills）

| Skill | 用途 |
| --- | --- |
| `personal-grill-me` | 需求挖掘：关键决策澄清，默认一次只问一个最高优先级问题 |
| `demand-evidence-research` | 需求挖掘：按需验证痛点、竞品与机会的外部证据 |
| `product-prd` | 把已确认决策写成可评审的 PRD |
| `product-flows` | 业务流程图、交互流程图、状态/时序图 |
| `product-prototype` | 可操作原型与 PRD 一致性 |
| `product-acceptance` | 从 PRD/原型推导可执行的验收用例 |
| `product-analytics` | 可复现的数据分析与迭代建议 |

## 演示

完整工作流录屏 —— 从项目进入到数据复盘（步骤 1-7，含可操作原型点击）：

[![IntentFlow 完整工作流演示](docs/demo/workflow-cover.png)](docs/demo/workflow.webm)

> 点击上方封面观看完整录屏（33 秒）。第 7 步「数据复盘」交互式仪表盘细节：[demo.gif](docs/demo/demo.gif)

## 测试

```powershell
py -3 -m pytest -q
```

## 目录结构

```text
assistants/    主会话与专业助手协作规则
requirements/  需求、决策、开放问题和验收记录（含 common 通用模板）
skills/        可复用工作流 skill
scripts/       工作区维护脚本与本地评审运行层
tests/         自动化测试
docs/          设计文档和实施计划
todos/         当前待办
```

## License

本仓库为个人工作流，未声明开放源代码许可。第三方依赖见 [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)。
