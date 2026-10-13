---
type: rule
---

# Git discipline

**Never `git commit --amend`** (in Claude Code the kit-core tripwire hook blocks it); make a new commit.

**Commit and PR-title scope names a capability, not a work item.** Use the plan's declared `Commit scope:` if any, else a product or capability slug from the project's capability map, else the area or module (`auth`, `api`, `deps`). Never a bare plan or ticket number (`feat(0121): …`); put it in a `Refs:` trailer. A squash merge uses the PR title as the commit subject, so the PR title follows the same rule.

**Branch names say what the change does:** `<type>/<explicit-slug>`, such as `fix/osv-scanner-gitignored-worktrees`. Never name a branch only after a plan, increment or milestone number (`feat/0121-inc03`, `m02-merge`); a number may follow the descriptive slug, never replace it.
