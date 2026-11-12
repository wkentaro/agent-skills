# Poleway

With the Poleway MCP, call `listLogbook` with `since` at the period's start, `until` at its end, and `everyComment: true`, paging with `after` while `hasMore` is true. It lists each checked or cancelled Task, each finished Project, and every Comment, with the Project and Area each belongs to.

- Comments are the owner's own account of the work and carry the links; checked Tasks show what finished.
- Group by Project. A loose Task groups under its Area.
- Areas are how the owner separates work from personal life: leave out the personal ones (health, family, home) unless asked.
