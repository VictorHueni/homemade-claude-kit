# Skill creation and cross-machine sync workflow

How to create a new Claude skill, publish it to `homemade-claude-kit`, and make it available globally via dotfiles/chezmoi.

## Where new skills live

New skills belong in `<KIT_DIR>/<skill-name>/SKILL.md` (with optional `references/` and `scripts/` subdirs).

**Finding the kit:** `homemade-claude-kit` is always a sibling of the current project — the parent folder name varies by machine (`projets/` vs `projects/`). Derive it reliably from the current git root:

```bash
KIT_DIR="$(dirname "$(git rev-parse --show-toplevel)")/homemade-claude-kit"
```

## Standard skill structure

```
<KIT_DIR>/<skill-name>/
  SKILL.md              # required — YAML frontmatter + Claude-facing instructions
  references/           # optional — markdown content the skill loads on demand
  scripts/              # optional — runtime helpers
  templates/            # optional — output templates
```

## Naming convention (canonical)

Skill folder name + `name:` frontmatter field must follow this exact pattern:

```
<category>-<artifact-singular>[-<verb>]
```

**Core principle:** for doc-producing skills, **the category prefix names the output folder under `docs/`**. For non-doc skills (utilities), the category prefix names the function.

### Categories (pick exactly one — required)

| Category | Maps to output folder | Examples |
|---|---|---|
| `business-` | `docs/business/` | `business-persona`, `business-capability-map`, `business-value-stream`, `business-process`, `business-model-canvas`, `business-quantitative-model` |
| `spec-` | `docs/product-specs/`, `docs/exec-plans/`, `docs/ideas/` (pre-PRD specs all live in the `spec-` family) | `spec-prd`, `spec-functional-breakdown-structure`, `spec-implementation-plan`, `spec-peer-review`, `spec-idea` |
| `arch-` | `docs/architecture/` (subfolders per artefact type) | `arch-adr` (writes to `docs/architecture/decisions/`) |
| `domain-` | `docs/domain/` | DDD artefacts — bounded contexts, glossary, domain model; the shared language between business and tech | `domain-bounded-context`, `domain-glossary`, `domain-model` |
| `ops-` | `docs/ops/` (subfolders per artefact type) | `ops-runbook` (→ `docs/ops/runbooks/`), `ops-bug-rca` (→ `docs/ops/rcas/`) |
| `dev-` | *(no doc folder — developer workflow utility)* | `dev-git-commit`, `dev-pr`, `dev-git-worktree`, `dev-slide-deck`, `dev-ralph-loop` |
| `util-` | *(no doc folder — housekeeping)* | `util-docs-audit`, `util-toolkit-doctor` |

**Why this matters:** when you (or Claude) see a skill name, the prefix immediately tells you (a) which folder its output goes into, or (b) that it's a non-doc utility. No ambiguity.

### Inner-redundancy rule

If the artefact name already starts with the category word, **strip the redundancy**.

| ❌ Redundant | ✅ Clean |
|---|---|
| `business-business-process` | `business-process` |
| `business-business-model-canvas` | `business-model-canvas` |
| `arch-architecture-decision` | `arch-adr` |

### Artefact name (required)

The noun the skill produces or operates on, in **kebab-case**, **singular**. The artefact name should be the natural English noun for the deliverable, not an action verb.

- ✅ `spec-persona` (the artefact is "persona")
- ✅ `spec-business-capability-map` (the artefact is "business capability map")
- ❌ `spec-personas` (no plural)
- ❌ `spec-building-personas` (verb-phrase, not noun)

### Verb suffix (optional — only when disambiguation is required)

When **two skills share the same artefact** but differ in intent, append a verb suffix:

- `spec-prd` (creates PRDs) vs `spec-prd-review` (reviews PRDs) — different intents on the same artefact
- `spec-adr-manager` (full CRUD lifecycle) — manager verb expresses the lifecycle intent

When only ONE skill exists per artefact, **drop the verb suffix**. The "build" intent is implicit; the SKILL.md description carries the trigger words.

| ❌ Wrong (redundant verb) | ✅ Right (implicit) |
|---|---|
| `spec-persona-builder` | `spec-persona` |
| `spec-prd-creator` | `spec-prd` |
| `spec-value-stream-mapper` | `spec-value-stream` |
| `spec-implementation-planner` | `spec-implementation-plan` |
| `spec-peer-reviewer` | `spec-peer-review` |
| `ops-runbook-creator` | `ops-runbook` |

### Allowed verbs (when disambiguation is needed)

| Verb | Use for |
|---|---|
| `-builder` | Creates new instances (replaces `-creator`, `-generator`) |
| `-manager` | Full CRUD lifecycle |
| `-mapper` | Links/maps between artefacts |
| `-reviewer` / `-review` | Critical review / quality assessment |
| `-auditor` / `-audit` | Read-only assessment |
| `-runner` | Executes a process |

### Anti-patterns (don't do these)

| Anti-pattern | Why | Fix |
|---|---|---|
| Missing category prefix (`docs-auditor`) | No discoverability axis | Add prefix → `util-docs-audit` |
| `-skill` suffix (`slide-builder-skill`) | Tautological | Drop suffix → `dev-slide-deck` |
| `using-` prefix (`using-git-worktrees`) | Verb-led, plural noun | Reframe → `dev-git-worktree` |
| Synonym verbs (`-creator`, `-generator`, `-builder` interchangeably) | Pick-one inconsistency | Standardise on `-builder`, drop others |
| Folder name ≠ `name:` field | Hidden inconsistency | Always align both |

### Verification

When you create or rename a skill, verify name consistency:

```bash
for skill in */; do
  skill_name="${skill%/}"
  [ -f "$skill/SKILL.md" ] && name=$(grep "^name:" "$skill/SKILL.md" | sed -E 's/name: *//; s/^"//; s/"$//')
  [ "$skill_name" != "$name" ] && echo "MISMATCH: folder=$skill_name name=$name"
done
```

Should return zero output.

---

## SKILL.md frontmatter convention

Match existing skills like `spec-prd`:

```yaml
---
name: skill-name-kebab
description: "One sentence + 'Triggers on: phrase1, phrase2, phrase3.' Claude uses this to decide when to activate."
version: "1.0.0"
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "specification"   # or "infrastructure", "review", etc.
  complexity: "medium"
---
```

## Domain-agnostic discipline (critical)

The kit is USER-GLOBAL across every project. Skills shipped here must avoid project-specific terms — no client names, industry jargon, real currencies as defaults, or segment names from the originating project. Examples in `references/` should use placeholders (`{{currency}}`, "Industry A", "top N customers"). The originating project's own scaffolds can stay project-specific; only the kit-side copy must be neutral.

Audit before pushing:

```bash
grep -niE "<project-specific terms>" SKILL.md references/*.md
```

Should return zero matches.

## Metamodel impact assessment (run before publishing any skill change)

Before committing a new skill or a change to an existing artefact-producing skill, answer the five questions below. Each "yes" triggers a mandatory update to the files listed.

| Question | If yes → update |
|---|---|
| Does the skill's **output path** change or is it a new skill with a new path? | `rules/metamodel.md` canonical paths + artefact table · `util-metamodel-audit/references/check-catalogue.md` Check 1 · `util-metamodel-migration/references/detection-signals.md` §Filename patterns + §Folder patterns |
| Does the skill **mint a new ID format** (e.g. `XX-NN`)? | `rules/metamodel.md` cross-doc ID conventions · `util-metamodel-audit/references/check-catalogue.md` Check 5 · `util-metamodel-migration/references/detection-signals.md` §Filename patterns |
| Does the skill **add or change a prerequisite** (upstream artefact it depends on)? | `rules/metamodel.md` DAG + build order step · `util-metamodel-audit/references/check-catalogue.md` Check 7 |
| Does the skill **add, rename, or remove a mandatory section** from its template? | `util-metamodel-audit/references/check-catalogue.md` Check 9 · `util-metamodel-migration/references/detection-signals.md` §Content signals |
| Is this a **brand-new artefact-producing skill** (new step in the build order)? | `rules/metamodel.md` artefact table + DAG + build order section + canonical paths + prefix mapping · README.md flowchart + ER diagram · `util-metamodel-audit/SKILL.md` step count · all four files above |

**Scope filter:** this checklist applies to skills in the `business-`, `spec-`, `arch-`, and `domain-` families. `dev-*`, `util-*`, and `ops-*` skills that produce no metamodel artefact can skip it.

## Publish and install

1. Commit + push in `$KIT_DIR` — convention: `feat(<skill-name>): <title>` or `chore(<skill-name>): <title>`
2. `$KIT_DIR/install.sh` — symlinks all skills into `~/.claude/skills/`

## Cross-machine sync via chezmoi

Dotfiles hook `run_onchange_install-claude-kit.sh.tmpl` re-runs on every `chezmoi apply` *only when its rendered content changes*. The hash comment uses:

```
# claude-kit remote HEAD: {{ output "git" "ls-remote" "https://github.com/VictorHueni/homemade-claude-kit.git" "HEAD" | sha256sum }}
```

This hashes the kit's remote HEAD SHA — different on every kit commit, so chezmoi correctly re-triggers `git pull` + `install.sh`. Earlier versions hashed the literal string `"homemade-claude-kit"` which is constant; that bug was fixed 2026-05-16 (dotfiles commit `94a1bba`).

## Verification + repair

The `util-toolkit-doctor` skill audits the whole flow — chezmoi state, kit + dotfiles repo sync, `~/.claude/` symlink integrity. Invoke it if anything looks broken or after a major refactor.

## Why this matters

Skills in a project's `.claude/skills/` are project-scoped only. The kit makes them available everywhere and chezmoi-synced across machines. Never write skills directly to `~/.claude/skills/` — always go through the kit. The hardcoded `~/projets/` path in the dotfiles script only applies to the chezmoi bootstrap; for day-to-day use always derive the path from the git root.

## Repos

- Kit: <https://github.com/VictorHueni/homemade-claude-kit>
- Dotfiles: <https://github.com/VictorHueni/dotfiles>
