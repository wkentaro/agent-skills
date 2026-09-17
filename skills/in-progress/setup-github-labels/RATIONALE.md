# Why the label set looks like this

Read this when changing `labels.json`, not when applying it.

## Contents

- Naming rule
- Issue `type:` axis
- Issue triage axis
- Agent PR-verdict axis
- Maintainer PR-verdict axis
- Issue and PR equivalents
- Deliberate omissions

## Naming rule

Prefix encodes the object the label applies to, not the audience:

- `type:*`, `needs-*`, `ready-for-*`, `wontfix` are issue labels.
- `recommend-*` are agent verdicts on a PR.
- `maintainer-approved` is the one PR label outside `recommend-*`, because its
  authority is the human, not the agent.

Lowercase, hyphenated, no spaces. `type:bug` rather than `type: bug` so the
label filters without quoting and matches the other families.

## Issue `type:` axis

`type:bug` / `type:feature` / `type:task` mirror GitHub's native Issue Types
(Bug / Feature / Task), which are org-only. If a repo moves under an org, these
map 1:1 and the labels can be retired. `task` is the catch-all for
refactor/docs/chore/test work and carries real signal: about a quarter of
labelme's issues wear it. GitHub's default `bug` / `enhancement` pair has no home
for that work, which is why the defaults are not reused.

`/triage` emits two category roles, `bug` and `enhancement`. The contract maps
`bug` to `type:bug` and `enhancement` to `type:feature`, with `type:task` when the
request is maintenance, docs, or refactor. The maintainer confirms before any
label is applied, so the many-to-one mapping is safe.

## Issue triage axis

Five whose-turn states that `/triage` moves an issue through. `needs-triage`
means *under evaluation, not yet routed*, which is what Kubernetes and `/triage`
both mean by it: an unlabeled issue is untriaged and gets `needs-triage` first.
An earlier revision reserved `needs-triage` for "maintainer must decide" and
treated unlabeled as "agent routes it"; that inverted the dominant meaning and
contradicted the consumer, so it was dropped.

`needs-info` is issue-only. On a PR, "waiting on reporter" means waiting on the
author, and `recommend-revise` already says that.

## Agent PR-verdict axis

A non-draft PR with no verdict is the agent's to finalize, so routing needs no
label. The axis records the agent's **terminal verdict** after finalizing:

- `recommend-merge`: endorsed, maintainer reviews and merges.
- `recommend-close`: active reject. Broken, abandoned, superseded, or clearly out
  of scope. The maintainer glances and closes.
- `recommend-triage`: code is sound but merge/close is a product or scope call
  the agent cannot make. Not an escape hatch: a *technical* reason not to merge
  is a `recommend-close` with the reason in the review.
- `recommend-revise`: hands the PR back to its **author**. Stands in for GitHub's
  native "changes requested", which is unavailable on a self-authored PR, and
  covers both defects and open questions. The substance goes in review comments;
  the label records whose turn it is.

Folding `recommend-triage` into `recommend-close` would be dishonest (the agent
does not recommend closing a sound feature) and would bury the expensive pile
(product calls) inside the cheap one (rubber-stamp closes). The maintainer's
world is three filters: `label:recommend-merge`, `label:recommend-triage`,
`label:recommend-close`.

The agent never merges and never closes. That is why the family is
`recommend-*` and not the conventional `ready-to-merge`: merge bots (Kodiak,
Mergify, bors, GitHub auto-merge) watch that string, and a bot wired to it would
turn a recommendation into a merge. Do not rename it back.

## Maintainer PR-verdict axis

GitHub prevents authors from approving their own PR. `maintainer-approved` lets a
maintainer record that human decision on a self-authored PR while checks are
pending. It records acceptance, not merge readiness; required checks stay
authoritative and the maintainer still merges. An agent applies it only on
explicit direction and never infers it from a verdict, green CI, or
mergeability. It may coexist with a `recommend-*` label because the two record
different authorities.

Both verdict axes bind to one head. A new push makes the verdict stale; the
authority that set it clears and renews it. Pushes after a verdict are rare, so
this stays manual rather than a CI workflow.

## Issue and PR equivalents

| State                                  | Issue                 | PR                              |
| -------------------------------------- | --------------------- | ------------------------------- |
| Untriaged                              | no triage label       | no verdict label, non-draft     |
| Under evaluation                       | `needs-triage`        | no verdict label, non-draft     |
| Waiting on author                      | `needs-info`          | `recommend-revise`              |
| Still being built                      | *(none)*              | **draft** flag                  |
| Agent's turn                           | `ready-for-agent`     | no verdict label, non-draft     |
| Maintainer's turn, endorsed            | `ready-for-human`     | `recommend-merge`               |
| Maintainer's turn, must decide         | `needs-triage`        | `recommend-triage`              |
| Maintainer accepted, checks pending    | *(none)*              | `maintainer-approved`           |
| Won't proceed                          | `wontfix`             | `recommend-close`               |

Asymmetries are intentional. Untriaged, under evaluation, and agent's turn
collapse into one PR state because a non-draft PR without a verdict already
means "agent, finalize this". `ready-for-human` means *implement it* while
`recommend-merge` means *review and merge it*, so they stay separate labels.

## Deliberate omissions

- **Tool-owned labels** (`dependencies` from Dependabot, labeler output) belong
  to the tool. Do not manage them here or you fight the tool that recreates them.
- **`area:*`** is per-repo, ideally via path-based `actions/labeler`.
- **PR type and area**: type comes from the conventional-commit title; area is
  per-repo. Only the verdict generalizes across repos.
- **`ready-for-review` / `ready-for-maintainer`**: `recommend-merge` already is
  the "your turn to ship" signal and the draft flag already owns "not yet".
- **`do-not-merge`**: a temporary "don't merge yet" is exactly what draft
  expresses, and a draft cannot be merged.
