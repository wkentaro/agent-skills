# PR evidence

Assess the actual base-to-head diff and existing evidence. Choose the smallest demonstration that helps a reviewer verify behavior beyond what the diff and tests already explain: screenshots for appearance, recordings for interaction, or before/after text for CLI or backend behavior. New behavior can use an after-only Preview.

Reuse published evidence after checking that it still proves the current change; verify its existing presentation without recapturing or re-uploading. If evidence adds nothing, intentionally skip it with a brief reason, removing any stale marked block while preserving unrelated prose. An intentional skip satisfies the evidence gate. Unavailable tooling or failed capture, upload, or verification is a failure, not a skip.

## Screenshots and recordings

Use the existing `before-and-after` skill to obtain missing media and publish it. Give it the existing PR, base and head revisions, the affected UI and comparable state, and any existing captures. Follow its installed capture and attachment instructions; capture delegates to `agent-browser` and uploads use `gh --attach`. Keep media out of commits and sensitive files out of uploads.

## Text evidence

Run the project's existing commands at the base and head revisions with comparable inputs, or reuse supplied observations verified against those revisions. Write labeled Before and After fenced code blocks, or a single Preview for new behavior, between `<!-- before-and-after:start -->` and `<!-- before-and-after:end -->`. Include the command or input and the observed output; redact credentials and unnecessary personal information. Use ordinary Markdown without invoking `before-and-after` or its media formatter.

Read the current PR body and replace only the marked evidence block. Place new evidence after the opening context and any Preview or deployment link, before implementation details. Preserve unrelated prose and complete Markdown structures; append if no safe anchor exists. Publish with `gh pr edit --body-file`, without attachment flags.

## Verify and recover

Inspect the fetched PR body and rendered evidence yourself before making the readiness decision; a successful command or another skill's completion message is insufficient. Confirm the evidence matches the current change, text and media render in the intended order, videos are playable, and no local attachment references remain.

If an attachment command exits nonzero, successful uploads and PR changes may already have landed. Resolve the PR from stdout or the current branch, fetch its body, and retry only missing files with `gh pr edit --attach`. Preserve successful attachment URLs; never rerun PR creation or re-upload files that already succeeded. Recheck the body after a failed retry, since that attempt may also have partially succeeded.

If recovery cannot produce verified evidence, leave the PR draft and report its URL, missing evidence, blocker, and last successful phase. PR creation and readiness stay in `sending-pull-request`; this workflow requires no status-return protocol from `before-and-after`.
