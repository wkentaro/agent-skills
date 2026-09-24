---
name: resume-note
description: Print a copyable Kanban note for resuming the current Codex session.
disable-model-invocation: true
---

# Resume note

Summarize the current session for the user to copy with `/copy`.

Use the active conversation for a short topic, one-sentence status, and one next
step. Report the work without continuing it or checking external services.

Read the current working directory with `pwd`, the session ID from
`CODEX_THREAD_ID`, and the computer name with `scutil --get ComputerName` on
macOS or `hostname` elsewhere. Shell-quote the directory and session ID in the
command. If the session ID is unavailable, state that instead of inventing a
command or using `--last`.

Output only this note, without an outer code fence or additional commentary:

````markdown
<Short session topic>
Computer: <computer name>
Status: <current outcome or stopping point>
Next: <one next step>

```sh
cd <absolute working directory> && codex resume <session ID>
```
````
