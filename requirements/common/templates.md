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
  contracts/
  design/
  acceptance.md
  links.md
  archive/
```

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
