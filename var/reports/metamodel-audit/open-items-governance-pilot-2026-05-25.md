# Open-Items Governance — Repo Pilot Report

- **Scope:** entire `homemade-claude-kit` repository
- **Date:** 2026-05-25
- **Plan:** `Plan-0001 — Open Items Governance`, Increment 08
- **Mode:** ad-hoc pilot run (precursor to the first scheduled `util-metamodel-audit` Mode 5 run)
- **Verdict:** governance contract is implemented end-to-end across every skill that emits unresolved work. No critical drift found. Two intentional design choices and one minor follow-up are listed below.

This pilot pre-flights the governance model on the kit itself. It is **not** the
authoritative `util-metamodel-audit` report — that skill remains the canonical auditor and
will run on its own cadence. The pilot is a sanity check that the contract from
[`rules/open-items-governance.md`](../../../rules/open-items-governance.md) is wired
through every place it needs to be.

---

## Coverage matrix

### Canonical section + schema

Every artefact-producing skill that can emit unresolved work has a `## Open Items` section
in its template with the canonical 11-column schema and source-anchor / source-heading
provenance:

| Skill                                  | `## Open Items` section | Schema columns | Source anchor | Source heading | Chain to sync |
| :------------------------------------- | :---------------------: | :------------: | :-----------: | :------------: | :-----------: |
| `arch-research`                         | yes                     | yes            | yes (per Q)   | yes (per Q)    | yes (Mode 4) |
| `business-process`                      | yes                     | yes            | yes           | yes            | yes (synthesis) |
| `business-research`                     | yes (synth + research)  | yes (×2)       | yes           | yes            | yes (Mode 3/4) |
| `business-workshop`                     | yes                     | yes            | yes           | yes            | yes (Mode 4) |
| `business-model-canvas`                 | yes                     | yes            | yes           | yes            | n/a (no chain step) |
| `business-capability-map`               | yes                     | yes            | yes           | yes            | n/a (no chain step) |
| `business-value-stream`                 | yes                     | yes            | yes           | yes            | n/a (no chain step) |
| `spec-functional-breakdown-structure`   | yes                     | yes            | yes           | yes            | n/a (no chain step) |
| `spec-prd`                              | §9 inline in SKILL.md   | yes            | yes           | yes            | yes (Step 5) |
| `spec-implementation-plan`              | conditional             | n/a unless emitted | n/a       | n/a            | yes (conditional) |
| `ops-runbook`                           | conditional             | n/a unless emitted | n/a       | n/a            | yes (conditional) |
| `business-competitive-landscape`        | **changelog-only — by design** | n/a       | n/a           | n/a            | n/a |

### Central control plane

- `project-control/open-items/open-items.md` — exists, schema-conformant 12-column ledger, initialises empty per §2 of the governance rule. ✓
- `project-control/open-items/README.md` — operator guidance present. ✓
- `project-control/open-items/archive/` — exists with `.gitkeep`. ✓

### Forbidden legacy variants

`rg` across the repo (excluding the rule + check catalogue + exec plan workspace) returns
zero hits for:

- `^## Open / TODO`
- `^## Open TODOs`
- `^## Open questions remaining`
- `^## Open questions for next interview`
- `^## Open questions for next workshop / research wave`
- `^### Open Items` (i.e. non-document-level placements)
- `§Open Issues`

All remaining hits are inside `rules/open-items-governance.md`, `rules/metamodel.md`, or
`util-metamodel-audit/references/check-catalogue.md` — i.e. text that **defines** the
forbidden set rather than violates it. Expected, no action.

### Audit + boundary tooling

- `util-metamodel-audit` — Check 18 (governance health, six sub-checks) wired into the
  catalogue, template, SKILL.md and methodology references. Mode 5 (focused open-items
  governance run) defined with its own output filename. ✓
- `util-open-items` — six modes (sync / triage / close / drop / archive / report)
  defined, schemas in `references/template.md`, triage signals in
  `references/triage-rules.md`. ✓
- `util-docs-audit` — boundary section now explicitly states this skill is **not a
  stack-governance tracker** and routes governance questions to `util-metamodel-audit` and
  `util-open-items`. ✓

---

## Findings

### F1 — `spec-implementation-plan` + `ops-runbook` use conditional chaining (intentional)

Both skills chain to `util-open-items` only when the plan / runbook actually carries open
items. Their templates do not pre-scaffold a `## Open Items` section because most plans
and many runbooks have nothing to declare and a placeholder-only section would violate
§2 of the governance rule (no scaffold-only open-item rows).

- **Severity:** informational
- **Action:** none — documented in increment 06 progress notes and in each SKILL.md's
  chaining section.
- **Re-evaluation trigger:** if a future audit shows the conditional language is being
  skipped silently (i.e. plans accumulate ungoverned open items), reconsider whether the
  template should carry an explicit "Open Items: none at present." stub instead.

### F2 — `business-competitive-landscape` is deliberately changelog-only

The discipline doc explicitly documents that competitive-landscape artefacts capture
unresolved work as per-claim evidence-freshness (`Source:` + `Last verified:` lines) rather
than as a parallel `## Open Items` ledger. ADR-blocking decisions go into the relevant
ADR's open-items section instead.

- **Severity:** informational
- **Action:** none — documented stance in `business-competitive-landscape/references/landscape-discipline.md`.
- **Re-evaluation trigger:** if competitive intel starts driving execution work that needs
  ledger tracking (e.g. competitor product changes requiring our response), revisit and
  add a `## Open Items` section then.

### F3 — Mode 5 of `util-metamodel-audit` has not yet been run on the repo

Increment 07 wired Check 18 + Mode 5 into the catalogue and SKILL but the first focused
run has not yet executed. This pilot covers the manual equivalents (`rg` scans of the
forbidden set, coverage matrix above) but is not a substitute for the audit's structured
output.

- **Severity:** low (cosmetic — no drift was found that the audit would have caught)
- **Action:** schedule the first `util-metamodel-audit` Mode 5 run after this plan
  archives. Add as a follow-up in the central ledger only if the run surfaces drift.

### F4 — Central ledger is empty (expected initial state)

`project-control/open-items/open-items.md` has zero rows. This is correct per §2 of the
governance rule (do not scaffold placeholder rows; empty is the right starting state).
The ledger will fill as `util-open-items sync` runs against artefacts that actually carry
items.

- **Severity:** informational
- **Action:** none.

---

## Recommendations

1. **Archive Plan-0001** when increment 08 lands. The plan delivered the contract end-to-end
   and the kit can rely on `util-metamodel-audit` Mode 5 for future drift detection.
2. **First scheduled audit run:** trigger `util-metamodel-audit` Mode 5 within 30 days of
   archive so the contract has been exercised at least once by the auditor itself.
3. **Track future violations as open items, not pilot reports.** This document is a
   one-shot pre-flight — recurring governance health belongs in the audit + ledger
   feedback loop, not in standalone reports under `var/reports/`.

---

## Provenance

- Plan: [`docs/exec-plans/active/0001_open-items-governance/0001_exec_open-items-governance.md`](../../../docs/exec-plans/active/0001_open-items-governance/0001_exec_open-items-governance.md)
- Contract: [`rules/open-items-governance.md`](../../../rules/open-items-governance.md)
- Auditor: [`util-metamodel-audit/SKILL.md`](../../../util-metamodel-audit/SKILL.md)
- Ledger ops: [`util-open-items/SKILL.md`](../../../util-open-items/SKILL.md)
- Boundary tool: [`util-docs-audit/SKILL.md`](../../../util-docs-audit/SKILL.md)
