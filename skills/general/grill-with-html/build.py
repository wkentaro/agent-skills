#!/usr/bin/env python3
"""Build a self-contained decision queue page: build.py queue.json out.html"""
import base64
from html import unescape as html_unescape
import json
import mimetypes
import secrets
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote_to_bytes
from tempfile import TemporaryDirectory

LEVELS = {"ran", "seen", "read", "reported", "claimed"}
VISUALS = {"text", "diff", "image", "html"}
DRAWN = {"image", "html"}
HARNESS = """<!doctype html><body style="margin: 0; inline-size: 734px"><pre id="report"></pre><script>
const CHECK = /*__CHECK__*/null;
const report = [];
const frames = CHECK.visuals.map(visual => {
  const frame = document.createElement("iframe");
  frame.setAttribute("sandbox", "allow-scripts");
  frame.style.cssText = `display: block; inline-size: 100%; border: 0; block-size: ${visual.height}px`;
  frame.srcdoc = visual.head + CHECK.reporter + visual.content;
  document.body.append(frame);
  return frame;
});
addEventListener("message", e => {
  if (e.data?.token !== CHECK.token) return;
  report.push([frames.findIndex(frame => frame.contentWindow === e.source), e.data.message]);
});
addEventListener("error", e => report.push([-1, "check page error " + e.message]));
setTimeout(() => document.querySelector("#report").textContent = "REPORT" + JSON.stringify(report), CHECK.wait);
</script>"""
REPORTER = """<script nonce="NONCE">{
const send = message => parent.postMessage({ token: "NONCE", message }, "*");
addEventListener("securitypolicyviolation", e => !["inline", "eval", "wasm-eval"].includes(e.blockedURI) && send("load " + e.blockedURI));
addEventListener("error", e => e.target === window && send("error " + e.message), true);
addEventListener("unhandledrejection", e => send("error " + e.reason));
}</script>"""
WAIT_MS = 5000
BROWSERS = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable")


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
            if not visual["src"].startswith("data:"):
                path = (base / visual["src"]).expanduser()
                mime = mimetypes.guess_type(path.name)[0] or "image/png"
                visual["src"] = f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"
            header, _, payload = visual["src"].partition(",")
            data = base64.b64decode(payload) if header.endswith(";base64") else unquote_to_bytes(payload)
            assert data, f"item {item['id']!r}: an image visual has no image data"


def check_offline(queue: dict) -> str:
    html = [(item["id"], visual) for item in queue["items"] for visual in item.get("visuals") or []
            if visual["type"] == "html"]
    browser = next(filter(None, map(shutil.which, BROWSERS)), None)
    if not browser:
        return "NOT CHECKED OFFLINE: no Chromium found"
    if not html:
        return "loads offline"
    nonce = secrets.token_hex(8)

    def head(visual: dict) -> str:
        scripts = "'unsafe-inline' 'unsafe-eval' data: blob:" if visual.get("interactive") else f"'nonce-{nonce}'"
        policy = f"default-src data: blob: 'unsafe-inline'; script-src {scripts}"
        return f'<meta http-equiv="Content-Security-Policy" content="{policy}"><base href="https://relative.invalid/">'

    check = {
        "token": nonce,
        "wait": WAIT_MS,
        "reporter": REPORTER.replace("NONCE", nonce),
        "visuals": [{"head": head(visual), "content": visual["content"], "height": int(visual.get("height") or 320)}
                    for _, visual in html],
    }
    with TemporaryDirectory() as directory:
        page = Path(directory) / "pages" / "check.html"
        page.parent.mkdir()
        page.write_text(HARNESS.replace("/*__CHECK__*/null", json.dumps(check).replace("<", "\\u003c")))
        result = subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--disable-background-networking",
             f"--user-data-dir={directory}/profile", "--host-resolver-rules=MAP * ~NOTFOUND",
             f"--virtual-time-budget={WAIT_MS + 1000}", "--dump-dom", page.as_uri()],
            capture_output=True, text=True, timeout=120,
        )
    assert result.returncode == 0 and "REPORT" in result.stdout, \
        f"browser check did not run: {browser} exited {result.returncode}: {result.stderr.strip()[-300:]}"
    report = json.loads(html_unescape(result.stdout.split("REPORT", 1)[1].split("</pre>", 1)[0]))
    for index, message in report:
        where = html[index][0] if 0 <= index < len(html) else "?"
        assert False, f"item {where!r}: html visual fails offline: {message}; inline it, since a shared page loads no URL"
    return "loads offline"


def main() -> None:
    source, target = Path(sys.argv[1]), Path(sys.argv[2])
    queue = json.loads(source.read_text())
    check(queue)
    offline = check_offline(queue)
    inline_images(queue, source.parent)
    template = (Path(__file__).parent / "template.html").read_text()
    marker = "/*__QUEUE__*/null"
    assert template.count(marker) == 1
    payload = json.dumps(queue, ensure_ascii=False).replace("<", "\\u003c")
    target.write_text(template.replace(marker, payload))
    open_items = [item for item in queue["items"] if not item.get("settled")]
    print(f"{target}: round {queue['round']}, {len(open_items)} open, {len(queue['items']) - len(open_items)} settled, {offline}")


if __name__ == "__main__":
    main()
