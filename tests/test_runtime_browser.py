from pathlib import Path
import threading
from contextlib import contextmanager

import pytest

from scripts.intentflow_runtime.server import make_server


@contextmanager
def running_server(root: Path):
    server = make_server(root, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server, f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def test_browser_copies_local_image_as_embedded_data(tmp_path: Path):
    playwright = pytest.importorskip("playwright.sync_api")
    req = tmp_path / "case"
    prd = req / "prd"
    prd.mkdir(parents=True)
    (prd / "PRD.md").write_text("# 图文\n\n![示意](pixel.png)\n", encoding="utf-8")
    (prd / "pixel.png").write_bytes(
        bytes.fromhex(
            "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
            "0000000b49444154789c636000020000050001a5f645400000000049454e44ae426082"
        )
    )
    with running_server(req) as (_, base):
        with playwright.sync_playwright() as runtime:
            try:
                browser = runtime.chromium.launch(channel="msedge")
            except Exception:
                browser = runtime.chromium.launch()
            try:
                page = browser.new_page()
                page.add_init_script("""
                    Object.defineProperty(navigator, 'clipboard', {value: {
                      write: async items => {
                        const blob = await items[0].getType('text/html');
                        window.copiedHtml = await blob.text();
                      }
                    }});
                """)
                page.goto(f"{base}/review?path=prd/PRD.md&kind=prd")
                page.locator("#copy-content").click()
                page.wait_for_function("window.copiedHtml !== undefined")
                assert "data:image/png;base64," in page.evaluate("window.copiedHtml")
            finally:
                browser.close()


def test_acceptance_progress_and_filter_follow_saved_status(tmp_path: Path):
    playwright = pytest.importorskip("playwright.sync_api")
    req = tmp_path / "case"
    qa = req / "qa"
    qa.mkdir(parents=True)
    (qa / "checklist.md").write_text(
        "| ID | 检查 | 状态 |\n| --- | --- | --- |\n"
        "| AC-01 | 提交 | 未测 |\n| AC-02 | 重试 | 未测 |\n", encoding="utf-8",
    )
    with running_server(req) as (_, base):
        with playwright.sync_playwright() as runtime:
            try:
                browser = runtime.chromium.launch(channel="msedge")
            except Exception:
                browser = runtime.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(f"{base}/review?path=qa/checklist.md&kind=acceptance")
                assert "0/2" in page.locator("#acceptance-progress").inner_text()
                assert page.locator("#review-build").count() == 1
                assert page.locator("#review-environment, #review-evidence").count() == 0
                page.get_by_role("button", name="AC-01 状态 通过").click()
                page.wait_for_function("document.querySelector('#acceptance-progress').textContent.includes('1/2')")
                page.locator("#acceptance-filter").select_option("通过")
                assert page.locator("#document tbody tr:visible").count() == 1
            finally:
                browser.close()
