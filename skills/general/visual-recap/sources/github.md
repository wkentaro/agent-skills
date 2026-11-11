# GitHub

With `gh` signed in as the user, read the period as a `<start>..<end>` range of timestamps with the user's UTC offset, such as `2026-11-11T00:00:00+09:00..2026-11-11T23:59:59+09:00`. A bare date reads as UTC and shifts the day.

```sh
gh search prs --author @me --merged-at <start>..<end> --json repository,number,title,url -L 1000
gh search prs --author @me --created <start>..<end> --json repository,number,title,url,state,closedAt -L 1000
gh search prs --reviewed-by @me --merged-at <start>..<end> --json repository,number,title,url,author -L 1000
gh release list -R <owner/repo> -L 1000 --json tagName,publishedAt   # for each repository above
```

Search returns at most 1,000 results: when a search returns that many, split the period in halves and search each. Keep only releases whose `publishedAt` falls inside the period. A PR created in the period is still open at its end unless it closed or merged before `<end>`.

Group PRs by repository, and repositories by the project they serve. A PR merged from someone else after your review counts toward your project, credited to its author. Link a group by its search, such as `https://github.com/<owner/repo>/pulls?q=is%3Apr+merged%3A<start>..<end>`, with the `+` in the offset written as `%2B`.

Numbers such as benchmarks come from the repository's docs or the PR body; open them before you use them.
