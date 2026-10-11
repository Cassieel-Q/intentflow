"""Record a full-workflow demo of IntentFlow as an animated GIF.

Builds a minimal but complete example case (a expense-tracking app, labelled
as demo data), renders every workflow stage's artifact, records one continuous
screen capture walking the seven stages — including clicking through the
operable prototype — then converts the recording into docs/demo/workflow.gif:

  1 项目进入 → 2 需求挖掘 → 3 需求闸门 → 4 PRD 评审
  → 5 流程+原型(点击操作) → 6 验收 → 7 数据复盘
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "intentflow.py"

# ---------------------------------------------------------------- demo case

FEEDBACK = """id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id
D-01,记账负担,日常消费,手动记账步骤太多,坚持不下去,几秒记完一笔,simulation,
D-02,分类不清,餐饮购物,不知道该选哪个分类,记录乱七八糟,分类自动又准确,simulation,
D-03,预算失控,月底结账,月底才发现超支,存不下钱,超支前提前提醒,simulation,
"""

PRODUCTS = """name,official_url,observed_capability,unverified,source_id
示例记账产品,https://example.org/bill,快速记账与分类统计,实际效果未核实,S-01
"""

SOURCE = """# 材料与来源

| ID | 材料 | 来源位置 | 获取日期 | 适用范围 |
| --- | --- | --- | --- | --- |
| S-01 | 公开产品页 | https://example.org/bill | 2026-10-11 | 演示 |
"""

FINDINGS = """# 记账本 App 需求洞察

## 洞察总览

用户不缺记账工具，缺的是「几秒记完、超支提前知道」。以下为演示数据。

## 场景与材料

日常消费后记账坚持难；材料为模拟反馈与公开产品页。

## 反馈与聚类

- 记账负担：手动步骤太多，坚持不下去。
- 分类不清：不知道选哪个分类，记录混乱。
- 预算失控：月底才发现超支。

## 问题与归因

记账路径长与预算提醒缺失，是放弃记账的主要原因（待验证）。

## 公开产品参考

公开产品提供快速记账与分类统计，但效果未核实。

## 首版需求收口

首版聚焦记一笔、账单首页、分类统计与预算提醒。

## 验证与指标

记账完成率、次日记账留存率、预算设置率。

## 待确认结论

预算默认值仍待确认。
"""

PRD = """# 记账本 App 功能需求文档

## 文档概述

- 标题：记账本 App
- 版本号：V0.1
- 作者：IntentFlow 演示
- 日期：2026-10-11
- 状态：探索性草案（演示数据）
- 适用对象：产品、设计、开发、测试
- 证据状态：provisional
- 变更摘要：首版聚焦记一笔、账单首页、分类统计与预算提醒。

## 需求背景和目标

### 项目背景

- 问题现状：日常消费后记账坚持难，月底才发现超支。
- 数据佐证：模拟反馈 3 条，公开产品页 1 个（演示）。
- 归因分析：记账路径长与预算提醒缺失是主因（待验证）。
- 解决方案：几秒记完一笔，分类自动，预算超支提前提醒。
- 产品价值：降低记账负担，帮助用户看清并控制支出。

### 需求目标

- 用户目标：几秒记完一笔，月底不超支。
- 业务/研究目标：验证简化记账路径能否提升坚持率。
- 衡量指标：记账完成率、预算设置率。
- 分子/分母：保存成功 / 开始记账；设置预算 / 进入统计。

## 功能详细说明

### 功能列表

| 优先级 | 功能 ID | 功能名称 | 功能流程 | 原型图/状态 | 功能描述 | 数据策略 | 特殊场景 | 依赖项 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | F-01 | 记一笔 | 首页 → 记一笔 → 保存 | P02 | 几秒记录一笔支出 | 账单记录 | 空金额拦截 | 本地存储 |
| P0 | F-02 | 账单首页 | 进入 → 查看今日与最近 | P01 | 汇总展示今日与最近账单 | 账单记录 | 空状态 | 本地存储 |
| P0 | F-03 | 分类统计 | 首页 → 查看统计 | P03 | 按分类汇总本月支出 | 金额汇总 | 无 | 账单数据 |
| P1 | F-04 | 月度切换 | 首页 → 切换月份 | P01 | 按月查看账单 | 月度汇总 | 无 | 账单数据 |
| P1 | F-05 | 预算提醒 | 统计 → 设置预算 | P03 | 超支前提醒 | 预算设置 | 无 | 通知 |

### F-01 记一笔

#### 功能原型与交互说明

| 序号与功能名称 | 原型图/状态 | 详细说明 |
| --- | --- | --- |
| 1. 记一笔 | [[prototype:P02]] | **页面元素**：金额、分类网格、保存按钮。<br>**功能流程**：首页 → 记一笔 → 选分类 → 保存。<br>**展示/交互说明**：点选分类高亮，保存后回首页并置顶新账单。<br>**数据策略**：金额 + 分类 + 时间写入账单。<br>**边界/异常说明**：金额为 0 时不可保存。<br>**埋点关联**：EVT-02、EVT-03。 |

### F-02 账单首页

#### 功能原型与交互说明

| 序号与功能名称 | 原型图/状态 | 详细说明 |
| --- | --- | --- |
| 1. 账单首页 | [[prototype:P01]] | **页面元素**：今日支出、最近账单、记一笔按钮。<br>**功能流程**：进入 → 查看今日与最近账单。<br>**数据策略**：按时间倒序展示。<br>**边界/异常说明**：无账单时显示空状态。<br>**埋点关联**：EVT-01。 |

### F-03 分类统计

#### 功能原型与交互说明

| 序号与功能名称 | 原型图/状态 | 详细说明 |
| --- | --- | --- |
| 1. 分类统计 | [[prototype:P03]] | **页面元素**：本月总额、分类条形。<br>**功能流程**：首页 → 统计。<br>**数据策略**：按分类汇总。<br>**埋点关联**：EVT-04。 |

## 非功能需求

- 性能：首页加载目标在真实设备测试后确认。
- 安全性：账单仅保存在用户设备。

## 数据埋点

### 分析思路

先回答记账完成率与预算设置率两个问题。

### 埋点表

| 事件 ID | 参数名 | 参数说明 | 埋点时机 | 触发条件 | 关联指标 |
| --- | --- | --- | --- | --- | --- |
| EVT-01 | bill_home_viewed | 查看首页 | 进入首页 | 首页加载成功 | 进入人数 |
| EVT-02 | bill_entry_started | 开始记账 | 打开记一笔 | 点击记一笔 | 开始人数 |
| EVT-03 | bill_saved | 保存账单 | 保存成功 | 金额合法 | 记账完成率 |
| EVT-04 | stats_viewed | 查看统计 | 打开统计 | 点击统计 | 统计人数 |

## 附录

### 参考文档

- 需求洞察：[research/demand-findings.md](../research/demand-findings.md)
- 来源登记：[source.md](../source.md)
"""

STATE_MAP = """| State ID | PRD behavior ID | Entry/trigger | Visible state | Available action | Next state | Asset link | Data status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | F-02 | 进入 | 账单首页 | 记一笔/统计 | P02 | #P01 | 模拟 |
| P02 | F-01 | 点击记一笔 | 记一笔 | 选分类保存 | P01 | #P02 | 模拟 |
| P03 | F-03、F-05 | 点击统计 | 分类统计 | 设置预算 | P01 | #P03 | 模拟 |
"""

PROTOTYPE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>记账本 App 原型</title><style>
*{box-sizing:border-box} body{margin:0;font:14px/1.6 system-ui,"Microsoft YaHei",sans-serif;background:#e9edf2;color:#243044}
.app{max-width:520px;margin:0 auto;background:#f6f8fb;min-height:100vh;position:relative}
.screen{display:none;padding-bottom:90px} .screen.active{display:block}
.navbar{background:#1f7a5c;color:#fff;padding:18px 20px;font-size:18px;font-weight:700;display:flex;justify-content:space-between;align-items:center}
.navbar .back{color:#fff;text-decoration:none;font-size:14px}
.body{padding:16px}
.today{background:linear-gradient(120deg,#1f7a5c,#2b9d77);color:#fff;border-radius:16px;padding:20px;margin-bottom:16px}
.today .label{font-size:13px;opacity:.85} .today .num{font-size:34px;font-weight:800;margin-top:4px}
.today .row2{display:flex;justify-content:space-between;margin-top:10px;font-size:13px;opacity:.9}
.section-title{font-size:13px;color:#6a7a8e;margin:2px 2px 10px}
.bill{background:#fff;border-radius:14px;padding:14px 16px;display:flex;align-items:center;gap:14px;margin-bottom:10px;box-shadow:0 1px 2px rgba(20,40,70,.05)}
.bill .ic{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;font-size:20px;flex:0 0 auto}
.bill .info{flex:1} .bill .name{font-weight:600} .bill .sub{color:#8a96a6;font-size:12.5px}
.bill .amt{font-weight:700}
.fab{position:absolute;right:22px;bottom:26px;background:#1f7a5c;color:#fff;border:0;border-radius:999px;padding:14px 22px;font-size:15px;font-weight:700;cursor:pointer;box-shadow:0 6px 16px rgba(31,122,92,.4)}
.amount-display{text-align:center;padding:26px 0 10px}
.amount-display .num{font-size:44px;font-weight:800;color:#243044}
.amount-display .label{color:#8a96a6;font-size:13px}
.cat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;padding:10px 0 20px}
.cat{background:#fff;border:2px solid transparent;border-radius:14px;padding:14px 4px;text-align:center;cursor:pointer}
.cat .e{font-size:24px} .cat .t{font-size:12.5px;margin-top:4px;color:#51647a}
.cat.selected{border-color:#1f7a5c;background:#edf7f3}
.save-btn{width:100%;background:#1f7a5c;color:#fff;border:0;border-radius:12px;padding:14px;font-size:16px;font-weight:700;cursor:pointer}
.bar-row{margin-bottom:14px} .bar-row .t{display:flex;justify-content:space-between;font-size:13.5px;margin-bottom:5px}
.bar-row .t b{font-weight:600} .bar-track{height:10px;background:#e4e9ef;border-radius:999px;overflow:hidden}
.bar-fill{height:100%;border-radius:999px}
.total-card{background:#fff;border-radius:14px;padding:16px;display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.total-card b{font-size:22px;color:#1f7a5c}
.budget{background:#fff;border-radius:14px;padding:14px 16px;display:flex;gap:12px;align-items:center;margin-top:16px}
.budget input{flex:1;border:1px solid #c9d4e0;border-radius:10px;padding:10px;font:inherit}
</style></head><body data-intentflow-viewport="520x900">
<div class="app">

<section id="P01" class="screen">
  <div class="navbar">简记账本 <span style="font-size:13px;font-weight:400">10 月</span></div>
  <div class="body">
    <div class="today"><div class="label">今日支出</div><div class="num" id="today-num">¥128.50</div>
      <div class="row2"><span>本月累计 ¥2,340.20</span><span>预算 ¥3,000</span></div></div>
    <div class="section-title">最近账单</div>
    <div id="bill-list">
      <div class="bill"><div class="ic" style="background:#fdf1e7">🍜</div><div class="info"><div class="name">餐饮</div><div class="sub">午餐 · 12:02</div></div><div class="amt">-¥28.00</div></div>
      <div class="bill"><div class="ic" style="background:#e7f0ff">🚕</div><div class="info"><div class="name">交通</div><div class="sub">打车 · 09:40</div></div><div class="amt">-¥18.50</div></div>
      <div class="bill"><div class="ic" style="background:#f3ecfb">🛒</div><div class="info"><div class="name">购物</div><div class="sub">日用品 · 昨天</div></div><div class="amt">-¥82.00</div></div>
      <div class="bill"><div class="ic" style="background:#e7f6f1">☕</div><div class="info"><div class="name">餐饮</div><div class="sub">咖啡 · 昨天</div></div><div class="amt">-¥18.00</div></div>
    </div>
  </div>
  <button class="fab" onclick="go('P02')">＋ 记一笔</button>
</section>

<section id="P02" class="screen">
  <div class="navbar"><a class="back" onclick="go('P01')">← 返回</a> 记一笔</div>
  <div class="body">
    <div class="amount-display"><div class="label">支出金额</div><div class="num">¥25.00</div></div>
    <div class="cat-grid" id="cats">
      <div class="cat" data-name="餐饮"><div class="e">🍜</div><div class="t">餐饮</div></div>
      <div class="cat" data-name="交通"><div class="e">🚕</div><div class="t">交通</div></div>
      <div class="cat" data-name="购物"><div class="e">🛒</div><div class="t">购物</div></div>
      <div class="cat" data-name="娱乐"><div class="e">🎮</div><div class="t">娱乐</div></div>
    </div>
    <button class="save-btn" onclick="save()">保存</button>
  </div>
</section>

<section id="P03" class="screen">
  <div class="navbar"><a class="back" onclick="go('P01')">← 返回</a> 分类统计</div>
  <div class="body">
    <div class="total-card"><div><div style="color:#8a96a6;font-size:13px">本月支出</div><b>¥2,340.20</b></div><span class="pill" style="border:1px solid #c9d4e0;border-radius:999px;padding:2px 9px;color:#51647a;font-size:12px">预算 ¥3,000 · 剩 22%</span></div>
    <div class="section-title">分类占比</div>
    <div class="bar-row"><div class="t"><b>🍜 餐饮</b><span>¥980 · 42%</span></div><div class="bar-track"><div class="bar-fill" style="width:42%;background:#1f7a5c"></div></div></div>
    <div class="bar-row"><div class="t"><b>🛒 购物</b><span>¥640 · 27%</span></div><div class="bar-track"><div class="bar-fill" style="width:27%;background:#2b9d77"></div></div></div>
    <div class="bar-row"><div class="t"><b>🏠 居住</b><span>¥420 · 18%</span></div><div class="bar-track"><div class="bar-fill" style="width:18%;background:#57b896"></div></div></div>
    <div class="bar-row"><div class="t"><b>🚕 交通</b><span>¥180 · 8%</span></div><div class="bar-track"><div class="bar-fill" style="width:8%;background:#8fd0ba"></div></div></div>
    <div class="bar-row"><div class="t"><b>🎮 娱乐</b><span>¥120 · 5%</span></div><div class="bar-track"><div class="bar-fill" style="width:5%;background:#bfe4d6"></div></div></div>
    <div class="budget">💰 <span>月预算</span><input value="3000"><span>元</span></div>
  </div>
</section>

</div>
<script>
function go(id){location.hash=id}
function show(id){document.querySelectorAll('.screen').forEach(function(s){s.classList.remove('active')});var el=document.getElementById(id);if(el)el.classList.add('active')}
show(location.hash.slice(1)||'P01');
window.addEventListener('hashchange',function(){show(location.hash.slice(1)||'P01')});
var picked='餐饮';
document.querySelectorAll('#cats .cat').forEach(function(c){
  c.addEventListener('click',function(){
    document.querySelectorAll('#cats .cat').forEach(function(x){x.classList.remove('selected')});
    c.classList.add('selected');picked=c.dataset.name;
  });
});
document.querySelector('#cats .cat').classList.add('selected');
function save(){
  var list=document.getElementById('bill-list');
  var div=document.createElement('div');div.className='bill';
  div.innerHTML='<div class="ic" style="background:#edf7f3">🍜</div><div class="info"><div class="name">餐饮</div><div class="sub">刚刚</div></div><div class="amt">-¥25.00</div>';
  list.insertBefore(div,list.firstChild);
  var num=document.getElementById('today-num');
  num.textContent='¥153.50';
  go('P01');
}
</script></body></html>
"""

CHECKLIST = """# 记账本 App 验收清单

| ID | 来源 | 优先级 | 前置条件 | 步骤 | 期望结果 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AC-01 | F-02 | P0 | 已有账单 | 进入首页 | 展示今日与最近账单 | 未测 | |
| AC-02 | F-02 | P0 | 无账单 | 进入首页 | 显示空状态 | 未测 | |
| AC-03 | F-01 | P0 | 首页 | 点击记一笔 | 打开记账页 | 未测 | |
| AC-04 | F-01 | P0 | 记账页 | 选分类并保存 | 账单置顶并更新今日 | 未测 | |
| AC-05 | F-01 | P0 | 金额为 0 | 点击保存 | 拦截保存 | 未测 | |
| AC-06 | F-03 | P0 | 首页 | 点击统计 | 展示分类占比 | 未测 | |
"""

REPORT = """# 记账本 App 数据复盘报告

## 1. 复盘问题与产品决策

### 复盘问题

简化记账路径后，记账完成率与预算设置率是否达到预期？

### 本报告支持的决策

决定下一步是否继续压缩记账步骤，以及预算默认值如何定。以下为演示数据。

## 2. 数据契约

| 项目 | 本轮记录 |
| --- | --- |
| 提取日期 | 2026-10-11 |
| 观察窗口 | 2026-09-01 ~ 2026-09-30 |
| 分析单位 | 会话 |
| 主要来源 | events.csv（演示） |
| 样本量 | 6,318 会话 |
| 缺失字段 | 无 |
| 排除项 | 内部测试账号 |

## 3. 指标与可计算性

| 指标 | 目标口径 | 本轮结果 | 原因 |
| --- | --- | --- | --- |
| 记账完成率 | 保存成功 / 开始记账 | 86.2% | 可复算 |
| 预算设置率 | 设置预算 / 进入统计 | 21.5% | 可复算 |

## 4. 已观察事实

1. 记账完成率 86.2%，简化路径后保存顺畅。
2. 预算设置率 21.5%，大量用户从不设置预算。

## 5. 观察、推断与反例

### 观察

- 记账路径已足够短，放弃主要发生在开始记账之前。
### 推断（待验证）

- 预算设置入口太深，用户找不到，需把入口前置验证。
### 其他解释

- 低设置率也可能来自用户本来就没有预算习惯。

## 6. 可执行选项（均为助手建议）

1. **前置预算入口**：首页预算卡片直达设置，观察设置率变化。
2. **默认预算**：按上月支出给默认预算，用户可改。

## 8. 局限与复盘结论

- 本报告为演示数据。

**结论：**优先做预算入口前置，并小流量验证默认预算。
"""

METRICS = """# 指标定义

| 指标 | 单位 | 分子 | 分母 | 资格条件 | 时间窗/时区 | 去重键 | 当前基线 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 记账完成率 | 会话 | 保存成功的会话数 | 开始记账的会话数 | 打开记一笔 | 30 天 | session_id | 86.2% |
| 预算设置率 | 会话 | 设置预算的会话数 | 进入统计的会话数 | 进入统计 | 30 天 | session_id | 21.5% |

## 口径约束

- 会话级去重，同一会话多次保存只计一次。
- 以上数字为演示数据。
"""

STAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><style>
*{box-sizing:border-box} body{margin:0;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif;background:#f5f7fa;color:#243044;display:grid;place-items:center;min-height:100vh}
.card{background:#fff;border:1px solid #dfe5ec;border-radius:18px;padding:70px 90px;text-align:center;box-shadow:0 6px 24px rgba(20,40,70,.06)}
.eyebrow{color:#1f7a5c;font:600 15px/1 ui-monospace,monospace;letter-spacing:.28em}
h1{font-size:46px;margin:18px 0 0}
</style></head><body><div class="card">
<div class="eyebrow">__NO__</div><h1>__TITLE__</h1>
</div></body></html>
"""


def _stage_page(no: str, title: str) -> str:
    return STAGE_TEMPLATE.replace("__NO__", no).replace("__TITLE__", title)


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
    (req / "stage-1.html").write_text(_stage_page("STEP 1", "项目进入"), encoding="utf-8")
    (req / "stage-3.html").write_text(_stage_page("STEP 3", "需求闸门"), encoding="utf-8")


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


def _find_ffmpeg() -> Path | None:
    base = Path.home() / "AppData" / "Local" / "ms-playwright"
    if not base.is_dir():
        return None
    for child in sorted(base.glob("ffmpeg-*"), reverse=True):
        exe = child / "ffmpeg-win64.exe"
        if exe.is_file():
            return exe
    return None


def _record(req: Path, target: Path) -> None:
    from playwright.sync_api import sync_playwright

    def scroll(page, px: int) -> None:
        page.evaluate(f"window.scrollBy({{top: {px}, behavior: 'smooth'}})")

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
        page.on("dialog", lambda dialog: dialog.accept())

        # 1 项目进入
        page.goto((req / "stage-1.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2200)

        # 2 需求挖掘（滚动展示反馈卡片与聚类）
        page.goto((req / "research" / "demand-insight.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(1800)
        scroll(page, 700)
        page.wait_for_timeout(1500)
        scroll(page, 700)
        page.wait_for_timeout(1500)

        # 3 需求闸门
        page.goto((req / "stage-3.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2200)

        # 4 PRD 评审（滚动展示功能详情与嵌入原型）
        page.goto((req / "prd" / "PRD-review.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(1800)
        scroll(page, 800)
        page.wait_for_timeout(1700)
        scroll(page, 800)
        page.wait_for_timeout(1700)

        # 5 流程 + 原型（快速点击：记一笔 → 选分类 → 保存 → 统计）
        page.goto((req / "design" / "prototype.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(2000)
        page.locator(".fab").click()
        page.wait_for_timeout(900)
        page.locator('#cats .cat[data-name="餐饮"]').click()
        page.wait_for_timeout(700)
        page.locator(".save-btn").click()
        page.wait_for_timeout(1600)
        page.evaluate("location.hash='P03'")
        page.wait_for_timeout(2200)

        # 6 验收（滚动后点通过）
        page.goto((req / "qa" / "checklist-review.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(1600)
        scroll(page, 400)
        page.wait_for_timeout(1300)
        try:
            page.locator(".acceptance-status-button[data-status='通过']").first.click()
        except Exception:
            pass
        page.wait_for_timeout(1400)

        # 7 数据复盘（依次滚动浏览多个面板并交互）
        page.goto((req / "analytics" / "report-review.html").as_uri(), wait_until="networkidle")
        page.wait_for_timeout(1600)
        scroll(page, 800)
        page.wait_for_timeout(1300)
        page.locator('[data-funnel-base="previous"]').click()
        page.wait_for_timeout(1000)
        page.locator("#panel-5").scroll_into_view_if_needed()
        page.wait_for_timeout(900)
        page.locator('.attribution-block[data-kind="hypothesis"] summary').click()
        page.wait_for_timeout(1100)
        page.locator("#panel-7").scroll_into_view_if_needed()
        page.wait_for_timeout(1300)

        context.close()
        browser.close()

    videos = list(video_dir.glob("*.webm"))
    if not videos:
        raise RuntimeError("no video produced")
    shutil.copy(videos[0], target)


def _webm_to_gif(webm: Path, gif: Path) -> None:
    ffmpeg = _find_ffmpeg()
    if ffmpeg is None:
        raise RuntimeError("playwright ffmpeg not found")
    with tempfile.TemporaryDirectory() as tmp:
        frames_dir = Path(tmp) / "frames"
        frames_dir.mkdir()
        # The bundled ffmpeg has no -vf filter support, so extract every frame
        # and sample/scale with PIL instead.
        subprocess.run(
            [str(ffmpeg), "-y", "-i", str(webm), str(frames_dir / "f_%05d.png")],
            capture_output=True, check=True,
        )
        paths = sorted(frames_dir.glob("f_*.png"))
        # ~25fps source → take every 12th frame ≈ 2fps GIF.
        _frames_to_gif(paths[::12], gif)


def _frames_to_gif(frame_paths: list[Path], gif: Path) -> None:
    from PIL import Image

    images = []
    for p in frame_paths:
        image = Image.open(p).convert("RGB")
        image.thumbnail((800, 800))
        images.append(image)
    if not images:
        raise RuntimeError("no frames extracted")
    durations = [500] * len(images)
    durations[-1] = 1400
    images[0].save(
        gif, save_all=True, append_images=images[1:],
        duration=durations, loop=0, optimize=True,
    )


def main() -> None:
    demo_dir = ROOT / "docs" / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    gif = demo_dir / "workflow.gif"
    webm = demo_dir / "workflow.webm"
    with tempfile.TemporaryDirectory() as tmp:
        req = Path(tmp) / "expense-app"
        _write_case(req)
        _generate(req)
        _record(req, webm)
        _webm_to_gif(webm, gif)
    for f in (gif, webm):
        print(f"{f.name}: {f.stat().st_size} bytes")


if __name__ == "__main__":
    main()
