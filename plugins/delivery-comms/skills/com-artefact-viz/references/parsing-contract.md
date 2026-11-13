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

## delivery-roadmap — `plan-delivery-roadmap`

Source: `docs/plans/delivery-roadmap.md`

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

## service-blueprint — composition lens (multi-source)

Unlike every parser above, this one reads **several** files and composes them.
It is invoked through `render.py` flags, not a single positional source:
`--proc FILE` (repeatable), `--value-stream FILE` (optional), `--personas PATH`
(file or directory, repeatable), `--stream VS-N` (optional column filter). It
restates nothing — it reads the process docs and derives the rest.

| Element | Read / derived from |
|---|---|
| Lanes (actors) | Union of each `business-process` **§3 Actors** first column and the **§6** `### N.M {Actor}'s flow` sub-headings. |
| Lane steps | The numbered list inside each **§6** actor sub-section (`N. **Step** — …`). |
| Systems lane | **§4 Data Stores** first column, plus any actor whose name reads as a system (`system`/`platform`/`service`/`api`/`engine`/`automation`/`portal`/`registry`/`database`/`store`). |
| Handoff spine ("the dance") | **§5 Data Objects** `Created by` → `Consumed by` pairs; each becomes one cross-actor connector chip. |
| Evidence band | §5 Data Objects whose `Created by` **or** `Consumed by` is a customer-lane actor (the customer-perceived touchpoints). |
| Fail / pain flags | **§9 What's broken today** — an actor named in the `Who experiences it` cell gets a ⚠ pain badge. |
| Phase columns | `business-value-stream` `#### VS-N.M · Stage` headings (filtered by `--stream`), with the stage `Pain point index` tinting the header. **Fallback** when no `--value-stream`: ordinal `Step 1…N` columns from §6 step order. |
| **Line of visibility (derived)** | `business-persona` **`Persona type`**: a `Customer`/`Served` persona → **customer** lane; `Negative` → dropped; any other resolved actor → **frontstage** if it exchanges a §5 data object with a customer-lane actor, else **backstage**; an actor that resolves to no persona type → **unclassified** (badged, never guessed). |

Step→column placement is deterministic, never keyword-guessed: with value-stream
columns, step *i* of *n* maps to column `min(N-1, i*N // n)`; with the ordinal
fallback, step *i* maps to column *i*. Persona resolution is token overlap on
the persona's name + role against the actor name; ties resolve to the highest
overlap, none → unclassified.

A worked multi-file fixture is in `examples/service-blueprint/` (process +
personas + value stream).

---

## slice-design — a slice folder

Not one Markdown file: a folder, read by `parse_slice_design(folder)`.

```text
<slice folder>/
├── README.md                      frontmatter: title (required), description (the lead), eyebrow
├── header.html                    optional: the labels under the lead
├── footer.html                    optional: the paragraphs of the foot
├── screens.html                   one HTML partial per tab, each optional
├── api.html
├── code.html
├── database.html
├── openapi.json | openapi.yaml    needed only when a partial has the OpenAPI slot
└── views/<name>.svg, views/dark/<name>.svg    the rendered diagrams a partial shows
```

| What | Read from | Rule |
|---|---|---|
| Title, lead, line above the title | `README.md` frontmatter `title`, `description`, `eyebrow` | Scalar `key: value` lines, quotes removed. No `title` stops the render; `--title` overrides it. Without `eyebrow` the line reads "Slice design sheet". |
| Labels under the lead | `header.html` | Optional. Typically a `<div class="meta">` of chips (the specification the sheet follows, its date) and a `<div class="stories">` of reference chips. No slot. |
| Foot | `footer.html` | Optional paragraphs (the sources, the sheet's authority), placed before the generated line. No slot. |
| Tab content | `screens.html`, `api.html`, `code.html`, `database.html` | The inner HTML of one tab. A missing file, or one that is empty once its summary is removed, is a layer the slice does not touch: the tab says so. |
| Tab summary | A first-line comment `<!-- summary: ... -->` in the partial | Shown on the tab. Optional. |
| Figure | The slot `{{FIGURE:name|alt|caption}}` | `name` is the stem of a diagram (lower case, digits, hyphens). Both `views/<name>.svg` and `views/dark/<name>.svg` must exist; either missing stops the render naming the file. `alt` is plain text; `caption` is optional HTML. |
| OpenAPI viewer | The slot `{{OPENAPI}}` | Renders `openapi.json`; `openapi.yaml` or `.yml` when PyYAML is importable, else a refusal naming both remedies. No document stops the render. |

Any other `{{...}}` in a partial stops the render naming it. The slots are expanded by the renderer; the diagrams are inlined as data URIs, so the page stays one file.

**Classes a partial may use.** The partial holds content only: no `<style>`, no `<script>`, no literal colour (the validator refuses one, as in every view).

| Class | On | Effect |
|---|---|---|
| `block` | a `<div>` wrapping one heading and what follows it | A section of the tab |
| `note` | a `<p>` | Secondary text under a heading |
| `scroll` | a `<div>` around a `<table>` | The table's frame; the table becomes cards on a phone |
| `key`, `num`, `quiet`, `nw` | a `<td>` | An identifier, a right-aligned number, a muted cell, a cell that does not wrap |
| `chip`, with `ref`, `solid` or `open` | a `<span>` | A label: a reference, a filled label, a dashed "open" label |
| `meta`, `stories` | a `<div>` of chips in `header.html` | A row of labels, a row of story references |
| `mono` | any inline element | Monospace |
| `decisions` | a `<div>` holding two `<section>`s, the second with class `open` | The block that closes a tab: what is settled, and what is left to the implementation. Each `<section>` is a chip then a `<ul>`; a `<span class="refs">` in an `<li>` holds reference chips. |
| `msgs`, `msg` | a `<div>` grid and its items | Messages or examples side by side, each a heading and a `<pre>` |
| `empty` | a `<div>` | A dashed frame for something deliberately absent |

A fixture lives in `examples/slice-design/`.

---

## Adding a new artefact type

1. Add `parse_<kind>(text) -> model` to `scripts/parsers.py`; register it in
   `PARSERS` and add a detection rule in `detect_kind`.
2. Add `render_<kind>(model, options)` to `scripts/renderers.py`; register it
   in `RENDERERS`. Style with contract roles and `--kit-*` properties only (no literal colour).
3. Add an `examples/<kind>.sample.md` fixture and dry-run
   `python3 scripts/render.py examples/<kind>.sample.md`.
