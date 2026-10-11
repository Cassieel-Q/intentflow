"""Append executed acceptance outcomes to a Markdown run log."""

from __future__ import annotations

import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .core import RevisionConflict, resolve_requirement_path, sha256_text


VALID_STATUSES = frozenset({"未测", "通过", "失败", "跳过"})
HEADER = (
    "# 验收执行记录\n\n"
    "| 时间（UTC） | Case ID | 状态 | 构建版本（选填） | 备注 |\n"
    "| --- | --- | --- | --- | --- |\n"
)


def _cell(value: str) -> str:
    return " ".join(value.replace("|", "/").split())


def latest_results(root: Path) -> dict[str, dict[str, str]]:
    path = resolve_requirement_path(root, "qa/results.md")
    if not path.exists():
        return {}
    results: dict[str, dict[str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) not in {5, 6, 7} or cells[2] not in VALID_STATUSES:
            continue
        # Earlier run logs contained environment and evidence columns. Keep
        # them readable without requiring either field for new results.
        notes = cells[4] if len(cells) == 5 else "；".join(
            item for item in cells[5:] if item
        )
        results[cells[1]] = {
            "status": cells[2],
            "build": cells[3],
            "notes": notes,
        }
    return results


def record_result(
    root: Path,
    case_id: str,
    status: str,
    build: str,
    notes: str,
    expected_hash: str,
) -> str:
    if not re.fullmatch(r"AC-[A-Za-z0-9-]+", case_id):
        raise ValueError("invalid case ID")
    if status not in VALID_STATUSES:
        raise ValueError("invalid status")

    checklist = resolve_requirement_path(root, "qa/checklist.md")
    if not checklist.is_file():
        raise ValueError("acceptance checklist is missing")
    checklist_text = checklist.read_text(encoding="utf-8")
    if not re.search(rf"^\|\s*{re.escape(case_id)}\s*\|", checklist_text, re.MULTILINE):
        raise ValueError("unknown case ID")

    output = resolve_requirement_path(root, "qa/results.md")
    current = output.read_bytes().decode("utf-8") if output.exists() else ""
    if sha256_text(current) != expected_hash and not (not current and expected_hash == ""):
        raise RevisionConflict("acceptance results changed; reload before saving")
    if not current:
        current = HEADER
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    row = f"| {stamp} | {case_id} | {status} | {_cell(build)} | {_cell(notes)} |\n"
    updated = current + row

    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=output.parent, prefix=".intentflow-", delete=False
        ) as temp:
            temp_name = temp.name
            temp.write(updated.encode("utf-8"))
            temp.flush()
            os.fsync(temp.fileno())
        os.replace(temp_name, output)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
    return sha256_text(updated)
