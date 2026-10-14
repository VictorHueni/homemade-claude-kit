# Design-system discipline

Internal guidance for the `ux-design-system` skill.

## Principles

1. **One design per project.** `docs/ux/package.json` pins the single design every renderer uses: a published package or the project's generated subset. Two designs means drift.

2. **A published design system wins.** When the organisation publishes a design-system package with a `kit-manifest.json`, `point` at it; do not author a subset that copies its values. A subset is for a project with no design system of its own.

3. **Author the DESIGN.md, generate the rest.** The DESIGN.md is the human artefact (values in the front matter, guidance in the prose); `design-system/` is generated and machine-owned. Durable edits go in the DESIGN.md.

4. **Declare what is missing.** A subset fills whole modules and names every optional module it leaves out, with the reason, under `omitted`. The kit's neutral base stands in for an omitted module, and the render's provenance says so.

5. **Roles are the contract; values are the brand.** The front matter keys are the contract roles (`contract/modules.json`). Renderers derive their domain colours from those roles (`com-artefact-viz`: status and pain on the state roles, importance and confidence on `--chart-1` to `--chart-3`); a project themes the roles, never the renderers' `--kit-*` properties.

6. **The owner confirms the chart palette.** A proposed `dataviz` block is a starting point computed from the accent, contrast-checked; the agent shows it, and only the owner removes the `proposed:` mark.

7. **Domain-agnostic.** The skill ships neutral defaults and a fillable template. No real brand colour, font or client name appears on the skill side, only in a project's own `docs/ux/`.

8. **No IDs, no links.** The design mints no IDs and carries no references to other artefacts.

## Boundaries: what this skill is not

- **Not a renderer.** It produces a design, not HTML. Decks are `com-slide-deck`, artefact views `com-artefact-viz`, release notes `com-release-note`.
- **Not a design-system builder.** A complete design system (DTCG source, build, adapters, release) from a template is out of scope ([#114](https://github.com/VictorHueni/homemade-claude-kit/issues/114)).
- **Not per-deck or per-view.** It is project-scoped (`docs/ux/`). A deck may still carry deck-only CSS, which the validator checks against the design.
