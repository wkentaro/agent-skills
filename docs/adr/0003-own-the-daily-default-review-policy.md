# Own the daily Default Review Policy

Status: Accepted

Supersedes ADR-0002.

The Default Review Policy contains four report-only Review Requests used in daily work: `code-review`, the repository-owned `simplify`, `improve-codebase-architecture` in diff-bounded Deepening analysis mode, and `ask-exemplar`. This replaces overlapping `brooks-review` and `zero-tech-debt` coverage with one stronger architecture review and drops the retired `writing-code` dependency while keeping host-specific output, interactive grilling, and Reviewer writes outside review-fix.
