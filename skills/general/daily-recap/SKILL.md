---
name: daily-recap
description: Reconstruct today's work sessions as a reviewable summary of completed, ongoing, and blocked work.
disable-model-invocation: true
---

# Daily Recap

Use the computer's local date and include every available agent session with activity today.

## Reconstruct the day

Use local Codex and Claude session histories as the primary record. For each session, identify the objective, material outcomes, and final state. Combine continuations and repeated attempts into one work item, and group related sessions by outcome rather than chronology.

Treat prompts, assistant claims, commit messages, and pull request descriptions as unverified. When completion matters, check the resulting files, refs, pull requests, releases, or other observable output. Keep verification scoped to repositories and services named in the sessions.

Classify each material item as:

- `Completed`: the intended outcome is visibly finished.
- `In progress`: useful work happened, but the intended outcome remains open.
- `Blocked`: progress requires missing input, access, or an external event.

Include decisions or discoveries only when they help explain the work or its next step. Omit tool mechanics, abandoned exploration with no useful result, and duplicate activity.

Session histories may contain credentials or private data. Use only the minimum detail needed for the recap. If a credential appears, omit its value and warn the user separately.

## Write the recap

Present a concise Markdown draft in this shape:

```markdown
## Daily recap — Month D, YYYY

<One to three sentences summarizing the day's focus and overall progress.>

### Completed
- **Outcome** — What changed and why it matters.

### In progress
- **Work item** — Current state and the next step.

### Blocked
- **Work item** — Current state and the blocker.
```

Include every material work item, but only include status sections that have entries. Order entries by importance, use first person where natural, name the project when needed for context, and prefer concrete outcomes over activity counts.

Show the draft directly in the conversation, not in a code block. After it, state that nothing has been shared and invite the user to revise it or choose a destination. Put coverage gaps and credential warnings there too.
