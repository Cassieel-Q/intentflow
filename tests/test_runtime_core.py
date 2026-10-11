from pathlib import Path

import pytest

from scripts.intentflow_runtime.core import (
    InvalidTarget,
    RevisionConflict,
    resolve_requirement_path,
    save_if_revision,
    sha256_text,
)


def test_resolve_stays_inside_active_requirement(tmp_path: Path):
    req = tmp_path / "requirements" / "example"
    req.mkdir(parents=True)
    target = resolve_requirement_path(req, "prd/PRD.md")
    assert target == req / "prd" / "PRD.md"

    with pytest.raises(InvalidTarget):
        resolve_requirement_path(req, "../other/prd/PRD.md")
    with pytest.raises(InvalidTarget):
        resolve_requirement_path(req, str(tmp_path / "outside.md"))


def test_resolve_rejects_symlink_escape(tmp_path: Path):
    req = tmp_path / "requirements" / "example"
    req.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (req / "prd").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("directory symlinks unavailable")

    with pytest.raises(InvalidTarget):
        resolve_requirement_path(req, "prd/PRD.md")


def test_save_requires_current_revision_and_allowed_target(tmp_path: Path):
    req = tmp_path / "example"
    target = req / "prd" / "PRD.md"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"# First\n")
    old_hash = sha256_text("# First\n")

    new_hash = save_if_revision(req, "prd/PRD.md", old_hash, "# Revised\n")
    assert new_hash == sha256_text("# Revised\n")
    assert target.read_text(encoding="utf-8") == "# Revised\n"

    with pytest.raises(RevisionConflict):
        save_if_revision(req, "prd/PRD.md", old_hash, "# Stale\n")
    assert target.read_text(encoding="utf-8") == "# Revised\n"

    with pytest.raises(InvalidTarget):
        save_if_revision(req, "decisions.md", new_hash, "overwrite")
    with pytest.raises(InvalidTarget):
        save_if_revision(req, "prd/page.html", new_hash, "overwrite")
