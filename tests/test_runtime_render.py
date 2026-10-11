from pathlib import Path

from scripts.intentflow_runtime.core import sha256_text
from scripts.intentflow_runtime.render import render_review


def test_review_uses_formal_markdown_and_escapes_content(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    source.parent.mkdir(parents=True)
    markdown = "# Example\n\n<script>alert('bad')</script>\n"
    source.write_bytes(markdown.encode("utf-8"))

    html = render_review(source, "prd")

    assert 'data-source="prd/PRD.md"' in html
    assert f'data-revision="{sha256_text(markdown)}"' in html
    assert "&lt;script&gt;alert" in html
    assert "<script>alert('bad')</script>" not in html
    assert "id=\"markdown-editor\"" in html


def test_prototype_panel_is_lazy_and_has_no_initial_iframe_src(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    prototype = req / "design" / "prototype.html"
    source.parent.mkdir(parents=True)
    prototype.parent.mkdir(parents=True)
    source.write_bytes(b"# Example\n")
    prototype.write_text("<h1>Prototype</h1>", encoding="utf-8")

    html = render_review(source, "prd", prototype)

    assert 'data-preview="../design/prototype.html"' in html
    assert 'id="prototype-frame"' in html
    assert 'id="prototype-frame" src=' not in html


def test_prd_review_has_traceable_dual_pane_and_state_sync(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    prototype = req / "design" / "prototype.html"
    state_map = req / "design" / "state-map.md"
    source.parent.mkdir(parents=True)
    prototype.parent.mkdir(parents=True)
    source.write_text(
        "# Example\n\n## 功能详细说明\n\n### F-01 订正\n\n- 功能流程：进入 → 提交\n- 原型图：P01\n\n| 功能 ID | 功能名称 | 功能流程 | 原型图/状态 | 功能描述 |\n| --- | --- | --- | --- | --- |\n| F-01 | 订正 | 进入 → 提交 | P01 | 完成订正 |\n",
        encoding="utf-8",
    )
    prototype.write_text("<h1 id='P01'>P01</h1>", encoding="utf-8")
    state_map.write_text(
        "| State ID | PRD behavior ID | Entry/trigger | Visible state | Available action | Next state | Asset link | Data status |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| P01 | F-01、F-02 | 进入 | 订正页 | 提交 | P02 | #P01 | 模拟 |\n",
        encoding="utf-8",
    )

    html = render_review(source, "prd", prototype)

    assert 'id="prototype-state-select"' in html
    assert 'data-state-map' in html
    assert 'data-prd-id="F-01"' in html
    assert 'data-prototype-state="P01"' in html
    assert "IntersectionObserver" in html


def test_prd_review_embeds_business_and_interaction_flows_when_present(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    flows = req / "flows"
    source.parent.mkdir(parents=True)
    flows.mkdir(parents=True)
    source.write_text("# Example\n", encoding="utf-8")
    (flows / "business-flow.html").write_text("<h1>Business</h1>", encoding="utf-8")
    (flows / "interaction-flow.html").write_text("<h1>Interaction</h1>", encoding="utf-8")

    html = render_review(source, "prd")

    assert 'class="flow-embed"' in html
    assert '../flows/business-flow.html' in html
    assert '../flows/interaction-flow.html' in html


def test_prd_review_has_section_navigation_for_headings(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Example\n\n## 背景\n\n### 功能详细说明\n\n内容\n", encoding="utf-8")

    html = render_review(source, "prd")

    assert 'id="toc"' in html
    assert 'class="toc-link ' in html
    assert 'href="#背景"' in html
    assert 'data-toc-target="背景"' in html
    assert 'href="#功能详细说明"' not in html


def test_prd_detail_table_expands_operable_prototype_markers(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    prototype = req / "design" / "prototype.html"
    source.parent.mkdir(parents=True)
    prototype.parent.mkdir(parents=True)
    source.write_text(
        "# Example\n\n## 功能详细说明\n\n### F-01 订正\n\n| 序号与功能名称 | 原型图/状态 | 详细说明 |\n| --- | --- | --- |\n| 1. 订正 | [[prototype:P01]] | 页面元素：按钮 |\n",
        encoding="utf-8",
    )
    prototype.write_text("<section id='P01'>P01</section>", encoding="utf-8")

    html = render_review(source, "prd", prototype)

    assert 'class="prd-inline-prototype"' in html
    assert 'src="../design/prototype.html#P01"' in html
    assert 'P01 · 可操作原型' in html
    assert '&lt;br&gt;' not in html


def test_acceptance_review_has_optional_build_and_status_export(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "qa" / "checklist.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "| ID | Status |\n| --- | --- |\n| AC-01 | 未测 |\n", encoding="utf-8"
    )

    html = render_review(source, "acceptance")

    assert 'id="acceptance-controls"' in html
    assert 'id="review-build"' in html
    assert 'id="review-environment"' not in html
    assert 'id="review-evidence"' not in html
    assert 'id="export-status"' in html
