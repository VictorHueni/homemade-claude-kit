# Visualisation discipline

Internal guidance for `com-artefact-viz`. Principles first; the mechanics live
in `SKILL.md` and `parsing-contract.md`.

## Principles

1. **The Markdown is the source of truth.** A view is a derived read-out, never
   a second editing surface. It carries no authored content that isn't in the
   artefact, so it can always be regenerated and never drifts. If a user wants
   to "fix" something in a view, the fix belongs in the source artefact.

2. **Style is the project's, not the skill's.** Renderers emit semantic class
   names and reference only contract roles (`var(--accent)`, `var(--chart-1)`)
   and renderer-owned `--kit-*` properties, never a literal colour, font,
   radius, or shadow. The kit's base theme is deliberately neutral; the
   project's resolved design (its `docs/ux/package.json` pin, or a
   `--design-system` folder) themes every view. Status and pain take the
   state roles; importance and confidence take the ordered chart scale,
   darkest first. A renderer that hard-codes `#396cf5` is a bug, and the
   validator refuses the view.

3. **One self-contained file.** All CSS and JS are inlined. No build step at
   view-time, no network fetch, no runtime dependency. The output is shareable
   by sending one file and is diff-friendly enough to commit.

4. **Progressive interactivity.** Every view is valid static HTML first; the
   JS runtime only *enhances* (collapse, orientation, disclosure). A view with
   JS disabled still reads correctly.

5. **Parse defensively.** Real artefacts are half-filled. Parsers tolerate
   missing columns, placeholder cells, reordered headers, and absent sections,
   and degrade to an empty-but-valid view rather than crashing.

## Boundaries — what this skill is NOT

- **Not a slide builder.** Narrative presentations are `com-slide-deck`. This
  skill renders one artefact as one analytical view, not a sequence of slides.
- **Not an architecture diagrammer.** C4 / structurizr diagrams are `arch-c4`
  and `arch-structurizr`. This skill does not draw containers/components.
- **Not an authoring tool.** It never writes into the source artefact and never
  invents content. Authoring stays with the owning skill
  (`business-capability-map`, `plan-delivery-roadmap`, etc.).
- **Not a metamodel step.** It mints no IDs and nothing references its output.
  It is a supporting communication skill, wired like `com-slide-deck`.

## Domain-agnostic discipline

Per `rules/skill-creation-sync.md`, the kit is user-global. Templates, defaults,
and example fixtures use neutral placeholders ("Example Platform", generic
capability names) — never a real client, currency, or segment. Only a project's
own rendered output is project-specific; the skill side stays neutral.

## Re-theming recipe (most common request)

Views, decks and release notes all theme from the project design, so a view
already matches the project's decks. To change the look, change the design
with `ux-design-system` (`point` a published package, or edit
`docs/ux/DESIGN.md` and run `subset`), then re-render. To preview an
unreleased design, name its folder:

```bash
python3 scripts/render.py docs/business/03a-capability-map.md --design-system path/to/design-system/
```

A single stylesheet (a deck's `styles.css`, a legacy `docs/ux/tokens.css`) is
refused: the design is a folder with a `kit-manifest.json`.
