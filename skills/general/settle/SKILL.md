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
session is **settled** when every check below passes, or each failure has been
resolved by its tier (see Deciding) or left by the user's choice.

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

A branch other than the default branch is **stale** when its local head, and
its fetched remote head if the remote branch still exists, each either is
contained in the default branch or equals the `headRefOid` of its merged pull
request. Stale status does not depend on which session created the branch.
Find a branch's worktree by the `branch` line of `git worktree list
--porcelain`, since a worktree's directory name can differ from its branch.

Delete without asking only a stale branch that no linked worktree has checked
out and no other local branch tracks as upstream. Its commits exist on the
default branch or in its merged pull request, so nothing is lost. Delete
stacked branches child first.

Every other branch the session left behind is a loose end, and so is every
linked worktree, however clean it looks: Git settings and index flags can hide
a worktree's files from `git status`. When asking about one, name what
deleting it would lose:

- its unique commits;
- every path `git status --porcelain --ignored --untracked-files=all` lists
  in its worktree, ignored files such as `.env` included;
- every path whose `git ls-files -v` tag is not `H`, such as `h` for
  assume-unchanged or `S` for skip-worktree;
- the herdr pane whose cwd is inside the worktree (`herdr pane list`).

To delete a branch, whether asked or not: if the user chose to delete its
worktree, first run `git worktree remove --force <path>`. Then run
`git branch -D`, and delete the remote branch when one still exists, leased to the remote head you
checked: `git push --force-with-lease=<branch>:<sha> origin :<branch>`. Run
`git worktree prune` for worktrees whose directory is gone.

### Deciding

Sort each remaining loose end into the first tier that fits, so the user
answers only what needs their judgment:

1. **Clean up without asking** what the session started and nothing else
   uses: its scratch directories, temporary files, background processes,
   local servers, and `tailscale serve` entries.
2. **File an issue without asking** for follow-up work that could hide a
   defect: a failure found on the default branch, or a check reported as
   skipped or not verified on shipped code. This holds even when the user
   moved past an offer to fix or file it. File it in the repository's issue
   tracker per its `AGENTS.md`, with redacted credentials and personal data.
   Drop a skipped check whose worst case is cosmetic and already visible to
   the user.
3. **Drop without asking** any other offer or question the user moved past.
   Their next request answered it.
4. **Ask** about everything else: every branch other than a stale one,
   every linked worktree, every open pull request, and uncommitted changes.
   A wrong call on these loses work or changes what others see.

Ask in one batch through native structured input (`AskUserQuestion` in
Claude Code, `request_user_input` in Codex). Offer the choices that fit each
one, such as finishing it now, filing an issue, keeping or deleting an
artifact, or leaving it. A worktree another pane is in stays until that
pane's session settles itself, so offer only waiting or leaving it. Do what
the user picks, then run the checks again. This step is done when the session
is settled.

## 3. File the lessons

A **lesson** is something from the session that would change what a future
session does or knows: a decision and its reason, a gotcha, a working recipe,
a fact that took real digging to find. Work that a repository, its history, an
issue, or a pull request already records is not a lesson.

Keep a lesson only when rediscovering it would cost a future session real
time: it took digging, a wrong turn, or a correction from the user. Drop the
rest without asking. When no lesson is kept, write nothing and say so in one
line.

Otherwise, read `~/ghq/github.com/wkentaro/secondbrain/AGENTS.md` and search
secondbrain for the page each lesson belongs on. Cross-project tool lessons
usually belong on a page under `references/tools/`. Write every kept lesson
without asking: update the existing page in place, or create one per the
target domain's `AGENTS.md`. Redact credentials and personal data the lesson
does not need. Commit and push to `main`, confirm the push succeeded, and
list each lesson with its page in one line.

Ask before acting on a lesson that would create or change a skill, an
`AGENTS.md`, or a `CLAUDE.md`, since those change what every later session
does. Propose each with its target in one multi-select question, and write
what the user approves.

## 4. Close the pane

Do this last, since it ends the session. When `HERDR_PANE_ID` is set, read the
pane's current tab from `herdr pane get "$HERDR_PANE_ID"`, since
`HERDR_TAB_ID` keeps the tab the pane started in after it moves. Then read
`herdr tab get` for that tab. Run `herdr tab close` on it when its
`pane_count` is 1, and `herdr pane close "$HERDR_PANE_ID"` otherwise. When
`HERDR_PANE_ID` is not set, say that no herdr pane was found and stop.
