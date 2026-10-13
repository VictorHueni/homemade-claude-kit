---
type: rule
---

# Bulk `gh issue transfer`: the sub-issue moved right before its parent loses its link

Transferring issues between repos of the same owner preserves comments, assignees, Projects v2 membership (item and field values intact), same-name labels (create them in the target FIRST — missing labels are silently dropped), and sub-issue parent links — cross-repo parent links work under the same owner. GitHub's docs are silent on projects and sub-issues; this was verified empirically (2026-09-01, 109 issues, 12 epics).

**The trap:** in a sequential loop that transfers an epic's sub-issues and then the epic, the sub-issue transferred *immediately before* the epic loses its parent link — a server-side race, reproduced on 10 of 12 epics. Every other sub-issue keeps its link.

**How to apply:** keep an old→new mapping file (epic, old number, new URL) as you go; after the loop, walk it and re-attach any sub whose `parent` is null via the `addSubIssue` GraphQL mutation; then verify each migrated epic's `subIssues.totalCount` against the pre-migration count and that no sub-issue sits in a foreign repo. Do a one-issue canary first to confirm labels/project/parent survive in the specific setup. Old issue URLs redirect after transfer, so existing doc links keep resolving.
