# Check Catalogue — util-metamodel-audit

For each of the 16 checks: bash detection pattern, interpretation rules, severity, and proposed fix template. Claude reads this file during audit execution to know exactly how to run each check.

---

## Check 1 — Stack progress

**What:** verifies which of the 11 canonical output paths exist.

**Detection:**
```bash
# Run for each step — adapt path per step number
find docs -maxdepth 1 -name "VISION.md" 2>/dev/null                              # Step 0
find docs -maxdepth 4 -name "personas.md" -path "*/personas/*" 2>/dev/null
find docs -maxdepth 4 \( -name "business-model-canvas.md" -o -name "lean-canvas.md" \) 2>/dev/null
find docs -maxdepth 4 -name "capability-map.md" 2>/dev/null
find docs -maxdepth 4 -name "value-streams.md" 2>/dev/null
find docs/business/objectives -name "objectives.md" 2>/dev/null              # Step 4.5
find docs/business/processes -name "*-process.md" 2>/dev/null | head -1
find docs/business/models -name "*.md" 2>/dev/null | head -1
find docs -maxdepth 5 -name "FBS.md" 2>/dev/null
find docs -maxdepth 4 -name "epic-catalogue.md" 2>/dev/null
find docs -maxdepth 5 -name "quality-attributes.md" 2>/dev/null
find docs/product-specs -maxdepth 1 -name "*_prd_*.md" 2>/dev/null | head -1
find docs/exec-plans/active -mindepth 1 -maxdepth 1 -type d 2>/dev/null | head -1
find docs/domain/bounded-contexts -name "bounded-contexts.md" 2>/dev/null  # Step 2b
find docs/domain/glossary -name "glossary.md" 2>/dev/null                  # Step 2c
find docs/domain -name "domain-model.md" 2>/dev/null | head -1              # Step 7b (per BC)
```

**Status assignment:**
- ✅ Done — canonical file/folder found
- 🔄 In progress — file found but >50% _TODO_ content
- ⬜ Not started — no file found

**Severity:** Info

**Proposed fix template:** "Run `{skill}` Mode 1 (scaffold) to create the missing artefact."

---

## Check 2 — Folder placement

**What:** finds markdown files that exist but are not in their canonical location per the stack rule.

**Detection:**
```bash
find docs -name "*.md" | while read f; do echo "$f"; done
```
Then compare each path against the canonical map:
- `VISION.md` → must be directly under `docs/` (not nested deeper — singleton)
- `personas.md` → must be under `docs/business/personas/`
- `capability-map.md` → must be under `docs/business/capability-map/`
- `value-streams.md` → must be under `docs/business/value-streams/`
- `objectives.md` → must be under `docs/business/objectives/`
- `*-process.md` → must be under `docs/business/processes/`
- `business-model-canvas.md` / `lean-canvas.md` → must be under `docs/business/business-model-canvas/`
- `FBS.md` → must be under `docs/product-specs/functional-breakdown-structure/`
- `epic-catalogue.md` → must be at `docs/product-specs/epic-catalogue.md`
- `quality-attributes.md` → must be under `docs/product-specs/quality-attributes/`
- `*_prd_*.md` → must be under `docs/product-specs/`
- `*.md` under `docs/architecture/decisions/` → ADRs, correct

**Severity:** Warning

**Proposed fix template:** "Move `{file}` to `{canonical_path}` and update any links pointing to the old location."

---

## Check 3 — Internal links

**What:** finds relative markdown links that resolve to non-existent files.

**Detection:**
```bash
grep -rn '\[.*\](\.\./' docs/ --include="*.md" | grep -v '^\s*<!--' | grep -v '```'
```
For each match, extract the relative path, resolve it from the source file's directory, and check existence:
```bash
# pseudo-pattern per link
source_dir=$(dirname "$source_file")
resolved=$(realpath --relative-to=. "$source_dir/$link_target" 2>/dev/null)
[ -f "$resolved" ] || echo "BROKEN: $source_file → $link_target"
```
Also check anchor fragments: if link is `file.md#section-id`, verify the heading `# Section Id` exists in `file.md`.

**Severity:** Error

**Proposed fix template:** "Update link in `{source_file}` line {N}: `{link_text}` → correct path is `{correct_path}` (or remove if target was deleted)."

---

## Check 4 — External links

**What:** finds dead external URLs and links missing a `Last verified` date.

**Detection — dead links:**
```bash
grep -roh 'https\?://[^)> "]*' docs/ --include="*.md" | sort -u | while read url; do
  status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 --location "$url" 2>/dev/null)
  [ "$status" -ge 400 ] && echo "DEAD ($status): $url"
done
```

**Detection — missing Last verified:**
```bash
# Find lines with http links NOT preceded by "Last verified" within 3 lines
grep -rn 'https\?://' docs/ --include="*.md" | grep -v 'Last verified'
```

**Severity:**
- 4xx/5xx response → Error
- 3xx permanent redirect → Warning (update the URL)
- Missing `Last verified` date → Warning

**Proposed fix template:**
- Dead link: "Replace or remove URL `{url}` in `{file}` line {N}. Suggested replacement: search for updated URL."
- Missing date: "Add `Last verified: {today}` on the line following the URL in `{file}`."

---

## Check 5 — ID cross-references

**What:** finds IDs referenced in one doc that have no definition in their owning artefact.

**ID patterns and owning artefacts:**

| ID format | Regex | Owning artefact |
|---|---|---|
| `P-NN` | `\bP-[0-9]{2}\b` | `docs/business/personas/personas.md` |
| `C-N.M` or `C1.1` | `\bC[0-9]+\.[0-9]+\b` | `docs/business/capability-map/capability-map.md` |
| `VS-N` | `\bVS-[0-9]+\b` | `docs/business/value-streams/value-streams.md` |
| `VS-N.M` | `\bVS-[0-9]+\.[0-9]+\b` | `docs/business/value-streams/value-streams.md` |
| `C-N.M.FXX` | `\bC-[0-9]+\.[0-9]+\.F[0-9]+\b` | `docs/product-specs/functional-breakdown-structure/FBS.md` |
| `BC-NN` | `\bBC-[0-9]{2}\b` | `docs/domain/bounded-contexts/bounded-contexts.md` |
| `BC-NN.GT-NN` | `\bBC-[0-9]{2}\.GT-[0-9]{2}\b` | `docs/domain/glossary/glossary.md` |
| `BC-NN.AGG-NN` | `\bBC-[0-9]{2}\.AGG-[0-9]{2}\b` | `docs/domain/{bc-slug}/domain-model.md` |
| `BC-NN.ENT-NN` | `\bBC-[0-9]{2}\.ENT-[0-9]{2}\b` | `docs/domain/{bc-slug}/domain-model.md` |
| `BC-NN.VO-NN` | `\bBC-[0-9]{2}\.VO-[0-9]{2}\b` | `docs/domain/{bc-slug}/domain-model.md` |
| `BC-NN.EVT-NN` | `\bBC-[0-9]{2}\.EVT-[0-9]{2}\b` | `docs/domain/{bc-slug}/domain-model.md` |
| `OBJ-NN` | `\bOBJ-[0-9]{2}\b` | `docs/business/objectives/objectives.md` |
| `KR-NN.M` | `\bKR-[0-9]{2}\.[0-9]\b` | `docs/business/objectives/objectives.md` |
| `E-NN` | `\bE-[0-9]{2}\b` | `docs/product-specs/epic-catalogue.md` |
| `QA-[A-Z]{2}[0-9]{2}` | `\bQA-[A-Z]{2}[0-9]{2}\b` | `docs/product-specs/quality-attributes/quality-attributes.md` |
| `ADR-NNNN` | `\bADR-[0-9]{4}\b` | `docs/architecture/decisions/` |
| `PRD-NNNN` | `\bPRD-[0-9]{4}\b` | `docs/product-specs/*_prd_*.md` |

**Detection (example for P-NN):**
```bash
# Collect all P-NN references across all docs
grep -roh '\bP-[0-9]\{2\}\b' docs/ --include="*.md" | grep -oP 'P-[0-9]{2}' | sort -u > /tmp/p_refs.txt
# Collect all P-NN definitions in personas.md
grep -oh '\bP-[0-9]\{2\}\b' docs/business/personas/personas.md 2>/dev/null | sort -u > /tmp/p_defs.txt
# Find refs with no definition
comm -23 /tmp/p_refs.txt /tmp/p_defs.txt
```
Repeat for each ID type.

**Severity:** Error

**Proposed fix template:** "ID `{ID}` used in `{source_file}` is not defined in `{owning_artefact}`. Either define it there or correct the reference."

---

## Check 6 — ID integrity

**What:** finds duplicate IDs within a namespace and malformed ID formats.

**Detection — duplicates:**
```bash
# Example for P-NN in personas.md
grep -oh '\bP-[0-9]\{2\}\b' docs/business/personas/personas.md 2>/dev/null | sort | uniq -d
```

**Detection — malformed format:**
```bash
# Single-digit persona IDs (P-1 instead of P-01)
grep -roh '\bP-[0-9]\b' docs/ --include="*.md"
# Single-digit epic IDs
grep -roh '\bE-[0-9]\b' docs/ --include="*.md"
# QA IDs with wrong format
grep -roh '\bQA-[^A-Z ]' docs/ --include="*.md"
```

**Severity:** Error

**Proposed fix template:**
- Duplicate: "Renumber `{ID}` in `{file}` — two definitions of the same ID will corrupt cross-references."
- Malformed: "Fix `{ID}` in `{file}` to canonical format `{correct_format}` and update all references."

---

## Check 7 — Dependency enforcement

**What:** checks that prerequisites defined in the stack DAG exist when a downstream artefact is present.

**Dependency rules to enforce:**

| If this exists | Then this must also exist |
|---|---|
| `value-streams.md` | `capability-map.md` (stages consume capabilities) |
| `FBS.md` | `capability-map.md` (FBS inherits L0+L1) |
| `epic-catalogue.md` | `FBS.md` (epics group FBS functionalities) |
| `quality-attributes.md` | `FBS.md` (QA reads FBS differentiators) |
| Any `*_prd_*.md` | `epic-catalogue.md` (PRDs map to E-NN epics) |
| Any `*_prd_*.md` | `quality-attributes.md` (PRDs reference QA-XXNN) |
| Any `exec-plans/active/*/` plan | Corresponding `*_prd_*.md` |
| `docs/domain/glossary/glossary.md` exists | `docs/domain/bounded-contexts/bounded-contexts.md` must also exist (glossary is scoped to BCs) |
| `docs/domain/{bc-slug}/domain-model.md` exists | `docs/domain/bounded-contexts/bounded-contexts.md` must exist (domain model is namespaced by BC) |
| `docs/domain/{bc-slug}/domain-model.md` exists | `docs/domain/glossary/glossary.md` must exist (entity names must match glossary terms) |
| `docs/business/objectives/objectives.md` exists | `docs/business/value-streams/value-streams.md` must also exist (objectives consume pain index from VS) |
| Any `*_prd_*.md` | If `docs/business/objectives/objectives.md` exists, the PRD should reference ≥1 `OBJ-NN` in §0 |

**Detection (example):**
```bash
[ -f "docs/product-specs/functional-breakdown-structure/FBS.md" ] && \
  [ ! -f "docs/business/capability-map/capability-map.md" ] && \
  echo "WARNING: FBS exists but capability-map.md missing"

[ -f "docs/domain/glossary/glossary.md" ] && \
  [ ! -f "docs/domain/bounded-contexts/bounded-contexts.md" ] && \
  echo "WARNING: Glossary exists but bounded-contexts.md missing"

find docs/domain -name "domain-model.md" 2>/dev/null | while read f; do
  [ ! -f "docs/domain/bounded-contexts/bounded-contexts.md" ] && \
    echo "WARNING: Domain model exists but bounded-contexts.md missing: $f"
  [ ! -f "docs/domain/glossary/glossary.md" ] && \
    echo "WARNING: Domain model exists but glossary missing: $f"
done
```

**Severity:** Warning

**Proposed fix template:** "Create the missing prerequisite artefact using `{skill}` before proceeding. The downstream artefact `{file}` has soft-links that will be `_TODO_` until the prerequisite exists."

---

## Check 8 — _TODO_ density

**What:** counts unfilled `_TODO_` placeholders per file and computes completeness %.

**Detection:**
```bash
find docs -name "*.md" | while read f; do
  todos=$(grep -c '_TODO_' "$f" 2>/dev/null || echo 0)
  total_lines=$(wc -l < "$f")
  echo "$todos $total_lines $f"
done | sort -rn
```

**Interpretation:**
- 0 _TODO_ → complete
- 1–10 _TODO_ → mostly filled; normal for active work
- >50% of lines contain _TODO_ → scaffolded but not filled; flag as Info
- Any _TODO_ in a mandatory field (§8 KPIs, §5.2 assumptions, persona `Goals`) → flag specifically

**Severity:** Info (density); Warning (mandatory field _TODO_)

**Proposed fix template:** "Fill `{field}` in `{file}` using `{skill}` Mode 2 (fill). Priority: {high/medium/low}."

---

## Check 9 — Mandatory sections

**What:** verifies that each file type contains its required sections.

**Rules per file type:**

| File type | Mandatory sections | Detection pattern |
|---|---|---|
| `*-process.md` | `## §8 KPIs` or `## KPIs`, `## §11` or `## Open TODOs`, `## §0 Master flow` | `grep -q 'KPI\|§8'` |
| `docs/business/models/*.md` | `§5.2` or `Implicit assumptions`, `§6` or `Scenario Matrix`, `§7` or `Value capture` | `grep -q '5\.2\|Implicit assumptions'` |
| `personas.md` | `## Persona Backlog`, `## Personas`, `## Persona Template` | `grep -q 'Persona Backlog'` |
| `capability-map.md` | `## L0 axis`, `## Global overview`, `## Capability index` | `grep -q 'L0 axis\|Capability index'` |
| `value-streams.md` | `## Catalogue`, `## Value Streams` | `grep -q '## Catalogue'` |
| `FBS.md` | At least one `### C` capability heading with a functionality table | `grep -q '### C[0-9]'` |
| `epic-catalogue.md` | Epic table with `E-NN` IDs | `grep -q 'E-[0-9][0-9]'` |
| `quality-attributes.md` | ISO characteristic headings (`Performance Efficiency`, `Security`, `Reliability`, etc.) | `grep -q 'Performance Efficiency\|Security\|Reliability'` |
| `*_prd_*.md` | `§0 Architecture Traceability` or traceability block, `## Acceptance criteria` | `grep -q 'Traceability\|Acceptance'` |
| `objectives.md` | At least one `OBJ-NN` heading, `## Changelog`, `## Objective × Epic` section | `grep -q 'OBJ-[0-9][0-9]\|Changelog'` |
| `VISION.md` | `## The Elevator Pitch`, `## What We Are NOT`, `## North Star Metric`, `## Changelog` | `grep -q 'Elevator Pitch\|North Star'` |
| `bounded-contexts.md` | `## Subdomain catalogue`, at least one `BC-NN` entry | `grep -q 'BC-[0-9][0-9]'` |
| `glossary.md` | At least one BC section, `## Changelog` | `grep -q '## Changelog'` |
| `domain-model.md` | `## Aggregate catalogue`, `## Domain event catalogue`, Mermaid `classDiagram` | `grep -q 'Aggregate catalogue\|classDiagram'` |

**Detection (example for process doc):**
```bash
find docs/business/processes -name "*-process.md" 2>/dev/null | while read f; do
  grep -q 'KPI\|§8' "$f" || echo "MISSING KPIs: $f"
  grep -q '§11\|Open TODOs' "$f" || echo "MISSING TODOs section: $f"
done
```

**Severity:** Error

**Proposed fix template:** "Add missing section `{section}` to `{file}`. Template in `{skill} references/template.md §{N}`."

---

## Check 10 — Methodology pointers

**What:** verifies that `business-*` docs contain the kit methodology blockquote in their header section.

**Detection:**
```bash
find docs/business -name "*.md" | while read f; do
  grep -q 'homemade-claude-kit\|methodology-references\|canonical bibliography' "$f" || \
    echo "MISSING methodology pointer: $f"
done
```

**Severity:** Warning (doc created by hand, bypassing the skill; methodology drift risk)

**Proposed fix template:** "Add the 2-line methodology pointer blockquote to `{file}` header. Copy from `~/.claude/skills/{skill}/references/methodology-references.md` first paragraph."

---

## Check 11 — Confidence distribution

**What:** counts `Assumed`, `Tested`, `Validated` labels per file and flags stale-hypothesis patterns.

**Detection:**
```bash
find docs -name "*.md" | while read f; do
  assumed=$(grep -co '\bAssumed\b' "$f" 2>/dev/null || echo 0)
  tested=$(grep -co '\bTested\b' "$f" 2>/dev/null || echo 0)
  validated=$(grep -co '\bValidated\b' "$f" 2>/dev/null || echo 0)
  total=$((assumed + tested + validated))
  [ "$total" -gt 0 ] && echo "$assumed $tested $validated $total $f"
done
```

**Flag condition:** file is 100% Assumed AND was created more than 90 days ago (check git log creation date).

**Severity:** Warning (100% Assumed + >90 days); Info (distribution report only)

**Proposed fix template:** "Run `business-research` Mode 2 (interview script) targeting the Assumed bullets in `{file}` to gather evidence and promote to Tested/Validated."

---

## Check 12 — Expiry + staleness

**What:** finds proto-persona next-review dates that have passed, and competitive landscape claims past their refresh window.

**Detection — proto-persona expiry:**
```bash
grep -n 'Next review' docs/business/personas/personas.md 2>/dev/null
# Compare each date against today
```

**Detection — competitive landscape staleness:**
```bash
grep -rn 'Last verified' docs/business/competitive-landscape/ 2>/dev/null
# For each date, compute days since; flag if > 90 days (fast market) or > 180 days (slow)
```

**Detection — process doc last-updated:**
```bash
find docs/business/processes -name "*-process.md" | while read f; do
  last=$(git log -1 --format="%ci" -- "$f" 2>/dev/null | cut -d' ' -f1)
  echo "$last $f"
done | sort
```

**Severity:**
- Proto-persona past next-review → Error (expired assumption)
- Competitive claim past threshold → Warning
- Process doc not updated in >180 days → Info

**Detection — glossary changelog discipline:**
```bash
# Glossary exists but has no Changelog section → living-doc discipline missing
if [ -f "docs/domain/glossary/glossary.md" ]; then
  grep -q '## Changelog' docs/domain/glossary/glossary.md || \
    echo "WARNING: glossary.md missing Changelog section"
  # Changelog exists but last entry is > 30 days ago for Core BC (sprint cadence)
  last_entry=$(grep -m1 '^### [0-9]' docs/domain/glossary/glossary.md 2>/dev/null | grep -oP '[0-9]{4}-[0-9]{2}-[0-9]{2}')
  [ -n "$last_entry" ] && echo "Glossary last changelog entry: $last_entry"
fi
```

**Severity:**
- Proto-persona past next-review → Error (expired assumption)
- Competitive claim past threshold → Warning
- Process doc not updated in >180 days → Info
- Glossary missing Changelog section → Warning (living-doc discipline missing)
- Glossary changelog last entry >30 days ago → Info (may need sprint review)

**Proposed fix template:**
- Expired persona: "Run `business-research` Mode 2 to validate `{persona}` and update `Next review` date, or mark as retired."
- Stale competitive claim: "Run `business-competitive-landscape` Mode 5 (refresh) for `{competitor}` claim in `{file}`."
- Missing glossary changelog: "Run `domain-glossary` Mode 4 (Maintain) — add `## Changelog` section and log all terms added/retired to date."
- Stale glossary changelog: "Run `domain-glossary` Mode 4 (Maintain, trigger 1D — scheduled sprint review) for the Core BC."

---

## Check 13 — Orphaned files

**What:** finds markdown files in `docs/` that are not referenced by any other doc.

**Detection:**
```bash
find docs -name "*.md" | while read f; do
  fname=$(basename "$f")
  # Check if any other doc links to this file by filename or relative path
  count=$(grep -rl "$fname" docs/ --include="*.md" 2>/dev/null | grep -v "^$f$" | wc -l)
  [ "$count" -eq 0 ] && echo "ORPHANED: $f"
done
```

**Exclusions (never flag as orphaned):**
- Hub docs: `personas.md`, `capability-map.md`, `value-streams.md`, `epic-catalogue.md`, `quality-attributes.md`, `FBS.md`
- README.md files
- Index files

**Severity:** Info

**Proposed fix template:** "If `{file}` is intentional (e.g., a draft), add a link from the relevant hub doc. If it is obsolete, delete it or move to `docs/archive/`."

---

## Check 14 — Research sync

**What:** finds research synthesis docs that contain "updates needed" sections where the referenced upstream artefact has not been modified since the synthesis was written.

**Detection:**
```bash
# Find synthesis files with update sections
grep -rln 'Per-artefact updates\|updates needed\|artefact.*update' \
  docs/business/research/ 2>/dev/null | while read synth; do
  synth_date=$(git log -1 --format="%ct" -- "$synth" 2>/dev/null)
  # For each upstream artefact mentioned in the synthesis
  grep -oh 'docs/[^)]*\.md' "$synth" | while read upstream; do
    upstream_date=$(git log -1 --format="%ct" -- "$upstream" 2>/dev/null)
    [ -n "$upstream_date" ] && [ "$synth_date" -gt "$upstream_date" ] && \
      echo "UNSYNCED: $synth → $upstream (synthesis newer than artefact)"
  done
done
```

**Severity:** Warning

**Proposed fix template:** "Apply updates proposed in `{synthesis}` to `{upstream_artefact}`. Mark as done by adding a line `<!-- synced: {date} -->` in the synthesis."

---

## Check 15 — ADR supersession chains

**What:** finds one-sided ADR supersession links.

**Detection:**
```bash
find docs/architecture/decisions -name "*.md" 2>/dev/null | while read adr; do
  # Find ADRs this one supersedes
  superseded=$(grep -oh 'ADR-[0-9]\{4\}' "$adr" | sort -u)
  for target_id in $superseded; do
    target=$(find docs/architecture/decisions -name "${target_id}-*.md" 2>/dev/null | head -1)
    if [ -n "$target" ]; then
      # Check target has back-link to this ADR
      this_id=$(basename "$adr" | grep -oh 'ADR-[0-9]\{4\}')
      grep -q "$this_id\|superseded" "$target" || \
        echo "BROKEN CHAIN: $(basename $adr) supersedes $(basename $target) but no back-link"
    fi
  done
done
```

**Severity:** Warning

**Proposed fix template:** "Add `Superseded by: [ADR-{NNNN} {title}]({path})` to §Status in `{adr_file}`."

---

## Check 16 — Delivery progress

**What:** reports FBS functionality status distribution and epic ↔ PRD linkage completeness.

**Detection — FBS status:**
```bash
fbs="docs/product-specs/functional-breakdown-structure/FBS.md"
if [ -f "$fbs" ]; then
  done=$(grep -c '✅' "$fbs" 2>/dev/null || echo 0)
  in_progress=$(grep -c '🔄' "$fbs" 2>/dev/null || echo 0)
  not_started=$(grep -c '⬜' "$fbs" 2>/dev/null || echo 0)
  echo "FBS: ✅ $done / 🔄 $in_progress / ⬜ $not_started"
fi
```

**Detection — epic ↔ PRD linkage:**
```bash
epic_count=$(grep -c '\bE-[0-9]\{2\}\b' docs/product-specs/epic-catalogue.md 2>/dev/null || echo 0)
prd_count=$(find docs/product-specs -maxdepth 1 -name "*_prd_*.md" 2>/dev/null | wc -l)
echo "Epics: $epic_count | PRDs: $prd_count"
# Find epics with no corresponding PRD link
grep -oh '\bE-[0-9]\{2\}\b' docs/product-specs/epic-catalogue.md 2>/dev/null | sort -u | while read epic; do
  grep -rl "$epic" docs/product-specs --include="*_prd_*.md" 2>/dev/null | head -1 || \
    echo "NO PRD for $epic"
done
```

**Detection — domain model completeness:**
```bash
# Domain model completeness
bc_count=$(grep -c 'BC-[0-9][0-9]' docs/domain/bounded-contexts/bounded-contexts.md 2>/dev/null || echo 0)
dm_count=$(find docs/domain -name "domain-model.md" 2>/dev/null | wc -l)
echo "Bounded contexts: $bc_count | Domain models: $dm_count"
[ "$dm_count" -lt "$bc_count" ] && echo "WARNING: $(($bc_count - $dm_count)) BC(s) missing domain model"
```

**Severity:** Info

**Proposed fix template:** "Run `spec-prd` for epic `{E-NN}` to create the missing PRD. Promote FBS rows from ⬜ → 🔄 as the PRD is written."
