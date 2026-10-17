---
name: ambitious-prompt
description: Rewrite a prompt to ask for more altitude, depth, and range, following Felix Rieseberg's "How to be more ambitious".
disable-model-invocation: true
argument-hint: "<prompt to polish>"
---

# Ambitious prompt

Rewrite the prompt in the argument so the model aims at the real outcome, works the
way the best people in the field work, and draws on more fields than the task shows at
the surface. If there is no argument, use the prompt the user most recently wrote or
quoted in the conversation.

Aim for a **deeper** prompt. Every addition must change what gets done or how the
result is checked. Wording that only makes the prompt sound expert is filler.

## Steps

1. **Read the task.** Name the deliverable the prompt asks for and the material it
   supplies. Use the conversation and the working directory to learn what data, tools,
   and access actually exist. Done when you can say what the prompt produces and what
   it starts from.

2. **Altitude.** Ask what the user wants to happen after the deliverable, the goal
   beyond the goal. Climb one or two rungs. Stop at the rung the model can still own and
   verify with the access it has. "Fix this crash" climbs to "keep the app crash-free",
   not to "grow the business". Altitude fits work that ends in a decision or an
   outcome, such as anything that will be discussed in a meeting. For creative or
   one-off craft work, keep the original altitude and say so. Done when the prompt
   names the outcome, or you have stated why the original altitude is right.

3. **Depth.** Answer each question for this task:
   1. What would a top professional in the field do here that the prompt leaves out?
   2. What is the rawest material they would start from, instead of what has already
      been digested? (Raw logs, not a summary. The database, not the dashboard.)
   3. Which specific methods and tools would they use? Name them, for example "a
      survival model in DuckDB" instead of "analyze it".
   4. Which belief behind the task should be checked against that raw material?
   5. What new knowledge could the work produce while it is in there, such as an
      earlier signal or a blind spot, and how would held-out data confirm it?

   Raise any numeric target to one that feels unreasonable, and state it as reachable.
   Done when each question has a concrete answer or you have marked it not applicable.

4. **Range.** Restate the deliverable's noun as verbs. A QBR deck becomes "getting
   busy people to believe a story about cause and effect and decide under uncertainty
   in 30 minutes". Pick the two to four fields those verbs call for, including one
   adversarial field (a short seller, a forensic accountant, a security auditor, a
   hostile reviewer). For each field, write what its practitioners **do**: the
   technique or tool they bring. Leave out any instruction to write or speak like
   them. Done when each chosen field contributes a technique that appears in the
   rewritten prompt.

5. **Outside judge.** Name what, other than the model or the user, will show the
   result is right: a test, a benchmark, a backtest, a reproduction, a measurement, a
   third-party source. Prefer one the model can run itself for fast feedback. Done when
   the rewritten prompt names that judge and the pass condition.

6. **Access.** List what the model needs to do the rewritten prompt: data sources,
   connectors, machines, permission to install software. Done when every input or tool
   the rewritten prompt mentions is either available or listed under setup.

## Output

Reply with:

1. **The rewritten prompt** in one fenced block, ready to paste. Write it in the
   user's language and voice, as instructions to the model, with the outcome first.
2. **What changed**, one line per axis (altitude, depth, range, judge). Mark an axis
   `unchanged` with a short reason when it did not apply.
3. **Setup**, the access from step 6 that the user must provide. Leave this section
   out when nothing is missing.
