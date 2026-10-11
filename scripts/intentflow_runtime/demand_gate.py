"""Pre-PRD gate for evidence-backed demand discovery.

The evaluator is deliberately independent of any product case. It reports
whether the discovery record is ready for a PRD, usable only as a provisional
demo, or blocked by missing/untied evidence.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import urlparse


REQUIRED_FEEDBACK = {"id", "cluster", "scenario", "obstacle", "impact", "desired"}
SECTION_NAMES = [
    "洞察总览", "场景与材料", "反馈与聚类", "问题与归因",
    "公开产品参考", "首版需求收口", "验证与指标", "待确认结论",
]
PRODUCT_FIELDS = {"name", "official_url", "observed_capability", "unverified", "source_id"}


def _check(check_id: str, label: str, status: str, detail: str) -> dict[str, str]:
    return {"id": check_id, "label": label, "status": status, "detail": detail}


def _read_feedback(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not Path(path).is_file():
        return [], [f"反馈材料不存在：{path}"]
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not REQUIRED_FEEDBACK <= set(reader.fieldnames):
            return [], ["反馈材料缺少必需字段：id、cluster、scenario、obstacle、impact、desired"]
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    for row in rows:
        row.setdefault("evidence_type", "simulation")
        row.setdefault("source_id", "")
    return rows, []


def _source_ids(path: Path) -> set[str]:
    if not Path(path).is_file():
        return set()
    ids: set[str] = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0] and cells[0].lower() not in {"id", "---"} and not set(cells[0]) <= {"-", ":"}:
            ids.add(cells[0])
    return ids


def _sections(text: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.MULTILINE))
    values: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        values[match.group(1).strip()] = text[match.end():end].strip()
    return values


def _read_products(path: Path | None) -> tuple[list[dict[str, str]], list[str]]:
    if path is None or not Path(path).is_file():
        return [], []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames or not PRODUCT_FIELDS <= set(reader.fieldnames):
            return [], ["公开产品参考缺少字段：name、official_url、observed_capability、unverified、source_id"]
        rows = [{key: (value or "").strip() for key, value in row.items()} for row in reader]
    malformed = [row.get("name", "未命名") for row in rows if urlparse(row.get("official_url", "")).scheme not in {"http", "https"}]
    return rows, ([f"公开产品参考存在无效 URL：{'、'.join(malformed)}"] if malformed else [])


def evaluate_demand_gate(
    requirement: Path,
    feedback_path: Path,
    findings_path: Path,
    source_path: Path,
    products_path: Path | None = None,
) -> dict[str, object]:
    """Evaluate whether discovery can be handed to PRD work."""
    checks: list[dict[str, str]] = []
    blockers: list[str] = []
    warnings: list[str] = []
    requirement = Path(requirement)
    feedback, feedback_errors = _read_feedback(Path(feedback_path))
    findings_text = Path(findings_path).read_text(encoding="utf-8") if Path(findings_path).is_file() else ""
    sections = _sections(findings_text)
    source_ids = _source_ids(Path(source_path))
    products, product_errors = _read_products(products_path)

    if feedback_errors:
        blockers.extend(feedback_errors)
        checks.append(_check("feedback", "反馈材料", "block", "；".join(feedback_errors)))
    elif not feedback:
        blockers.append("反馈材料为空，无法判断痛点是否有材料支撑")
        checks.append(_check("feedback", "反馈材料", "block", "反馈 CSV 没有数据行"))
    else:
        checks.append(_check("feedback", "反馈材料", "pass", f"已读取 {len(feedback)} 条反馈"))

    if not findings_text:
        blockers.append("正式需求洞察 Markdown 不存在")
        checks.append(_check("findings", "正式洞察记录", "block", "找不到 demand-findings.md"))
    else:
        missing = [name for name in SECTION_NAMES if not sections.get(name, "").strip()]
        if missing:
            blockers.append(f"正式洞察缺少章节：{'、'.join(missing)}")
            checks.append(_check("findings", "正式洞察记录", "block", f"缺少或为空：{'、'.join(missing)}"))
        else:
            checks.append(_check("findings", "正式洞察记录", "pass", "八个正式章节均有内容"))

    real_rows = [row for row in feedback if row.get("evidence_type") == "real"]
    simulated_rows = [row for row in feedback if row.get("evidence_type") != "real"]
    invalid_types = [row.get("id", "未命名") for row in feedback if row.get("evidence_type") not in {"real", "simulation"}]
    if invalid_types:
        detail = f"evidence_type 只能是 real 或 simulation：{'、'.join(invalid_types)}"
        blockers.append(detail)
        checks.append(_check("evidence_type", "反馈证据类型", "block", detail))
    missing_source = [row.get("id", "未命名") for row in real_rows if not row.get("source_id")]
    unknown_source = [row.get("id", "未命名") for row in real_rows if row.get("source_id") and row["source_id"] not in source_ids]
    if missing_source or unknown_source:
        details = []
        if missing_source:
            details.append(f"缺 source_id：{'、'.join(missing_source)}")
        if unknown_source:
            details.append(f"source.md 未登记：{'、'.join(unknown_source)}")
        blockers.append("真实反馈不可追溯：" + "；".join(details))
        checks.append(_check("traceability", "真实反馈可追溯", "block", "；".join(details)))
    elif real_rows:
        checks.append(_check("traceability", "真实反馈可追溯", "pass", f"{len(real_rows)} 条真实反馈均能回指 source.md"))
    else:
        warnings.append("当前只有模拟反馈，不能证明真实痛点频率或需求规模")
        checks.append(_check("traceability", "真实反馈可追溯", "warn", "没有真实反馈，当前结果只能作为演示或探索性输入"))

    if products_path is None or not Path(products_path).is_file():
        warnings.append("尚未提供公开产品参考，替代方式和机制对照仍不完整")
        checks.append(_check("alternatives", "公开产品参考", "warn", "products.csv 不存在"))
    elif product_errors:
        warnings.extend(product_errors)
        checks.append(_check("alternatives", "公开产品参考", "warn", "；".join(product_errors)))
    elif products:
        checks.append(_check("alternatives", "公开产品参考", "pass", f"已登记 {len(products)} 个公开产品参考"))
    else:
        warnings.append("公开产品参考文件为空，替代方式和机制对照仍不完整")
        checks.append(_check("alternatives", "公开产品参考", "warn", "products.csv 没有数据行"))

    unresolved = sections.get("待确认结论", "")
    if unresolved:
        warnings.append("仍存在待确认结论，进入 PRD 前需要保留这些边界或完成确认")
        checks.append(_check("open_questions", "待确认边界", "warn", "待确认结论已记录，不能视为用户确认"))

    if blockers:
        status = "blocked"
        next_action = "先补齐阻塞项，再重新运行需求挖掘闸门。"
    elif not real_rows:
        status = "provisional"
        next_action = "可以继续做演示或探索性方案，但补充真实反馈后才能标记为 ready。"
    else:
        status = "ready"
        next_action = "可以进入 PRD 产出；仍需把待确认结论保留为边界，不得当作已确认决策。"
    return {
        "requirement": str(requirement.resolve()),
        "status": status,
        "ready_for_prd": status == "ready",
        "counts": {"feedback": len(feedback), "real": len(real_rows), "simulation": len(simulated_rows), "products": len(products)},
        "checks": checks,
        "blockers": blockers,
        "warnings": warnings,
        "next_action": next_action,
    }


def render_gate_markdown(result: dict[str, object]) -> str:
    """Render a stable Markdown record from a gate result."""
    counts = result["counts"]
    lines = [
        "# 需求挖掘终审闸门",
        "",
        f"- 状态：`{result['status']}`",
        f"- 可进入 PRD：`{'是' if result['ready_for_prd'] else '否'}`",
        f"- 反馈：{counts['feedback']} 条（真实 {counts['real']}，模拟 {counts['simulation']}）",
        f"- 公开产品参考：{counts['products']} 个",
        "",
        "## 检查结果",
        "",
        "| 检查 | 状态 | 说明 |",
        "| --- | --- | --- |",
    ]
    status_labels = {"pass": "通过", "warn": "提醒", "block": "阻塞"}
    for check in result["checks"]:
        lines.append(f"| {check['label']} | {status_labels.get(check['status'], check['status'])} | {check['detail']} |")
    lines.extend(["", "## 阻塞项", ""])
    lines.extend(f"- {item}" for item in result["blockers"] or ["无"])
    lines.extend(["", "## 提醒项", ""])
    lines.extend(f"- {item}" for item in result["warnings"] or ["无"])
    lines.extend(["", "## 下一步", "", str(result["next_action"]), ""])
    return "\n".join(lines)


def write_gate_report(result: dict[str, object], output: Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_gate_markdown(result), encoding="utf-8", newline="\n")
    return output
