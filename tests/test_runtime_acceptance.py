from pathlib import Path

import pytest

from scripts.intentflow_runtime.acceptance import latest_results, record_result
from scripts.intentflow_runtime.core import RevisionConflict


def make_checklist(req: Path):
    qa = req / "qa"
    qa.mkdir(parents=True)
    (qa / "checklist.md").write_bytes(
        b"| ID | Behavior | Status |\n| --- | --- | --- |\n| AC-01 | P-1 | \xe6\x9c\xaa\xe6\xb5\x8b |\n"
    )


def test_result_allows_direct_status_without_context_and_rejects_unknown_case(tmp_path: Path):
    req = tmp_path / "example"
    make_checklist(req)

    revision = ""
    for status in ("未测", "通过", "失败", "跳过"):
        revision = record_result(req, "AC-01", status, "", "", revision)
        assert latest_results(req)["AC-01"]["status"] == status
    with pytest.raises(ValueError, match="unknown case"):
        record_result(req, "AC-99", "通过", "", "", revision)


def test_result_is_appended_to_markdown_with_revision_guard(tmp_path: Path):
    req = tmp_path / "example"
    make_checklist(req)

    revision = record_result(req, "AC-01", "失败", "build-1", "失败备注", "")
    assert latest_results(req)["AC-01"]["status"] == "失败"
    assert "build-1" in (req / "qa" / "results.md").read_text(encoding="utf-8")

    with pytest.raises(RevisionConflict):
        record_result(req, "AC-01", "通过", "build-2", "", "")

    record_result(req, "AC-01", "通过", "build-2", "复测备注", revision)
    assert latest_results(req)["AC-01"]["status"] == "通过"
    assert latest_results(req)["AC-01"]["notes"] == "复测备注"
