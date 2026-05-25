# Methodology References — util-metamodel-scaffold

Internal reference. Not copied to projects. Explains the rationale behind the skill's
design decisions.

---

## Why always scaffold the full tree?

An early design considered variant-aware scaffolding (greenfield / brownfield /
strategy-only / single-feature), where each variant would create a different subset of
folders. The variant model was dropped for two reasons:

1. **Empty folders are free.** Git ignores empty directories until a file lands in them.
   `util-metamodel-audit` checks for *files*, not *folders* — an empty
   `docs/ops/runbooks/` on a single-feature project produces no audit findings and no
   noise. The cost of having extra empty directories is exactly zero.

2. **Variant selection adds complexity with no payoff.** A four-way configuration
   question, a promotion mechanism for growing projects, and four parallel folder lists
   to maintain — all to avoid a handful of empty directories that nobody sees.

The simpler rule: one universal structure, every project, every time. Teams fill what
they need and ignore the rest. This is the same principle as `git init` — it does not
ask whether the project is small or large.

---

## Why `.gitkeep` for empty directories?

Git does not track empty directories. A scaffold that creates only `mkdir -p` commands
leaves a structure that vanishes on `git clone` — the next developer or agent session
sees none of the intended skeleton.

`.gitkeep` is a zero-byte sentinel file that satisfies git's content-tracking requirement
without polluting the namespace with meaningful filenames. It is removed automatically when
the first real file is added to the directory (the presence of any other file makes the
`.gitkeep` redundant — skills that write to a folder do not need to delete it explicitly;
the directory continues to be tracked via its new content).

This is the same convention used in the kit's own `project-control/open-items/archive/`.

---

## Why scaffold `project-control/open-items/` rather than leaving it to `util-open-items`?

`util-open-items` is a **runtime operator** — its `sync` mode reads artefact-local
`## Open Items` sections and writes rows to the central ledger. It assumes the ledger
path (`project-control/open-items/open-items.md`) already exists. When it doesn't, `sync`
fails with a file-not-found error before any row is processed.

The scaffold is the correct place to initialise the control plane because:
1. It runs before any artefact-producing skill, so the structure exists when needed.
2. The initial content (empty ledger with canonical schema, README) is project-agnostic
   and deterministic — it does not require operator input.
3. `util-open-items` remains the sole authoritative writer of row data; the scaffold only
   creates the structural skeleton.

The strategy-only and single-feature variants omit `project-control/` because those
project types rarely produce artefact-level open items at scale. If open items are later
needed, the user can re-run scaffold Mode 2 with a larger variant (idempotent).

---

## Why not add `var/reports/` to `.gitignore` automatically?

Some teams commit audit reports deliberately — for audit trail purposes, for async review
in a pull request, or because they lack a separate CI artefact store. Auto-modifying
`.gitignore` would silently remove that option.

The skill surfaces the suggestion as a one-liner in the closing report. The operator makes
the choice. This is the same philosophy as the report-only discipline in `util-metamodel-audit`
and `util-metamodel-migration`: surface findings, let the operator act.

---

## Why does INDEX.md use `review_interval: 30d`?

The INDEX.md is a generated snapshot, not an authored artefact. Its content becomes stale
the moment any stack step changes status. A 30-day review interval triggers `util-metamodel-audit`
Check 12 (staleness) frequently enough to prompt regular refreshes without being so short
that every sprint produces an audit warning.

Mode 3 regenerates INDEX.md in seconds. The cost of refreshing is negligible; the cost of
a stale INDEX.md misleading an agent into skipping a completed step is high.

---

## Sources

| Source | What it informs |
|---|---|
| Git documentation — gitignore(5) | `.gitkeep` convention and universal-tree rationale |
| `util-open-items/SKILL.md` | Project-control scope boundary |
| `rules/open-items-governance.md` | Control-plane initialisation requirements |
| `util-metamodel-audit/references/methodology-references.md` | Report-only / suggest-only discipline |
