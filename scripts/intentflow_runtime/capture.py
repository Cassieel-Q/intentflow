"""Browser screenshots with a file ownership manifest."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable

from .core import InvalidTarget


MANIFEST = ".intentflow-captures.json"
Renderer = Callable[[str, Path, tuple[int, int]], None]


class MissingCaptureDependency(RuntimeError):
    """Playwright or a supported browser is not available."""


def _load_manifest(output_dir: Path) -> dict:
    path = output_dir / MANIFEST
    if not path.exists():
        return {"version": 1, "entries": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("entries"), dict):
        raise ValueError("unsupported capture manifest")
    return data


def _save_manifest(output_dir: Path, data: dict) -> None:
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=output_dir,
            prefix=".intentflow-", delete=False,
        ) as temp:
            temp_name = temp.name
            json.dump(data, temp, ensure_ascii=False, indent=2)
            temp.write("\n")
            temp.flush()
            os.fsync(temp.fileno())
        os.replace(temp_name, output_dir / MANIFEST)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def _check_paths(html_path: Path, output_dir: Path) -> tuple[Path, Path]:
    html_path = Path(html_path).resolve(strict=True)
    if not html_path.is_file() or html_path.suffix.lower() != ".html":
        raise InvalidTarget("capture source must be an HTML file")
    requirement_root = html_path.parent.parent.resolve(strict=True)
    output_dir = Path(output_dir).resolve(strict=False)
    if not output_dir.is_relative_to(requirement_root):
        raise InvalidTarget("screenshot output must stay inside its requirement")
    return html_path, output_dir


def _render_with_playwright(url: str, target: Path, viewport: tuple[int, int]) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise MissingCaptureDependency("Install Playwright to capture browser screenshots") from exc
    try:
        with sync_playwright() as playwright:
            try:
                browser = playwright.chromium.launch(channel="msedge")
            except Exception:
                browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": viewport[0], "height": viewport[1]})
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.screenshot(path=str(target), full_page=True)
            finally:
                browser.close()
    except Exception as exc:
        raise MissingCaptureDependency(f"Browser capture failed: {exc}") from exc


def capture(
    html_path: Path,
    output_dir: Path,
    page_ids: Iterable[str],
    *,
    viewport: tuple[int, int] = (1440, 900),
    renderer: Renderer | None = None,
) -> list[Path]:
    html_path, output_dir = _check_paths(html_path, output_dir)
    if viewport[0] < 320 or viewport[1] < 320:
        raise ValueError("viewport is too small")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest(output_dir)
    source = str(html_path)
    source_id = hashlib.sha256(source.encode("utf-8")).hexdigest()[:8]
    source_digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
    render = renderer or _render_with_playwright
    paths = []
    for page_id in page_ids:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", page_id):
            raise ValueError("page ID must contain only letters, digits, dash or underscore")
        key = f"{source}|{page_id}|{viewport[0]}x{viewport[1]}"
        signature = hashlib.sha256(
            f"{source_digest}|{page_id}|{viewport[0]}x{viewport[1]}".encode("utf-8")
        ).hexdigest()
        filename = f"{html_path.stem}-{source_id}-{page_id}-{viewport[0]}x{viewport[1]}.png"
        target = output_dir / filename
        previous = manifest["entries"].get(key, {})
        if previous.get("signature") != signature or not target.is_file():
            url = html_path.as_uri() + (f"#{page_id}" if page_id != "default" else "")
            render(url, target, viewport)
            if not target.is_file():
                raise RuntimeError("screenshot renderer returned without a file")
            manifest["entries"][key] = {
                "source": source, "page_id": page_id,
                "file": filename, "signature": signature,
                "viewport": list(viewport),
                "output_digest": hashlib.sha256(target.read_bytes()).hexdigest(),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        paths.append(target)
    _save_manifest(output_dir, manifest)
    return paths


def prune_owned(output_dir: Path, html_path: Path, active_page_ids: Iterable[str]) -> list[Path]:
    html_path, output_dir = _check_paths(html_path, output_dir)
    if not output_dir.exists():
        return []
    manifest = _load_manifest(output_dir)
    active = set(active_page_ids)
    removed: list[Path] = []
    for key, item in list(manifest["entries"].items()):
        if item.get("source") != str(html_path) or item.get("page_id") in active:
            continue
        filename = item.get("file", "")
        if isinstance(filename, str) and Path(filename).name == filename:
            target = (output_dir / filename).resolve(strict=False)
            if target.parent == output_dir and target.is_file():
                expected_digest = item.get("output_digest")
                actual_digest = hashlib.sha256(target.read_bytes()).hexdigest()
                if expected_digest and actual_digest != expected_digest:
                    continue
                target.unlink()
                removed.append(target)
        del manifest["entries"][key]
    _save_manifest(output_dir, manifest)
    return removed
