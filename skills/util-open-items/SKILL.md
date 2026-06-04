---
name: util-open-items
description: "Maintain the repo-wide living ledger of unresolved governance work at `docs/project-control/open-items/open-items.md`. Use this skill to sync local `## Open Items` sections from artefacts into the central ledger, triage incoming rows, close or drop items with a tracker ref, archive terminal rows at the end of a review cycle, and produce status reports. Triggers on: sync open items, triage open items, close open item, drop open item, archive open items, open-items report, roll up open items, OI-NNNN, central ledger, docs/project-control/open-items."
version: "1.2.0"
status: active
last_reviewed: 2026-06-04
review_interval: 180d
user-invocable: true
allow_implicit_invocation: true
impact: "medium"
metadata:
  category: "infrastructure"
  complexity: "medium"
---

# util-open-items — Open Items Ledger Operator

Operate the central control plane for unresolved governance work. This skill is the only
sanctioned writer of `docs/project-control/open-items/open-items.md`; every other skill emits
open items into its own artefact's document-level `## Open Items` section and then chains
to this skill to push them into the ledger.

The canonical contract — section name, schema, taxonomy, lifecycle, central-plane rules —
lives in [`rules/open-items-governance.md`](../rules/open-items-governance.md). This skill
is the operating manual that turns the contract into repeatable mechanics. When the rule
and this file diverge, the rule wins; this skill must then be reconciled.

---

## Backends

The central plane is a **serialization** of the §4 model (governance §5.3). This skill
operates one of two backends:

- **`markdown`** (default) — the living ledger at
  `docs/project-control/open-items/open-items.md` plus `archive/`. Mints `OI-NNNN`.
- **`github`** — GitHub Issues + one Project (v2) as the consolidated read-out. Identity is
  the issue number `#N`; `OI-NNNN` is retired.

**Declaration.** A project selects its backend in
`docs/project-control/open-items/backend.yml`; absent ⇒ `markdown`:

```yaml
backend: github          # markdown (default) | github
repo: owner/name         # github only — where the issues live
project: 7               # github only — the Project (v2) number for the read-out
```

**What stays the same regardless of backend:** the local `## Open Items` section is always
§4 markdown (Invariant I4) — only what `sync` *writes to* changes. The abstract model,
taxonomy, lifecycle, and provenance composite are identical (governance §4/§5.3).

**One backend per project.** Never both. Moving between them is a one-way
`markdown → github` migration (planned — `OI-0029`), never a live two-way sync.

**Operational github mapping.** Before operating the `github` backend, read
[`references/github-backend.md`](references/github-backend.md) — the normative slug
contract, serialization, identity translation, status decomposition, and invariants
I1–I5. The authoring surface for a github-backend project is the issue form
[`templates/open-item.form.yml`](templates/open-item.form.yml).

**github adoption checklist** (per project, one-time):

1. Copy `templates/open-item.form.yml` → `.github/ISSUE_TEMPLATE/open-item.yml`.
2. Create the four Issue Types: `doc-gap`, `decision-gap`, `execution-item`, `tech-debt`.
3. Create the Project (v2) with `Status` (Open / In progress / Blocked), `Priority`, and a
   `Review date` field.
4. Add `docs/project-control/open-items/backend.yml` with `backend: github` + `repo` +
   `project`.

---

## When to invoke

Invoke `util-open-items` whenever:

- An artefact has just been generated or updated and its `## Open Items` section has new,
  changed, or terminal rows → run `sync`.
- A new row was authored locally without an `OI-NNNN` ID → run `sync` to assign one.
- A row needs review for priority, owner, or de-duplication against the ledger → run
  `triage`.
- An open item has been resolved by a PR / ADR / plan increment / runbook / audit
  report → run `close` (or `drop` if abandoned).
- A review cycle ends and terminal rows are eligible for archival → run `archive`.
- Someone wants a snapshot of governance health → run `report`.

Do NOT invoke this skill to mutate `_TODO_` scaffold placeholders in artefact bodies —
those are scaffold debt, audited by `util-metamodel-audit` Check 8, and are not open items.

---

## Modes

This skill exposes seven modes — six steady-state operations plus a one-time `migrate`
cutover (Mode 7, `markdown → github`). Each mode reads or writes
`docs/project-control/open-items/open-items.md` and respects the lifecycle in
`rules/open-items-governance.md` §3.

### Mode 1 — `sync`

Roll local `## Open Items` rows from one or more artefacts into the central ledger.

Input:

- One or more artefact paths (e.g. `docs/architecture/research/0003-token-auth.md`). If no
  path is given, scan every `docs/**/*.md` for a document-level `## Open Items` section.

Process:

1. **Read each source artefact** and locate the document-level `## Open Items` section
   (top-level `^## Open Items` heading; reject nested `### Open Items` per §1 of the
   governance rule).
2. **Parse rows** using the canonical column order (`OI-ID`, `Type`, `Summary`,
   `Source anchor`, `Source heading`, `Resolution path`, `Priority`, `Status`, `Owner`,
   `Due / Review date`, `Tracker ref`). Reject rows with missing mandatory columns or with
   a `Type` outside the four-value taxonomy.
3. **Match each row against the ledger.** Identity is the triple `(Source artefact path,
   Source anchor, Summary fingerprint)`. If the row already carries a canonical `OI-NNNN`
   ID, that ID wins.
4. **Assign IDs.** For unmatched rows, mint the next monotonic `OI-NNNN` starting from
   `OI-0001`. Compute the next ID from the maximum currently in `open-items.md` plus the
   maximum in every `archive/*.md` file — never recycle.
5. **Write back to the source artefact.** Replace the local pre-sync ID with the
   canonical `OI-NNNN`. The source artefact remains the authoring surface; after sync it
   simply carries the ledger ID.
6. **Write the ledger row.** In `open-items.md` use the extended schema (canonical 11
   columns + `Source artefact` inserted after `Summary`). Preserve `Source anchor` and
   `Source heading` verbatim — this is the provenance contract from §4 of the governance
   rule and is non-negotiable.
7. **Reconcile drift.** If a ledger row's `Source heading` changed in the source artefact,
   update the ledger row but keep `OI-NNNN` and `Source anchor` stable. If
   `Source anchor` changed, update both fields and log the rename in §Status snapshot.

Refuse to sync if:

- The source artefact's `## Open Items` section is `### Open Items` (nested) — point the
  operator at §1 of the governance rule.
- A row's `Type` is not one of `doc-gap`, `decision-gap`, `execution-item`, `tech-debt`.
- A row carries `Status: closed` or `Status: dropped` with `Tracker ref: _TBD_` — §3
  requires a non-`_TBD_` tracker ref before reaching a terminal state.

### Mode 2 — `triage`

Walk every `open` and `in-progress` row in the ledger and propose owner, priority, and
de-duplication changes. Triage never mutates the source artefact silently; it produces a
diff or proposal list for operator approval.

Process:

1. Cluster rows by `Source artefact` and by `Resolution path` to surface duplicates.
2. Flag rows with `Owner: _TBD_` older than 14 days as triage-needed.
3. Flag rows with `Priority: critical` or `high` and no `Tracker ref` movement as
   escalation candidates.
4. Output a triage report (in-memory or written to
   `var/reports/open-items/triage-YYYY-MM-DD.md` if the operator requests a file).

### Mode 3 — `close`

Move a single row to terminal state `closed`.

Input: `OI-NNNN`, `Tracker ref` (PR / ADR / plan increment / runbook / audit report URL),
optional closure-date override (default: today).

Process:

1. Verify the row exists in `open-items.md` and is in state `open`, `in-progress`, or
   `blocked`.
2. Verify `Tracker ref` is a non-`_TBD_` value — §3 requires it.
3. Update the ledger row: `Status: closed`, `Tracker ref: <value>`,
   `Due / Review date: <closure-date>`.
4. Mirror the change back to the source artefact's local `## Open Items` row (so the
   authoring surface stays in sync).
5. Leave the row on the live ledger for one review cycle (default 30 days) before it
   becomes archive-eligible.

### Mode 4 — `drop`

Same mechanics as `close` but the terminal state is `dropped`.

Required extra input: a rationale sentence in `Resolution path` explaining why the item is
abandoned (e.g. "Superseded by ADR-0007"). `Tracker ref` still required — typically the
discussion link (PR comment, ADR rejection, meeting note).

### Mode 5 — `archive`

Move eligible terminal rows out of the live ledger into a time-bucketed snapshot.

Process:

1. Identify rows in `open-items.md` with `Status: closed` or `Status: dropped` whose
   `Due / Review date` is older than 30 days (configurable per invocation).
2. Move those rows into `docs/project-control/open-items/archive/<YYYY-Q[1-4]>.md`, creating
   the bucket file with the canonical 12-column ledger schema if it does not already
   exist.
3. Remove the rows from `open-items.md` only after they have been written to the archive
   file. Never silently delete — the move is the audit trail.
4. Update §Status snapshot in `open-items.md` to reflect the new totals.

### Mode 6 — `report`

Produce a governance-health snapshot.

Output sections:

- **Counts.** `open` / `in-progress` / `blocked` / `closed` / `dropped` totals.
- **By type.** Distribution across `doc-gap`, `decision-gap`, `execution-item`,
  `tech-debt`.
- **Oldest open items.** Top-N by age.
- **Stale closure candidates.** Rows in `closed` / `dropped` older than 30 days (i.e.
  archive-eligible — feeds Mode 5).
- **Coverage map.** Source artefacts with at least one open item; soft-flag artefacts
  that have a `## Open Items` section but zero rows for more than two review cycles (may
  indicate stale governance).

Write to `var/reports/open-items/report-YYYY-MM-DD.md`. Never mutates the ledger.

### Mode 7 — `migrate` (markdown → github, one-way)

One-time cutover of a project from the `markdown` backend to `github`. Enforces Invariant I2
(governance §5.3): one-way only, emits the `OI-NNNN → #N` map, never a reverse or concurrent
sync.

**Preconditions:** the github adoption checklist (§Backends) is done — form installed, Issue
Types created, Project exists, `gh` authenticated against the target repo. The `markdown`
ledger `open-items.md` is the source.

**Driver:** [`scripts/migrate_markdown_to_github.py`](scripts/migrate_markdown_to_github.py)
— stdlib + `gh`, **dry-run by default**.

```text
# 1. Dry-run — prints planned issues + the OI-NNNN→#N map + ref-rewrite diff, mutates nothing
python3 scripts/migrate_markdown_to_github.py --repo OWNER/NAME

# 2. Apply — create issues, write the map, rewrite OI-NNNN back-references across docs/
python3 scripts/migrate_markdown_to_github.py --repo OWNER/NAME --apply
```

**Per live ledger row:**

1. De-dups by summary + provenance (`gh issue list --search`) — re-runs are idempotent.
2. `gh issue create` — `summary`→title, `type`→Issue Type, provenance + `resolution_path`→
   form-structured body, `owner`→assignee.
3. Lifecycle: `open` stays open; `in-progress`/`blocked` stay open (set the Project Status
   field manually — the script logs which); `closed`→close `completed`; `dropped`→close
   `not planned` (original `tracker_ref` preserved as a comment).
4. Records `OI-NNNN → #N`, writing the map to
   `docs/project-control/open-items/migration-map.md` (the persisted I2 artefact).
5. Rewrites every `OI-NNNN` back-reference under `--docs` (OI-ID cells + prose) to `#N`.

**Operator finish (not automated — verify first):**

1. Eyeball the issues + Project board.
2. Set Project `Status` for any `in-progress`/`blocked` rows.
3. Move `open-items.md` into `archive/` as a frozen, dated snapshot — never silent-delete (§6).
4. Set `backend.yml: github`. From here `sync` / `close` / etc. operate the github backend.

**Rollback** (before step 3–4): the migration is one-way, so undo = delete the created issues
and `git checkout` the ref rewrites while the markdown ledger is still authoritative.

`archive/*.md` history stays as frozen markdown (optionally backfilled as closed issues
later). Issue Type + Project-field assignment are `gh`-version-dependent; the script logs
anything it could not set so you can finish via the GitHub UI or GraphQL.

---

## Backend behaviour per mode (`github`)

Under `backend: github`, the six modes keep their contract but retarget GitHub via `gh`. The
local `## Open Items` section is still the input; only the central writes change. See
[`references/github-backend.md`](references/github-backend.md) for the full field mapping.

| Mode | `github` behaviour |
| :--- | :--- |
| `sync` | For each local row without a resolved `#N`: `gh issue create` from the form fields — `summary` → title, `type` → Issue Type + form dropdown, provenance + `resolution_path` → form body, `priority` → Project field; set assignee = `owner`, Project `Review date` = `review_date`. Write the resulting `#N` back into the local row's `OI-ID` cell. De-dup by `(source_artefact, source_anchor, summary)` via `gh issue list --search` before creating. |
| `triage` | `gh issue list` / `gh project item-list` to cluster duplicates, flag `_TBD_` assignees and stale high-priority items. Proposal only — never mutates silently. |
| `close` | `gh issue close --reason completed`. The closing reference (`Closes #N` / linked PR) **is** the `tracker_ref` — evidence is structurally enforced, so the §3 `_TBD_` guard cannot be violated. |
| `drop` | `gh issue close --reason "not planned"`; record the rationale as an issue comment (the `Resolution path` analog). |
| `archive` | No-op. Closed issues are the archive (searchable indefinitely); there is no `archive/` file. |
| `report` | Render from the Project (v2) view / `gh` queries instead of the markdown ledger. May still emit a `var/reports/open-items/report-YYYY-MM-DD.md` snapshot. |

Refusal conditions from `sync` (nested `### Open Items`, invalid `Type`, terminal status
with `_TBD_` tracker) apply unchanged — they are validated on the **local** section before
any `gh` call.

---

## ID assignment

**`markdown` backend only.** Under `github`, identity is the issue number `#N` (native,
monotonic, never recycled) and no `OI-NNNN` is minted — skip this section.

Canonical IDs are `OI-NNNN` (four-digit zero-padded, monotonic).

- The next ID is computed by scanning every row in `open-items.md` AND every
  `archive/*.md` file for the highest `OI-NNNN` value, then incrementing by one.
- Pre-sync local IDs in source artefacts MAY use any short token (e.g. `OI-001`); they
  are replaced by the canonical `OI-NNNN` on first sync, and the source artefact is
  rewritten in place.
- IDs are never recycled. A `dropped` row's ID stays with that row forever, including
  after it moves to `archive/`.

---

## Source-location provenance

Every synced ledger row preserves three coordinates back to its origin:

| Field             | Where it comes from                                                          |
| :---------------- | :--------------------------------------------------------------------------- |
| `Source artefact` | Relative repo path to the source document (e.g. `docs/business/04a-value-streams.md`). |
| `Source anchor`   | Short fragment identifier from the local row (e.g. `#stage-onboarding`, `#q3`). |
| `Source heading`  | Full heading text the anchor resolves to (e.g. `Stage 2: Onboarding`).        |

The pair `(Source anchor, Source heading)` is the provenance contract from
[`rules/open-items-governance.md`](../rules/open-items-governance.md) §4. Both halves are
required because:

- The anchor is the stable jump target — surviving heading edits.
- The heading is the readable context — surviving anchor renames.

Governance-only items (raised directly at the central plane with no artefact home) carry
`_central-only_` in `Source heading`, an empty `Source anchor`, and an empty
`Source artefact`. `util-metamodel-audit` does not flag these as orphans (per the README
in `docs/project-control/open-items/`).

---

## De-duplication policy

A row is considered a duplicate of an existing ledger row when ALL of the following match:

1. `Source artefact` is identical (path, post-rename normalisation).
2. `Source anchor` is identical OR `Source heading` is identical (one half of the
   provenance pair is enough — heading changes alone are not duplicates).
3. `Summary` shares ≥80% lexical overlap (case-insensitive, whitespace-normalised) with
   the existing row OR explicitly references the same `Resolution path`.

When `sync` detects a duplicate:

- If the local row carries no `OI-NNNN`: adopt the existing ledger row's ID and write it
  back to the source artefact. No new row is created.
- If the local row carries a different `OI-NNNN`: refuse the sync and produce an operator
  warning naming both IDs — the operator must merge manually (typically by `drop`-ping
  the newer ID with rationale `Duplicate of OI-NNNN`).

---

## Closure semantics

Closure is event-driven, not date-driven:

- A row becomes `closed` only when a real tracker reference exists (PR merged, ADR
  written, plan increment shipped, runbook published, audit report acted on).
- A row becomes `dropped` only when an explicit decision exists not to act (recorded in
  `Resolution path`, with the discussion link in `Tracker ref`).
- Reaching a `Due / Review date` without a tracker ref does NOT auto-close the row — it
  surfaces in `triage` as an escalation candidate.
- Closed and dropped rows stay on the live ledger for one review cycle (default 30 days)
  so they remain visible in retrospectives. After that, `archive` moves them out.

The 30-day linger period is intentional: it is the difference between "we resolved this
item" and "we have forgotten about it". Retrospectives, post-mortems, and quarterly
audits use the linger period to scan recent resolutions for patterns.

---

## Operator-facing examples

**Sync after authoring an arch-research note:**

```text
util-open-items sync docs/architecture/research/0003-token-auth.md
# → reads the document-level ## Open Items section,
#   mints OI-NNNN for any unmatched rows,
#   writes those IDs back into the source file,
#   appends rows to docs/project-control/open-items/open-items.md.
```

**Close a resolved decision gap:**

```text
util-open-items close OI-0007 --tracker-ref https://github.com/.../pull/142
# → updates the ledger row + the source artefact row to Status: closed.
```

**End-of-quarter archive sweep:**

```text
util-open-items archive --older-than 30d
# → moves eligible closed/dropped rows into archive/2026-Q2.md,
#   refreshes the §Status snapshot block in open-items.md.
```

**Governance health report:**

```text
util-open-items report
# → writes var/reports/open-items/report-2026-05-25.md with counts,
#   type distribution, oldest open items, and coverage map.
```

---

## Output paths

| Path                                                          | Owner                                  |
| :------------------------------------------------------------ | :------------------------------------- |
| `docs/project-control/open-items/open-items.md`                    | This skill (sync / close / drop / archive). |
| `docs/project-control/open-items/archive/<YYYY-Q[1-4]>.md`         | This skill (archive only).             |
| `var/reports/open-items/triage-YYYY-MM-DD.md`                 | This skill (triage report).            |
| `var/reports/open-items/report-YYYY-MM-DD.md`                 | This skill (report mode).              |
| The source artefact's document-level `## Open Items` section. | This skill (sync writes back IDs only). |

The `open-items.md` / `archive/` paths above apply to the **`markdown` backend**. Under
**`github`**, those central writes go to GitHub Issues + the Project instead (via `gh`); the
only repo-file this skill writes is the local `## Open Items` section (writing back `#N`).

This skill MUST NOT write to any other path. In particular it MUST NOT mutate
`util-metamodel-audit` reports (those are produced by a separate report-only skill) and
MUST NOT touch artefact body content outside the document-level `## Open Items` table.

---

## Reference files

- [`references/template.md`](references/template.md) — canonical ledger table skeleton and
  worked sync example (`markdown` backend).
- [`references/triage-rules.md`](references/triage-rules.md) — operator playbook for
  triage mode (de-duplication, priority escalation, owner assignment).
- [`references/github-backend.md`](references/github-backend.md) — normative `github`-backend
  mapping: slug contract, serialization, identity translation, status decomposition,
  invariants I1–I5.
- [`templates/open-item.form.yml`](templates/open-item.form.yml) — the GitHub Issue Form
  (authoring surface for the `github` backend); copy to `.github/ISSUE_TEMPLATE/` on adoption.
- [`scripts/migrate_markdown_to_github.py`](scripts/migrate_markdown_to_github.py) — the
  one-way `markdown → github` migration driver for Mode 7 (dry-run by default; emits the
  `OI-NNNN → #N` map and rewrites back-references).

---

## See also

- [`rules/open-items-governance.md`](../rules/open-items-governance.md) — canonical
  contract; the rule wins on every conflict.
- [`docs/project-control/open-items/README.md`](../docs/project-control/open-items/README.md) —
  operator orientation for the central control plane.
- `util-metamodel-audit/references/check-catalogue.md` — governance-drift audit (report
  only; never mutates).
