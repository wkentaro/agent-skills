---
name: grill-with-html
description: Grill a plan or a set of pending questions into a design tree and ask it in rounds on a visual page, each decision with options, a recommendation, evidence and a picture of what each option produces. Use only when the user names grill-with-html.
---

# Grill with HTML

Take a plan, an idea, or the unanswered questions already in the conversation, and map
it as a **design tree**: every decision branches into the decisions that hang off it.
Put the tree to the user on one **page** per **round**, and grill until the tree has no
open branch.

## Design tree

Walk the plan and write down every choice it makes or leaves open, including the ones it
silently assumes. Each choice is a **decision**. A decision that only makes sense once
another is settled is **blocked by** it.

The **frontier** is every open decision whose blockers are all settled. A fact still being
found is a blocker too. Ask the whole frontier each round. A decision blocked by an open
one waits for a later round. When the frontier is empty and facts are still pending, build
no page: tell the user which facts you are waiting for. When they return, recompute the
frontier and ask it without waiting for another answer.

Order the frontier with the decisions an agent is blocked on first, then by group.

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
- **Visual**: a picture of what each option produces, so the user answers by picking a
  picture rather than by reading. Every decision gets its own, chosen by what that
  decision is about:

  | The question is about | Show |
  | --- | --- |
  | how something looks | one mock or screenshot per option, bound to that option |
  | how something behaves over a sequence of steps | a demo built with the `prototype` skill's LOGIC branch, as one interactive visual where the user runs the same steps under each of that decision's options |
  | what depends on what | a drawing of the dependency in inline SVG |
  | how big or how often | a chart, following the `dataviz` skill when it is installed |
  | how parts connect, such as a data flow or a layout | a drawing in inline SVG |
  | a policy with nothing to show | the text each option would put in place, one plain-text visual per option |

- **Danger**: the door (`two-way` when the choice can be undone, `one-way` when it cannot)
  and the blast radius in a few words.
- **Draft**: the exact text that will be posted or sent if the user accepts, when there is one.

Facts are your job. Look up, run, or dispatch a subagent for anything the environment can
answer, and bring the result as evidence. Only what the user must judge becomes a
decision. A question the plan's own words answer is a fact too: state your reading as
evidence instead of asking it.

## Page

Put each round on one self-contained HTML page. Follow [PAGE.md](PAGE.md) for the queue
file, the visuals, the build command and how answers come back.

## Rounds

The user may answer only some decisions. After each set of answers:

1. Carry out every choice that is an action of its own, such as posting a draft or
   closing an issue. The choice approves that action and its draft, including an edited
   draft. Building the plan itself waits for the end.
2. Reply to every note that came without a choice. It is a question or a steer: answer
   it with new evidence, or reshape the decision and its options.
3. Update the tree. A choice can settle, add, or remove the branches below it.
4. Recompute the frontier and ask the next round: the decisions still open, the ones
   reshaped by a note, and the ones the answers unblocked.

The grilling is done when every decision is settled or the user says to stop. A decision
waiting for a later round or for a fact is not settled. Then state the settled plan in a
few lines and wait for the user to confirm it before you build on it.
When the input has no open decision at the start, say so and stop.
