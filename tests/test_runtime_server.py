import json
import threading
from contextlib import contextmanager
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from scripts.intentflow_runtime.core import sha256_text
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


def post_json(url: str, payload: dict, token: str = "", headers: dict | None = None):
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-IntentFlow-Token": token,
            **(headers or {}),
        },
    )
    return urlopen(request, timeout=3)


def test_server_exposes_health_and_review_with_session_token(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"# Ready\n")

    with running_server(req) as (server, base):
        health = json.load(urlopen(f"{base}/api/health", timeout=3))
        review = urlopen(f"{base}/review?path=prd/PRD.md&kind=prd", timeout=3).read().decode("utf-8")

    assert health["ok"] is True
    assert f'data-session-token="{server.session_token}"' in review


def test_save_rejects_bad_token_origin_host_and_stale_revision(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"# First\n")
    payload = {
        "path": "prd/PRD.md",
        "expected_hash": sha256_text("# First\n"),
        "content": "# Second\n",
    }

    with running_server(req) as (server, base):
        with pytest.raises(HTTPError) as bad_token:
            post_json(f"{base}/api/save-markdown", payload)
        assert bad_token.value.code == 403

        with pytest.raises(HTTPError) as bad_origin:
            post_json(
                f"{base}/api/save-markdown",
                payload,
                server.session_token,
                {"Origin": "http://evil.test"},
            )
        assert bad_origin.value.code == 403

        with pytest.raises(HTTPError) as bad_host:
            post_json(
                f"{base}/api/save-markdown",
                payload,
                server.session_token,
                {"Host": "evil.test"},
            )
        assert bad_host.value.code == 403

        good = json.load(post_json(f"{base}/api/save-markdown", payload, server.session_token))
        assert good["revision"] == sha256_text("# Second\n")

        with pytest.raises(HTTPError) as stale:
            post_json(f"{base}/api/save-markdown", payload, server.session_token)
        assert stale.value.code == 409

    assert source.read_bytes() == b"# Second\n"


def test_acceptance_result_endpoint_persists_to_markdown(tmp_path: Path):
    req = tmp_path / "example"
    qa = req / "qa"
    qa.mkdir(parents=True)
    (qa / "checklist.md").write_text(
        "| ID | 描述 |\n| --- | --- |\n| AC-01 | 登录成功 |\n", encoding="utf-8"
    )

    with running_server(req) as (server, base):
        initial = json.load(urlopen(f"{base}/api/acceptance-results", timeout=3))
        assert initial == {"revision": "", "results": {}}
        payload = {
            "case_id": "AC-01", "status": "通过",
            "notes": "首轮备注",
            "expected_hash": initial["revision"],
        }
        saved = json.load(post_json(f"{base}/api/acceptance-status", payload, server.session_token))
        assert saved["revision"]
        current = json.load(urlopen(f"{base}/api/acceptance-results", timeout=3))
        assert current["results"]["AC-01"]["status"] == "通过"
        assert current["results"]["AC-01"]["build"] == ""
        assert current["results"]["AC-01"]["notes"] == "首轮备注"

    assert "AC-01" in (qa / "results.md").read_text(encoding="utf-8")


def test_review_rejects_wrong_kind_and_resolves_prototype_from_root(tmp_path: Path):
    req = tmp_path / "example"
    source = req / "prd" / "PRD.md"
    prototype = req / "design" / "prototype.html"
    source.parent.mkdir(parents=True)
    prototype.parent.mkdir(parents=True)
    source.write_text("# PRD", encoding="utf-8")
    prototype.write_text("<h1>Demo</h1>", encoding="utf-8")
    with running_server(req) as (_, base):
        with pytest.raises(HTTPError) as wrong:
            urlopen(f"{base}/review?path=prd/PRD.md&kind=acceptance", timeout=3)
        assert wrong.value.code == 400
        review = urlopen(
            f"{base}/review?path=prd/PRD.md&kind=prd&prototype=design/prototype.html",
            timeout=3,
        ).read().decode("utf-8")
    assert 'data-preview="/design/prototype.html"' in review
    assert '<base href="/prd/">' in review
