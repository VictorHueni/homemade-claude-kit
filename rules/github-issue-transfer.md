---
type: rule
---

# Bulk `gh issue transfer` loses one parent link per epic

Between repos of the same owner, a transfer keeps comments, assignees, Projects v2 items and their field values, same-name labels and sub-issue links, and old URLs redirect. The exception: the sub-issue transferred just before its parent epic loses its parent link. Create the target's labels first (missing ones are dropped), transfer one issue as a canary, keep an old-to-new map, then re-attach any null parent with the `addSubIssue` mutation and check each epic's `subIssues.totalCount` against its count before the move, with no sub-issue left in a foreign repo.
