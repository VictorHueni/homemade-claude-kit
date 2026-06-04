# Open Items Governance

The kit captures unresolved work across many artefact types — research questions, missing
decisions, follow-up implementation items, deferred refactors. Without a single contract
those captures drift in heading name, table shape, lifecycle vocabulary, and physical
location, making it impossible to audit governance health or roll up live open work across
the stack.

This rule is the **single source of truth** for that contract. Every skill that emits
unresolved work, every artefact template that exposes it, and every audit that verifies it
must conform to the schema and lifecycle defined here. `util-docs-audit` stays generic
(file-level rot) and is out of scope; stack-aware governance lives in `util-metamodel-audit`
and the dedicated `util-open-items` skill.

---

## 1. Canonical local section

Every artefact that can carry unresolved work exposes it in **exactly one**
**document-level** `## Open Items` section. Document-level means the section is a top-level
heading (`## Open Items`) in the artefact file — never an inner subsection nested under
per-question, per-stage, or per-block headings.

**Heading:**

```markdown
## Open Items
```

**Variants forbidden** (these are migrated by Increment 03 of the plan that introduced this
contract):

- `## Open / TODO`
- `## Open TODOs`
- `## Open questions remaining`
- `## Open questions for next interview`
- `## Open questions for next workshop / research wave`
- `### Open Items` (any non-document-level placement)
- `§Open Issues` (legacy wording in discipline docs)

Discipline docs, skill instructions, and audit catalogues all use the canonical phrase
`## Open Items` when they reference the section.

---

## 2. Item taxonomy

Every row in an `## Open Items` table is exactly one of four types:

| Type            | Meaning                                                                                                         | Typical resolution path                                  |
| :-------------- | :-------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------- |
| `doc-gap`       | Information that should live in this artefact is missing and needs to be researched or written.                  | Update the artefact in place.                            |
| `decision-gap`  | A decision is required (often architectural) before downstream work can proceed.                                | Write or update an ADR, then close the row.              |
| `execution-item`| Concrete follow-up work that does not change the artefact itself but must be scheduled.                          | Open a PRD / implementation plan increment / runbook.    |
| `tech-debt`     | Known structural shortcut that must be paid back later; not a defect, but a deliberate deferral.                | Open a refactor PRD or schedule into a maintenance epic. |

The type field is mandatory on every row. A row that does not fit one of the four types
either belongs elsewhere (product backlog, defect tracker) or has been mis-classified.

### Open items are NOT scaffold placeholders

Inline `_TODO_` placeholders inside an artefact body (a stub heading, an unfinished
sentence, a missing diagram) are **not** open items. They are scaffold debt: they signal an
incomplete first draft of the document itself. `_TODO_` density is measured by
`util-metamodel-audit` Check 8 and is reported separately.

Open items capture **work that remains after the artefact is internally complete** —
unanswered questions, deferred decisions, follow-ups, debt. Skills must not scaffold
placeholder-only rows in `## Open Items` just to satisfy the heading; an empty `## Open
Items` section (with a "None at present." note) is the correct initial state when no
actionable unresolved work exists yet.

---

## 3. Lifecycle states

Each row uses one of the following statuses, in this lifecycle order:

| Status        | Meaning                                                                                  |
| :------------ | :--------------------------------------------------------------------------------------- |
| `open`        | Identified, not yet being worked on.                                                      |
| `in-progress` | Actively being resolved (assigned, on the active work plan).                              |
| `blocked`     | Cannot progress without an external dependency (decision, evidence, third party).         |
| `closed`      | Resolved. Kept in the row for one review cycle, then archived per §6.                     |
| `dropped`     | Decided not to act on this item. Rationale recorded in `Resolution path`.                 |

Closure must be evidenced: a `Tracker ref` (link to PR, ADR, plan increment, or audit
report) is required to move a row to `closed` or `dropped`.

---

## 4. Table schema

The `## Open Items` section uses one canonical Markdown table. Column order and headings are
fixed:

```markdown
## Open Items

| OI-ID  | Type           | Summary                       | Source anchor         | Source heading                          | Resolution path                                  | Priority | Status      | Owner   | Due / Review date | Tracker ref       |
| :----- | :------------- | :---------------------------- | :-------------------- | :-------------------------------------- | :----------------------------------------------- | :------- | :---------- | :------ | :---------------- | :---------------- |
| OI-001 | decision-gap   | Auth model for partner API    | #q3                   | Q3 — How do partners authenticate?      | Open ADR on token strategy                       | high     | open        | victor  | 2026-06-15        | _TBD_             |
```

**Column rules:**

- `OI-ID` — local to the artefact only when the row has not yet been synced to the central
  ledger. After sync the row carries the ledger-assigned `OI-NNNN` ID and the local ID is
  retired (see §5 below).
- `Type` — exactly one of the four taxonomy values from §2.
- `Summary` — one-sentence statement of the open item. Self-contained: a reader should
  understand the row without opening the source artefact.
- `Source anchor` — short fragment identifier (e.g. `#q3`, `#stage-onboarding`, `#vp-2`,
  `#cs-1`). Provides a precise jump target inside the source document and is the stable
  half of the provenance pair.
- `Source heading` — the full heading text the anchor resolves to (e.g.
  `Q3 — How do partners authenticate?`, `Stage 2: Onboarding`, `VP-2: Self-serve setup`).
  Provides human-readable context that survives anchor renames and is the readable half of
  the provenance pair.
- `Resolution path` — what closing this row looks like in practice (e.g. "Open ADR on token
  strategy", "Schedule into refactor epic E-07").
- `Priority` — `low` | `medium` | `high` | `critical`.
- `Status` — lifecycle value from §3.
- `Owner` — person accountable. Use `_TBD_` if no owner is yet assigned.
- `Due / Review date` — ISO 8601. For `closed` / `dropped` rows this is the closure date.
- `Tracker ref` — link to the resolving PR, ADR, plan increment, runbook, or audit report.
  Use `_TBD_` while the row is still `open`; required to leave `open` for a terminal state.

Skills MAY add additional informational columns *after* `Tracker ref`. They MUST NOT remove
or reorder the canonical columns.

---

## 5. Central control plane

The repo-level living ledger lives under:

```text
docs/project-control/open-items/
```

This path is **under `docs/` for unified navigation** (every persistent artefact in the
repo lives somewhere under `docs/`, so contributors only have to remember one root) but
**named `project-control/` because it is an operational control plane, not a product
spec**. The folder name is the load-bearing signal: anything under
`docs/project-control/` is a live, continuously-changing system of record — closer to a
runbook or an internal tracker than to a PRD, an ADR, or a domain model. Audits and
linters that operate on product-spec artefacts (PRDs, FBS, ADRs, domain models, etc.)
either match by file pattern or by deeper folder (`docs/product-specs/`, `docs/domain/`,
`docs/architecture/`) and therefore do **not** sweep `docs/project-control/`.

Why it is separate from product backlog artefacts (PRDs, delivery roadmap, FBS):

- The delivery roadmap (`E-NN` epics) plans **what we build next** at product scope. Open
  items capture **governance-level unresolved work** across every kind of artefact, only
  some of which results in built features.
- PRDs and implementation plans are commitment artefacts. Open items can include items that
  may never become commitments (e.g. dropped research questions).
- The FBS tracks **functionality status** in shipped or in-flight features. Open items can
  include doc gaps and decision gaps that never appear as functionalities.

Source-of-truth rule: **the local `## Open Items` section in each artefact is the authoring
surface; the central ledger is the consolidated read-out.** Skills must update the local
section first; `util-open-items` then syncs to the central ledger, assigns the canonical
`OI-NNNN` ID, and preserves both `Source anchor` and `Source heading` on every synced row so
the ledger can navigate back into the source artefact without relying on tribal knowledge.

Each ledger row points back to its source via three coordinates:

- The relative path to the source artefact (e.g. `docs/architecture/research/0003-token-auth.md`).
- The `Source anchor` (e.g. `#q3`).
- The `Source heading` (e.g. `Q3 — How do partners authenticate?`).

If a source artefact is renamed, the central ledger row is updated; if a heading is
renamed, the `Source heading` field is updated while the anchor remains stable, or the
anchor is updated and the new heading recorded.

### 5.1 Ledger column layout

The ledger uses the §4 canonical columns plus one ledger-only column, `Source artefact`
(the relative repo path), inserted **after `Summary`**:

```
OI-ID | Type | Summary | Source artefact | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref
```

This is the one sanctioned deviation from §4's "additional columns only after `Tracker ref`"
rule — it applies to the ledger surface only, never to a local `## Open Items` section.

### 5.2 Central-only rows (governance work with no source artefact)

Most rows originate in an artefact's local `## Open Items` section and carry full provenance.
Some governance work is raised **directly at the central plane** and has no artefact home —
e.g. kit-development items (per §9), or repo-wide decisions not owned by any single document.
These **central-only** rows are valid and use this provenance form:

- `Source heading` = `_central-only_`
- `Source anchor` = empty
- `Source artefact` = the owning folder/skill or scope marker (e.g. `ops-terraform-exoscale/`),
  or `(cross-cutting)` when no single location applies.

`util-metamodel-audit` MUST NOT flag central-only rows as orphaned or as provenance-drift
findings. All other §4 column rules (valid `Type`, lifecycle `Status`, `_TBD_`-until-terminal
`Tracker ref`, ISO date) apply unchanged.

### 5.3 Pluggable backend

The central plane is a **serialization** of the §4 model, not the model itself. The default
and only universally-required backend is **`markdown`** — the living ledger of §5 plus the
archive of §6. A project MAY select an alternative backend (for example, an issue tracker)
for the consolidated read-out. Whatever the backend, these invariants hold:

- **Backend-independent model.** The §4 schema is the one logical model; each backend is a
  serialization of it. The field **slugs** (the stable lower-snake keys behind each §4
  column) — not column headers or UI labels — are the binding contract every backend
  conforms to. The audit reads any backend through that single slug map.
- **Authoring surface is backend-invariant.** The local `## Open Items` section (§1) is
  always §4 markdown regardless of backend. Only what the sync step *writes to* changes;
  switching backends never edits an authoring surface.
- **One backend per project.** Backends are never run concurrently — two live writers over
  two identity spaces reintroduce the dual-source-of-truth this contract exists to prevent.
  Moving between backends is a **one-way migration** performed once, and MUST emit an
  identity map so back-references survive the identifier re-mint.
- **Evidence-gated closure holds.** A terminal `Status` still requires a non-`_TBD_`
  `Tracker ref`, whether the backend enforces it natively or the operator validates it.
- **Provenance is preserved.** Every backend stores the full provenance composite
  (`Source artefact` + `Source anchor` + `Source heading`) under the canonical slugs, so
  central-only and artefact-originated items are distinguishable in any backend.

A worked two-backend mapping (the kit's own `markdown` ledger plus an issue-tracker backend)
is maintained as the reference model that operator tooling and the audit conform to; see
§10.

---

## 6. Archive and snapshots

Closed and dropped items remain on the active local section and the central ledger for one
review cycle (default: 30 days). After that they are moved to:

```text
docs/project-control/open-items/archive/
```

Archive files are time-bucketed snapshots (e.g. `2026-Q2.md`) or per-resolution rollups.
The live ledger never silently deletes rows — archival is explicit and dated.

---

## 7. Audit and tooling boundaries

| Tool                          | Responsibility                                                                                              |
| :---------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `util-docs-audit`             | Generic file-level rot (stale, outdated, dead). **Not** an open-items governance tracker.                   |
| `util-open-items`             | Maintains the central plane — sync, triage, close, archive, report — honouring the configured backend (§5.3). Living ledger CRUD.         |
| `util-metamodel-audit`        | Report-only. Verifies `## Open Items` section presence, schema compliance, source-anchor / source-heading provenance, tracker sync coverage, closure drift — reading whichever backend is configured via the canonical field slugs (§5.3). Never mutates source artefacts or the ledger. |

`util-metamodel-audit` is the only place that flags governance drift between artefacts and
the central ledger. It must not mutate either side; remediation is always operator-driven
via `util-open-items` or direct artefact edits.

---

## 8. Skill conformance checklist

When a skill emits or governs unresolved work **in the artefacts it produces** (under a
project's `docs/`), its `SKILL.md` instructions and template files must:

1. Use the canonical `## Open Items` heading at document level.
2. Reference the column schema in §4 (either inline or by linking to this rule).
3. Distinguish `_TODO_` scaffold placeholders from real `doc-gap` / `decision-gap` /
   `execution-item` / `tech-debt` rows.
4. Preserve `Source anchor` + `Source heading` on every row that originates from a
   sub-section of the artefact (questions, stages, blocks, processes).
5. Chain to `util-open-items` after generation or update to sync the central ledger.

Templates SHOULD include the bare table header with the canonical columns and a single
"None at present." note for the initial empty state.

---

## 9. Scope boundary — skill folders are tooling, not artefacts

The `## Open Items` contract governs **project artefacts** (PRDs, ADRs, domain models,
research notes, and the like) — the documents a skill *produces* under a project's `docs/`.
It does **not** apply to the skill definitions themselves.

A skill folder (`<skill>/SKILL.md` and its `references/`, `templates/`, `scripts/`) is
tooling, not a governed artefact. It **MUST NOT** contain a `## Open Items` section tracking
the skill's own development. Such a section is swept by no ledger, drifts silently, and
mis-signals to `util-metamodel-audit` (which expects open items only in project artefacts).

Follow-up work on a skill — new modes, extra checks, deferred refinements — is **real
governance work on the kit itself**, so the kit dogfoods this very contract: such items live
in the kit's own central ledger at `docs/project-control/open-items/open-items.md` (§5), as
central-only rows (`Source heading: _central-only_`, empty `Source anchor`). They do **not**
live in the skill folder. The same ledger also holds the kit's candidate-skill backlog and
structural-decision items (the former `BACKLOG.md`, merged in); shipped-skill history is
recorded under `docs/project-control/open-items/archive/`. A skill's `SKILL.md` may carry at most a short
**"Follow-up work"** pointer to the ledger; it never carries the canonical `## Open Items`
table.

**Skills do not restate the schema.** A skill that produces an artefact carrying Open Items
does **not** embed the canonical table, an example row, or a §4 column recital in its
`SKILL.md` or inline instructions. The schema is supplied by the artefact's own **output
template** (under the skill's `templates/`, or a `references/template.md` copied verbatim
into `docs/`), and by this rule, which applies to every artefact globally — so the skill has
nothing to point at. The sole place an Open Items table literally appears in a skill folder
is such an output template: that template *is* the artefact's initial state (§8).

Restated:

- Items a skill tells Claude to **write into produced artefacts** → governed by §1–§8; schema comes from the output template, not from the SKILL.md.
- Items about the **skill's own evolution** → the kit's `docs/project-control/open-items/` ledger, never inside the skill folder.

---

## 10. See also

- `rules/metamodel.md` — strategic-architecture build order; references this contract.
- `util-open-items/references/github-backend.md` — the operator skill's worked backend-mapping reference (canonical field slugs, identity translation, status decomposition); the §5.3 worked example. Travels with the skill — never copied into a project's `docs/`.
- `docs/project-control/open-items/open-items.md` — the kit's own ledger: kit-dev open items (per §9) **and** the merged skill backlog (candidate skills + structural decisions). Shipped history under `archive/`.
- `util-open-items/SKILL.md` — operating manual for the living ledger.
- `util-metamodel-audit/references/check-catalogue.md` — exact audit checks for governance
  drift, schema compliance, and provenance.
