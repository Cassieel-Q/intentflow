from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_prd_template_uses_product_review_structure():
    template = (ROOT / "requirements/common/prd-template.md").read_text(encoding="utf-8")
    required_headings = (
        "文档概述",
        "需求背景和目标",
        "功能详细说明",
        "非功能需求",
        "数据埋点",
        "附录",
    )
    assert all(f"## {heading}" in template for heading in required_headings)
    assert "问题现状" in template
    assert "数据佐证" in template
    assert "归因分析" in template
    assert "解决方案" in template
    assert "产品价值" in template
    assert "功能流程" in template
    assert "数据策略" in template
    assert "埋点时机" in template


def test_prd_template_declares_traceable_feature_table_and_artifacts():
    template = (ROOT / "requirements/common/prd-template.md").read_text(encoding="utf-8")
    assert "| 功能 ID | 功能名称 | 功能流程 | 原型图/状态 | 功能描述 | 数据策略 | 特殊场景 | 依赖项 |" in template
    assert "design/state-map.md" in template
    assert "flows/business-flow" in template
    assert "flows/interaction-flow" in template


def test_product_prd_skill_requires_background_formula_and_tracking():
    skill = (ROOT / "skills/product-prd/SKILL.md").read_text(encoding="utf-8")
    assert "需求背景黄金公式" in skill
    assert "数据埋点" in skill
    assert "非功能需求" in skill


def test_flow_and_prototype_skills_require_integrated_traceability():
    flow_skill = (ROOT / "skills/product-flows/SKILL.md").read_text(encoding="utf-8")
    prototype_skill = (ROOT / "skills/product-prototype/SKILL.md").read_text(encoding="utf-8")
    assert "flows/business-flow.md" in flow_skill
    assert "flows/interaction-flow.md" in flow_skill
    assert "Pxx" in flow_skill
    assert "dual-pane" in prototype_skill
    assert "state-map.md" in prototype_skill


def test_workflow_requires_prototype_embedded_interaction_board_and_section_nav():
    workflow = (ROOT / "INTENTFLOW.md").read_text(encoding="utf-8")
    template = (ROOT / "requirements/common/prd-template.md").read_text(encoding="utf-8")
    flows = (ROOT / "skills/product-flows/SKILL.md").read_text(encoding="utf-8")
    assert "原型界面" in workflow
    assert "章节导航" in workflow
    assert "序号与功能名称" in template
    assert "原型图/状态" in template
    assert "页面元素" in template
    assert "[[prototype:P01]]" in template
    assert "统一收录在上表" in template
    assert "prototype" in flows.lower()
    assert "缩略" in flows


def test_intentflow_orders_prd_review_before_integrated_design_delivery():
    workflow = (ROOT / "INTENTFLOW.md").read_text(encoding="utf-8")
    prd_review = workflow.index("PRD 产出与评审")
    integrated = workflow.index("流程—原型—联动评审交付")
    assert prd_review < integrated
    assert "5. **流程—原型—联动评审交付**" in workflow
