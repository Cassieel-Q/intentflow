"""Render an optional local review page from formal Markdown."""

from __future__ import annotations

import html as html_lib
import json
import os
import re
from pathlib import Path

from .core import InvalidTarget, sha256_text


KINDS = {"prd": "需求文档", "acceptance": "验收清单", "analytics": "数据报告"}
FORMAL_SOURCES = {"prd": "prd/PRD.md", "acceptance": "qa/checklist.md", "analytics": "analytics/report.md"}


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _read_state_map(requirement_root: Path) -> dict[str, object]:
    """Read the lightweight state map used to link PRD features and prototypes."""
    path = requirement_root / "design" / "state-map.md"
    if not path.is_file():
        return {"states": [], "by_prd": {}, "by_state": {}}
    lines = path.read_text(encoding="utf-8").splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if "State ID" in line and "PRD behavior ID" in line),
        None,
    )
    if header_index is None:
        return {"states": [], "by_prd": {}, "by_state": {}}
    headers = _table_cells(lines[header_index])
    rows: list[dict[str, str]] = []
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            if rows:
                break
            continue
        cells = _table_cells(line)
        if len(cells) < len(headers):
            continue
        row = dict(zip(headers, cells))
        state_id = row.get("State ID", "").strip()
        if not re.fullmatch(r"P[A-Za-z0-9_-]+", state_id):
            continue
        rows.append(row)
    by_prd: dict[str, list[str]] = {}
    by_state: dict[str, dict[str, str]] = {}
    for row in rows:
        state_id = row["State ID"]
        prd_id = row.get("PRD behavior ID", "").strip()
        by_state[state_id] = row
        if prd_id:
            for behavior_id in re.split(r"[,、/\s]+", prd_id):
                if behavior_id:
                    by_prd.setdefault(behavior_id, []).append(state_id)
    return {"states": rows, "by_prd": by_prd, "by_state": by_state}


def _heading_slug(text: str, seen: dict[str, int]) -> str:
    plain = re.sub(r"<[^>]+>", "", text).strip().lower()
    plain = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", plain).strip("-") or "section"
    count = seen.get(plain, 0) + 1
    seen[plain] = count
    return plain if count == 1 else f"{plain}-{count}"


def _decorate_prd_body(body: str, state_map: dict[str, object]) -> tuple[str, list[dict[str, object]]]:
    by_prd = state_map.get("by_prd", {})
    if not isinstance(by_prd, dict):
        return body, []
    headings: list[dict[str, object]] = []
    seen_slugs: dict[str, int] = {}

    def heading(match: re.Match[str]) -> str:
        tag, attrs, text = match.groups()
        attrs = attrs or ""
        heading_id = _heading_slug(text, seen_slugs)
        behavior = re.search(r"\b(F-[A-Za-z0-9_-]+)\b", text)
        extra = f' id="{html_lib.escape(heading_id, quote=True)}"'
        if not behavior:
            headings.append({"id": heading_id, "level": int(tag[1]), "text": re.sub(r"<[^>]+>", "", text).strip()})
            return f"<{tag}{attrs}{extra}>{text}</{tag}>"
        prd_id = behavior.group(1)
        states = by_prd.get(prd_id, [])
        state = states[0] if states else ""
        extra += f' data-prd-id="{html_lib.escape(prd_id, quote=True)}"'
        if state:
            extra += f' data-prototype-state="{html_lib.escape(state, quote=True)}"'
        headings.append({"id": heading_id, "level": int(tag[1]), "text": re.sub(r"<[^>]+>", "", text).strip(), "prd_id": prd_id})
        return f"<{tag}{attrs}{extra}>{text}</{tag}>"

    body = re.sub(r"<(h[2-4])(\s[^>]*)?>(.*?)</\1>", heading, body, flags=re.S)

    def table_row(match: re.Match[str]) -> str:
        row = match.group(0)
        behavior = re.search(r"<td>\s*(F-[A-Za-z0-9_-]+)\s*</td>", row)
        if not behavior:
            return row
        prd_id = behavior.group(1)
        states = by_prd.get(prd_id, [])
        attrs = f' data-prd-id="{html_lib.escape(prd_id, quote=True)}"'
        if states:
            attrs += f' data-prototype-state="{html_lib.escape(states[0], quote=True)}"'
        return row.replace("<tr>", f"<tr{attrs}>", 1)

    return re.sub(r"<tr>.*?</tr>", table_row, body, flags=re.S), headings


def _render_toc(headings: list[dict[str, object]]) -> str:
    links: list[str] = []
    for heading in headings:
        level = int(heading["level"])
        # Keep the navigation at the document's primary section level. Feature
        # and detail headings remain addressable in the body but do not flood
        # the sidebar with every subheading.
        if level != 2:
            continue
        heading_id = html_lib.escape(str(heading["id"]), quote=True)
        label = html_lib.escape(str(heading["text"]))
        links.append(
            f'<a class="toc-link toc-primary" href="#{heading_id}" '
            f'data-toc-target="{heading_id}">{label}</a>'
        )
    return (
        '<nav class="toc" id="toc" aria-label="文档章节"><div class="toc-title">章节导航</div>'
        + "".join(links)
        + "</nav>"
    )


def render_review(
    source: Path, kind: str, prototype: Path | None = None, *, served: bool = False
) -> str:
    if kind not in KINDS:
        raise ValueError(f"unsupported review kind: {kind}")
    source = Path(source).resolve(strict=True)
    requirement_root = source.parent.parent.resolve(strict=True)
    if source.relative_to(requirement_root).as_posix() != FORMAL_SOURCES[kind]:
        raise InvalidTarget("source does not match this formal document kind")
    try:
        from markdown_it import MarkdownIt
    except ImportError as exc:
        raise RuntimeError("Install markdown-it-py to render review pages") from exc

    markdown = source.read_bytes().decode("utf-8")
    revision = sha256_text(markdown)
    body = MarkdownIt("commonmark", {"html": False}).enable("table").render(markdown)
    # The formal Markdown keeps compact `<br>` separators inside detail-table
    # cells. Allow that harmless layout token while continuing to escape all
    # other raw HTML such as scripts.
    body = body.replace("&lt;br&gt;", "<br>").replace("&lt;br /&gt;", "<br>")
    state_map: dict[str, object] = {"states": [], "by_prd": {}, "by_state": {}}
    headings: list[dict[str, object]] = []
    if kind == "prd":
        state_map = _read_state_map(requirement_root)
        body, headings = _decorate_prd_body(body, state_map)
    else:
        body, headings = _decorate_prd_body(body, state_map)
    rel_source = source.relative_to(requirement_root).as_posix()
    preview = ""
    prototype_viewport = "520x900"
    if prototype is not None:
        prototype = Path(prototype).resolve(strict=True)
        if not prototype.is_relative_to(requirement_root) or not prototype.is_file() or prototype.suffix.lower() != ".html":
            raise InvalidTarget("prototype is outside requirement")
        preview = (
            "/" + prototype.relative_to(requirement_root).as_posix()
            if served else os.path.relpath(prototype, source.parent).replace("\\", "/")
        )
        # Keep embedded screens at the prototype's canonical canvas size so a
        # narrow table cell scales the screen as a whole instead of triggering
        # a new responsive layout that changes the original proportions.
        prototype_source = prototype.read_text(encoding="utf-8", errors="ignore")
        viewport_match = re.search(
            r'data-intentflow-viewport=["\'](\d+x\d+)["\']', prototype_source, re.IGNORECASE
        )
        if viewport_match:
            prototype_viewport = viewport_match.group(1)
    if kind == "prd":
        def inline_prototype(match: re.Match[str]) -> str:
            state_id = match.group(1)
            if not preview:
                return f'<span class="prototype-unavailable" data-prototype-state="{state_id}">{state_id} · 原型预览未加载</span>'
            state_url = f"{preview}#{state_id}"
            return (
                f'<span class="prd-inline-prototype" data-prototype-state="{state_id}" '
                f'data-state-id="{state_id}" data-prototype-viewport="{prototype_viewport}">'
                '<span class="prd-inline-prototype-viewport">'
                f'<iframe title="{state_id} 原型状态" src="{html_lib.escape(state_url, quote=True)}" '
                '></iframe></span>'
                f'<small>{state_id} · 可操作原型</small></span>'
            )

        body = re.sub(r"\[\[prototype:(P[A-Za-z0-9_-]+)\]\]", inline_prototype, body)

    here = Path(__file__).parent
    css = (here / "review.css").read_text(encoding="utf-8")
    js = (here / "review.js").read_text(encoding="utf-8")
    title = html_lib.escape(KINDS[kind])
    source_attr = html_lib.escape(rel_source, quote=True)
    revision_attr = html_lib.escape(revision, quote=True)
    preview_attr = html_lib.escape(preview, quote=True)
    state_map_attr = html_lib.escape(json.dumps(state_map, ensure_ascii=False), quote=True)
    flow_embeds = ""
    if kind == "prd":
        flow_files = (
            ("business", "业务流程图", requirement_root / "flows" / "business-flow.html"),
            ("interaction", "交互流程图", requirement_root / "flows" / "interaction-flow.html"),
        )
        sections: list[str] = []
        for flow_kind, label, flow_path in flow_files:
            if not flow_path.is_file():
                continue
            flow_url = (
                "/" + flow_path.relative_to(requirement_root).as_posix()
                if served else os.path.relpath(flow_path, source.parent).replace("\\", "/")
            )
            sections.append(
                f'<section class="flow-embed" id="flow-{flow_kind}" data-flow-kind="{flow_kind}">'
                f"<h2>{html_lib.escape(label)}</h2>"
                f'<iframe title="{html_lib.escape(label)}" src="{html_lib.escape(flow_url, quote=True)}" loading="lazy"></iframe>'
                "</section>"
            )
        flow_embeds = "".join(sections)
    escaped_markdown = html_lib.escape(markdown)
    base_tag = f'<base href="/{html_lib.escape(source.parent.name, quote=True)}/">' if served else ""
    prd_review_url = ""
    prd_review = requirement_root / "prd" / "PRD-review.html"
    if kind == "acceptance" and prd_review.is_file():
        prd_review_url = os.path.relpath(prd_review, source.parent).replace("\\", "/")
    prd_review_attr = html_lib.escape(prd_review_url, quote=True)
    acceptance_controls = ""
    if kind == "acceptance":
        acceptance_controls = """<div class="acceptance-controls" id="acceptance-controls">
<label>构建版本（选填） <input id="review-build" autocomplete="off" placeholder="可留空"></label>
<label>筛选 <select id="acceptance-filter"><option value="全部">全部</option><option value="未测">未测</option><option value="通过">通过</option><option value="失败">失败</option><option value="跳过">跳过</option></select></label>
<div class="acceptance-progress-wrap"><progress id="acceptance-progress-bar" max="0" value="0"></progress><output id="acceptance-progress" aria-live="polite">0/0 已处理</output></div>
<button id="export-status" type="button">导出状态</button></div>"""

    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>IntentFlow · {title}</title>{base_tag}<style>{css}</style></head>
<body data-kind="{kind}" data-source="{source_attr}" data-revision="{revision_attr}" data-preview="{preview_attr}" data-prd-review="{prd_review_attr}" data-state-map="{state_map_attr}">
<header class="toolbar"><div><strong>IntentFlow</strong><span>{title}</span></div><nav>
{f'<button id="open-prd" type="button" data-prd-url="{prd_review_attr}">打开 PRD</button>' if prd_review_url else ''}
<button id="edit-toggle" type="button">编辑 Markdown</button>
<button id="copy-content" type="button">复制正文</button>
<button id="preview-toggle" type="button" {'disabled' if not preview else ''}>原型预览</button>
</nav></header>
<div id="notice" role="status" aria-live="polite"></div>
{acceptance_controls}
<main class="layout">{_render_toc(headings)}<section class="document" id="document">{body}{flow_embeds}</section>
<section class="editor" id="editor-panel" hidden><label for="markdown-editor">正式 Markdown</label>
<textarea id="markdown-editor" spellcheck="false">{escaped_markdown}</textarea>
<div class="editor-actions"><button id="save-markdown" type="button">保存到正式文件</button><button id="download-markdown" type="button">下载修改稿</button></div></section>
<aside class="preview" id="preview-panel" {'hidden' if not preview else ''}><div class="preview-controls"><label for="prototype-state-select">原型状态</label><select id="prototype-state-select"><option value="">请选择状态</option></select><button id="zoom-out" type="button">－</button><output id="zoom-level">100%</output><button id="zoom-in" type="button">＋</button></div><output id="prototype-mapping" class="prototype-mapping" aria-live="polite"></output>
<iframe id="prototype-frame" title="原型预览"></iframe></aside></main>
<script>{js}</script></body></html>"""
