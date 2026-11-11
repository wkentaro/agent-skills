#!/usr/bin/env python3
"""Render a recap JSON into one self-contained HTML file.

    render.py recap.json -o out.html [--shots DIR]

--shots writes DIR/shots.png: the desktop and phone layouts side by side,
each drawing in its final frame, rendered by headless Chrome with the
network blocked.
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TINTS = {"sand", "sage", "mist", "clay", "stone"}
SVG_BANNED = re.compile(
    r"<script|<image|<foreignObject|<style|\son\w+\s*=|href|https?:|url\(", re.I
)
CSS_BANNED = re.compile(r"url\(|@import|</style|https?:", re.I)


class Invalid(ValueError):
    pass


def _text(value, where):
    if not isinstance(value, str) or not value.strip():
        raise Invalid(f"{where}: expected non-empty text")
    return html.escape(value.strip())


def _bullet(value, where):
    # Only <b>...</b> survives, for the one number a bullet is about.
    return _text(value, where).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")


def _svg(value, where):
    if not isinstance(value, str) or not value.lstrip().startswith('<svg viewBox="0 0 200 200"'):
        raise Invalid(f'{where}: must start with <svg viewBox="0 0 200 200"')
    if not value.rstrip().endswith("</svg>"):
        raise Invalid(f"{where}: must end with </svg>")
    if m := SVG_BANNED.search(value):
        raise Invalid(f"{where}: not allowed in a drawing: {m.group(0)!r}")
    return value.strip()


def render(data):
    cards = data.get("cards")
    if not isinstance(cards, list) or not 1 <= len(cards) <= 5:
        raise Invalid("cards: expected 1 to 5 cards")
    parts, css = [], []
    for n, c in enumerate(cards):
        w = f"cards[{n}]"
        if c.get("tint") not in TINTS:
            raise Invalid(f"{w}.tint: one of {sorted(TINTS)}")
        bullets = c.get("bullets")
        if not isinstance(bullets, list) or not 3 <= len(bullets) <= 5:
            raise Invalid(f"{w}.bullets: expected 3 to 5 bullets")
        if c.get("css"):
            if CSS_BANNED.search(c["css"]):
                raise Invalid(f"{w}.css: no url(), @import or </style>")
            css.append(c["css"])
        items = "".join(f"<li>{_bullet(b, f'{w}.bullets')}</li>" for b in bullets)
        parts.append(
            f'<article class="card">\n'
            f'  <div class="art" style="background:var(--{c["tint"]})">\n{_svg(c.get("svg"), f"{w}.svg")}\n  </div>\n'
            f'  <div class="k">{_text(c.get("area"), f"{w}.area")}</div>\n'
            f'  <h2>{_text(c.get("headline"), f"{w}.headline")}</h2>\n'
            f"  <ul>{items}</ul>\n"
            f"</article>"
        )
    out = (HERE / "template.html").read_text()
    for key, value in {
        "{{TITLE}}": _text(data.get("title"), "title"),
        "{{SUBTITLE}}": _text(data.get("subtitle"), "subtitle"),
        "{{CARD_CSS}}": "\n".join(css),
        "{{CARDS}}": "\n".join(parts),
    }.items():
        out = out.replace(key, value)
    return out


def _chrome():
    mac = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if mac.exists():
        return str(mac)
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        if path := shutil.which(name):
            return path
    sys.exit("render.py: --shots needs Chrome or Chromium")


def shoot(page, shots):
    shots.mkdir(parents=True, exist_ok=True)
    url = page.resolve().as_uri() + "?still"
    png = shots / "shots.png"
    with tempfile.TemporaryDirectory() as tmp:
        wrap = Path(tmp) / "wrap.html"
        wrap.write_text(
            '<body style="margin:0;display:flex;gap:24px;align-items:flex-start;background:#fff">'
            f'<iframe src="{url}" style="width:1280px;height:1000px;border:0"></iframe>'
            f'<iframe src="{url}" style="width:390px;height:1400px;border:0"></iframe>'
        )
        subprocess.run(
            [_chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--user-data-dir={tmp}/profile", "--proxy-server=127.0.0.1:9",
             "--allow-file-access-from-files", "--window-size=1700,1400",
             "--virtual-time-budget=2000", f"--screenshot={png}", wrap.as_uri()],
            check=True, capture_output=True,
        )
    return png


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json", type=Path)
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--shots", type=Path)
    args = ap.parse_args()
    try:
        page = render(json.loads(args.json.read_text()))
    except Invalid as e:
        sys.exit(f"render.py: {e}")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page)
    print(args.out)
    if args.shots:
        print(shoot(args.out, args.shots))


if __name__ == "__main__":
    main()
