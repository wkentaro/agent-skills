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

- Both states run as web pages: point each `<iframe>` at its own server.
- HTML, CSS, or SVG to recreate (web UI, diagram, email, rendered doc): put the real source
  in an `<iframe srcdoc>`, so the two stylesheets stay isolated.
- Rendered output (chart, model prediction, native or mobile UI): an image per side,
  produced by the real code at each revision.
- Text output (terminal, logs, copy): the real text in a monospace block per side.

Feed both sides the same input, data, and seed, so the change is the only difference.

## Page

1. Title, then one or two sentences: what changes and what stays fixed.
2. One row of controls, only those this comparison needs: annotations toggle, layout (Side
   by side / Stacked), viewport, scroll together for long frames, and input variants that
   exercise the change.
3. Two panes: "Before · <source>" and "After · <one-line summary>".
4. Numbered notes under each pane. Before notes name the problems; After notes name the
   fixes. Each note is a bold claim plus one sentence of why, with concrete numbers (px,
   counts, prices, metrics) where they exist.
5. A numbered pin on the frame at the element or region each note describes. Hovering a note
   highlights its pin, and hovering a pin highlights its note.

## Output

Write the page to `$TMPDIR/<topic>/before-after.html` and open it in a background browser
window. Serve the directory with `python3 -m http.server` when fonts, assets, or iframes
need http. Reply with the path.

The page is done when every note has a pin on what it describes and each side matches its
labelled source.
