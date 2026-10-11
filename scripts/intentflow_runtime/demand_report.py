"""Generate an optional, case-agnostic demand-insight dashboard.

Markdown remains the formal record. This module only creates a derived HTML
view, so rendering never edits the findings or evidence files.
"""

from __future__ import annotations

import csv
import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_FEEDBACK = {"id", "cluster", "scenario", "obstacle", "impact", "desired"}
PRODUCT_FIELDS = {"name", "official_url", "observed_capability", "unverified", "source_id"}
SECTION_NAMES = [
    "洞察总览", "场景与材料", "反馈与聚类", "问题与归因",
    "公开产品参考", "首版需求收口", "验证与指标", "待确认结论",
]


def _read_rows(path: Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not REQUIRED_FEEDBACK <= set(rows[0]):
        raise ValueError("demand feedback needs id, cluster, scenario, obstacle, impact and desired columns")
    for row in rows:
        row.setdefault("evidence_type", "simulation")
        row.setdefault("source_id", "")
        row.setdefault("voice", "")
        if row["evidence_type"] not in {"real", "simulation"}:
            raise ValueError("evidence_type must be real or simulation")
        if row["evidence_type"] == "real" and not row["source_id"]:
            raise ValueError(f"real feedback {row.get('id', '')} requires source_id")
    return rows


def _read_products(path: Path | None) -> list[dict[str, str]]:
    if path is None or not Path(path).is_file():
        return []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in csv.DictReader(stream)]
    if rows and not PRODUCT_FIELDS <= set(rows[0]):
        missing = "、".join(sorted(PRODUCT_FIELDS - set(rows[0])))
        raise ValueError(f"product references need {missing} columns")
    for row in rows:
        parsed = urlparse(row.get("official_url", ""))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("product official_url must be an http or https URL")
    return rows


def _formal_sections(findings: str) -> tuple[str, dict[str, str]]:
    title_match = re.search(r"^#\s+(.+?)\s*$", findings, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "需求洞察"
    found: dict[str, str] = {}
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", findings, re.MULTILINE))
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(findings)
        found[heading] = findings[match.end():end].strip()
    return title, found


def _safe(value: str) -> str:
    return html.escape(value or "", quote=True)


def _feedback_cards(rows: list[dict[str, str]]) -> str:
    cards = []
    for row in rows:
        kind = row["evidence_type"]
        label = "真实反馈" if kind == "real" else "模拟反馈"
        voice = f'<blockquote>{_safe(row["voice"])}</blockquote>' if row.get("voice") else ""
        cards.append(
            f'<article class="feedback-card" data-kind="{_safe(kind)}" data-cluster="{_safe(row["cluster"])}">'
            f'<div class="card-top"><span class="pill {kind}">{label}</span><code>{_safe(row["id"])}</code></div>'
            f'<h3>{_safe(row["cluster"])}</h3>'
            f'<p><b>场景</b>{_safe(row["scenario"])}</p><p><b>困难</b>{_safe(row["obstacle"])}</p>'
            f'<p><b>影响</b>{_safe(row["impact"])}</p><p><b>期望</b>{_safe(row["desired"])}</p>{voice}</article>'
        )
    return "".join(cards)


def _product_cards(products: list[dict[str, str]]) -> str:
    if not products:
        return '<div class="empty">尚未提供公开产品参考。请把可核验页面及查阅日期登记到 products.csv 与 source.md。</div>'
    return "".join(
        f'<article class="product-card"><div class="card-top"><span class="pill public">公开页面</span>'
        f'<a href="{_safe(row["official_url"])}" target="_blank" rel="noreferrer">打开来源 ↗</a></div>'
        f'<h3>{_safe(row["name"])}</h3><p>{_safe(row["observed_capability"])}</p>'
        f'<p class="unverified"><b>尚未核实：</b>{_safe(row["unverified"])}</p>'
        f'<small>来源 ID：{_safe(row["source_id"]) or "待补"}</small></article>' for row in products
    )


def build_insight_html(
    csv_path: Path,
    findings_path: Path,
    output: Path,
    *,
    products_path: Path | None = None,
) -> Path:
    rows = _read_rows(csv_path)
    findings = Path(findings_path).read_text(encoding="utf-8")
    products = _read_products(products_path)
    title, sections = _formal_sections(findings)
    clusters = Counter(row["cluster"] for row in rows)
    real_count = sum(row["evidence_type"] == "real" for row in rows)
    simulation_count = len(rows) - real_count
    cluster_cards = "".join(
        f'<article class="stat-card"><span>{_safe(cluster)}</span><strong>{count}</strong><small>条反馈</small></article>'
        for cluster, count in clusters.most_common()
    )
    nav = "".join(f'<a href="#section-{i}">0{i} <span>{_safe(name)}</span></a>' for i, name in enumerate(SECTION_NAMES, 1))
    formal_sections = "".join(
        f'<section id="section-{i}" class="report-section"><div class="eyebrow">0{i}</div><h2>{_safe(name)}</h2>'
        f'<div class="markdown-block">{_safe(sections.get(name, "尚未填写。"))}</div></section>'
        for i, name in enumerate(SECTION_NAMES, 1)
        if i not in {1, 3, 5}
    )
    # Keep JSON valid inside the script element; HTML entities such as &quot;
    # are not decoded in JavaScript raw-text elements.
    feedback_json = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c").replace("</", "<\\/")
    page = f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IntentFlow · {_safe(title)}</title><style>
:root {{ color-scheme:dark; font:14px/1.65 Inter,system-ui,"Microsoft YaHei",sans-serif; --bg:#0b111d; --panel:#121b2b; --line:#2b3b56; --text:#eef5ff; --muted:#9caeca; --mint:#65e6bd; }}
* {{ box-sizing:border-box }} html {{ scroll-behavior:smooth }} body {{ margin:0; color:var(--text); background:radial-gradient(circle at 80% -20%,#1e3850 0,transparent 45%),var(--bg); }}
.layout {{ display:flex; min-height:100vh }} aside {{ position:fixed; width:240px; top:0; bottom:0; padding:28px 18px; border-right:1px solid #203149; background:#0d1523; }}
.brand {{ display:flex; gap:10px; align-items:center; margin-bottom:34px; font-weight:700; letter-spacing:.08em }} .brand-mark {{ background:var(--mint); color:#09211c; border-radius:9px; padding:5px 8px; font-size:20px }} .brand small {{ display:block; color:var(--muted); font-size:10px; letter-spacing:.18em }}
nav {{ display:grid; gap:5px }} nav a {{ color:var(--muted); text-decoration:none; padding:10px 11px; border-radius:9px }} nav a:hover,nav a:first-child {{ color:var(--text); background:#18372f }} nav a span {{ margin-left:8px }}
main {{ width:min(1320px,calc(100% - 240px)); margin-left:240px; padding:30px 48px 80px }} .topline,.toolbar,.stage,.hero,.cards,.feedback-grid,.product-grid {{ display:flex; gap:14px }} .topline,.toolbar {{ justify-content:space-between; align-items:center }} .topline {{ color:var(--muted); font-size:13px }}
button,.button {{ border:1px solid var(--line); background:#162337; color:var(--text); border-radius:9px; padding:10px 14px; cursor:pointer }} button.primary {{ border-color:#55d3af; background:var(--mint); color:#06231d; font-weight:700 }}
.stage {{ align-items:center; margin:22px 0 30px; max-width:720px }} .stage .step {{ color:var(--muted); display:flex; align-items:center; gap:8px; white-space:nowrap }} .stage .step.active {{ color:var(--mint); font-weight:700 }} .step i {{ display:grid; place-items:center; width:26px; height:26px; border:1px solid var(--line); border-radius:50%; font-style:normal }} .step.active i {{ background:var(--mint); color:#09211c; border:0 }} .connector {{ height:1px; background:var(--line); flex:1 }}
.hero {{ padding:31px; border:1px solid #273850; border-radius:20px; background:linear-gradient(120deg,#172536,#111a28); justify-content:space-between; align-items:end }} h1 {{ margin:4px 0 8px; font-size:42px; line-height:1.18 }} h2 {{ font-size:25px; margin:0 0 18px }} h3 {{ margin:8px 0; }} .eyebrow {{ color:var(--mint); letter-spacing:.18em; font-size:11px; text-transform:uppercase }} .muted,small {{ color:var(--muted) }} .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px }} .chip,.pill {{ border:1px solid #38516c; border-radius:999px; padding:4px 9px; color:#b9cbea; font-size:12px }}
.record-panel {{ width:min(390px,40%); border:1px solid #32425a; border-radius:15px; padding:18px }} .record-row {{ padding:9px 0; border-bottom:1px solid #27374f }} .record-row:last-child {{ border:0 }} .record-row b {{ display:block }}
.notice {{ margin:17px 0; padding:14px 18px; border:1px solid #695333; background:#2b2417; color:#f5d99b; border-radius:12px }} .notice.ok {{ border-color:#286652; background:#102b27; color:#a4f4db }}
.section-head {{ display:flex; justify-content:space-between; align-items:end; margin:40px 0 16px }} .cards {{ flex-wrap:wrap }} .stat-card,.feedback-card,.product-card,.empty {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:17px }} .stat-card {{ flex:1; min-width:160px }} .stat-card strong {{ display:block; color:#8de4ca; font-size:32px }} .stat-card small {{ display:block }}
.feedback-grid,.product-grid {{ flex-wrap:wrap }} .feedback-card {{ flex:1 1 280px; min-width:270px }} .product-card {{ flex:1 1 300px; min-width:280px }} .card-top {{ display:flex; justify-content:space-between; align-items:center; gap:8px }} .pill.real {{ color:#9debcf; border-color:#2c836c }} .pill.simulation {{ color:#f4d08d; border-color:#7d6130 }} .pill.public {{ color:#a9c8ff }} code {{ color:var(--muted) }} .feedback-card p,.product-card p {{ margin:7px 0; color:#c9d4e8 }} .feedback-card b {{ color:#7e91af; margin-right:7px }} blockquote {{ margin:14px 0 0; padding:10px 12px; border-left:3px solid #5ddbb8; color:#e3efff; background:#172638 }}
.filters {{ display:flex; flex-wrap:wrap; gap:8px; margin-bottom:15px }} .filters button.active {{ border-color:var(--mint); color:var(--mint) }} .report-section {{ scroll-margin-top:25px; margin-top:55px }} .markdown-block {{ white-space:pre-wrap; background:#111a2a; border:1px solid var(--line); border-radius:12px; padding:18px; color:#cdd8ec }} .unverified {{ color:#f4d08d !important }} .empty {{ color:var(--muted); width:100% }} .hidden {{ display:none !important }}
@media(max-width:850px) {{ aside {{ position:static; width:100%; height:auto; border-right:0; border-bottom:1px solid #203149 }} .layout {{ display:block }} main {{ width:100%; margin:0; padding:24px 18px 60px }} nav {{ display:flex; overflow:auto }} nav a {{ white-space:nowrap }} .hero {{ display:block }} .record-panel {{ width:100%; margin-top:20px }} h1 {{ font-size:32px }} .stage {{ overflow:auto }} }}
</style></head><body><div class="layout"><aside><div class="brand"><span class="brand-mark">↗</span><div>IntentFlow<small>REQUIREMENT DISCOVERY</small></div></div><div class="muted" style="margin-bottom:10px">本期需求 / 01</div><nav>{nav}</nav></aside><main>
<div class="topline"><span>需求挖掘 / {_safe(title)}</span><div class="toolbar"><button id="toggle-demo">隐藏模拟反馈</button><button id="export">导出反馈 CSV</button><button class="primary" id="copy">复制需求结论</button></div></div>
<div class="stage"><div class="step active"><i>1</i>需求挖掘</div><div class="connector"></div><div class="step"><i>2</i>需求产出</div><div class="connector"></div><div class="step"><i>3</i>功能验收</div><div class="connector"></div><div class="step"><i>4</i>数据分析</div></div>
<section id="section-1" class="hero"><div><div class="eyebrow">Learning Experience / Discovery</div><h1>{_safe(title)}</h1><p class="muted">由逐条反馈、公开资料和问题归因组成可评审的需求洞察。</p><div class="chips"><span class="chip">正式记录：Markdown</span><span class="chip">演示视图：HTML</span><span class="chip">证据与推断分开</span></div></div><div class="record-panel"><div class="muted">需求分开记录的三件事</div><div class="record-row"><b>观察当前行为</b><span class="muted">记录发生了什么</span></div><div class="record-row"><b>描述遇到的困难</b><span class="muted">保留原话与来源</span></div><div class="record-row"><b>验证结果是否改善</b><span class="muted">定义可计算指标</span></div></div></section>
<div class="notice {'ok' if real_count else ''}"><b>材料状态：</b>{'模拟演示数据，不是用户证据。' if simulation_count else '本页含真实反馈，仍需结合来源范围审阅。'} 本页共有 {len(rows)} 条反馈，其中 <strong>真实反馈 {real_count}</strong> 条、<strong>模拟反馈 {simulation_count}</strong> 条。模拟材料只用于检验整理、聚类和展示，不代表真实频率或市场规模。</div>
<div class="section-head"><div><div class="eyebrow">Overview</div><h2>洞察总览</h2></div><small>公开产品参考 {len(products)} 个</small></div><div class="cards"><article class="stat-card"><span>反馈总数</span><strong>{len(rows)}</strong><small>真实与模拟分开标记</small></article><article class="stat-card"><span>真实反馈</span><strong>{real_count}</strong><small>需有 source_id</small></article><article class="stat-card"><span>模拟反馈</span><strong>{simulation_count}</strong><small>仅供演示验证</small></article><article class="stat-card"><span>问题聚类</span><strong>{len(clusters)}</strong><small>来自 feedback.csv</small></article><article class="stat-card"><span>公开机制参考</span><strong>{len(products)}</strong><small>不等于效果证明</small></article></div><div class="cards" style="margin-top:14px">{cluster_cards}</div><div class="markdown-block">{_safe(sections.get("洞察总览", "尚未填写。"))}</div>
<section class="report-section" id="section-3"><div class="section-head"><div><div class="eyebrow">Evidence</div><h2>反馈与聚类</h2></div><div class="filters"><button class="active" data-filter="all">全部</button><button data-filter="real">真实</button><button data-filter="simulation">模拟</button></div></div><div class="feedback-grid">{_feedback_cards(rows)}</div><div class="markdown-block" style="margin-top:14px">{_safe(sections.get("反馈与聚类", "尚未填写。"))}</div></section>
<section class="report-section" id="section-5"><div class="section-head"><div><div class="eyebrow">Public reference</div><h2>公开产品参考</h2></div></div><div class="product-grid">{_product_cards(products)}</div><div class="markdown-block" style="margin-top:14px">{_safe(sections.get("公开产品参考", "尚未填写。"))}</div></section>
{formal_sections}
<details class="report-section"><summary>查看完整正式 Markdown 原文</summary><pre class="markdown-block">{_safe(findings)}</pre></details>
<script>
const rawRows={feedback_json}; const cards=[...document.querySelectorAll('.feedback-card')]; let hideDemo=false; let filter='all';
function refresh(){{cards.forEach(c=>{{const showKind=filter==='all'||c.dataset.kind===filter; const showDemo=!hideDemo||c.dataset.kind!=='simulation'; c.classList.toggle('hidden',!(showKind&&showDemo));}})}}
document.querySelectorAll('[data-filter]').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('[data-filter]').forEach(x=>x.classList.remove('active'));b.classList.add('active');filter=b.dataset.filter;refresh();}}));
document.getElementById('toggle-demo').addEventListener('click',e=>{{hideDemo=!hideDemo;e.target.textContent=hideDemo?'显示模拟反馈':'隐藏模拟反馈';refresh();}});
document.getElementById('export').addEventListener('click',()=>{{const keys=Object.keys(rawRows[0]||{{}});const csv=[keys.join(','),...rawRows.map(r=>keys.map(k=>JSON.stringify(r[k]||'')).join(','))].join('\\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{{type:'text/csv;charset=utf-8'}}));a.download='feedback-export.csv';a.click();}});
document.getElementById('copy').addEventListener('click',async()=>{{const text=[...document.querySelectorAll('.report-section .markdown-block')].map(x=>x.innerText).join('\\n\\n');try{{await navigator.clipboard.writeText(text);document.getElementById('copy').textContent='已复制';setTimeout(()=>document.getElementById('copy').textContent='复制需求结论',1500);}}catch(e){{window.prompt('复制以下结论',text);}}}});
</script></main></div></body></html>"""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8", newline="\n")
    return output
