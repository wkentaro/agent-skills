---
name: visual-recap
description: Turn a day, week or month of work into a one-page visual recap, one card per project with a drawing and bullets, for a standup, team update or review.
disable-model-invocation: true
---

# Visual recap

A one-page HTML recap of a **period** of work: a card per project, each with a drawing of what changed, a headline that names the outcome, and short bullets the reader can check off. Cards sit in a row on a wide screen and become rows on a phone. `render.py` owns the page; you write `notes.md`, then `recap.json`.

## 1. Set the scope

The scope is the first of these that holds:

1. **A period the request names**: "today", "this week", "October", a date range.
2. **A period the conversation is about**: when the recap is asked for while discussing, say, this week's work, the scope is this week. What the conversation already gathered goes into `notes.md`, and the sources fill in the rest.
3. **This session's work**: when the conversation is the work itself, the recap covers what was done in it. The conversation is the source; step 2 reads it in place of the user's sources.
4. **Nothing yet**: in a session with no work to recap, ask which period.

When two of these fit, such as a session that did work and also discussed this week, ask which one, naming both with their dates.

Resolve a period to a start and end in the user's local time zone; every later step reads only that window. Open your reply with the scope in one line, such as "Recapping this week, Nov 9 to 15", so the user can redirect it.

## 2. Gather into notes.md

For a session recap, write `notes.md` from the conversation and go to step 3. For a period, find the sources in the user's instructions, under a heading such as "Visual recap sources". When there is none, ask once where their work leaves a trace (code hosting, an issue tracker, a task app, notes, agent sessions) and offer the line they could save to their instructions for next time.

Read each source over the period and write what it shows into `notes.md`, grouped by project, each outcome with the link or file that shows it:

```markdown
## SAM3
- Memory attention 93 → 68 ms per frame on CUDA (sam3-onnx docs/performance.md)
- 14 PRs merged (https://github.com/wkentaro/sam3-onnx/pulls?q=is%3Apr+merged%3A2026-11-11)
```

`sources/` has a guide per source: `github.md`, `sessions.md`, `poleway.md`. Read the ones the user named; read any other source the same way, outcomes with links. When no source is reachable, run `sources/interview.md`. A `notes.md` the user hands you, or one written on another machine, is merged in as another source.

Leave out personal work (health, family, errands) unless the user asks for it. Done when every source the user named is read or reported as unreachable.

## 3. Check every number

A comment or session claim is a lead, not a fact. For each count, PR, version and benchmark in `notes.md`, look at the source it cites, and correct or drop what it doesn't show. Done when every number has a source you looked at.

## 4. Write the cards

One card per project, 3 or 4 cards, most important first; a fifth narrows every card on a wide screen, so merge or drop the least important instead. Match the card to the period: a day's card is what moved that day; a week's or month's card is the outcome of the whole stretch, such as "v0.7.0 released, 2× faster on CUDA", with the steps behind it left to the bullets.

```json
{"title": "Nov 11 update", "subtitle": "Wednesday · four projects",
 "cards": [{"area": "SAM3", "tint": "sage",
   "headline": "Fused attention: 93 → 68 ms per frame",
   "bullets": ["14 sam3-onnx PRs merged", "<b>6 ms</b> behind PyTorch on an RTX 3080 Ti", "v0.7.0 after video parity checks"],
   "svg": "<svg viewBox=\"0 0 200 200\" aria-hidden=\"true\">...</svg>",
   "css": "optional, for custom motion"}]}
```

- `title` names the period: `Nov 11 update`, `Week of Nov 9`, `November 2026`. `subtitle` adds the weekday or date range and the project count, such as `Wednesday · four projects`.
- `area`: the project name.
- `tint`: `sand`, `sage`, `mist`, `clay` or `stone`, each card a different one.
- `headline`: the outcome, with its number when there is one.
- `bullets`: 3 to 5 things a teammate could check, each under 8 words. Wrap at most one number per bullet in `<b>`.

`examples/2026-11-11.json` is a finished daily recap.

## 5. Draw

Read `DRAWING.md`, then draw one SVG per card.

## 6. Render and look

```sh
python3 render.py recap.json -o <out>.html --shots <dir>
```

It rejects a malformed card with the field to fix. Open `<dir>/shots.png`, the desktop and phone layouts in their final frame, and go through the checklist in `DRAWING.md` for every drawing. Redraw and render again until every drawing passes.

## 7. Share

Share the HTML as the user's instructions say for HTML files, and reply with the link and the card headlines.
