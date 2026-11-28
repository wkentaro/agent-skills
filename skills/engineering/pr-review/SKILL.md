---
name: pr-review
description: Gut-check whether a pull request is meaningful, worth adding, the right approach, correct, and minimal against the caller's blocker definition, and give one recommend-* verdict.
argument-hint: "[PR URL or #N ...]"
---

# PR Review

With PRs named, check each one. With none, check every open non-draft PR in the
current repository that has no `recommend-*` label, one subagent per PR.

The caller defines what counts as a blocker, what is a nitpick, and when
Right approach fails. Only a blocker fails Correct. When the caller gives no
definition, open the report with a warning that the verdict rests on your own
judgment of what blocks.

Check the title, description, and tests against the linked issue and the code
at the head commit; they are claims.

Answer five questions in order, each with one line of evidence:

1. **Meaningful**: is the problem real and still present on the base branch?
2. **Worth adding**: does the value justify the scope and ongoing maintenance?
3. **Right approach**: would you solve it this way, at the root cause?
4. **Correct**: does it solve the problem without breaking a caller or edge case, shown by a test or journey you ran?
5. **Minimal**: is every changed line needed, with nothing that existing code already does?

Take the first failure's verdict:

| Fails | Verdict |
| --- | --- |
| Meaningful, or Worth adding for a technical reason | `recommend-close` |
| Worth adding as a product or scope call | `recommend-triage` |
| Right approach, Correct, or Minimal | `recommend-revise` |
| Nothing | `recommend-merge` |

Report to the caller the verdict, the five answers, every nitpick, and for
`revise` the specific changes needed. The caller decides what reaches the PR.
