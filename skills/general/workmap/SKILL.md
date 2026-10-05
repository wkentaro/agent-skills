---
name: workmap
description: Map the session's work as an idea, its projects, and their tasks, each with a status and a stable ID. Use when the user asks to divide work into projects or tasks, asks where the session stands, or a reply has to show how pieces of work relate.
argument-hint: "[projects | tasks | open | decisions | delta]"
---

# Workmap

Draw the active conversation's work as a workmap: one tree of an idea, its projects, and their tasks and questions. The workmap is a view built from the conversation alone; drawing it leaves the work, native todos, files, and trackers as they were.

## Nodes

- **Idea**: the one-line problem or aim the session is about.
- **Project**: one goal with a one-line done-condition, orthogonal to its sibling projects.
- **Task**: one reviewable change; in a code repository, one PR.
- **Question**: a decision or unknown still to be settled.

These name units of the work being mapped, whatever the repository's own domain calls a project or a task.

The tree also carries the order of the work:

- A project's tasks form a **stack** in listed order: each builds on the one above it in the list, one PR each, each PR based on the previous one (`gh stack` on GitHub). `∥` marks a task that stands outside the stack.
- Projects run in parallel, each in its own worktree. `after P1` marks one that waits for another.
- `touches:` names the area a project changes. Two projects that touch the same area are not orthogonal: merge them, or order them with `after`.

Nodes that belong to no project go under `Loose`. A session with no projects is all `Loose`.

## Dividing

On "divide into projects" or "divide into tasks", split that level only and redraw. A new node is `[proposed]` until the user accepts it; the latest explicit user decision wins. The user edits the workmap by talking; redraw after each change.

## Scope

Use only the active thread. Treat inherited, parent, or side-conversation context as interpretive context, not nodes, unless the user explicitly imports it.

Include:

- Explicit requests and accepted actions.
- Work started or completed.
- Promises and consequential unanswered questions.
- Meaningful choices under discussion, blockers, and deferred follow-ups.
- Concrete assistant recommendations, consolidated into actionable nodes.
- Consequential rejected or superseded choices.

Exclude mechanical tool steps, minor brainstorming, illustrative examples, facts without actions or decisions, completed substeps already represented by a parent node, and duplicates.

## Statuses

Render each task and question with its fixed emoji and text:

- `✅ [done]`: completed with visible evidence or explicit user confirmation.
- `🔄 [in-progress]`: started but unfinished. If interrupted, add `Interrupted at:` and keep this status.
- `⏳ [pending]`: agreed and actionable but not started.
- `💬 [discussing]`: a decision or approach remains unresolved.
- `⛔ [blocked]`: waiting for input, access, or an external event.
- `⏸️ [deferred]`: intentionally postponed until a condition; add `Resume when:` when known.
- `💡 [proposed]`: concretely suggested but never accepted.
- `🚫 [cancelled]`: rejected, superseded, or no longer needed; add `Reason:` when useful.

Several nodes may be `[in-progress]` when work was genuinely concurrent or interrupted. A project shows a status only when its tasks do not already imply it, such as a `[proposed]` project not yet divided.

## IDs

Projects are `P1`, `P2`; tasks `T1`, `T2`; questions `Q1`, `Q2`. Each sequence is global across the workmap, so a task that moves to another project keeps its ID. On every later drawing, inline or full, reuse IDs, give new nodes the next free number, and keep retired numbers retired. If an earlier workmap is no longer visible after compaction, state that ID continuity cannot be guaranteed.

## Drawing

Keep each node on one line. Add one indented continuation only when omitting it would hide a dependency, blocker, owner, interruption point, resume condition, or essential evidence. Show an owner only when responsibility is ambiguous or belongs to someone other than the agent. List a project's tasks in stack order and its other nodes in discussion order.

### Inline

Inside a discussion, draw only the nodes the reply is about and put the discussion around them. Leave out the title, `Outcome so far`, and `Next move`, and refer to nodes by ID in the prose. A point about one node sits directly under it:

```text
P2 Sidebar clears the home indicator        after P1
├─ 💡 [proposed] T4 safe-area foot
│    could fold into T2: same file, ten lines
└─ 💬 [discussing] Q1 pad the foot or the whole sidebar?
```

### Full

When the user invokes the skill by name or asks where the session stands, draw the whole workmap in this shape, with one blank line between sections and none between adjacent nodes:

```text
Workmap — <idea>

Outcome so far
<one-sentence outcome summary>

P1 <goal>                                   touches: <area>
├─ ✅ [done] T1 <change> (#<PR>)
├─ 🔄 [in-progress] T2 <change> (#<PR>)
└─ ⏳ [pending] T3 <change>
P2 <goal>                                   touches: <area>   after P1
├─ ⏳ [pending] T4 <change>
├─ ⏳ [pending] T5 <change>  ∥
└─ 💬 [discussing] Q1 <open decision>
Loose
└─ ⏸️ [deferred] T6 <change>
     Resume when: <condition>

Next move
<one-sentence recommendation, by ID>
```

## Views

A full workmap takes an optional trailing view:

- `open`: omit `[done]` and `[cancelled]`.
- `decisions`: show only questions and unresolved choices.
- `delta`: show changes since the previous visible workmap.
