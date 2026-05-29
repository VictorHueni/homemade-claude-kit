---
name: com-artefact-viz
description: "Render canonical kit artefacts into single-file, self-contained interactive HTML views via a shared Python pipeline and a token-driven design system. Four pluggable renderers: capability map (L0-grouped cards + directional left-axis band), delivery roadmap (phase-column timeline + walking-skeleton band + expandable per-epic features), functional breakdown structure (collapsible tree with horizontal/vertical toggle + status badges), and Business Model / Lean Canvas (9-block grid). Styling is delegated to the project design system — renderers emit only semantic classes and var() tokens, so one CSS sheet re-themes every view. Use when the user wants a web view, visualisation, board, timeline, canvas, or shareable HTML of a capability map, FBS, delivery roadmap, BMC, or Lean Canvas. Triggers on: visualise capability map, render FBS tree, roadmap timeline view, BMC canvas HTML, artefact visualisation, com-artefact-viz. Do NOT use for slide decks (com-slide-deck) or C4 diagrams (arch-c4)."
version: "1.0.0"
status: active
last_reviewed: 2026-05-29
review_interval: 180d
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "communication"
  complexity: "medium"
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

## Supported artefacts

| Kind (`--kind`) | Source skill | Canonical path | View |
|---|---|---|---|
| `capability-map` | `business-capability-map` | `docs/business/03a-capability-map.md` | L0-grouped capability cards + directional left-axis band; importance colour-coding |
| `fbs` | `spec-functional-breakdown-structure` | `docs/product-specs/07a-fbs.md` | Collapsible tree, horizontal⇄vertical toggle, ✅/🔄/⬜ status badges + counts |
| `delivery-roadmap` | `spec-delivery-roadmap` | `docs/product-specs/08a-delivery-roadmap.md` | Phase-column timeline, walking-skeleton band, pain-coded epic cards with expandable features/stories |
| `bmc` | `business-model-canvas` | `docs/business/02a-bmc.md` / `02a-lean-canvas.md` | Classic 9-block canvas grid (BMC + Lean variants), confidence colour-coding |

It produces **communication artefacts** (the `com-` prefix → `docs/communication/`),
mints no IDs, and is not a step in the strategic-architecture build order — it is
a supporting skill, like `com-slide-deck`.

---

## Quick reference

| Task | Command |
|---|---|
| Render an artefact (auto-detect kind) | `python scripts/render.py docs/business/03a-capability-map.md` |
| Force the kind | `python scripts/render.py SRC.md --kind fbs` |
| Theme with a project design system | `python scripts/render.py SRC.md --design-system docs/communication/slides/{slug}/design/styles.css` |
| Override the capability/FBS left-axis label | `python scripts/render.py SRC.md --left-axis-label "Customer Journey" --left-axis-arrow "→"` |
| Choose the output path | `python scripts/render.py SRC.md --out docs/communication/visualisations/capability-map.html` |
| Just print the detected kind | `python scripts/render.py SRC.md --detect` |
| Live preview while editing | `python scripts/dev_server.py docs/business/03a-capability-map.md` |

Default output: `docs/communication/visualisations/<kind>.html`.

---

## How to run it (operating sequence)

1. **Locate the source artefact.** It must be the canonical Markdown produced
   by the owning skill (see the table above). If the artefact does not exist
   yet, stop and point the user at the skill that builds it — this skill
   visualises, it does not author.
2. **Pick or confirm the design system.** By default the view ships with the
   skill's neutral token set (`templates/design-system.css`). If the project
   has a design system — most commonly the `design/styles.css` of a
   `com-slide-deck` project — pass it with `--design-system`. Its `:root`
   tokens are inlined last and win. This is the supported way to make every
   view match the project's look (the user's "style applied per project design
   system" requirement).
3. **Render.** Run `scripts/render.py`. One self-contained HTML file is written
   (all CSS + JS inlined — no runtime, no network, diff-friendly, shareable).
4. **Verify in a browser.** Open the file. Check the verification list below.
5. **Re-render after the source changes.** Views never drift silently because
   they carry no authored content — re-run the same command.

---

## Templating model (three layers)

The pipeline keeps parsing, structure, and styling independent so each can
evolve alone:

1. **Design tokens** — `templates/design-system.css` defines `:root` custom
   properties (`--accent`, `--surface`, `--differentiator`, `--status-shipped`,
   `--pain-critical`, `--conf-validated`, spacing, radii, fonts). A project
   sheet passed via `--design-system` is inlined after the defaults and wins.
   **Renderers reference only `var(--token)` — never a literal colour, font, or
   radius.** That contract is what makes re-theming a one-file operation.
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
  `## Capability index` table. The **left-axis band** defaults to the declared
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
5. [ ] Project design system, if supplied, visibly themes the view (`--design-system`).
6. [ ] Interactive controls work (FBS orientation + collapse; epic feature disclosure).
7. [ ] Re-rendering after a source edit reflects the change (no stale authored content).

---

## Dependencies

- Python 3.8+ (standard library only — no third-party packages, no Node).

---

## Follow-up work

Planned enhancements, deferred refinements, and decisions for this skill are
tracked as central-only rows in the kit's ledger at
`docs/project-control/open-items/open-items.md` (per `rules/open-items-governance.md`
§9) — not in this folder. This skill resolves `OI-0010` (cross-skill web
visualisations).

## See also

- `references/parsing-contract.md` — exact Markdown each parser reads, field by field.
- `references/viz-discipline.md` — design principles and boundaries (what this skill is NOT).
- `com-slide-deck/SKILL.md` — sibling HTML builder; share its `design/styles.css` via `--design-system`.
- `rules/skill-creation-sync.md` · `rules/artefact-frontmatter.md` · `rules/diagramming-mermaid.md`.
