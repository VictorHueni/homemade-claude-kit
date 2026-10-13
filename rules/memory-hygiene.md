---
type: rule
---

# Memory hygiene: classify a lesson before saving it

Before writing any auto-memory file under `~/.claude/projects/<project>/memory/`, decide where the lesson belongs. The default failure is writing a cross-project lesson into per-project memory, where it only fires for one repo.

1. **Would it apply to any future project?** (framework patterns, git and tool discipline, naming, working style, diagramming, language-agnostic gotchas)
   → Write it as a rule in the **kit repo** (the checkout `install.sh` runs from): `rules/<topic>.md` for shared engineering knowledge, `rules/personal/<topic>.md` for the owner's own preferences or this machine's setup. Give it `type: rule` frontmatter and `paths:` when it only matters for certain files. Commit it on a branch, then run `install.sh` to link it.
   → Never write a plain file into `~/.claude/rules/`: that directory holds only links the installer manages, and a plain file there exists on one machine and in no repo.
2. **Is it a team standard for the current repo?** (branch protection quirks, CI gotchas, repo conventions a new collaborator needs on day one)
   → Add it to the project's `AGENTS.md` (or a nested one for the area it concerns), so it lives in source control.
3. **Does it only make sense next to a specific symbol, path or schema in this codebase, and is it something Claude learned rather than a team rule?**
   → Then, and only then, write it to the project auto-memory.

**When in doubt, prefer the wider scope.** A rule that occasionally fires on an irrelevant project is harmless; a cross-project lesson trapped in one project's memory is relearned everywhere else.

**Keep kit rules generic.** They reach every project and, for shared rules, every teammate: no client or product names, no project-bound paths, no domain jargon as examples. The project's own memory can stay specific.
