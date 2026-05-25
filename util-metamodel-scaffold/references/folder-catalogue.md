# Folder Catalogue — util-metamodel-scaffold

Complete canonical folder list per project variant. Claude reads this file during scaffold
execution to know which `mkdir -p` commands to run.

All paths are relative to the project root. `{docs_root}` defaults to `docs/`.

---

## Variant A — Greenfield (full canonical tree)

All canonical folders. Use when starting a brand-new software product or venture.

```bash
# Business architecture layer
mkdir -p docs/business/05a-processes
mkdir -p docs/business/06a-models
mkdir -p docs/business/01b-competitive-landscape
mkdir -p docs/business/discovery/interviews
mkdir -p docs/business/discovery/workshops

# Domain layer (DDD artefacts)
mkdir -p docs/domain/07b-models

# Product specs layer
mkdir -p docs/product-specs/prds

# Execution plans layer
mkdir -p docs/exec-plans/active

# Architecture layer
mkdir -p docs/architecture/decisions
mkdir -p docs/architecture/research

# Ops layer
mkdir -p docs/ops/runbooks
mkdir -p docs/ops/rcas

# Communication layer
mkdir -p docs/communication/slides

# Pre-PRD ideas
mkdir -p docs/ideas

# Reports (non-docs — audit + migration output)
mkdir -p var/reports/metamodel-audit
mkdir -p var/reports/metamodel-migration
mkdir -p var/reports/open-items

# Open-items control plane (non-docs — operational system of record)
mkdir -p project-control/open-items/archive
```

**Implied parent folders** (created automatically by `mkdir -p` above):
`docs/` · `docs/business/` · `docs/domain/` · `docs/product-specs/` · `docs/exec-plans/`
`docs/architecture/` · `docs/ops/` · `docs/communication/` · `var/` · `var/reports/`
`project-control/` · `project-control/open-items/`

**Stub files also created (by SKILL.md §Project-control scaffold):**
`project-control/open-items/open-items.md` · `project-control/open-items/README.md`
`project-control/open-items/archive/.gitkeep`

**Leaf folders that get `.gitkeep` until content is added:**
All `docs/` and `var/` leaf folders when empty at scaffold time.

**Total leaf directories (greenfield):** ~21

---

## Variant B — Brownfield (existing system, adding capability)

Skip the personas and BMC layers — those are rarely re-created for brownfield projects.
Start at Step 3 (Capability Map). Business objectives are included because new capability
delivery benefits from OKR framing.

```bash
# Business architecture layer (start at capability map)
mkdir -p docs/business/05a-processes
mkdir -p docs/business/06a-models

# Domain layer
mkdir -p docs/domain/07b-models

# Product specs layer
mkdir -p docs/product-specs/prds

# Execution plans layer
mkdir -p docs/exec-plans/active

# Architecture layer
mkdir -p docs/architecture/decisions
mkdir -p docs/architecture/research

# Ops layer
mkdir -p docs/ops/runbooks
mkdir -p docs/ops/rcas

# Pre-PRD ideas
mkdir -p docs/ideas

# Reports
mkdir -p var/reports/metamodel-audit
mkdir -p var/reports/metamodel-migration
mkdir -p var/reports/open-items

# Open-items control plane
mkdir -p project-control/open-items/archive
```

**Omitted vs Greenfield:**
- `docs/business/01b-competitive-landscape/` — competitive landscape is context-only for brownfield
- `docs/business/discovery/` — assume stakeholder interviews already exist elsewhere
- `docs/communication/slides/` — add later if needed

**Total leaf directories (brownfield):** ~15

---

## Variant C — Strategy-only (investor / executive engagement)

Business architecture layer only. No product specs, no domain model, no ops. Add
quantitative models (TAM/SAM/SOM) and competitive landscape — both are common in strategy
decks and investor materials.

```bash
# Business architecture layer
mkdir -p docs/business/06a-models
mkdir -p docs/business/01b-competitive-landscape

# Communication layer (slide decks for investor / exec presentations)
mkdir -p docs/communication/slides

# Reports
mkdir -p var/reports/metamodel-audit
```

**Omitted vs Greenfield:**
- `docs/business/05a-processes/` — operational detail not needed for strategy-only
- `docs/business/discovery/` — research is out of scope for pure strategy work
- `docs/domain/` — no DDD work
- `docs/product-specs/` — no feature specs
- `docs/exec-plans/` — no implementation plans
- `docs/architecture/` — no ADRs
- `docs/ops/` — no ops artefacts
- `docs/ideas/` — not applicable

**Total leaf directories (strategy-only):** ~4

---

## Variant D — Single-feature (no full architecture)

Product specs and exec-plans only. Useful when a single PRD + plan is all that's needed.
Includes architecture/decisions for the ADRs that typically accompany any non-trivial
feature.

```bash
# Product specs layer
mkdir -p docs/product-specs/prds

# Execution plans layer
mkdir -p docs/exec-plans/active

# Architecture layer (ADRs only — research optional)
mkdir -p docs/architecture/decisions

# Pre-PRD ideas
mkdir -p docs/ideas

# Reports
mkdir -p var/reports/metamodel-audit
```

**Omitted vs Greenfield:**
- Entire `docs/business/` subtree — no strategic architecture
- `docs/domain/` — no DDD work
- `docs/ops/` — no ops artefacts
- `docs/communication/` — no slide decks

**Total leaf directories (single-feature):** ~5

---

## Variant promotion guide

Start on a smaller variant and want to grow? Add the missing folders by running
`util-metamodel-scaffold` Mode 2 again with the larger variant — `mkdir -p` is idempotent
and won't overwrite existing content.

| From | To | Folders to add |
|---|---|---|
| Single-feature | Brownfield | `docs/business/` tree (B variant commands) + `docs/domain/` |
| Single-feature | Greenfield | All greenfield commands |
| Brownfield | Greenfield | `docs/business/01b-competitive-landscape/` · `docs/business/discovery/` · `docs/communication/` |
| Strategy-only | Greenfield | All non-business folders from greenfield commands |
