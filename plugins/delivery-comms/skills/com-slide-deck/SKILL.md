---
name: com-slide-deck
license: MIT
description: "Build single-file HTML slide presentations from modular partials and a Python build pipeline, themed by the project's design system (the docs/ux/package.json pin, else the kit base theme) and checked by a blocking validator before anything is written. Use this skill any time the user wants to create, edit, split, stitch, prototype, or migrate HTML slide decks. Triggers include: any mention of \"slides\", \"presentation\", \"deck\", \"slide builder\", requesting a new slide, editing an existing slide, prototyping visual variations, migrating an old deck onto the design system, a dark slide or deck, a deck's classification in the footer, or working with the slide-builder folder. Also use for paginated A4/Letter documents built from the same partials pipeline (`mode: document`: user guides, forms, handouts, one-pagers rendered to a print PDF with running header and page numbers). Do NOT use for PowerPoint (.pptx) files or Google Slides (this skill exports its own decks to PDF via render.py)."
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/init.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/build.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/split.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/migrate.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/dev_server.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/render.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/shared/design_source.py *) Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/shared/check_render.py *)
user-invocable: true
metadata:
  category: "communication"
  complexity: "high"
  version: "2.1.0"
  status: active
  last_reviewed: 2026-10-14
  impact: "low"
---

# Slide Builder

Build modular HTML slide presentations driven by a presentation brief and the project's design system, stitched into a single shareable file via Python.

This skill is a **portable toolkit**. It lives in its own versioned folder and generates projects elsewhere. The skill never contains project-specific content.

## Running the scripts

- `<skill-dir>` in every command below is the absolute path on the "Base directory for this skill" line at the top of this skill. Write it out in full: no shell variable, no `cd`.
- **One plain command per Bash call**, starting with `python3`. No `&&`, `;`, pipes, redirections or `$VAR`: restricted sessions (only `python3`, `mkdir` and `cp` allowed) deny compound commands. Paths are relative to the working directory.
- Look at files with Read, Glob and Grep, never `ls`, `cat` or `head`. Create and change files (brief, config, partials, styles) with the Write and Edit tools.
- **If a command is denied, or a script refuses** (exit 1 or 2): stop and report the command, its message, and what the owner must do. Never hand-write the deck's HTML or CSS instead: no hand-written CSS replaces a refused design.

## Quick Reference

| Task | What to do |
|---|---|
| Check which design a build will use | `python3 <skill-dir>/scripts/shared/design_source.py provenance` |
| New deck | `python3 <skill-dir>/scripts/init.py docs/communication/slides/{slug} --name "Title" --author "Name"`, then write the brief and the partials |
| New A4 document (guide, form, handout) | `python3 <skill-dir>/scripts/init.py docs/communication/documents/{slug} --mode document`; see **Document mode** |
| Add or edit a slide | Write the partial in the project's `output/slides/`, list it in `config.yaml` |
| Build shareable HTML | `python3 <skill-dir>/scripts/build.py --config {deck}/config.yaml [--output out/deck.html]` |
| Record the verdict (after every build) | `python3 <skill-dir>/scripts/shared/check_render.py --record {output}.verdict.txt {output}` |
| Export to PDF | `python3 <skill-dir>/scripts/render.py --config {deck}/config.yaml [--recipient NAME] [--date YYYY-MM-DD]` (optional Playwright) |
| Re-theme the brand (palette, fonts, logo) | Change the project design, never the deck: `ux-design-system` (`point` a package, or edit `docs/ux/DESIGN.md` and run `subset`) |
| Restyle this deck only | Edit the project's `design/styles.css` (components, contract roles only) |
| Make one slide dark | Add `dark` to the partial's root: `<div class="slide s-example dark">`; see **Dark slides, decks and documents** |
| Make the whole deck or document dark | `theme: dark` in `config.yaml` |
| Print the deck's classification in the footer | `classification: Confidential` in `config.yaml` (Public, Internal, Confidential, Strictly confidential); see **Classification** |
| Live preview while editing | `python3 <skill-dir>/scripts/dev_server.py --config {deck}/config.yaml --port 3000` |
| Split an existing deck | `python3 <skill-dir>/scripts/split.py <file> --config {deck}/config.yaml` |
| Migrate an old deck | `python3 <skill-dir>/scripts/migrate.py --config {deck}/config.yaml` (report) · `--apply` (alias shim) · `--rename` (rewrite names) |
| Cite a source on a slide | `data-sources="key1,key2"` on the `.slide` div; entries in `context/bibliography.yaml` |
| Add `<head>` meta tags | A `meta:` list in `config.yaml` (`- {name: …, content: …}`), HTML-escaped |

Add a `bibliography.yaml` entry only for a source a slide cites (`data-sources`); never pre-populate it, and remove existing entries only on request. Keep the inline links in the markdown research docs: the two channels do not substitute for each other.

---

## Design, validator, provenance and verdict

The design contract (modules, manifest, contrast pairs, fonts) is [`contract/README.md`](../../contract/README.md). What a deck needs from it:

1. **Resolution order**, once per build: `paths.design_tokens` in `config.yaml` (a design-system folder with a `kit-manifest.json`, for previewing an unreleased design), else the `docs/ux/package.json` pin found by walking up from the deck, else the kit's neutral base theme. A pin names a package at an exact version (downloaded once, integrity-checked, cached per machine) or a local folder (`file:design-system`). Modules the design omits come from the base theme.
2. **What the design gives the deck**: the palette, type, spacing, the slide canvas (`--slide-width`, `--slide-height`), the frame (`.slide`, `.slide-label`, and the footer row with the brand logo, the legal line, the classification and the slide number), the dark roles (the `dark` module, from the design or the base theme) and the font faces. `build.py` inlines them in one `<style data-design-layer>`; the deck's `design/styles.css` comes after and holds deck components only.
3. **Blocking validator**: the build checks the HTML before writing it. Refused: a literal colour (hex, `rgb()`, `hsl()`, a named colour) outside the design layer, a custom property outside the contract's roles and the reserved `--kit-*` prefix, a contrast pair an exception brings below WCAG AA. Exit `0` written; `1` findings, nothing written, each finding naming the value, its location and the role to use: fix the CSS or the partial to use that role and build again; `2` the design was refused (a legacy file, a broken manifest, a pair below AA): see **Legacy design file**.
4. **Exceptions**: a deliberate local value the owner asked for is declared in `config.yaml` under `design.exceptions` (`NAME: VALUE`) and listed in the provenance report. Never add one to get past a finding.
5. **Provenance**: every build prints and writes `<output>.provenance.json` next to the HTML: the design's name, version and repo-relative path, the source (`design-system` or `base`) of every module, the exceptions and warnings. `render.py` writes one next to the PDF too.
6. **Verdict**: after the build, run `python3 <skill-dir>/scripts/shared/check_render.py --record <output>.verdict.txt <output>` on the delivered HTML and report its first line. It writes `PASS: no findings` or `FAIL: …`, the file, the design and the findings. The deck is not done without `PASS`.
7. **Reproducible output**: the same sources and the same design give byte-identical HTML and PDF. Dates come from the sources (`config.yaml`, partials, styles, script, bibliography), never the clock: `SOURCE_DATE_EPOCH` when set, else the sources' last commit, else their newest modification time. `--date` overrides only the recipient stamp and footer label. Printed paths are repo-relative.

### Legacy design file

A project whose only design source is a `docs/ux/tokens.css` (or `docs/design/tokens.css`) is refused with exit 2 and a message naming `ux-design-system point`, `subset` and `subset --from-legacy`. Then:

1. Invoke the `ux-design-system` skill and run its `subset --from-legacy docs/ux/tokens.css`. It drafts `docs/ux/DESIGN.md` with the legacy colours and a proposed chart palette under a `proposed:` mark.
2. **Stop.** Show the owner the drafted `DESIGN.md`, the proposed chart colours and anything the run could not map, and say what remains: the owner reviews the palette and removes the `proposed:` line, `subset` generates the design, then the deck builds.
3. Never edit or delete the legacy file, never remove the `proposed:` line yourself, never write `docs/ux/design-system/` by hand, and never deliver a deck on hand-written colours.

---

## Skill vs Project

This skill contains only reusable, versionable assets:

```
com-slide-deck/
  SKILL.md                     This file
  README.md                    Human-readable docs
  templates/
    brief-template.md          Blank presentation brief
    design-system-template.md  Deck component notes (colours and type come from the project design)
    bibliography-template.yaml Blank source registry
    config-template.yaml       Blank build configuration
    doc.baseline.css           Document-mode break rules
  scripts/
    init.py                    Scaffolds a new project
    build.py                   Stitches partials into one HTML, validates, writes provenance
    render.py                  PDF export (optional Playwright)
    split.py                   Splits a single-file deck into partials
    migrate.py                 Moves an old deck's token names onto the contract
    dev_server.py              Auto-rebuild + local HTTP server
    shared/                    The kit resolver and validator (design_source.py, check_render.py, base theme)
```

A project is generated by `init.py` and lives in your working repo:

```
docs/communication/slides/{slug}/   PROJECT, named after the deck (e.g. investor-pitch)
  context/
    brief.md                 The brief (you fill this)
    bibliography.yaml        Source registry
  design/
    design-system.md         Deck component notes (optional until the deck adds components)
    styles.css               Deck components, contract roles only
    script.js                Presentation mode and helpers
  output/
    slides/                  One file per slide (source of truth)
    prototypes/              Experimental variations
    slide-deck/              Built HTML (default output)
  config.yaml                Build configuration
```

---

## Startup sequence

Run these steps in order before writing slide HTML, CSS or JS.

### Step 0: Locate the project

1. Find the deck's folder (the one holding `config.yaml`) with Glob.
2. If none exists, derive a kebab-case slug from the deck's subject and scaffold it with `init.py` (one command, see Quick Reference).

### Step 1: Brief

1. Read the project's `context/brief.md`.
2. **If it still holds placeholders ("..."):** when the user's request already gives the subject, audience, tone and the content of each slide, write `context/brief.md` from it with the Write tool (follow `context/brief-template.md`'s sections, mark a section the request does not cover as "not specified") and go on. Otherwise ask for what is missing, one point at a time, before writing slides.

### Step 2: Design

1. Check the design: `python3 <skill-dir>/scripts/shared/design_source.py provenance`. Exit 0 prints the design and the source of each module; exit 2 is a refusal: follow **Legacy design file** (a legacy token file) or report the message (anything else) and stop.
2. The palette, type, canvas and frame come from that design. `design/styles.css` holds only the deck's components, written with contract roles (`var(--accent)`, `var(--font-mono)`), never a literal colour.
3. `design/design-system.md` records the deck's own components and layout rules (template: `design/design-system-template.md`). A deck that uses only the frame and plain text needs nothing in it; fill a section when the deck adds a component.

### Step 3: Load context

Read `context/brief.md`, `design/design-system.md` (if filled) and `config.yaml` before any slide work.

---

## Bibliography & Source Citations

Every external figure (statistic, count, date, published claim) on a slide **must** be backed by a source entry in `context/bibliography.yaml`, scaffolded by `init.py`.

- **External fact with a public URL**: add an entry and reference it on the slide with `data-sources`.
- **Internal estimate (no public source)**: add an entry with `org: "Internal estimate"` and no `url`, so the assumption is explicit.
- **Unsourced figure**: leave it out. A figure the user gives in the request as fictitious or internal is an internal estimate.

```yaml
# context/bibliography.yaml
sources:
  interpharma-preismodelle:
    org: Interpharma
    title: "Preismodelle bei Medikamenten"
    url: "https://www.interpharma.ch/blog/preismodelle-bei-medikamenten-darum-geht-es/"
    year: 2023
    accessed: 2026-05-14
```

Fields: `org`, `title`, `url`, `year`, `accessed`, all optional except the key; recommended minimum `org + title + url + year`. Add `data-sources="key1,key2"` to the **root `.slide` div**; `build.py` resolves the keys and injects a `.slide-source-bar` above the footer row. An absent or empty bibliography skips the bars; an unknown key prints a warning and is skipped; several keys render left to right, separated by `|`.

---

## Creating a slide

### Partial format

Every slide is a standalone HTML fragment:

```html
<div class="slide s-example">
  <div class="slide-label">SECTION NAME</div>
  <h2 class="slide-title">Slide Title Here</h2>
  <!-- content using components from design/styles.css -->
</div>
```

Rules:
- Wrap in `<div class="slide {slide-class}">`; one root `.slide` per partial.
- The section label is `<div class="slide-label">`, styled by the design's frame. Do not write a slide number, logo, legal line or classification: `build.py` adds the footer row to every slide (a legacy `<div class="slide-number">` is removed with a note).
- A dark slide carries `dark` on this root element (`<div class="slide s-example dark">`), never on an inner element and never through the `class:` key of `config.yaml`, which `build.py` does not read.
- Use the frame's classes and the classes in `design/styles.css`; colours, fonts and spacing through contract roles (`var(--accent)`, `var(--font-mono)`), never a literal value.
- Lay content out within the design's canvas (`--slide-width` by `--slide-height`; `canvas:` in `config.yaml` overrides it for one deck).

### Adding it to the deck

1. Write the file in the project's `output/slides/` with a numbered prefix: `NN-slug.html`.
2. If new CSS is needed, add it to `design/styles.css` scoped as `.s-example .my-element { ... }`.
3. List it in `config.yaml`:
   ```yaml
   slides:
     - file: "NN-slug.html"
       class: "s-example"
       label: "Human-readable name"
   ```
4. Build, then record the verdict (Quick Reference). A delivery path the user names goes in `--output` (for example `--output out/deck.html`); the provenance file follows it.

### CSS conventions

- Scope slide-specific styles: `.{slide-class} .{element} { ... }`.
- Check the frame's classes and existing components before creating new ones.

---

## Dark slides, decks and documents

The design's `dark` module holds a dark twin `--dark-<role>` of every colour role (contract: [`contract/README.md`](../../contract/README.md), **Dark**). A design that does not provide `dark` gets the kit base theme's neutral dark roles; the provenance says which.

- **One slide**: `dark` on the partial's root, `<div class="slide s-example dark">`.
- **Every slide, or every page of a `mode: document`**: `theme: dark` in `config.yaml`. `theme:` takes `light` (the default) or `dark`; any other value exits 2.
- **What the kit does**: inside a dark slide or page, `build.py`'s own layer remaps every mirrored role to its twin (`--ink` reads `--dark-ink`, `--slide-bg` reads `--dark-slide-bg`, and so on), chooses the text on each fill again against the dark roles, and swaps the footer logo to `--brand-logo-on-dark` (a design without an on-dark logo shows no logo on a dark slide). So the deck's components keep their light rules (`var(--ink)`, `var(--surface)`, `var(--chart-1)`) and turn dark with the slide; charts are allowed on dark. The dark CSS is inlined only when a slide or the deck is dark.
- **The key element** of a dark slide (the one card or figure the slide is about) takes `class="dark-key"`: its fill is `--dark-key-fill`, its outline `--dark-key-edge`, and its text is checked on `--dark-key-base`. One per slide.
- **Highlighted words** on a dark slide take `class="dark-accent"` (`--dark-accent-text`).
- **Never a deck-local dark palette.** No `--dark-bg`, `--dark-text` or any other `--dark-*` property in `design/styles.css`, no `.dark { --ink: ... }` remap of your own and no exception for one: the validator refuses a property outside the contract, and the remap is the kit's. A dark value the design lacks belongs in the project design (`ux-design-system`).
- A document's running header and footer follow `theme: dark` (the dark `--muted`, the on-dark logo); the printed page background is the design's `--dark-print-bg`.

## Classification

`classification:` in `config.yaml` prints the deck's data classification at the right of every slide's footer row, just before the slide number, and in the running footer of every page of a `mode: document`. A classification alone turns the footer on (a deck with numbering off still gets the footer row). Absent, nothing is printed.

- **Four levels**, a common four-level scheme, matched case-insensitively: `Public`, `Internal`, `Confidential`, `Strictly confidential`. Any other value exits 2 naming the four. Use `Strictly confidential` for a deck holding sensitive personal data in the sense of GDPR Art. 9 (special categories, such as health data) and the Swiss nFADP Art. 5 lit. c; the other three follow the organisation's own scheme. When the user names no level, leave the key out or ask; never guess one.
- **Language**: the label follows the deck's `lang:` (`fr-CH` reads as `fr`). Built in: `en`, `fr` (Public, Interne, Confidentiel, Strictement confidentiel), `de` (Öffentlich, Intern, Vertraulich, Streng vertraulich) and `it` (Pubblico, Interno, Confidenziale, Strettamente confidenziale). Another language prints the English label and the build warns.
- **The label only**: no code (C0 to C3) and no free text; never write a classification into a partial or the legal line.
- **Restyle it**: the cell is `<span class="slide-classification">` (mono, uppercase, `--tertiary`). A deck restyles it in `design/styles.css` with `.slide-classification`; a design's `slide-frame` module needs `.slide-footer .slide-classification`, since the kit's rule comes after the design layer.

---

## Editing and prototyping

- **Edit**: change the partial in `output/slides/` with the Edit tool, build, record the verdict.
- **Prototype**: write variations in `output/prototypes/` as `{slide-number}-{concept}-v{version}.html` (same partial format); once approved, move to `output/slides/` and update `config.yaml`.

## Splitting an existing deck

One-time migration from a single-file HTML presentation: `python3 <skill-dir>/scripts/split.py path/to/deck.html --config path/to/config.yaml`. Rename the generated files to match `config.yaml`, then build.

## Migrating an old deck onto the design contract

A deck written before 2.0.0 usually carries literal colours and legacy token names, which the validator refuses. **Commit the deck first.**

1. **Give the project a design** if it has none: `ux-design-system` (`point` a published design, or `subset` from a DESIGN.md; a legacy `docs/ux/tokens.css` goes through `subset --from-legacy`, see **Legacy design file**).
2. **Report**: `python3 <skill-dir>/scripts/migrate.py --config path/to/config.yaml` lists every literal colour in `styles.css` and the partials with the closest resolved role, the legacy token names in use (file and count) and the rename map.
3. **Pick a path**: `--apply` adds an alias shim to `styles.css` (`--bg: var(--canvas-bg)`, …); the aliased names are not contract roles, so the build then needs them under `design.exceptions` (the report says which). `--rename` rewrites the changed names to contract names across `styles.css` and every partial; no shim or exception needed. Prefer `--rename`.
4. **Replace the literal colours** the report lists with the roles it names. A brand value the design lacks belongs in the project design (`ux-design-system`), not in the deck.
   **A deck-local dark palette** (`--dark-bg`, `--dark-text` and friends in `styles.css`, used by a dark slide's rules): delete those properties and the rules that apply them to the dark slide, put `dark` on that slide's partial root (or `theme: dark` when every slide is dark), mark the key element `dark-key` and highlighted words `dark-accent`. The slide then takes the design's dark roles, or the base theme's when the design omits `dark`.
5. **Build** until the validator passes, then record the verdict.

`migrate.py` changes token names only; it never moves values or edits component rules.

## PDF export (leave-behind)

`render.py` reads the deck `build.py` wrote to its default output (`output/slide-deck/`), so build without `--output` first. It validates the HTML (exit 1 on findings, 2 on a refused design, no PDF either way), then renders it with headless Chromium through Playwright: one slide per page at the canvas size, backgrounds kept, an optional recipient stamp (`--recipient "Name"` prints "Prepared for Name · <date>"). It writes `output/pdf/<name>[--recipient].pdf` (override with `--output`) and `<pdf>.provenance.json`. Playwright is optional and never auto-installed: without it `render.py` fails with an explicit message.

**The PDF is reproducible** ([#106](https://github.com/VictorHueni/homemade-claude-kit/issues/106), ADR-0013 in the kit repository): its creation and modification dates are the deck's source date, so the same sources and the same design give the same bytes. To check that a committed PDF is current, render it again to another path (`--output`) and compare the bytes with the committed file (`cmp`, or the two SHA-256 digests): equal bytes mean current; a difference means the sources, the design or the toolchain changed since. PDFs rendered before 2.0.0 change bytes once.

## Document mode (A4 / Letter documents)

`mode: document` in `config.yaml` reuses the whole pipeline (brief, design, partials, bibliography, `build.py`, `render.py`) to produce a **paginated print document** instead of a 16:9 deck: a user guide, a data-collection form, a handout, a one-pager. Scaffold with `init.py --mode document` (creates `output/pages/` and `output/document/`, and a `script.js` with no presentation controls).

What changes versus slides:

- **Partials are flowing sections, not fixed canvases.** Each file is `<section class="doc-section">…</section>`; no `.slide` wrapper, no absolute positioning. A `.doc-section` starts a new page by default; add `doc-section--flow` to let it follow the previous one. Use `.doc-keep` on any block that must not split across pages. The `doc*` classes are the design's `document` module vocabulary.
- **Page geometry lives in one place.** The `page:` block (`size`, `orientation`, `margin`, `running_header`, `footer_left`, `numbering`) is turned into the `@page` rule by `build.py` and passed verbatim to Chromium by `render.py`. On screen, `build.py` previews the document on a paper sheet with the same margins.
- **Page numbers come from Chromium.** The running header and the footer sit in the page-margin boxes, a separate document the validator never sees; they carry the design's resolved `--muted` and `--font-mono`, and the brand logo and legal line when the design provides them.
- **`render.py` prints with real print media** (`@media print` applies); slides mode emulates screen media. Set `lang:` in `config.yaml` for a non-English document (it also sets the classification's language).
- **Dark and classified documents**: `theme: dark` prints every page dark; `classification:` puts the label in every page's running footer, just before the page number. See **Dark slides, decks and documents** and **Classification**.
- **Never let an inline run exceed the measure.** A single unbreakable run wider than the page (a `white-space: nowrap` code span holding a SQL statement, a long URL) makes Chromium scale the *whole document* down to fit; the tell is a page count that drops and body text that looks smaller than the stylesheet says. Give long inline code `overflow-wrap: anywhere`, or set it in a `pre`.
- **Break rules in the shipped baseline** (`templates/doc.baseline.css`): headings never strand at a page foot, tables repeat their `<thead>`, rows, list items and figures do not split, orphans and widows are three lines.

The design rules apply unchanged. In `design/design-system.md`, the canvas section becomes the page geometry and the presentation-mode section is N/A.

## Verification checklist

1. [ ] Project folder exists with `config.yaml`; `context/brief.md` has no placeholders.
2. [ ] `design_source.py provenance` names the intended design (a pin, a folder, or the base theme on purpose).
3. [ ] `design/styles.css` holds deck components only, contract roles only; no literal colour anywhere and no `--dark-*` property.
4. [ ] Each partial has one root `.slide` (slides mode) and no slide number, logo, legal line or classification of its own; a dark slide carries `dark` on that root.
5. [ ] A classified deck has `classification:` in `config.yaml` at one of the four levels, and the label shows in the deck's language.
6. [ ] Every slide is listed in `config.yaml` in order; content follows the brief.
7. [ ] Every external figure has a key in `context/bibliography.yaml`.
8. [ ] `build.py` exited 0 and wrote `<output>.provenance.json`.
9. [ ] `check_render.py --record <output>.verdict.txt <output>` reads `PASS: no findings`; report it.
10. [ ] Slides mode: the deck scales on a mobile viewport (baseline responsive CSS is injected by `build.py`).

## Dependencies

- Python 3.12 or later and PyYAML (`pip install pyyaml`).
- **Playwright**, optional, only for `render.py`: `pip install playwright && python3 -m playwright install chromium`.
