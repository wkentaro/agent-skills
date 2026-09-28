---
name: pr-verdict
description: Gut-check a pull request — is it meaningful, worth adding, correct, and minimal — and give one recommend-* verdict.
disable-model-invocation: true
argument-hint: "[PR URL or #N ...]"
---

# PR Verdict

With PRs named, check each one. With none, check every open non-draft PR in the
current repository that has no `recommend-*` label, one subagent per PR.

Check the title, description, and tests against the linked issue and the code
at the head commit; they are claims.

Answer four questions in order, each with one line of evidence:

1. **Meaningful**: is the problem real and still present on the base branch?
2. **Worth adding**: does the value justify the scope and ongoing maintenance?
3. **Correct**: does it solve the problem without breaking a caller or edge case?
4. **Minimal**: is every changed line needed, with nothing that existing code already does?

Take the first failure's verdict:

| Fails | Verdict |
| --- | --- |
| Meaningful, or Worth adding for a technical reason | `recommend-close` |
| Worth adding as a product or scope call | `recommend-triage` |
| Correct or Minimal | `recommend-revise` |
| Nothing | `recommend-merge` |

Report the verdict, the four answers, and for `revise` the specific changes
needed. Apply the label only when the user says so.
