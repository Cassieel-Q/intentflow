from pathlib import Path

from scripts.intentflow_runtime.analytics_report import build_analytics_html


def _write_case(root: Path) -> tuple[Path, Path]:
    analytics = root / "analytics"
    analytics.mkdir(parents=True)
    report = analytics / "report.md"
    report.write_text(
        "# 示例产品数据复盘报告\n\n"
        "## 1. 复盘问题与产品决策\n\n示例问题。\n\n"
        "## 2. 数据契约\n\n"
        "| 项目 | 本轮记录 |\n| --- | --- |\n"
        "| 提取日期 | 2026-10-11 |\n| 观察窗口 | 不适用 |\n"
        "| 分析单位 | 示例会话 |\n| 主要来源 | research/demo.csv |\n"
        "| 样本量 | 模拟 3 行 |\n| 缺失字段 | 真实会话 ID、时间戳 |\n\n"
        "## 3. 指标与可计算性\n\n"
        "| 指标 | 目标口径 | 本轮结果 | 原因 |\n| --- | --- | --- | --- |\n"
        "| 转化完成率 | 完成 / 进入 | 不可计算 | 无真实事件 |\n"
        "| 留存率 | 回访 / 首访 | 不可计算 | 无真实时间戳 |\n\n"
        "## 4. 已观察事实\n\n1. 仅记录了指标定义。\n\n"
        "## 5. 观察、推断与反例\n\n"
        "### 观察\n\n- 交付的是指标设计。\n"
        "### 推断（待验证）\n\n- 机制待验证。\n"
        "### 其他解释\n\n- 可能由样本偏差导致。\n\n"
        "## 6. 可执行选项（均为助手建议）\n\n"
        "1. **先做小样本采集**：采集真实链路。\n"
        "2. **先做事件校验**：检查去重。\n\n"
        "## 8. 局限与复盘结论\n\n- 无真实数据。\n\n**结论：**保留为演示。\n",
        encoding="utf-8",
    )
    metrics = analytics / "metric-definitions.md"
    metrics.write_text(
        "# 示例指标定义\n\n"
        "| 指标 | 单位 | 分子 | 分母 | 资格条件 | 时间窗/时区 | 去重键 | 当前基线 |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| 转化完成率 | 会话 | 完成的会话数 | 进入的会话数 | 进入流程 | 单次 | session_id | 未建立 |\n"
        "| 留存率 | 用户 | 回访用户数 | 首访用户数 | 有首访记录 | 7 天 | user_id | 未建立 |\n\n"
        "## 口径约束\n\n- 无真实 ID 不计算。\n",
        encoding="utf-8",
    )
    return report, metrics


def test_analytics_view_renders_seven_panels_from_formal_markdown(tmp_path: Path):
    report, metrics = _write_case(tmp_path / "case")
    output = tmp_path / "case" / "analytics" / "report-review.html"

    build_analytics_html(report, metrics, output)

    page = output.read_text(encoding="utf-8")
    for panel_id in ("panel-1", "panel-2", "panel-3", "panel-4", "panel-5", "panel-6", "panel-7"):
        assert f'id="{panel_id}"' in page
    assert "示例产品数据复盘报告" in page
    assert "演示" in page and "不可计算" in page


def test_analytics_view_is_case_agnostic_and_derives_from_metrics(tmp_path: Path):
    report, metrics = _write_case(tmp_path / "case")
    output = tmp_path / "case" / "analytics" / "report-review.html"

    build_analytics_html(report, metrics, output)

    page = output.read_text(encoding="utf-8")
    # Funnel steps come from the metric definitions, not a hardcoded chain.
    assert "转化完成率" in page
    assert "留存率" in page
    # Segment panel derives from eligibility / dedup keys.
    assert "session_id" in page
    assert "user_id" in page
    # No case-specific content leaks into the generic renderer.
    for forbidden in ("错题", "原题订正", "相近题", "wrong_question", "规则混淆", "EVT-0"):
        assert forbidden not in page


def test_analytics_view_does_not_modify_formal_markdown(tmp_path: Path):
    report, metrics = _write_case(tmp_path / "case")
    before_report = report.read_bytes()
    before_metrics = metrics.read_bytes()
    output = tmp_path / "case" / "analytics" / "report-review.html"

    build_analytics_html(report, metrics, output)

    assert report.read_bytes() == before_report
    assert metrics.read_bytes() == before_metrics
