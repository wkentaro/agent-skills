---
name: copy-link
description: Copy and print the current Claude Code or Codex session's link, preferring Claude's existing Remote Control HTTPS URL.
disable-model-invocation: true
---

Use the branch for the agent hosting this conversation:

- **Codex:** run `printenv CODEX_THREAD_ID` in this session's shell.
  Build `codex://threads/<returned-id>`.
- **Claude Code:** use the current session ID substituted here:
  `${CLAUDE_SESSION_ID}`. If the placeholder is still literal, check
  `printenv CLAUDE_SESSION_ID`. Run `python3 scripts/claude_link.py '<id>'`
  from this skill's directory. It returns the existing Remote Control
  HTTPS URL when the current session log has one, or the desktop deep
  link otherwise. It honors `CLAUDE_CONFIG_DIR`. Read only the returned
  URL, not conversation contents.

This operation retrieves an existing link; it leaves Remote Control settings
unchanged. On a helper error, report that the session link is unavailable.

Use a nonempty UUID from the current session. If unavailable, say the
current session ID is unavailable and stop. Validate it before building
or copying the URL; use only the current host's ID.

Copy the URL using the native clipboard tool when available. On macOS,
pipe `printf '%s' '<url>'` to `pbcopy`. Confirm copying only when the
clipboard command succeeds.

Respond with three short paragraphs:

1. `Copied the session link to your clipboard.` On failure or when no
   clipboard tool is available, use `Your session link is ready. Clipboard
   copying was unavailable.`
2. `[Open this session in Codex](<url>)` or
   `[Open this session in Claude](<url>)`, matching the host agent.
3. `Session ID:` followed by the actual ID in inline code.
