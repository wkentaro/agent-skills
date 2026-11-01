---
name: settle
description: Close out a finished session by clearing its loose ends, filing its lessons in secondbrain, and closing its herdr pane.
disable-model-invocation: true
---

# Settle

Settle the current session in four steps. Each step finishes before the next
starts.

## 1. Read live state

The session's memory of its repositories and pull requests may be hours old.
For every repository the session touched, run `git fetch`, then read
`git status`, `git worktree list --porcelain`, and `git branch -vv`. For every
pull request the session opened or pushed to, read `gh pr view` with `state`,
`headRefOid`, `labels`, `comments`, and `statusCheckRollup`. Base every later
check on this output.

## 2. Clear the loose ends

A **loose end** is anything that keeps the session from being settled. The
session is **settled** when every check below passes, or the user has chosen to
leave what fails.

For each repository the session touched:

- `git status` is clean and no branch is ahead of its upstream.
- No **stale** branch or worktree remains (see below).
- The primary checkout is on the default branch and up to date. When it sits
  on a stale branch, switch it to the default branch and pull.

For each pull request the session opened or pushed to:

- It is merged, or the user chose to leave it open.
- It has a `recommend-*` label and a review comment. When either is missing on
  a merged pull request, stop any review still running for it and list it as
  merged without review. Start no new review.

For the session itself:

- No offer, question, or follow-up the session raised is still unanswered.
  Search the whole session, not only the last message: "Want me to…",
  "Should I…", failures found on the default branch, and anything reported as
  skipped or not verified.
- No scratch directory, temporary file, or background process it started
  remains. That includes `mktemp -d` directories, local servers, and
  `tailscale serve` entries.

### Stale branches and worktrees

A branch is **stale** when its local head, and its fetched remote head if the
remote branch still exists, each either is contained in the default branch or
equals the `headRefOid` of its merged pull request. Stale status does not
depend on which session created the branch. Find a branch's worktree by the
`branch` line of `git worktree list --porcelain`, since a worktree's directory
name can differ from its branch.

Delete a stale branch without asking when all of these hold:

- Its worktree, if any, is clean apart from `.DS_Store`.
- No herdr pane has its cwd inside that worktree (`herdr pane list`).
- No other local branch tracks it as upstream. Delete stacked branches child
  first.

Use `git wt -d` when the branch has a worktree, after removing its
`.DS_Store`, which `git wt -d` refuses to delete, and `git branch -D`
otherwise. Then delete its remote branch when one still exists, leased to the
remote head you checked:
`git push --force-with-lease=<branch>:<sha> origin :<branch>`. Run
`git worktree prune` for worktrees whose directory is gone. Any other branch or
worktree the session left behind is a loose end.

### Asking

Ask about every remaining loose end in one batch through native structured
input (`AskUserQuestion` in Claude Code, `request_user_input` in Codex). Offer
the choices that fit each one, such as finishing it now, filing an issue,
keeping or deleting an artifact, or leaving it. A worktree another pane is in
stays until that pane's session settles itself, so offer only waiting or
leaving it. Do what the user picks, then
run the checks again. This step is done when the session is settled.

## 3. File the lessons

A **lesson** is something from the session that would change what a future
session does or knows: a decision and its reason, a gotcha, a working recipe,
a fact that took real digging to find. Work that a repository, its history, an
issue, or a pull request already records is not a lesson.

When the session has no lesson, write nothing and say so in one line.

Otherwise, read `~/ghq/github.com/wkentaro/secondbrain/AGENTS.md` and search
secondbrain for the page each lesson belongs on. Cross-project tool lessons
usually belong on a page under `references/tools/`. Propose every lesson with
its target page in one multi-select question. For each lesson the user
approves, update the existing page in place, or create one per the target
domain's `AGENTS.md`. Redact credentials and personal data the lesson does
not need. Commit and push to `main`, and confirm the push succeeded.

## 4. Close the pane

Do this last, since it ends the session. When `HERDR_PANE_ID` is set, read
`herdr tab get "$HERDR_TAB_ID"`. Run `herdr tab close "$HERDR_TAB_ID"` when
its `pane_count` is 1, and `herdr pane close "$HERDR_PANE_ID"` otherwise. When
`HERDR_PANE_ID` is not set, say that no herdr pane was found and stop.
