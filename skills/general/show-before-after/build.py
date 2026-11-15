#!/usr/bin/env python3
"""Build a self-contained before/after page: build.py spec.json out.html"""
import base64
import json
import mimetypes
import re
import sys
from pathlib import Path

TYPES = {"image", "text", "html", "url"}
ASSET = re.compile(r"""(?:\bsrc|\bsrcset|<link\b[^>]*\bhref)\s*=\s*["']?|url\(\s*["']?|@import\s+["']?""", re.I)


def panes(spec: dict) -> list[tuple[str, dict]]:
    return [(side, v[side]) for v in spec["variants"] for side in ("before", "after")]


def check(spec: dict) -> None:
    for key in ("title", "summary", "variants"):
        assert spec.get(key), f"spec is missing {key!r}"
    variants = spec["variants"]
    if len(variants) > 1:
        assert all(v.get("name") for v in variants), "every variant needs a name when there are several"
    for v in variants:
        for side in ("before", "after"):
            pane = v.get(side)
            where = f"variant {v.get('name', 1)!r} {side}"
            assert pane, f"{where} is missing"
            assert pane.get("type") in TYPES, f"{where}: type must be one of {sorted(TYPES)}"
            assert pane.get("source"), f"{where} needs a source label"
            if side == "after":
                assert pane.get("summary"), f"{where} needs a one-line summary"
            if pane["type"] == "text":
                assert isinstance(pane.get("content"), str), f"{where} needs 'content'"
            else:
                field = "content" if pane["type"] == "html" else "src"
                assert pane.get(field), f"{where} needs {field!r}"
            if pane["type"] == "url":
                assert pane["src"].startswith(("http://", "https://", "file://")), f"{where}: src must be an http, https, or file URL"
            assert isinstance(pane.setdefault("notes", []), list), f"{where}: notes must be a list"
            for i, note in enumerate(pane["notes"], 1):
                assert note.get("claim") and note.get("why"), f"{where} note {i} needs claim and why"
                pin = note.get("pin") or {}
                if pane["type"] == "text":
                    assert isinstance(pin.get("line"), int) and pin["line"] >= 1, f"{where} note {i} needs pin.line"
                else:
                    assert all(isinstance(pin.get(k), (int, float)) for k in ("x", "y")), f"{where} note {i} needs pin.x and pin.y"


def inline_images(spec: dict, base: Path) -> None:
    for _, pane in panes(spec):
        if pane["type"] == "image" and not pane["src"].startswith("data:"):
            path = base / Path(pane["src"]).expanduser()
            mime = mimetypes.guess_type(path.name)[0] or "image/png"
            pane["src"] = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def warnings(spec: dict) -> list[str]:
    found = []
    for side, pane in panes(spec):
        if pane["type"] == "url":
            found.append(f"{side} loads {pane['src']}; it shows only where that server is reachable")
        if pane["type"] == "html" and any(not pane["content"].startswith(("data:", "#"), m.end()) for m in ASSET.finditer(pane["content"])):
            found.append(f"{side} html loads assets by URL or path; inline them as data: URIs for a self-contained page")
    return found


def main() -> None:
    source, target = Path(sys.argv[1]), Path(sys.argv[2])
    spec = json.loads(source.read_text())
    check(spec)
    inline_images(spec, source.parent)
    template = (Path(__file__).parent / "template.html").read_text()
    marker = "/*__SPEC__*/null"
    assert template.count(marker) == 1
    payload = json.dumps(spec, ensure_ascii=False).replace("<", "\\u003c")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(template.replace(marker, payload))
    notes = sum(len(pane["notes"]) for _, pane in panes(spec))
    print(f"{target}: {len(spec['variants'])} variant(s), {notes} notes, {target.stat().st_size // 1024} KB")
    for warning in warnings(spec):
        print(f"warning: {warning}")


if __name__ == "__main__":
    main()
