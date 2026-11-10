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


def test_page():
    with TemporaryDirectory() as directory:
        result, html = build(directory, [
            item("settled", settled={"choice": "done"}, visuals=[{"type": "text", "content": "v", "option": "yes"}]),
            item("constructor", summary=["<!-- <script> example source"]),
            item("noted"),
            item("old", settled={"choice": "done"}, options=[{"key": "yes"}, {"key": "no"}],
                 visuals=[{"type": "text", "content": "v", "option": "no"}]),
        ])
        assert result.returncode == 0, result.stderr
        assert "<!--" not in html.read_text().split("const QUEUE = ")[1].split(";\n")[0]
        out = run_page(html, """
console.log(JSON.stringify(ITEMS.map(x => x.id)));
state.sel = ITEMS.findIndex(x => x.id === "old"); render();
console.log(nodes["#main"].innerHTML.includes("data-choose"));
state.answers.noted = { note: "why?" };
click({ accept: "" });
console.log(JSON.stringify(output()));
console.log(store["queue:t:2"]);
""").splitlines()
        assert json.loads(out[0]) == ["constructor", "noted", "settled", "old"], "settled items go last"
        assert out[1] == "false", "settled visuals are not choices"
        assert json.loads(out[2]) == "queue: t  round: 2\nconstructor: yes\nnoted: ?\n  note: why?", \
            "bulk accept skips note-only items and settled items without options"
        assert json.loads(out[3])["constructor"] == {"choice": "yes"}, "answers persist for any id"


if __name__ == "__main__":
    test_build_rejects_empty_queue()
    test_page()
    print("Queue checks passed.")
