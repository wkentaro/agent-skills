---
name: session-status
description: Reconstruct the active session as a status checklist with stable IDs and one recommended next move.
disable-model-invocation: true
---

# Session Status

Reconstruct the active conversation as a read-only work ledger. Report state; do not continue the work, call tools to verify it, update native todos, or persist the status report.

## Scope

Use only the active thread. Treat inherited, parent, or side-conversation context as interpretive context, not checklist material, unless the user explicitly imports it.

Include:

- Explicit requests and accepted actions.
- Work started or completed.
- Promises and consequential unanswered questions.
- Meaningful choices under discussion, blockers, and deferred follow-ups.
- Concrete assistant recommendations, consolidated into actionable items.
- Consequential rejected or superseded choices.

Exclude mechanical tool steps, minor brainstorming, illustrative examples, facts without actions or decisions, completed substeps already represented by a parent item, and duplicates.

The latest explicit user decision wins. Never promote a proposal into a commitment.

## Statuses

Render each status with its fixed emoji and text:

- `✅ [done]`: completed with visible evidence or explicit user confirmation.
- `🔄 [in-progress]`: started but unfinished. If interrupted, add `Interrupted at:` and keep this status.
- `⏳ [pending]`: agreed and actionable but not started.
- `💬 [discussing]`: a decision or approach remains unresolved.
- `⛔ [blocked]`: waiting for input, access, or an external event.
- `⏸️ [deferred]`: intentionally postponed until a condition; add `Resume when:` when known.
- `💡 [proposed]`: concretely suggested but never accepted.
- `🚫 [cancelled]`: rejected, superseded, or no longer needed; add `Reason:` when useful.

Multiple items may be `[in-progress]` when work was genuinely concurrent or interrupted.

## IDs and updates

Assign global sequential report IDs: `R-001`, `R-002`, and so on. Treat a legacy `SL-NNN` as the equivalent `R-NNN`, preserving its number. On later invocations within the visible conversation, reuse IDs, update statuses instead of duplicating items, append new IDs, and never renumber. If an earlier status report is no longer visible after compaction, state that ID continuity cannot be guaranteed.

## Output

Return a compact plain-text ledger. Use one blank line only between sections, never between adjacent checklist items or between an item and its continuation. Keep each item on one line; add one indented continuation only when omitting it would hide a dependency, blocker, owner, interruption point, resume condition, or essential evidence. Keep the outcome and next move to one sentence each.

Use this shape:

```text
Session status — <topic>

Outcome so far
<one-sentence outcome summary>

<workstream>
<emoji> [status] R-NNN <action-oriented item>
  <essential detail only when needed>
<emoji> [status] R-NNN <action-oriented item>

Next move
<one-sentence global recommendation, preferably by ID>
```

Group items under workstream headings. Order `[pending]` and `[blocked]` items by dependency; retain original discussion order for other statuses. Show an owner only when responsibility is ambiguous or belongs to someone other than the agent.

## Views

Interpret an optional trailing view:

- `open`: omit `[done]` and `[cancelled]`.
- `decisions`: show only unresolved decisions.
- `delta`: show changes since the previous visible status report.

With no view, show the complete ledger.
