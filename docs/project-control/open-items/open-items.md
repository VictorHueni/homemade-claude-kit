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

| OI-ID | Type | Summary | Source artefact | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref |
| :---- | :--- | :------ | :-------------- | :------------ | :------------- | :-------------- | :------- | :----- | :---- | :---------------- | :---------- |

_None at present._ The ledger initialises empty; the first sync from any artefact will
populate it. Do not scaffold placeholder rows here — empty is the correct initial state
per §2 of the governance rule.

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

_No snapshot yet — the ledger has not received its first sync._

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
