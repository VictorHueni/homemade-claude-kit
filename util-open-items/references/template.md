# Open Items Ledger — Template & Worked Sync Example

This file shows the canonical ledger table skeleton and a worked end-to-end sync example
so an operator (or a future agent invocation) can reproduce the mechanics of `sync` mode
without reverse-engineering them from the live ledger.

The schema, taxonomy, and lifecycle live in
[`rules/open-items-governance.md`](../../rules/open-items-governance.md). This file is a
copy-pasteable template, not an independent definition.

---

## 1. Canonical ledger table skeleton

The live ledger at `project-control/open-items/open-items.md` uses this header and
column order. The ledger extends the local artefact schema with `Source artefact`
inserted after `Summary`.

```markdown
## Open Items

| OI-ID | Type | Summary | Source artefact | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref |
| :---- | :--- | :------ | :-------------- | :------------ | :------------- | :-------------- | :------- | :----- | :---- | :---------------- | :---------- |

_None at present._ The ledger initialises empty; the first sync from any artefact will
populate it. Do not scaffold placeholder rows here — empty is the correct initial state
per §2 of the governance rule.
```

The same 12-column shape is used for every archive file under
`project-control/open-items/archive/<YYYY-Q[1-4]>.md`.

---

## 2. Local artefact section template

Use this exact heading + table header inside any artefact that may carry unresolved work.
The local schema is the canonical 11 columns (the ledger adds `Source artefact` on sync).

```markdown
## Open Items

| OI-ID  | Type | Summary | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref |
| :----- | :--- | :------ | :------------ | :------------- | :-------------- | :------- | :----- | :---- | :---------------- | :---------- |

_None at present._
```

When the artefact has actionable rows, replace the `_None at present._` line with the
populated rows. Do NOT mix the placeholder line with real rows — either the section is
empty (placeholder line only) or it is populated (placeholder line removed).

---

## 3. Worked sync example

This example walks through one sync invocation end-to-end. The source artefact is an
`arch-research` note with two `## Open Items` rows; the central ledger is empty.

### Before sync — source artefact

`docs/architecture/research/0003-token-auth.md`:

```markdown
## Open Items

| OI-ID  | Type          | Summary                                | Source anchor | Source heading                          | Resolution path                  | Priority | Status | Owner   | Due / Review date | Tracker ref |
| :----- | :------------ | :------------------------------------- | :------------ | :-------------------------------------- | :------------------------------- | :------- | :----- | :------ | :---------------- | :---------- |
| OI-001 | decision-gap  | Auth model for partner API undecided   | #q3           | Q3 — How do partners authenticate?      | Open ADR on token strategy       | high     | open   | victor  | 2026-06-15        | _TBD_       |
| OI-002 | doc-gap       | Threat model for refresh tokens absent | #q5           | Q5 — What is the refresh-token threat model? | Extend research note §Threats | medium   | open   | _TBD_   | 2026-07-01        | _TBD_       |
```

### Before sync — central ledger

`project-control/open-items/open-items.md`:

```markdown
## Open Items

| OI-ID | Type | Summary | Source artefact | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref |
| :---- | :--- | :------ | :-------------- | :------------ | :------------- | :-------------- | :------- | :----- | :---- | :---------------- | :---------- |

_None at present._
```

### Invocation

```text
util-open-items sync docs/architecture/research/0003-token-auth.md
```

### Sync mechanics (what the skill does)

1. Read the source artefact and locate the document-level `## Open Items` section.
2. Parse the two rows; validate `Type` values against the four-value taxonomy; validate
   that no terminal-state row carries `Tracker ref: _TBD_` (none here — both rows are
   `open`).
3. Look up duplicates against the empty ledger — none found.
4. Mint IDs: the ledger is empty, so the next ID is `OI-0001`. Assign `OI-0001` to the
   first row and `OI-0002` to the second.
5. Write the canonical IDs back to the source artefact (`OI-001` → `OI-0001`, `OI-002` →
   `OI-0002`).
6. Append two rows to the central ledger with `Source artefact` populated and
   `Source anchor` + `Source heading` preserved verbatim.

### After sync — source artefact (rewritten in place)

```markdown
## Open Items

| OI-ID   | Type          | Summary                                | Source anchor | Source heading                          | Resolution path                  | Priority | Status | Owner   | Due / Review date | Tracker ref |
| :------ | :------------ | :------------------------------------- | :------------ | :-------------------------------------- | :------------------------------- | :------- | :----- | :------ | :---------------- | :---------- |
| OI-0001 | decision-gap  | Auth model for partner API undecided   | #q3           | Q3 — How do partners authenticate?      | Open ADR on token strategy       | high     | open   | victor  | 2026-06-15        | _TBD_       |
| OI-0002 | doc-gap       | Threat model for refresh tokens absent | #q5           | Q5 — What is the refresh-token threat model? | Extend research note §Threats | medium   | open   | _TBD_   | 2026-07-01        | _TBD_       |
```

### After sync — central ledger

```markdown
## Open Items

| OI-ID   | Type          | Summary                                | Source artefact                                       | Source anchor | Source heading                                  | Resolution path                  | Priority | Status | Owner  | Due / Review date | Tracker ref |
| :------ | :------------ | :------------------------------------- | :---------------------------------------------------- | :------------ | :---------------------------------------------- | :------------------------------- | :------- | :----- | :----- | :---------------- | :---------- |
| OI-0001 | decision-gap  | Auth model for partner API undecided   | docs/architecture/research/0003-token-auth.md         | #q3           | Q3 — How do partners authenticate?              | Open ADR on token strategy       | high     | open   | victor | 2026-06-15        | _TBD_       |
| OI-0002 | doc-gap       | Threat model for refresh tokens absent | docs/architecture/research/0003-token-auth.md         | #q5           | Q5 — What is the refresh-token threat model?    | Extend research note §Threats    | medium   | open   | _TBD_  | 2026-07-01        | _TBD_       |
```

---

## 4. Worked close example

Continuing from the sync example above, the ADR has now been written and merged.

### Invocation

```text
util-open-items close OI-0001 --tracker-ref https://github.com/example/repo/pull/142
```

### Close mechanics

1. Locate `OI-0001` in `project-control/open-items/open-items.md` and verify its current
   state is `open`, `in-progress`, or `blocked` (it is `open`).
2. Verify the supplied `--tracker-ref` is non-`_TBD_`.
3. Update the ledger row:
   - `Status: closed`
   - `Tracker ref: https://github.com/example/repo/pull/142`
   - `Due / Review date: 2026-05-25` (today, as the closure date).
4. Locate the matching row in the source artefact (matched by `OI-0001` ID) and apply
   the same three updates so the local section stays in sync.
5. Leave the row on the live ledger — it becomes archive-eligible in 30 days.

### After close — ledger row

```markdown
| OI-0001 | decision-gap | Auth model for partner API undecided | docs/architecture/research/0003-token-auth.md | #q3 | Q3 — How do partners authenticate? | Open ADR on token strategy | high | closed | victor | 2026-05-25 | https://github.com/example/repo/pull/142 |
```

---

## 5. Worked archive example

Thirty days after the closure above, the row becomes archive-eligible.

### Invocation

```text
util-open-items archive --older-than 30d
```

### Archive mechanics

1. Scan `open-items.md` for rows with `Status: closed` or `Status: dropped` and
   `Due / Review date` older than today minus 30 days.
2. Append eligible rows to `project-control/open-items/archive/2026-Q2.md`, creating the
   file with the canonical 12-column header if it does not exist.
3. Only after the rows are persisted to the archive file, delete them from
   `open-items.md`.
4. Refresh the `§Status snapshot` block in `open-items.md` to reflect the new totals.

---

## 6. Field-by-field reference

The columns below are reproduced for operator convenience. The rule wins on every
conflict:

| Column              | Allowed values / format                                                                   |
| :------------------ | :---------------------------------------------------------------------------------------- |
| `OI-ID`             | Pre-sync local token (any short string) → canonical `OI-NNNN` after sync. Monotonic, never recycled. |
| `Type`              | `doc-gap` \| `decision-gap` \| `execution-item` \| `tech-debt`.                            |
| `Summary`           | One-sentence statement of the open item. Self-contained.                                   |
| `Source artefact`   | (Ledger-only field) Relative repo path to the source document.                             |
| `Source anchor`     | Short fragment identifier (`#q3`, `#stage-onboarding`, `#vp-2`). Stable jump target.        |
| `Source heading`    | Full heading text the anchor resolves to. Readable provenance.                              |
| `Resolution path`   | What closing looks like (`Open ADR on token strategy`, `Schedule into refactor epic E-07`). |
| `Priority`          | `low` \| `medium` \| `high` \| `critical`.                                                  |
| `Status`            | `open` \| `in-progress` \| `blocked` \| `closed` \| `dropped`.                              |
| `Owner`             | Person accountable; `_TBD_` if unassigned.                                                  |
| `Due / Review date` | ISO 8601. For terminal states, the closure date.                                            |
| `Tracker ref`       | URL to resolving PR / ADR / plan increment / runbook / audit report; `_TBD_` while `open`. Mandatory for terminal states. |

---

## 7. Anti-patterns to refuse during sync

The `sync` mode refuses to act on:

- A nested `### Open Items` heading anywhere in the source artefact — only document-level
  `## Open Items` is canonical.
- A row whose `Type` is not one of the four allowed values.
- A row whose `Status` is `closed` or `dropped` but whose `Tracker ref` is `_TBD_`.
- A row whose `Source anchor` and `Source heading` are both empty (governance-only rows
  must be entered directly via `report` mode or operator editing, not synced).
- A duplicate row with a conflicting `OI-NNNN` — the operator must merge manually before
  re-syncing.

When refusing, the skill prints the refusal reason + the conflicting row + a pointer to
the relevant section of `rules/open-items-governance.md`. It never partially syncs.
