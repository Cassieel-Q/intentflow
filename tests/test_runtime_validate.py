from pathlib import Path

from scripts.intentflow_runtime.validate import validate_prd


def test_prd_validator_reports_missing_sections_and_unmapped_behaviors(tmp_path: Path):
    req = tmp_path / "case"
    prd = req / "prd" / "PRD.md"
    prd.parent.mkdir(parents=True)
    prd.write_text("# 功能需求\n\n## 版本信息\n版本：v1\n\n## 详细方案\n### B-01 提交\n", encoding="utf-8")
    result = validate_prd(prd)
    codes = {item["code"] for item in result["findings"]}
    assert {"MISSING_SECTION", "MISSING_BEHAVIOR_FIELD"} <= codes
    assert not result["ok"]


def test_prd_validator_accepts_complete_contract_with_explicit_unknown_baseline(tmp_path: Path):
    req = tmp_path / "case"
    prd = req / "prd" / "PRD.md"
    prd.parent.mkdir(parents=True)
    prd.write_text(
        "# 功能需求\n\n## 版本信息\n版本：v1\n状态：草稿\n更新日期：2026-10-09\n负责人：产品\n"
        "\n## 问题与证据\n目标用户：学生\n场景：复习\n证据：E-01\n"
        "\n## 目标与衡量\n用户结果：能订正\n指标：订正完成率\n分子：完成人数\n分母：进入人数\n周期：7 天\n基线：待基线确认\n"
        "\n## 范围\n本期：订正\n不做：推送\n依赖：题目数据\n"
        "\n## 详细方案\n### B-01 提交订正\n触发：点击提交\n可见结果：显示反馈\n成功：写入记录\n失败：显示重试\n权限：本人\n"
        "\n## 待确认事项\n当前无影响本期的待确认项。\n",
        encoding="utf-8",
    )
    result = validate_prd(prd)
    assert result["ok"], result


def test_prd_validator_accepts_modern_product_review_structure(tmp_path: Path):
    req = tmp_path / "case"
    prd = req / "prd" / "PRD.md"
    prd.parent.mkdir(parents=True)
    prd.write_text(
        "# 功能需求文档\n\n## 文档概述\n标题：错题处理\n版本号：V0.1\n作者：产品\n日期：2026-10-09\n适用对象：设计、开发、测试\n"
        "\n## 需求背景和目标\n项目背景：学生订正困难\n需求目标：独立完成相近题\n相关资料：E-01\n"
        "\n## 功能详细说明\n功能列表：\n### F-01 订正流程\n功能名称：独立重做\n功能流程：进入→提交\n原型图：尚未创建\n展示、交互及逻辑说明：显示结果\n数据策略：记录事件\n特殊场景：空状态\n依赖项：题库\n"
        "\n## 非功能需求\n性能：记录验证方式\n\n## 数据埋点\n参数名：stage\n埋点时机：提交\n\n## 附录\n术语表：无\n参考文档：E-01\n项目排期：待定\n",
        encoding="utf-8",
    )
    result = validate_prd(prd)
    assert result["ok"], result
