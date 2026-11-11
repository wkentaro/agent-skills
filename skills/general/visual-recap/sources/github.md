# GitHub

With `gh` signed in as the user, read the period as a `<start>..<end>` date range:

```sh
gh search prs --author @me --merged-at <start>..<end> --json repository,number,title,url -L 1000
gh search prs --author @me --created <start>..<end> --state open --json repository,number,title,url -L 1000
gh search prs --reviewed-by @me --merged-at <start>..<end> --json repository,number,title,url,author -L 1000
gh release list -R <owner/repo> -L 1000 --json tagName,publishedAt   # for each repository above
```

Search returns at most 1,000 results: when a search returns that many, split the period in halves and search each. Keep only releases whose `publishedAt` falls inside the period.

Group PRs by repository, and repositories by the project they serve. A PR merged from someone else after your review counts toward your project, credited to its author. Link a group by its search, such as `https://github.com/<owner/repo>/pulls?q=is%3Apr+merged%3A<start>..<end>`.

Numbers such as benchmarks come from the repository's docs or the PR body; open them before you use them.
