---
name: ask-me-again
description: Ask pending or upcoming questions as native interactive choices. Use only when the user names ask-me-again.
---

# Ask Me Again

Ask every unanswered question, whether from your preceding message or one you are about
to ask, through native structured input (`AskUserQuestion` in Claude Code,
`request_user_input` in Codex).

- Preserve the question order and any existing options or recommendation.
- For a question without options, offer two or three mutually exclusive choices. Put the
  recommended choice first and explain each choice's tradeoff in one sentence.
- Batch independent questions up to the tool's limit. Ask dependent questions after the
  earlier answers.
- When structured input is unavailable, ask one plain-text question at a time.
- When no unanswered question exists, say so and stop.
