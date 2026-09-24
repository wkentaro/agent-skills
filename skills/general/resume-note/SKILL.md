---
name: resume-note
description: Print a copyable Kanban note for resuming the current coding-agent session.
disable-model-invocation: true
---

# Resume note

Summarize the current session for the user to copy.

Use the active conversation for a short topic, one-sentence status, and one next
step. Report the work without continuing it or checking external services.

Read the current working directory with `pwd` and the computer name with
`scutil --get ComputerName` on macOS or `hostname` elsewhere. Read the session ID
and build the resume command for the agent running this skill, not for whichever
variable happens to be set; a nested session can inherit its parent's variable.

| Agent | Session ID | Resume command |
| --- | --- | --- |
| Codex | `CODEX_THREAD_ID` | `codex resume <session ID>` |
| Claude | `CLAUDE_CODE_SESSION_ID` | `claude --resume <session ID>` |

Shell-quote the directory and session ID in the command. If the session ID is
unavailable or the agent is not listed, state that instead of inventing a command
or falling back to `--last` or `--continue`.

Output only this note, without an outer code fence or additional commentary:

````markdown
- Topic: <Short session topic>
- Computer: <computer name>
- Status: <current outcome or stopping point>
- Next: <one next step>

```sh
cd <absolute working directory> && <resume command>
```
````
