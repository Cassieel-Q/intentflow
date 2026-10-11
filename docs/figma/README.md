# IntentFlow Figma 工作流

IntentFlow 的 Figma 工作流由三层组成：

```text
按需 personal-grill-me / demand-evidence-research
→ figma-build / figma-codegen
→ figma-to-real-feature
```

## 入口

- [figma-build](../../skills/figma-build/SKILL.md)：把代码、需求或描述落到已连接的 Figma 文件。
- [figma-codegen](../../skills/figma-codegen/SKILL.md)：把 Figma 设计转成符合目标项目技术栈的代码。
- [figma-to-real-feature](../../skills/local-codex-skills/figma-to-real-feature/SKILL.md)：核对路由、组件、接口、权限、状态和浏览器验证。

## 依赖

`figma-build` 和 `figma-codegen` 需要外部 Figwright MCP server 与 Figma plugin 提供工具，例如 `get_design_context`、`component_map`、`token_map`、`get_screenshot` 和 `design_diff`。

IntentFlow 只维护工作流和记录规则，不在本仓库复制 Figwright 的 MCP server、plugin 或运行时依赖。外部来源和许可见 [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)。

## 使用顺序

1. 先读已有需求材料。关键产品选择未定时使用 `personal-grill-me`；痛点或机会需要证据时使用 `demand-evidence-research`。两者都不需要时直接进入设计任务。
2. 需要创建设计时使用 `figma-build`。
3. 需要从设计生成代码时使用 `figma-codegen`。
4. 进入真实项目前使用 `figma-to-real-feature`，核对接口、权限、旧行为和页面状态。
5. 用截图、浏览器路径和 `design_diff` 完成验证。

## 记录规则

稳定的设计决策、组件映射、Token 映射和验证证据写入对应需求目录或项目文档。截图是验证证据，不自动等同于产品需求。
