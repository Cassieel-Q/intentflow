"""Small reproducible funnel calculations with an explicit data contract."""

from __future__ import annotations

import csv
from pathlib import Path


class MissingDataContract(ValueError):
    """Input data cannot support the requested metric without an assumption."""


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    path = Path(path).resolve(strict=True)
    if path.suffix.lower() != ".csv":
        raise MissingDataContract("analysis input must be a CSV file")
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or not rows[0]:
        raise MissingDataContract("CSV has no header or rows")
    return [{str(key): (value or "").strip() for key, value in row.items()} for row in rows]


def summarize_funnel(
    rows: list[dict[str, str]], key_field: str, stage_field: str,
    stages: list[str], window: str,
) -> dict:
    if len(stages) < 2 or len(set(stages)) != len(stages):
        raise MissingDataContract("funnel needs at least two distinct ordered stages")
    if not window.strip():
        raise MissingDataContract("observation window is required")
    if not rows or any(key_field not in row or stage_field not in row for row in rows):
        raise MissingDataContract("key and stage fields are required")
    stage_people: dict[str, set[str]] = {stage: set() for stage in stages}
    for row in rows:
        key = row.get(key_field, "")
        stage = row.get(stage_field, "")
        if not key:
            raise MissingDataContract("person-level metric cannot use blank identity")
        if stage not in stage_people:
            continue
        stage_people[stage].add(key)
    counts = {stage: len(stage_people[stage]) for stage in stages}
    first_count = counts[stages[0]]
    if first_count == 0:
        raise MissingDataContract("funnel denominator is zero")
    conversion: dict[str, dict] = {}
    for stage in stages[1:]:
        numerator = counts[stage]
        conversion[stage] = {
            "numerator": numerator, "denominator": first_count,
            "rate": numerator / first_count,
        }
    lines = [
        "# 漏斗分析（可复算记录）", "", f"观察窗口：{window}",
        f"分析单位：按 `{key_field}` 去重的人", f"阶段字段：`{stage_field}`", "",
        "## 观察结果", "", "| 阶段 | 人数 | 相对首阶段 |", "| --- | ---: | ---: |",
    ]
    for stage in stages:
        rate = counts[stage] / first_count
        lines.append(f"| {stage} | {counts[stage]} | {rate:.2%} |")
    lines.extend([
        "", "## 口径", "", f"首阶段分母：{stages[0]} 的去重人数（{first_count}）",
        "后续阶段分子：该阶段的去重人数；以上数字只描述观察结果，不证明原因。", "",
        "## 限制", "", "- 未提供实验分组、归因窗口或外部基线，不能据此判断因果或增长。",
    ])
    return {"window": window, "key_field": key_field, "stage_field": stage_field,
            "stages": stages, "counts": counts, "conversion": conversion,
            "markdown": "\n".join(lines) + "\n"}
