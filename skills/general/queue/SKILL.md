---
name: queue
description: Queue pending questions as decisions with options, a recommendation and evidence on a visual page. Use only when the user names queue.
---

# Queue

Turn every unanswered question, whether already in the conversation or one you are about
to ask, into a **decision**, then put the
decisions to the user on one **page** and work through them in **rounds**.

## Decision

A decision is a question the user can settle in one read. Each carries:

- **Title**: the question or the proposed action, in one line.
- **Summary**: what is being decided and why it came up, in one or two short paragraphs.
- **Evidence**: one line per fact, each tagged with how you know it and linked to its
  source (issue, PR, commit, file line, test, log):
  - `ran`: you executed it this session.
  - `seen`: you observed it in the running app or its output.
  - `read`: you read the source or document yourself.
  - `reported`: a subagent or another tool said so and you did not re-check it.
  - `claimed`: a person's statement, such as an issue thread or a PR description.
- **Options**: two to four mutually exclusive choices, each with its consequence in one
  sentence. Mark the one you recommend. Leave all unmarked only when the choice is taste.
- **Visual**: what each option produces, so the user answers by picking a picture rather
  than by reading. When options differ in what the user would see or experience, give
  each its own visual. A pure policy call with nothing to show still gets one plain-text
  visual. When a static visual cannot settle the choice, such as how an interaction
  feels or how a state model handles a tricky sequence, build it with the `prototype`
  skill.
- **Danger**: the door (`two-way` when the choice can be undone, `one-way` when it cannot)
  and the blast radius in a few words.
- **Draft**: the exact text that will be posted or sent if the user accepts, when there is one.

Facts are your job. Look up, run, or dispatch a subagent for anything the environment can
answer, and bring the result as evidence. Only what the user must judge becomes a decision.

Ask the frontier: the decisions whose prerequisites are already settled. A decision that
depends on an open one waits for a later round.

Order decisions with the ones an agent is blocked on first, then by group.

## Page

Put each round on one self-contained HTML page. Follow [PAGE.md](PAGE.md) for the queue
file, the visuals, the build command and how answers come back.

## Rounds

The user may answer only some decisions. After each set of answers:

1. Act on every decision that has a choice. A choice the user made approves that
   decision's draft and action, including an edited draft.
2. Reply to every note that came without a choice. It is a question or a steer: answer
   it with new evidence, or reshape the decision and its options.
3. Recompute the frontier and ask the next round: the decisions still open, the ones
   reshaped by a note, and the ones the answers unblocked.

The work is done when every decision is settled or the user says to stop. When no
unanswered question exists at the start, say so and stop.
