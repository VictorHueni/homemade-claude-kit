# homemade-claude-kit

A personal Claude Code toolkit — composable skills for business architecture, domain modeling, product specification, and developer workflow. Install once, available in every project.

---

## Skill index

| Prefix | Skill | Purpose |
|---|---|---|
| `business-` | `business-vision` | Product north star — `docs/VISION.md` |
| `business-` | `business-persona` | Persona registry — `P-NN` |
| `business-` | `business-model-canvas` | Lean Canvas / BMC |
| `business-` | `business-capability-map` | Capability map — `C-N.M` |
| `business-` | `business-value-stream` | Value streams — `VS-N.M` |
| `business-` | `business-objective` | OKRs — `OBJ-NN` · `KR-NN.M` |
| `business-` | `business-process` | BPMN-ready process docs |
| `business-` | `business-quantitative-model` | TAM/SAM/SOM · ROI models |
| `business-` | `business-competitive-landscape` | Five Forces · value curve |
| `discovery-` | `discovery-idea` | Pre-formal idea capture · refine · graduate — `IDEA-NNNN` |
| `discovery-` | `discovery-research` | Interview scripts + synthesis |
| `discovery-` | `discovery-workshop` | Workshop planning + facilitation |
| `domain-` | `domain-bounded-context` | Bounded context map — `BC-NN` |
| `domain-` | `domain-glossary` | Ubiquitous language — `GT-NN` |
| `domain-` | `domain-model` | Entities · aggregates · events |
| `spec-` | `spec-functional-breakdown-structure` | Feature registry — `C-N.M.FXX` |
| `spec-` | `spec-delivery-roadmap` | Epics + walking skeleton — `E-NN` |
| `spec-` | `spec-quality-attributes` | NFRs — `QA-XXNN` |
| `spec-` | `spec-use-case` | Use cases (actor↔system scenarios) — `UC-NN` |
| `spec-` | `spec-prd` | Product Requirements Document — `PRD-NNNN` |
| `spec-` | `spec-implementation-plan` | Atomic increment plan |
| `spec-` | `spec-peer-review` | PRD / plan review |
| `arch-` | `arch-adr` | Architecture Decision Records — `ADR-NNNN` |
| `arch-` | `arch-research` | Evidence base for ADRs — `Research-NNNN` |
| `arch-` | `arch-service-contract` | Service interface contract per BC — `BC-NN.CTR-NN` / `CTR-NN` |
| `arch-` | `arch-cli-contract` | CLI surface contract — `BC-NN.CLI-NN.CMD-NN` / `CLI-NN.CMD-NN` |
| `arch-` | `arch-structurizr` | Structurizr DSL workspace + Docker render pipeline (foundation for `arch-c4`) |
| `arch-` | `arch-c4` | C4 diagrams + DSL-derived table blocks for arc42 §3 / §5 / §7 (inside `arch-c4` markers; no narrative — ADR-0004) — `SYS-NN`, `CON-NN`, `CMP-NN`, `DN-NN` |
| `arch-` | `arch-plantuml` | PlantUML diagrams workspace + Docker render pipeline (foundation for `arch-uml`) |
| `arch-` | `arch-uml` | UML diagrams (sequence / class / state / activity / ER / use-case) via PlantUML → committed SVG; mints no IDs |
| `arch-` | `arch-arc42` | arc42 narrative — owns ALL prose §2 / §4 / §6 / §8 / §11 (ADR-0004); §6/§8 pull figures from C4 or `arch-uml` — `CST-NN`, `SCN-NN`, `CC-NN`, `RSK-NN` |
| `ops-` | `ops-runbook` | Operator runbooks |
| `ops-` | `ops-bug-rca` | Root cause analysis |
| `dev-` | `dev-stack-guide` | Per-technology developer guide + MCP discovery — `docs/dev-guides/{tech-slug}.md` |
| `dev-` | `dev-getting-started` | Project onboarding guide — `docs/dev-guides/getting-started.md` |
| `dev-` | `dev-git-commit` | Conventional commit generation |
| `dev-` | `dev-pr` | Pull request creation |
| `dev-` | `dev-git-worktree` | Isolated git worktrees |
| `dev-` | `dev-ralph-loop` | Autonomous increment execution |
| `ux-` | `ux-design-system` | Project visual source of truth — `docs/ux/design-system.md` → `tokens.css` (themes the `com-` layer) |
| `com-` | `com-slide-deck` | HTML slide deck builder |
| `com-` | `com-artefact-viz` | Interactive HTML views of artefacts (capability map · FBS · roadmap · BMC) |
| `util-` | `util-metamodel-scaffold` | Canonical docs/ folder tree + INDEX.md + CLAUDE.md wiring |
| `util-` | `util-metamodel-audit` | Artefact stack health check |
| `util-` | `util-metamodel-migration` | Docs folder migration report |
| `util-` | `util-docs-audit` | Documentation freshness audit |
| `util-` | `util-docs-lint` | Docs lint toolchain (dprint/Vale/lychee) — audit, enforce, CI |
| `util-` | `util-toolkit-doctor` | Claude Code setup health |

---

## Install

```bash
# Clone once
git clone git@github.com:VictorHueni/homemade-claude-kit.git ~/projects/homemade-claude-kit

# Symlink skills into ~/.claude/skills/ (and ~/.codex/skills/ if present)
./install.sh

# Verbose output for debugging
./install.sh --verbose
```

## Update

```bash
cd ~/projects/homemade-claude-kit
git pull
# Symlinks already point here — no reinstall needed
```

## Adding a skill

1. Create `skills/{skill-name}/SKILL.md` — follow the naming convention in [`rules/skill-creation-sync.md`](./rules/skill-creation-sync.md)
2. Run `./install.sh` to symlink it
3. Commit and push

## Backlog

Planned skills, decision gaps, and follow-ups are tracked as open items in the kit's own
control plane, [`docs/project-control/open-items/open-items.md`](./docs/project-control/open-items/open-items.md)
(`OI-NNNN`). Shipped-skill history is archived under
[`docs/project-control/open-items/archive/`](./docs/project-control/open-items/archive/).

## Rules

Cross-project conventions loaded automatically by Claude Code:

| Rule file | Covers |
|---|---|
| `rules/artefact-frontmatter.md` | Standard frontmatter for all skill-produced docs |
| `rules/skill-creation-sync.md` | Skill naming, frontmatter, cross-machine sync |
| `rules/metamodel.md` | Artefact definitions, build order, ID conventions |
| `rules/open-items-governance.md` | Cross-cutting open-items contract: canonical document-level `## Open Items` heading, item taxonomy (`doc-gap`, `decision-gap`, `execution-item`, `tech-debt`), provenance fields (`Source anchor` + `Source heading`), and central ledger under `docs/project-control/open-items/` |
| `rules/git-and-tools.md` | Git discipline, Edit tool usage |
| `rules/working-style.md` | Sequential plans, trust-but-verify |
| `rules/diagramming-mermaid.md` | Mermaid diagram pitfalls |
| `rules/frontend-nuxt.md` | Nuxt UI v4 / Vue 3.5 / Reka UI |
| `rules/python-extras.md` | Python naming conventions |
| `rules/writing-citations.md` | Citation discipline |
