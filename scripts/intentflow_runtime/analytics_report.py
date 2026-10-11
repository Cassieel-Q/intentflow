"""Generate an optional, interactive analytics view from the formal analytics record.

Markdown (`analytics/report.md` + `analytics/metric-definitions.md`) stays the
formal record. This module only derives an HTML dashboard, so rendering never
edits the report or metric definitions. With no real data it renders a clearly
labelled 演示/不可计算 demonstration instead of an apparent product result.

Panels follow `skills/product-analytics/SKILL.md` "Interactive analysis view":
分析总览 / 转化漏斗 / 每日趋势 / 分群诊断 / 洞察归因 / 行动建议 / 数据质量.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


# The funnel and segment panels are derived from the metric definitions in
# `analytics/metric-definitions.md`; nothing case-specific is hardcoded here.

PANEL_NAMES = [
    "分析总览", "转化漏斗", "每日趋势", "分群诊断", "洞察归因", "行动建议", "数据质量",
]


def _safe(value: str) -> str:
    return html.escape(value or "", quote=True)


def _split_sections(md: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", md, re.MULTILINE))
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(md)
        sections[heading] = md[match.end():end].strip()
    return sections


def _split_subsections(body: str) -> dict[str, str]:
    subsections: dict[str, str] = {}
    matches = list(re.finditer(r"^###\s+(.+?)\s*$", body, re.MULTILINE))
    if not matches:
        return {"": body}
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        subsections[heading] = body[match.end():end].strip()
    return subsections


def _find_section(sections: dict[str, str], *keywords: str) -> str:
    for title, body in sections.items():
        if all(keyword in title for keyword in keywords):
            return body
    return ""


def _parse_table(body: str) -> tuple[list[str], list[list[str]]]:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|") or index + 1 >= len(lines):
            continue
        separator = lines[index + 1].strip()
        if not separator.startswith("|") or set(separator.replace("|", "").replace(":", "").replace("-", "").replace(" ", "")):
            continue
        headers = [cell.strip() for cell in stripped.strip("|").split("|")]
        rows: list[list[str]] = []
        for row_line in lines[index + 2:]:
            row_line = row_line.strip()
            if not row_line.startswith("|"):
                break
            rows.append([cell.strip() for cell in row_line.strip("|").split("|")])
        return headers, rows
    return [], []


def _numbered_list(body: str) -> list[str]:
    items: list[str] = []
    for line in body.splitlines():
        match = re.match(r"^\s*(?:\d+\.|-|\*)\s+(.+)$", line)
        if match:
            items.append(match.group(1).strip())
    return items


def _parse(report_md: str, metrics_md: str) -> dict:
    title_match = re.search(r"^#\s+(.+?)\s*$", report_md, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "数据复盘报告"

    sections = _split_sections(report_md)

    # 2. Data contract (key/value table)
    contract: dict[str, str] = {}
    contract_body = _find_section(sections, "数据契约")
    if contract_body:
        _, rows = _parse_table(contract_body)
        for row in rows:
            if len(row) >= 2 and row[0]:
                contract[row[0]] = row[1]

    # 3. Metric computability (指标 | 目标口径 | 本轮结果 | 原因)
    computability: list[dict] = []
    comp_body = _find_section(sections, "指标")
    if comp_body:
        headers, rows = _parse_table(comp_body)
        for row in rows:
            if len(row) >= 2 and row[0]:
                computability.append({
                    "metric": row[0],
                    "target": row[1] if len(row) > 1 else "",
                    "result": row[2] if len(row) > 2 else "",
                    "reason": row[3] if len(row) > 3 else "",
                })

    # 4. Observed facts
    observations = _numbered_list(_find_section(sections, "观察事实"))

    # 5. Attribution (观察 / 推断 / 其他解释)
    attribution_body = _find_section(sections, "推断")
    if not attribution_body:
        attribution_body = _find_section(sections, "观察", "反例")
    attribution: dict[str, list[str]] = {}
    for sub, body in _split_subsections(attribution_body).items():
        items = _numbered_list(body)
        if items:
            attribution[sub] = items

    # 6. Actions
    actions = _numbered_list(_find_section(sections, "选项"))
    if not actions:
        actions = _numbered_list(_find_section(sections, "建议"))

    # 8. Conclusion and limits
    conclusion_body = _find_section(sections, "局限")
    if not conclusion_body:
        conclusion_body = _find_section(sections, "结论")
    conclusion_match = re.search(r"\*\*结论[：:]\*\*\s*(.+)", conclusion_body, re.DOTALL)
    conclusion = conclusion_match.group(1).strip() if conclusion_match else ""
    limits = _numbered_list(conclusion_body)

    # Metric definitions table (指标 | 单位 | 分子 | 分母 | 资格条件 | 时间窗/时区 | 去重键 | 当前基线)
    metric_defs: list[dict] = []
    m_headers, m_rows = _parse_table(metrics_md)
    for row in m_rows:
        if len(row) >= 2 and row[0]:
            metric_defs.append({
                "metric": row[0],
                "unit": row[1] if len(row) > 1 else "",
                "numerator": row[2] if len(row) > 2 else "",
                "denominator": row[3] if len(row) > 3 else "",
                "eligibility": row[4] if len(row) > 4 else "",
                "window": row[5] if len(row) > 5 else "",
                "dedup": row[6] if len(row) > 6 else "",
                "baseline": row[7] if len(row) > 7 else "",
            })

    # Metric constraints (口径约束)
    constraints: list[str] = []
    constraint_body = _find_section(_split_sections(metrics_md), "口径约束")
    if constraint_body:
        constraints = _numbered_list(constraint_body)

    return {
        "title": title,
        "contract": contract,
        "computability": computability,
        "observations": observations,
        "attribution": attribution,
        "actions": actions,
        "conclusion": conclusion,
        "limits": limits,
        "metric_defs": metric_defs,
        "constraints": constraints,
    }


def _computable(result: str) -> bool:
    return bool(result) and "不可计算" not in result and "不能" not in result and "尚无" not in result


def _overview_cards(data: dict) -> str:
    contract = data["contract"]
    cards = []
    sample = contract.get("样本量", "")
    if sample:
        cards.append(f'<article class="stat-card"><span>样本量</span><strong>{_safe(sample)}</strong><small>分析单位</small></article>')
    missing = contract.get("缺失字段", "")
    missing_count = len([m for m in re.split(r"[、,，]", missing) if m.strip()]) if missing else 0
    cards.append(f'<article class="stat-card"><span>缺失字段</span><strong>{missing_count}</strong><small>不可计算的原因</small></article>')
    cards.append(f'<article class="stat-card"><span>指标定义</span><strong>{len(data["metric_defs"])}</strong><small>来自 metric-definitions</small></article>')
    cards.append(f'<article class="stat-card"><span>行动建议</span><strong>{len(data["actions"])}</strong><small>助手建议·待确认</small></article>')
    return "".join(cards)


def _funnel_panel(data: dict) -> str:
    metric_defs = data["metric_defs"]
    computable_metrics = {row["metric"] for row in data["computability"] if _computable(row["result"])}
    has_data = bool(computable_metrics)
    if not metric_defs:
        return (
            '<div class="panel-notice"><b>转化漏斗：</b>未在 <code>analytics/metric-definitions.md</code> '
            '中登记指标，无法构建漏斗。</div>'
        )
    stages_html = []
    for metric in metric_defs:
        ok = metric["metric"] in computable_metrics
        status = "可计算" if ok else "不可计算"
        denominator = metric["denominator"] or "—"
        numerator = metric["numerator"] or "—"
        stages_html.append(
            f'<div class="funnel-stage">'
            f'<div class="funnel-stage-head"><span class="funnel-label">{_safe(metric["metric"])}</span>'
            f'<span class="funnel-event">分母：{_safe(denominator)}</span>'
            f'<span class="funnel-event">分子：{_safe(numerator)}</span></div>'
            f'<div class="funnel-bar"><span class="funnel-count">—</span><small>{_safe(status)}</small></div>'
            f'</div>'
        )
    status_text = "有可计算指标" if has_data else "无真实事件数据"
    return (
        f'<div class="panel-notice {"ok" if has_data else ""}"><b>漏斗状态：</b>{status_text}。'
        f'以下步骤由 <code>metric-definitions.md</code> 的指标分子/分母派生，当前没有真实会话与事件流，'
        f'无法计算人数和转化率，仅展示结构。</div>'
        f'<div class="seg-toggle" role="group" aria-label="漏斗口径">'
        f'<button class="active" data-funnel-base="first">相对首指标</button>'
        f'<button data-funnel-base="previous">相对上一指标</button>'
        f'</div>'
        f'<div class="funnel">{"".join(stages_html)}</div>'
        f'<p class="muted" id="funnel-base-note">口径：相对首个指标计算转化率。</p>'
    )


def _trend_panel(data: dict) -> str:
    contract = data["contract"]
    window = contract.get("观察窗口", "不适用；当前无真实产品事件流")
    return (
        f'<div class="panel-notice"><b>每日趋势：</b>不可计算。当前没有真实时间戳，无法按日聚合。'
        f'观察窗口记录为「{_safe(window)}」。</div>'
        f'<div class="trend-placeholder"><div class="trend-axes"></div>'
        f'<div class="trend-empty">需要真实 <code>timestamp</code> 后才能绘制趋势</div></div>'
        f'<ul class="muted">'
        f'<li>趋势图只在存在真实时间戳时渲染；否则保留本占位并标注不可计算。</li>'
        f'<li>需要字段：事件时间戳、会话 ID、阶段、指标值。</li>'
        f'</ul>'
    )


def _segments_panel(data: dict) -> str:
    metric_defs = data["metric_defs"]
    dims = []
    for metric in metric_defs:
        for label, value in (("资格条件", metric["eligibility"]), ("去重键", metric["dedup"])):
            if value and value.strip() and value.strip() not in {"未建立", "—", ""}:
                dims.append((metric["metric"], label, value))
    if not dims:
        dim_list = '<div class="panel-notice"><b>分群诊断：</b>指标定义未登记可用于分群的维度。</div>'
    else:
        dim_list = "".join(
            f'<article class="segment-dim"><h4>{_safe(metric)}</h4>'
            f'<p><b>{_safe(label)}</b>{_safe(value)}</p></article>'
            for metric, label, value in dims
        )
    return (
        f'<div class="panel-notice"><b>分群诊断：</b>不可计算。没有真实会话级分群字段，不能从聚合值推断任何人群结论。</div>'
        f'<p class="muted">指标定义中登记的可分群字段（资格条件 / 去重键）：</p>'
        f'<div class="segment-list">{dim_list}</div>'
    )


def _attribution_panel(data: dict) -> str:
    attribution = data["attribution"]
    if not attribution:
        return '<div class="panel-notice"><b>洞察归因：</b>尚未记录观察与推断。</div>'
    blocks = []
    order = [("观察", "observation"), ("推断", "hypothesis"), ("其他解释", "counter")]
    for label, key in order:
        match = next((items for heading, items in attribution.items() if key in heading or (label in heading)), None)
        if match is None and label == "观察":
            match = next((items for heading, items in attribution.items() if "观察" in heading), None)
        if match is None and label == "推断":
            match = next((items for heading, items in attribution.items() if "推断" in heading), None)
        if match is None and label == "其他解释":
            match = next((items for heading, items in attribution.items() if "其他" in heading or "反例" in heading or "解释" in heading), None)
        if match is None:
            continue
        open_attr = " open" if label == "观察" else ""
        items_html = "".join(f"<li>{_safe(item)}</li>" for item in match)
        blocks.append(
            f'<details class="attribution-block" data-kind="{_safe(key)}"{open_attr}>'
            f'<summary><span class="attribution-dot"></span>{_safe(label)}<span class="muted">{len(match)} 条</span></summary>'
            f'<ul>{items_html}</ul></details>'
        )
    return (
        f'<p class="muted">「观察」是已记录的事实；「推断」是待验证假设；「其他解释」是需要区分的替代原因。'
        f'一次指标变化只是观察，产品机制在测试前只是假设。</p>'
        + "".join(blocks)
    )


def _actions_panel(data: dict) -> str:
    actions = data["actions"]
    if not actions:
        return '<div class="panel-notice"><b>行动建议：</b>尚未给出可执行选项。</div>'
    items = []
    for index, action in enumerate(actions, 1):
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", action).strip()
        if "：" in text:
            label, _, detail = text.partition("：")
            label = label.strip()
            detail = detail.strip()
        elif ":" in text:
            label, _, detail = text.partition(":")
            label = label.strip()
            detail = detail.strip()
        else:
            label = f"选项 {index}"
            detail = text
        items.append(
            f'<label class="action-item"><input type="checkbox" data-action>'
            f'<span class="action-check"></span>'
            f'<span class="action-body"><b>{_safe(label)}</b><span class="action-detail">{_safe(detail)}</span></span>'
            f'<span class="pill">助手建议·待确认</span></label>'
        )
    return (
        f'<div class="panel-notice"><b>以下均为助手建议</b>，在你确认前不进入实现。勾选用于标记你倾向采纳的项，'
        f'不会被写回正式报告。</div>'
        f'<div class="action-list">{"".join(items)}</div>'
        f'<p class="muted" id="action-count">已勾选 0 / {len(actions)} 条。</p>'
    )


def _quality_panel(data: dict) -> str:
    rows = []
    for row in data["computability"]:
        ok = _computable(row["result"])
        status = "可计算" if ok else "不可计算"
        rows.append(
            f'<tr data-computable="{"yes" if ok else "no"}">'
            f'<td>{_safe(row["metric"])}</td><td>{_safe(row["result"] or "—")}</td>'
            f'<td class="{"ok" if ok else "warn"}">{status}</td><td>{_safe(row["reason"])}</td></tr>'
        )
    missing = data["contract"].get("缺失字段", "—")
    constraints = "".join(f"<li>{_safe(item)}</li>" for item in data["constraints"])
    return (
        f'<div class="quality-toolbar">'
        f'<span class="muted">按状态筛选：</span>'
        f'<div class="seg-toggle" role="group" aria-label="质量筛选">'
        f'<button class="active" data-quality="all">全部</button>'
        f'<button data-quality="no">仅不可计算</button>'
        f'</div></div>'
        f'<div class="quality-callout">'
        f'<h4>缺失字段</h4><p>{_safe(missing)}</p>'
        f'</div>'
        f'<div class="table-wrap"><table><thead><tr>'
        f'<th>指标</th><th>本轮结果</th><th>状态</th><th>原因</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
        f'<h4 style="margin-top:18px">口径约束</h4><ul class="muted">{constraints}</ul>'
    )


def build_analytics_html(report_path: Path, metrics_path: Path, output: Path) -> Path:
    report_md = Path(report_path).read_text(encoding="utf-8")
    metrics_md = Path(metrics_path).read_text(encoding="utf-8")
    data = _parse(report_md, metrics_md)

    title = data["title"]
    contract = data["contract"]
    material = contract.get("主要来源", "—")
    window = contract.get("观察窗口", "—")
    extract = contract.get("提取日期", "—")
    conclusion = data["conclusion"]

    nav = "".join(
        f'<a href="#panel-{index}" data-nav="panel-{index}"><span class="nav-num">0{index}</span>{_safe(name)}</a>'
        for index, name in enumerate(PANEL_NAMES, 1)
    )

    panels = "".join([
        f'<section class="panel" id="panel-1"><div class="panel-head"><div class="eyebrow">01 · Overview</div>'
        f'<h2>分析总览</h2></div>'
        f'<div class="notice"><b>材料状态：</b>本页由 <code>analytics/report.md</code> 与 <code>analytics/metric-definitions.md</code> 派生，'
        f'所有指标当前均<strong>不可计算</strong>，仅作为交互式分析视图的格式演示，不代表任何产品结果。</div>'
        f'<div class="stat-grid">{_overview_cards(data)}</div>'
        f'<div class="contract-grid">'
        f'<div><span>提取日期</span><b>{_safe(extract)}</b></div>'
        f'<div><span>观察窗口</span><b>{_safe(window)}</b></div>'
        f'<div><span>主要来源</span><b>{_safe(material)}</b></div>'
        f'</div>'
        f'<div class="conclusion"><span>一句话结论</span><p>{_safe(conclusion) or "尚未形成结论。"}</p></div>'
        f'</section>',
        f'<section class="panel" id="panel-2"><div class="panel-head"><div class="eyebrow">02 · Funnel</div>'
        f'<h2>转化漏斗</h2></div>{_funnel_panel(data)}</section>',
        f'<section class="panel" id="panel-3"><div class="panel-head"><div class="eyebrow">03 · Trend</div>'
        f'<h2>每日趋势</h2></div>{_trend_panel(data)}</section>',
        f'<section class="panel" id="panel-4"><div class="panel-head"><div class="eyebrow">04 · Segments</div>'
        f'<h2>分群诊断</h2></div>{_segments_panel(data)}</section>',
        f'<section class="panel" id="panel-5"><div class="panel-head"><div class="eyebrow">05 · Attribution</div>'
        f'<h2>洞察归因</h2></div>{_attribution_panel(data)}</section>',
        f'<section class="panel" id="panel-6"><div class="panel-head"><div class="eyebrow">06 · Actions</div>'
        f'<h2>行动建议</h2></div>{_actions_panel(data)}</section>',
        f'<section class="panel" id="panel-7"><div class="panel-head"><div class="eyebrow">07 · Quality</div>'
        f'<h2>数据质量</h2></div>{_quality_panel(data)}</section>',
    ])

    observations = "".join(f"<li>{_safe(item)}</li>" for item in data["observations"])
    limits = "".join(f"<li>{_safe(item)}</li>" for item in data["limits"])

    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IntentFlow · {_safe(title)}</title><style>
:root {{ color-scheme:light; font:15px/1.65 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif; --bg:#f5f7fa; --card:#ffffff; --line:#dfe5ec; --text:#243044; --muted:#6a7a8e; --accent:#1e5fa5; --accent-soft:#eaf4fb; --ok:#1e8f73; --ok-soft:#e7f6f1; --warn:#b25000; --warn-soft:#fdf1e7; --bad:#a04e45; }}
* {{ box-sizing:border-box }} html {{ scroll-behavior:smooth }} body {{ margin:0; color:var(--text); background:var(--bg) }}
code {{ font:12.5px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace; background:#eef2f7; border:1px solid var(--line); border-radius:5px; padding:1px 6px }}
button {{ font:inherit; border:1px solid #b8c3d1; border-radius:8px; background:white; color:var(--text); padding:.4rem .8rem; cursor:pointer }}
button:hover {{ background:var(--accent-soft) }}
.layout {{ display:flex; align-items:flex-start; gap:1rem; max-width:1560px; margin:0 auto; padding:0 1rem 3rem }}
aside {{ flex:0 0 200px; position:sticky; top:1rem; background:var(--card); border:1px solid var(--line); border-radius:14px; padding:.9rem .6rem }}
.brand {{ display:flex; gap:9px; align-items:center; padding:.2rem .55rem .9rem; font-weight:700 }} .brand-mark {{ background:var(--accent); color:#fff; border-radius:8px; padding:4px 8px; font-size:18px }} .brand small {{ display:block; color:var(--muted); font-size:10.5px; font-weight:500; letter-spacing:.06em }}
nav {{ display:grid; gap:3px }} nav a {{ display:flex; align-items:center; gap:8px; color:var(--muted); text-decoration:none; padding:8px 10px; border-radius:8px }} nav a:hover,nav a.active {{ color:var(--accent); background:var(--accent-soft) }} .nav-num {{ font:600 11px/1 ui-monospace,monospace; color:var(--muted); min-width:18px }}
main {{ flex:1 1 auto; min-width:0 }}
.topbar {{ position:sticky; top:0; z-index:5; display:flex; align-items:center; justify-content:space-between; gap:1rem; background:rgba(245,247,250,.92); backdrop-filter:blur(6px); border-bottom:1px solid var(--line); padding:.7rem 1rem; margin:0 -1rem 1rem }}
.topbar .crumb {{ color:var(--muted); font-size:13px }} .topbar .crumb b {{ color:var(--text) }}
.topbar .tools {{ display:flex; gap:.5rem }}
.badge {{ display:inline-flex; align-items:center; gap:6px; border:1px solid #e2c47c; background:#fbf4e2; color:#8f6713; border-radius:999px; padding:3px 11px; font-size:12.5px; font-weight:600 }}
.panel {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:1.6rem; margin-bottom:1.2rem; scroll-margin-top:4.5rem }}
.panel-head h2 {{ margin:.2rem 0 .2rem; font-size:22px }} .eyebrow {{ color:var(--accent); font:600 11px/1 ui-monospace,monospace; letter-spacing:.1em; text-transform:uppercase }}
.muted {{ color:var(--muted) }} .muted code {{ color:#51647a }}
.notice {{ margin:.4rem 0 1rem; padding:12px 15px; border:1px solid #e2c47c; background:var(--warn-soft); color:#7a5213; border-radius:10px; font-size:14px }} .notice b {{ color:var(--warn) }}
.panel-notice {{ margin:.3rem 0 1rem; padding:12px 15px; border:1px solid var(--line); background:#f6f8fb; color:var(--muted); border-radius:10px; font-size:14px }} .panel-notice.ok {{ border-color:#b7e0d4; background:var(--ok-soft); color:#146b54 }}
.stat-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:.8rem 0 }}
.stat-card {{ border:1px solid var(--line); border-radius:12px; padding:14px 16px }} .stat-card span {{ color:var(--muted); font-size:13px }} .stat-card strong {{ display:block; font-size:26px; margin:2px 0 }} .stat-card small {{ color:var(--muted) }}
.contract-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin:.6rem 0 }} .contract-grid div {{ border:1px solid var(--line); border-radius:12px; padding:12px 15px }} .contract-grid span {{ display:block; color:var(--muted); font-size:12.5px }} .contract-grid b {{ font-weight:600; overflow-wrap:anywhere }}
.conclusion {{ margin-top:.6rem; border-left:3px solid var(--accent); background:var(--accent-soft); border-radius:0 12px 12px 0; padding:13px 16px }} .conclusion span {{ color:var(--accent); font-size:12.5px; font-weight:700 }} .conclusion p {{ margin:.3rem 0 0 }}
.seg-toggle {{ display:inline-flex; gap:4px; background:#eef2f7; border-radius:9px; padding:3px }} .seg-toggle button {{ border:0; background:transparent; border-radius:7px; padding:.35rem .8rem }} .seg-toggle button.active {{ background:white; box-shadow:0 1px 3px rgba(20,40,70,.12); font-weight:600 }}
.funnel {{ display:flex; align-items:flex-end; gap:14px; margin:1.2rem 0 .4rem; min-height:200px }}
.funnel-stage {{ flex:1; display:flex; flex-direction:column; gap:6px }} .funnel-stage-head {{ display:flex; flex-direction:column; gap:2px }} .funnel-stage-head code {{ align-self:flex-start }} .funnel-label {{ font-weight:600; font-size:14px }} .funnel-event {{ color:var(--muted); font-size:11.5px; overflow-wrap:anywhere }}
.funnel-bar {{ display:flex; flex-direction:column; align-items:center; justify-content:flex-end; gap:4px; background:repeating-linear-gradient(45deg,#f2f5f9,#f2f5f9 8px,#eceff4 8px,#eceff4 16px); border:1px dashed #c6d0dd; border-radius:10px; min-height:150px; padding:12px 8px }} .funnel-count {{ font-weight:700; color:#98a3b3 }} .funnel-bar small {{ color:#98a3b3 }}
.trend-placeholder {{ position:relative; height:220px; border:1px solid var(--line); border-radius:12px; background:linear-gradient(#fff,#f7f9fc); overflow:hidden; margin:.8rem 0 }} .trend-axes {{ position:absolute; inset:18px 22px 26px 48px; border-left:1px solid var(--line); border-bottom:1px solid var(--line); background:repeating-linear-gradient(0deg,transparent,transparent 31px,#eef2f7 31px,#eef2f7 32px) }} .trend-empty {{ position:absolute; inset:0; display:grid; place-items:center; color:var(--muted) }}
.chips {{ display:flex; flex-wrap:wrap; gap:8px }} .chip {{ border:1px solid #c9d4e0; border-radius:999px; padding:4px 11px; color:#51647a; font-size:13px }}
.cluster-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:10px; margin:.5rem 0 }} .segment-list {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:10px; margin:.5rem 0 }} .segment-dim {{ border:1px solid var(--line); border-radius:12px; padding:12px 14px }} .segment-dim h4 {{ margin:.4rem 0 .2rem }} .segment-dim p {{ margin:0; color:var(--muted); font-size:13px }} .segment-dim b {{ color:var(--text) }}
.pill {{ border:1px solid #c9d4e0; border-radius:999px; padding:2px 9px; color:#51647a; font-size:12px; white-space:nowrap }} .pill.simulation {{ color:#8f6713; border-color:#e2c47c; background:#fbf4e2 }}
.attribution-block {{ border:1px solid var(--line); border-radius:12px; margin:.5rem 0; overflow:hidden }} .attribution-block summary {{ display:flex; align-items:center; gap:9px; padding:12px 15px; cursor:pointer; font-weight:600 }} .attribution-block summary .muted {{ font-weight:400; margin-left:auto }} .attribution-block ul {{ margin:0; padding:.4rem 1.2rem 1rem 2.6rem; color:#3a4a5e }} .attribution-dot {{ width:9px; height:9px; border-radius:50%; background:var(--accent) }} .attribution-block[data-kind="hypothesis"] .attribution-dot {{ background:#8a6fc0 }} .attribution-block[data-kind="counter"] .attribution-dot {{ background:#d27668 }}
.action-list {{ display:grid; gap:9px; margin:.7rem 0 }} .action-item {{ display:flex; align-items:flex-start; gap:11px; border:1px solid var(--line); border-radius:12px; padding:13px 15px; cursor:pointer }} .action-item input {{ margin-top:4px }} .action-item:hover {{ border-color:#b7d4ee }} .action-body {{ display:flex; flex-direction:column; gap:3px }} .action-detail {{ color:var(--muted); font-size:13.5px }} .action-item .pill {{ margin-left:auto; align-self:center }}
.quality-toolbar {{ display:flex; align-items:center; gap:10px; margin:.5rem 0 }} .quality-callout {{ border:1px solid #e2c47c; background:var(--warn-soft); border-radius:10px; padding:11px 15px; margin:.5rem 0 }} .quality-callout h4 {{ margin:0 0 .2rem; color:var(--warn) }} .quality-callout p {{ margin:0; color:#7a5213 }}
.table-wrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:10px }} table {{ width:100%; border-collapse:collapse; font-size:13.5px }} th,td {{ border-bottom:1px solid var(--line); padding:.55rem .7rem; text-align:left; vertical-align:top }} th {{ background:#f3f6fa; font-weight:600 }} tr:last-child td {{ border-bottom:0 }} td.ok {{ color:var(--ok); font-weight:600 }} td.warn {{ color:var(--warn); font-weight:600 }}
.markdown-block {{ white-space:pre-wrap; background:#f6f8fb; border:1px solid var(--line); border-radius:12px; padding:1rem; color:#3a4a5e; font:13px/1.7 ui-monospace,monospace; margin-top:.6rem }}
details.source {{ border:1px solid var(--line); border-radius:14px; padding:0 1.6rem 1.6rem; margin-top:1rem; background:var(--card) }}
details.source summary {{ padding:1rem 0; cursor:pointer; font-weight:700; color:var(--accent) }}
.hidden {{ display:none !important }}
@media(max-width:900px) {{ .layout {{ flex-direction:column }} aside {{ position:static; width:100%; display:flex; align-items:center; gap:4px; overflow-x:auto }} nav {{ display:flex }} nav a {{ white-space:nowrap }} .brand {{ display:none }} .funnel {{ flex-direction:column; align-items:stretch }} .funnel-bar {{ min-height:60px; flex-direction:row; justify-content:space-between }} }}
</style></head><body>
<header class="topbar"><div class="crumb">IntentFlow · 数据分析 / <b>{_safe(title)}</b></div><div class="tools"><span class="badge">演示 · 不可计算</span><button id="copy-conclusion" type="button">复制结论</button><button id="toggle-source" type="button">查看正式记录</button></div></header>
<div class="layout"><aside><div class="brand"><span class="brand-mark">↗</span><div>IntentFlow<small>PRODUCT ANALYTICS</small></div></div><nav>{nav}</nav></aside><main>
{panels}
<details class="source" id="source-block"><summary>正式记录原文（analytics/report.md）</summary><pre class="markdown-block">{_safe(report_md)}</pre></details>
</main></div>
<script>
const DATA = {json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace("</", "<\\/")};
const navLinks=[...document.querySelectorAll('nav a[data-nav]')];
const panels=[...document.querySelectorAll('.panel')];
const navObserver=new IntersectionObserver(entries=>{{const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>b.intersectionRatio-a.intersectionRatio)[0];if(!visible)return;navLinks.forEach(l=>l.classList.toggle('active',l.dataset.nav===visible.target.id));}},{{rootMargin:'-10% 0px -72% 0px',threshold:[0,.2,.6]}});
panels.forEach(p=>navObserver.observe(p));
document.querySelectorAll('[data-funnel-base]').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('[data-funnel-base]').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById('funnel-base-note').textContent=b.dataset.funnelBase==='first'?'口径：相对首个指标计算转化率。':'口径：相对上一指标计算转化率。';}}));
document.querySelectorAll('[data-quality]').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('[data-quality]').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.querySelectorAll('#panel-7 tbody tr').forEach(tr=>{{tr.classList.toggle('hidden',b.dataset.quality==='no'&&tr.dataset.computable==='yes');}});}}));
const actionInputs=[...document.querySelectorAll('input[data-action]')];
actionInputs.forEach(i=>i.addEventListener('change',()=>{{const n=actionInputs.filter(x=>x.checked).length;document.getElementById('action-count').textContent='已勾选 '+n+' / '+actionInputs.length+' 条（仅本页标记，未写回正式记录）。';}}));
document.getElementById('toggle-source').addEventListener('click',()=>{{const b=document.getElementById('source-block');b.open=!b.open;}});
document.getElementById('copy-conclusion').addEventListener('click',async()=>{{const parts=['# 数据分析结论摘要','',DATA.title?('- 标题：'+DATA.title):'','- 结论：'+(DATA.conclusion||'尚未形成结论。'),'- 材料状态：演示/不可计算','','## 行动建议（助手建议，待确认）',...DATA.actions.map((a,i)=>(i+1)+'. '+a.replace(/\\*\\*/g,'')),'','## 数据缺口','- '+String(DATA.contract['缺失字段']||'—')];const text=parts.join('\\n');try{{await navigator.clipboard.writeText(text);document.getElementById('copy-conclusion').textContent='已复制';setTimeout(()=>document.getElementById('copy-conclusion').textContent='复制结论',1500);}}catch(e){{window.prompt('复制以下结论',text);}}}});
</script></body></html>"""

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8", newline="\n")
    return output
