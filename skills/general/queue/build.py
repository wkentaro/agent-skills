#!/usr/bin/env python3
"""Build a self-contained decision queue page: build.py queue.json out.html"""
import base64
import json
import mimetypes
import sys
from pathlib import Path

LEVELS = {"ran", "seen", "read", "reported", "claimed"}
VISUALS = {"text", "diff", "image", "html"}


def check(queue: dict) -> None:
    for key in ("queue", "title", "round", "items"):
        assert key in queue, f"queue is missing {key!r}"
    assert queue["items"], "queue has no items"
    ids = [item["id"] for item in queue["items"]]
    assert len(ids) == len(set(ids)), "item ids must be unique"
    for item in queue["items"]:
        where = f"item {item['id']!r}"
        for key in ("title", "summary", "evidence", "door", "blast"):
            assert item.get(key), f"{where} is missing {key!r}"
        assert isinstance(item["summary"], list), f"{where}: summary is a list of paragraphs"
        assert item["door"] in ("two-way", "one-way"), f"{where}: door is two-way or one-way"
        for evidence in item["evidence"]:
            assert evidence.get("level") in LEVELS, f"{where}: evidence level must be one of {sorted(LEVELS)}"
            assert evidence.get("text"), f"{where}: evidence needs text"
        if item.get("settled"):
            assert item["settled"].get("choice"), f"{where}: settled needs the choice"
            continue
        options = item.get("options") or []
        assert 2 <= len(options) <= 9, f"{where} needs 2 to 9 options"
        keys = [option["key"] for option in options]
        assert len(keys) == len(set(keys)), f"{where}: option keys must be unique"
        assert sum(bool(option.get("recommended")) for option in options) <= 1, f"{where}: at most one recommended option"
        for visual in item.get("visuals") or []:
            assert visual.get("type") in VISUALS, f"{where}: visual type must be one of {sorted(VISUALS)}"
            assert visual.get("option") in (None, *keys), f"{where}: visual option {visual.get('option')!r} is not an option key"


def inline_images(queue: dict, base: Path) -> None:
    for item in queue["items"]:
        for visual in item.get("visuals") or []:
            if visual["type"] == "image" and not visual["src"].startswith("data:"):
                path = (base / visual["src"]).expanduser()
                mime = mimetypes.guess_type(path.name)[0] or "image/png"
                visual["src"] = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def main() -> None:
    source, target = Path(sys.argv[1]), Path(sys.argv[2])
    queue = json.loads(source.read_text())
    check(queue)
    inline_images(queue, source.parent)
    template = (Path(__file__).parent / "template.html").read_text()
    marker = "/*__QUEUE__*/null"
    assert template.count(marker) == 1
    payload = json.dumps(queue, ensure_ascii=False).replace("<", "\\u003c")
    target.write_text(template.replace(marker, payload))
    open_items = [item for item in queue["items"] if not item.get("settled")]
    print(f"{target}: round {queue['round']}, {len(open_items)} open, {len(queue['items']) - len(open_items)} settled")


if __name__ == "__main__":
    main()
