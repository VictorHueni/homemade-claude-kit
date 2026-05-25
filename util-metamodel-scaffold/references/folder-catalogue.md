# Folder Catalogue — util-metamodel-scaffold

The single canonical folder list. Claude reads this file during scaffold execution to know
which `mkdir -p` commands to run. Every project gets the full tree — empty folders cost
nothing and the audit checks for files, not folders.

All paths are relative to the project root. `{docs_root}` defaults to `docs/`.

---

## Full canonical tree

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

**Total directories:** ~21
