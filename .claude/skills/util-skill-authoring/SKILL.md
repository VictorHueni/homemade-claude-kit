---
name: util-skill-authoring
description: "Create, rename or change a skill in this kit: where it lives, its folder structure, SKILL.md frontmatter, output conventions, the naming convention, the metamodel impact assessment, and how to publish and install it. Use before adding a skill under plugins/*/skills/, renaming one, adding a frontmatter field, or changing a doc-producing skill's output path or IDs. Triggers on: new skill, create a skill, rename a skill, skill naming, skill frontmatter, publish a skill, metamodel impact."
user-invocable: true
---

# Authoring a kit skill

## Where skills live

`plugins/<set>/skills/<skill-name>/SKILL.md`, in one of the plugin sets (ADR-0006): `kit-core`, `strategy`, `domain-modeling`, `product-spec`, `quality-assurance`, `architecture`, `dev-flow`, `agent-loop`, `delivery-comms`, `ops`, `docs-hygiene`. Skill names are unique across all sets, because `install.sh` flattens them into one directory per harness.

```
plugins/<set>/skills/<skill-name>/
  SKILL.md       # required: frontmatter + instructions
  references/    # optional: loaded on demand
  scripts/       # optional: runtime helpers
  templates/     # optional: output skeletons
```

Before naming it, read `references/naming.md`. Before designing a doc-producing skill or changing one's output path, IDs or prerequisites, run `references/metamodel-impact.md`.

## SKILL.md frontmatter

```yaml
---
name: skill-name-kebab      # equals the folder name
license: MIT                # matches the repo LICENSE
description: "What it does, when to use it. Triggers on: phrase1, phrase2."
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/foo.sh *)   # optional
disable-model-invocation: true                              # optional
user-invocable: true
metadata:
  category: "specification"
  complexity: "medium"
  version: "1.0.0"
  status: active            # draft | active | deprecated | superseded
  last_reviewed: YYYY-MM-DD
  review_interval: 180d
  impact: "low"
---
```

- **Top level** holds only fields a skill loader reads (`name`, `description`, `license`, `user-invocable`, `allowed-tools`, `disable-model-invocation`). Claude Code looks for them there; nested, they silently stop working.
- **`metadata`** holds the kit's governance fields. Only `scripts/audit-skills.sh` and the `metamodel` skill read them, and the Agent Skills standard scopes custom keys there.
- **`description`**: Codex skips a skill whose description exceeds 1024 characters. Keep it to what, when, and a `Triggers on:` list; put methodology in the body. It also carries routing: say what the skill is NOT for when a neighbour covers it. Check: `ruby -e 'require "yaml"; d = YAML.load_file("SKILL.md")["description"]; puts d.length; abort("too long") if d.length > 1024'`.
- **`allowed-tools`** pre-approves calls for the turn that invokes the skill; it restricts nothing. Grant only a bounded pattern: the skill's own `${CLAUDE_SKILL_DIR}/scripts/*` or a read-only call the body documents. Never bare `Bash` or a wildcard over a side-effecting command (`git commit`, `git push`, `gh pr create`, `terraform apply`) unless that one action is the skill's whole purpose, and then scoped to the exact subcommand.
- **`disable-model-invocation: true`** for any skill with side effects or timing you control (commit, PR, autonomous loop); it stays available as `/name`.
- `scripts/audit-skills.sh` enforces `name`, `description`, `license`, `user-invocable` and `metadata.{version,status,last_reviewed,impact,category,complexity}`, and warns on a `status` outside the four values; it does not check `review_interval` or `allowed-tools`, so drift there goes unreported. A new required field goes into its `top_level_fields` or `metadata_fields` array in the same change.

## Output conventions (doc-producing skills)

- Every file a skill writes under `docs/` opens with the artefact frontmatter (OKF v0.1 superset plus lifecycle fields). The schema lives in the `metamodel` skill's `references/artefact-frontmatter.md`; reference it by name (ADR-0007), never by a relative path across skills, and never restate it.
- Under a consuming project's `var/`: `var/reports/<feature>/` for what a skill found (audits, syntheses, eval results), never top-level `var/reports/` or `outputs/`; `var/handoffs/<workstream-slug>/` for session state (`agent-handoff`).

## Domain-agnostic content

Every kit skill reaches every project. No client names, industry jargon, real currencies as defaults or segment names; examples use placeholders (`{{currency}}`, "Industry A"). Grep the skill for the originating project's terms before committing.

## Publish and install

1. Bump `plugins/<set>/.claude-plugin/plugin.json` `version` in the same commit; the plugin cache only moves on a version change.
2. Commit as `feat(<skill-name>): …` or `chore(<skill-name>): …` on a `<type>/<explicit-slug>` branch, PR, merge.
3. `./install.sh` from `main`. It symlinks skills into `~/.codex/skills` and `~/.agents/skills`; for Claude Code it follows `var/claude-channel`: `symlink` links `~/.claude/skills`, `marketplace` refreshes the `/plugin` cache instead. A running session needs `/reload-plugins` or a restart.
4. Rules take the same path: author them in `rules/` or `rules/personal/` (ADR-0011).

Never write a skill directly into `~/.claude/skills/` or a project's `.claude/skills/` when it belongs in the kit.

**Cross-machine sync:** the dotfiles repo's chezmoi hook `run_onchange_install-claude-kit.sh.tmpl` hashes the kit's remote `HEAD`, so every kit commit re-runs `git pull` and `install.sh` on the next `chezmoi apply`. `util-toolkit-doctor` audits the chain (chezmoi state, repo sync, link integrity).

Repos: kit <https://github.com/VictorHueni/homemade-claude-kit>, dotfiles <https://github.com/VictorHueni/dotfiles>.
