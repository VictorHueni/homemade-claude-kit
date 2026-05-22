# Path Migration v2 — Canonical Paths Mapping Table

This file is the single source of truth for the v1 → v2 metamodel path simplification.

- **v1 paths:** nested subfolders with redundant names (e.g. `personas/personas.md`)
- **v2 paths:** numbered flat files for singletons; multi-file artefacts unchanged

Used by `util-metamodel-migration` Mode 4 to generate project migration scripts.
Used by the kit maintainer as the authoritative reference when updating skill files.

---

## Naming convention (v2)

| Context | Pattern | Example |
|---|---|---|
| Primary singleton (business / spec) | `docs/{layer}/NNa-{slug}.md` | `docs/business/01a-personas.md` · `docs/product-specs/07a-fbs.md` |
| Fractional / sub-step artefact | `docs/{layer}/NNb-{slug}.md` · `NNc-{slug}.md` ... | `docs/business/04b-objectives.md` · `docs/domain/02c-glossary.md` |
| BMC / VS companion VPC | `docs/business/NNa-vpc-{segment}.md` | `docs/business/02a-vpc-enterprise.md` |
| Domain singleton (sub-step) | `docs/domain/NNX-{slug}.md` | `docs/domain/02b-bounded-contexts.md` · `docs/domain/02c-glossary.md` |
| Domain model (per BC) | `docs/domain/models/{bc-slug}.md` | `docs/domain/models/scheduling.md` |
| Multi-file artefact folder (step-scoped) | `docs/business/NNa-{slug}/` | `docs/business/06a-models/{slug}.md` |
| Multi-file artefact (slug, no step prefix) | unchanged | `docs/business/processes/{slug}-process.md` |
| Numbered multi-file artefact | unchanged | `docs/product-specs/prd-{NNNN}-{feature}.md` |

**Rules:**
- Step numbers zero-pad to 2 digits **plus a letter** to identify ordering: `01a`, `02a`, `03a`, `04a`, `07a`, `08a`, `09a` (primary singleton at each step).
- The `a` letter is **explicit, not implicit** — `01a-personas.md` (primary), `01b-…` (secondary at the same step), `01c-…` (tertiary), etc. This avoids visual ambiguity where bare `01-` would silently mean "step 1 primary" alongside other `01b-` siblings.
- **Fractional / sub-step artefacts** use letter increments: `04b` (between Step 4 and Step 5), `02b` / `02c` (Bounded Contexts and Glossary as sub-steps of Step 2's Capability-Map area).
- **Domain singletons keep the step-letter prefix** (e.g. `02b-bounded-contexts.md`, `02c-glossary.md`). Sub-step letters are the discriminator that distinguishes them from primary singletons at the same parent step.
- **Multi-file artefact folders** use the step-letter prefix on the FOLDER (e.g. `06a-models/`), and the files inside follow the originating skill's own naming (funnel `1a-`, `1b-`, `2a-` for quantitative models — no step collision because the parent folder scopes them).
- **Domain model files** (`docs/domain/models/{bc-slug}.md`) skip the step prefix — the `bc-slug` itself is the scoping discriminator; adding `07b-` to every file would be redundant.
- `docs/VISION.md` stays at root regardless of numbering — agent context visibility takes priority over filesystem ordering.

---

## Full before → after mapping

| Step | Artefact | v1 path (old) | v2 path (new) | Type |
|---|---|---|---|---|
| 0 | Product Vision | `docs/VISION.md` | `docs/VISION.md` | no-change |
| 1 | Personas | `docs/business/personas/personas.md` | `docs/business/01a-personas.md` | singleton |
| 2 | Business Model Canvas | `docs/business/business-model-canvas/business-model-canvas.md` | `docs/business/02a-bmc.md` | singleton |
| 2 | Lean Canvas (variant) | `docs/business/business-model-canvas/lean-canvas.md` | `docs/business/02a-lean-canvas.md` | singleton |
| 2 | BMC Value Proposition Canvas | `docs/business/business-model-canvas/value-proposition-canvas-{segment}.md` | `docs/business/02a-vpc-{segment}.md` | multi-slug |
| 2b | Bounded Contexts | `docs/domain/bounded-contexts/bounded-contexts.md` | `docs/domain/02b-bounded-contexts.md` | singleton |
| 2b | Context Map | `docs/domain/bounded-contexts/context-map.md` | `docs/domain/02b-context-map.md` | singleton |
| 2c | Domain Glossary | `docs/domain/glossary/glossary.md` | `docs/domain/02c-glossary.md` | singleton |
| 3 | Capability Map | `docs/business/capability-map/capability-map.md` | `docs/business/03a-capability-map.md` | singleton |
| 4 | Value Streams | `docs/business/value-streams/value-streams.md` | `docs/business/04a-value-streams.md` | singleton |
| 4 | VS Value Proposition Canvas | `docs/business/value-streams/value-proposition-canvas-{segment}.md` | `docs/business/04a-vpc-{segment}.md` | multi-slug |
| 4b | Business Objectives | `docs/business/objectives/objectives.md` | `docs/business/04b-objectives.md` | singleton |
| 5 | Business Processes | `docs/business/processes/{slug}-process.md` | `docs/business/05a-processes/proc-NN-{slug}.md` | singleton-folder (Pattern B inside) |
| 6 | Quantitative Models | `docs/business/models/{slug}.md` | `docs/business/06a-models/qm-NN-{topic}.md` | singleton-folder (Pattern B inside) |
| 6 (supporting) | Competitive Landscape | `docs/business/competitive-landscape/competitive-landscape.md` | `docs/business/01b-competitive-landscape/cl-NN-{slug}.md` + `CO-NN-{slug}.md` for competitor profiles | singleton-folder (Pattern B inside) |
| 7 | FBS | `docs/product-specs/functional-breakdown-structure/FBS.md` | `docs/product-specs/07a-fbs.md` | singleton |
| 7b | Domain Model (per BC) | `docs/domain/{bc-slug}/domain-model.md` | `docs/domain/07b-models/{bc-slug}.md` | singleton-folder (Pattern B inside) |
| 8 | Delivery Roadmap | `docs/product-specs/delivery-roadmap/delivery-roadmap.md` | `docs/product-specs/08a-delivery-roadmap.md` | singleton |
| 9 | Quality Attributes | `docs/product-specs/quality-attributes/quality-attributes.md` | `docs/product-specs/09a-quality-attributes.md` | singleton |
| 10 | PRDs | `docs/product-specs/{NNNN}_prd_{feature}.md` | `docs/product-specs/prd-{NNNN}-{feature}.md` | pattern-b-rename |
| 11 | Implementation Plans | `docs/exec-plans/active/{NNNN}_{slug}/` | `docs/exec-plans/active/{NNNN}_{slug}/` | no-change |
| — | ADRs | `docs/architecture/decisions/{NNNN}-{slug}.md` | `docs/architecture/decisions/adr-{NNNN}-{slug}.md` | pattern-b-rename |
| — | Ops Runbooks | `docs/ops/runbooks/{slug}.md` | `docs/ops/runbooks/{slug}.md` | no-change |
| — | Ops RCAs | `docs/ops/rcas/{YYYY-MM-DD}-{slug}.md` | `docs/ops/rcas/{YYYY-MM-DD}-{slug}.md` | no-change |
| — | Ideas | `docs/ideas/{slug}.md` | `docs/ideas/{slug}.md` | no-change |

---

## Mode 4 implementation notes

### Variable substitution rules

When matching v1 paths containing variables:

| Variable | What it matches | v2 treatment |
|---|---|---|
| `{slug}` | kebab-case file name (e.g. `my-process`) | Pass through unchanged |
| `{segment}` | customer segment slug | Pass through unchanged |
| `{bc-slug}` | bounded context slug (e.g. `scheduling`) | In v2 domain models: **becomes the filename** — `docs/domain/my-bc/domain-model.md` → `docs/domain/models/my-bc.md` |
| `{NNNN}` | 4-digit zero-padded number | Pass through unchanged |
| `{YYYY-MM-DD}` | date string | Pass through unchanged |

### Relative path recomputation

When a file moves, all inbound `[text](path)` links must be recomputed. **Do NOT string-substitute `../` chains** — the depth change makes simple substitution wrong.

Instead, for each linking file `L` and each moved file `F`:
```python
import os
new_rel = os.path.relpath(F_new_abs, os.path.dirname(L_abs))
# Replace old_rel with new_rel in L
```

Depth change examples:
- `docs/business/personas/personas.md` (depth 3) → `docs/business/01a-personas.md` (depth 2)
  - A link from `docs/product-specs/07a-fbs.md` was `../business/personas/personas.md`
  - After move: `../business/01a-personas.md` (loses one `../`)
- `docs/domain/glossary/glossary.md` (depth 3) → `docs/domain/02c-glossary.md` (depth 2)
  - A link from `docs/domain/models/scheduling.md` was `../glossary/glossary.md`
  - After move: `../02c-glossary.md`

### Domain model consolidation (special case)

The v1 pattern `docs/domain/{bc-slug}/domain-model.md` creates one folder per BC.
The v2 pattern `docs/domain/models/{bc-slug}.md` consolidates into a single folder.

Detection:
```bash
find docs/domain -mindepth 2 -name "domain-model.md" | while read f; do
  bc_slug=$(basename $(dirname "$f"))
  echo "mv: $f -> docs/domain/models/${bc_slug}.md"
done
```

Also check for other files in the `docs/domain/{bc-slug}/` folders before deleting them.
If any non-domain-model files are present, report as a warning and skip folder deletion.

### VISION.md — no action needed

`docs/VISION.md` stays at the root. No move, no link rewriting for VISION.md itself.
However, if Mode 4 finds any link pointing to `docs/VISION.md` using a nested path
(e.g. `../VISION.md` from inside `docs/business/`), verify the relative path is still
correct after the business-layer files move (it should be, since VISION.md doesn't move).
