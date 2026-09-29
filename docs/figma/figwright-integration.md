# Figwright 集成说明

## 外部源项目

本地参考源码：`G:\myself\figwright`

它包含：

- Figwright MCP server；
- Figma plugin；
- shared protocol 和类型；
- `figma-build` skill；
- `figma-codegen` skill。

IntentFlow 已提取两个 skill 及其参考文档，作为工作流层使用。Figwright 源码、插件构建产物和运行时仍独立维护。

## 连接前检查

- 目标 Figma 文件已经在 Figma 中打开；
- Figwright plugin 已启动并连接；
- MCP server 可以响应 `ping`；
- 当前项目的技术栈、组件目录和 Token 来源可被读取；
- 用户已经确认本次任务是新建、改造还是混合。

## 边界

- Figma 设计稿是设计输入，不是 API、权限或数据模型真源；
- `figma-codegen` 生成的代码必须经过项目自身的路由、接口和状态核对；
- `figma-build` 不能用新组件替换已有设计系统，除非差异已经确认；
- 视觉截图不能替代真实浏览器路径验证。

## 映射文件

高价值项目可以在自己的需求或项目目录中维护：

- `docs/figma-component-map.md`：已验证的 Figma 组件到代码组件映射；
- `docs/figma-token-map.md`：已验证的 Figma Token 到项目 Token 映射。

只记录已经渲染并验证过的映射，避免把猜测固化成长期真源。
