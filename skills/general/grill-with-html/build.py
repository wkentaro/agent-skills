#!/usr/bin/env python3
"""Build a self-contained decision queue page: build.py queue.json out.html"""
import base64
import json
import mimetypes
import sys
from pathlib import Path

LEVELS = {"ran", "seen", "read", "reported", "claimed"}
VISUALS = {"text", "diff", "image", "html"}


def check(queue: dict) -> dict:
    for key in ("queue", "title", "round", "items"):
        assert key in queue, f"queue is missing {key!r}"
    assert type(queue["round"]) is int, "round is an integer"
    assert queue["items"], "queue has no items"
    items = {item["id"]: item for item in queue["items"]}
    assert len(items) == len(queue["items"]), "item ids must be unique"
    for item in queue["items"]:
        where = f"item {item['id']!r}"
        assert isinstance(item.get("blockedBy", []), list), f"{where}: blockedBy is a list of ids"
        for blocker in item.get("blockedBy") or []:
            assert blocker in items, f"{where} is blocked by unknown id {blocker!r}"
        if "settled" in item:
            assert isinstance(item["settled"], dict) and item["settled"].get("choice"), f"{where}: settled needs the choice"
    check_acyclic(items)
    for item in queue["items"]:
        where = f"item {item['id']!r}"
        if waits(item, items):
            assert item.get("title"), f"{where} is missing 'title'"
            continue
        for key in ("title", "summary", "evidence", "door", "blast"):
            assert item.get(key), f"{where} is missing {key!r}"
        assert isinstance(item["summary"], list), f"{where}: summary is a list of paragraphs"
        assert item["door"] in ("two-way", "one-way"), f"{where}: door is two-way or one-way"
        for evidence in item["evidence"]:
            assert evidence.get("level") in LEVELS, f"{where}: evidence level must be one of {sorted(LEVELS)}"
            assert evidence.get("text"), f"{where}: evidence needs text"
        if item.get("settled"):
            continue
        options = item.get("options") or []
        assert 2 <= len(options) <= 9, f"{where} needs 2 to 9 options"
        keys = [option["key"] for option in options]
        assert len(keys) == len(set(keys)), f"{where}: option keys must be unique"
        assert sum(bool(option.get("recommended")) for option in options) <= 1, f"{where}: at most one recommended option"
        assert item.get("visuals"), f"{where} needs at least one visual"
        bound = [visual["option"] for visual in item["visuals"] if visual.get("option")]
        assert len(bound) == len(set(bound)), f"{where}: at most one visual per option"
        for visual in item["visuals"]:
            assert visual.get("type") in VISUALS, f"{where}: visual type must be one of {sorted(VISUALS)}"
            assert visual.get("src" if visual["type"] == "image" else "content"), f"{where}: a {visual['type']} visual needs its {'src' if visual['type'] == 'image' else 'content'}"
            assert visual.get("option") in (None, *keys), f"{where}: visual option {visual.get('option')!r} is not an option key"
            assert visual.get("interactive", False) in (True, False), f"{where}: interactive is true or false"
            if visual.get("interactive"):
                assert visual["type"] == "html", f"{where}: only html visuals can be interactive"
                assert not visual.get("option"), f"{where}: an interactive visual takes no option key"
    return items


def waits(item: dict, items: dict) -> bool:
    return not item.get("settled") and any(not items[b].get("settled") for b in item.get("blockedBy") or [])


def check_acyclic(items: dict) -> None:
    done, path = set(), []

    def visit(id: str) -> None:
        assert id not in path, f"blockedBy has a cycle: {' -> '.join(path[path.index(id):] + [id])}"
        if id in done:
            return
        path.append(id)
        for blocker in items[id].get("blockedBy") or []:
            visit(blocker)
        path.pop()
        done.add(id)

    for id in items:
        visit(id)


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
    items = check(queue)
    inline_images(queue, source.parent)
    template = (Path(__file__).parent / "template.html").read_text()
    marker = "/*__QUEUE__*/null"
    assert template.count(marker) == 1
    payload = json.dumps(queue, ensure_ascii=False).replace("<", "\\u003c")
    target.write_text(template.replace(marker, payload))
    settled = sum(bool(item.get("settled")) for item in queue["items"])
    held = sum(waits(item, items) for item in queue["items"])
    print(f"{target}: round {queue['round']}, {len(items) - settled - held} open, {held} held, {settled} settled")


if __name__ == "__main__":
    main()
