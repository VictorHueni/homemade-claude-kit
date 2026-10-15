# Slide Builder

A portable toolkit for building single-file HTML presentations from modular
slide partials, driven by a presentation brief and a design system, stitched
via Python.

This is the **skill** (reusable toolkit). It does not contain any
project-specific content. Version this in Git and import it into any
agent or project when needed.

---

## Install as a Claude Skill

Copy or clone this folder into your skills directory:

```bash
# Personal skill (all projects)
cp -r com-slide-deck ~/.claude/skills/slide-builder

# Project skill (this repo only)
cp -r com-slide-deck .claude/skills/slide-builder
```

The agent will pick it up automatically via the `SKILL.md` frontmatter.

---

## Folder Structure

```
com-slide-deck/
  SKILL.md                       Agent instructions (with frontmatter)
  README.md                      This file
  templates/
    brief-template.md            Blank presentation brief
    design-system-template.md    Deck component notes (colours and type come from the project design)
    config-template.yaml         Blank build configuration
  scripts/
    init.py                      Scaffolds a new project directory
    build.py                     Stitches slide partials into one HTML
    split.py                     Splits a single-file deck into partials
    migrate.py                   Migrate an old deck onto the shared design-system tokens
    dev_server.py                Auto-rebuild + local HTTP server
```

---

## Requirements

- Python 3.12+
- PyYAML (`pip install pyyaml`)
- A project design: the `docs/ux/package.json` pin written by `ux-design-system` (`point` or `subset`), else the kit's base theme. See [`../../contract/README.md`](../../contract/README.md).

---

## Quick Start

### 1. Scaffold a new project

```bash
python3 scripts/init.py ./my-presentation --name "My Talk" --author "Jane Doe"
```

This creates:

```
my-presentation/
  context/
    brief-template.md       Reference copy
    brief.md                Fill this in
  design/
    design-system-template.md  Reference copy
    design-system.md        Deck component notes (optional)
    styles.css              Deck components, contract roles only
    script.js               Presentation mode JS here
  output/
    slide-deck/             Build output lands here
    slides/                 One HTML file per slide
    prototypes/             Experimental variations
  config.yaml               Slide order, paths, metadata
```

### 2. Fill in the prerequisites

1. Complete `context/brief.md` (summary, goal, audience, tone, key messages)
2. Note the deck's own components in `design/design-system.md` (colours, fonts, canvas and frame come from the project design)
3. Write `design/styles.css` for those components with contract roles only (`var(--accent)`); the build refuses literal colours
4. Adjust `design/script.js` for presentation mode if needed

### 3. Create slides and build

```bash
# Create slide partials in output/slides/
# Add them to config.yaml
# Then build:
python3 path/to/com-slide-deck/scripts/build.py --config ./my-presentation/config.yaml
# Record the verdict next to the output:
python3 path/to/com-slide-deck/scripts/shared/check_render.py --record my-presentation/output/slide-deck/presentation.html.verdict.txt my-presentation/output/slide-deck/presentation.html
```

Output: `my-presentation/output/slide-deck/presentation.html`, with `presentation.html.provenance.json` (which design themed it) beside it. The build checks the HTML against the design before writing it: exit 1 on findings, 2 when the design is refused.

### 4. Share

Send the generated HTML file. It's self-contained, works offline in any
browser, zero dependencies.

---

## Migrating an Existing Deck

If you already have a single-file HTML presentation:

```bash
# Scaffold a project first
python3 scripts/init.py ./my-deck

# Split the existing file into the project
python3 scripts/split.py existing-deck.html --config ./my-deck/config.yaml
```

Then rename the generated slide files, update `config.yaml`, and build.

---

## Document mode (A4 / Letter)

Set `mode: document` in `config.yaml` (or scaffold with `init.py --mode document`) to build a paginated print document from the same partials pipeline: flowing `<section class="doc-section">` partials, page geometry from the `page:` block (shared by the `@page` rule and Chromium's print margins), running header and page numbers in the PDF. Same `build.py` / `render.py` commands. See SKILL.md → Document mode.

## Dev Server

Auto-rebuild on file changes with a local HTTP server:

```bash
python3 scripts/dev_server.py --config ./my-presentation/config.yaml --port 3000
```

Or use VS Code Live Server pointed at `output/slide-deck/`.

---

## LLM Agent Usage

Point any Claude agent at `SKILL.md`. The agent will:

1. Scaffold a project if none exists
2. Check that the brief is completed (or walk you through filling it in)
3. Check which design the build will use (`design_source.py provenance`), and stop on a refused legacy `tokens.css`
4. Read the brief, the deck notes and the config before touching any slides
5. Follow the brief for content and the project design for visuals
6. Build, then record the validator verdict, after every change
