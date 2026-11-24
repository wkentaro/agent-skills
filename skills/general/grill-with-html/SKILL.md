---
name: grill-with-html
description: Queue pending questions as decisions with options, a recommendation and evidence on a visual page. Use only when the user names grill-with-html.
---

# Grill with HTML

Turn every unanswered question, whether already in the conversation or one you are about
to ask, and every assumption you are about to act on, into a **decision**, then put the
decisions to the user on one **page** and work through them in **rounds**.

## Assumption audit

Before each round, write down what you will do once the user answers, step by step, and
every choice inside it you would otherwise make silently: how an edge case behaves, what
stays unfixed or unfiled, what ships before what, what you will report and to whom.
Each one that changes what the user gets, risks or is told becomes a decision; a routine
choice of how to do the work, such as which check runs first, does not. The audit is
done when every step follows from a settled decision, a stated rule or a fact, or waits
on a decision in this round or a later one.

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
- **Visual**: a drawing of what each option produces, so the user answers by picking a
  picture rather than by reading. Every option gets its own `html` or `image` picture,
  such as a screen, a timeline of a count, or a flow of the steps that follow; text and
  diff only add to them. A policy call still gets a picture of where each option leads.
  Draw from the real code, data or output, not from your summary of it. When drawing
  shows a claim of yours is wrong, correct the claim and its evidence.
  When a sequence decides the choice, such as how an interaction feels or how a state
  model handles a tricky order of events, build a walkthrough with the `prototype` skill
  and keep one static picture per option beside it, so the user can still pick by
  picture.
- **Danger**: the door (`two-way` when the choice can be undone, `one-way` when it cannot)
  and the blast radius in a few words.
- **Draft**: the exact text that will be posted or sent if the user accepts, when there is one.

Facts are your job. Look up, run, or dispatch a subagent for anything the environment can
answer, and bring the result as evidence. Only what the user must judge becomes a decision.

Ask the frontier: every decision whose prerequisites are already settled, with no cap on
how many. A decision that depends on an open one waits for a later round.

Order decisions with the ones an agent is blocked on first, then by group.

## Page

Put each round on one self-contained HTML page. Follow [PAGE.md](PAGE.md) for the queue
file, the visuals, the build command and how answers come back.

## Rounds

The user may answer only some decisions. After each set of answers:

1. Run the assumption audit on the answers: the choices, every edited draft and every
   note. A note narrows or withdraws any action it speaks to, whatever item it is on. A
   choice or draft that leaves a silent choice, such as a placeholder or a detail the
   user never picked, becomes a decision.
2. Gate every action, approved this round or held from an earlier one. Run it only when
   it follows from the user's answers, a stated rule or a verified fact, such as the
   result of an action it needs. A choice approves that decision's draft and action,
   including an edited draft. Otherwise hold it until it does; drop it when the answers
   or a result rule it out, and ask again when they change it.
3. Reply to every note that came without a choice. It is a question or a steer: answer
   it with new evidence, or reshape the decision and its options.
4. Recompute the frontier and ask the next round: the decisions still open, the ones
   reshaped by a note, the ones the answers unblocked, and the ones the audit found. When
   none remain, skip the page and report each held action and what would let it run.

The work is done when every decision is settled and every approved action has run, been
dropped, or been reported as waiting on something outside the user's answers, or when the
user says to stop. When neither
an unanswered question nor an assumption from the audit exists at the start, say so and
stop.
