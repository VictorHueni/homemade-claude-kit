# homemade-claude-kit

A personal, harness-portable toolkit — 61 composable skills for business architecture, domain modeling, product specification, and developer workflow, packaged as **11 toggleable plugin sets** and consumable from **Claude Code, OpenAI Codex CLI, and OpenCode**.

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
| `agent-loop` | Guide → Verify → Solve agent cycle (+ `ralph-audit` command) | `agent-config` · `agent-grill-me` · `agent-handoff` · `agent-issue-loop` · `agent-peer-review` · `agent-ralph-loop` |
| `delivery-comms` | Presentation layer | `com-slide-deck` · `com-artefact-viz` · `com-release-note` · `ux-design-system` |
| `ops` | Post-ship operations | `ops-runbook` · `ops-bug-rca` · `ops-sonarcloud-audit` · `ops-terraform-exoscale` |
| `docs-hygiene` | Documentation housekeeping | `util-docs-audit` · `util-docs-index` · `util-docs-lint` · `util-docs-log` |

Per-skill purpose lives in each `plugins/<set>/skills/<name>/SKILL.md` frontmatter description.

---

## Install

### New laptop

1. Register an SSH key on GitHub, then `git clone git@github.com:VictorHueni/homemade-claude-kit.git ~/projects/homemade-claude-kit` (on the owner's machines the dotfiles' chezmoi run script clones it and runs `install.sh` on every kit change).
2. `cd ~/projects/homemade-claude-kit && ./install.sh`. The owner adds `--personal-rules on` once.
3. In Claude Code: `/plugin marketplace add VictorHueni/homemade-claude-kit`, enable the sets in `/plugin`, then `./install.sh --claude-channel marketplace` once (below).
4. Start a new Claude Code session: rules, hooks and MCP servers load at session start.

### Claude Code — marketplace channel (recommended)

```bash
# In Claude Code:
/plugin marketplace add VictorHueni/homemade-claude-kit
# then enable the sets you want in /plugin
```

Each plugin bundles its skills, commands, hooks and MCP servers (`plugins/<set>/.mcp.json`), so a set toggle carries all of them. **One channel per machine:** after adopting the marketplace, record it once:

```bash
cd ~/projects/homemade-claude-kit && ./install.sh --claude-channel marketplace
```

Every later `install.sh` run (including chezmoi's) then skips and prunes the `~/.claude/skills` and `~/.claude/commands` links, and refreshes the plugin cache instead: `claude plugin marketplace update homemade-claude-kit`, then `claude plugin update <set>@homemade-claude-kit` for each installed kit plugin. Without that, a `git pull` never reaches the cache that Claude Code serves. Codex/OpenCode, rules, adapters and MCP are still served. Revert with `--claude-channel symlink`. The choice persists in `var/claude-channel` (per machine, gitignored); `util-toolkit-doctor` warns if both channels end up live.

### All harnesses — symlink channel

```bash
git clone git@github.com:VictorHueni/homemade-claude-kit.git ~/projects/homemade-claude-kit
cd ~/projects/homemade-claude-kit && ./install.sh
```

A global run:

- symlinks all skills (flat) into `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills` (OpenCode discovers the latter two natively) and commands into `~/.claude/commands`;
- symlinks the Claude rules into `~/.claude/rules` (the personal layer only after `--personal-rules on`, see [Rules](#rules));
- renders the **AGENTS.md adapter** (metamodel routing + behavioural rules, marker-delimited) into `~/.codex/AGENTS.md` and `~/.config/opencode/AGENTS.md`;
- projects **`mcp/registry.json`** into `~/.codex/config.toml` (`[mcp_servers.*]` marker block) and `opencode.json`'s `mcp` key;
- enables the official `pyright-lsp`, `typescript-lsp` and `jdtls-lsp` plugins in `~/.claude/settings.json` (only those `enabledPlugins` keys);
- sets `core.hooksPath` to `.githooks` on the kit checkout unless it already has one (also on project runs).

`./install.sh /path/to/project` installs into a single project instead: skills, commands and rules (the personal layer when it is on), always through symlinks whatever the recorded channel. Re-run after `git pull`: it is idempotent, prunes retired skills, rules and commands, and never touches your content outside its marker blocks.

## Update

```bash
cd ~/projects/homemade-claude-kit && git pull && ./install.sh   # chezmoi machines do this automatically
```

Symlinked skills see the pull at once; the re-run links new skills, rules and commands, prunes retired ones, regenerates the adapters and MCP, and on the marketplace channel refreshes the plugin cache. Start a new session afterwards.

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

`mcp/registry.json` is the single source of truth, pinned to exact versions: `scripts/gen-mcp.py` refuses an enabled npx server without one. It holds 3 always-on servers (Chrome DevTools and Context7 → `dev-flow`; Playwright → `delivery-comms`) and 3 disabled ones: GitHub and Terraform are opt-ins (flip `enabled`, then run `python3 scripts/gen-mcp.py plugins .` and `./install.sh`); the community SonarQube server is retired in favour of SonarSource's official `sonarqube@claude-plugins-official` plugin. **Project-scoped recipes** (declare per project, not user-globally): PostgreSQL (Postgres MCP Pro), `quarkus-agent` and `maven-tools`. Web search is deliberately absent: harness-native search is relied on.

---

## Adding a skill

1. Create `plugins/<set>/skills/<skill-name>/SKILL.md` — naming + set placement per the kit-local [`util-skill-authoring`](./.claude/skills/util-skill-authoring/SKILL.md) skill; reference the metamodel **name-first** ("the `metamodel` skill's `references/<file>`").
2. Structural metamodel changes (new artefact type, ID, path) are authored **clew-side first** (clew ADR-0008), then synced into the `metamodel` skill's registry YAML.
3. Bump the set's `plugins/<set>/.claude-plugin/plugin.json` version, or the marketplace cache keeps serving the old copy ([`rules/skill-creation-sync.md`](rules/skill-creation-sync.md)).
4. A new or removed skill changes the count in this README, `.claude-plugin/marketplace.json`, `index.md` and `AGENTS.md`.
5. Run `./install.sh` and `bash scripts/audit-skills.sh`.
6. Commit and push.

## Backlog

Open items live as GitHub Issues labelled `open-item` —
<https://github.com/VictorHueni/homemade-claude-kit/issues?q=label%3Aopen-item>
(authored via the Open Item form; contract: the `metamodel` skill's
`references/open-items-governance.md`).

## Hooks

`kit-core` ships Claude Code hooks in `plugins/kit-core/hooks/hooks.json`; they run whenever the plugin is enabled. They replace always-on rules that only mattered for one command.

- **`tripwires.py`** (PreToolUse, Bash) checks each command against a table. `deny` blocks it outright with what to do instead (`git commit --amend`, `pgrep -f` in a wait loop). `ack` blocks a one-shot, hard-to-undo call with its checklist until the command is rerun with a trailing `# tripwire-ack` (`gh issue transfer`, an `updateProjectV2Field` GraphQL call). `note` lets it run and adds the explanation to the model's context with the result (`osv-scanner`; `claude plugin update`/`install`, `claude mcp`; `dig`/`nslookup`/`host`; a test run while Docker Desktop's `desktop-linux` context is active on WSL). Commands are matched in command position, after quoted text, heredoc bodies and comments are removed, so a commit message or a grep naming a command does not trip it; `sh -c` and `eval` payloads are still checked.
- **`memory_write_check.py`** (PreToolUse, Write/Edit/MultiEdit) denies the first write to each auto-memory file in a session with the "kit rule, AGENTS.md, or memory?" checklist; the retry goes through. `MEMORY.md` itself is exempt.
- **`docker_context_check.py`** (SessionStart) prints the same Docker warning when a session opens with that context active. Silent everywhere else, macOS included.

Add a tripwire as one row in `TRIPWIRES` plus its cases in `scripts/test-hooks.py`, then bump `kit-core`'s version. Run the tests with `python3 scripts/test-hooks.py`.

## Rules

Every Claude rule is authored here, never directly in `~/.claude/rules/` (kit [ADR-0011](docs/architecture/decisions/adr-0011-rules-single-authoring-surface-and-layers.md)). `install.sh` links each file flat into `~/.claude/rules/`, replacing a same-named plain file, and prunes links whose source is gone. Two layers:

- **`rules/`**: shared engineering rules, installed for everyone.
- **`rules/personal/`**: the owner's preferences and this machine's setup. Installed only after `./install.sh --personal-rules on`, which is remembered in `var/personal-rules`, so a teammate's install gets the shared layer alone. A file name may exist in one layer only.

The rules marked *(→ AGENTS.md adapter)* also feed the generated AGENTS.md adapter for Codex/OpenCode. `scripts/test-install-rules.sh` checks the installer's rule handling against a throwaway kit. `scripts/check-rules.py` checks every rule against the budget: 3k per always-on rule, 6k always-on in total, 4k per path-scoped rule, and no dated history, incident narrative or wiki-links. A pre-commit hook in `.githooks/` runs it, along with `test-hooks.py`, `audit-skills.sh` and `test-install-rules.sh`, each only when the commit touches files that check covers; `install.sh` enables it by setting `core.hooksPath` unless the checkout already has one.

### Shared (`rules/`)

| Rule file | Covers |
|---|---|
| `rules/ci-workflows.md` | Local mirror for every CI tool; `GITHUB_TOKEN` chains and `workflow_run`; `GH_REPO` without a checkout (path-scoped) |
| `rules/claude-plugins-and-mcp.md` | Plugin refresh, MCP version pins, OAuth client reset (path-scoped) |
| `rules/diagramming-mermaid.md` | Diagram tool split (C4, UML, Mermaid; kit [ADR-0012](docs/architecture/decisions/adr-0012-diagram-tool-split.md)) and Mermaid pitfalls on GitHub (path-scoped) *(→ AGENTS.md adapter)* |
| `rules/diagramming-plantuml.md` | PlantUML creole markup eating CLI flags (path-scoped) |
| `rules/frontend-nuxt.md` | Nuxt UI 4 / Vue 3.5 / Reka UI (path-scoped) *(→ AGENTS.md adapter)* |
| `rules/git.md` | No amend, commit and PR-title scope, branch names *(→ AGENTS.md adapter)* |
| `rules/jvm-toolchain.md` | Maven, Temurin, current LTS (path-scoped) |
| `rules/kit-docs-stack.md` | **Pointer stub** → the `metamodel` skill: spine, artefact registry, frontmatter, open-items contract (kit ADR-0007; path-scoped) |
| `rules/postgres-schema-gotchas.md` | PostgreSQL NULL, jsonb and planner traps (path-scoped) |
| `rules/python-gotchas.md` | pydantic-settings, radon/xenon, venv and uv, mypy/Pyright (path-scoped) |
| `rules/shell-verdicts.md` | `PIPESTATUS`, truncated output, `pgrep -f` waits *(→ AGENTS.md adapter)* |
| `rules/skill-creation-sync.md` | Skill-edit checklist; points to the kit-local `util-skill-authoring` skill (path-scoped) |
| `rules/sonarcloud-silent-analysis-failure.md` | **Pointer stub** → the `ops-sonarcloud-audit` skill (path-scoped) |
| `rules/supabase-config-push-scope.md` | `supabase config push` pushing the whole local config (path-scoped) |
| `rules/working-style.md` | Sequential plans, trust-but-verify, reuse project automation, no hard-wrapped markdown, sources in answers *(→ AGENTS.md adapter)* |
| `rules/writing-citations.md` | Inline source links in markdown docs (path-scoped) *(→ AGENTS.md adapter)* |

### Personal (`rules/personal/`)

| Rule file | Covers |
|---|---|
| `rules/personal/bang-prefix-is-for-the-claude-prompt.md` | Say that a `! command` goes in the Claude prompt |
| `rules/personal/decisions-in-prose-not-forms.md` | Owner decisions discussed in prose |
| `rules/personal/diagramming-layout.md` | Orthogonal edges, fewest elbows (path-scoped) |
| `rules/personal/preferences.md` | Naming, code language |
| `rules/personal/python-docstring-policy.md` | Google §3.8 docstrings as written (path-scoped) |
| `rules/personal/subagent-orchestration.md` | Pointer to chat-driven Ralph orchestration |
| `rules/personal/ui-copy-no-em-dash.md` | No em dash in user-facing copy (path-scoped) |
