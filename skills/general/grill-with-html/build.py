#!/usr/bin/env python3
"""Build a self-contained decision queue page: build.py queue.json out.html"""
import base64
import json
import mimetypes
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

LEVELS = {"ran", "seen", "read", "reported", "claimed"}
VISUALS = {"text", "diff", "image", "html"}
DRAWN = {"image", "html"}
LOCAL = ("data:", "blob:", "#", "about:", "javascript:")
URL_ATTRIBUTES = {"src", "poster", "background"}
HREF_TAGS = {"link", "image", "use", "feimage"}
PAINT_ATTRIBUTES = {"fill", "stroke", "filter", "clip-path", "mask", "marker-start", "marker-mid", "marker-end"}


def css_urls(css: str) -> list[str]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    urls = [m[1] for m in re.finditer(r"url\(\s*['\"]?(.*?)['\"]?\s*\)", css, flags=re.I)]
    urls += [m[2] for m in re.finditer(r"@import\s*(['\"])(.*?)\1", css, flags=re.I)]
    for start in re.finditer(r"image-set\(", css, flags=re.I):
        depth, end = 1, start.end()
        while end < len(css) and depth:
            depth += {"(": 1, ")": -1}.get(css[end], 0)
            end += 1
        candidates = re.sub(r"(?:url|type)\([^)]*\)", "", css[start.end():end], flags=re.I)
        urls += [m[2] for m in re.finditer(r"(['\"])(.*?)\1", candidates)]
    return urls


def srcset_urls(srcset: str) -> list[str]:
    urls, expecting = [], True
    for token in srcset.split():
        if expecting:
            urls.append(token.strip(","))
        elif "," in token and token.split(",", 1)[1]:
            urls.append(token.split(",", 1)[1].strip(","))
        expecting = token.endswith(",")
    return urls


class LoadedUrls(HTMLParser):
    def __init__(self, scripts: bool):
        super().__init__()
        self.scripts, self.urls, self.raw = scripts, [], None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and not self.scripts:
            return
        self.raw = tag if tag in ("style", "script") else None
        self.urls += [value for name, value in attrs.items() if name in URL_ATTRIBUTES and value]
        if tag == "object":
            self.urls.append(attrs.get("data") or "")
        if tag in HREF_TAGS:
            self.urls += [attrs.get("href") or "", attrs.get("xlink:href") or ""]
        for name in ("srcset", "imagesrcset"):
            self.urls += srcset_urls(attrs.get(name) or "")
        for name in ("style", *PAINT_ATTRIBUTES):
            self.urls += css_urls(attrs.get(name) or "")
        self.urls += remote_urls(attrs.get("srcdoc") or "", self.scripts)
        if tag == "meta" and (attrs.get("http-equiv") or "").lower() == "refresh":
            self.urls += re.findall(r"url\s*=\s*['\"]?([^'\"\s;]+)", attrs.get("content") or "", flags=re.I)

    def handle_endtag(self, tag):
        if tag == self.raw:
            self.raw = None

    def handle_data(self, data):
        if self.raw == "style":
            self.urls += css_urls(data)
        if self.raw == "script":
            self.urls += [m[2] or m[4] for m in re.finditer(r"\b(?:import|export)\s*(?:\(\s*|[\w$*{}\s,]+?\bfrom\s*)?(['\"])(.*?)\1|(?<![\w$.])(?:(?:window|self|globalThis)\.)?fetch\s*\(\s*(['\"`])(.*?)\3", data)]


def remote_urls(content: str, scripts: bool) -> list[str]:
    parser = LoadedUrls(scripts)
    parser.feed(content)
    parser.close()
    return [url for url in parser.urls if url.strip() and not url.strip().lower().startswith(LOCAL)]


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
        assert item.get("visuals"), f"{where} needs at least one visual"
        for visual in item["visuals"]:
            assert visual.get("type") in VISUALS, f"{where}: visual type must be one of {sorted(VISUALS)}"
            if visual["type"] == "html":
                assert isinstance(visual.get("content"), str) and visual["content"].strip(), f"{where}: an html visual needs content"
            if visual["type"] == "image":
                assert isinstance(visual.get("src"), str) and visual["src"].strip(), f"{where}: an image visual needs src"
            assert visual.get("option") in (None, *keys), f"{where}: visual option {visual.get('option')!r} is not an option key"
            if visual.get("interactive"):
                assert visual["type"] == "html", f"{where}: only html visuals can be interactive"
                assert not visual.get("option"), f"{where}: an interactive visual takes no option key"
        pictured = {visual.get("option") for visual in item["visuals"]
                    if visual.get("type") in DRAWN and not visual.get("interactive")}
        missing = [key for key in keys if key not in pictured]
        assert not missing, \
            f"{where} needs a static html or image visual for option {missing[0]!r}; text, diff and walkthroughs only add to one"


def inline_images(queue: dict, base: Path) -> None:
    for item in queue["items"]:
        for visual in item.get("visuals") or []:
            if visual["type"] != "image":
                continue
            if visual["src"].startswith("data:"):
                if item.get("settled"):
                    continue
                data = visual["src"].partition(",")[2].strip()
            else:
                path = (base / visual["src"]).expanduser()
                data = path.read_bytes()
                mime = mimetypes.guess_type(path.name)[0] or "image/png"
                visual["src"] = f"data:{mime};base64,{base64.b64encode(data).decode()}"
            assert data or item.get("settled"), f"item {item['id']!r}: an image visual has no image data"


def warn_remote(queue: dict) -> None:
    for item in queue["items"]:
        for visual in item.get("visuals") or []:
            if visual.get("type") == "html" and isinstance(visual.get("content"), str):
                for url in remote_urls(visual["content"], bool(visual.get("interactive"))):
                    print(f"warning: item {item['id']!r}: an html visual may load {url!r}", file=sys.stderr)


def main() -> None:
    source, target = Path(sys.argv[1]), Path(sys.argv[2])
    queue = json.loads(source.read_text())
    check(queue)
    warn_remote(queue)
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
