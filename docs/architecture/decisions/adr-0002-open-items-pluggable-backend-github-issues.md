---
title: Central Open-Items Plane — Pluggable Backend with GitHub Issues for the Kit Repo
status: active
owner: Victor Hueni
last_reviewed: 2026-06-04
review_interval: 180d
---

# Central Open-Items Plane — Pluggable Backend with GitHub Issues for the Kit Repo

Date: 2026-06-03

## Context and Problem Statement

The kit governs unresolved work through the contract in [`rules/open-items-governance.md`](../../../rules/open-items-governance.md). That contract has two surfaces:

1. **Authoring surface** — a document-level `## Open Items` table inside each artefact, co-located with the work that spawned it, version-controlled and diffable in the same PR (§1, §4).
2. **Central read-out** — a consolidated living ledger at `docs/project-control/open-items/open-items.md`, with minted `OI-NNNN` IDs, plus time-bucketed `archive/*.md` snapshots (§5, §6). Operated solely by `util-open-items`; audited (report-only) by `util-metamodel-audit` (§7).

The central read-out is a flattened roll-up: assign an ID, track a lifecycle, evidence a closure, view the open set. That is precisely what an issue tracker plus a board does — natively, and arguably better than a hand-maintained Markdown table (the ID is free and monotonic, closure-by-reference is unfakeable, and a Project view beats a static table for filtering and grouping).

The question this ADR settles: **should the central read-out move to GitHub Issues, and if so, how — without breaking the kit's domain-agnostic, user-global design?** The kit scaffolds into arbitrary projects (GitHub, GitLab, Gitea, local-only, air-gapped, or no remote at all), so a hard dependency on GitHub Issues for *every* project is not acceptable. The kit repo itself, however, already lives on GitHub.

This decision is scoped to the **kit repo's own ledger** as the first step (dogfood, learn, then decide separately whether to generalise the contract). It does **not** yet rewrite the contract for every scaffolded project.

## Decision Drivers

- **Preserve domain-agnostic portability.** The kit must still work for projects with no GitHub remote. A GitHub-only central plane violates the kit's user-global premise.
- **Keep the authoring surface intact.** Co-located, in-repo, PR-diffable `## Open Items` sections are the strongest part of the current design and have no equivalent in an issue tracker; they must not move.
- **Make closure evidence structural, not conventional.** §3 requires a non-`_TBD_` `Tracker ref` to reach a terminal state; today that is a human-typed convention. A native closing reference enforces it.
- **Retire avoidable bookkeeping.** `OI-NNNN` minting, the 30-day linger, and explicit `archive/*.md` snapshots are mechanics the Markdown backend needs but a tracker provides for free (issue number, closed-issue search).
- **One canonical model.** Whatever the storage, there must be a single logical schema so `util-metamodel-audit` and `util-open-items` reason about one contract, not two forks.
- **Don't commit downstream projects prematurely.** The approach should be proven on the kit before the universal contract is touched.

## Considered Options

1. **Pluggable backend; GitHub backend for the kit repo (chosen).** `util-open-items` gains a `backend:` setting (`markdown` | `github`). The §4 schema stays the single source of truth; each backend is a serialization of it. The kit repo selects `github`; other projects keep `markdown`.
2. **GitHub Issues become canonical everywhere.** Issues fully replace `open-items.md` for every project. Simplest mental model and best UX, but hard-requires a GitHub remote + Issues + `gh` auth, breaking non-GitHub and offline projects.
3. **GitHub as a one-way projection.** Markdown stays canonical; a sync pushes rows to read-only Issues. Preserves in-repo audit but maintains two surfaces permanently and cannot accept edits back from Issues.
4. **Status quo.** Keep the Markdown ledger everywhere; do nothing. No new dependency, but forgoes the native ID, structural closure evidence, and a better read-out even where GitHub is available.

## Decision Outcome

Chosen option: **Option 1 — pluggable backend, with the kit repo on the `github` backend.**

This is recorded as a single decision, not two: the backend abstraction and the choice of `github` for the kit repo are deliberately coupled, because the abstraction exists precisely to make the `github` choice adoptable without sacrificing the kit's domain-agnostic portability. Splitting them would record an abstraction with no driver and a backend choice with no escape hatch.

The authoring surface is unchanged: local `## Open Items` sections remain §4 Markdown in **both** backends, so they are backend-agnostic. `util-open-items sync` is the adapter boundary — it reads the same §4 Markdown and writes *either* `open-items.md` *or* GitHub Issues, depending on `backend:`. A project selects exactly **one** backend; the two are never run concurrently (that would reintroduce a dual source of truth).

### GitHub primitive mapping (when `backend: github`)

| §4 model field | GitHub primitive |
| :--- | :--- |
| `OI-ID` | Issue number `#N` (native; `OI-NNNN` minting retired in this backend) |
| `Type` (4-value taxonomy) | Issue Type (`doc-gap`, `decision-gap`, `execution-item`, `tech-debt`) |
| `Summary`, `Resolution path` | Issue Form fields |
| `Source artefact` / `Source anchor` / `Source heading` | Issue Form fields with stable `id:` keys mirroring §4 column names |
| `Priority` | Project single-select field |
| `Status` | open/closed natively · `in-progress`/`blocked` via Project Status field · `dropped` = close **as "not planned"** |
| `Owner` | Assignee |
| `Due / Review date` | Project date field / Milestone |
| `Tracker ref` | Native closing reference (`Closes #N` / linked PR) |
| Central read-out | A saved GitHub Project (v2) view (replaces `report`-mode table) |
| Archive + 30-day linger | Closed issues (searchable indefinitely); explicit `archive/` largely retired |
| Central-only rows (§5.2) | Issues with `Source heading: _central-only_`, scope label for the owning skill |

Schema enforcement moves to an Issue Form (`.github/ISSUE_TEMPLATE/open-item.yml`): required dropdowns for `Type` and `Priority`, required fields for the provenance triple and `Resolution path`. The form enforces the contract at creation time — stronger than a Markdown column header that relies on correct hand-entry.

### Data model & interoperability

- **§4 is the shared contract.** Both backends serialize the one logical model defined in `open-items-governance.md` §4. The Issue Form field `id:` keys MUST mirror the §4 column names so `util-metamodel-audit` can read either backend from a single field map.
- **Schema-interoperable always; instance-interoperable once, one-way.** A clean `markdown → github` migration is sanctioned at adoption time. Bidirectional or concurrent sync is **not** sanctioned — two live writers over two ID spaces is the dual-source-of-truth anti-pattern.
- **The crossing is slightly lossy by design.** `OI-NNNN` is retired in favour of `#N` (identity is re-minted: a former `OI-NNNN` becomes its GitHub issue number `#N`), and the explicit `archive/` is absorbed into closed-issue search. Migration MUST emit an `OI-NNNN → #N` map so existing back-references (and any `Tracker ref` pointing at an old `OI-ID`) can be rewritten.
- **`Status` is composite on the GitHub side** (open/closed + Project field + close-reason), not a single column — round-trippable, but not field-for-field.

### Tooling consequences

- `util-open-items` gains a `backend:` setting. `github` mode wraps `gh issue create/edit/close` and `gh project`; `close`/`drop`/`triage` become thin `gh` wrappers; `archive` is effectively a no-op.
- `util-metamodel-audit` gains a parallel check path that reads Issue-Form bodies via `gh` to verify provenance and a valid `Type`, instead of parsing the Markdown ledger. For the `github` backend the audit therefore requires `gh` auth and network access — acceptable for the kit repo (always on GitHub), and a primary reason this ADR does **not** yet make GitHub the universal contract.
- `rules/open-items-governance.md` §5–§7 require revision to describe the two backends and the adapter boundary; that edit is implementation work tracked as open items, not part of this decision.

### Positive Consequences

- Native, monotonic, never-recycled ID for free; no `OI-NNNN` minting in this backend.
- Closure evidence (§3) becomes structurally impossible to fake.
- A Project view is a materially better read-out than a static Markdown table.
- The kit stays domain-agnostic: non-GitHub and offline projects keep the Markdown backend unchanged.
- The kit dogfoods the change on itself before any downstream project is committed.

### Negative Consequences

- Two backends to build and maintain in `util-open-items` and `util-metamodel-audit`.
- For the `github` backend, audit and ledger operations require `gh` auth and network access — the ledger's history leaves the repo and is no longer PR-diffable or air-gapped-auditable.
- The provenance triple has no native structured field; it lives in Issue-Form fields whose `id:` keys become a load-bearing contract the audit depends on.
- Migration is one-way and re-mints IDs; back-references must be rewritten via the emitted ID map.

## Dogfood findings — Mode 7 dry-run (2026-06-04)

A dry-run of `util-open-items` Mode 7 against the kit repo
(`VictorHueni/homemade-claude-kit` — personal, 0 existing issues) confirmed the migration
*plan* (32 issues: 20 open + 12 closed; form-structured bodies render with all canonical
slug fields) but surfaced four portability gaps that block a faithful `--apply` on a solo /
personal repo. These are the concrete evidence for `#36`:

1. **Issue Types are org-level.** `repos/.../issue-types` → 404; `gh issue create --type
   doc-gap` cannot set a native Issue Type on a personal repo. The `type → Issue Type`
   mapping needs a **`type:<value>` label fallback** when Issue Types are unavailable.
2. **`owner` ≠ GitHub login.** The ledger `owner` is `victor`, but the account login is
   `VictorHueni`; `--assignee victor` errors. Migration needs an **owner→login mapping**
   (or to drop the assignee when unmatched).
3. **No `open-item` label / no Project.** Both must be bootstrapped first; the token also
   lacked the `project` scope.
4. **Form not installed** (expected — it ships as a skill template, copied on adoption).

**Conclusion (input to #36):** the `github` backend as specced assumes org-grade Issue
Types + a Project + `owner`==login — fine for an org repo, not portable to a solo personal
repo without adaptation. Generalising it to the universal contract should be **gated on a
portability pass** (type→label fallback, owner→login mapping, label/Project bootstrap helper)
rather than done as-is. The kit therefore **stays on the `markdown` backend** for now; no
issues were created.

**Update — portability pass done (#37, PR #4).** The script-side gaps (1)–(3) are now
fixed in `migrate_markdown_to_github.py`: it auto-detects missing Issue Types and falls back
to `type:<value>` labels, bootstraps `open-item` + `type:` labels idempotently, and takes
`--assignee-map LEDGER_OWNER=LOGIN` (skipping `_TBD_`/unmapped owners instead of erroring). A
re-run dry-run against the kit repo now plans all 33 issues cleanly (0 native `--type`, 33
`type:` labels, assignees only for mapped owners). A real `--apply` is therefore viable;
**#36 (the generalise decision) stays open** pending an actual apply + an operating
period to judge the GitHub-Issues experience.

## Open Items

| OI-ID | Type | Summary | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref |
| :---- | :--- | :------ | :------------ | :------------- | :-------------- | :------- | :----- | :---- | :---------------- | :---------- |
| #31 | execution-item | Revise `open-items-governance.md` §5–§7 to define the two-backend model and adapter boundary | #tooling-consequences | Tooling consequences | Edit the governance rule | high | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| #32 | execution-item | Add `backend:` setting + `github` mode (gh issue/project wrappers) to `util-open-items` | #tooling-consequences | Tooling consequences | Update `util-open-items/SKILL.md` + references | high | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| #33 | execution-item | Add `github`-backend check path to `util-metamodel-audit` (read Issue-Form bodies via `gh`) | #tooling-consequences | Tooling consequences | Update audit check catalogue | medium | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| #34 | execution-item | Author `.github/ISSUE_TEMPLATE/open-item.yml` with `id:` keys mirroring §4 columns | #data-model--interoperability | Data model & interoperability | Write the issue form | high | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| #35 | execution-item | Build one-way `markdown → github` migration emitting an `OI-NNNN → #N` map | #data-model--interoperability | Data model & interoperability | Add a migration mode/script | medium | closed | victor | 2026-06-04 | [#3](https://github.com/VictorHueni/homemade-claude-kit/pull/3) |
| #36 | decision-gap | Decide whether to generalise the `github` backend to the universal contract after dogfooding | #context-and-problem-statement | Context and Problem Statement | Resolved: declined to generalise — `github` stays opt-in, `markdown` the universal default (ADR-0003) | low | closed | victor | 2026-06-04 | [ADR-0003](adr-0003-github-backend-stays-opt-in.md) |
| #37 | execution-item | Make Mode 7 portable to personal repos — Issue-Types→`type:` label fallback + owner→login `--assignee-map` + idempotent label bootstrap | #dogfood-findings--mode-7-dry-run-2026-06-04 | Dogfood findings — Mode 7 dry-run (2026-06-04) | Implement in `migrate_markdown_to_github.py`; re-validate via dry-run | medium | closed | victor | 2026-06-04 | [#4](https://github.com/VictorHueni/homemade-claude-kit/pull/4) |
