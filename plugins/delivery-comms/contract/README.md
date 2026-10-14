# delivery-comms design contract 2.0.0

What a design system gives the three renderers (`com-slide-deck`, `com-artefact-viz`, `com-release-note`). It replaces the single 24-token `docs/ux/tokens.css` file. The role list per module is `modules.json`; the manifest format is `kit-manifest.schema.json`. This README is the prose; where they disagree, the JSON wins and this file is wrong.

## Modules

| Module | Required | Holds |
|---|---|---|
| `core` | yes | The 24 roles of the old contract: palette, state colours, three font roles, title size, spacing, radii, shadow |
| `dataviz` | yes | `--chart-1` to `--chart-4` (darkest first), `--chart-rest`, `--chart-axis` (axis and baseline), `--chart-grid`, `--chart-highlight` |
| `type` | no | Type scale, line heights, weights |
| `space-shape` | no | Extra spacing steps, radii, border width |
| `document` | no | Paper sheet roles and the `doc*` class vocabulary |
| `slide-frame` | no | Slide canvas roles and the slide class vocabulary |
| `print` | no | Printed page roles and the report class vocabulary |
| `brand` | no | `--brand-logo-on-light`, `--brand-logo-on-dark`, `--brand-mark` (CSS `url()` strings naming a package export path) and `--brand-legal` (a CSS string) |
| `guidance` | no | Written guidelines: one export path to a Markdown file or a folder |

Every role belongs to exactly one module. `type` and `space-shape` add roles and never redefine a `core` role. A module absent from a design system comes from the kit's neutral base theme (`shared/base/<module>.css`), which defines every role of every module. The class modules list a `classes` vocabulary: the class names the renderers emit for that concern, which the design may style.

## Manifest

A design system publishes `kit-manifest.json` in its package:

- `contractVersion`: SemVer of this contract (`2.0.0`), independent of the design system's own version.
- `provides`: module name to a package export path. `core` and `dataviz` are mandatory.
- `omitted`: module name to the reason it is not provided.
- `exceptions`: optional vocabulary of named local exceptions a document may declare, each with its reason.

Unknown keys and unknown module names are errors. The kit addresses files by the package's published export names (wildcard exports allowed), never by its internal folders. `shared/manifest_check.py` checks a manifest against the schema with the keywords the schema uses (`type`, `required`, `properties`, `additionalProperties`, `enum`, `const`, `pattern`); external tools such as `ajv` can use the schema directly.

## Rules

- **Fonts** are the `@font-face` rules of any provided module, with `url()` relative to that module's file.
- **Guidance** is informational: the kit lists it in the provenance report and does nothing else with it; agents may read it from the package.
- **Contrast**: `pairs` in `modules.json` lists the foreground and background roles whose WCAG AA contrast is checked. Text on a fill is a pair too: every fill a renderer paints text on (`--success`, `--info`, `--warning`, `--danger`, `--muted`, `--chart-1` to `--chart-3`) names the one text role used on it, `--ink` on `--success`, `--warning` and `--chart-3`, `--accent-ink` on the others, so a design whose fill fails its text role at AA is refused at resolve time.

## Shared files

`plugins/delivery-comms/shared/` and the two contract JSON files are canonical; `scripts/sync-shared.py` copies them into each renderer's `scripts/shared/` so every skill stays self-contained (`--check` fails when a copy differs). Run it in the same commit as any change under `shared/` or `contract/`.
