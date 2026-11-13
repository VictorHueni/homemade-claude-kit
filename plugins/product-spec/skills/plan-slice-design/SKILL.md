---
name: plan-slice-design
license: MIT
description: "Build a Slice Design Sheet: the architectural view of one vertical slice, read before its plan or tickets are cut. One folder per slice under docs/plans/active/, holding the sources of a tabbed page in four layers from the outside in (screens, API and contracts, code organisation, database), each tab closed by its decisions: settled, and left to the implementation. Modes: scaffold (the slice folder and its four layers, written from the specification), render (diagrams through arch-uml, the page through com-artefact-viz, the verdict recorded), publish (a private page, republished at the same address). Mints no ID; the sheet is cited by its path. Triggers on: slice design sheet, slice design, design sheet for this slice, architectural view of a slice. NOT for the specification itself (spec-prd), the order of work (plan-implementation), drawing a diagram on its own (arch-uml), rendering another artefact (com-artefact-viz), or lasting architecture documents (arch-arc42, arch-c4, arch-adr)."
user-invocable: true
metadata:
  category: "planning"
  complexity: "medium"
  version: "1.0.0"
  status: active
  last_reviewed: 2026-11-13
  review_interval: 180d
  impact: "low"
---

# Slice Design Sheet

A Slice Design Sheet shows how one vertical slice is built, in four layers from the outside in, on one page a product owner can read before the work is cut. This skill writes the sources of that page into the slice's folder. It does not draw the diagrams (`arch-uml` does) and it does not build the page (`com-artefact-viz` does); it calls both by name.

## Where a sheet stands

The order for one slice is fixed:

1. **The specification** of the slice: a PRD, or the stories of one that the slice delivers.
2. **The sheet**, written from that specification.
3. **The plan or the tickets**, which cite the sheet by the path of its folder.

**Authority.** The sheet follows the specification. Where the two differ, the specification decides and the sheet is corrected; never the reverse. A gap found in the specification while writing the sheet is raised with the owner and settled in the specification first.

A sheet is a specification of intended design, so it can diverge from the code once the slice is built. It does not replace the architecture documents: a decision that outlives the slice is recorded by `arch-adr` and cited from the sheet.

## The artefact

| | |
|---|---|
| Type | `Slice Design Sheet` (registry key `slice_design`) |
| ID | None. Cite the sheet by its path. |
| Path | `docs/plans/active/<slice-slug>/`, one folder per slice; `README.md` in it carries the artefact frontmatter |
| Page | Built into `<folder>/out/<slice-slug>.html`, with its verdict beside it; both ignored by git |

`<slice-slug>` is kebab-case and says what the slice delivers (`rebook-a-slot`), never a bare number.

The four tabs, in order:

| Tab | File | Holds |
|---|---|---|
| Screens | `screens.html` | Mock-ups of the screens the slice adds or changes |
| API and contracts | `api.html` | Operations and contracts, the OpenAPI viewer, result shapes, decision tables |
| Code organisation | `code.html` | What each module gains, a class diagram, the sequence of one run, how it is tested |
| Database | `database.html` | An entity-relationship diagram, the tables, the column conventions |

Each tab ends with the decisions of its layer: settled, and left to the implementation. What belongs in each tab, what does not, and how the closing block is written: `references/tab-guide.md`. Read it before writing a tab.

## Mode: scaffold

Creates the slice folder and writes its four layers from the specification.

1. **Read first.** The specification of the slice, in full. Then, where present: the ADRs it cites, the interface contract (`docs/architecture/interfaces/`), the domain model (`docs/domain/`), the quality attributes, and the architecture documents (`docs/architecture/`). If no specification exists for the slice, stop and say so: a sheet is not written from a conversation.
2. **Choose the folder.** `docs/plans/active/<slice-slug>/`; create `docs/plans/active/` when the project does not have it yet. If the folder already holds a `README.md`, do not scaffold over it: go on from step 5 with what is there.
3. **Set up the diagram pipeline** in the folder: follow the `arch-plantuml` skill, `init docs/plans/active/<slice-slug>`. It writes `render.sh`, `_theme.puml`, `_palette.puml`, an example diagram and a `README.md`, and takes the palette from the project's design system when one is pinned. If that skill is not installed, skip this step and say in the closing report that the sheet has no diagrams.
4. **Lay the templates.** Copy every file of this skill's `templates/` into the folder, `gitignore` as `.gitignore`. The sheet's `README.md` replaces the one the pipeline wrote; it keeps the render commands. Fill the `{{...}}` fields of `README.md`: `slice_title`, `eyebrow` (the product or component, then "slice design sheet"), `lead` (one or two sentences: what the slice delivers and how much it touches), `specification` (a link to it), `slice_slug`, `owner` (`git config user.name`), `date`, `timestamp`. The frontmatter is the artefact frontmatter of the `metamodel` skill (`references/artefact-frontmatter.md`) plus `eyebrow`; the README carries it because it is the sheet's own file, not a navigation aid.
5. **Write the layers**, one tab at a time, from the outside in, following `references/tab-guide.md`. Replace every `_TODO_`. A layer the slice does not touch keeps only its summary line: leave it empty on purpose, do not fill it for the sake of symmetry.
6. **Write `header.html` and `footer.html`**: the specification the sheet follows and its date, the stories of the slice, the sources. Keep the authority sentence of the foot.
7. **Diagrams.** For each diagram a tab calls for, follow the `arch-uml` skill with the slice folder as the diagram folder, then place its `{{FIGURE:...}}` slot in the tab. Once a real diagram renders, delete `seq-00-example.puml` and its two SVGs: the example proved the pipeline and is not a figure of the sheet.
8. **OpenAPI.** When the slice adds or changes HTTP operations, write `openapi.json` (or `openapi.yaml`) with those operations only, and place `{{OPENAPI}}` in `api.html`.
9. Go on to **render**.

## Mode: render

Builds the page from the folder. Run it after every change to a source.

1. **Diagrams.** `./render.sh` in the slice folder (it needs Docker). Every figure a tab names must exist as `views/<name>.svg` and `views/dark/<name>.svg`.
2. **Page.** Follow the `com-artefact-viz` skill, kind `slice-design`:
   `python3 <com-artefact-viz skill dir>/scripts/render.py --kind slice-design --slice docs/plans/active/<slice-slug> --out docs/plans/active/<slice-slug>/out/<slice-slug>.html`
   A missing figure, a missing OpenAPI document or an unknown slot stops the render with a message naming the file: fix the source, never the page.
3. **Verdict.** `python3 <com-artefact-viz skill dir>/scripts/shared/check_render.py --record <page>.verdict.txt <page>`. The build is done only when the recorded verdict opens with `PASS: no findings`. On a finding, correct the partial it names (a literal colour, a `<style>`, a `<script>`) and render again.
4. **Look at it.** Open the page: the four tabs in order, each figure in the light and the dark theme, no sideways scroll at phone width.

If `com-artefact-viz` is not installed (the `delivery-comms` set), stop after the sources and say plainly that the page cannot be built on this machine; the sources are complete without it.

## Mode: publish

Puts the built page in front of its readers.

1. Render first; publish only a page whose recorded verdict is `PASS: no findings`, built after the last change to a source.
2. Where the harness can publish an HTML file as a private page, publish `out/<slice-slug>.html`. A first publication is outward-facing: confirm it with the owner unless they asked for it. Record the address on the `**Published page:**` line of the sheet's `README.md`.
3. When that line already holds an address, republish at that same address; never mint a second one for the same sheet.
4. Where the harness cannot publish, report the path of the built file and say that it was not published.

## What this skill does not do

| Asked for | Belongs to |
|---|---|
| The requirements, the stories, the acceptance criteria | `spec-prd`; the sheet follows them |
| The order of the work, increments, test gates | `plan-implementation`, which reads the sheet |
| A decision that outlives the slice | `arch-adr`, cited from the tab's decisions |
| The lasting views of the system (C4, arc42) | `arch-c4`, `arch-arc42` |
| What happens to a sheet once its slice is delivered | Not decided yet: leave the folder where it is and ask the owner |

## Closing report

1. The mode run and the folder.
2. Per tab: filled, or left empty on purpose and why.
3. The diagrams drawn, and whether the palette is the project's or the neutral one.
4. The verdict line as recorded, or why the page was not built.
5. The published address, or that the page was not published.
6. Each point where the specification was silent or contradicted itself, and how it was settled.

## Checklist

- [ ] The specification was read in full before any tab was written, and it is linked from `README.md` and named in `header.html`.
- [ ] The folder is `docs/plans/active/<slice-slug>/`, with `README.md` carrying the artefact frontmatter and `type: Slice Design Sheet`.
- [ ] No `_TODO_` and no unfilled `{{...}}` field is left in the folder.
- [ ] Every tab that has content ends with its decisions block; a tab the slice does not need holds its summary line only.
- [ ] No partial holds a `<style>`, a `<script>` or a literal colour.
- [ ] Every diagram was drawn through `arch-uml` and exists in both variants; the example diagram is gone.
- [ ] The recorded verdict opens with `PASS: no findings`.
- [ ] `out/` is ignored by git; the sources and `views/` are not.
- [ ] The foot states the sheet's authority: the specification decides.
