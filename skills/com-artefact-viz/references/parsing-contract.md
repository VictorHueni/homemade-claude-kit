# Parsing contract — what each parser reads

This is the precise contract between `com-artefact-viz` parsers
(`scripts/parsers.py`) and the canonical Markdown each source skill emits. If a
source skill changes its output template, update the matching parser here — the
renderers and HTML templates do not change.

All parsers first strip a leading YAML frontmatter block and take the document
title from the first level-1 (`# `) heading. Values matching `_TODO_`, `_TBD_`,
`[bracketed]`, or `{{templated}}` are treated as empty.

---

## capability-map — `business-capability-map`

Source: `docs/business/03a-capability-map.md`

| Field | Read from |
|---|---|
| Left-axis label | `**Chosen axis:** <text>` under `## L0 axis declaration` (overridable by `--left-axis-label`) |
| Hierarchy | The fenced ASCII block under `## Global overview`. Each line containing a `C-N.M` ID becomes a node; **nesting is derived from the ID's dot-depth**, not indentation. Label = text after the ID, minus a leading `· ` separator. |
| Strategic importance | `## Capability index` table, column matching `importance`. Only a single clean keyword (`differentiator`/`necessary`/`commodity`) is taken; placeholder `_Differentiator / Necessary / Commodity_` is ignored. |
| One-line definition | `## Capability index` table, column matching `definition`. |

---

## fbs — `spec-functional-breakdown-structure`

Source: `docs/product-specs/07a-fbs.md`

| Field | Read from |
|---|---|
| Left-axis label | `**Chosen axis:** <text> *(inherited from BC Map)*` (the `*(inherited…)*` note is stripped). |
| Capability hierarchy | `## Global overview` ASCII block (same ID-depth nesting as the capability map). The trailing `(functionalities: …)` count annotation is stripped from labels. |
| Functionalities | Every per-capability table whose headers include `ID` and a `Functionality` column. Rows with a `C-N.M.FXX` ID are grouped under their capability (`C-N.M`). |
| Status | `Status` column; ✅→`shipped`, 🔄→`planned`, ⬜→`backlog` (default `backlog`). |
| VS stage | `VS stage` column (optional). |

---

## delivery-roadmap — `spec-delivery-roadmap`

Source: `docs/product-specs/08a-delivery-roadmap.md`

| Field | Read from |
|---|---|
| Walking skeleton | `## Walking Skeleton — MVP`: `**Hypothesis to validate:**`, `**Value stream delivered end-to-end:**`, and the `can:` / `cannot yet:` bullet lists. |
| Phases | `## Phase Plan` table: columns `Phase`, `Epics`, `Value streams … operational`, `Goal`. |
| Epics | `## Epic Table`: columns `ID` (`E-NN`), `Epic name`, `VS anchor`, `Pain`, `Personas`, `Capabilities`, `Phase`, `PRD`, `Status`. |
| Per-epic value statement + FBS scope | `### E-NN` sections under `## Epics`: `**Value statement:**` and the FBS-scope table (rows with `C-N.M.FXX`). These become the expandable "features" list on each epic card. |
| Phase bucketing | Each epic is placed in the column matching its `Phase` value (`MVP`, `Phase N`); fallback is the epic IDs named in the phase-plan `Epics` cell; final fallback is the first phase. |
| Pain colour | `Pain` value → `critical`/`high`/`medium`/`low` stripe. |

---

## bmc — `business-model-canvas`

Source: `docs/business/02a-bmc.md` or `docs/business/02a-lean-canvas.md`

| Field | Read from |
|---|---|
| Variant | `**Variant chosen:** <BMC \| Lean Canvas>` (or the title). Decides which grid layout + which blocks are kept. |
| Blocks | `### N · Name` / `### N' · Name` headings before `## Value Proposition Deep-dives` / `## Inter-block` / `# VPC Companion`. The number/prime is the block key. |
| Bullets | `-`/`*` list items under each block (placeholders skipped). |
| Confidence | `**Confidence:** <Assumed \| Tested \| Validated>` → colour-coded. |
| Grid placement | Block key → `grid-area` via `BMC_AREAS` / `LEAN_AREAS` in `renderers.py`. Blocks with no area for the chosen variant are dropped (this removes the alternate variant's blocks). |

---

## Adding a new artefact type

1. Add `parse_<kind>(text) -> model` to `scripts/parsers.py`; register it in
   `PARSERS` and add a detection rule in `detect_kind`.
2. Add `render_<kind>(model, options)` to `scripts/renderers.py`; register it
   in `RENDERERS`. Emit only `var(--token)` styling.
3. Add an `examples/<kind>.sample.md` fixture and dry-run
   `python scripts/render.py examples/<kind>.sample.md`.
