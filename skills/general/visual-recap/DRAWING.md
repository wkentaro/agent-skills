# Drawing a card

Each card's drawing is a **diagram of what changed**, drawn as a miniature of the real thing: the app window with the changed panel, the pipeline with the faster blocks, one tile per merged PR. The reader should be able to point at the drawing and say what was done. `examples/2026-11-11.json` holds four approved drawings; read them before drawing.

## Canvas

- `<svg viewBox="0 0 200 200" aria-hidden="true">`, content inside x and y 8 to 192.
- Draw on the card's tint. Panels and windows use `class="t sheet"` so they read as paper on the tint.
- Integer or half coordinates, and shared edges where parts meet (pane tops on one y, rows on one step such as 18).

## Vocabulary

Use these classes only, never inline colors except `var(--sheet)` or the card's own tint (`var(--sage)` etc.) for a cut-out line.

| Class | Use |
|---|---|
| `i` | 4 px ink stroke, for the one or two lines that matter: headings, the main path |
| `t` | 2.5 px ink stroke, for outlines, icons and rows |
| `f` | 2.5 px faint stroke, for text stand-ins, ghosted and "before" states. Add `style="stroke-dasharray:4 5"` for not-yet or removed things |
| `sheet` | paper fill, combine with `t` for windows and panels |
| `fill` | solid ink, for the changed or finished part: fused blocks, merged PRs, parked chips |
| `shade` | 12% ink fill, for selection highlights and masks |
| `lbl` | 11 px label in ink, one or two words |
| `sm` | 9 px muted note, for numbers like `93→68` and short captions |

`lbl` and `sm` are hidden on phones, so the drawing must still read without them.

## Motion

Every drawing plays once when it scrolls into view. Give each element its moment with `style="--w:.35s"` (delay); stagger by 0.15 to 0.25 s and finish within 1.5 s, with the changed part last.

- `pop`: scales in, for tiles, blocks and dots.
- `drop`: falls in from 8 px above, for list rows and labels.
- `draw` with `pathLength="1"`: draws the stroke, for paths and circles. `--d` sets its duration.

A `pop` or `drop` on a `<g transform="...">` overrides that transform: wrap the group in a plain `<g class="pop">`.

Motion the classes can't express goes in the card's `css` field. Write the final frame as the base state and animate from the start with `backwards` fill, under `.play`, so screenshots and reduced motion show the finished drawing. Prefix every class and `@keyframes` name in `css` with the card's area, such as `lawn-park`, since all cards share one stylesheet. The Lawn card's park animation is the pattern.

## Patterns

- **App window**: `t sheet` frame with `rx="10"`, a sidebar split by a `t` line, the changed panel drawn in detail and the rest as `f` lines. Poleway's Trail card.
- **One per item**: a grid of tiles where the count is the fact (6 tiles for 6 PRs), with a dashed tile for the open one. Labelme's card.
- **Pipeline**: blocks joined by arrows, the changed blocks in `fill`, before→after numbers above in `sm`. SAM3's card.
- **State change**: the thing in its old place as a dashed `f` outline and in its new place as `fill`. Lawn's card.

## Checklist

Look at `shots.png` from `render.py --shots` and fix the drawing until every line holds:

- Someone who reads only the headline can match each part of the drawing to it.
- The real number or count is in the structure: tiles, rows or blocks you can count.
- Nothing overlaps unintentionally, clips at the edge, or floats off the grid.
- The phone thumbnail still shows the idea without its labels.
- It sits beside the other drawings as one set: same line weights, similar density, 15 to 40 elements.
