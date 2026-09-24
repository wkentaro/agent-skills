---
name: ui-diff
description: >-
  Build a side-by-side before/after HTML page with numbered annotations to show a UI
  change. Use when the user asks for a UI diff, a before/after mock, or to see a UI plan or
  change visually. PR screenshots belong to before-and-after.
---

# UI Diff

A UI diff is one self-contained HTML page that sets two states of a UI side by side and pins
the reasoning to the pixels. Before is usually the current UI; After is a plan, a finished
branch, or an alternative.

## Sources

Render each side from the most faithful source available, and label it under the pane
title ("Current app.css", "localhost:5173 on main", "Screenshot, macOS"):

- Both states run: point each `<iframe>` at its own server.
- Web UI to recreate: put its real CSS and markup in an `<iframe srcdoc>`, so the two
  stylesheets stay isolated.
- Anything else (native, mobile, terminal): a screenshot per side.

Feed both sides the same content and data, so the change is the only difference.

## Page

1. Title, then one or two sentences: what changes and what stays fixed.
2. One row of controls, only those this diff needs: annotations toggle, layout (Side by
   side / Stacked), viewport, scroll together for long frames, and data variants that
   exercise the change.
3. Two panes: "Before · <source>" and "After · <one-line summary>".
4. Numbered notes under each pane. Before notes name the problems; After notes name the
   fixes. Each note is a bold claim plus one sentence of why, with concrete numbers (px,
   counts, prices) where they exist.
5. A numbered pin on the frame at the element each note describes. Hovering a note
   highlights its pin, and hovering a pin highlights its note.

## Output

Write the page to `$TMPDIR/<topic>/before-after.html` and open it in a background browser
window. Serve the directory with `python3 -m http.server` when fonts, assets, or iframes
need http. Reply with the path.

The UI diff is done when every note has a pin on the element it describes and each side
matches its labelled source.
