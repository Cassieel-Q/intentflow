"""Path and revision protection for editable Markdown artifacts."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


ALLOWED_EDIT_TARGETS = frozenset(
    {"prd/PRD.md", "qa/checklist.md", "analytics/report.md"}
)


class InvalidTarget(ValueError):
    """The requested file is outside the active requirement or not editable."""


class RevisionConflict(RuntimeError):
    """The formal Markdown changed after the review page was generated."""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def resolve_requirement_path(root: Path, relative: str) -> Path:
    root = Path(root).resolve(strict=True)
    rel = Path(relative)
    if not relative or rel.is_absolute() or ".." in rel.parts:
        raise InvalidTarget("path must be relative to the active requirement")
    target = (root / rel).resolve(strict=False)
    if not target.is_relative_to(root):
        raise InvalidTarget("path escapes the active requirement")
    return target


def save_if_revision(
    root: Path, relative: str, expected_hash: str, content: str
) -> str:
    rel = Path(relative).as_posix()
    if rel not in ALLOWED_EDIT_TARGETS:
        raise InvalidTarget("this Markdown artifact is not editable from review")
    target = resolve_requirement_path(root, relative)
    if not target.is_file():
        raise RevisionConflict("formal Markdown is missing")

    current = target.read_bytes()
    current_hash = hashlib.sha256(current).hexdigest()
    if current_hash != expected_hash:
        raise RevisionConflict("formal Markdown changed; reload before saving")

    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=target.parent, prefix=".intentflow-", delete=False
        ) as temp:
            temp_name = temp.name
            temp.write(content.encode("utf-8"))
            temp.flush()
            os.fsync(temp.fileno())
        os.replace(temp_name, target)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)
    return sha256_text(content)
