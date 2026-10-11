from pathlib import Path

from scripts.intentflow_runtime.demand_gate import evaluate_demand_gate


SECTION_NAMES = [
    "洞察总览", "场景与材料", "反馈与聚类", "问题与归因",
    "公开产品参考", "首版需求收口", "验证与指标", "待确认结论",
]


def write_case(root: Path, feedback: str, findings: str | None = None, products: str | None = None) -> Path:
    research = root / "research"
    research.mkdir(parents=True)
    (root / "source.md").write_text(
        "# 材料与来源\n\n| ID | 材料 | 来源位置 | 获取日期 | 适用范围 |\n| --- | --- | --- | --- | --- |\n"
        "| S-01 | 访谈记录 | local/interview.md | 2026-10-09 | 目标场景 |\n",
        encoding="utf-8",
    )
    (research / "feedback.csv").write_text(feedback, encoding="utf-8")
    if findings is None:
        findings = "# 示例需求洞察\n\n" + "\n".join(f"## {name}\n已记录。" for name in SECTION_NAMES)
    (research / "demand-findings.md").write_text(findings, encoding="utf-8")
    if products is not None:
        (research / "products.csv").write_text(products, encoding="utf-8")
    return root


def test_gate_is_ready_when_real_feedback_is_traceable_and_sections_are_complete(tmp_path: Path):
    root = write_case(
        tmp_path / "ready",
        "id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id\n"
        "F-01,理解困难,课后,看不懂,反复失败,理解原因,real,S-01\n",
        products=(
            "name,official_url,observed_capability,unverified,source_id\n"
            "示例产品,https://example.org,公开练习入口,效果未核实,S-02\n"
        ),
    )

    result = evaluate_demand_gate(
        root,
        root / "research/feedback.csv",
        root / "research/demand-findings.md",
        root / "source.md",
        root / "research/products.csv",
    )

    assert result["status"] == "ready"
    assert result["ready_for_prd"] is True
    assert result["blockers"] == []


def test_gate_is_provisional_for_simulation_only(tmp_path: Path):
    root = write_case(
        tmp_path / "demo",
        "id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id\n"
        "D-01,理解困难,课后,看不懂,反复失败,理解原因,simulation,\n",
    )

    result = evaluate_demand_gate(
        root,
        root / "research/feedback.csv",
        root / "research/demand-findings.md",
        root / "source.md",
    )

    assert result["status"] == "provisional"
    assert result["ready_for_prd"] is False
    assert any("模拟" in warning for warning in result["warnings"])


def test_gate_blocks_missing_required_findings_section(tmp_path: Path):
    findings = "# 示例需求洞察\n\n" + "\n".join(
        f"## {name}\n已记录。" for name in SECTION_NAMES if name != "验证与指标"
    )
    root = write_case(
        tmp_path / "blocked",
        "id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id\n"
        "F-01,理解困难,课后,看不懂,反复失败,理解原因,real,S-01\n",
        findings=findings,
    )

    result = evaluate_demand_gate(
        root,
        root / "research/feedback.csv",
        root / "research/demand-findings.md",
        root / "source.md",
    )

    assert result["status"] == "blocked"
    assert result["ready_for_prd"] is False
    assert any("验证与指标" in blocker for blocker in result["blockers"])


def test_gate_blocks_unknown_evidence_type(tmp_path: Path):
    root = write_case(
        tmp_path / "invalid",
        "id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id\n"
        "X-01,理解,课后,困难,失败,理解,guess,S-01\n",
    )

    result = evaluate_demand_gate(
        root,
        root / "research/feedback.csv",
        root / "research/demand-findings.md",
        root / "source.md",
    )

    assert result["status"] == "blocked"
    assert any("evidence_type" in blocker for blocker in result["blockers"])
