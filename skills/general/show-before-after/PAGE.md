# Page spec

`build.py spec.json out.html` checks the spec, inlines images, and writes one
self-contained page. It exits non-zero with the reason when the spec is incomplete, and
prints a warning for any pane that still loads an asset by URL or path.

```json
{
  "title": "Save button",
  "summary": "The tap target grows to 44px; the layout stays fixed.",
  "variants": [
    {
      "name": "Dark",
      "before": {
        "type": "image", "src": "before-dark.png", "source": "localhost:5173 on main",
        "notes": [{"claim": "24px tap target", "why": "20px under the 44px minimum.",
                   "pin": {"x": 40, "y": 40, "width": 38, "height": 24}}]
      },
      "after": {
        "type": "image", "src": "after-dark.png", "source": "localhost:5174 on feat/tap",
        "summary": "44px tap target",
        "notes": [{"claim": "44px tap target", "why": "Meets the minimum with no layout shift.",
                   "pin": {"x": 40, "y": 40, "width": 74, "height": 44}}]
      }
    }
  ]
}
```

## Panes

Every pane has `type`, `source` (shown under the pane title), and `notes`. The After pane
also has `summary`, its one-line title.

| `type`  | Content                | Pin                                 |
|---------|------------------------|-------------------------------------|
| `image` | `src`, path relative to the spec; `scale` when captured above device scale 1 | `x`, `y` in CSS pixels of the captured page |
| `text`  | `content`              | `line`, 1-based                     |
| `html`  | `content`, rendered in `srcdoc`; `width`, `height` of its viewport (default 1280 x 800) | `x`, `y` in viewport pixels |
| `url`   | `src`; `width`, `height` as for `html` | `x`, `y` in viewport pixels |

Add `width` and `height` to a pin to outline that region while its note is hovered. The
output of `agent-browser get box <selector> --json` is already in this shape.

## Variants

Each variant is one Before/After pair with the same input on both sides. With more than
one, every variant needs a `name`, and the page shows a picker.
