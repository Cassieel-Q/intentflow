# IntentFlow Review Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为正式 Markdown 产物提供可选的交互式评审页、本地安全保存、状态记录、真实截图和跨平台诊断。

**Architecture:** Python 包负责路径与版本保护、Markdown 渲染、HTTP 预览和浏览器截图；浏览器端只编辑对应的 Markdown 或提交结构化的验收状态。原型与流程图仍可作为独立 HTML/SVG 文件。所有写操作限定在当前需求目录，并用内容哈希防止覆盖新版本。

**Tech Stack:** Python 3.11+、`markdown-it-py`、可选 Playwright、标准库 HTTP 服务、浏览器原生 JavaScript、pytest。

## Global Constraints

- 正式产物为 Markdown；HTML 是生成视图，可删除后重新生成。
- HTTP 服务仅绑定 `127.0.0.1`；写操作需要当前会话令牌和版本匹配。
- 不允许 `..` 或符号链接穿越项目目录；保存采用临时文件加原子替换。
- 截图清理只处理运行工具记录归属的文件，不扫描删除用户手工图片。
- 运行时缺浏览器依赖时明确报错或降级，不伪称截图成功。

---

### Task 1: 路径与版本保护

**Files:** `scripts/intentflow_runtime/core.py`, `tests/test_runtime_core.py`

**Interfaces:** `resolve_requirement_path(root, rel) -> Path`, `sha256_text(text) -> str`, `save_if_revision(root, rel, expected_hash, content) -> str`.

- [x] 先写路径穿越、符号链接穿越、版本冲突、原子保存和不覆盖其他需求的失败测试。
- [x] 实现最小路径解析与保存逻辑，测试通过。

### Task 2: Markdown 评审页

**Files:** `scripts/intentflow_runtime/render.py`, `scripts/intentflow_runtime/review.js`, `scripts/intentflow_runtime/review.css`, `tests/test_runtime_render.py`

**Interfaces:** `render_review(source: Path, kind: str, prototype: Path | None) -> str`.

- [x] 先测 PRD、验收、数据报告的正式源路径/哈希被写入生成页；HTML 正文转义；原型面板默认收起。
- [x] 实现 Markdown 渲染、目录导航、懒加载原型侧栏、缩放和编辑区；编辑区保存时提交 Markdown 源和预期哈希。
- [x] 验收视图按案例 ID 管理未测/通过/失败/跳过，并能导出状态；离线时标明状态只在浏览器暂存。

### Task 3: 本地预览与保存服务

**Files:** `scripts/intentflow_runtime/server.py`, `tests/test_runtime_server.py`

**Interfaces:** `make_server(root, host='127.0.0.1', port=0)`, `GET /api/health`, `POST /api/save-markdown`, `POST /api/acceptance-status`.

- [x] 先测外部 Host/Origin、缺令牌、非法路径和旧哈希不能写文件。
- [x] 实现静态文件预览、令牌验证、请求体限制、Markdown 保存与验收状态回写。
- [x] 确认错误会返回明确状态，不生成空白成功文件。

### Task 4: 真实截图与产物归属

**Files:** `scripts/intentflow_runtime/capture.py`, `tests/test_runtime_capture.py`

**Interfaces:** `capture(html_path, output_dir, pages) -> list[Path]`.

- [x] 测试页面清单、输出文件命名、旧归属清单清理范围和用户手工 PNG 保留。
- [x] 使用 Playwright 对指定本地页面/状态真实渲染；缺依赖时返回诊断信息。
- [x] 记录截图尺寸、源文件哈希和生成时间，重复截图时只复用匹配版本。

### Task 5: CLI、安装与诊断

**Files:** `scripts/intentflow.py`, `scripts/intentflow_runtime/doctor.py`, `scripts/intentflow-start.bat`, `scripts/intentflow-start.command`, `tests/test_runtime_cli.py`, `scripts/README.md`

- [x] 提供 `render`、`serve`、`capture`、`doctor` 命令，支持指定项目根与需求目录。
- [x] 输出 Python、依赖、浏览器、端口、目录权限和当前配置的诊断结果。
- [x] Windows/macOS 启动入口调用同一 Python CLI；重复初始化保护现有文件。

### Task 6: 端到端与安全复核

**Files:** `tests/test_runtime_e2e.py`, `requirements/intentflow-lifecycle-2026-10-09/acceptance.md`

- [x] 从示例 Markdown 生成评审页，编辑并保存，再读正式 Markdown 确认一致。
- [x] 运行路径/令牌/冲突测试、生成页浏览器检查、截图保留测试和 `doctor`。
- [x] 检查未实现的可选功能仍标待建立，不宣称全流程完成。
