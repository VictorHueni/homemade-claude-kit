---
type: rule
---

# Memory hygiene: classify a lesson before saving it

Before writing any file under `~/.claude/projects/<project>/memory/`, decide where the lesson belongs:

1. **It applies to any future project** (tool gotchas, conventions, working style): write a rule in the kit repo (the checkout `install.sh` runs from), `rules/` for shared knowledge or `rules/personal/` for the owner's preferences and machine, with `type: rule` and `paths:` when only certain files need it. Commit it on a branch and run `install.sh`. Never write a plain file into `~/.claude/rules/`: it would exist on one machine only.
2. **A collaborator on this repo needs it on day one:** the project's `AGENTS.md`, or the nested one for that area.
3. **Only otherwise**, a fact Claude learned about this codebase: project auto-memory.

When in doubt, choose the wider scope. Kit rules reach every project and teammate, so they stay generic: no client, product or project names, no project paths, no domain jargon in examples.
