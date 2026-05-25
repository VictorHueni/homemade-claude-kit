---
name: util-metamodel-scaffold
description: "Initialise the canonical docs/ folder tree for a new project, generate a live INDEX.md navigation hub in docs/, and wire a stack pointer into CLAUDE.md. Variant-aware: greenfield (full tree), brownfield (start at capability map), strategy-only (business layer only), or single-feature (product-specs + exec-plans only). Triggers on: scaffold the docs, initialise the project, set up the docs folder, create the documentation structure, create the folder structure, init metamodel, build the doc tree, scaffold docs, start the documentation."
version: "1.0.0"
status: active
last_reviewed: 2026-05-25
review_interval: 180d
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "utility"
  complexity: "low"
---

# Metamodel Scaffold

Initialise the canonical `docs/` folder tree, generate a live `docs/INDEX.md` navigation
hub, and wire a stack pointer into `CLAUDE.md`. Run this skill once at the start of every
new project — before any artefact-producing skill is invoked.

The canonical folder tree and artefact paths are defined in `rules/metamodel.md`. This
skill operationalises that definition: it creates the directories, documents them in an
INDEX.md snapshot, and tells the agent where to look. It does NOT create artefact content
— that is the job of the `business-*`, `domain-*`, `spec-*`, `arch-*`, `ops-*`, and
`com-*` skills.

**Complement to `util-metamodel-migration`:** migration restructures an existing docs/
folder that predates the metamodel. Scaffold initialises a fresh structure. Run scaffold
on new projects; run migration on existing ones.

---

## The three modes

### Mode 1 — Full scaffold (default)

**When:** starting a new project with no existing `docs/` structure.

**Step 0 — Clarifying questions (ask BEFORE running)**

Ask the user these 3 questions in a single message. Users respond like `1A, 2B, 3A`:

```text
1. Project variant?
   A. Greenfield — full canonical tree (default)
   B. Brownfield — existing system adding capability (skip personas + BMC layers)
   C. Strategy-only — investor / executive engagement (business layer + comms)
   D. Single-feature — no full architecture work (product-specs + exec-plans only)

2. Docs root?
   A. docs/ (default)
   B. Other — please specify

3. Wire the stack pointer into CLAUDE.md after scaffold?
   A. Yes — update CLAUDE.md (or create it if absent)
   B. No — scaffold only; I will update CLAUDE.md manually
```

Also ask for the **project name** if it is not already clear from context — used in the INDEX.md header.

**Pre-flight check (run before creating anything):**

```bash
existing=$(find {docs_root} -name "*.md" 2>/dev/null | wc -l)
echo "Existing markdown files in {docs_root}: $existing"
```

If `{docs_root}` already contains markdown files, warn the user:

> "`docs/` already has N markdown file(s). Running scaffold will create any missing
> canonical folders and **overwrite `docs/INDEX.md`** with a fresh status snapshot.
> Existing artefact files are NOT touched.
> If the folder structure needs restructuring (files in wrong locations), run
> `util-metamodel-migration` instead. Continue with scaffold? (Y/N)"

If the user says N, stop and suggest `util-metamodel-migration` Mode 1.
If the user says Y, proceed.

**Process:**
1. Read the folder list for the chosen variant from `references/folder-catalogue.md`.
2. For each folder in the list: `mkdir -p {folder}`.
3. Place a `.gitkeep` in every empty leaf folder so the tree is git-trackable.
4. **For greenfield and brownfield variants:** create the `project-control/open-items/`
   control plane — see §Project-control scaffold below.
5. **`.gitignore` check:**
   ```bash
   grep -q 'var/reports' .gitignore 2>/dev/null \
     || echo "SUGGEST: 'var/reports/' is not in .gitignore — generated reports should not be committed."
   ```
   Record the result; surface it in the closing report.
6. Detect the current status of each canonical artefact path (bash — same logic as
   `util-metamodel-audit` Check 1) and generate `docs/INDEX.md` from
   `references/index-template.md`.
7. If the user chose to wire CLAUDE.md (Step 0 option 3A): apply the stack pointer update
   (see §CLAUDE.md update rules below).

**Output verification:**
- All variant-appropriate folders exist (`find {docs_root} -type d | sort`).
- `docs/INDEX.md` exists and contains a row for every canonical artefact step.
- For greenfield/brownfield: `project-control/open-items/open-items.md` and
  `project-control/open-items/README.md` exist.
- If wired: `CLAUDE.md` contains a reference to `docs/INDEX.md`.
- No artefact content files created — only folders, `.gitkeep` files, `docs/INDEX.md`,
  and the `project-control/open-items/` control-plane stubs.
- If `var/reports/` is absent from `.gitignore`, this was surfaced in the closing report.

---

### Mode 2 — Folders only

**When:** the user wants the directory structure but will manage INDEX.md and CLAUDE.md
separately, or a hub doc already exists.

No Step 0 questions needed beyond variant + docs root.

**Process:**
1. Read folder list from `references/folder-catalogue.md` for the chosen variant.
2. `mkdir -p` each folder; place `.gitkeep` in empty leaf folders.
3. Report: folders created / folders already existed.

No INDEX.md generated. No CLAUDE.md update.

---

### Mode 3 — INDEX.md refresh

**When:** the project already has a `docs/` structure; the user wants to regenerate
`docs/INDEX.md` with fresh status detection (after completing several stack steps, for
example).

**Process:**
1. Detect docs root (check for existing `docs/INDEX.md` or default to `docs/`).
2. Re-run the status detection bash commands from `references/index-template.md §Detection`.
3. Update the `last_reviewed` field in the frontmatter to today's date before writing.
4. Overwrite `docs/INDEX.md` with the refreshed status snapshot.
5. Report: N steps now ✅ / N steps 🔄 / N steps ⬜.

Does NOT create folders or touch CLAUDE.md.

---

## Folder creation — bash pattern

For each folder in the variant list (from `references/folder-catalogue.md`):

```bash
# Create all variant folders in one pass
mkdir -p \
  docs/business/05a-processes \
  docs/domain/07b-models \
  ...   # (full list from folder-catalogue.md for the chosen variant)

# Place .gitkeep in leaf folders that have no content yet
find docs -mindepth 1 -type d | while read d; do
  if [ -z "$(ls -A "$d" 2>/dev/null)" ]; then
    touch "$d/.gitkeep"
  fi
done
```

**Rules:**
- Use `mkdir -p` — safe to run on existing trees; never fails if folder already exists.
- Never delete or overwrite existing files.
- Report how many folders were created vs already existed.
- `var/reports/` directories are created by this skill (audit + migration report targets).
- `project-control/open-items/` is created by this skill for greenfield and brownfield
  variants (see §Project-control scaffold). For strategy-only and single-feature it is
  omitted — those variants rarely produce artefact-level open items at scale.

---

## Project-control scaffold

**Scope:** greenfield and brownfield variants only (Mode 1, step 4).

Creates the minimal `project-control/open-items/` control plane so `util-open-items`
can run `sync` immediately after the first artefact is authored. Without this structure,
the first sync fails with a missing-path error.

**Files created:**

```bash
mkdir -p project-control/open-items/archive
touch project-control/open-items/archive/.gitkeep
```

Then write two stub files:

**`project-control/open-items/open-items.md`** — empty ledger with canonical schema,
sourced from `util-open-items/references/template.md §1` (canonical ledger table skeleton):

```markdown
# Open Items — Living Ledger

This is the consolidated, repo-wide ledger of unresolved work synced from every
artefact's local `## Open Items` section. It is the operational system of record
described in §5 of `rules/open-items-governance.md`.

The ledger is **not** a product artefact — no frontmatter, no review cadence.
See `README.md` for purpose, lifecycle, and operator guidance.

---

## How rows arrive here

1. A skill emits an open item into the source artefact's `## Open Items` section.
2. `util-open-items sync` reads the local section, deduplicates, assigns `OI-NNNN`,
   and writes the row here — extended with `Source artefact` (relative repo path).

---

## Live items

| OI-ID | Type | Summary | Source artefact | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref |
| :---- | :--- | :------ | :-------------- | :------------ | :------------- | :-------------- | :------- | :----- | :---- | :---------------- | :---------- |

_None at present._ The ledger initialises empty; the first sync from any artefact
will populate it.

---

## Status snapshot

_No snapshot yet — the ledger has not received its first sync._

---

## See also

- `README.md` — operator guidance for this folder.
- `rules/open-items-governance.md` — canonical schema, taxonomy, lifecycle.
- `util-open-items/SKILL.md` — ledger CRUD operating manual.
```

**`project-control/open-items/README.md`** — operator orientation. Copy the content of
the existing `project-control/open-items/README.md` in the kit as-is — it is
project-agnostic and applies verbatim to any project scaffolded with this skill.

**Safety rules:**
- If `project-control/open-items/open-items.md` already exists (non-empty repo): skip
  creation entirely and report "control plane already present".
- Never overwrite an existing non-empty ledger.

---

## `.gitignore` check

Run at the end of Mode 1 (step 5). If `var/reports/` is not in `.gitignore`:

1. Surface in the closing report: "⚠️ `var/reports/` is not in `.gitignore`. Generated
   audit and migration reports should not be committed. Add to `.gitignore`:"
   ```
   var/reports/
   ```
2. Do NOT automatically modify `.gitignore` — the user may have a reason for tracking
   reports (e.g. in a shared team context). Surface it as a suggestion, not an auto-fix.

---

## INDEX.md generation

The INDEX.md is a **point-in-time snapshot** — a navigation hub with live status detected
at the moment the skill runs. It is not a truly dynamic dashboard; run Mode 3 to refresh.

Full template and detection commands in `references/index-template.md`.

**Status detection per step:**

```bash
# Detect status for each canonical path.
# ✅ Done    — file/folder found AND < 50% lines are _TODO_
# 🔄 In progress — file/folder found AND ≥ 50% lines are _TODO_
# ⬜ Not started — no file/folder found

check_status() {
  local path="$1"
  if [ -f "$path" ]; then
    total=$(wc -l < "$path")
    todos=$(grep -c '_TODO_' "$path" 2>/dev/null || echo 0)
    [ "$total" -gt 0 ] && ratio=$(( todos * 100 / total )) || ratio=0
    [ "$ratio" -ge 50 ] && echo "🔄" || echo "✅"
  elif [ -d "$path" ] && [ -n "$(ls "$path"/*.md 2>/dev/null)" ]; then
    echo "✅"
  else
    echo "⬜"
  fi
}
```

**INDEX.md frontmatter:** the file lives under `docs/` so it must carry the 5-field
frontmatter schema from `rules/artefact-frontmatter.md`. Use:
- `status: active` — it is always current (it's a generated snapshot, not a draft)
- `review_interval: 30d` — refresh frequently (mode 3 re-generates it in seconds)

---

## CLAUDE.md update rules

Mirrors the wire-mode pattern from `business-vision`.

1. Check if `CLAUDE.md` exists at the project root.
2. Check if a stack pointer is already present:
   ```bash
   grep -q 'INDEX.md\|metamodel.*scaffold\|documentation stack' CLAUDE.md 2>/dev/null \
     && echo "already wired"
   ```
3. **If already wired:** report and skip. Never duplicate.
4. **If `CLAUDE.md` exists but no stack pointer:** append the following block (Edit tool,
   never overwrite):

   ```markdown

   ## Documentation stack (read at session start)

   This project uses the homemade-claude-kit strategic-architecture metamodel.

   - **Index:** [`docs/INDEX.md`](docs/INDEX.md) — live artefact status table; run
     `util-metamodel-scaffold` Mode 3 to refresh.
   - **Build order:** `rules/metamodel.md` (11 steps; variant: {variant})
   - **Audit:** run `util-metamodel-audit` for full health checks
   - **Scaffolded:** {YYYY-MM-DD}

   Before doing any documentation work: read `docs/INDEX.md` to know which steps are
   complete (✅), in progress (🔄), or not started (⬜), and which skill to invoke next.
   ```

5. **If `CLAUDE.md` does not exist:** create it with the block above as the only content,
   wrapped in a minimal header:

   ```markdown
   # Project Context

   ## Documentation stack (read at session start)

   This project uses the homemade-claude-kit strategic-architecture metamodel.

   - **Index:** [`docs/INDEX.md`](docs/INDEX.md) — live artefact status table; run
     `util-metamodel-scaffold` Mode 3 to refresh.
   - **Build order:** `rules/metamodel.md` (11 steps; variant: {variant})
   - **Audit:** run `util-metamodel-audit` for full health checks
   - **Scaffolded:** {YYYY-MM-DD}

   Before doing any documentation work: read `docs/INDEX.md` to know which steps are
   complete (✅), in progress (🔄), or not started (⬜), and which skill to invoke next.
   ```

**Safety rules:**
- NEVER overwrite or truncate an existing `CLAUDE.md`. Append only.
- NEVER duplicate the stack pointer if already present.
- If the existing `CLAUDE.md` already has a "Documentation stack" or "metamodel" section,
  ask the user whether to update it or skip.
- Always show the user exactly what was appended before closing.

---

## Sizing heuristics

| Element | Value |
|---|---|
| Run cadence | Once per project (Mode 1/2); Mode 3 as needed |
| Time to run Mode 1 | < 10 seconds (mkdir + status detection) |
| INDEX.md refresh cadence | After completing each stack step, or before a sprint review |
| Folders created (greenfield) | ~20 directories |
| Folders created (strategy-only) | ~6 directories |

---

## Closing report to the user

After any mode, summarise in 5–7 lines:

1. **Mode run** + **variant** + **docs root**.
2. **Folders created** (N new) / **already existed** (N skipped).
3. **Project-control plane** — created / already present / skipped (strategy-only or single-feature).
4. **INDEX.md** — written / refreshed / skipped; current status breakdown (✅ N / 🔄 N / ⬜ N).
5. **CLAUDE.md** — updated / created / skipped / already wired.
6. **`.gitignore`** — `var/reports/` present ✅ or missing ⚠️ (suggest the one-liner to add).
7. **Next step** — variant-specific first skill to invoke:
   - Greenfield → `business-vision` Mode 1 (scaffold) then Mode 2 (fill) then Mode 3 (wire)
   - Brownfield → `business-capability-map` Mode 1 (scaffold) then Mode 2 (structure)
   - Strategy-only → `business-vision` Mode 1+2 or `business-model-canvas` Mode 1
   - Single-feature → `spec-idea` (if feature not yet committed) or `spec-prd` Mode 1

---

## Reference materials

- **`references/folder-catalogue.md`** — complete folder list per variant with `mkdir -p` commands.
- **`references/index-template.md`** — INDEX.md skeleton and per-step status detection bash commands.
- **`references/methodology-references.md`** — rationale for variant model, `.gitkeep` discipline, project-control scope, and `.gitignore` policy.

---

## Checklist

Before declaring the work done:

- [ ] Step 0 answered (Mode 1) or mode detected from context.
- [ ] Pre-flight check run: docs root inspected for existing markdown files; user confirmed before proceeding if content was found.
- [ ] Variant confirmed — folder list selected from `references/folder-catalogue.md`.
- [ ] All variant-appropriate folders created (`mkdir -p`).
- [ ] `.gitkeep` placed in every empty leaf folder.
- [ ] Project-control plane created (greenfield/brownfield) or skipped with acknowledgement (strategy-only/single-feature/already exists).
- [ ] `.gitignore` checked; result surfaced in closing report.
- [ ] `docs/INDEX.md` written (Modes 1 + 3) with `last_reviewed` set to today, or skipped with acknowledgement (Mode 2).
- [ ] `docs/INDEX.md` contains a row for every canonical step (not only those for the chosen variant).
- [ ] `docs/INDEX.md` frontmatter present (5 fields per `rules/artefact-frontmatter.md`).
- [ ] CLAUDE.md updated / created (Mode 1 with option 3A) or skipped with acknowledgement.
- [ ] No artefact content files created — folders + `.gitkeep` + INDEX.md + control-plane stubs only.
- [ ] Closing report delivered with variant-specific next-step recommendation.
