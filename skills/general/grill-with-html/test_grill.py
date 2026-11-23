"""Regression checks for build.py and the page script. Needs python3 and node."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

HERE = Path(__file__).parent

STUB = """
const store = {}, nodes = {};
const node = () => ({ textContent: "", innerHTML: "", style: {}, querySelector: () => node(), querySelectorAll: () => [], setAttribute() {} });
globalThis.document = { querySelector: s => nodes[s] ||= node(), querySelectorAll: () => [], addEventListener() {} };
globalThis.localStorage = { getItem: k => store[k] ?? null, setItem: (k, v) => store[k] = v };
globalThis.IntersectionObserver = class { observe() {} };
globalThis.requestAnimationFrame = globalThis.addEventListener = () => {};
globalThis.CSS = { escape: s => s };
"""

def item(id, **extra):
    base = {"id": id, "title": id, "summary": ["s"], "evidence": [{"level": "ran", "text": "x"}],
            "door": "two-way", "blast": "one"}
    if "settled" not in extra:
        base["options"] = [{"key": "yes", "recommended": True}, {"key": "no"}]
        base["visuals"] = [{"type": "text", "content": "v"}]
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


def test_build_rejects_interactive_visual_with_option():
    with TemporaryDirectory() as directory:
        result, _ = build(directory, [item("mock", visuals=[
            {"type": "html", "content": "<button>x</button>", "interactive": True, "option": "yes"}])])
        assert result.returncode != 0 and "interactive visual takes no option key" in result.stderr


def test_build_rejects_unknown_blocker():
    with TemporaryDirectory() as directory:
        result, _ = build(directory, [item("a", blockedBy=["ghost"])])
        assert result.returncode != 0 and "blocked by unknown id 'ghost'" in result.stderr


def test_build_rejects_blocker_cycle():
    with TemporaryDirectory() as directory:
        result, _ = build(directory, [item("a", blockedBy=["b"]), item("b", blockedBy=["a"])])
        assert result.returncode != 0 and "blockedBy has a cycle" in result.stderr


def test_build_accepts_waiting_item_with_only_a_title():
    with TemporaryDirectory() as directory:
        result, _ = build(directory, [item("a"), {"id": "later", "title": "Later", "blockedBy": ["a"]}])
        assert result.returncode == 0, result.stderr
        assert "1 open, 1 held, 0 settled" in result.stdout


def test_build_rejects_malformed_fields():
    cases = [
        ({"round": "<em>2</em>"}, [item("a")], "round is an integer"),
        ({}, [item("a"), item("b", blockedBy="a")], "blockedBy is a list of ids"),
        ({}, [item("a", settled={})], "settled needs the choice"),
        ({}, [item("a", fact="true")], "fact is true or false"),
        ({}, [item("a", fact=True, settled={"choice": "yes"})], "a fact is never settled"),
        ({}, [item("a", visuals=[{"type": "html", "content": "x", "interactive": []}])], "interactive is true or false"),
        ({}, [item("a", visuals=[{"type": "html", "content": "x", "interactive": 1}])], "interactive is true or false"),
        ({}, [item("a", visuals=[{"type": "diff"}])], "a diff visual needs its content"),
        ({}, [item("a", visuals=[{"type": "text", "content": "x", "option": "yes"},
                                 {"type": "text", "content": "y", "option": "yes"}])], "at most one visual per option"),
    ]
    for queue, items, message in cases:
        with TemporaryDirectory() as directory:
            source, target = Path(directory) / "q.json", Path(directory) / "q.html"
            source.write_text(json.dumps({"queue": "t", "title": "T", "round": 2, "items": items, **queue}))
            result = subprocess.run([sys.executable, HERE / "build.py", source, target], capture_output=True, text=True)
            assert result.returncode != 0 and message in result.stderr, (message, result.stderr)


def test_page():
    with TemporaryDirectory() as directory:
        result, html = build(directory, [
            item("settled", settled={"choice": "done"}),
            item("constructor", summary=["<!-- <script> example source"]),
            item("policy", confirm=True),
            item("noted", blockedBy=["settled"], visuals=[{"type": "html", "content": "<b>static</b>"},
                                                         {"type": "html", "content": "<b>live</b>", "interactive": True}]),
            {"id": "later", "title": "Later", "blockedBy": ["noted"]},
            {"id": "count", "title": "Count", "fact": True},
            {"id": "sized", "title": "Sized", "blockedBy": ["count"]},
        ])
        assert result.returncode == 0, result.stderr
        assert "<!--" not in html.read_text().split("const QUEUE = ")[1].split(";\n")[0]
        out = run_page(html, """
console.log(JSON.stringify([OPEN, HELD, SETTLED].map(xs => xs.map(x => x.id))));
const page = nodes["#page"].innerHTML;
console.log(JSON.stringify(page.match(/sandbox="[^"]*"/g)));
console.log(page.includes("Design tree") && page.includes("waits on noted") && page.includes("waits on count") && !page.includes("This round"));
const batch = OPEN.filter(batchable).map(x => x.id);
answers.noted = { note: "why?" };
accept(OPEN.filter(verified));
console.log(JSON.stringify(output()));
console.log(store["queue:t:2"]);
console.log(JSON.stringify([...page.matchAll(/data-node="([^"]+)"/g)].map(m => m[1])));
console.log(JSON.stringify(batch));
console.log(JSON.stringify([...page.matchAll(/ id="(o-[^"]+)"/g)].map(m => m[1])));
""").splitlines()
        assert json.loads(out[0]) == [["constructor", "policy", "noted"], ["later", "count", "sized"], ["settled"]], \
            "an item blocked by an open item is held, and one blocked by a settled item is open"
        assert json.loads(out[1]) == ['sandbox="allow-same-origin"', 'sandbox="allow-scripts"'], \
            "only interactive visuals run scripts, and never with allow-same-origin"
        assert out[2] == "true", "the page shows the design tree and what each waiting item waits on"
        assert json.loads(out[3]) == "queue: t  round: 2\nconstructor: yes\nnoted: ?\n  note: why?", \
            "bulk accept skips note-only items"
        assert json.loads(out[4])["constructor"] == {"choice": "yes"}, "answers persist"
        assert sorted(json.loads(out[5])) == ["constructor", "count", "later", "noted", "policy", "settled", "sized"], \
            "an id that is an Object.prototype key still gets a tree node"
        radio_ids = json.loads(out[7])
        assert len(radio_ids) == len(set(radio_ids)) == 6, "radio ids are unique across items"
        assert json.loads(out[6]) == ["constructor", "noted"], "group accept skips confirm items"


if __name__ == "__main__":
    test_build_rejects_empty_queue()
    test_build_rejects_open_item_without_visual()
    test_build_rejects_interactive_visual_with_option()
    test_build_rejects_unknown_blocker()
    test_build_rejects_blocker_cycle()
    test_build_accepts_waiting_item_with_only_a_title()
    test_build_rejects_malformed_fields()
    test_page()
    print("grill-with-html checks passed.")
