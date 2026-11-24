"""Regression checks for build.py and the page script. Needs python3 and node."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).parent

# A minimal DOM stub: enough for the page script to render and take clicks.
STUB = """
const nodes = {}, listeners = {}, store = {};
globalThis.document = {
  querySelector: s => nodes[s] ||= { textContent: "", innerHTML: "", scrollTop: 0, scrollIntoView() {}, focus() {} },
  addEventListener: (t, f) => listeners[t] = f,
};
globalThis.localStorage = { getItem: k => store[k] ?? null, setItem: (k, v) => store[k] = v };
const click = dataset => listeners.click({ target: { closest: s => s === "[data-item]" ? { dataset: { item: dataset.item } } : { dataset } } });
"""


def item(id, **extra):
    base = {"id": id, "title": id, "summary": ["s"], "evidence": [{"level": "ran", "text": "x"}],
            "door": "two-way", "blast": "one"}
    if "settled" not in extra:
        base["options"] = [{"key": "yes", "recommended": True}, {"key": "no"}]
        base["visuals"] = [{"type": "html", "content": f"<b>{key}</b>", "option": key} for key in ("yes", "no")]
    return {**base, **extra}


def build(directory, items):
    source, target = Path(directory) / "q.json", Path(directory) / "q.html"
    source.write_text(json.dumps({"queue": "t", "title": "T", "round": 2, "items": items}))
    result = subprocess.run([sys.executable, HERE / "build.py", source, target], capture_output=True, text=True)
    return result, target


def run_page(html, checks):
    script = html.read_text().split("<script>")[-1].split("</script>")[0]
    result = subprocess.run(["node", "-e", STUB + script + checks], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_build_rejects_empty_queue():
    with TemporaryDirectory() as directory:
        result, _ = build(directory, [])
        assert result.returncode != 0 and "queue has no items" in result.stderr


def test_build_rejects_open_item_without_visual():
    with TemporaryDirectory() as directory:
        result, _ = build(directory, [item("bare", visuals=[])])
        assert result.returncode != 0 and "needs at least one visual" in result.stderr


def test_build_rejects_open_item_without_a_static_picture():
    with TemporaryDirectory() as directory:
        result, _ = build(directory, [item("words", visuals=[
            {"type": "text", "content": "v", "option": "yes"}, {"type": "diff", "content": "+v", "option": "no"},
            {"type": "html", "content": "<button>Run</button>", "interactive": True}])])
        assert result.returncode != 0 and "needs a static html or image visual" in result.stderr
        result, _ = build(directory, [item("half", visuals=[{"type": "html", "content": "<b>y</b>", "option": "yes"}])])
        assert result.returncode != 0 and "for option 'no'" in result.stderr
        result, _ = build(directory, [item("blank", visuals=[{"type": "html", "content": "<b>y</b>", "option": "yes"},
                                                        {"type": "html", "content": "  \n", "option": "no"}])])
        assert result.returncode != 0 and "needs content" in result.stderr


def test_build_rejects_empty_image():
    with TemporaryDirectory() as directory:
        (Path(directory) / "empty.png").write_bytes(b"")
        result, _ = build(directory, [item("empty", visuals=[
            {"type": "image", "src": "empty.png", "option": "yes"}, {"type": "html", "content": "<b>no</b>", "option": "no"}])])
        assert result.returncode != 0 and "no image data" in result.stderr
        for src in ["data:image/png;base64,", "data:image/svg+xml, "]:
            result, _ = build(directory, [item("empty", visuals=[
                {"type": "image", "src": src, "option": "yes"}, {"type": "html", "content": "<b>no</b>", "option": "no"}])])
            assert result.returncode != 0 and "no image data" in result.stderr, src
        result, _ = build(directory, [item("open"), item("carried", settled={"choice": "done"},
                                                         visuals=[{"type": "image", "src": "empty.png"}])])
        assert result.returncode == 0, ("a settled item keeps its old picture", result.stderr)


def test_build_rejects_interactive_visual_with_option():
    with TemporaryDirectory() as directory:
        result, _ = build(directory, [item("mock", visuals=[
            {"type": "html", "content": "<b>yes</b>", "option": "yes"},
            {"type": "html", "content": "<button>x</button>", "interactive": True, "option": "yes"}])])
        assert result.returncode != 0 and "interactive visual takes no option key" in result.stderr


def test_build_warns_on_html_visual_that_loads_a_url():
    loads = ['<img src="shot.png">', '<img srcset="data:image/png;base64,A,B 1x, shot@2x.png 2x">',
             '<div style="background: url(&quot;bg.png&quot;)">', '<style>@import "https://cdn.example/a.css";</style>',
             '<svg><image href="map.png"/></svg>', '<script src="https://cdn.example/a.js"></script>',
             '<script type="module">import { h } from "https://esm.sh/preact";</script>',
             '<meta http-equiv="refresh" content="0; url=https://example.com">',
             '<iframe srcdoc="&lt;img src=shot.png&gt;"></iframe>', '<style>@import"theme.css";</style>',
             '<style>.a { background: image-set(url(data:image/gif;base64,AA) 1x, "large.png" 2x) }</style>',
             '<svg><rect fill="url(paints.svg#fade)"/></svg>', '<link rel="preload" as="image" imagesrcset="head.png 1x">',
             '<img srcset="data:image/gif;base64,AA 1x,data:image/gif;base64,AA, large.png 2x">',
             '<script>fetch ("https://example.com/data.json")</script>', '<script>window.fetch("data.json")</script>',
             '<svg><image xlink:href="map.png"/></svg>', '<object data="chart.svg"></object>',
             '<script type="module">export { scale } from "https://esm.sh/d3";</script>']
    shows = ['<pre>&lt;img src="shot.png"&gt; url(bg.png) https://example.com</pre>',
             '<img src="data:image/png;base64,AA"><svg><use href="#dot"/></svg>',
             '<style>/* url(old.png) */ .a { background: url(data:image/png;base64,AA) }</style>',
             '<a href="https://example.com">source</a>', '<svg><rect fill="url(#fade)"/></svg>',
             '<style>.a { background: image-set("data:image/gif;base64,AA" type("image/gif") 1x) }</style>',
             '<img srcset=",data:image/gif;base64,AA 1x,,data:image/gif;base64,AA 2x">',
             '<svg><a xlink:href="https://example.com"><text>Docs</text></a></svg>', '<script>api.fetch("/api/tasks")</script>',
             '<demo-chart data="[1,2]"></demo-chart>']
    with TemporaryDirectory() as directory:
        for content in loads + shows:
            result, _ = build(directory, [item("x", settled={"choice": "done"},
                                               visuals=[{"type": "html", "content": content, "interactive": True}])])
            assert result.returncode == 0, (content, result.stderr)
            assert ("may load" in result.stderr) == (content in loads), (content, result.stderr)
        result, _ = build(directory, [item("snapshot", visuals=[
            {"type": "html", "content": '<script src="demo.js"></script><b>yes</b>', "option": "yes"},
            {"type": "html", "content": "<b>no</b>", "option": "no"}])])
        assert "may load" not in result.stderr, ("a static visual runs no script", result.stderr)
        result, page = build(directory, [item("x", settled={"choice": "done"},
                                              visuals=[{"type": "html", "content": f'<img alt="&#{"0" * 5000}65;">'}])])
        assert result.returncode == 0 and page.exists() and "could not scan" in result.stderr, result.stderr


def test_page():
    with TemporaryDirectory() as directory:
        result, html = build(directory, [
            item("settled", settled={"choice": "done"}, visuals=[{"type": "text", "content": "v", "option": "yes"}]),
            item("constructor", summary=["<!-- <script> example source"]),
            item("noted", visuals=[{"type": "html", "content": "<b>yes</b>", "option": "yes"},
                                   {"type": "html", "content": "<b>no</b>", "option": "no"},
                                   {"type": "html", "content": "<b>live</b>", "interactive": True}]),
            item("old", settled={"choice": "done"}, options=[{"key": "yes"}, {"key": "no"}],
                 visuals=[{"type": "text", "content": "v", "option": "no"}]),
        ])
        assert result.returncode == 0, result.stderr
        assert "<!--" not in html.read_text().split("const QUEUE = ")[1].split(";\n")[0]
        out = run_page(html, """
console.log(JSON.stringify(ITEMS.map(x => x.id)));
state.sel = ITEMS.findIndex(x => x.id === "old"); render();
console.log(nodes["#main"].innerHTML.includes("data-choose"));
state.sel = ITEMS.findIndex(x => x.id === "noted"); render();
console.log(JSON.stringify(nodes["#main"].innerHTML.match(/sandbox="[^"]*"/g)));
state.answers.noted = { note: "why?" };
click({ accept: "" });
console.log(JSON.stringify(output()));
console.log(store["queue:t:2"]);
""").splitlines()
        assert json.loads(out[0]) == ["constructor", "noted", "settled", "old"], "settled items go last"
        assert out[1] == "false", "settled visuals are not choices"
        assert json.loads(out[2]) == ['sandbox=""', 'sandbox=""', 'sandbox="allow-scripts"'], \
            "only interactive visuals run scripts, and never with allow-same-origin"
        assert json.loads(out[3]) == "queue: t  round: 2\nconstructor: yes\nnoted: ?\n  note: why?", \
            "bulk accept skips note-only items and settled items without options"
        assert json.loads(out[4])["constructor"] == {"choice": "yes"}, "answers persist for any id"


if __name__ == "__main__":
    test_build_rejects_empty_queue()
    test_build_rejects_open_item_without_visual()
    test_build_rejects_open_item_without_a_static_picture()
    test_build_rejects_empty_image()
    test_build_rejects_interactive_visual_with_option()
    test_build_warns_on_html_visual_that_loads_a_url()
    test_page()
    print("grill-with-html checks passed.")
