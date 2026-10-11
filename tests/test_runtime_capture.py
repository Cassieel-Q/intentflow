from pathlib import Path
import json

from scripts.intentflow_runtime.capture import capture, prune_owned


def test_capture_cache_and_prune_touch_only_registered_files(tmp_path: Path):
    req = tmp_path / "example"
    html = req / "design" / "prototype.html"
    html.parent.mkdir(parents=True)
    html.write_bytes(b"<h1>First</h1>")
    output = req / "design" / "screenshots"
    output.mkdir()
    manual = output / "handmade.png"
    manual.write_bytes(b"manual")
    calls = []

    def renderer(url: str, target: Path, viewport: tuple[int, int]):
        calls.append((url, viewport))
        target.write_bytes(b"PNG" + str(len(calls)).encode())

    first = capture(html, output, ["start", "error"], renderer=renderer)
    assert len(first) == 2
    assert len(calls) == 2
    assert all(path.is_file() for path in first)

    second = capture(html, output, ["start", "error"], renderer=renderer)
    assert second == first
    assert len(calls) == 2

    html.write_bytes(b"<h1>Changed</h1>")
    capture(html, output, ["start", "error"], renderer=renderer)
    assert len(calls) == 4

    removed = prune_owned(output, html, ["start"])
    assert len(removed) == 1
    assert not removed[0].exists()
    assert first[0].exists()
    assert manual.read_bytes() == b"manual"


def test_capture_detects_modified_output_and_prune_preserves_it(tmp_path: Path):
    req = tmp_path / "example"
    html = req / "design" / "prototype.html"
    html.parent.mkdir(parents=True)
    html.write_text("<h1>Ready</h1>", encoding="utf-8")
    output = req / "design" / "screenshots"
    calls = []

    def renderer(url: str, target: Path, viewport: tuple[int, int]):
        calls.append(url)
        target.write_bytes(f"PNG-{len(calls)}".encode())

    image = capture(html, output, ["old"], renderer=renderer)[0]
    image.write_bytes(b"manually changed")
    removed = prune_owned(output, html, [])
    assert removed == []
    assert image.read_bytes() == b"manually changed"

    active = capture(html, output, ["new"], renderer=renderer)[0]
    manifest = output / ".intentflow-captures.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    entry = next(item for item in data["entries"].values() if item["page_id"] == "new")
    entry["file"] = "handmade.png"
    (output / "handmade.png").write_bytes(b"keep")
    manifest.write_text(json.dumps(data), encoding="utf-8")
    removed = prune_owned(output, html, [])
    assert removed == []
    assert (output / "handmade.png").read_bytes() == b"keep"
    assert active.is_file()
