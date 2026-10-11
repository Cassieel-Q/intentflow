"""Generate a full-workflow demo GIF for IntentFlow.

Builds a minimal but complete example case (a subscription-management app,
clearly labelled as demo data), renders every workflow stage's artifact, and
produces docs/demo/workflow.gif walking through the seven stages in order:

  1-2 需求挖掘 → 3 需求闸门 → 4 PRD → 5 流程+原型 → 6 验收 → 7 数据复盘
"""

from __future__ import annotations

import io
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
*{{box-sizing:border-box}} body{{margin:0;font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif;background:#f5f7fa;color:#243044}}
.screen{{display:none;padding:24px;min-height:100vh;max-width:520px;margin:0 auto;background:#fff;border:1px solid #dfe5ec}}
.screen.active{{display:block}}
h1{{font-size:20px;margin:0 0 16px}} .card{{background:#fff;border:1px solid #dfe5ec;border-radius:12px;padding:16px;margin-bottom:12px}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid #f0f2f5}}
.row:last-child{{border:0}} .name{{font-weight:600}} .amount{{color:#1e5fa5;font-weight:700}}
.pill{{border:1px solid #c9d4e0;border-radius:999px;padding:2px 9px;color:#51647a;font-size:12px}}
button{{background:#1e5fa5;color:#fff;border:0;border-radius:8px;padding:9px 16px;cursor:pointer;font:inherit}}
button.danger{{background:#a04e45}} .muted{{color:#6a7a8e}} .empty{{text-align:center;padding:40px 0;color:#6a7a8e}}
.detail-line{{padding:10px 0;border-bottom:1px solid #f0f2f5}} .detail-line b{{display:inline-block;width:80px;color:#6a7a8e}}
</style></head><body data-intentflow-viewport="520x900">
<section id="P01" class="screen"><h1>订阅管理</h1>
<div class="card"><div class="row"><div><div class="name">视频会员</div><div class="muted">每月 30 元</div></div><span class="amount">¥30</span></div>
<div class="row"><div><div class="name">云存储</div><div class="muted">每年 298 元</div></div><span class="amount">¥298</span></div>
<div class="row"><div><div class="name">音乐会员</div><div class="muted">每月 15 元</div></div><span class="amount">¥15</span></div></div>
<div class="muted" style="margin-top:12px">本月支出 ¥343 · 点击卡片查看详情</div></section>
<section id="P02" class="screen"><h1>订阅详情</h1>
<div class="card"><div class="detail-line"><b>名称</b>视频会员</div>
<div class="detail-line"><b>金额</b>¥30 / 月</div>
<div class="detail-line"><b>状态</b><span class="pill">生效中</span></div>
<div class="detail-line"><b>下次扣费</b>2026-11-01</div></div>
<div style="display:flex;gap:10px;margin-top:16px"><button onclick="go('P03')">取消订阅</button><button onclick="alert('已开启续费提醒')">开启提醒</button></div></section>
<section id="P03" class="screen"><h1>取消订阅</h1>
<div class="card"><p>确定取消「视频会员」吗？取消后当前周期结束即停止。</p>
<div style="display:flex;gap:10px;margin-top:8px"><button class="danger" onclick="alert('已取消')">确认取消</button><button onclick="go('P01')">返回</button></div></div></section>
<script>
function go(id){{location.hash=id}}
function show(id){{document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));document.getElementById(id).classList.add('active')}}
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

STAGES = [
    ("步骤 1-2 · 需求挖掘", "research/demand-insight.html", None),
    ("步骤 3 · 需求闸门", None, "provisional · 探索性演示"),
    ("步骤 4 · PRD 评审", "prd/PRD-review.html", None),
    ("步骤 5 · 流程 + 原型", "design/prototype.html", None),
    ("步骤 6 · 验收", "qa/checklist-review.html", None),
    ("步骤 7 · 数据复盘", "analytics/report-review.html", None),
]


def _run(*args: str, check: bool = True) -> None:
    result = subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"command failed: {args}\n{result.stderr}")


def _write_case(req: Path) -> None:
    (req / "research").mkdir(parents=True)
    (req / "prd").mkdir(parents=True)
    (req / "design").mkdir(parents=True)
    (req / "flows").mkdir(parents=True)
    (req / "qa").mkdir(parents=True)
    (req / "analytics").mkdir(parents=True)
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
        _capture(req, demo_dir / "workflow.gif")
    print(f"workflow.gif: {(demo_dir / 'workflow.gif').stat().st_size} bytes")


def _capture(req: Path, target: Path) -> None:
    from playwright.sync_api import sync_playwright

    shots: list[tuple[str, bytes | None, str | None]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        for stage, rel, gate_text in STAGES:
            if rel is None:
                shots.append((stage, None, gate_text))
                continue
            html = req / rel
            page.goto(html.as_uri(), wait_until="networkidle")
            page.wait_for_timeout(700)
            shots.append((stage, page.screenshot(), None))
        browser.close()

    _write_staged_gif(shots, target)


def _load_font(size: int):
    from PIL import ImageFont

    for path in ("C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttc",
                 "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/simsun.ttc"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return None


def _write_staged_gif(shots: list[tuple[str, bytes | None, str | None]], target: Path) -> None:
    from PIL import Image, ImageDraw

    font = _load_font(30)
    font_small = _load_font(22)

    images = []
    for stage, raw, gate_text in shots:
        if raw is not None:
            image = Image.open(io.BytesIO(raw)).convert("RGB")
            image.thumbnail((860, 860))
        else:
            # Text card for the gate stage.
            image = Image.new("RGB", (860, 540), (245, 247, 250))
            draw = ImageDraw.Draw(image)
            if font:
                draw.text((60, 180), stage, fill=(36, 48, 68), font=font)
                draw.text((60, 240), "需求闸门结果：", fill=(106, 122, 142), font=font_small)
                draw.text((60, 290), "provisional", fill=(178, 80, 0), font=font)
                draw.text((60, 340), "探索性演示 · 模拟数据仅验证流程与展示", fill=(106, 122, 142), font=font_small)
        if raw is None or font:
            draw = ImageDraw.Draw(image)
            if font:
                w, _ = image.size
                box = draw.textbbox((0, 0), stage, font=font)
                tw, th = box[2] - box[0], box[3] - box[1]
                draw.rectangle([0, 0, tw + 28, th + 18], fill=(30, 95, 165))
                draw.text((14, 9), stage, fill=(255, 255, 255), font=font)
        images.append(image)

    durations = [1300] * len(images)
    if durations:
        durations[-1] = 1800
    images[0].save(
        target, save_all=True, append_images=images[1:],
        duration=durations, loop=0, optimize=True,
    )


if __name__ == "__main__":
    main()
