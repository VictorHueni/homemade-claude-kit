# Metamodel impact assessment

Run before publishing any skill change. Stage 1 decides which Stage 2 applies, so it prevents both updating everything for a utility and missing the wiring for a real artefact.

## Stage 1 — Classify

> Does this skill produce a new named artefact that other skills or agents need to know about and reference?

| Classification | Meaning | Examples | Next |
|---|---|---|---|
| **New metamodel step** | A new artefact type with its own step in the build order; other skills read or reference it | `business-vision`, `business-objective` | Stage 2A |
| **Variant or refinement** | A skill for an artefact type that already exists; no new step, no new IDs | a review skill for PRDs, a canvas variant | Stage 2B |
| **No metamodel impact** | Workflow, housekeeping, or an operational artefact nothing references | `dev-*`, `util-*`, `ops-runbook`, `ops-bug-rca` | Stage 2C |

If you catch yourself saying "other skills should read this first" or "PRDs should reference this ID", it is a new step.

## Stage 2A — New artefact step

Run it before writing the skill and show the owner the blast radius first.

### Design questions

1. **Output path**, and whether it breaks the prefix → folder rule (`business-vision` writes `docs/VISION.md`).
2. **IDs minted** (`OBJ-NN`, `KR-NN.M`), or a singleton referenced by path.
3. **Modes** (scaffold, fill, align, refresh, wire) and what each does.
4. **References**: `template.md` (output skeleton), `methodology-references.md` (bibliography), a discipline file (internal guidance).
5. **Writes outside `docs/`** (for example `CLAUDE.md`): set `metadata.impact: "medium"`.

### Structural facts go to clew first

The clew repo owns the structural and relational metamodel (ADR-0007, clew ADR-0008). Add a new artefact type, ID format, path or relationship to clew's `docs/metamodel/` first, then sync it into the kit's `metamodel` skill.

### Files to update

**`plugins/kit-core/skills/metamodel/`:**

| Change | File |
|---|---|
| Registry entry (`id_format`, layout, `default_path`, `review_interval`, `okf_type`), synced from clew; Audit, Scaffold and Migrate derive from it | `references/artefact-types-registry.yaml` |
| Spine table count and row | `SKILL.md` |
| `### Step N` (skill, prerequisites, modes, output verification) | `references/metamodel-reference.md` |
| DAG node and edges, ER entity and relationships | `references/metamodel-reference.md` |
| Sub-element ID conventions (artefact-type IDs live in the registry); a minted sub-element ID also goes into Check 5's curated table | `references/metamodel-reference.md`, `references/modes/audit-check-catalogue.md` |
| Canonical `docs/` paths tree, and any prefix exception | `references/metamodel-reference.md` |

Record the change in clew's maintenance log; the kit's `docs/project-control/metamodel-changelog.md` is a parked digest, no longer updated.

**README:** the skill count in the intro line and the set's row in the Plugin sets table.

**Upstream reads:** each existing skill that should read the new artefact before its own work gets a "read it if present" line in its context step. An artefact upstream of everything (vision) goes into every `business-*` and `spec-*` skill; a mid-stack one (objectives) only into the skills it guides (roadmap, PRDs, quality attributes).

**Downstream references:** each skill whose output should cite the new IDs or path gets them in its traceability block (PRDs, implementation plans), epic template (roadmap), cross-references (quality attributes) or soft-links table (canvas, objectives).

**Audit and Migrate** derive path, placement, ID and `okf_type` checks from the registry. Touch only:

| File | When |
|---|---|
| `references/modes/audit-check-catalogue.md` | A Check 7 dependency rule, a Check 9 mandatory-sections pattern, or a Check 5 sub-element ID |
| `references/modes/migrate-detection-signals.md` | Fuzzy-name heuristics (synonyms, legacy names) beyond the derived baseline |

### After building

Run the naming check in `naming.md`, then `./install.sh`, and confirm the skill is served (`ls ~/.codex/skills/<name>`, or the plugin cache on a marketplace machine).

## Stage 2B — Variant or refinement

| Changed | Update |
|---|---|
| Output path | clew first, then the registry `default_path` and the paths tree in `metamodel-reference.md` |
| New ID format | clew first, then the registry `id_format`; sub-element IDs also go to Check 5 |
| Prerequisite added or removed | DAG and build-order step in `metamodel-reference.md`, Check 7 in `audit-check-catalogue.md` |
| Mandatory section added, renamed or removed | Check 9 and its content signals |

## Stage 2C — No metamodel impact

Run `./install.sh` and confirm the skill is served.

## Worked examples

- **`business-vision`** (2A, singleton, naming exception): new Step 0; no IDs, so no Check 5 row; output `docs/VISION.md` recorded in the prefix mapping; wire mode writes `CLAUDE.md`, so `impact: "medium"`; upstream reads added to `business-persona`, `business-model-canvas`, `business-objective`, `plan-delivery-roadmap`, `spec-prd`.
- **`business-objective`** (2A, ID-minting): new Step 4.5; mints `OBJ-NN` and `KR-NN.M`; downstream references added to `plan-delivery-roadmap` (epic template), `spec-prd` (traceability), `spec-quality-attributes` (KR grounding), `business-model-canvas` (value proposition soft-link), `business-value-stream` (pain index).
