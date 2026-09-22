---
name: simplify
description: >-
  Simplify changed code without changing intended behavior. Use for /simplify,
  cleanup focused on reuse, unnecessary complexity, efficiency, or abstraction
  altitude, and report-only simplify reviews inside review-fix.
---

# Simplify

Improve the quality of changed code without hunting for correctness bugs:

```text
/simplify [target]
```

Use the supplied target when present. Otherwise review the current working-tree
and branch diff against its base. Keep the work inside the changed code's
footprint except when an existing repository helper is the simpler replacement.

The normal mode applies verified cleanups. When a parent workflow or caller sets
a report-only boundary, use Report-only mode and leave the target unchanged.

## Review the change

Read the complete diff, its callers, relevant repository instructions, and the
tests or docs that establish intended behavior. Then assign one fresh,
report-only Reviewer to each angle. Run them concurrently where capacity allows
and serialize only as needed; capacity never removes an angle.

| Angle | Review criterion |
| --- | --- |
| Reuse | Replace new duplication with an existing helper, utility, type, or installed dependency when that is clearer and preserves behavior. |
| Simplification | Remove redundant or derivable state, needless branches or nesting, copy-paste variation, indirection, and dead code introduced or exposed by the change. |
| Efficiency | Remove demonstrated repeated work, unnecessary I/O, allocation, or overly broad operations; omit speculative micro-optimization. |
| Altitude | Keep policy, orchestration, and low-level mechanics at their appropriate existing boundaries; remove leaky or pass-through abstractions instead of adding new layers. |

Each Reviewer returns only findings with a location, one-line claim, concrete
cost, evidence, and smallest behavior-preserving remedy, or `No findings.` A
Reviewer does not edit, commit, publish, or delegate.

## Synthesize

Deduplicate findings that name the same mechanism and verify each against the
source and intended behavior. Keep a finding only when its cost is concrete, its
remedy stays in scope, and intended behavior remains unchanged. Reject false
positives, style-only churn, speculative flexibility, and remedies that require
broad adjacent refactors.

Treat a suspected correctness bug as out of scope for this skill and recommend
`code-review`; do not disguise it as cleanup.

## Report-only mode

Return the verified findings and rejected claims with their reasons. Return
`No findings.` when clean. State that the target was not modified. This mode is
a Composite Review Skill: provenance includes the top-level Simplify Reviewer
and all four angle Reviewers.

## Apply mode

Apply every verified cleanup as the smallest coherent edit. Run the narrowest
relevant tests, lint, and type checks, plus a direct check of any changed output
surface. Retain an edit only when the checks pass and intended behavior is still
demonstrably unchanged.

Finish with a brief list of fixes, skipped findings with reasons, and checks, or
confirm that the code was already clean. Leave history and publication to the
caller: do not commit, rebase, comment, or push.
