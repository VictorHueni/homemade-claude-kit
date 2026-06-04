# Open Items — Living Ledger

This is the consolidated, repo-wide ledger of unresolved work synced from every artefact's
local `## Open Items` section. It is the operational system of record described in §5 of
[`rules/open-items-governance.md`](../../rules/open-items-governance.md).

The ledger is **not** a product artefact. It has no frontmatter, no review cadence, and is
not part of the strategic-architecture build order. It is expected to mutate continuously
as artefacts are written, decisions are taken, and tracker references are added. See
[`README.md`](./README.md) for purpose, lifecycle, and operator guidance.

---

## How rows arrive here

1. A skill emits an open item into the source artefact's document-level `## Open Items`
   section using the canonical schema (`OI-ID`, `Type`, `Summary`, `Source anchor`,
   `Source heading`, `Resolution path`, `Priority`, `Status`, `Owner`,
   `Due / Review date`, `Tracker ref`).
2. `util-open-items` runs in `sync` mode: it reads the local section, deduplicates against
   existing ledger rows, assigns the canonical `OI-NNNN` ID on first sync, and writes the
   row into the table below — extended with `Source artefact` (relative repo path) so the
   ledger can navigate back into the originating document.
3. Both `Source anchor` and `Source heading` are preserved verbatim from the source row.
   The pair is the provenance contract: the anchor is the stable jump target; the heading
   is the human-readable context that survives anchor renames.

Rows that have no artefact home (governance-only items raised directly at the central
plane) carry `_central-only_` in `Source heading` and an empty `Source anchor` —
`util-metamodel-audit` does not flag these as orphans.

---

## Live items

This table is the only authoritative view of currently open governance work. Closed and
dropped rows linger here for one review cycle (default 30 days per §6 of the governance
rule), then move to `archive/`.

| OI-ID   | Type           | Summary                                                                                              | Source artefact                                       | Source anchor | Source heading  | Resolution path                                                            | Priority | Status | Owner  | Due / Review date | Tracker ref |
| :------ | :------------- | :--------------------------------------------------------------------------------------------------- | :---------------------------------------------------- | :------------ | :-------------- | :------------------------------------------------------------------------- | :------- | :----- | :----- | :---------------- | :---------- |
| OI-0001 | execution-item | Expand native Exoscale checks beyond `EXO-001` (permissive egress, public DBaaS, unencrypted volumes) | `ops-terraform-exoscale/scripts/exoscale-policy.sh`   |               | _central-only_  | Add checks to `exoscale-policy.sh` following the `EXO-001` pattern          | medium   | open   | victor | 2026-08-29        | _TBD_       |
| OI-0002 | execution-item | Evaluate Checkov as a second Terraform scanner (reliable custom policies)                            | `ops-terraform-exoscale/`                             |               | _central-only_  | Spike Checkov YAML/Python policies on Exoscale HCL; decide keep/drop        | low      | open   | _TBD_  | 2026-08-29        | _TBD_       |
| OI-0003 | execution-item | Add `domain-event-storming` skill — Event Storming to discover bounded contexts before Step 2b (mints `ES-EVT-NN`, `ES-CMD-NN`) | `docs/domain/event-storming/` (planned) | | _central-only_ | Build the skill; feeds `BC-NN` / `BC-NN.EVT-NN` | high | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0004 | execution-item | Add `spec-test-strategy` skill — test pyramid + coverage + `QA-XXNN`→test-type mapping (mints `TS-NN`) | `docs/product-specs/test-strategy/` (planned) | | _central-only_ | Build the skill | high | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0005 | execution-item | Add `business-customer-journey-map` skill — experience-view journeys (mints `CJ-N.M`) | `docs/business/customer-journeys/` (planned) | | _central-only_ | Build the skill | high | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0006 | execution-item | Add `arch-team-topology` skill — Team Topologies from `BC-NN` (mints `TEAM-NN`) | `docs/architecture/team-topology/` (planned) | | _central-only_ | Build the skill | medium | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0007 | execution-item | Add `ops-slo` skill — SLI/SLO/error budgets from `QA-XXNN` (mints `SLO-NN`) | `docs/ops/slos/` (planned) | | _central-only_ | Build the skill | medium | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0008 | execution-item | Add `arch-threat-model` skill — STRIDE per data-flow; feeds ADRs + security QAs (mints `THR-NN`) | `docs/architecture/threat-model/` (planned) | | _central-only_ | Build the skill | medium | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0009 | execution-item | Add `domain-integration-contract` skill — concrete contract per BC-pair (mints `INT-NN`) | `docs/domain/integration-contracts/` (planned) | | _central-only_ | Build the skill | medium | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0010 | execution-item | Cross-skill web visualisations — shared HTML/SVG views from canonical Markdown (capability maps, BMC, roadmaps, FBS) | `skills/com-artefact-viz/` | | _central-only_ | Built as `com-artefact-viz`: parse→model→render pipeline, four renderers, shared `design-system` token sheet. Merged to main | medium | closed | victor | 2026-05-30 | [9c9cf00](https://github.com/VictorHueni/homemade-claude-kit/commit/9c9cf00) |
| OI-0011 | execution-item | Add `spec-release-plan` skill — rollout/comms/rollback per `E-NN` | (planned) | | _central-only_ | Build the skill | low | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0012 | execution-item | Add `ops-post-mortem` skill — blameless incident review (broader than `ops-bug-rca`) | (planned) | | _central-only_ | Build the skill | low | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0013 | execution-item | Add `business-stakeholder-map` skill — RACI / influence-interest grid | (planned) | | _central-only_ | Build the skill | low | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0014 | execution-item | Add `dev-changelog` skill — CHANGELOG.md per Keep a Changelog | (planned) | | _central-only_ | Build the skill | low | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0015 | execution-item | Add `dev-tech-debt` skill — log/triage/close/report tech + docs debt → `TECH_DEBT.md` | (planned) | | _central-only_ | Build the skill | low | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0016 | execution-item | Add deterministic runner/CLI for `util-open-items` — parse tables, mint `OI-NNNN`, sync, validate, archive | `util-open-items/` | | _central-only_ | Build the runner | low | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0017 | decision-gap | PRD naming with epic reference — encode epic in filename vs subfolder vs keep-flat (audit-enforced) | `docs/product-specs/prds/` | | _central-only_ | Decide convention; update metamodel + `spec-prd` | medium | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0018 | decision-gap | Exec-plan folder ↔ PRD link — match NNNN vs reference-PRD-in-name vs nest-under-PRD | `docs/exec-plans/active/` | | _central-only_ | Decide convention; update metamodel + `spec-implementation-plan` | medium | open | _TBD_ | 2026-08-29 | _TBD_ |
| OI-0019 | execution-item | Unify `com-slide-deck` styling onto the shared `design-system` tokens — deck `styles.css` inherits the `tokens.css` `:root` contract instead of defining its own palette | `skills/com-slide-deck/` | | _central-only_ | `build.py` inlines `docs/design/tokens.css` before the deck styles; full rename to the contract vocabulary + semantic bridge. Merged to main | low | closed | victor | 2026-05-30 | [1147cf7](https://github.com/VictorHueni/homemade-claude-kit/commit/1147cf7) |
| OI-0020 | execution-item | Make the `design-system` token contract generic + portable for cross-project interoperability — semantic layer is `--success/--warning/--danger/--info`; kit-domain tokens (status, pain, confidence, importance) are consumer-derived aliases | `skills/design-system/` | | _central-only_ | Invert the semantic layer: contract carries generics only; `com-artefact-viz` derives domain tokens from them; `com-slide-deck` drops the bridge. Merged to main | medium | closed | victor | 2026-05-30 | [e7302f8](https://github.com/VictorHueni/homemade-claude-kit/commit/e7302f8) |
| OI-0021 | execution-item | Symmetric, consistently-named token layering across the `com-` skills — both ship `templates/tokens.fallback.css` (identical) and layer fallback → project override → tool layer; fixes the standalone deck having an undefined base palette | `skills/com-slide-deck/`, `skills/com-artefact-viz/` | | _central-only_ | Ship identical `tokens.fallback.css` in both consumers + viz `tokens.domain.css`; `build.py`/`render.py` inline the fallback first so a standalone deck/view is zero-config. Merged to main | medium | closed | victor | 2026-05-30 | [ac37c0f](https://github.com/VictorHueni/homemade-claude-kit/commit/ac37c0f) |
| OI-0022 | execution-item | `com-slide-deck` migrate mode — help an existing pre-design-system deck adopt the shared token contract (detect legacy token names, emit a compatibility shim, or rewrite names in place) | `skills/com-slide-deck/` | | _central-only_ | New `scripts/migrate.py`: report (read-only) / `--apply` (alias shim) / `--rename` (rewrite); SKILL + README documented. Merged to main | low | closed | victor | 2026-05-30 | [e1d8e9f](https://github.com/VictorHueni/homemade-claude-kit/commit/e1d8e9f) |
| OI-0023 | execution-item | `util-provenance` `--sign` step — detached digital signature of the digest (GPG or `openssl dgst -sign`) proving authorship by a key, fully local. Reserved flag already exits with a "planned" message | `skills/util-provenance/` | | _central-only_ | Implement `--sign` in `scripts/provenance.py`; decide signing-key model (self-managed vs CA-backed); emit a `.sig` + extend the provenance record. Must preserve the hash-only/local tenet | medium | open | victor | 2026-08-31 | _TBD_ |
| OI-0024 | execution-item | `util-provenance` `--c2pa` step — embed a signed C2PA Content Credentials manifest (author + edit history). Reserved flag already exits with a "planned" message | `skills/util-provenance/` | | _central-only_ | Implement `--c2pa`; needs a `c2patool`/`c2pa-python` install; verify C2PA-for-PDF support (partial/evolving) else apply to per-page PNG renders. Best-effort companion to hash+timestamp | low | open | victor | 2026-08-31 | _TBD_ |
| OI-0025 | execution-item | Service blueprint — front-stage/back-stage multi-actor view (actor lanes × steps, line of visibility, systems + notification spine); the only artefact showing a whole multi-actor coordination loop at once | `skills/com-artefact-viz/` | | _central-only_ | **Resolved as a composition lens, not a standalone skill.** Scoping found ~80% overlap with `business-process` (actor swimlanes, systems §4, steps §6, KPIs §8, pain points §9 already there); only the line of visibility + customer-perceived evidence were genuinely new. Shipped as `com-artefact-viz --kind service-blueprint` (5th renderer) composing `business-process` + `business-value-stream` + `business-persona` docs; **derives** front/back-stage from persona type, surfacing unclassifiable actors rather than guessing. Mints no IDs, authors no new artefact → no metamodel build-order/audit/migration/scaffold coupling. Closes the multi-actor-loop gap without a second source of truth | high | closed | victor | 2026-06-02 | [ac51987](https://github.com/VictorHueni/homemade-claude-kit/commit/ac51987) |
| OI-0026 | execution-item | Establish the `ux-` design+experience category (`docs/ux/`); move `design-system`'s output `docs/design/` → `docs/ux/` (incl. `tokens.css`). The skill **keeps its name** `design-system` — a prefix→folder exception like `business-vision`→`docs/VISION.md`. Prerequisite for OI-0025; unifies visual + experience design under one `ux-` prefix instead of a split `design-`/`ux-` | `skills/design-system/`, `skills/com-slide-deck/`, `skills/com-artefact-viz/` | | _central-only_ | Done: `ux-` prefix→folder mapping added (with the `design-system` name exception); all `docs/design/` → `docs/ux/`; `com-` token auto-detect (build.py/render.py/migrate.py) hard-repointed to `docs/ux/tokens.css`, no fallback; metamodel paths+prefix table+bullets+coupling note, README, skill-creation-sync, and migration detection-signals updated; smoke-tested both detectors | high | closed | victor | 2026-06-02 | [1825c46](https://github.com/VictorHueni/homemade-claude-kit/commit/1825c46) |
| OI-0027 | execution-item | Revise `open-items-governance.md` §5–§7 to define the two-backend model and adapter boundary | `docs/architecture/decisions/adr-0002-open-items-pluggable-backend-github-issues.md` | #tooling-consequences | Tooling consequences | Edit the governance rule | high | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| OI-0028 | execution-item | Add `backend:` setting + `github` mode (gh issue/project wrappers) to `util-open-items` | `docs/architecture/decisions/adr-0002-open-items-pluggable-backend-github-issues.md` | #tooling-consequences | Tooling consequences | Update `util-open-items/SKILL.md` + references | high | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| OI-0029 | execution-item | Add `github`-backend check path to `util-metamodel-audit` (read Issue-Form bodies via `gh`) | `docs/architecture/decisions/adr-0002-open-items-pluggable-backend-github-issues.md` | #tooling-consequences | Tooling consequences | Update audit check catalogue | medium | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| OI-0030 | execution-item | Author `.github/ISSUE_TEMPLATE/open-item.yml` with `id:` keys mirroring §4 columns | `docs/architecture/decisions/adr-0002-open-items-pluggable-backend-github-issues.md` | #data-model--interoperability | Data model & interoperability | Write the issue form | high | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| OI-0031 | execution-item | Build one-way `markdown → github` migration emitting an `OI-NNNN → #N` map | `docs/architecture/decisions/adr-0002-open-items-pluggable-backend-github-issues.md` | #data-model--interoperability | Data model & interoperability | Add a migration mode/script | medium | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| OI-0032 | decision-gap | Decide whether to generalise the `github` backend to the universal contract after dogfooding | `docs/architecture/decisions/adr-0002-open-items-pluggable-backend-github-issues.md` | #context-and-problem-statement | Context and Problem Statement | Follow-up ADR superseding/extending this one; gated on a portability pass (ADR-0002 §Dogfood findings, 2026-06-04) | low | open | victor | 2026-09-01 | _TBD_ |
| OI-0033 | execution-item | Make Mode 7 portable to personal repos — Issue-Types→`type:` label fallback + owner→login `--assignee-map` + idempotent label bootstrap | `docs/architecture/decisions/adr-0002-open-items-pluggable-backend-github-issues.md` | #dogfood-findings--mode-7-dry-run-2026-06-04 | Dogfood findings — Mode 7 dry-run (2026-06-04) | Implement in `migrate_markdown_to_github.py`; re-validate via dry-run | medium | closed | victor | 2026-06-04 | [#4](https://github.com/VictorHueni/homemade-claude-kit/pull/4) |

Most rows are kit-development items raised directly at the central plane (the kit dogfoods its
own open-items contract per `rules/open-items-governance.md` §9), so they carry `_central-only_`
provenance — they have no source-artefact `## Open Items` section (skill folders do not carry
one). `OI-0001`/`OI-0002` are `ops-terraform-exoscale` follow-ups; `OI-0003`–`OI-0018` are the
former `BACKLOG.md` candidate-skill backlog (Tier 1 → `high`, Tier 2 → `medium`, Tier 3 →
`low`) and structural-decision items, merged here so the kit has a single control plane.
`OI-0019`–`OI-0024` are later additions (`com-`/`design-` token unification and
`util-provenance` follow-ups). `OI-0025`/`OI-0026` open the kit's UX layer: `OI-0026`
establishes a unified `ux-` design+experience category (migrating `design-system` into it),
and `OI-0025` closes the multi-actor-loop gap — the highest-leverage UX/UI gap, since no
existing skill showed a multi-actor coordination loop whole. `OI-0025` was deliberately
**not** built as a standalone `ux-service-blueprint` skill: it overlapped `business-process`
too heavily, so it shipped as a derived composition lens in `com-artefact-viz`
(`--kind service-blueprint`) that reads the process/value-stream/persona docs rather than
restating them.

`OI-0027`–`OI-0032` are the first **artefact-originated** rows: they carry full provenance
back into [`adr-0002`](../../architecture/decisions/adr-0002-open-items-pluggable-backend-github-issues.md)
(the open-items pluggable-backend decision), not `_central-only_`. `OI-0027`–`OI-0031` are its
implementation items (governance §5.3 + the two-backend `util-open-items` / `util-metamodel-audit`
skills + the migration mode), closed by [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3);
`OI-0032` is the deferred decision on whether to generalise the `github` backend to the
universal contract, and `OI-0033` is the portability pass the Mode 7 dry-run revealed it
needs (Issue-Types→`type:` label fallback + owner→login mapping). They were renumbered from a
transient `OI-0025`–`OI-0030` block that collided with the UX rows above when both branches
minted from `OI-0024` in parallel.

**Recommended build order** (former BACKLOG guidance, by structural impact, not strict
priority): `OI-0003` domain-event-storming → `OI-0004` spec-test-strategy → `OI-0026`
establish `ux-` category + migrate `design-system` → `OI-0025` service-blueprint lens (done)
→ `OI-0006` arch-team-topology → `OI-0007` ops-slo. Tier 2/3 items improve completeness but
are not structural metamodel gaps. Shipped-skill history lives in
[`archive/2026-Q2-shipped.md`](./archive/2026-Q2-shipped.md).

---

## ID assignment

The ledger assigns `OI-NNNN` IDs in monotonic order starting at `OI-0001`. IDs are stable
once assigned — closing or dropping a row never recycles its ID. The next ID to issue is
tracked implicitly by the highest `OI-NNNN` currently in the ledger or in any archive
file; `util-open-items` computes it on each sync.

A row's pre-sync local ID (used by the source artefact before the first sync) is allowed
to be any short token — e.g. `OI-001` scoped to the artefact — and is replaced by the
canonical `OI-NNNN` once the central row exists. After replacement the source artefact
carries the canonical ID, and the local ID is retired.

---

## Status snapshot

Skills and audits MAY render summary counts here (e.g. open / in-progress / blocked /
closed / dropped totals), but the snapshot must always derive from the live table above —
never the other way around. The live table is the source of truth.

As of 2026-06-04 (33 rows): **open 20** · in-progress 0 · blocked 0 · **closed 13** (`OI-0010`, `OI-0019`–`OI-0022`, `OI-0025`–`OI-0031`, `OI-0033`) · dropped 0. Closed rows linger on the live ledger for one review cycle (30 days) before archival per §6.

---

## Archive convention

When `util-open-items` runs in `archive` mode it moves eligible `closed` / `dropped` rows
into a time-bucketed file under `archive/` — for example `archive/2026-Q2.md`. The live
ledger never silently deletes a row; archival is explicit and dated, and each archive file
preserves the same canonical schema so the historical record stays queryable.

See [`README.md`](./README.md) and §6 of the governance rule for the archival policy.

---

## See also

- [`README.md`](./README.md) — operator guidance for this folder.
- [`rules/open-items-governance.md`](../../rules/open-items-governance.md) — canonical
  schema, taxonomy, lifecycle, central-plane rules.
- `util-open-items/SKILL.md` — ledger CRUD operating manual (sync, triage, close,
  archive, report).
