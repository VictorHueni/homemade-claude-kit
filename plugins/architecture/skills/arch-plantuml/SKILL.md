---
name: arch-plantuml
license: MIT
description: "Initialise and maintain the PlantUML diagrams workspace + Docker-based render pipeline that powers UML diagrams (sequence, class, state-machine, activity, ER, use-case) — the kit renders every UML diagram, arc42 §6 runtime sequences included, through it. One-time setup skill: scaffolds docs/architecture/diagrams/ (or the folder given) with {*.puml, _theme.puml, _palette.puml, render.sh, README.md, views/}, pins the official plantuml/plantuml Docker image, and provides a validate→render pipeline (.puml → SVG, light and dark, coloured by the project's design system). Companion to arch-uml, which authors the diagrams going forward. Triggers on: scaffold plantuml, init plantuml, plantuml workspace, set up plantuml, plantuml render pipeline, plantuml docker, uml render pipeline, plantuml foundation, diagrams folder. NOT for C4 architecture diagrams (arch-c4 / arch-structurizr) nor non-UML diagrams such as flowcharts (Mermaid)."
user-invocable: true
metadata:
  category: "architecture"
  complexity: "medium"
  version: "1.1.0"
  status: active
  last_reviewed: 2026-11-13
  review_interval: 365d
  impact: "low"
---

# PlantUML diagrams workspace + render pipeline

This is the **foundation** for every UML diagram the kit produces with PlantUML. It scaffolds the `docs/architecture/diagrams/` folder, or another folder you name, and the single-image Docker render pipeline (`.puml` → SVG, in a light and a dark variant). After `init` runs once, the `arch-uml` skill authors `.puml` files going forward; `arch-plantuml` does not author diagrams itself.

It is the structural twin of `arch-structurizr`:

| Structurizr pair | PlantUML pair | Role |
|---|---|---|
| `arch-structurizr` | **`arch-plantuml`** *(this skill)* | One-time scaffold: filesystem layout, pinned Docker version, render script, shared theme, conventions. |
| `arch-c4` | `arch-uml` | Per-diagram authoring: writes `.puml` files, runs `render.sh`, embeds SVGs into markdown. |

## Which diagram goes where

`rules/diagramming-mermaid.md` sets the split: C4 views go to Structurizr, every UML diagram goes to PlantUML rendered to **committed SVG**, and Mermaid covers only diagrams that are neither. This pipeline renders:

- **Sequence** diagrams, arc42 §6 runtime scenarios included
- **Class** diagrams (associations, generalization, multiplicities)
- **State-machine** diagrams (composite/nested states, history)
- **Activity** diagrams (swimlanes, fork/join)
- **Entity-Relationship** diagrams
- **Use-case** diagrams (actors, `«include»`/`«extend»`), for `spec-use-case`

**Out of scope (do not duplicate existing tooling):**

| Want | Use instead |
|---|---|
| C4 context / container / component / deployment | `arch-c4` (+ `arch-structurizr` pipeline) |
| A non-UML, non-C4 diagram (flowchart, mind map, timeline, Gantt) | Mermaid (`rules/diagramming-mermaid.md`) |
| Interactive HTML board / canvas / timeline | `com-artefact-viz` |

## Why two skills instead of one

| Skill | Role | Frequency |
|---|---|---|
| `arch-plantuml` | One-time scaffold: folder, pinned Docker version, render script, shared `_theme.puml`, conventions. | Once per project (re-run only on `upgrade`). |
| `arch-uml` | Per-diagram authoring: writes one `.puml` per diagram, runs `render.sh`, embeds the SVG into the consuming markdown. | Many times — every time a diagram is needed. |

The split mirrors structurizr/c4: **authoring (`.puml` editing) is separate from generation (the Docker pipeline)**.

## What the analogy bends on (read this)

Structurizr has **one** `workspace.dsl` = one shared model that `arch-c4` keeps extending. PlantUML has **no shared model** — each diagram is an independent `.puml` file. So:

- The "single source of truth" is the **`diagrams/` folder of independent `.puml` files**, not one file.
- Visual consistency is held by a shared **`_theme.puml`** that every diagram `!include`s (the analog of Structurizr's `styles{}` block). `arch-plantuml` owns that theme; `arch-uml` authors against it. The theme holds shape only; its colours are the variables of **`_palette.puml`** (see §Light and dark, and the palette).
- Files whose name starts with `_` are **includes, not diagrams** — `render.sh` never renders them.

## Output the skill produces

```
docs/architecture/diagrams/
├── _theme.puml          ← shared skinparam theme, !include'd by every diagram
├── _palette.puml        ← the colours, a light and a dark branch, !include'd by the theme
├── render.sh            ← single-image Docker pipeline (executable)
├── README.md            ← how to render locally; pinned version; conventions
├── *.puml               ← individual diagrams (authored by arch-uml)
└── views/               ← rendered SVGs, light (committed)
    ├── .gitkeep
    └── dark/            ← the same diagrams, dark (committed)
```

`docs/architecture/diagrams/` is the default. A diagram set that belongs to one document and is kept with it (a design sheet, a plan) takes its own folder and its own copy of the pipeline: `init <folder>`. `render.sh` renders the diagrams of the folder it sits in, wherever that is.

The skill does **not** author any diagram — that is `arch-uml`'s job. `init` seeds **one** example diagram (`seq-00-example.puml`) purely to prove the pipeline renders, then `verify` removes nothing (the example stays as a living smoke test until `arch-uml` adds real diagrams).

## Pipeline (read this before editing render.sh)

The official [`plantuml/plantuml`](https://hub.docker.com/r/plantuml/plantuml) image bundles `plantuml.jar` + a JRE + **Graphviz** (needed for class/state/activity/component layout — sequence diagrams do not need it). One image, one pass:

```
diagrams/*.puml
   │
   │  docker run plantuml/plantuml:<pin>
   │      -checkonly -failfast2   (validate)
   │
   │  docker run plantuml/plantuml:<pin>
   │      -tsvg -failfast2 -o <abs>/views  diagrams/*.puml
   │
   │  docker run plantuml/plantuml:<pin>
   │      -tsvg -failfast2 -DDARK=1 -o <abs>/views/dark  diagrams/*.puml
   ▼
diagrams/views/*.svg          ← light; committed; embedded in consuming markdown
diagrams/views/dark/*.svg     ← dark; committed; for a page that follows the viewer's theme
```

A **`-checkonly` validation** runs before render on every invocation. If any `.puml` fails to parse, render does not run and the script exits non-zero with the offending file.

**No Chromium, no headless browser.** Unlike the Structurizr `-playwright` image (~1.8 GB), `plantuml/plantuml` renders SVG directly from the jar. The image is a few hundred MB and a full render of a handful of diagrams completes in **~1–3 seconds** once pulled.

## Light and dark, and the palette

Every diagram renders twice from the same source: a light variant in `views/` and a dark one in `views/dark/`. `render.sh` passes `-DDARK=1` for the second pass, and `_palette.puml` answers it with its dark branch (`!ifdef DARK`). A page that follows the viewer's theme shows the variant that matches; markdown read on a white page embeds the light one.

`_palette.puml` defines twelve variables (`$canvas`, `$panel`, `$border`, `$head`, `$head_ink`, `$ink`, `$muted`, `$accent`, `$success`, `$warning`, `$danger`, `$info`) and `_theme.puml` uses nothing else for colour. The scaffolded palette is the kit's neutral base theme.

**When the project has a design system** (a `docs/ux/package.json` pin), the palette comes from it: invoke the `ux-design-system` skill and follow its **Diagram palette** section, which prints the palette of the resolved design, then write that output, unchanged, over `_palette.puml` and re-render. Run it again when the pin changes. Without a pin, or when that skill is not installed, keep the neutral palette and say so in the closing report. Never type a colour into `_palette.puml` or `_theme.puml` by hand.

`_theme.puml` hides the spot icon of a class (the circled C, I or E), whose colours no palette reaches, and styles the few marks PlantUML otherwise leaves in its own near-black, so that no mark of a dark render is unreadable.

## Modes

### Mode 1 — `init [folder]` (default)

Scaffold the diagrams tree from `templates/`. `<folder>` below is `docs/architecture/diagrams/` unless another folder is given. Pin the Docker image version in `render.sh`. Make `render.sh` executable.

**Steps:**
1. Verify the parent of the target folder exists (create `docs/architecture/` if the default is used and it is missing).
2. If `<folder>/render.sh` already exists, **abort** and recommend `verify` or `upgrade` instead. Never overwrite an existing pipeline.
3. Copy `templates/diagrams/_theme.puml` and `templates/diagrams/_palette.puml` into the folder. If the project has a design pin, replace the palette as §Light and dark, and the palette says.
4. Copy `templates/diagrams/seq-00-example.puml` → `<folder>/seq-00-example.puml` (the smoke-test diagram).
5. Copy `templates/render.sh` → `<folder>/render.sh` with `{{plantuml_version}}` substituted from the pin table in `references/docker-pipeline.md`. `chmod +x` it.
6. Copy `templates/plantuml-readme.md` → `<folder>/README.md` with the same substitution.
7. Create `<folder>/views/.gitkeep`.
8. Run Mode 2 (`verify`) automatically to confirm the scaffold renders.
9. Print a closing report (see §Closing report) and point the user at `arch-uml` for authoring.

### Mode 2 — `verify`

Confirm the scaffold + Docker image + diagrams all render. Read-only — never edits files.

**Steps:**
1. Check that `docs/architecture/diagrams/{render.sh, README.md, _theme.puml, _palette.puml, views/}` all exist (in the folder given, for a set that lives elsewhere).
2. Check that `render.sh` is executable.
3. Check that `render.sh` pins a concrete version (not `:latest`). Flag deviation.
4. Check Docker availability: `docker version` returns 0.
5. Check that the pinned `plantuml/plantuml:<pin>` image is present or pullable: `docker image inspect plantuml/plantuml:<pin> 2>/dev/null || docker pull plantuml/plantuml:<pin>`.
6. Run `./docs/architecture/diagrams/render.sh --dry-run` (validates every `.puml` with `-checkonly`). Surface any parse error with its filename.
7. Optionally run a full `./render.sh` and confirm at least one SVG lands under `views/` and its twin under `views/dark/`.
8. Report pass/fail per check.

### Mode 3 — `upgrade`

Bump the pinned Docker image version in `render.sh`, then re-render all diagrams to detect any visual change from the renderer.

**Steps:**
1. Read the current pin from `docs/architecture/diagrams/render.sh`.
2. Show the recommended new pin from `references/docker-pipeline.md` (kit-maintained pin table).
3. Ask the user to confirm the bump.
4. Edit `render.sh` to update the pin.
5. Run Mode 2 (`verify`) with the new pin.
6. Run `./render.sh` to re-render all diagrams; report any view that produced different SVG output (`git diff --stat docs/architecture/diagrams/views/`).
7. Recommend committing the render-script bump + any re-rendered SVGs together so reviewers can correlate.

**A workspace scaffolded before the two variants** has a `render.sh` that renders one theme and a `_theme.puml` that carries its own colours. `upgrade` brings it across, with the user's agreement at each step:

1. Replace `render.sh` with the current template, keeping the pin the workspace has (or the new one being adopted).
2. Add `_palette.puml` (the neutral one, or the design system's).
3. `_theme.puml`: if it is byte-identical to the template the workspace was scaffolded from, replace it with the current template. **If it was edited by hand, never overwrite it**: show the user the diff against the current template and let them decide; until the theme reads the palette variables, both variants render with the same colours.
4. Re-render and report the SVGs that changed, as step 6 above.

## Cross-references

- `arch-uml` (companion skill) — authors `.puml` diagrams, runs `render.sh`, embeds SVGs into the consuming markdown. Always check that `arch-plantuml init` has run first.
- `arch-structurizr` / `arch-c4` — the C4 toolchain. PlantUML does **not** draw C4 here; defer to those.
- `spec-use-case` — its UML use-case diagrams are rendered by `arch-uml` through this pipeline.
- `domain-model` — class / state-machine / ER diagrams for the domain are rendered here.
- `rules/diagramming-mermaid.md` — the three-way diagram split (C4, UML, everything else).
- the `metamodel` skill — supporting-skills list entry + canonical path `docs/architecture/diagrams/`.

## Optional — PlantUML MCP server

Community MCP servers (e.g. `infobip/plantuml-mcp-server`, `antoinebou12/uml-mcp`) expose PlantUML render / encode / lint as MCP tools an agent can call directly (no shell-out). Setting one up is **optional** — `arch-plantuml` + `arch-uml` work without it via `docker run`.

See `references/mcp-optional.md` for the trade-off and setup instructions if you want the MCP path.

## Reference materials

- `references/puml-conventions.md` — filename convention (`<type>-NN-<slug>.puml`), view-key = filename stem, the `_`-prefix include rule, `@startuml/@enduml` + `!include _theme.puml` discipline, kit cross-reference rules (carry upstream IDs in titles).
- `references/docker-pipeline.md` — render.sh contract, pinned version, volume-mount conventions, exit codes, troubleshooting, CI hook recommendations.
- `references/mcp-optional.md` — optional PlantUML MCP server setup.

## Closing report

After each mode, deliver:

- Mode executed (init / verify / upgrade)
- Files created or modified (list)
- Pinned version: `plantuml/plantuml:<pin>`
- Validation/render result (which diagrams rendered)
- Next step: `arch-uml <type>` (if init) or commit (if upgrade)

## Checklist

- [ ] The diagrams folder exists with `render.sh`, `README.md`, `_theme.puml`, `_palette.puml`, `views/.gitkeep`
- [ ] `render.sh` is executable + pins a concrete version (not `:latest`)
- [ ] `docker version` succeeds in the verify step
- [ ] `--dry-run` (`-checkonly`) passes on the seed diagram(s)
- [ ] Initial `render.sh` run produces at least one SVG under `views/` and its dark twin under `views/dark/`
- [ ] `_palette.puml` is the design system's when the project pins one, else the neutral one, and the report says which
- [ ] `README.md` documents the pinned version + the manual render command + the `_`-prefix include rule
- [ ] User reminded that `arch-uml` is the next skill to invoke
