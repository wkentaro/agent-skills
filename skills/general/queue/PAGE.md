# Page

Write the round as a JSON file, build it into one HTML page, and share the page the way
the user's instructions say to share HTML. Keep the JSON and any images in a scratch
directory.

```sh
python3 <this skill's directory>/build.py queue.json round-1.html
```

`build.py` checks the JSON, inlines every image, and prints the count of open and
settled items. The round is ready to share when it exits without an assertion error.

## Queue file

```json
{
  "queue": "labelme-triage",
  "title": "Labelme triage",
  "round": 1,
  "items": [
    {
      "id": "pr-2747",
      "title": "Config file permissions: keep the user's, or always private?",
      "from": "Labelme triage",
      "group": "Pull requests",
      "waiting": true,
      "links": [{"label": "#2747", "url": "https://github.com/owner/repo/pull/2747"}],
      "summary": ["First paragraph.", "Second paragraph."],
      "visuals": [
        {"type": "diff", "title": "What the PR changes", "content": "-old line\n+new line"},
        {"type": "image", "title": "Current", "option": "keep-mode", "src": "current.png"}
      ],
      "evidence": [
        {"level": "ran", "text": "`git log -S` on main returned nothing."},
        {"level": "reported", "text": "Both tests fail without the fix: [#2747](https://github.com/owner/repo/pull/2747)."}
      ],
      "door": "two-way",
      "blast": "config file mode",
      "options": [
        {"key": "keep-mode", "label": "Keep the user's permissions and merge", "consequence": "A shared config stays shared.", "recommended": true},
        {"key": "always-private", "label": "Always owner-only, close the PR", "consequence": "Simpler."}
      ],
      "draft": {"label": "Comment that will be posted", "text": "..."}
    }
  ]
}
```

- `queue` and each item `id` are short kebab-case names. Keep an item's `id` the same in
  every round.
- `summary`, evidence `text` and option `consequence` take inline markdown only:
  `` `code` ``, `**bold**` and `[label](https://url)`.
- `from` names the agent or workstream that raised the item. `group` batches items the
  user can accept together. `waiting` marks an item an agent is blocked on.
- Option `key` is what comes back as the answer, so make it readable alone:
  `close-completed`, `keep-2203`.

The page tags an item **verified** when it has `ran` or `seen` evidence, a two-way door
and a recommendation. The user can accept every verified item in one click, so tag
evidence honestly: `reported` and `claimed` keep an item out of that batch.

Set `"confirm": true` on an item to keep it out of that batch whatever its evidence.
Use it when the facts are checked but the choice is policy, or when the blast radius is
more than a handful of things.

## Visuals

Every open decision has a visual. Use the richest type that fits:

1. `image`: a screenshot or rendered output. `src` is a path relative to the JSON file.
2. `html`: a small self-contained mock in `content`, shown in a sandboxed frame.
   Set `height` in pixels. Inline its CSS and use no external URLs. Scripts run only
   with `"interactive": true`, for a mock the user must click through. An interactive
   visual takes no `option` key, so the user picks with the option buttons.
3. `diff`: lines starting with `+` and `-` are coloured.
4. `text`: a tree, pseudocode or ASCII diagram.

Embed a single-file prototype from the `prototype` skill as an interactive `html`
visual. Link a prototype that needs a dev server from `links`.

Give a visual an `option` key when it shows what that option produces. The user can then
click the visual to choose it, and options with visuals sit side by side for comparison.
Add `title` as its caption.

## Answers

The user pastes back a block like this:

```text
queue: labelme-triage  round: 1
issue-1250: close-not-planned
gpu: ?
  note: what does "on by default" mean on a Mac?
pr-2816: close-both
  draft: |
    edited text
```

- `id: key` is a choice. An indented `draft` replaces that item's draft text.
- `id: ?` with a `note` is a question or steer with no choice yet.
- Items missing from the block are still open.

## Next round

Raise `round` by one and rebuild with:

- Settled items: keep the item and add `"settled": {"choice": "close-both", "note": "posted and closed"}`.
  `options` may be dropped. The page lists them last.
- Items that got a note: add `"reply": {"asked": "<the user's note>", "answer": "<your reply>"}`
  and update the summary, evidence, visuals and options to match.
- Items you reshaped for another reason: add `"changed": "<what changed>"`.
- Newly unblocked decisions as new items.
