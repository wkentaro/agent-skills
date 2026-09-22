---
name: dispatch-new-session
description: Launch a task in a new Herdr tab after choosing the agent harness and model.
disable-model-invocation: true
argument-hint: "[task]"
---

# Dispatch New Session

Launch one independent session in a background Herdr tab.

## Choose

Use the invocation argument or current request as the task brief. If neither contains a
concrete task, ask for it first.

Ask for the target harness with native structured input, then ask for a model compatible
with that harness. Recommend the path matching the harness running this skill:

| Caller | Recommended target |
| --- | --- |
| Claude | Claude with Opus |
| Codex | Codex with Sol |
| Pi | Pi with its configured default model |

For a cross-harness dispatch, recommend that target's same default. Offer these useful
alternatives:

- Claude: Opus, Fable, or another Claude model.
- Codex: Sol or another Codex model.
- Pi: its configured default or a model present in `pi --list-models`.

Put the recommendation first and label it `Recommended`. When structured input is
unavailable, ask one plain-text question at a time. Never silently replace an unavailable
or incompatible choice.

## Dispatch

Read `herdr --skill`, require `HERDR_ENV=1`, and use the installed CLI syntax. Create a new
tab in the current workspace and directory with `--no-focus`. Derive a short tab label and
unique agent name from the task.

Start the selected harness in the tab's root pane:

- Claude: `--allow-dangerously-skip-permissions --model <model>`
- Codex: `--yolo -m <model>`; use `gpt-5.6-sol` for Sol.
- Pi: omit `--model` for the Pi default; otherwise pass the exact provider/model identifier
  reported by `pi --list-models`.

Prompt the new agent with the task brief without expanding its scope. Wait only long enough
to confirm the prompt enters `working` or `blocked`; leave the session running. If startup
fails before an agent starts, close only the tab created by this invocation. If blocked,
inspect and report the blocker without answering it.

Report the tab, agent name, harness, model, and observed state.
