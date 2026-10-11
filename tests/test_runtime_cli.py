import json
import os
import subprocess
import sys
from pathlib import Path


CLI = Path(__file__).resolve().parents[1] / "scripts" / "intentflow.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


def test_render_creates_review_without_changing_formal_markdown(tmp_path: Path):
    req = tmp_path / "case"
    source = req / "prd" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_text("# 中文需求\n", encoding="utf-8")
    before = source.read_bytes()

    result = run_cli("render", "--requirement", str(req), "--kind", "prd")

    assert result.returncode == 0, result.stderr
    page = req / "prd" / "PRD-review.html"
    assert page.is_file()
    assert "中文需求" in page.read_text(encoding="utf-8")
    assert source.read_bytes() == before


def test_render_rejects_wrong_source_kind(tmp_path: Path):
    req = tmp_path / "case"
    (req / "qa").mkdir(parents=True)
    (req / "qa" / "checklist.md").write_text("# 验收", encoding="utf-8")
    result = run_cli(
        "render", "--requirement", str(req), "--kind", "prd",
        "--source", "qa/checklist.md",
    )
    assert result.returncode != 0
    assert not (req / "qa" / "PRD-review.html").exists()


def test_doctor_json_reports_required_checks(tmp_path: Path):
    req = tmp_path / "case"
    req.mkdir()
    result = run_cli("doctor", "--requirement", str(req), "--json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report["requirement"] == str(req.resolve())
    assert {"python", "markdown", "browser", "write", "port"} <= set(report["checks"])


def test_init_refuses_to_overwrite_existing_requirement(tmp_path: Path):
    req = tmp_path / "case"
    req.mkdir()
    existing = req / "README.md"
    existing.write_text("keep me", encoding="utf-8")
    result = run_cli("init", "--requirement", str(req))
    assert result.returncode == 0, result.stderr
    assert existing.read_text(encoding="utf-8") == "keep me"
    assert (req / "decisions.md").is_file()


def test_demand_report_writes_optional_html_from_demo_csv(tmp_path: Path):
    req = tmp_path / "case"
    research = req / "research"
    research.mkdir(parents=True)
    (research / "demo.csv").write_text(
        "id,cluster,scenario,obstacle,impact,desired\n"
        "D-01,规则,分数题,规则混淆,再错,理解\n", encoding="utf-8"
    )
    (research / "findings.md").write_text("# 洞察\n", encoding="utf-8")
    result = run_cli(
        "demand-report", "--requirement", str(req), "--csv", "research/demo.csv",
        "--findings", "research/findings.md",
    )
    assert result.returncode == 0, result.stderr
    output = research / "demand-insight.html"
    assert output.is_file()
    assert "模拟演示数据" in output.read_text(encoding="utf-8")


def test_demand_gate_writes_report_and_returns_blocked_exit_code(tmp_path: Path):
    req = tmp_path / "case"
    research = req / "research"
    research.mkdir(parents=True)
    (req / "source.md").write_text("# 来源\n", encoding="utf-8")
    (research / "feedback.csv").write_text(
        "id,cluster,scenario,obstacle,impact,desired,evidence_type,source_id\n"
        "F-01,理解,课后,困难,失败,理解,real,S-404\n", encoding="utf-8"
    )
    (research / "demand-findings.md").write_text("# 洞察\n", encoding="utf-8")

    result = run_cli("demand-gate", "--requirement", str(req))

    assert result.returncode == 2
    report = research / "demand-gate.md"
    assert report.is_file()
    assert "阻塞" in report.read_text(encoding="utf-8")
