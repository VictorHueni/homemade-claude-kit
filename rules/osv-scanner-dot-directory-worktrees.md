---
type: rule
---

# osv-scanner finds nothing when the checkout path contains a dot-directory

osv-scanner (2.3.8) prunes hidden directories while walking, and it applies the prune to the scan root's own path components. A checkout that lives under a dot-directory, such as a git worktree at `<repo>/.worktrees/<slug>`, therefore scans one directory and fails with `No package sources found` (exit 128). The same binary on the same tree reached through a non-hidden path (a symlink outside any dot-directory) walks the whole tree and passes. Reported by an iteration agent on 2026-09-10; `realpath` on the scan root does not help because the resolved path still contains the dot-directory.

**How to apply:** when a local CI gate that wraps osv-scanner goes red on `No package sources found` from a worktree, check whether the worktree path contains a `.something/` component before debugging lockfiles. Run that one block through a symlink placed outside any dot-directory, or keep worktrees in a non-hidden sibling directory. Do not treat the failure as a dependency problem; the scanner never opened a manifest.

**Why:** the error text names package sources, which sends you to the lockfiles, while every other block of the same gate passes from the same path. The failure is a path-shape artefact of the scanner's walker, not a property of the project.
