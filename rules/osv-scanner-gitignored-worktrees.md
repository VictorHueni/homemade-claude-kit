---
type: rule
---

# osv-scanner finds nothing inside a gitignored checkout

osv-scanner honours the enclosing repository's `.gitignore`, so a worktree or checkout that sits in a parent repo's ignored folder scans nothing and fails with `No package sources found` (exit 128). It is not a lockfile problem. Tell: `git -C <parent> check-ignore -q <path>` succeeds. Pass `--no-ignore`, or keep worktrees outside the parent repository.
