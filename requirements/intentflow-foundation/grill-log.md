# Grill Log

## 意图

把 Superflow 改造成名为 IntentFlow 的个人 AI 产品工作台，并加入自有的
`grill-me` 前置决策 skill。

## 已确认

- 产品定位为个人 AI 产品工作台。
- 默认一次只问一个最高优先级问题。
- 结果写入需求目录中的决策、开放问题、验收和摘要文件。

## 约束

- 不能把第三方 skill 原样复制成最终规则。
- 不先实现具体业务产品代码。
- 先完成设计、记录和行为验证，再考虑发布到 GitHub。

## 下一步

实现并验证 `skills/personal-grill-me/`。
