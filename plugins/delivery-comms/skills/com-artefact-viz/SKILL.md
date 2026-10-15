---
name: com-artefact-viz
license: MIT
description: "Render canonical kit artefacts into single-file, self-contained interactive HTML views via a shared Python pipeline, themed by the project's resolved design system and checked by a blocking validator. Five pluggable renderers: capability map, delivery roadmap timeline (walking-skeleton band + per-epic features), FBS collapsible tree, Business Model / Lean Canvas grid, and service blueprint (swimlane composition over process + value-stream + persona docs, with the line of visibility and pain overlays). Use when the user wants a web view, visualisation, board, timeline, canvas, swimlane, or shareable HTML of a capability map, FBS, delivery roadmap, BMC, Lean Canvas, or service blueprint. Triggers on: visualise capability map, render FBS tree, roadmap timeline view, BMC canvas HTML, service blueprint, swimlane view, line of visibility, artefact visualisation, com-artefact-viz. Do NOT use for slide decks (com-slide-deck) or C4 diagrams (arch-c4)."
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/render.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/dev_server.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/shared/design_source.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/shared/check_render.py *)
user-invocable: true
metadata:
  category: "communication"
  complexity: "medium"
  version: "2.0.0"
  status: active
  last_reviewed: 2026-10-14
  review_interval: 180d
  impact: "low"
---

# com-artefact-viz — Artefact Web Visualiser

Turn the kit's canonical Markdown artefacts into single-file, self-contained
interactive HTML views. The source Markdown stays the single source of truth;
each view is a **derived, regenerable read-out** — never a second place to edit
content.

This skill is a **portable toolkit**: it lives in its own versioned folder and
generates output into a project's `docs/communication/visualisations/`. It
never contains project-specific content.

```
Markdown artefact ──(parser)──> normalized model ──(renderer)──> one HTML file
   (source of truth)              scripts/parsers      scripts/renderers
```

## Running the scripts

- `<skill-dir>` in every command below is the absolute path on the "Base directory for this skill" line at the top of this skill. Write it out in full: no shell variable, no `cd`.
- **One plain command per Bash call**, starting with `python3`. No `&&`, `;`, pipes, redirections or `$VAR`: restricted sessions (only `python3`, `mkdir` and `cp` allowed) deny compound commands. Paths are relative to the working directory; when the user says they work in a subfolder, keep the working directory and write the paths from it (`docs/strategy/capability-map.md`).
- Look at files with Read, Glob and Grep, never `ls`, `cat` or `head`; write files with the Write tool.
- **If a command is denied, or `render.py` refuses** (exit 1 or 2): stop and report the command, its message, and what the owner must do. Never hand-write the view's HTML or CSS instead.

## Supported artefacts

| Kind (`--kind`) | Source skill | Canonical path | View |
|---|---|---|---|
| `capability-map` | `business-capability-map` | `docs/business/03a-capability-map.md` | L0-grouped capability cards + directional left-axis band; importance colour-coding |
| `fbs` | `spec-functional-breakdown-structure` | `docs/product-specs/07a-fbs.md` | Collapsible tree, horizontal⇄vertical toggle, ✅/🔄/⬜ status badges + counts |
| `delivery-roadmap` | `plan-delivery-roadmap` | `docs/plans/delivery-roadmap.md` | Phase-column timeline, walking-skeleton band, pain-coded epic cards with expandable features/stories |
| `bmc` | `business-model-canvas` | `docs/business/02a-bmc.md` / `02a-lean-canvas.md` | Classic 9-block canvas grid (BMC + Lean variants), confidence colour-coding |
| `service-blueprint` | `business-process` + `business-value-stream` + `business-persona` *(composition)* | `docs/communication/visualisations/service-blueprint.html` | Swimlane grid (evidence · customer · frontstage · backstage · systems) with the **line of visibility**, value-stream phase columns, pain overlays, and a cross-actor handoff spine |

It produces **communication artefacts** (the `com-` prefix → `docs/communication/`),
mints no IDs, and is not a step in the strategic-architecture build order — it is
a supporting skill, like `com-slide-deck`.

### Service blueprint — a composition lens (multi-source)

Four of the kinds render **one** source file. `service-blueprint` is different:
it **composes several** canonical artefacts into the one cross-process,
customer-visibility view none of them gives alone — and it restates nothing.
It reads the `business-process` doc(s) for actors, systems, steps, handoffs and
pain points; drapes them under `business-value-stream` phase columns; and
**derives the only thing no source carries — the line of visibility — from
`business-persona` type** (a `Customer`/`Served` persona → customer lane; other
resolved actors → front- or back-stage by whether they exchange a data object
with the customer; system-named actors → systems lane). Actors it cannot
classify are surfaced in an **Unclassified** band with a badge — never guessed.
Because the classification is derived, **it changes no source doc**; to move an
unclassified actor, set its `Persona type` in the persona doc and re-render.

Invoke it with `--proc` (repeatable), an optional `--value-stream`, and
`--personas` (a file or a folder):

```bash
python3 <skill-dir>/scripts/render.py --kind service-blueprint --proc docs/business/05a-processes/proc-03-slot-rebooking.md --value-stream docs/business/04a-value-stream.md --personas docs/business/03b-personas/
```

Without `--value-stream`, phase columns fall back to the §6 step order. A
worked multi-file fixture lives in `examples/service-blueprint/`.

---

## Quick reference

| Task | Command |
|---|---|
| Check which design a render will use | `python3 <skill-dir>/scripts/shared/design_source.py provenance` |
| Render an artefact (auto-detect kind) | `python3 <skill-dir>/scripts/render.py docs/business/03a-capability-map.md` |
| Force the kind | `python3 <skill-dir>/scripts/render.py SRC.md --kind fbs` |
| Compose a service blueprint | `python3 <skill-dir>/scripts/render.py --kind service-blueprint --proc PROC.md --value-stream VS.md --personas PERSONAS/` |
| Choose the output path | `python3 <skill-dir>/scripts/render.py SRC.md --out docs/strategy/capability-map.html` |
| Record the verdict (after every render) | `python3 <skill-dir>/scripts/shared/check_render.py --record OUT.html.verdict.txt OUT.html` |
| Theme with a specific design system | `python3 <skill-dir>/scripts/render.py SRC.md --design-system path/to/design-system/` (a folder with a `kit-manifest.json`; a single stylesheet is refused) |
| Declare a local exception | `python3 <skill-dir>/scripts/render.py SRC.md --exception NAME=VALUE` (`--exception=--name=value` when the name starts with `--`) |
| Override the capability/FBS left-axis label | `python3 <skill-dir>/scripts/render.py SRC.md --left-axis-label "Customer Journey" --left-axis-arrow "→"` |
| Just print the detected kind | `python3 <skill-dir>/scripts/render.py SRC.md --detect` |
| Live preview while editing | `python3 <skill-dir>/scripts/dev_server.py docs/business/03a-capability-map.md` |

Default output: `docs/communication/visualisations/<kind>.html`.

---

## How to run it (operating sequence)

1. **Locate the source artefact.** It must be the canonical Markdown produced
   by the owning skill (see the table above). If the artefact does not exist
   yet, stop and point the user at the skill that builds it — this skill
   visualises, it does not author.
2. **Check the design**: `python3 <skill-dir>/scripts/shared/design_source.py provenance`. Exit 0 names the design and the source of each module; exit 2 is a refusal (see **Design, validator, provenance and verdict**).
3. **Render** with `render.py`, `--out` set to the path the user asked for. One self-contained HTML file is written (all CSS and JS inlined, no runtime, no network), with `<out>.provenance.json` beside it.
4. **Record the verdict**: `python3 <skill-dir>/scripts/shared/check_render.py --record <out>.verdict.txt <out>`, and report its first line. The view is not done without `PASS`.
5. **Re-render after the source changes.** Views never drift silently because
   they carry no authored content — re-run the same command.

---

## Design, validator, provenance and verdict

The design contract (modules, manifest, contrast pairs, fonts) is [`contract/README.md`](../../contract/README.md). What a view needs from it:

1. **Resolution order**, once per render: `--design-system DIR` (a design-system folder with a `kit-manifest.json`), else the `docs/ux/package.json` pin found by walking up from the **working directory** (not from the source file), else the kit's neutral base theme. A pin names a package at an exact version (downloaded once, integrity-checked, cached per machine) or a local folder (`file:design-system`). The view inlines the font faces and the `core`, `dataviz`, `type` and `space-shape` modules in one `<style data-design-layer>`.
2. **Blocking validator**: the HTML is checked before anything is written. Refused: a literal colour outside the design layer, a custom property outside the contract's roles and the reserved `--kit-*` prefix, a contrast pair an exception brings below WCAG AA. Exit `0` written; `1` findings, neither the view nor the provenance file written, each finding naming the value, its location and the role to use; `2` the design was refused.
3. **Exceptions**: a deliberate local value the owner asked for, `--exception NAME=VALUE` (repeatable; `--exception=--name=value` for a name starting with `--`), listed in the provenance report. Never add one to get past a finding.
4. **Provenance**: every render prints and writes `<out>.provenance.json`: the design's name, version and repo-relative path, the source (`design-system` or `base`) of every module, the inlined modules, the exceptions and warnings.
5. **Verdict**: `check_render.py --record <out>.verdict.txt <out>` writes `PASS: no findings` or `FAIL: …`, the file, the design and the findings.
6. **Reproducible output**: the same sources and the same design give byte-identical HTML from any folder and at any time. The footer names each source by its repo-relative path (its name alone outside a repository) and the date comes from the sources: `SOURCE_DATE_EPOCH` when set, else the sources' last commit, else their newest modification time.
7. **Legacy design file**: a `docs/ux/tokens.css` (or `docs/design/tokens.css`) with no pin is refused with exit 2 and a message naming `ux-design-system point`, `subset` and `subset --from-legacy`. Invoke the `ux-design-system` skill, run its `subset --from-legacy`, show the owner the drafted `docs/ux/DESIGN.md` and its proposed chart colours, and stop. Never edit or delete the legacy file, never remove the `proposed:` line yourself, and never hand-write a stylesheet in place of the refused design.

---

## Templating model (three layers)

The pipeline keeps parsing, structure, and styling independent so each can
evolve alone:

1. **Design layer and domain colours**: the resolved design (`core`, `dataviz`, `type`, `space-shape`) is inlined first, in `<style data-design-layer>`; `templates/tokens.domain.css` then maps each domain colour to a renderer-owned `--kit-*` property declared as exactly `var(<role>)`. By meaning: status (shipped, planned, backlog) on `--success`, `--info`, `--muted`; pain (critical, high, medium, low) on `--danger`, `--warning`, `--info`, `--muted`; importance (differentiator, necessary, commodity) and confidence (validated, tested, assumed) on the ordered chart scale `--chart-1` to `--chart-3`, darkest first. Text on a fill uses `var(--kit-on-<fill>)`. **Renderers reference only contract roles and `--kit-*` properties, never a literal colour, font or radius**, so the project design re-themes every view. Bold text uses `--font-weight-bold` and pill badges `--radius-pill`.
   UI chrome (view title, group/card headings, badges, toolbar buttons) uses
   `--font-heading`, which is deliberately **not** derived from `--font-body`:
   a design that themes `--font-body` with a serif reading face keeps sans
   headings and badges unless it sets `--font-heading` too.
2. **Base layout** — `templates/base.html.tmpl` is the shell with slots
   (`{{TITLE}}`, `{{KIND}}`, `{{META}}`, `{{TOOLBAR}}`, `{{CONTENT}}`,
   `{{DESIGN_SYSTEM_CSS}}`, `{{VIEW_CSS}}`, `{{RUNTIME_JS}}`, `{{FOOTER}}`).
   Everything is inlined into the slots → one portable file per view.
3. **Pluggable renderers** — `scripts/renderers.py` has one function per kind
   that turns a model dict into the content fragment + view-scoped CSS +
   toolbar. The **parser layer** (`scripts/parsers.py`) turns canonical
   Markdown into that model. When a source skill's output template changes,
   only the matching parser changes; renderers and templates stay put.

To add a new artefact type later: add a `parse_*` to `parsers.py` (register it
in `PARSERS` + `detect_kind`), add a `render_*` to `renderers.py` (register it
in `RENDERERS`), and add a `.sample.md` fixture under `examples/`. No template
or design-system change is needed.

---

## Behaviour notes per renderer

- **Capability map.** Hierarchy comes from the artefact's `## Global overview`
  ASCII tree (nesting derived from the `C-N.M` ID depth, robust to indentation).
  Strategic importance + one-line definitions are joined in from the
  `## Capability index` table. Capability cards are **collapsed by default** —
  the grid reads as a compact taxonomy; clicking a card head (or Enter/Space —
  heads are keyboard-focusable) discloses its definition and children, and the
  toolbar's expand-all / collapse-all drives every card at once. The
  **left-axis band** defaults to the declared
  L0 axis and is overridable per project via `--left-axis-label` /
  `--left-axis-arrow` (the "arrow text varies by project" requirement).
- **FBS.** Same overview tree, with functionalities attached from each
  capability's table; status maps ✅→shipped, 🔄→planned, ⬜→backlog. The
  toolbar toggles orientation (vertical⇄horizontal), expand-all, collapse-all;
  individual nodes collapse on click.
- **Delivery roadmap.** Phases become timeline columns; epics are bucketed by
  their `Phase` column (falling back to the phase-plan epic list). Epic cards
  carry a pain-coded left stripe and an expandable list of FBS scope rows
  (features/stories). The walking-skeleton band shows hypothesis + can/cannot.
- **BMC / Lean Canvas.** Blocks are placed into the classic canvas grid via
  `grid-template-areas`, with separate layouts for BMC and Lean variants; the
  alternate variant's blocks are dropped. Confidence (Assumed/Tested/Validated)
  is colour-coded. The grid collapses to two columns on narrow viewports.

---

## Verification checklist

1. [ ] Source artefact is the canonical Markdown for its kind (right path/skill).
2. [ ] `--detect` (or auto-detect) resolves the intended kind.
3. [ ] Output opens in a browser with no console errors and no missing styles.
4. [ ] Every expected element is present (groups/nodes/phases/blocks — compare to source).
5. [ ] The provenance names the intended design (the pin, a `--design-system` folder, or the base theme on purpose), and the design visibly themes the view.
6. [ ] `check_render.py --record <out>.verdict.txt <out>` reads `PASS: no findings`; report it.
7. [ ] Interactive controls work (FBS orientation + collapse; epic feature disclosure; capability-card disclosure + expand/collapse-all).
8. [ ] Re-rendering after a source edit reflects the change (no stale authored content).
9. [ ] *(service-blueprint)* `--proc` resolves; ≥1 customer and ≥1 frontstage/backstage lane; the three control lines sit between the right bands; any **Unclassified** actor is one whose `Persona type` is missing in the source persona doc (fix there, not in the view); phase columns match the value stream (or note the §6 fallback); handoff spine lists the cross-actor data objects.

---

## Dependencies

- Python 3.12 or later, standard library only (no third-party packages, no Node).

---

## Follow-up work

Planned enhancements, deferred refinements, and decisions for this skill are
tracked as central-only rows in the kit's ledger at
`docs/project-control/open-items/open-items.md` (per the `metamodel` skill's `references/open-items-governance.md`
§9) — not in this folder. This skill resolves `OI-0010` (cross-skill web
visualisations).

## See also

- `references/parsing-contract.md` — exact Markdown each parser reads, field by field.
- `references/viz-discipline.md` — design principles and boundaries (what this skill is NOT).
- [`contract/README.md`](../../contract/README.md): the design contract (modules, manifest, contrast pairs).
- `ux-design-system/SKILL.md`: gives the project its design (`point`, `subset`, `subset --from-legacy`); the renderers find its `docs/ux/package.json` pin.
- `com-slide-deck/SKILL.md`: sibling HTML builder, themed by the same resolved design.
- `rules/skill-creation-sync.md` · the `metamodel` skill's `references/artefact-frontmatter.md` · `rules/diagramming-mermaid.md`.
