# homemade-claude-kit

A personal, harness-portable toolkit — 60 composable skills for business architecture,
domain modeling, product specification, and developer workflow, packaged as **11 toggleable
plugin sets** and consumable from **Claude Code, OpenAI Codex CLI, and OpenCode**.

Three design pillars (kit [ADR-0006](docs/architecture/decisions/adr-0006-plugin-packaging-cross-harness-activation.md) / [ADR-0007](docs/architecture/decisions/adr-0007-metamodel-distribution-as-skill.md)):

1. **SKILL.md is the portability layer** — all three harnesses read it natively; `install.sh` flattens `plugins/*/skills/*` into one directory per harness. No conversion, ever.
2. **The metamodel travels as a skill** — the `metamodel` skill carries the documentation-stack contract (build order, YAML type registry, frontmatter schema, open-items governance + Audit/Scaffold/Migrate modes). Structural facts are canonically owned by [clew](https://github.com/VictorHueni/clew) (clew ADR-0008); the kit ships the projection.
3. **Toggling is harness-native** — the kit ships no activation state; each harness uses its own idiom (see § Toggling a set).

---

## Plugin sets

| Set | Purpose | Skills |
|---|---|---|
| `kit-core` | Always on — the metamodel keystone + cross-cutting operators | `metamodel` · `util-open-items` · `util-provenance` · `util-toolkit-doctor` |
| `strategy` | Business architecture + discovery evidence | `business-vision` · `business-persona` · `business-model-canvas` · `business-capability-map` · `business-value-stream` · `business-objective` · `business-process` · `business-quantitative-model` · `business-competitive-landscape` · `discovery-idea` · `discovery-research` · `discovery-workshop` |
| `domain-modeling` | Strategic + tactical DDD | `domain-bounded-context` · `domain-glossary` · `domain-model` |
| `product-spec` | Specs + build planning | `spec-functional-breakdown-structure` · `spec-prd` · `spec-use-case` · `plan-delivery-roadmap` · `plan-implementation` |
| `quality-assurance` | Test strategy, scenarios, cases — the validate/test stage | `spec-quality-attributes` · `qa-test-strategy` · `qa-test-scenario` |
| `architecture` | Decisions, contracts, diagrams, arc42 | `arch-adr` · `arch-research` · `arch-service-contract` · `arch-cli-contract` · `arch-structurizr` · `arch-c4` · `arch-plantuml` · `arch-uml` · `arch-arc42` |
| `dev-flow` | Developer workflow (+ `branch-cleanup-audit` command) | `dev-git-init` · `dev-git-commit` · `dev-pr` · `dev-git-worktree` · `dev-release-init` · `dev-stack-guide` · `dev-getting-started` |
| `agent-loop` | Guide → Verify → Solve agent cycle (+ `ralph-audit` command) | `agent-config` · `agent-grill-me` · `agent-peer-review` · `agent-ralph-loop` |
| `delivery-comms` | Presentation layer | `com-slide-deck` · `com-artefact-viz` · `com-release-note` · `ux-design-system` |
| `ops` | Post-ship operations | `ops-runbook` · `ops-bug-rca` · `ops-terraform-exoscale` |
| `docs-hygiene` | Documentation housekeeping | `util-docs-audit` · `util-docs-index` · `util-docs-lint` · `util-docs-log` |

Per-skill purpose lives in each `plugins/<set>/skills/<name>/SKILL.md` frontmatter description.

---

## Install

### Claude Code — marketplace channel (recommended)

```bash
# In Claude Code:
/plugin marketplace add VictorHueni/homemade-claude-kit
# then enable the sets you want in /plugin
```

Each plugin bundles its skills, commands, and MCP servers (`plugins/<set>/.mcp.json`) — a
set toggle carries all three. **One channel per machine:** after adopting the marketplace,
record it once —

```bash
cd ~/projects/homemade-claude-kit && ./install.sh --claude-channel marketplace
```

— every later `install.sh` run (including chezmoi's) then skips and prunes the
`~/.claude/skills` + `~/.claude/commands` links while still serving Codex/OpenCode, rules,
adapters, and MCP. Revert with `--claude-channel symlink`. The choice persists in
`var/claude-channel` (per machine, gitignored); `util-toolkit-doctor` warns if both channels
end up live.

### All harnesses — symlink channel

```bash
git clone git@github.com:VictorHueni/homemade-claude-kit.git ~/projects/homemade-claude-kit
cd ~/projects/homemade-claude-kit && ./install.sh
```

A global run:

- symlinks all skills (flat) into `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills` (OpenCode discovers the latter two natively) and commands into `~/.claude/commands`;
- symlinks the Claude rules into `~/.claude/rules` (the personal layer only after `--personal-rules on`, see [Rules](#rules));
- renders the **AGENTS.md adapter** (metamodel routing + behavioural rules, marker-delimited) into `~/.codex/AGENTS.md` and `~/.config/opencode/AGENTS.md`;
- projects **`mcp/registry.json`** into `~/.codex/config.toml` (`[mcp_servers.*]` marker block) and `opencode.json`'s `mcp` key.

`./install.sh /path/to/project` installs into a single project instead (skills/commands/rules only). Re-run after `git pull` — idempotent, prunes retired skills, never touches your content outside its marker blocks.

## Update

```bash
cd ~/projects/homemade-claude-kit && git pull   # chezmoi machines do this automatically
# symlinks point here — install.sh re-runs only regenerate adapters/MCP
```

---

## Toggling a set

The kit ships no activation state — use each harness's native idiom (ADR-0006):

| Harness | Toggle | MCP follows? |
|---|---|---|
| **Claude Code** | `/plugin` → enable/disable the set | ✅ automatic (per-plugin `.mcp.json`) |
| **OpenCode** | Paste deny-globs into `opencode.json` — one line per set thanks to prefix naming: `"permission": { "skill": { "business-*": "deny", "discovery-*": "deny" } }` (that line disables `strategy`) | manual |
| **Codex CLI** | Remove the set's symlinks: `rm ~/.codex/skills/{business,discovery}-*` — **caveat:** any `install.sh` re-run (incl. the chezmoi hook) restores them | manual |

If you find yourself re-deleting the same Codex globs weekly, that's the recorded trigger to
build the deferred `--sets` activation layer (see the open-items ledger).

## MCP servers

`mcp/registry.json` is the single source of truth: 3 always-on (Chrome DevTools, Context7 →
`dev-flow`; Playwright → `delivery-comms`), 2 documented opt-ins (GitHub, Terraform — flip
`enabled` and re-run `scripts/gen-mcp.py plugins` + `./install.sh`), and a **project-scoped
PostgreSQL recipe** (Postgres MCP Pro — declare per project, not user-globally). Web search
is deliberately absent: harness-native search is relied on.

---

## Adding a skill

1. Create `plugins/<set>/skills/<skill-name>/SKILL.md` — naming + set placement per [`rules/skill-creation-sync.md`](./rules/skill-creation-sync.md); reference the metamodel **name-first** ("the `metamodel` skill's `references/<file>`").
2. Structural metamodel changes (new artefact type, ID, path) are authored **clew-side first** (clew ADR-0008), then synced into the `metamodel` skill's registry YAML.
3. Run `./install.sh` and `bash scripts/audit-skills.sh`.
4. Commit and push.

## Backlog

Open items live as GitHub Issues labelled `open-item` —
<https://github.com/VictorHueni/homemade-claude-kit/issues?q=label%3Aopen-item>
(authored via the Open Item form; contract: the `metamodel` skill's
`references/open-items-governance.md`).

## Rules

Every Claude rule is authored here, never directly in `~/.claude/rules/` (kit ADR-0011). `install.sh` links each file flat into `~/.claude/rules/`, replacing a same-named plain file, and prunes links whose source is gone. Two layers:

- **`rules/`**: shared engineering rules, installed for everyone.
- **`rules/personal/`**: the owner's preferences and this machine's setup. Installed only after `./install.sh --personal-rules on`, which is remembered in `var/personal-rules`, so a teammate's install gets the shared layer alone. A file name may exist in one layer only.

The rules marked *(→ AGENTS.md adapter)* also feed the generated AGENTS.md adapter for Codex/OpenCode. `scripts/test-install-rules.sh` checks the installer's rule handling against a throwaway kit. `scripts/check-rules.py` checks every rule against the budget: 3k per always-on rule, 20k always-on in total, 4k per path-scoped rule, and no dated history, incident narrative or wiki-links.

### Shared (`rules/`)

| Rule file | Covers |
|---|---|
| `rules/ci-workflows.md` | Local mirror for every CI tool; `GITHUB_TOKEN` chains and `workflow_run`; `GH_REPO` without a checkout (path-scoped) |
| `rules/claude-plugins-and-mcp.md` | Plugin refresh, MCP version pins, OAuth client reset |
| `rules/consistency-over-lean-variants.md` | Reuse the codebase's existing pattern before a leaner bespoke one |
| `rules/diagramming-mermaid.md` | Diagram tool split (C4, UML, Mermaid) and Mermaid pitfalls on GitHub (path-scoped) *(→ AGENTS.md adapter)* |
| `rules/diagramming-plantuml.md` | PlantUML creole markup eating CLI flags (path-scoped) |
| `rules/frontend-nuxt.md` | Nuxt UI 4 / Vue 3.5 / Reka UI (path-scoped) *(→ AGENTS.md adapter)* |
| `rules/git-and-tools.md` | Git discipline, Edit tool usage *(→ AGENTS.md adapter)* |
| `rules/github-issue-transfer.md` | Bulk issue transfer and lost sub-issue parent links |
| `rules/github-projects-single-select-field.md` | Adding a single-select option clears item values |
| `rules/jvm-toolchain.md` | Maven, Temurin, current LTS (path-scoped) |
| `rules/kit-docs-stack.md` | **Pointer stub** → the `metamodel` skill: spine, artefact registry, frontmatter, open-items contract (kit ADR-0007; path-scoped) |
| `rules/memory-hygiene.md` | Where a lesson belongs: kit rule, project AGENTS.md, or auto-memory |
| `rules/module-graph-reachability.md` | A direct-importer grep is not a reachability proof |
| `rules/osv-scanner-gitignored-worktrees.md` | osv-scanner finding nothing inside a gitignored checkout |
| `rules/postgres-schema-gotchas.md` | PostgreSQL NULL, jsonb and planner traps (path-scoped) |
| `rules/python-gotchas.md` | pydantic-settings, radon/xenon, venv and uv, mypy/Pyright (path-scoped) |
| `rules/skill-creation-sync.md` | Skill naming (incl. registered exceptions), set placement, reference convention, blast-radius procedure |
| `rules/sonarcloud-silent-analysis-failure.md` | SonarCloud analysis failing server-side behind a green CI |
| `rules/supabase-config-push-scope.md` | `supabase config push` pushing the whole local config (path-scoped) |
| `rules/testcontainers-wsl-docker-context.md` | Docker context on WSL breaking docker-py and Testcontainers |
| `rules/toolchain-version-managed-globals.md` | Version-manager globals vanishing on a runtime bump |
| `rules/working-style.md` | Sequential plans, trust-but-verify *(→ AGENTS.md adapter)* |
| `rules/writing-citations.md` | Inline source links in markdown docs (path-scoped) *(→ AGENTS.md adapter)* |

### Personal (`rules/personal/`)

| Rule file | Covers |
|---|---|
| `rules/personal/bang-prefix-is-for-the-claude-prompt.md` | Say that a `! command` goes in the Claude prompt |
| `rules/personal/browser-automation.md` | Prefer Playwright |
| `rules/personal/claude-plugin-eval-wsl-and-graders.md` | `claude plugin eval` on WSL; `tool_used` graders |
| `rules/personal/decisions-in-prose-not-forms.md` | Owner decisions discussed in prose |
| `rules/personal/diagramming-layout.md` | Orthogonal edges, fewest elbows (path-scoped) |
| `rules/personal/preferences.md` | Naming, code language |
| `rules/personal/python-docstring-policy.md` | Google §3.8 docstrings as written (path-scoped) |
| `rules/personal/subagent-orchestration.md` | Pointer to chat-driven Ralph orchestration; joining dead-code leads across audit slices |
| `rules/personal/ui-copy-no-em-dash.md` | No em dash in user-facing copy (path-scoped) |
| `rules/personal/wsl-test-resource-budget.md` | Memory budget for test runs on the WSL machine |
