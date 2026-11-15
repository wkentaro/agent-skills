---
name: show-before-after
description: >-
  Build a side-by-side before/after HTML page with numbered annotations to show a visual
  change: UI, chart, diagram, rendered document, image output, or terminal output. Use when
  the user asks for a before/after, a visual diff, or to see a plan or change visually. PR
  screenshots belong to before-and-after.
---

# Show Before/After

A before/after page is one self-contained HTML page that sets two states of something visual
side by side and pins the reasoning to what the reader sees. Before is usually the current
state; After is a plan, a finished branch, or an alternative.

## Sources

Render each side from the most faithful source available, and label it under the pane
title ("Current app.css", "localhost:5173 on main", "matplotlib, seed 0", "Screenshot,
macOS"):

- Both states run as web pages: a `url` pane per side, each at its own server.
- HTML, CSS, or SVG to recreate (web UI, diagram, email, rendered doc): an `html` pane with
  the real source, so the two stylesheets stay isolated.
- Rendered output (chart, model prediction, native or mobile UI): an `image` pane per
  side, produced by the real code at each revision.
- Text output (terminal, logs, copy): a `text` pane with the real text per side.

Feed both sides the same input, data, and seed, so the change is the only difference.

## Page

Write a spec and build the page from it; the template already carries the layout,
controls, pins, and hover links. [PAGE.md](PAGE.md) has the spec format.

```sh
python3 <skill-dir>/build.py spec.json "$TMPDIR/<topic>/before-after.html"
```

- One variant per input that exercises the change (theme, locale, data set). One variant
  needs no name.
- Before notes name the problems; After notes name the fixes. Each note is a claim plus
  one sentence of why, with concrete numbers (px, counts, prices, metrics) where they
  exist.
- Each note's pin comes from the source as text: `agent-browser get box <selector> --json`
  on the captured page, or the line number for text output. Capture screenshots at device
  scale 1, so box pixels are image pixels.

## Output

When the host's instructions say how to share HTML, share it that way. Otherwise open its
`file://` URL in a background browser window and reply with the absolute path. `srcdoc`
panes, `url` panes pointed at running servers, and inlined images all load from
`file://`, so skip the server.

The page is done when `build.py` exits clean, every note has a pin on what it describes,
and each side matches its labelled source. Check the pins by looking at one downscaled
screenshot of the built page; read captures as text (boxes, DOM, sizes) and open an image
only where text cannot settle the question.
