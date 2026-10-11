"""Mechanical PRD structure checks; product judgment still needs human review."""

from __future__ import annotations

import re
from pathlib import Path

from .core import InvalidTarget


LEGACY_SECTIONS = {
    "版本信息": ("版本", "状态", "更新日期", "负责人"),
    "问题与证据": ("目标用户", "场景", "证据"),
    "目标与衡量": ("用户结果", "指标", "分子", "分母", "周期", "基线"),
    "范围": ("本期", "不做", "依赖"),
    "详细方案": (),
    "待确认事项": (),
}
MODERN_SECTIONS = {
    "文档概述": ("标题", "版本号", "作者", "日期", "适用对象"),
    "需求背景和目标": ("项目背景", "需求目标", "相关资料"),
    "功能详细说明": ("功能列表",),
    "非功能需求": ("性能",),
    "数据埋点": ("参数名", "埋点时机"),
    "附录": ("术语表", "参考文档", "项目排期"),
}
LEGACY_BEHAVIOR_FIELDS = ("触发", "可见结果", "成功", "失败", "权限")
MODERN_BEHAVIOR_FIELDS = ("功能名称", "功能流程", "原型图", "展示、交互及逻辑说明", "数据策略", "特殊场景", "依赖项")
CONSOLIDATED_DETAIL_FIELDS = (
    "功能流程",
    "展示/交互说明",
    "数据策略",
    "边界/异常说明",
    "依赖项",
    "成功/失败条件",
    "埋点关联",
)


def validate_prd(path: Path) -> dict:
    path = Path(path).resolve(strict=True)
    if path.name != "PRD.md" or path.parent.name != "prd":
        raise InvalidTarget("PRD validator expects prd/PRD.md")
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    sections: dict[str, tuple[int, str]] = {}
    current: str | None = None
    buffer: list[str] = []
    findings: list[dict] = []

    def close_section(end_line: int) -> None:
        if current is not None:
            sections[current] = (end_line - len(buffer), "\n".join(buffer))

    for number, line in enumerate(lines, start=1):
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            close_section(number - 1)
            current = match.group(1)
            buffer = []
        elif current is not None:
            buffer.append(line)
    close_section(len(lines))

    def field_has_value(content: str, field: str) -> bool:
        if re.search(rf"(?m)^\s*(?:[-*]\s*)?{re.escape(field)}\s*[：:]\s*\S+", content):
            return True
        heading = re.search(rf"(?m)^###\s+{re.escape(field)}\s*$", content)
        if not heading:
            return False
        remainder = content[heading.end():]
        next_heading = re.search(r"(?m)^###?\s+", remainder)
        body = remainder[:next_heading.start()] if next_heading else remainder
        return bool(body.strip())

    schema = MODERN_SECTIONS if any(heading in sections for heading in MODERN_SECTIONS) else LEGACY_SECTIONS
    for heading, fields in schema.items():
        if heading not in sections:
            findings.append({"code": "MISSING_SECTION", "location": "document", "message": f"缺少二级标题：{heading}"})
            continue
        start, content = sections[heading]
        for field in fields:
            if not field_has_value(content, field):
                findings.append({"code": "MISSING_FIELD", "location": f"{heading}:L{start}", "message": f"缺少或未填写：{field}"})

    behavior_heading = "功能详细说明" if schema is MODERN_SECTIONS else "详细方案"
    behavior_fields = MODERN_BEHAVIOR_FIELDS if schema is MODERN_SECTIONS else LEGACY_BEHAVIOR_FIELDS
    behavior_pattern = r"(?m)^###\s+(F-[A-Za-z0-9-]+)\s+[^\n]+" if schema is MODERN_SECTIONS else r"(?m)^###\s+(B-[A-Za-z0-9-]+)\s+[^\n]+"
    if behavior_heading in sections:
        start, detail = sections[behavior_heading]
        entries = list(re.finditer(behavior_pattern, detail))
        if not entries:
            prefix = "F-" if schema is MODERN_SECTIONS else "B-"
            findings.append({"code": "MISSING_BEHAVIOR", "location": f"{behavior_heading}:L{start}", "message": f"缺少带 {prefix} ID 的行为条目"})
        ids: set[str] = set()
        for index, match in enumerate(entries):
            behavior_id = match.group(1)
            location = f"{behavior_id}:L{start + detail[:match.start()].count(chr(10)) + 1}"
            if behavior_id in ids:
                findings.append({"code": "DUPLICATE_BEHAVIOR_ID", "location": location, "message": "行为 ID 重复"})
            ids.add(behavior_id)
            end = entries[index + 1].start() if index + 1 < len(entries) else len(detail)
            block = detail[match.end():end]
            consolidated = all(token in block for token in ("序号与功能名称", "原型图/状态", "详细说明"))
            if consolidated:
                checks = list(CONSOLIDATED_DETAIL_FIELDS)
                if "[[prototype:" not in block and not re.search(r"\bP\d{2}\b", block):
                    checks.append("可操作原型标记")
                for field in checks:
                    if field not in block:
                        findings.append({"code": "MISSING_BEHAVIOR_FIELD", "location": location, "message": f"缺少或未填写：{field}"})
            else:
                for field in behavior_fields:
                    if not re.search(rf"(?m)^\s*(?:[-*]\s*)?{re.escape(field)}\s*[：:]\s*\S+", block):
                        findings.append({"code": "MISSING_BEHAVIOR_FIELD", "location": location, "message": f"缺少或未填写：{field}"})

    for number, line in enumerate(lines, start=1):
        if re.search(r"\b(?:TODO|TBD)\b|待补充|待填写", line, re.IGNORECASE):
            findings.append({"code": "PLACEHOLDER", "location": f"L{number}", "message": "仍有未处理占位符"})
    return {"ok": not findings, "source": str(path), "findings": findings,
            "scope": "mechanical structure only; evidence and product correctness require review"}
