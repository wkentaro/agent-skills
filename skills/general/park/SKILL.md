---
name: park
description: Print and copy a one-line reminder and the command for resuming the current coding-agent session.
disable-model-invocation: true
---

# Park

Output one line naming the user and computer and what this session is doing,
then the command that resumes it. Report the work without continuing it or
checking external services.

Read the username with `id -un`, the computer name with `hostname -s`, and the
current working directory with `pwd`. Read the session ID and build the resume
command for the agent running this skill, not for whichever variable happens to
be set; a nested session can inherit its parent's variable.

| Agent | Session ID | Resume command |
| --- | --- | --- |
| Codex | `CODEX_THREAD_ID` | `codex resume <session ID>` |
| Claude | `CLAUDE_CODE_SESSION_ID` | `claude --resume <session ID>` |

Shell-quote the directory and session ID in the command. If the session ID is
unavailable or the agent is not listed, state that instead of inventing a command
or falling back to `--last` or `--continue`.

Copy the note to the clipboard exactly as output, through a quoted heredoc, with
`pbcopy` on macOS, or `wl-copy` or `xclip -selection clipboard` elsewhere. If
none is available, add one line after the note saying it was not copied.

Output only this note, without an outer code fence or additional commentary:

````markdown
<username>@<computer name>: <topic and next step, under 15 words>

```sh
cd <absolute working directory> && <resume command>
```
````
