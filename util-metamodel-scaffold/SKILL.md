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

**Process:**
1. Read the folder list for the chosen variant from `references/folder-catalogue.md`.
2. For each folder in the list: `mkdir -p {folder}`.
3. Place a `.gitkeep` in every leaf folder that has no content yet, so the tree is git-trackable.
4. Detect the current status of each canonical artefact path (bash — same logic as
   `util-metamodel-audit` Check 1) and generate `docs/INDEX.md` from
   `references/index-template.md`.
5. If the user chose to wire CLAUDE.md (Step 0 option 3A): apply the stack pointer update
   (see CLAUDE.md update rules below).

**Output verification:**
- All variant-appropriate folders exist (`find {docs_root} -type d | sort`).
- `docs/INDEX.md` exists and contains a row for every canonical artefact step.
- If wired: `CLAUDE.md` contains a reference to `docs/INDEX.md`.
- No artefact content files were created — only folders, `.gitkeep` files, and `docs/INDEX.md`.

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
3. Overwrite `docs/INDEX.md` with the refreshed status snapshot.
4. Report: N steps now ✅ / N steps 🔄 / N steps ⬜.

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
- `var/` and `project-control/` are out-of-scope for this skill — those are created by
  `util-metamodel-audit` and `util-open-items` respectively when first needed.

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

After any mode, summarise in 3–5 lines:

1. **Mode run** + **variant** + **docs root**.
2. **Folders created** (N new) / **already existed** (N skipped).
3. **INDEX.md** — written / refreshed / skipped; current status breakdown (✅ N / 🔄 N / ⬜ N).
4. **CLAUDE.md** — updated / created / skipped / already wired.
5. **Next step** — which skill to invoke to begin documentation work (based on variant and INDEX.md status).

---

## Reference materials

- **`references/folder-catalogue.md`** — complete folder list per variant with `mkdir -p` commands.
- **`references/index-template.md`** — INDEX.md skeleton and per-step status detection bash commands.

---

## Checklist

Before declaring the work done:

- [ ] Step 0 answered (Mode 1) or mode detected from context.
- [ ] Variant confirmed — folder list selected from `references/folder-catalogue.md`.
- [ ] All variant-appropriate folders created (`mkdir -p`).
- [ ] `.gitkeep` placed in every empty leaf folder.
- [ ] `docs/INDEX.md` written (Modes 1 + 3) or skipped with acknowledgement (Mode 2).
- [ ] `docs/INDEX.md` contains a row for every canonical step (not only those for the chosen variant).
- [ ] `docs/INDEX.md` frontmatter present (5 fields per `rules/artefact-frontmatter.md`).
- [ ] CLAUDE.md updated / created (Mode 1 with option 3A) or skipped with acknowledgement.
- [ ] No artefact content files created — folders + `.gitkeep` + INDEX.md only.
- [ ] Closing report delivered with next-step recommendation.
