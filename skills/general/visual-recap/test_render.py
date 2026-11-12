"""python3 -I test_render.py"""

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import Invalid, render  # noqa: E402

example = json.loads((Path(__file__).parent / "examples/2026-11-11.json").read_text())
page = render(example)
assert page.count('<article class="card">') == 4
assert "{{" not in page
assert "<b>6 ms</b>" in page
literal = render({**example, "title": "{{CARDS}}"})
assert "<h1>{{CARDS}}" in literal

def raises(data, field):
    try:
        render(data)
    except Invalid as e:
        assert field in str(e), e
    else:
        raise AssertionError(f"accepted bad {field}")


def rejects(mutate, field):
    data = copy.deepcopy(example)
    mutate(data["cards"][0])
    raises(data, field)


raises([], "JSON object")
raises({**example, "cards": [None]}, "cards[0]")
rejects(lambda c: c.update(svg=c["svg"].replace("</svg>", '<image href="https://x/y.png"/></svg>')), "svg")
rejects(lambda c: c.update(svg=c["svg"].replace("<svg ", '<svg onload="x()" ', 1)), "svg")
rejects(lambda c: c.update(tint="purple"), "tint")
rejects(lambda c: c.update(tint=["sand"]), "tint")
rejects(lambda c: c.update(css=1), "css")
rejects(lambda c: c.update(bullets=["one", 2, "three"]), "bullets")
rejects(lambda c: c.update(bullets=["one", "two"]), "bullets")
rejects(lambda c: c.update(svg=c["svg"].replace("<svg ", '<svg/onload="x()" ', 1)), "svg")
rejects(lambda c: c.update(svg=c["svg"] + "<script>x()</script>"), "svg")
rejects(lambda c: c.update(svg=c["svg"].replace("</svg>", "<!--><script>x()</script>--></svg>")), "svg")
rejects(lambda c: c.update(svg=c["svg"].replace('class="t sheet"', 'style="fill:u\\72l(//x/y.png)"', 1)), "svg")
rejects(lambda c: c.update(css="@import 'x.css';"), "css")
rejects(lambda c: c.update(css="@\\69mport '//x/y.css';"), "css")
rejects(lambda c: c.update(css=".a{background:image-set('//x/y.png' 1x)}"), "css")

data = copy.deepcopy(example)
data["cards"][0]["headline"] = "<i>x</i> & y"
assert "&lt;i&gt;x&lt;/i&gt; &amp; y" in render(data)
print("ok")
