---
name: setup-github-labels
description: Apply and document the canonical GitHub issue and pull-request label set in a repository.
disable-model-invocation: true
---

# Setup GitHub Labels

Apply one label vocabulary to the repo you run this in, then record its meaning
for agents. `labels.json` in this skill directory is the single source of truth:
every label's name, color, description, scope, and the name it was renamed
from. Read [RATIONALE.md](RATIONALE.md) only when changing the set.

The set has four groups. Prefix encodes the object a label applies to:

| Group                  | Labels                                                                             |
| ---------------------- | ---------------------------------------------------------------------------------- |
| Issue type             | `type:bug`, `type:feature`, `type:task`                                            |
| Issue triage state     | `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`      |
| Agent PR verdict       | `recommend-merge`, `recommend-close`, `recommend-triage`, `recommend-revise`       |
| Maintainer PR verdict  | `maintainer-approved`                                                              |

Rules the labels encode:

- A triaged issue carries exactly one `type:` label and one triage state. An
  unlabeled issue is untriaged; `needs-triage` means under evaluation.
- A non-draft PR with no verdict is the agent's to finalize. The draft flag is
  the "still being built" state; there is no label for it.
- The agent emits at most one `recommend-*` verdict per head. `recommend-revise`
  hands the PR back to its author; the other three hand it to the maintainer.
- Verdicts are recommendations. The agent never merges and never closes. Never
  rename `recommend-merge` to `ready-to-merge`: merge bots watch that string.
- `maintainer-approved` is set only on explicit maintainer direction and may
  coexist with a `recommend-*` label.
- A new push makes any verdict stale. The authority that set it clears and
  renews it.

## Process

### 1. Detect the repo

```bash
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
```

If that fails, ask the user which repo to target.

### 2. Preview

Compare the manifest against the repo and show the user what will happen:

```bash
gh label list --repo "$REPO" --limit 200 --json name -q '.[].name' | sort > /tmp/have
jq -r '.[].name' labels.json | sort > /tmp/want
jq -r '.[] | select(.renamed_from) | .renamed_from' labels.json | sort > /tmp/old
comm -13 /tmp/have /tmp/want   # will be created (or renamed into, if the old name is present)
comm -12 /tmp/have /tmp/want   # will have color/description updated
comm -12 /tmp/have /tmp/old    # will be renamed
```

Also inspect `docs/agents/triage-labels.md` and the root `AGENTS.md`, and say
whether each will be created, updated, or left alone. End the preview with an
explicit question asking the user whether to apply it.

### 3. Confirm, then apply

Creating labels on an often-public repo is outward-facing: confirm the full
preview with the user first. Then run the manifest. Renames go first so issue
history follows the label; `--force` then creates or updates in place.

```bash
jq -c '.[]' labels.json | while read -r label; do
  name=$(jq -r .name <<<"$label")
  old=$(jq -r '.renamed_from // empty' <<<"$label")
  if [ -n "$old" ] && [ "$old" != "$name" ]; then
    gh label edit "$old" --name "$name" --repo "$REPO" 2>/dev/null || true
  fi
  gh label create "$name" \
    --color "$(jq -r .color <<<"$label")" \
    --description "$(jq -r .scope <<<"$label"): $(jq -r .description <<<"$label")" \
    --force --repo "$REPO"
done
```

Repeat with another `$REPO` to set up several repos.

### 4. Document the contract

Create or update `docs/agents/triage-labels.md`. It is the adapter that
`/triage` and the PR skills read to turn role names into label strings, so it
must contain:

- a table with one row per `/triage` role (`bug`, `enhancement`, `needs-triage`,
  `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) and two label
  columns, one for an issue and one for a PR, following the mapping in
  [RATIONALE.md](RATIONALE.md);
- the rules listed at the top of this file;
- any repository-specific labels or overrides already in the file, preserved.

Then make sure the root `AGENTS.md` points at that file wherever it mentions
issue triage or PR verdicts. Add the smallest pointer; do not copy the contract.

### 5. Report

Report three buckets, renamed, updated, and created, naming the labels in each
and writing "none" for an empty bucket, then which docs were created or updated.
Labels on the repo that are not in the manifest are left alone. If the
user wants one removed, that is a deliberate step, since deletion strips the
label from every issue and PR:

```bash
gh label delete "<name>" --repo "$REPO" --yes
```

## Changing the set

Edit `labels.json`. To rename a label, change `name` and set `renamed_from` to
the old string; drop `renamed_from` once every repo has been migrated. Keep the
set small: a new label must carry information the title, the diff, or an existing
label does not. Record the reasoning in [RATIONALE.md](RATIONALE.md) and update
the contract template in step 4 if a role mapping changes.
