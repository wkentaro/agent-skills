# Agent sessions

Claude Code and Codex keep a JSONL log per session on the computer they ran on:

- Claude Code: `~/.claude/projects/<project>/<session>.jsonl`
- Codex: `~/.codex/sessions/<YYYY>/<MM>/<DD>/<session>.jsonl`

Read the sessions with activity inside the period. For each, take the objective and the final state; merge continuations into one item and group by project. Session text is a claim: confirm outcomes in the files, commits or PRs it names, and quote only what the recap needs, since logs can hold credentials and private data. When a credential appears, leave its value out and warn the user.

These logs exist only on the machine that ran the session. For another machine, the user runs this step there and brings back its `notes.md`, or syncs that machine's logs to a folder this one can read.
