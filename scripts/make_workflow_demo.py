"""Record a full-workflow screen capture of IntentFlow.

Builds a minimal but complete example case (a subscription-management app,
labelled as demo data), then records one continuous screen capture walking the
seven stages in order — including clicking through the operable prototype:

  1 项目进入 → 2 需求挖掘 → 3 需求闸门 → 4 PRD 评审
  → 5 流程+原型(点击操作) → 6 验收 → 7 数据复盘

Output: docs/demo/workflow.webm
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "intentflow.py"

FEEDBACK = """id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id
D-01,订阅管理,多订阅,找不到取消入口,误续费,一键取消,simulation,
D-02,续费提醒,自动续费,续费前无提醒,意外扣费,提前提醒,simulation,
D-03,支出统计,订阅较多,金额分散难统计,预算失控,汇总统计,simulation,
"""

PRODUCTS = """name,official_url,observed_capability,unverified,source_id
示例订阅管理产品,https://example.org/sub,订阅列表与续费提醒,实际效果未核实,S-01
"""

SOURCE = """# 材料与来源

| ID | 材料 | 来源位置 | 获取日期 | 适用范围 |
| --- | --- | --- | --- | --- |
| S-01 | 公开产品页 | https://example.org/sub | 2026-10-11 | 演示 |
"""

FINDINGS = """# 订阅管理 App 需求洞察

## 洞察总览

用户需要在一个入口里看清所有订阅、控制取消与续费提醒。以下为演示数据。

## 场景与材料

多订阅用户管理分散；材料为模拟反馈与公开产品页。

## 反馈与聚类

- 订阅管理：找不到取消入口。
- 续费提醒：续费前无提醒导致意外扣费。
- 支出统计：金额分散难以汇总。

## 问题与归因

分散的订阅入口与缺失的续费提醒，是用户失控的主要原因（待验证）。

## 公开产品参考

公开产品提供订阅列表与续费提醒，但效果未核实。

## 首版需求收口

首版聚焦订阅列表、取消订阅、续费提醒与支出统计。

## 验证与指标

订阅转化完成率、取消成功率、续费提醒开启率。

## 待确认结论

续费提醒的默认时机仍待确认。
"""

PRD = """# 订阅管理 App 功能需求文档

## 文档概述

- 标题：订阅管理 App
- 版本号：V0.1
- 作者：IntentFlow 演示
- 日期：2026-10-11
- 状态：探索性草案（演示数据）
- 适用对象：产品、设计、开发、测试
- 证据状态：provisional
- 变更摘要：首版聚焦订阅列表、取消、续费提醒与支出统计。

## 需求背景和目标

### 项目背景

- 问题现状：多订阅用户入口分散，取消与续费失控。
- 数据佐证：模拟反馈 3 条，公开产品页 1 个（演示）。
- 归因分析：分散入口与缺失提醒是主因（待验证）。
- 解决方案：一个入口管理所有订阅、取消与续费提醒。
- 产品价值：减少误续费，帮助用户看清支出。

### 需求目标

- 用户目标：在一个入口看清并管理所有订阅。
- 业务/研究目标：验证集中管理是否降低误续费。
- 衡量指标：取消成功率、续费提醒开启率。
- 分子/分母：分别记录完成取消 / 进入取消、开启提醒 / 进入订阅详情。

## 功能详细说明

### 功能列表

| 优先级 | 功能 ID | 功能名称 | 功能流程 | 原型图/状态 | 功能描述 | 数据策略 | 特殊场景 | 依赖项 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | F-01 | 订阅列表 | 进入 → 查看列表 | P01 | 汇总展示所有订阅 | 订阅记录 | 空状态 | 订阅数据 |
| P0 | F-02 | 订阅详情 | 选择订阅 → 查看详情 | P02 | 展示单条订阅信息 | 订阅记录 | 无 | 订阅数据 |
| P0 | F-03 | 取消订阅 | 详情 → 确认取消 | P03 | 一键取消订阅 | 取消状态 | 确认拦截 | 订阅数据 |
| P1 | F-04 | 续费提醒 | 详情 → 设置提醒 | P03 | 续费前提醒 | 提醒设置 | 无 | 通知服务 |
| P1 | F-05 | 支出统计 | 列表 → 查看统计 | P01 | 汇总月度支出 | 金额汇总 | 无 | 订阅数据 |

### F-01 订阅列表

#### 功能原型与交互说明

| 序号与功能名称 | 原型图/状态 | 详细说明 |
| --- | --- | --- |
| 1. 订阅列表 | [[prototype:P01]] | **页面元素**：订阅卡片、金额、状态。<br>**功能流程**：进入 → 查看列表 → 选择订阅。<br>**展示/交互说明**：点击卡片进入详情。<br>**数据策略**：按订阅记录展示。<br>**边界/异常说明**：无订阅时显示空状态。<br>**埋点关联**：EVT-01。 |

### F-02 订阅详情

#### 功能原型与交互说明

| 序号与功能名称 | 原型图/状态 | 详细说明 |
| --- | --- | --- |
| 1. 订阅详情 | [[prototype:P02]] | **页面元素**：订阅信息、操作按钮。<br>**功能流程**：选择订阅 → 查看详情。<br>**展示/交互说明**：展示金额、周期、状态。<br>**数据策略**：读取单条订阅。<br>**埋点关联**：EVT-02。 |

### F-03 取消订阅

#### 功能原型与交互说明

| 序号与功能名称 | 原型图/状态 | 详细说明 |
| --- | --- | --- |
| 1. 取消订阅 | [[prototype:P03]] | **页面元素**：确认弹窗、取消按钮。<br>**功能流程**：详情 → 确认取消。<br>**展示/交互说明**：二次确认后取消。<br>**数据策略**：写入取消状态。<br>**边界/异常说明**：确认前不生效。<br>**埋点关联**：EVT-03。 |

## 非功能需求

- 性能：列表加载目标在真实设备测试后确认。
- 安全性：只允许用户管理自己的订阅。

## 数据埋点

### 分析思路

先回答取消成功率与续费提醒开启率两个问题。

### 埋点表

| 事件 ID | 参数名 | 参数说明 | 埋点时机 | 触发条件 | 关联指标 |
| --- | --- | --- | --- | --- | --- |
| EVT-01 | subscription_list_viewed | 查看列表 | 进入列表 | 列表加载成功 | 进入人数 |
| EVT-02 | subscription_detail_viewed | 查看详情 | 打开详情 | 点击卡片 | 详情人数 |
| EVT-03 | cancel_confirmed | 确认取消 | 确认取消 | 二次确认 | 取消成功率 |

## 附录

### 参考文档

- 需求洞察：[research/demand-findings.md](../research/demand-findings.md)
- 来源登记：[source.md](../source.md)
"""

STATE_MAP = """| State ID | PRD behavior ID | Entry/trigger | Visible state | Available action | Next state | Asset link | Data status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | F-01 | 进入 | 订阅列表 | 查看详情 | P02 | #P01 | 模拟 |
| P02 | F-02 | 点击卡片 | 订阅详情 | 取消/提醒 | P03 | #P02 | 模拟 |
| P03 | F-03、F-04 | 点击操作 | 确认/提醒 | 确认取消 | P01 | #P03 | 模拟 |
"""

PROTOTYPE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>订阅管理 App 原型</title><style>
*{{box-sizing:border-box}} body{{margin:0;font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif;background:#eef1f5;color:#243044}}
.app{{max-width:520px;margin:0 auto;background:#f5f7fa;min-height:100vh}}
.screen{{display:none;padding-bottom:24px}} .screen.active{{display:block}}
.navbar{{background:#1e5fa5;color:#fff;padding:18px 20px;font-size:18px;font-weight:700;display:flex;justify-content:space-between;align-items:center}}
.navbar .back{{color:#fff;text-decoration:none;font-size:14px}}
.body{{padding:18px}}
.section-title{{font-size:13px;color:#6a7a8e;margin:6px 2px 10px}}
.list-card{{background:#fff;border-radius:14px;padding:16px;margin-bottom:12px;display:flex;align-items:center;gap:14px;cursor:pointer;box-shadow:0 1px 2px rgba(20,40,70,.05)}}
.list-card:hover{{box-shadow:0 4px 12px rgba(20,40,70,.12)}}
.icon{{width:46px;height:46px;border-radius:12px;display:grid;place-items:center;font-size:22px;flex:0 0 auto}}
.icon.video{{background:#e7f0ff}} .icon.cloud{{background:#e7f6f1}} .icon.music{{background:#fdf1e7}}
.list-info{{flex:1}} .name{{font-weight:600}} .sub{{color:#6a7a8e;font-size:12.5px}}
.amount{{font-weight:700;color:#1e5fa5}}
.summary{{background:#fff;border-radius:14px;padding:16px;display:flex;justify-content:space-between;align-items:center;margin-top:4px}}
.summary b{{color:#1e5fa5;font-size:18px}}
.pill{{border:1px solid #c9d4e0;border-radius:999px;padding:2px 9px;color:#51647a;font-size:12px}}
.detail-line{{padding:12px 0;border-bottom:1px solid #f0f2f5;display:flex}} .detail-line b{{width:90px;color:#6a7a8e;font-weight:500}}
.btn-row{{display:flex;gap:10px;margin-top:18px}}
button{{flex:1;background:#1e5fa5;color:#fff;border:0;border-radius:10px;padding:12px;cursor:pointer;font:inherit;font-weight:600}}
button.danger{{background:#a04e45}} button.ghost{{background:#fff;color:#1e5fa5;border:1px solid #1e5fa5}}
.confirm-card{{background:#fff;border-radius:14px;padding:20px;text-align:center}}
.confirm-card .warn{{font-size:40px;margin-bottom:8px}}
.confirm-card p{{color:#51647a;margin:6px 0 18px}}
</style></head><body data-intentflow-viewport="520x900">
<div class="app">
<section id="P01" class="screen"><div class="navbar">订阅管理 <span style="font-size:13px;font-weight:400">本月支出 ¥343</span></div>
<div class="body"><div class="section-title">全部订阅 · 3 项</div>
<div class="list-card" onclick="go('P02')"><div class="icon video">🎬</div><div class="list-info"><div class="name">视频会员</div><div class="sub">每月 30 元 · 下次扣费 11-01</div></div><span class="amount">¥30</span></div>
<div class="list-card" onclick="go('P02')"><div class="icon cloud">☁️</div><div class="list-info"><div class="name">云存储</div><div class="sub">每年 298 元 · 下次扣费 2027-03</div></div><span class="amount">¥298</span></div>
<div class="list-card" onclick="go('P02')"><div class="icon music">🎵</div><div class="list-info"><div class="name">音乐会员</div><div class="sub">每月 15 元 · 下次扣费 11-05</div></div><span class="amount">¥15</span></div>
<div class="summary"><div><div class="sub">本月订阅支出</div><b>¥343</b></div><span class="pill">3 项生效中</span></div></div></section>

<section id="P02" class="screen"><div class="navbar"><a class="back" href="#P01" onclick="go('P01')">← 返回</a> 订阅详情</div>
<div class="body"><div class="list-card" style="cursor:default"><div class="icon video">🎬</div><div class="list-info"><div class="name">视频会员</div><div class="sub">每月订阅</div></div><span class="amount">¥30/月</span></div>
<div class="list-card" style="cursor:default"><div class="detail-line"><b>状态</b><span class="pill">生效中</span></div>
<div class="detail-line"><b>下次扣费</b>2026-11-01</div>
<div class="detail-line"><b>支付方式</b>微信支付</div>
<div class="detail-line" style="border:0"><b>已订阅</b>8 个月</div></div>
<div class="btn-row"><button class="ghost" onclick="alert('已开启续费提醒')">开启续费提醒</button><button class="danger" onclick="go('P03')">取消订阅</button></div></div></section>

<section id="P03" class="screen"><div class="navbar"><a class="back" href="#P02" onclick="go('P02')">← 返回</a> 取消订阅</div>
<div class="body"><div class="confirm-card"><div class="warn">⚠️</div>
<h3 style="margin:0 0 6px">确定取消「视频会员」？</h3>
<p>取消后当前周期结束即停止扣费，剩余权益保留至 2026-11-01。</p>
<div class="btn-row"><button class="danger" onclick="alert('已取消订阅')">确认取消</button><button class="ghost" onclick="go('P02')">再想想</button></div></div></div></section>
</div>
<script>
function go(id){{location.hash=id}}
function show(id){{document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));var el=document.getElementById(id);if(el)el.classList.add('active')}}
show(location.hash.slice(1)||'P01');window.addEventListener('hashchange',()=>show(location.hash.slice(1)||'P01'));
</script></body></html>
"""

CHECKLIST = """# 订阅管理 App 验收清单

| ID | 来源 | 优先级 | 前置条件 | 步骤 | 期望结果 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AC-01 | F-01 | P0 | 已有订阅 | 进入列表 | 展示所有订阅 | 未测 | |
| AC-02 | F-01 | P0 | 无订阅 | 进入列表 | 显示空状态 | 未测 | |
| AC-03 | F-02 | P0 | 有订阅 | 点击卡片 | 展示详情 | 未测 | |
| AC-04 | F-03 | P0 | 详情页 | 点击取消 | 二次确认 | 未测 | |
| AC-05 | F-03 | P0 | 确认弹窗 | 确认取消 | 写入取消状态 | 未测 | |
| AC-06 | F-04 | P1 | 详情页 | 开启提醒 | 记录提醒设置 | 未测 | |
"""

REPORT = """# 订阅管理 App 数据复盘报告

## 1. 复盘问题与产品决策

### 复盘问题

取消成功率与续费提醒开启率是否达到预期？

### 本报告支持的决策

决定下一步是否优化取消入口与提醒时机。以下为演示数据。

## 2. 数据契约

| 项目 | 本轮记录 |
| --- | --- |
| 提取日期 | 2026-10-11 |
| 观察窗口 | 2026-09-01 ~ 2026-09-30 |
| 分析单位 | 会话 |
| 主要来源 | events.csv（演示） |
| 样本量 | 8,420 会话 |
| 缺失字段 | 无 |
| 排除项 | 内部测试账号 |

## 3. 指标与可计算性

| 指标 | 目标口径 | 本轮结果 | 原因 |
| --- | --- | --- | --- |
| 取消成功率 | 完成取消 / 进入取消 | 71.4% | 可复算 |
| 续费提醒开启率 | 开启提醒 / 进入详情 | 43.2% | 可复算 |

## 4. 已观察事实

1. 取消成功率 71.4%，仍有约三成用户在确认弹窗流失。
2. 续费提醒开启率 43.2%，不足一半。

## 5. 观察、推断与反例

### 观察

- 确认弹窗是取消流程的主要流失点。
### 推断（待验证）

- 取消文案可能让用户犹豫，需 A/B 验证。
### 其他解释

- 流失也可能来自误点取消。

## 6. 可执行选项（均为助手建议）

1. **简化取消弹窗**：减少文案层级，观察成功率变化。
2. **默认开启提醒**：将续费提醒改为默认开启。

## 8. 局限与复盘结论

- 本报告为演示数据。

**结论：**优先简化取消弹窗，并小流量验证提醒默认开启。
"""

METRICS = """# 指标定义

| 指标 | 单位 | 分子 | 分母 | 资格条件 | 时间窗/时区 | 去重键 | 当前基线 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 取消成功率 | 会话 | 完成取消的会话数 | 进入取消流程的会话数 | 进入取消 | 30 天 | session_id | 71.4% |
| 续费提醒开启率 | 会话 | 开启提醒的会话数 | 进入订阅详情的会话数 | 进入详情 | 30 天 | session_id | 43.2% |

## 口径约束

- 会话级去重，同一会话多次操作只计一次。
- 以上数字为演示数据。
"""

STAGE_PAGE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box}} body{{margin:0;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif;background:#f5f7fa;color:#243044;display:grid;place-items:center;min-height:100vh}}
.card{{background:#fff;border:1px solid #dfe5ec;border-radius:16px;padding:48px 56px;max-width:760px;width:92%;box-shadow:0 6px 24px rgba(20,40,70,.06)}}
.eyebrow{{color:#1e5fa5;font:600 13px/1 ui-monospace,monospace;letter-spacing:.1em}}
h1{{font-size:34px;margin:8px 0 12px}}
p{{color:#51647a;margin:6px 0}}
.code{{background:#f2f5f9;border:1px solid #dfe5ec;border-radius:10px;padding:14px 18px;font:13px/1.7 ui-monospace,monospace;color:#3a4a5e;margin-top:16px;white-space:pre}}
.badge{{display:inline-block;border:1px solid #e2c47c;background:#fbf4e2;color:#8f6713;border-radius:999px;padding:3px 12px;font-size:13px;font-weight:600;margin-top:14px}}
</style></head><body><div class="card">
<div class="eyebrow">{EYEBROW}</div><h1>{TITLE}</h1>{BODY}
</div></body></html>
"""


def _stage_page(eyebrow: str, title: str, body: str) -> str:
    return STAGE_PAGE.format(EYEBROW=eyebrow, TITLE=title, BODY=body)


def _run(*args: str, check: bool = True) -> None:
    result = subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed: {args}\n{result.stderr}")


def _write_case(req: Path) -> None:
    for sub in ("research", "prd", "design", "flows", "qa", "analytics"):
        (req / sub).mkdir(parents=True)
    (req / "research" / "feedback.csv").write_text(FEEDBACK, encoding="utf-8")
    (req / "research" / "products.csv").write_text(PRODUCTS, encoding="utf-8")
    (req / "research" / "demand-findings.md").write_text(FINDINGS, encoding="utf-8")
    (req / "source.md").write_text(SOURCE, encoding="utf-8")
    (req / "prd" / "PRD.md").write_text(PRD, encoding="utf-8")
    (req / "design" / "state-map.md").write_text(STATE_MAP, encoding="utf-8")
    (req / "design" / "prototype.html").write_text(PROTOTYPE, encoding="utf-8")
    (req / "qa" / "checklist.md").write_text(CHECKLIST, encoding="utf-8")
    (req / "analytics" / "report.md").write_text(REPORT, encoding="utf-8")
    (req / "analytics" / "metric-definitions.md").write_text(METRICS, encoding="utf-8")
    (req / "stage-1.html").write_text(_stage_page(
        "STEP 1", "项目进入",
        '<p>确定当前需求，复用其 <code>requirements/&lt;name&gt;/</code> 目录，读取已有状态、决策与资料。</p>'
        '<div class="code">requirements/subflow/\n├── README.md\n├── source.md\n├── decisions.md\n├── open-questions.md\n├── research/  需求证据\n├── prd/       PRD\n├── design/    原型\n├── flows/     流程\n├── qa/        验收\n└── analytics/ 数据复盘</div>',
    ), encoding="utf-8")
    (req / "stage-3.html").write_text(_stage_page(
        "STEP 3", "需求闸门",
        '<p>进入 PRD 前运行需求挖掘终审闸门，判定需求材料是否足以支撑正式产出。</p>'
        '<span class="badge">provisional · 探索性演示</span>'
        '<p style="margin-top:14px">只有 <code>ready</code> 才能进入正式 PRD；<code>provisional</code> 只能做探索性方案；<code>blocked</code> 必须先补材料。</p>',
    ), encoding="utf-8")


def _generate(req: Path) -> None:
    _run("demand-report", "--requirement", str(req),
         "--csv", "research/feedback.csv",
         "--findings", "research/demand-findings.md",
         "--products", "research/products.csv",
         "--output", "research/demand-insight.html")
    _run("demand-gate", "--requirement", str(req), check=False)
    _run("render", "--requirement", str(req), "--kind", "prd",
         "--prototype", "design/prototype.html")
    _run("render", "--requirement", str(req), "--kind", "acceptance")
    _run("render", "--requirement", str(req), "--kind", "analytics")


def main() -> None:
    demo_dir = ROOT / "docs" / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        req = Path(tmp) / "subflow"
        _write_case(req)
        _generate(req)
        _record(req, demo_dir / "workflow.webm")
    print(f"workflow.webm: {(demo_dir / 'workflow.webm').stat().st_size} bytes")


def _record(req: Path, target: Path) -> None:
    from playwright.sync_api import sync_playwright

    video_dir = req.parent / "video"
    video_dir.mkdir()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=str(video_dir),
            record_video_size={"width": 1280, "height": 800},
        )
        page = context.new_page()

        # 1 项目进入
        page.goto((req / "stage-1.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2800)

        # 2 需求挖掘
        page.goto((req / "research" / "demand-insight.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(3000)

        # 3 需求闸门
        page.goto((req / "stage-3.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2800)

        # 4 PRD 评审
        page.goto((req / "prd" / "PRD-review.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(3200)

        # 5 流程 + 原型（点击操作）
        page.goto((req / "design" / "prototype.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2200)
        page.locator("#P01 .list-card").first.click()
        page.wait_for_timeout(1800)
        page.locator("#P02 button.danger").click()
        page.wait_for_timeout(1800)
        page.locator("#P03 button.danger").click()
        page.wait_for_timeout(1200)
        page.keyboard.press("Enter")  # dismiss the alert
        page.wait_for_timeout(800)

        # 6 验收
        page.goto((req / "qa" / "checklist-review.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2200)
        try:
            page.locator(".acceptance-status-button[data-status='通过']").first.click()
        except Exception:
            pass
        page.wait_for_timeout(1500)

        # 7 数据复盘
        page.goto((req / "analytics" / "report-review.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2200)
        page.locator('[data-funnel-base="previous"]').click()
        page.wait_for_timeout(1200)
        page.locator('#panel-5').scroll_into_view_if_needed()
        page.wait_for_timeout(1000)
        page.locator('.attribution-block[data-kind="hypothesis"] summary').click()
        page.wait_for_timeout(1400)

        context.close()
        browser.close()

    videos = list(video_dir.glob("*.webm"))
    if not videos:
        raise RuntimeError("no video produced")
    shutil.copy(videos[0], target)


if __name__ == "__main__":
    main()
