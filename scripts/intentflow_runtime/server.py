"""Loopback preview and guarded save service for one requirement directory."""

from __future__ import annotations

import json
import mimetypes
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .acceptance import latest_results, record_result
from .core import InvalidTarget, RevisionConflict, resolve_requirement_path, save_if_revision, sha256_text
from .render import render_review


MAX_BODY_BYTES = 5 * 1024 * 1024


def make_server(root: Path, host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    if host != "127.0.0.1":
        raise ValueError("review service must bind to 127.0.0.1")
    root = Path(root).resolve(strict=True)
    token = secrets.token_urlsafe(32)
    write_lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

        def _allowed_host(self) -> bool:
            host_header = self.headers.get("Host", "")
            expected_port = self.server.server_port
            return host_header in {
                f"127.0.0.1:{expected_port}",
                f"localhost:{expected_port}",
            }

        def _allowed_origin(self) -> bool:
            origin = self.headers.get("Origin")
            if not origin:
                return True
            expected_port = self.server.server_port
            return origin in {
                f"http://127.0.0.1:{expected_port}",
                f"http://localhost:{expected_port}",
            }

        def _send(self, data: bytes, status: int, content_type: str, sandbox: bool = False) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            if sandbox:
                self.send_header("Content-Security-Policy", "sandbox allow-scripts allow-forms")
            self.end_headers()
            self.wfile.write(data)

        def _json(self, payload: dict, status: int = 200) -> None:
            self._send(json.dumps(payload, ensure_ascii=False).encode("utf-8"), status, "application/json; charset=utf-8")

        def do_GET(self) -> None:
            if not self._allowed_host() or not self._allowed_origin():
                self._json({"error": "host or origin not allowed"}, 403)
                return
            url = urlparse(self.path)
            if url.path == "/api/health":
                self._json({"ok": True, "service": "intentflow-review"})
                return
            if url.path == "/api/acceptance-results":
                result_file = resolve_requirement_path(root, "qa/results.md")
                revision = sha256_text(result_file.read_bytes().decode("utf-8")) if result_file.exists() else ""
                self._json({"revision": revision, "results": latest_results(root)})
                return
            if url.path == "/review":
                query = parse_qs(url.query)
                rel = query.get("path", [""])[0]
                kind = query.get("kind", [""])[0]
                prototype_rel = query.get("prototype", [""])[0]
                try:
                    source = resolve_requirement_path(root, rel)
                    if not source.is_file() or source.suffix.lower() != ".md":
                        raise InvalidTarget("Markdown source not found")
                    prototype = (
                        resolve_requirement_path(root, prototype_rel)
                        if prototype_rel else None
                    )
                    page = render_review(source, kind, prototype, served=True)
                    page = page.replace("<body ", f'<body data-session-token="{token}" ', 1)
                except (InvalidTarget, FileNotFoundError, ValueError, RuntimeError) as exc:
                    self._json({"error": str(exc)}, 400)
                    return
                self._send(page.encode("utf-8"), 200, "text/html; charset=utf-8")
                return
            relative = unquote(url.path.lstrip("/"))
            try:
                file = resolve_requirement_path(root, relative)
                if not file.is_file():
                    raise FileNotFoundError(relative)
                content_type = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
                self._send(
                    file.read_bytes(), 200, content_type,
                    sandbox=content_type == "text/html",
                )
            except (InvalidTarget, FileNotFoundError, OSError):
                self._json({"error": "file not found"}, 404)

        def do_POST(self) -> None:
            if not self._allowed_host() or not self._allowed_origin():
                self._json({"error": "host or origin not allowed"}, 403)
                return
            if self.headers.get("X-IntentFlow-Token") != token:
                self._json({"error": "session token required"}, 403)
                return
            endpoint = urlparse(self.path).path
            if endpoint not in {"/api/save-markdown", "/api/acceptance-status"}:
                self._json({"error": "unknown endpoint"}, 404)
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > MAX_BODY_BYTES:
                    raise ValueError("invalid request size")
                payload = json.loads(self.rfile.read(length))
                if not isinstance(payload, dict):
                    raise ValueError("request body must be an object")
                if endpoint == "/api/save-markdown":
                    relative = payload["path"]
                    expected_hash = payload["expected_hash"]
                    content = payload["content"]
                    if not all(isinstance(item, str) for item in (relative, expected_hash, content)):
                        raise ValueError("invalid save fields")
                    with write_lock:
                        revision = save_if_revision(root, relative, expected_hash, content)
                else:
                    fields = [payload.get(key, "") for key in ("case_id", "status", "build", "notes", "expected_hash")]
                    if not all(isinstance(item, str) for item in fields):
                        raise ValueError("invalid acceptance fields")
                    with write_lock:
                        revision = record_result(root, *fields)
            except RevisionConflict as exc:
                self._json({"error": str(exc)}, 409)
                return
            except (ValueError, KeyError, TypeError, InvalidTarget, UnicodeDecodeError) as exc:
                self._json({"error": str(exc)}, 400)
                return
            self._json({"revision": revision})

    server = ThreadingHTTPServer((host, port), Handler)
    server.session_token = token
    return server
