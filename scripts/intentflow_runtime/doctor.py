"""Read-only environment checks for the optional local review runtime."""

from __future__ import annotations

import importlib.util
import os
import shutil
import socket
import sys
import tempfile
from pathlib import Path


def diagnose(requirement: Path) -> dict:
    requirement = Path(requirement).resolve(strict=True)
    if not requirement.is_dir():
        raise ValueError("requirement must be a directory")
    checks: dict[str, dict] = {}
    checks["python"] = {"ok": sys.version_info >= (3, 11), "detail": sys.version.split()[0]}
    checks["markdown"] = {
        "ok": importlib.util.find_spec("markdown_it") is not None,
        "detail": "markdown-it-py is required to render reviews",
    }
    browser = (
        shutil.which("msedge") or shutil.which("chromium") or shutil.which("google-chrome")
        or next((str(path) for path in (
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft/Edge/Application/msedge.exe",
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        ) if path.is_file()), None)
    )
    checks["browser"] = {
        "ok": bool(browser), "detail": browser or "No supported browser found; review HTML can still open manually",
        "playwright": importlib.util.find_spec("playwright") is not None,
    }
    try:
        with tempfile.NamedTemporaryFile(dir=requirement, prefix=".intentflow-doctor-", delete=True):
            pass
        checks["write"] = {"ok": True, "detail": "requirement directory is writable"}
    except OSError as exc:
        checks["write"] = {"ok": False, "detail": str(exc)}
    try:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            checks["port"] = {"ok": True, "detail": "loopback bind available"}
    except OSError as exc:
        checks["port"] = {"ok": False, "detail": str(exc)}
    return {"requirement": str(requirement), "checks": checks}
