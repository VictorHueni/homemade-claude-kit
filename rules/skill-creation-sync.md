---
type: rule
paths:
  - "plugins/**/skills/**"
  - ".claude/skills/**"
---

# Authoring skills

A skill meant for every project belongs in the kit, not a project's `.claude/skills/` or `~/.claude/skills/`: author it under `plugins/<set>/skills/` in the kit, a sibling of the current repo (`"$(dirname "$(git rev-parse --show-toplevel)")/homemade-claude-kit"`), and run `install.sh`. In the kit repo, load its `util-skill-authoring` skill before creating, renaming or restructuring a skill, or changing a doc-producing skill's output path, IDs or prerequisites.

On every skill edit:

- Folder name equals `name:`; kit skills follow `<category>-<artifact-singular>[-<verb>]`.
- `description` stays under 1024 characters (Codex skips longer ones) and says when to use the skill and what it is not for.
- Loader fields (`name`, `description`, `allowed-tools`, `user-invocable`, `disable-model-invocation`) stay top-level; kit governance fields (`version`, `status`, `last_reviewed`, …) sit under `metadata`.
- `allowed-tools` only for a bounded pattern (the skill's own scripts, a read-only call), never bare `Bash` or a wildcard over a side-effecting command. `disable-model-invocation: true` on any skill with side effects (commit, PR, autonomous loop).
- No client, product or project names in a kit skill; examples use placeholders.
- Bump the set's `.claude-plugin/plugin.json` version in the same commit, or the plugin cache never updates.
