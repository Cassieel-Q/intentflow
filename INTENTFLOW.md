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

1. 在 `requirements/<name>/` 创建需求目录。
2. 使用 `skills/personal-grill-me/`，一次确认一个最高优先级决策。
3. 把确认结果写入 `decisions.md`、`open-questions.md`、`acceptance.md` 和 `grill-log.md`。
4. 再进入 PRD、设计、实现或验证流程。

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
