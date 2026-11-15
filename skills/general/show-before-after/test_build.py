import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).parent
PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                    "1f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")


def pane(**extra):
    return {"type": "image", "src": "a.png", "source": "main", "summary": "s",
            "notes": [{"claim": "c", "why": "w", "pin": {"x": 1, "y": 2}}], **extra}


def build(directory, spec):
    (Path(directory) / "a.png").write_bytes(PNG)
    source, target = Path(directory) / "spec.json", Path(directory) / "new" / "out.html"
    source.write_text(json.dumps(spec))
    result = subprocess.run([sys.executable, HERE / "build.py", source, target], capture_output=True, text=True)
    return result, target


def spec(**variant):
    return {"title": "T", "summary": "S", "variants": [{"before": pane(), "after": pane(), **variant}]}


def test_builds_self_contained_page():
    with TemporaryDirectory() as d:
        result, target = build(d, spec())
        assert result.returncode == 0, result.stderr
        html = target.read_text()
        assert "data:image/png;base64," in html and "a.png" not in html
        assert "/*__SPEC__*/" not in html


def test_escapes_closing_script_tags():
    with TemporaryDirectory() as d:
        result, target = build(d, spec(after=pane(type="html", content="</script><script>alert(1)</script>")))
        assert result.returncode == 0, result.stderr
        assert target.read_text().count("</script>") == 1


def test_warns_on_external_resources():
    for content in ('<img src="https://x.test/a.png">', '<img srcset="a.png 1x, https://x.test/b.png 2x">',
                    '<style>@import "https://x.test/s.css";</style>', '<link rel="stylesheet" href="app.css">',
                    '<img src="assets/chart.png">'):
        with TemporaryDirectory() as d:
            result, _ = build(d, spec(after=pane(type="html", content=content)))
            assert "inline them" in result.stdout, content
    with TemporaryDirectory() as d:
        result, _ = build(d, spec(after=pane(type="html", content='<a href="x.html">x</a><img src="data:image/png;base64,AA">')))
        assert "inline them" not in result.stdout


def test_accepts_empty_text_output():
    with TemporaryDirectory() as d:
        result, _ = build(d, spec(after=pane(type="text", content="", notes=[])))
        assert result.returncode == 0, result.stderr


def test_rejects_bad_specs():
    cases = {
        "needs pin.x": spec(before=pane(notes=[{"claim": "c", "why": "w", "pin": {}}])),
        "needs pin.line": spec(before=pane(type="text", content="x", notes=[{"claim": "c", "why": "w", "pin": {"x": 1, "y": 1}}])),
        "needs a one-line summary": spec(after=pane(summary="")),
        "type must be one of": spec(before=pane(type="video")),
        "notes must be a list": spec(before=pane(notes={})),
        "needs a name": {"title": "T", "summary": "S", "variants": [{"before": pane(), "after": pane()}] * 2},
    }
    for message, bad in cases.items():
        with TemporaryDirectory() as d:
            result, _ = build(d, bad)
            assert result.returncode != 0 and message in result.stderr, (message, result.stderr)


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
    print("ok")
