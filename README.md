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
| `spec-` | `spec-prd` | Product Requirements Document — `PRD-NNNN` |
| `spec-` | `spec-implementation-plan` | Atomic increment plan |
| `spec-` | `spec-peer-review` | PRD / plan review |
| `arch-` | `arch-adr` | Architecture Decision Records |
| `arch-` | `arch-research` | Evidence base for ADRs |
| `ops-` | `ops-runbook` | Operator runbooks |
| `ops-` | `ops-bug-rca` | Root cause analysis |
| `dev-` | `dev-git-commit` | Conventional commit generation |
| `dev-` | `dev-pr` | Pull request creation |
| `dev-` | `dev-git-worktree` | Isolated git worktrees |
| `dev-` | `dev-ralph-loop` | Autonomous increment execution |
| `com-` | `com-slide-deck` | HTML slide deck builder |
| `util-` | `util-metamodel-scaffold` | Canonical docs/ folder tree + INDEX.md + CLAUDE.md wiring |
| `util-` | `util-metamodel-audit` | Artefact stack health check |
| `util-` | `util-metamodel-migration` | Docs folder migration report |
| `util-` | `util-docs-audit` | Documentation freshness audit |
| `util-` | `util-docs-lint` | Docs CI scaffold |
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

1. Create `{skill-name}/SKILL.md` — follow the naming convention in [`rules/skill-creation-sync.md`](./rules/skill-creation-sync.md)
2. Run `./install.sh` to symlink it
3. Commit and push

## Backlog

Planned skills, known issues, and shipped items are tracked in [`BACKLOG.md`](./BACKLOG.md).

## Rules

Cross-project conventions loaded automatically by Claude Code:

| Rule file | Covers |
|---|---|
| `rules/artefact-frontmatter.md` | Standard frontmatter for all skill-produced docs |
| `rules/skill-creation-sync.md` | Skill naming, frontmatter, cross-machine sync |
| `rules/metamodel.md` | Artefact definitions, build order, ID conventions |
| `rules/open-items-governance.md` | Cross-cutting open-items contract: canonical document-level `## Open Items` heading, item taxonomy (`doc-gap`, `decision-gap`, `execution-item`, `tech-debt`), provenance fields (`Source anchor` + `Source heading`), and central ledger under `project-control/open-items/` |
| `rules/git-and-tools.md` | Git discipline, Edit tool usage |
| `rules/working-style.md` | Sequential plans, trust-but-verify |
| `rules/diagramming-mermaid.md` | Mermaid diagram pitfalls |
| `rules/frontend-nuxt.md` | Nuxt UI v4 / Vue 3.5 / Reka UI |
| `rules/python-extras.md` | Python naming conventions |
| `rules/writing-citations.md` | Citation discipline |
