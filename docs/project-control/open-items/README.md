# Open Items — Central Control Plane

This folder hosts the **living ledger** of unresolved work consolidated across every artefact
in the kit. It is the operational system of record for governance work — research questions,
decision gaps, deferred follow-ups, and tech debt — rolled up from every artefact-level
`## Open Items` section into one navigable view.

The canonical contract for what an "open item" is, what its schema looks like, and how it
flows from artefact to ledger lives in [`rules/open-items-governance.md`](../../rules/open-items-governance.md).
This README documents how that contract is **operated** at the central plane.

---

## Why this lives under `docs/project-control/`

The ledger lives **under `docs/` for unified navigation** (every persistent artefact in
the repo sits somewhere under `docs/`, so contributors only have to remember one root),
but in a **dedicated `project-control/` folder** because it is fundamentally different
from every other artefact in `docs/`:

- The rest of `docs/` holds product and architecture artefacts. Each artefact has a
  stable shape, an owner, and a review cadence governed by frontmatter.
- `docs/project-control/open-items/` holds an **always-mutating operational log**. It does
  not carry artefact frontmatter, is not part of the strategic-architecture build order,
  and is not swept by product-spec audit rules (those checks match by file pattern or by
  deeper folder like `docs/product-specs/` or `docs/domain/`, never by being-under-`docs/`).
- Treating the ledger as a product artefact would invite audits to flag every legitimate
  row churn as drift. Keeping it under `project-control/` keeps governance work visible
  without polluting the product surface.

The same separation is why the ledger is **not** part of the product backlog. Open items
include things that may never become commitments (dropped questions, never-shipped tech
debt, governance-only follow-ups). PRDs, the delivery roadmap, and the FBS remain the home
for committed product work.

---

## Files in this folder

| File                   | Purpose                                                                                 |
| :--------------------- | :-------------------------------------------------------------------------------------- |
| `README.md`            | This file. Purpose, lifecycle, operator guidance.                                       |
| `open-items.md`        | The live ledger. One canonical table; every row originates in an artefact's local section. |
| `archive/`             | Time-bucketed snapshots of closed / dropped items. Never the live state.                |

---

## Lifecycle at the central plane

The ledger mirrors the lifecycle defined in §3 of the governance rule. The summary below
focuses on what an operator does at the central plane; the canonical state machine lives
in the rule.

1. **Authoring is local.** Skills write open items into the artefact's own document-level
   `## Open Items` section first. The central ledger never invents rows.
2. **Sync is explicit.** `util-open-items` reads the local sections, deduplicates against
   existing ledger rows, assigns the canonical `OI-NNNN` ID on first sync, and writes the
   resulting row into `open-items.md`. Both `Source anchor` and `Source heading` are
   preserved on every synced row.
3. **Status transitions follow the rule.** `open → in-progress → (closed | dropped)` is the
   happy path; `blocked` is a side state. Moving a row to `closed` or `dropped` requires a
   non-`_TBD_` `Tracker ref` (PR, ADR, plan increment, runbook, audit report).
4. **Closed / dropped rows linger.** They stay on the live table for one review cycle
   (default 30 days) so they remain visible in retrospectives, then move to `archive/` per
   §6 of the governance rule.
5. **Audit verifies, never mutates.** `util-metamodel-audit` cross-checks ledger rows
   against local sections and reports drift; it does not write back. Operator remediation
   is always via `util-open-items` or a direct edit to the source artefact.

---

## Operator guidance

The detail of each operation belongs to `util-open-items/SKILL.md`. The pointers below are
the minimum vocabulary an operator needs at this folder.

**Adding a new item.** Add the row in the artefact's `## Open Items` section first, using
the canonical schema (`OI-ID`, `Type`, `Summary`, `Source anchor`, `Source heading`,
`Resolution path`, `Priority`, `Status`, `Owner`, `Due / Review date`, `Tracker ref`). Run
`util-open-items` in `sync` mode to roll it into the central ledger.

**Changing status.** Edit the local row in the source artefact, then re-sync. The ledger
follows the artefact, not the other way around. The only exception is when an item exists
only at governance scope (no artefact home) — those rows are entered directly into
`open-items.md` and flagged with a `_central-only_` marker in `Source heading`.

**Closing an item.** Set `Status` to `closed`, fill the `Tracker ref` with the resolving
PR, ADR, plan increment, or audit report URL, and set `Due / Review date` to the closure
date. Do **not** delete the row — it must linger for one review cycle before archival.

**Dropping an item.** Set `Status` to `dropped`, fill `Resolution path` with the rationale
(why we chose not to act), and `Tracker ref` with the discussion link (PR comment, meeting
note, ADR rejection). Same archival rule.

**Archiving.** Run `util-open-items` in `archive` mode at the end of each review cycle to
move eligible `closed` / `dropped` rows into a time-bucketed file under `archive/`. The
live ledger never silently loses history; archival is explicit and dated.

---

## Schema (canonical)

The canonical table schema lives in §4 of `rules/open-items-governance.md`. Reproduced here
for operator convenience — if these diverge, the rule wins:

| Column              | Meaning                                                                                                          |
| :------------------ | :--------------------------------------------------------------------------------------------------------------- |
| `OI-ID`             | Ledger-assigned `OI-NNNN` after first sync; pre-sync local ID prior to that.                                     |
| `Type`              | One of `doc-gap`, `decision-gap`, `execution-item`, `tech-debt`.                                                  |
| `Summary`           | One-sentence, self-contained statement of the open item.                                                          |
| `Source artefact`   | Relative path to the originating artefact, anchored at the repo root (e.g. `docs/architecture/research/0003.md`). |
| `Source anchor`     | Short fragment identifier (e.g. `#q3`, `#stage-onboarding`) — stable jump target.                                 |
| `Source heading`    | Full heading text the anchor resolves to — survives anchor renames.                                                |
| `Resolution path`   | What closing looks like (`Open ADR on token strategy`, `Schedule into refactor epic E-07`).                       |
| `Priority`          | `low` \| `medium` \| `high` \| `critical`.                                                                        |
| `Status`            | `open` \| `in-progress` \| `blocked` \| `closed` \| `dropped`.                                                    |
| `Owner`             | Person accountable; `_TBD_` if unassigned.                                                                        |
| `Due / Review date` | ISO 8601. For terminal states, the closure date.                                                                  |
| `Tracker ref`       | Link to resolving PR / ADR / plan / runbook / audit report; `_TBD_` while `open`.                                 |

The ledger adds `Source artefact` relative to the per-artefact local section, which only
needs the in-document anchor + heading pair. Skills MAY append informational columns after
`Tracker ref`, but MUST NOT reorder or drop the canonical ones.

---

## Anti-patterns

- **Editing the ledger first.** The local artefact section is the authoring surface. If a
  row exists only in the central ledger without a `Source artefact` field, that is a bug.
- **Treating `_TODO_` placeholders as open items.** Inline scaffold debt is measured by
  `util-metamodel-audit` Check 8 and is reported separately; it does not belong in this
  ledger.
- **Silent deletion.** Rows leave the live ledger only via the archive flow. If a row
  needs to disappear without being archived (mis-classified, duplicate), record the
  deletion intent and the rationale in the same operation that removes the row.
- **Mixing this folder into `docs/` audits.** `util-metamodel-audit` treats this path as
  control-plane data, not as a docs artefact. Do not move the ledger under `docs/`.

---

## See also

- [`rules/open-items-governance.md`](../../rules/open-items-governance.md) — canonical
  contract: section name, schema, taxonomy, lifecycle.
- `util-open-items/SKILL.md` — operator manual for ledger sync, triage, close, archive,
  and report.
- `util-metamodel-audit/references/check-catalogue.md` — governance drift checks.
