---
title: arc42 Ownership by Content Type — Generators Emit Figures and Derived Tables, arc42 Owns All Narrative
status: active
owner: Victor Hueni
last_reviewed: 2026-06-09
review_interval: 180d
---

# arc42 Ownership by Content Type — Generators Emit Figures and Derived Tables, arc42 Owns All Narrative

Date: 2026-06-09

## Context and Problem Statement

The kit produces the arc42 architecture document through three skills with overlapping reach:

- **`arch-c4`** edits the Structurizr DSL model, renders C4 SVGs, **and writes the arc42 prose** for §3 (Context), §5 (Building Blocks), §6 (Runtime), §7 (Deployment) — diagram and prose coupled in one mode.
- **`arch-arc42`** writes the narrative sections that have no C4 counterpart: §2, §4, §8, §11.
- **`arch-uml`** is a pure diagram producer (sequence, class, state, activity, ER, use-case → committed SVG under `docs/architecture/diagrams/`), minting no IDs and embedding into whatever markdown consumes it.

Two problems follow from this layout:

1. An `arch-uml` sequence / class / state diagram is the natural figure for arc42 §6 (runtime) and §8 (cross-cutting), yet **no skill wires `arch-uml` output into arc42** — a UML figure can sit orphaned in `views/`, and §6 has no path to richer-than-C4 sequence detail.
2. `arch-c4` bundles two *different kinds* of content under one owner. Within §3/§5/§7 the **table** (container/component rows: responsibility, tech, `Domain aggregates implemented`, `Code path`) is *mechanically derived from `workspace.dsl`*, but the **surrounding narrative** (motivation for the decomposition, how blocks relate to other sections) is *authored architectural judgment*. Treating the whole section as one ownership unit fragments the document's narrative voice across `arch-c4` and `arch-arc42` for no structural reason.

The question this ADR settles: **what is the right unit of ownership for arc42 content, and how do generated figures/tables join authored prose without drifting?**

## Decision Drivers

- **Ownership should follow content type, not section boundaries.** Derived content (a table that is a projection of the DSL model, a rendered SVG) and authored content (narrative, rationale, cross-section coherence) have different sources of truth and should be owned by different skills even when they share a file.
- **Never make the document author re-parse a diagram toolchain.** Whoever writes arc42 narrative must not have to read `workspace.dsl` to rebuild a table — the generator that owns the model already has it in hand.
- **Single narrative voice.** One author for all arc42 prose (every section) keeps voice, ordering, and cross-references (§5 ↔ §6 ↔ §8) coherent.
- **Drift control as a detective overlay.** Coupling prevents drift at write time but blocks reuse; an explicit declared dependency + audit catches drift after the fact and is cheap. Use each where it fits.
- **Reusable figures.** `arch-uml` diagrams are embedded by many consumers (use-cases, domain, processes, *and* arc42); the producer must stay free of any one consumer's document format.
- **Soft-reference discipline.** Consistent with the kit DAG hard rule ("B can be scaffolded without A existing"), declared dependencies must be audit-surfaced warnings, never build-blocking prerequisites.
- **No monster skills.** One skill minting `SYS/CON/CMP/DN/SCN/CST/CC/RSK` with two embed pipelines violates the kit's mode-per-artefact granularity.

## Decision Outcome

Chosen option: **Option 1 — ownership by content type.**

The rule, stated once and applied uniformly across every arc42 section:

> **Derived content** (C4 diagram + the table extracted from `workspace.dsl`) is **generated** by `arch-c4` and lands as a *fenced generated block* inside the arc42 file. **Authored content** (all narrative, every section, plus runtime-scenario identity) is owned by `arch-arc42`. **Figures that illustrate** authored sections (§6/§8) are produced by `arch-uml` (or a C4 dynamic view) and joined to the prose by a *declared dependency*, never by co-authoring. An **audit** verifies both joins.

Resulting ownership:

| arc42 content | Producer | Lands as |
|---|---|---|
| C4 diagram + DSL-derived table (§3 context tables, §5 container/component tables, §7 deployment table) | `arch-c4` | fenced generated block (`<!-- arch-c4:table:start … end -->`) inside the arc42 section file |
| Runtime / cross-cutting figure (§6 sequence, §8 class/state/ER) | `arch-uml`, or a C4 **dynamic** view from `arch-c4` | committed SVG in `diagrams/views/` (or `c4/views/`), referenced by a declared-dependency block |
| **All narrative, every section (§2–§8, §11), plus `SCN-NN` scenario identity** | `arch-arc42` | the arc42 prose itself |

`arch-c4` thereby becomes a **pure generator** — diagrams plus the tables derived from them — authoring narrative *nowhere*. This is the full segregation ("split even for C4") **without** forcing `arch-arc42` to re-parse the DSL: `arch-c4` still performs the DSL→table extraction it always did; it merely confines its output to a fenced block instead of writing a whole section.

**Two join mechanisms, two audit duties:**

- **Fenced generated region** (derived tables): `arch-c4` rewrites *only* between its markers; `arch-arc42` owns everything outside them. The audit checks the markers are present and the table between them is in sync with the DSL (every `CON-NN` has a row; no stale rows).
- **Declared dependency** (figures): an arc42 §6/§8 subsection declares `scenario`/`realises`/`figure`/`figure_source`. The audit checks the figure path resolves, the SVG is not orphaned, and the upstream IDs the figure carries (`SCN-NN`, `UC-NN`, `BC-NN.AGG-NN`) still resolve in their owning artefacts. A freshness signal (SVG re-rendered after the section's `last_reviewed`) is **info-level only** — it hints at possible prose drift without failing.

**`SCN-NN` ownership (resolves the prior open item):** the runtime scenario is a §6 concept, so **`arch-arc42` mints `SCN-NN`**. `arch-c4`'s dynamic-view capability becomes a *figure producer keyed by a given `SCN-NN`*, exactly like `arch-uml`.

**§6 figure boundary rule:** use a **C4 dynamic view** for cross-container flows tied to the C4 model; use an **`arch-uml` sequence** for intra-component / algorithmic detail the C4 model does not carry. Intra-aggregate state machines never appear in §6 (they are §8, via `arch-uml state`).

### Positive Consequences

- Clean separation: `arch-c4` = pure generator, `arch-arc42` = sole narrative author. One voice across the whole document; cross-section references managed by one owner.
- `arch-arc42` never touches Structurizr — the full-split benefit with none of the re-parse cost.
- `arch-uml` stays a single-responsibility producer, reusable across use-cases, domain, processes, and arc42.
- The orphan/drift gap closes for both content kinds: figures via declared-dependency checks, tables via marker-sync checks.
- `SCN-NN` ownership is unambiguous; no section is "co-owned" in the sense of two authors fighting over the same prose.

### Negative Consequences

- **Two writers, one file** for §3/§5/§7. The fenced-marker contract must be airtight or one skill clobbers the other's content — so the **audit is load-bearing, not optional**. Mitigated: the markers are simple and the boundary is unambiguous.
- A §3/§5/§7 authoring session may now involve **two skill invocations** (`arch-c4` for the table block, `arch-arc42` for the narrative) instead of one.
- arc42 doctrine keeps §5 narrative deliberately thin, so for many sections the generated table + figure *is* nearly the whole section and arc42's wrapper is a few sentences — the narrative/table split can feel like ceremony where prose is sparse. Accepted: arc42 still owns those sentences and the cross-references.
- Coupling to update: `rules/metamodel.md` (`SCN-NN` owner `arch-c4`→`arch-arc42`, the three skill bullets, Check-7 dependency rule, canonical-paths note, changelog), `README.md`, the §3/§5/§7 and §6/§8 templates (markers + dependency block), and `util-metamodel-audit/references/check-catalogue.md` (figure + marker checks).
- `arch-c4`'s SKILL modes are redefined from "write §N section" to "render diagram + emit table block."

## Pros and Cons of the Options

### Option 1 — Ownership by content type (chosen)

`arch-c4` emits diagrams + fenced derived tables; `arch-arc42` owns all narrative + scenario IDs; figures joined by declared dependency; audit guards both.

#### Positive

- The single most consistent rule — every skill produces exactly what it can mechanically derive or is the authority for.
- Full C4 segregation without DSL re-parsing; single document voice; reusable producers.
- Resolves `SCN-NN` and the figure-orphan gap together.

#### Negative

- Introduces the two-writers-one-file pattern (fenced markers) and makes the audit load-bearing.
- More invocations per section; thin-narrative sections gain a little ceremony.

### Option 2 — Section-level ownership (the earlier Level-1 draft)

`arch-c4` keeps whole §3/§5/§7 (table *and* narrative); only §6 moves to `arch-arc42`.

#### Positive

- One skill, one section, one invocation for §3/§5/§7 — no fenced-marker machinery.
- Less coupling churn than Option 1.

#### Negative

- Bundles *authored* narrative with *derived* tables under the generator — inconsistent with the content-type principle.
- Narrative voice stays fragmented across `arch-c4` and `arch-arc42`; cross-section coherence has two owners.

### Option 3 — Full split with arc42 re-parsing the DSL

Generators emit only SVGs; `arch-arc42` writes all prose *and* rebuilds the tables from `workspace.dsl`.

#### Positive

- Maximum symmetry; one author literally writes every character of arc42.

#### Negative

- Couples the document author to the Structurizr toolchain — worse coupling than today.
- Two-step regenerate-then-re-pull dance on every model change → drift hazard.

### Option 4 — Status quo

Keep §6 in `arch-c4`; never wire `arch-uml` into arc42.

#### Positive

- Zero work.

#### Negative

- `arch-uml` figures stay orphaned; §6 has no richer-sequence path; the C4/UML-as-source question stays open and will be re-raised.

## Open Items

None at present. (`SCN-NN` ownership — the only prior open item — is resolved in the Decision Outcome: minted by `arch-arc42`.)
