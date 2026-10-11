# 新需求模板

建议新需求最小结构：

```text
requirements/<requirement-name>/
  README.md
  source.md
  requirement.md
  todo.md
  decisions.md
  open-questions.md
  acceptance.md
  links.md
```

用 `scripts/intentflow.py init --requirement requirements/<requirement-name>` 只补齐缺失的起始文件，不覆盖已有记录。按需添加阶段产物目录：`research/`（证据研究）、`prd/`（正式 PRD 与检查）、`design/`（原型/设计）、`flows/`（流程图）、`qa/`（验收清单与执行记录）、`analytics/`（指标定义与复盘）、`contracts/`（技术契约）、`archive/`（已停用版本）。只有实际进入该阶段才创建目录；同一需求始终复用同一个 `requirements/<requirement-name>/`。

PRD、验收清单和数据报告的正式记录为 Markdown。交互式 HTML 只在需要评审或演示时生成，并保留回到正式文件的路径和版本。

需求挖掘使用 [需求挖掘记录模板](./demand-discovery-template.md)。先记录案例和来源，再做痛点聚类、替代方式对照和机会假设；没有真实材料时只允许做明确标注的演示分析。需要演示或评审时，可从同一批 Markdown、`research/feedback.csv`、`research/products.csv` 和 `source.md` 生成需求洞察 HTML；HTML 不是新的正式结论。

进入 PRD 前运行 `py -3 scripts/intentflow.py demand-gate --requirement requirements/<name>`。`ready` 才能进入正式需求产出；`provisional` 只能输出探索性方案；`blocked` 先补证据或正式记录。

## source.md

只放非主观来源：

* 原始需求文档。

* Figma 链接。

* 截图目录。

* 接口平台或产品后台链接。

* 外部材料链接。

## decisions.md

只放已经确认的业务口径、技术取舍和验收判断。

## todo.md

只放未完成动作，不记录已完成历史。

每个 requirement 在最终验收前保留以下待办：

```text
- [终审适用性确认] 最终验收前由主会话主动评估并向用户建议完整终审、轻量终审或不做专项终审；具体是否执行及深度由用户决定。
```

该待办只强制主会话主动提议，不强制执行完整终审。具体规则见 [最终验收前终审适用性确认](./final-review-proposal.md)。
