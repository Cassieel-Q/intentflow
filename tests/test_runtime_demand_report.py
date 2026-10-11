from pathlib import Path

import pytest

from scripts.intentflow_runtime.demand_report import build_insight_html


def test_demand_report_marks_demo_data_and_renders_cards(tmp_path: Path):
    req = tmp_path / "case"
    research = req / "research"
    research.mkdir(parents=True)
    csv_path = research / "demo.csv"
    csv_path.write_text(
        "id,cluster,scenario,obstacle,impact,desired\n"
        "D-01,规则混淆,分数题,不会通分,相似题再错,理解规则\n"
        "D-02,规则混淆,面积题,公式混用,复习低效,说出区别\n"
        "D-03,审题困难,应用题,漏读条件,列式错误,找全条件\n", encoding="utf-8"
    )
    findings = research / "findings.md"
    findings.write_text("# 需求洞察\n\n模拟演示数据，不是用户证据。", encoding="utf-8")
    output = research / "insight.html"

    build_insight_html(csv_path, findings, output)

    html = output.read_text(encoding="utf-8")
    assert "模拟演示数据，不是用户证据" in html
    assert "3" in html
    assert "规则混淆" in html
    assert "需求洞察" in html


def test_dashboard_uses_formal_markdown_and_public_product_sources(tmp_path: Path):
    req = tmp_path / "case"
    research = req / "research"
    research.mkdir(parents=True)
    feedback = research / "feedback.csv"
    feedback.write_text(
        "id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id,voice\n"
        "F-01,理解困难,课后,看不懂说明,反复失败,理解原因,real,S-01,我不知道哪里错了\n"
        "D-01,练习困难,复习,不会迁移,新题再错,独立完成,simulation,,假设学生会这样说\n",
        encoding="utf-8",
    )
    products = research / "products.csv"
    products.write_text(
        "name,official_url,observed_capability,unverified,source_id\n"
        "示例产品,https://example.org/product,公开页面展示练习,实际学习效果,S-02\n",
        encoding="utf-8",
    )
    findings = research / "demand-findings.md"
    findings.write_text(
        "# 示例需求洞察\n\n## 洞察总览\n研究范围。\n"
        "## 场景与材料\n资料边界。\n## 反馈与聚类\n分类。\n"
        "## 问题与归因\n可能机制。\n## 公开产品参考\n对照。\n"
        "## 首版需求收口\n候选方向。\n## 验证与指标\n分母待定。\n"
        "## 待确认结论\n尚未证实。\n",
        encoding="utf-8",
    )
    before = findings.read_bytes()
    output = research / "insight.html"
    build_insight_html(feedback, findings, output, products_path=products)
    page = output.read_text(encoding="utf-8")
    assert "示例需求洞察" in page
    assert "错题订正与再练" not in page
    assert 'href="https://example.org/product"' in page
    assert "真实反馈 1" in page
    assert "模拟反馈 1" in page
    assert "实际学习效果" in page
    assert "#section-8" in page
    assert "const rawRows=[{" in page
    assert "&quot;" not in page.split("const rawRows=", 1)[1].split(";", 1)[0]
    assert findings.read_bytes() == before


def test_real_feedback_requires_source_id(tmp_path: Path):
    research = tmp_path / "research"
    research.mkdir()
    feedback = research / "feedback.csv"
    feedback.write_text(
        "id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id,voice\n"
        "F-01,理解困难,课后,看不懂说明,反复失败,理解原因,real,,我不知道哪里错了\n",
        encoding="utf-8",
    )
    findings = research / "demand-findings.md"
    findings.write_text("# 需求洞察\n", encoding="utf-8")
    with pytest.raises(ValueError, match="source_id"):
        build_insight_html(feedback, findings, research / "report.html")
