# Check Catalogue — util-metamodel-audit

For each of the 16 checks: bash detection pattern, interpretation rules, severity, and proposed fix template. Claude reads this file during audit execution to know exactly how to run each check.

---

## Check 1 — Stack progress

**What:** verifies which of the 11 canonical output paths exist.

**Detection:**
```bash
# Run for each step — adapt path per step number
find docs -maxdepth 1 -name "VISION.md" 2>/dev/null                              # Step 0
find docs/business -maxdepth 1 -name "01a-personas.md" 2>/dev/null
find docs -maxdepth 4 \( -name "business-model-canvas.md" -o -name "lean-canvas.md" \) 2>/dev/null
find docs/business -maxdepth 1 -name "03a-capability-map.md" 2>/dev/null
find docs/business -maxdepth 1 -name "04a-value-streams.md" 2>/dev/null
find docs/business -maxdepth 1 -name "04b-objectives.md" 2>/dev/null          # Step 4.5
find docs/business/05a-processes -name "proc-*.md" 2>/dev/null | head -1
find docs/business/06a-models -name "qm-*.md" 2>/dev/null | head -1
find docs/product-specs -maxdepth 1 -name "07a-fbs.md" 2>/dev/null
find docs/product-specs -maxdepth 1 -name "08a-delivery-roadmap.md" 2>/dev/null   # Step 8
find docs/product-specs -maxdepth 1 -name "09a-quality-attributes.md" 2>/dev/null
find docs/product-specs/prds -name "prd-*.md" 2>/dev/null | head -1
find docs/exec-plans/active -maxdepth 1 -name "*_exec_*.md" 2>/dev/null | head -1
find docs/domain -maxdepth 1 -name "02b-bounded-contexts.md" 2>/dev/null           # Step 2b
find docs/domain -maxdepth 1 -name "02c-glossary.md" 2>/dev/null                  # Step 2c
find docs/domain/07b-models -name "*.md" 2>/dev/null | head -1             # Step 7b (per BC)
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
- `01a-personas.md` → must be at `docs/business/01a-personas.md` (flat file)
- `02a-bmc.md` / `02a-lean-canvas.md` → must be at `docs/business/` (flat file)
- `03a-capability-map.md` → must be at `docs/business/03a-capability-map.md` (flat file)
- `04a-value-streams.md` → must be at `docs/business/04a-value-streams.md` (flat file)
- `04b-objectives.md` → must be at `docs/business/04b-objectives.md` (flat file)
- `*-process.md` → must be under `docs/business/05a-processes/`
- `07a-fbs.md` → must be at `docs/product-specs/07a-fbs.md` (flat file)
- `08a-delivery-roadmap.md` → must be at `docs/product-specs/08a-delivery-roadmap.md` (flat file)
- `09a-quality-attributes.md` → must be at `docs/product-specs/09a-quality-attributes.md` (flat file)
- `prd-*.md` → must be under `docs/product-specs/prds/`
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
| `P-NN` | `\bP-[0-9]{2}\b` | `docs/business/01a-personas.md` |
| `C-N.M` or `C1.1` | `\bC[0-9]+\.[0-9]+\b` | `docs/business/03a-capability-map.md` |
| `VS-N` | `\bVS-[0-9]+\b` | `docs/business/04a-value-streams.md` |
| `VS-N.M` | `\bVS-[0-9]+\.[0-9]+\b` | `docs/business/04a-value-streams.md` |
| `C-N.M.FXX` | `\bC-[0-9]+\.[0-9]+\.F[0-9]+\b` | `docs/product-specs/07a-fbs.md` |
| `BC-NN` | `\bBC-[0-9]{2}\b` | `docs/domain/02b-bounded-contexts.md` |
| `BC-NN.GT-NN` | `\bBC-[0-9]{2}\.GT-[0-9]{2}\b` | `docs/domain/02c-glossary.md` |
| `BC-NN.AGG-NN` | `\bBC-[0-9]{2}\.AGG-[0-9]{2}\b` | `docs/domain/07b-models/{bc-slug}.md` |
| `BC-NN.ENT-NN` | `\bBC-[0-9]{2}\.ENT-[0-9]{2}\b` | `docs/domain/07b-models/{bc-slug}.md` |
| `BC-NN.VO-NN` | `\bBC-[0-9]{2}\.VO-[0-9]{2}\b` | `docs/domain/07b-models/{bc-slug}.md` |
| `BC-NN.EVT-NN` | `\bBC-[0-9]{2}\.EVT-[0-9]{2}\b` | `docs/domain/07b-models/{bc-slug}.md` |
| `OBJ-NN` | `\bOBJ-[0-9]{2}\b` | `docs/business/04b-objectives.md` |
| `KR-NN.M` | `\bKR-[0-9]{2}\.[0-9]\b` | `docs/business/04b-objectives.md` |
| `E-NN` | `\bE-[0-9]{2}\b` | `docs/product-specs/08a-delivery-roadmap.md` |
| `QA-[A-Z]{2}[0-9]{2}` | `\bQA-[A-Z]{2}[0-9]{2}\b` | `docs/product-specs/09a-quality-attributes.md` |
| `ADR-NNNN` | `\bADR-[0-9]{4}\b` | `docs/architecture/decisions/` |
| `Research-NNNN` | `\bResearch-[0-9]{4}\b` | `docs/architecture/research/` |
| `CO-NN` | `\bCO-[0-9]{2}\b` | `docs/business/01b-competitive-landscape/` |
| `PRD-NNNN` | `\bPRD-[0-9]{4}\b` | `docs/product-specs/prds/prd-*.md` |
| `CS-N` | `\bCS-[0-9]+\b` | `docs/business/02a-bmc.md` |
| `VP-N` | `\bVP-[0-9]+\b` | `docs/business/02a-bmc.md` |
| `CH-N` | `\bCH-[0-9]+\b` | `docs/business/02a-bmc.md` |
| `CR-N` | `\bCR-[0-9]+\b` | `docs/business/02a-bmc.md` |
| `RS-N` | `\bRS-[0-9]+\b` | `docs/business/02a-bmc.md` |
| `KA-N` | `\bKA-[0-9]+\b` | `docs/business/02a-bmc.md` |
| `KP-N` | `\bKP-[0-9]+\b` | `docs/business/02a-bmc.md` |
| `CT-N` | `\bCT-[0-9]+\b` | `docs/business/02a-bmc.md` |

**Detection (example for P-NN):**
```bash
# Collect all P-NN references across all docs
grep -roh '\bP-[0-9]\{2\}\b' docs/ --include="*.md" | grep -oP 'P-[0-9]{2}' | sort -u > /tmp/p_refs.txt
# Collect all P-NN definitions in personas.md
grep -oh '\bP-[0-9]\{2\}\b' docs/business/01a-personas.md 2>/dev/null | sort -u > /tmp/p_defs.txt
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
grep -oh '\bP-[0-9]\{2\}\b' docs/business/01a-personas.md 2>/dev/null | sort | uniq -d
```

**Detection — malformed format:**
```bash
# Single-digit persona IDs (P-1 instead of P-01)
grep -roh '\bP-[0-9]\b' docs/ --include="*.md"
# Single-digit epic IDs
grep -roh '\bE-[0-9]\b' docs/ --include="*.md"
# QA IDs with wrong format
grep -roh '\bQA-[^A-Z ]' docs/ --include="*.md"
# Research IDs with wrong digit count (must be 4-digit)
grep -roh '\bResearch-[0-9]\{1,3\}\b' docs/ --include="*.md"
# Competitor IDs with wrong digit count (must be 2-digit)
grep -roh '\bCO-[0-9]\b' docs/ --include="*.md"
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
| `docs/business/04a-value-streams.md` | `docs/business/03a-capability-map.md` (stages consume capabilities) |
| `docs/product-specs/07a-fbs.md` | `docs/business/03a-capability-map.md` (FBS inherits L0+L1) |
| `docs/product-specs/08a-delivery-roadmap.md` | `docs/product-specs/07a-fbs.md` (epics group FBS functionalities) |
| `docs/product-specs/09a-quality-attributes.md` | `docs/product-specs/07a-fbs.md` (QA reads FBS differentiators) |
| Any `docs/product-specs/prds/prd-*.md` | `docs/product-specs/08a-delivery-roadmap.md` (PRDs map to E-NN epics) |
| Any `docs/product-specs/prds/prd-*.md` | `docs/product-specs/09a-quality-attributes.md` (PRDs reference QA-XXNN) |
| Any `exec-plans/active/*/` plan | Corresponding `docs/product-specs/prds/prd-*.md` |
| `docs/domain/02c-glossary.md` exists | `docs/domain/02b-bounded-contexts.md` must also exist (glossary is scoped to BCs) |
| `docs/domain/07b-models/{bc-slug}.md` exists | `docs/domain/02b-bounded-contexts.md` must exist (domain model is namespaced by BC) |
| `docs/domain/07b-models/{bc-slug}.md` exists | `docs/domain/02c-glossary.md` must exist (entity names must match glossary terms) |
| `docs/business/04b-objectives.md` exists | `docs/business/04a-value-streams.md` must also exist (objectives consume pain index from VS) |
| Any `docs/product-specs/prds/prd-*.md` | If `docs/business/04b-objectives.md` exists, the PRD should reference ≥1 `OBJ-NN` in §0 |

**Detection (example):**
```bash
[ -f "docs/product-specs/07a-fbs.md" ] && \
  [ ! -f "docs/business/03a-capability-map.md" ] && \
  echo "WARNING: FBS exists but 03a-capability-map.md missing"

[ -f "docs/domain/02c-glossary.md" ] && \
  [ ! -f "docs/domain/02b-bounded-contexts.md" ] && \
  echo "WARNING: Glossary exists but 02b-bounded-contexts.md missing"

find docs/domain/07b-models -name "*.md" 2>/dev/null | while read f; do
  [ ! -f "docs/domain/02b-bounded-contexts.md" ] && \
    echo "WARNING: Domain model exists but 02b-bounded-contexts.md missing: $f"
  [ ! -f "docs/domain/02c-glossary.md" ] && \
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
| `*-process.md` | `## §8 KPIs` or `## KPIs`, `## Open Items` (canonical document-level section per `rules/open-items-governance.md` §1; legacy variants such as the older §11 unresolved-work heading are forbidden), `## §0 Master flow` | `grep -q 'KPI\|§8'` |
| `docs/business/06a-models/*.md` | `§5.2` or `Implicit assumptions`, `§6` or `Scenario Matrix`, `§7` or `Value capture` | `grep -q '5\.2\|Implicit assumptions'` |
| `01a-personas.md` | `## Persona Backlog`, `## Personas`, `## Persona Template` | `grep -q 'Persona Backlog'` |
| `03a-capability-map.md` | `## L0 axis`, `## Global overview`, `## Capability index` | `grep -q 'L0 axis\|Capability index'` |
| `04a-value-streams.md` | `## Catalogue`, `## Value Streams` | `grep -q '## Catalogue'` |
| `07a-fbs.md` | At least one `### C` capability heading with a functionality table | `grep -q '### C[0-9]'` |
| `08a-delivery-roadmap.md` | Epic table with `E-NN` IDs | `grep -q 'E-[0-9][0-9]'` |
| `09a-quality-attributes.md` | ISO characteristic headings (`Performance Efficiency`, `Security`, `Reliability`, etc.) | `grep -q 'Performance Efficiency\|Security\|Reliability'` |
| `docs/product-specs/prds/prd-*.md` | `§0 Architecture Traceability` or traceability block, `## Acceptance criteria` | `grep -q 'Traceability\|Acceptance'` |
| `04b-objectives.md` | At least one `OBJ-NN` heading, `## Changelog`, `## Objective × Epic` section | `grep -q 'OBJ-[0-9][0-9]\|Changelog'` |
| `VISION.md` | `## The Elevator Pitch`, `## What We Are NOT`, `## North Star Metric`, `## Changelog` | `grep -q 'Elevator Pitch\|North Star'` |
| `02b-bounded-contexts.md` | `## Subdomain catalogue`, at least one `BC-NN` entry | `grep -q 'BC-[0-9][0-9]'` |
| `02c-glossary.md` | At least one BC section, `## Changelog` | `grep -q '## Changelog'` |
| `docs/domain/07b-models/{bc-slug}.md` | `## Aggregate catalogue`, `## Domain event catalogue`, Mermaid `classDiagram` | `grep -q 'Aggregate catalogue\|classDiagram'` |
| `docs/architecture/research/*.md` | `## Questions`, `## Findings`, `## Changelog` | `grep -q '## Questions\|## Findings'` |
| `docs/business/01b-competitive-landscape/*.md` | `## Porter Five Forces`, `## Competitor Profiles` or `## CO-` heading | `grep -q 'Five Forces\|CO-[0-9]'` |

**Detection (example for process doc):**
```bash
find docs/business/05a-processes -name "proc-*.md" 2>/dev/null | while read f; do
  grep -q 'KPI\|§8' "$f" || echo "MISSING KPIs: $f"
  grep -q '^## Open Items' "$f" || echo "MISSING canonical Open Items section: $f"
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

**What:** flags artefacts overdue for review based on `last_reviewed` + `review_interval` frontmatter fields, plus proto-persona expiry and glossary changelog discipline.

**Detection — frontmatter staleness (all docs):**
```bash
today=$(date +%s)
find docs -name "*.md" | while read f; do
  last=$(grep "^last_reviewed:" "$f" 2>/dev/null | sed 's/last_reviewed: *//')
  interval=$(grep "^review_interval:" "$f" 2>/dev/null | sed 's/review_interval: *//' | grep -oP '[0-9]+')
  [ -z "$last" ] || [ -z "$interval" ] && continue
  last_ts=$(date -d "$last" +%s 2>/dev/null) || continue
  due=$(( last_ts + interval * 86400 ))
  [ "$today" -gt "$due" ] && \
    echo "OVERDUE ($(( (today - due) / 86400 ))d past): $f (last_reviewed: $last, interval: ${interval}d)"
done | sort
```

**Detection — proto-persona expiry:**
```bash
grep -n 'Next review' docs/business/01a-personas.md 2>/dev/null
# Compare each date against today; proto-personas past next-review are expired assumptions
```

**Detection — glossary changelog discipline:**
```bash
# Glossary exists but has no Changelog section → living-doc discipline missing
if [ -f "docs/domain/02c-glossary.md" ]; then
  grep -q '## Changelog' docs/domain/02c-glossary.md || \
    echo "WARNING: glossary.md missing Changelog section"
  # Changelog exists but last entry is > 30 days ago for Core BC (sprint cadence)
  last_entry=$(grep -m1 '^### [0-9]' docs/domain/02c-glossary.md 2>/dev/null | grep -oP '[0-9]{4}-[0-9]{2}-[0-9]{2}')
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
- Hub docs: `01a-personas.md`, `03a-capability-map.md`, `04a-value-streams.md`, `08a-delivery-roadmap.md`, `09a-quality-attributes.md`, `07a-fbs.md`
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

**What:** finds broken or one-sided ADR supersession links in frontmatter.

ADR supersession is tracked via frontmatter fields only — there is no `## Status` body section. Two checks:
1. When a new ADR has `supersedes: <path>`, the target file must have `status: superseded` and `superseded_by:` pointing back.
2. When an ADR has `status: superseded`, it must have `superseded_by:` pointing to an existing file.

**Detection:**
```bash
find docs/architecture/decisions -name "[0-9]*.md" 2>/dev/null | while read adr; do
  # Check 1: ADR body still contains ## Status section (should have been removed)
  grep -q '^## Status' "$adr" && \
    echo "STALE BODY STATUS: $adr — ## Status section must be removed; use frontmatter status field"

  # Check 2: if supersedes: present, verify target has status: superseded + superseded_by
  supersedes_path=$(grep "^supersedes:" "$adr" 2>/dev/null | sed 's/supersedes: *//')
  if [ -n "$supersedes_path" ]; then
    target=$(find . -path "*/$supersedes_path" -o -name "$(basename $supersedes_path)" 2>/dev/null | head -1)
    if [ -n "$target" ]; then
      grep -q "^status: superseded" "$target" || \
        echo "BROKEN CHAIN: $(basename $adr) supersedes $(basename $target) but target status is not superseded"
      grep -q "^superseded_by:" "$target" || \
        echo "BROKEN CHAIN: $(basename $adr) supersedes $(basename $target) but target missing superseded_by"
    else
      echo "DEAD SUPERSEDES LINK: $(basename $adr) → $supersedes_path (file not found)"
    fi
  fi

  # Check 3: if status: superseded, superseded_by must resolve to an existing file
  if grep -q "^status: superseded" "$adr"; then
    sb_path=$(grep "^superseded_by:" "$adr" 2>/dev/null | sed 's/superseded_by: *//')
    [ -z "$sb_path" ] && echo "MISSING superseded_by: $adr has status: superseded but no superseded_by field"
    [ -n "$sb_path" ] && [ ! -f "$sb_path" ] && \
      echo "DEAD superseded_by LINK: $adr → $sb_path (file not found)"
  fi
done
```

**Severity:** Warning

**Proposed fix template:** "Set `status: superseded` and add `superseded_by: <path>` in frontmatter of `{adr_file}`. Remove any `## Status` body section."

---

## Check 16 — Delivery progress

**What:** reports FBS functionality status distribution and epic ↔ PRD linkage completeness.

**Detection — FBS status:**
```bash
fbs="docs/product-specs/07a-fbs.md"
if [ -f "$fbs" ]; then
  done=$(grep -c '✅' "$fbs" 2>/dev/null || echo 0)
  in_progress=$(grep -c '🔄' "$fbs" 2>/dev/null || echo 0)
  not_started=$(grep -c '⬜' "$fbs" 2>/dev/null || echo 0)
  echo "FBS: ✅ $done / 🔄 $in_progress / ⬜ $not_started"
fi
```

**Detection — epic ↔ PRD linkage:**
```bash
epic_count=$(grep -c '\bE-[0-9]\{2\}\b' docs/product-specs/08a-delivery-roadmap.md 2>/dev/null || echo 0)
prd_count=$(find docs/product-specs/prds -name "prd-*.md" 2>/dev/null | wc -l)
echo "Epics: $epic_count | PRDs: $prd_count"
# Find epics with no corresponding PRD link
grep -oh '\bE-[0-9]\{2\}\b' docs/product-specs/08a-delivery-roadmap.md 2>/dev/null | sort -u | while read epic; do
  grep -rl "$epic" docs/product-specs/prds --include="prd-*.md" 2>/dev/null | head -1 || \
    echo "NO PRD for $epic"
done
```

**Detection — domain model completeness:**
```bash
# Domain model completeness
bc_count=$(grep -c 'BC-[0-9][0-9]' docs/domain/02b-bounded-contexts.md 2>/dev/null || echo 0)
dm_count=$(find docs/domain/07b-models -name "*.md" 2>/dev/null | wc -l)
echo "Bounded contexts: $bc_count | Domain models: $dm_count"
[ "$dm_count" -lt "$bc_count" ] && echo "WARNING: $(($bc_count - $dm_count)) BC(s) missing domain model"
```

**Severity:** Info

**Proposed fix template:** "Run `spec-prd` for epic `{E-NN}` to create the missing PRD. Promote FBS rows from ⬜ → 🔄 as the PRD is written."

---

## Check 17 — Frontmatter validity

**What:** verifies that every `docs/**/*.md` file opens with the standard artefact frontmatter block and that all required fields are present, valid, and consistent.

**Schema (canonical — defined in `rules/artefact-frontmatter.md`):**
- Always present: `title`, `status`, `owner`, `last_reviewed`, `review_interval`
- Conditional: `superseded_by` required when `status: superseded`; `supersedes` present only on documents created to replace another
- Valid `status` values: `draft`, `active`, `superseded`, `deprecated`

**Detection:**
```bash
find docs -name "*.md" | sort | while read f; do
  # 1. Frontmatter block must be present (file must start with ---)
  head -1 "$f" | grep -q '^---' || { echo "MISSING FRONTMATTER: $f"; continue; }

  # 2. All 5 required fields must exist
  for field in title status owner last_reviewed review_interval; do
    grep -q "^${field}:" "$f" || echo "MISSING FIELD '${field}': $f"
  done

  # 3. status must be one of the four allowed values
  status=$(grep "^status:" "$f" | head -1 | sed 's/status: *//')
  case "$status" in
    draft|active|superseded|deprecated) ;;
    *) echo "INVALID STATUS '${status}': $f" ;;
  esac

  # 4. When status: superseded, superseded_by must be present and target must exist
  if [ "$status" = "superseded" ]; then
    sb=$(grep "^superseded_by:" "$f" 2>/dev/null | sed 's/superseded_by: *//')
    [ -z "$sb" ] && echo "MISSING superseded_by (status is superseded): $f"
    [ -n "$sb" ] && [ ! -f "$sb" ] && echo "DEAD superseded_by TARGET '$sb': $f"
  fi

  # 5. When supersedes: present, target must exist and have status: superseded
  sup=$(grep "^supersedes:" "$f" 2>/dev/null | sed 's/supersedes: *//')
  if [ -n "$sup" ]; then
    [ ! -f "$sup" ] && echo "DEAD supersedes TARGET '$sup': $f"
    [ -f "$sup" ] && ! grep -q "^status: superseded" "$sup" && \
      echo "supersedes TARGET NOT SUPERSEDED '$sup': $f"
  fi

  # 6. owner must not be empty or a placeholder
  owner=$(grep "^owner:" "$f" | head -1 | sed 's/owner: *//')
  [ -z "$owner" ] && echo "EMPTY owner: $f"

  # 7. last_reviewed must be a valid YYYY-MM-DD date
  lr=$(grep "^last_reviewed:" "$f" | head -1 | sed 's/last_reviewed: *//')
  echo "$lr" | grep -qP '^\d{4}-\d{2}-\d{2}$' || echo "INVALID last_reviewed '${lr}': $f"
done
```

**Severity:**
- Missing frontmatter block → Error
- Missing required field → Error
- Invalid `status` value → Error
- `superseded` without `superseded_by` → Error
- Dead `superseded_by` or `supersedes` target → Error
- Empty `owner` → Warning
- Invalid `last_reviewed` date format → Warning

**Proposed fix template:**
- Missing block: "Add standard frontmatter to `{file}` using `rules/artefact-frontmatter.md` schema. Run `git config user.name` for owner."
- Missing field: "Add `{field}:` to the frontmatter of `{file}`."
- Invalid status: "Set `status:` in `{file}` to one of: `draft`, `active`, `superseded`, `deprecated`."
- Missing `superseded_by`: "Add `superseded_by: <path-to-replacement>` to `{file}` frontmatter."
- Dead target: "Update `superseded_by` / `supersedes` path in `{file}` — target file no longer exists at `{path}`."

---

## Check 18 — Open items governance

**What:** verifies that every artefact's local `## Open Items` section conforms to
`rules/open-items-governance.md` and that the central ledger at
`project-control/open-items/open-items.md` stays in sync with the artefact rows.

This is the only check category in the catalogue that spans both `docs/` and
`project-control/`. It is **report-only** — findings are surfaced to the operator;
remediation is always done through `util-open-items` (sync, triage, close, archive)
or direct artefact edits. The audit never mutates the ledger or any source artefact.

The check bundles six sub-checks, each with its own detection pattern and severity.
All six run together in Mode 1 (full audit); operators wanting only governance drift
can invoke Mode 5 (open-items governance) when it lands.

### Sub-check 18a — Section compliance

**What:** every artefact that carries unresolved work uses the canonical document-level
`## Open Items` heading. Forbidden variants — listed in §1 of
`rules/open-items-governance.md` — must not appear anywhere in the repo's artefact files.

**Detection:**

```bash
# 1. Forbidden legacy heading variants (must return zero matches)
rg -n '^## Open / TODO$|^## Open TODOs$|^## Open questions remaining$|^## Open questions for next interview$|^## Open questions for next workshop / research wave$|^## 11\. Open TODOs' docs/ business-* arch-* spec-* domain-* ops-* com-* util-* 2>/dev/null

# 2. Non-document-level placement (### subsection forbidden per §1)
rg -n '^### Open Items$' docs/ 2>/dev/null

# 3. Legacy wording in discipline / SKILL docs
rg -n '§Open Issues|Open Issues' docs/ business-* arch-* spec-* domain-* 2>/dev/null
```

**Severity:** Error

**Proposed fix template:** "Rename `{found heading}` in `{file}` line {N} to the canonical
`## Open Items` (document-level). Migration steps in `rules/open-items-governance.md` §1."

### Sub-check 18b — Schema compliance

**What:** tables under `## Open Items` use the canonical column order and column names
from §4 of `rules/open-items-governance.md`. Columns must not be removed or reordered;
additional informational columns are permitted only **after** `Tracker ref`.

**Detection:**

```bash
# Find every ## Open Items section, capture the header row (first line beginning with |
# after the heading), and verify the column sequence.
find docs -name "*.md" -print0 | while IFS= read -r -d '' f; do
  awk '
    /^## Open Items[[:space:]]*$/ { in_section=1; next }
    in_section && /^## / { in_section=0 }
    in_section && /^\|/ {
      print FILENAME ":" NR ":" $0
      exit
    }
  ' "$f"
done | while IFS=':' read -r file line header; do
  echo "$header" | grep -qE '\|[[:space:]]*OI-ID[[:space:]]*\|[[:space:]]*Type[[:space:]]*\|[[:space:]]*Summary[[:space:]]*\|[[:space:]]*Source anchor[[:space:]]*\|[[:space:]]*Source heading[[:space:]]*\|[[:space:]]*Resolution path[[:space:]]*\|[[:space:]]*Priority[[:space:]]*\|[[:space:]]*Status[[:space:]]*\|[[:space:]]*Owner[[:space:]]*\|[[:space:]]*Due / Review date[[:space:]]*\|[[:space:]]*Tracker ref' || \
    echo "SCHEMA NON-COMPLIANT: $file line $line — header is: $header"
done
```

**Severity:** Error

**Proposed fix template:** "Restore canonical column order in `## Open Items` table at
`{file}` line {N}. Canonical order: `OI-ID | Type | Summary | Source anchor | Source
heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref`.
Additional columns are allowed only after `Tracker ref`."

### Sub-check 18c — Source-location provenance

**What:** every row in a local `## Open Items` table has both `Source anchor` and
`Source heading` populated. Rows that genuinely have no in-artefact origin (raised
directly at the central plane) carry the sentinel `_central-only_` in `Source heading`
and an empty `Source anchor` — these are not flagged.

**Detection:**

```bash
# For each ## Open Items table, read the data rows and check columns 4 (Source anchor)
# and 5 (Source heading) are non-blank and not _TBD_.
find docs -name "*.md" -print0 | while IFS= read -r -d '' f; do
  awk -v F="$f" '
    /^## Open Items[[:space:]]*$/ { in_section=1; row=0; next }
    in_section && /^## / { in_section=0 }
    in_section && /^\|/ {
      row++
      if (row <= 2) next   # header + separator
      n = split($0, cols, "|")
      anchor = cols[5]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", anchor)
      heading = cols[6]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", heading)
      oi = cols[2]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", oi)
      if (heading == "_central-only_") next
      if (anchor == "" || anchor == "_TBD_" || heading == "" || heading == "_TBD_") {
        printf "PROVENANCE MISSING: %s row %s (OI=%s anchor=%s heading=%s)\n", F, NR, oi, anchor, heading
      }
    }
  ' "$f"
done
```

**Severity:** Warning

**Proposed fix template:** "Populate `Source anchor` and `Source heading` for row `{OI-ID}`
in `{file}`. The pair is the provenance contract (§4 of `rules/open-items-governance.md`).
Use `_central-only_` in `Source heading` only when the row has no in-artefact origin."

### Sub-check 18d — Tracker sync coverage

**What:** every local row whose `OI-ID` has been promoted to the canonical `OI-NNNN`
format must have a corresponding row in `project-control/open-items/open-items.md`.
Rows still on a pre-sync local ID (e.g. `OI-001`, `OI-002`) are not flagged — they
indicate the artefact has not been synced yet, which is normal between edits.

**Detection:**

```bash
ledger="project-control/open-items/open-items.md"
[ ! -f "$ledger" ] && echo "LEDGER MISSING: $ledger" && exit 0

# Collect every canonical OI-NNNN ID present in the ledger
grep -oh '\bOI-[0-9]\{4\}\b' "$ledger" 2>/dev/null | sort -u > /tmp/oi_ledger.txt

# Collect every canonical OI-NNNN ID referenced in artefact-local Open Items sections
find docs -name "*.md" -print0 | while IFS= read -r -d '' f; do
  awk -v F="$f" '
    /^## Open Items[[:space:]]*$/ { in_section=1; next }
    in_section && /^## / { in_section=0 }
    in_section && /^\|/ {
      if (match($0, /OI-[0-9][0-9][0-9][0-9]/)) {
        printf "%s\t%s\n", substr($0, RSTART, RLENGTH), F
      }
    }
  ' "$f"
done | sort -u > /tmp/oi_local.txt

# Local OI-NNNN IDs that are missing from the ledger → sync drift
cut -f1 /tmp/oi_local.txt | sort -u > /tmp/oi_local_ids.txt
comm -23 /tmp/oi_local_ids.txt /tmp/oi_ledger.txt | while read oi; do
  src=$(grep -P "^${oi}\t" /tmp/oi_local.txt | cut -f2 | head -1)
  echo "SYNC DRIFT: $oi present in $src but missing from $ledger"
done

# Ledger OI-NNNN IDs that have no local row → orphaned ledger entry (or _central-only_)
comm -13 /tmp/oi_local_ids.txt /tmp/oi_ledger.txt | while read oi; do
  is_central=$(grep -P "\|\s*${oi}\s*\|" "$ledger" | grep -c '_central-only_' || true)
  [ "$is_central" -eq 0 ] && echo "ORPHANED LEDGER ROW: $oi in $ledger has no matching local row"
done
```

**Severity:** Warning

**Proposed fix template:**

- Sync drift: "Run `util-open-items` in `sync` mode for `{source artefact}` so the local
  `{OI-NNNN}` row reaches `project-control/open-items/open-items.md`."
- Orphaned ledger row: "Either the source artefact was deleted (close or drop the ledger
  row with `util-open-items` and record the rationale) or the row should be marked
  `_central-only_` in `Source heading` per §5 of `rules/open-items-governance.md`."

### Sub-check 18e — Closure drift

**What:** rows whose `Status` is `closed` or `dropped` must carry a non-`_TBD_`
`Tracker ref`. Closure must be evidenced (§3 of `rules/open-items-governance.md`).

**Detection:**

```bash
ledger="project-control/open-items/open-items.md"

# Closure drift in artefact-local sections
find docs -name "*.md" -print0 | while IFS= read -r -d '' f; do
  awk -v F="$f" '
    /^## Open Items[[:space:]]*$/ { in_section=1; row=0; next }
    in_section && /^## / { in_section=0 }
    in_section && /^\|/ {
      row++
      if (row <= 2) next
      n = split($0, cols, "|")
      oi = cols[2]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", oi)
      status = cols[9]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", status)
      tracker = cols[12]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", tracker)
      if ((status == "closed" || status == "dropped") && (tracker == "" || tracker == "_TBD_")) {
        printf "CLOSURE DRIFT: %s row %s (OI=%s status=%s tracker=%s)\n", F, NR, oi, status, tracker
      }
    }
  ' "$f"
done

# Same check against the central ledger (Source artefact is column 4 there → tracker is column 13)
if [ -f "$ledger" ]; then
  awk -v F="$ledger" '
    /^## Live items[[:space:]]*$/ { in_section=1; row=0; next }
    in_section && /^## / { in_section=0 }
    in_section && /^\|/ {
      row++
      if (row <= 2) next
      n = split($0, cols, "|")
      oi = cols[2]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", oi)
      status = cols[10]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", status)
      tracker = cols[13]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", tracker)
      if ((status == "closed" || status == "dropped") && (tracker == "" || tracker == "_TBD_")) {
        printf "CLOSURE DRIFT: %s row %s (OI=%s status=%s tracker=%s)\n", F, NR, oi, status, tracker
      }
    }
  ' "$ledger"
fi
```

**Severity:** Error

**Proposed fix template:** "Row `{OI-ID}` in `{file}` is `{status}` but `Tracker ref` is
`_TBD_`. Either record the resolving PR / ADR / plan increment / runbook URL via
`util-open-items` in `close` (or `drop`) mode, or re-open the row by setting status back
to `open` / `in-progress` / `blocked`."

### Sub-check 18f — Stale open items (overdue review)

**What:** rows whose `Status` is `open`, `in-progress`, or `blocked` and whose
`Due / Review date` has passed are overdue. This is not auto-closure — operators must
re-triage via `util-open-items`. Surfacing them in the audit is the trigger.

**Detection:**

```bash
today=$(date +%s)
find docs -name "*.md" -print0 | while IFS= read -r -d '' f; do
  awk -v F="$f" -v TODAY="$today" '
    /^## Open Items[[:space:]]*$/ { in_section=1; row=0; next }
    in_section && /^## / { in_section=0 }
    in_section && /^\|/ {
      row++
      if (row <= 2) next
      n = split($0, cols, "|")
      oi = cols[2]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", oi)
      status = cols[9]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", status)
      due = cols[11]; gsub(/^[[:space:]]+|[[:space:]]+$/, "", due)
      if (status != "open" && status != "in-progress" && status != "blocked") next
      if (due == "" || due == "_TBD_") next
      # parse YYYY-MM-DD into epoch via system date
      cmd = "date -d \"" due "\" +%s 2>/dev/null"
      cmd | getline due_ts
      close(cmd)
      if (due_ts == "" || due_ts == 0) next
      if (TODAY > due_ts) {
        overdue_days = int((TODAY - due_ts) / 86400)
        printf "OVERDUE %dd: %s row %s (OI=%s status=%s due=%s)\n", overdue_days, F, NR, oi, status, due
      }
    }
  ' "$f"
done
```

**Severity:** Warning

**Proposed fix template:** "Row `{OI-ID}` in `{file}` is `{status}` and was due
`{due date}` ({overdue days}d ago). Run `util-open-items` in `triage` mode to either
re-date, escalate priority, reassign owner, or close with a `Tracker ref`."

### Summary — Check 18 outputs

| Sub-check | Severity | What it flags |
| :-- | :-- | :-- |
| 18a Section compliance | Error | Forbidden legacy headings; non-document-level `### Open Items` |
| 18b Schema compliance | Error | Missing / reordered canonical columns in `## Open Items` tables |
| 18c Source-location provenance | Warning | Empty / `_TBD_` `Source anchor` or `Source heading` (excludes `_central-only_`) |
| 18d Tracker sync coverage | Warning | Canonical `OI-NNNN` IDs out of sync between local sections and the central ledger |
| 18e Closure drift | Error | `closed` / `dropped` rows without an evidencing `Tracker ref` |
| 18f Stale open items | Warning | `open` / `in-progress` / `blocked` rows past `Due / Review date` |

All six sub-checks are read-only; none of them write to `project-control/open-items/` or
to any source artefact. Findings always route to the operator for action through
`util-open-items`.
