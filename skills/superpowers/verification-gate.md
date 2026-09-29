# Verification Gate

## 目的

把分级 TDD 和最低验证要求固定下来，既保证关键路径稳定，又避免对低风险改动过度测试。

## 分级 TDD 策略

| 变更类型 | 默认要求 |
| --- | --- |
| 金额、库存、订单状态、权限、数据同步 | 强制 TDD，先 Red 后 Green。 |
| 后端持久化、事务、异步、调度、跨 Bean 协作 | 单测覆盖分支逻辑，集成测试覆盖真实链路。 |
| 前端关键主路径 | 至少一条可重复 E2E 或等价路径验证。 |
| 前端复杂逻辑、表单规则、状态映射 | 优先单测/组件测试。 |
| 文案、纯样式、小布局 | 可降级为构建/类型检查/截图验证，必须记录跳过 TDD 原因。 |
| 无测试基础的旧项目 | 先覆盖本次最容易坏、代价最高的行为；必要时补最低测试入口。 |

## TDD 铁律

```text
先写失败测试，再写生产代码。
不能用“最后补测试”冒充 TDD。
```

详细执行规则见：[tdd-red-green-refactor](./tdd-red-green-refactor.md)。

## 提交前测试产物检查

进入提交或交付前，必须确认 TDD/验证产物的去向：

- 长期保留测试：随代码提交。
- 阶段性保留测试：说明阶段用途和后续转正/删除条件。
- 临时测试或探针脚本：删除，不进入提交。

临时产物必须带 `TEMP_TDD`、`SCRATCH_TEST`、`TEMP_TEST`、`临时测试` 或 `探针测试` 标记。提交前运行：

```sh
./scripts/check-temporary-test-artifacts.sh <repo-path>
```

命中临时标记时，不允许进入最终提交说明，除非用户明确要求保留且已改成阶段性测试。

## 前端验证节流

Playwright / E2E 只用于值得验证的用户路径：

- 只跑目标 spec，不默认全量 E2E。
- 截图只保留关键状态：初始态、操作后、异常态。
- 日志只摘要失败断言、URL、选择器、关键 console error。
- Figma 改造只验证对应 frame 的页面路径，不扫描全应用。

前端复用、H5 自测和可见路径验证见：[frontend-reuse-and-path-verification](./frontend-reuse-and-path-verification.md)。

## 子会话汇报格式

```text
验证命令：
Red 证据：
Green 证据：
测试产物去向：
跳过项和原因：
残余风险：
```

返回：[Superpowers 索引](./README.md)
