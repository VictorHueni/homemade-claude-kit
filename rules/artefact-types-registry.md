---
paths:
  - "docs/**"
  - "rules/artefact-types-registry.md"
---

# Artefact Types Registry — structural definitions

This rule is the **single structural source of truth** for every artefact type the kit
mints. It is the *structural half* of the two-layer split decided in
clew [ADR-0006](../../clew/docs/architecture/decisions/adr-0006-canonical-home-for-artefact-type-definitions.md):

- **Structural facts** (id format, file layout, default path, review interval, frontmatter
  conditionals, property-schema reference) → **this file**.
- **Semantic facts** ("what *is* a persona, when to use it, anti-patterns, examples") →
  a `## Canonical definition` section in each minting `SKILL.md`.

Build-order and dependency facts stay in [`metamodel.md`](metamodel.md); this file does
**not** restate them (ADR-0006 rejected widening `metamodel.md` into a vocabulary
registry). clew's `ARTEFACT_TYPE_CONFIGS` is the runtime consumer that **derives from**
this table; per ADR-0006 Phase 4 a clew test asserts the two match, so config drift
becomes a CI failure.

---

## Registry

One row per artefact type. `type` is the snake_case identifier used in
`ARTEFACT_TYPE_CONFIGS`. `id_format` is a regex. `layout` is one of `single-collection`
(many instances in one file), `one-per-artefact` (one file per instance), or
`inherits-from-parent` (file binding inherited from `parent`, per ADR-0002).

| type | minting skill | id_format | layout | default_path | review_interval | frontmatter_conditionals | property_schema_ref |
|---|---|---|---|---|---|---|---|
| `vision` | `business-vision` | _(singleton — no ID)_ | one-per-artefact ¹ | `docs/VISION.md` | `180d` | — | _TBD_ |
| `persona` | `business-persona` | `P-\d{2}` | single-collection | `docs/business/01a-personas.md` | `180d` | — | _TBD_ ² |
| `canvas` | `business-model-canvas` | _(slug)_ | one-per-artefact | `docs/business/02a-{slug}.md` | `90d` | — | _TBD_ |
| `bmc_block` | `business-model-canvas` | `[A-Z]{2}-\d+` | inherits-from-parent (`canvas`) | _(inherits canvas)_ | `90d` | — | _TBD_ |
| `capability` | `business-capability-map` | `C\d+(\.\d+){0,2}` | single-collection | `docs/business/03a-capability-map.md` | `180d` | — | _TBD_ ² |
| `value_stream` | `business-value-stream` | `VS-\d+` | single-collection | `docs/business/04a-value-streams.md` | `90d` | — | _TBD_ |
| `vs_stage` | `business-value-stream` | `VS-\d+\.\d+` | inherits-from-parent (`value_stream`) | _(inherits value_stream)_ | `90d` | — | _TBD_ |
| `objective` | `business-objective` | `OBJ-\d{2}` | single-collection | `docs/business/04b-objectives.md` | `60d` | — | _TBD_ ² |
| `key_result` | `business-objective` | `KR-\d{2}\.\d+` | inherits-from-parent (`objective`) | _(inherits objective)_ | `60d` | — | _TBD_ ² |
| `process` | `business-process` | _(slug)_ | one-per-artefact | `docs/business/05a-processes/proc-{nn}-{slug}.md` | `90d` | — | _TBD_ |
| `quantitative_model` | `business-quantitative-model` | _(slug)_ | one-per-artefact | `docs/business/06a-models/qm-{nn}-{topic}.md` | `90d` | — | _TBD_ |
| `competitor` | `business-competitive-landscape` | `CO-\d{2}` | one-per-artefact ³ | `docs/business/01b-competitive-landscape/{slug}.md` | `90d` | — | _TBD_ |
| `bounded_context` | `domain-bounded-context` | `BC-\d{2}` | single-collection ⁴ | `docs/domain/02b-bounded-contexts.md` | `180d` | — | _TBD_ |
| `glossary_term` | `domain-glossary` | `BC-\d{2}\.GT-\d{2}` | single-collection ⁴ | `docs/domain/02c-glossary.md` | `180d` | — | _TBD_ |
| `fbs_functionality` | `spec-functional-breakdown-structure` | `C\d+\.\d+\.F\d{2}` | single-collection ⁵ | `docs/product-specs/07a-fbs.md` | `90d` | — | _TBD_ ² |
| `domain_model` | `domain-model` | _(per-BC file; elements below)_ | one-per-artefact (per BC) ⁶ | `docs/domain/07b-models/{bc-slug}.md` | `180d` | — | _TBD_ |
| `aggregate` | `domain-model` | `BC-\d{2}\.AGG-\d{2}` | inherits-from-parent (`domain_model`) ⁶ | _(inherits domain_model)_ | `180d` | — | _TBD_ |
| `entity` | `domain-model` | `BC-\d{2}\.ENT-\d{2}` | inherits-from-parent (`domain_model`) ⁶ | _(inherits domain_model)_ | `180d` | — | _TBD_ |
| `value_object` | `domain-model` | `BC-\d{2}\.VO-\d{2}` | inherits-from-parent (`domain_model`) ⁶ | _(inherits domain_model)_ | `180d` | — | _TBD_ |
| `domain_event` | `domain-model` | `BC-\d{2}\.EVT-\d{2}` | inherits-from-parent (`domain_model`) ⁶ | _(inherits domain_model)_ | `180d` | — | _TBD_ |
| `interface_contract` | `arch-service-contract` | `(BC-\d{2}\.)?CTR-\d{2}` | one-per-artefact | `docs/architecture/interfaces/{bc-slug}.md` | `90d` ⁷ | — | _TBD_ |
| `epic` | `spec-delivery-roadmap` | `E-\d{2}` | single-collection | `docs/product-specs/08a-delivery-roadmap.md` | `60d` | — | _TBD_ ² |
| `cli_surface` | `arch-cli-contract` | `(BC-\d{2}\.)?CLI-\d{2}` | one-per-artefact | `docs/architecture/interfaces/cli-{slug}.md` | `90d` ⁷ | — | _TBD_ |
| `cli_command` | `arch-cli-contract` | `(BC-\d{2}\.)?CLI-\d{2}\.CMD-\d{2}` | inherits-from-parent (`cli_surface`) | _(inherits cli_surface)_ | `90d` ⁷ | — | _TBD_ |
| `quality_attribute` | `spec-quality-attributes` | `QA-[A-Z]{2}\d{2}` | single-collection | `docs/product-specs/09a-quality-attributes.md` | `60d` | — | _TBD_ |
| `use_case` | `spec-use-case` | `UC-\d{2}` | one-per-artefact | `docs/product-specs/use-cases/uc-{nn}-{slug}.md` | `60d` ⁷ | — | _TBD_ |
| `prd` | `spec-prd` | `PRD-\d{4}` | one-per-artefact | `docs/product-specs/prds/prd-{nnnn}-{feature}.md` | `30d` | — | _TBD_ |
| `implementation_plan` | `spec-implementation-plan` | `Plan-\d{4}` | one-per-artefact | `docs/exec-plans/active/{nnnn}_exec_{slug}.md` | `30d` | — | _TBD_ |
| `adr` | `arch-adr` | `ADR-\d{4}` | one-per-artefact | `docs/architecture/decisions/adr-{nnnn}-{slug}.md` | `180d` | `supersedes`, `superseded_by` | _TBD_ |
| `research` | `arch-research` | `Research-\d{4}` | one-per-artefact | `docs/architecture/research/{nnnn}-{slug}.md` | `90d` | — | _TBD_ |
| `idea` | `discovery-idea` | `IDEA-\d{4}` | one-per-artefact | `docs/discovery/ideation/IDEA-{nnnn}-{slug}.md` | `90d` | `graduates_to` | _TBD_ |

---

## Provenance & precedence

Each column has exactly one upstream source; this table consolidates them (no new facts):

| Column | Source of truth |
|---|---|
| `id_format` | [`metamodel.md` §Cross-doc ID conventions](metamodel.md) |
| `default_path` | [`metamodel.md` §Canonical output paths](metamodel.md) |
| `layout`, `parent` | clew [ADR-0002](../../clew/docs/architecture/decisions/adr-0002-artefact-file-binding.md) §Layout taxonomy |
| `review_interval` | [`artefact-frontmatter.md` §Default review intervals](artefact-frontmatter.md) |
| `frontmatter_conditionals` | [`artefact-frontmatter.md`](artefact-frontmatter.md) (universal `supersedes`/`superseded_by` are *not* listed here — only per-type extras) |
| `property_schema_ref` | clew Pydantic models (`schema.py`) — `_TBD_` until clew Phase 2 lands them |

On conflict, the source column above wins; fix the source, then re-derive this row.

---

## Known discrepancies & open items

Flagged rather than silently resolved (this registry is meant to *surface* drift):

1. **¹ `vision` layout** — a singleton (one file, no minted ID) does not map cleanly onto
   the three-category enum; recorded as `one-per-artefact` with one instance. A dedicated
   `singleton` category may be warranted (would require the `schema.py` `FileLayout`
   change ADR-0002 §Negative anticipates).
2. **² `property_schema_ref`** — clew's [`artefact-store.md` §Property schemas](../../clew/docs/domain/07b-models/artefact-store.md) already *sketches* fields for
   `persona`, `capability`, `fbs_functionality`, `epic`, `objective`, `key_result`, but no
   Pydantic model exists yet anywhere, so all refs read `_TBD_` until clew Phase 2.
3. **³ `competitor` path/layout** — `metamodel.md` describes a
   `docs/business/01b-competitive-landscape/` directory but does not pin a per-profile
   filename; `{slug}.md` + `one-per-artefact` is assumed. Confirm against the
   `business-competitive-landscape` skill output.
4. **⁴ bounded-context / glossary path conflict** — clew **ADR-0002** specs
   `bounded-context` as `one-per-artefact` at `docs/domain/contexts/{slug}.md` and glossary
   at `docs/domain/glossary.md`, but `metamodel.md` (and the actual clew repo) use
   single-file `02b-bounded-contexts.md` / `02c-glossary.md`. This registry follows
   `metamodel.md`/repo reality (`single-collection`). **ADR-0002 §Layout taxonomy is stale
   and should be updated** to match.
5. **⁵ `fbs_functionality`** — file layout is `single-collection` (all functionalities live
   in `07a-fbs.md`), even though its *ID* is parented on `capability` (`C-N.M.FXX`). ID
   parentage ≠ file parentage.
6. **⁶ domain-model elements** — `aggregate`/`entity`/`value_object`/`domain_event` live in a
   per-BC file (`07b-models/{bc-slug}.md`) that is itself one-per-BC. They are modelled as
   `inherits-from-parent` of a synthetic `domain_model` row, but this is the one case that
   strains ADR-0002's 3-category enum (the parent file is keyed by BC, not by another
   minted artefact). A 4th layout category or a BC-keyed binding may be the cleaner fix.
7. **⁷ review_interval not in the frontmatter table** — `interface_contract`, `cli_surface`,
   `cli_command`, and `use_case` are absent from
   [`artefact-frontmatter.md` §Default review intervals](artefact-frontmatter.md);
   nearest-analogue values are assigned here and must be ratified by adding rows to that
   rule.
8. **c4 / arc42 diagram-ID types stay out (decided 2026-06-11)** — `SYS/CON/CMP/DN`
   (`arch-c4`), `SCN/CST/CC/RSK` (`arch-arc42`), and `Inc-N` (plan increment) mint IDs but
   are diagram / figure / sub-element identifiers, **not clew-persisted artefact types**.
   They remain defined in `metamodel.md` §Cross-doc ID conventions, not here — that section
   was trimmed to keep only those non-artefact IDs. This registry covers artefact types only.
9. **clew `ARTEFACT_TYPE_CONFIGS` derivation** — per ADR-0006 Phase 4, clew must derive its
   runtime config from this table and assert equality in CI. Not yet wired (clew has no
   code yet).

---

## Maintenance coupling

When a new artefact type lands (or an existing one changes id/path/layout):

| What changed | Update |
|---|---|
| New type, or id/path/layout change | **this file** (the structural row) |
| New type's semantics | the minting `SKILL.md` `## Canonical definition` (ADR-0006 Phase 3) |
| Build-order / dependency / ER | [`metamodel.md`](metamodel.md) (+ its own §Maintenance coupling fan-out) |
| New review interval | [`artefact-frontmatter.md`](artefact-frontmatter.md) §Default review intervals |
| Runtime enforcement | clew `ARTEFACT_TYPE_CONFIGS` (must re-derive from this file) |

---

## Changelog

- 2026-06-11 · Initial registry created (closes clew ADR-0006 `OI-0024`). Structural rows
  backfilled from `metamodel.md` (ids, paths), ADR-0002 (layout), and
  `artefact-frontmatter.md` (review intervals). Nine known discrepancies flagged above.
