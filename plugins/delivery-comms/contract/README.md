# delivery-comms design contract 2.1.0

What a design system gives the three renderers (`com-slide-deck`, `com-artefact-viz`, `com-release-note`). It replaces the single 24-token `docs/ux/tokens.css` file. The role list per module is `modules.json`; the manifest format is `kit-manifest.schema.json`. This README is the prose; where they disagree, the JSON wins and this file is wrong.

## Modules

| Module | Required | Holds |
|---|---|---|
| `core` | yes | The 24 roles of the old contract: palette, state colours, three font roles, title size, spacing, radii, shadow; plus `--tertiary`, the optional text role for footers, legal lines and slide numbers, which defaults to `--muted` |
| `dataviz` | yes | `--chart-1` to `--chart-4` (darkest first), `--chart-rest`, `--chart-axis` (axis and baseline), `--chart-grid`, `--chart-highlight` |
| `type` | no | Type scale, line heights, weights |
| `space-shape` | no | Extra spacing steps, radii, border width |
| `document` | no | Paper sheet roles and the `doc*` class vocabulary |
| `slide-frame` | no | Slide canvas roles and the slide class vocabulary |
| `dark` | no | `--dark-<role>`, the dark twin of every colour role of `core`, `dataviz`, `slide-frame`, `document` and `print`; plus `--dark-key-fill`, `--dark-key-base`, `--dark-key-edge` and `--dark-accent-text`; the `dark`, `dark-key` and `dark-accent` classes |
| `print` | no | Printed page roles and the report class vocabulary; plus `--print-breaking`, the optional accent for breaking changes in printed reports, which defaults to `--danger` |
| `brand` | no | `--brand-logo-on-light`, `--brand-logo-on-dark`, `--brand-mark` (CSS `url()` strings naming a package export path) and `--brand-legal` (a CSS string) |
| `guidance` | no | Written guidelines: one export path to a Markdown file |

Every role belongs to exactly one module. A module declares its roles on `:root` only: the resolver refuses a role declared under any other selector, which would replace that role for the whole render. `type` and `space-shape` add roles and never redefine a `core` role. A module absent from a design system comes from the kit's neutral base theme (`shared/base/<module>.css`), which defines every role of every module. The class modules list a `classes` vocabulary: the class names the renderers emit for that concern, which the design may style.

## Manifest

A design system publishes `kit-manifest.json` in its package:

- `contractVersion`: SemVer of this contract (`2.1.0`), independent of the design system's own version. A kit reads every manifest of its major up to its own minor: a 2.0 manifest resolves under 2.1, and a manifest at a newer minor is refused with the kit version to install.
- `provides`: module name to a package export path. `core` and `dataviz` are mandatory.
- `omitted`: module name to the reason it is not provided.
- `exceptions`: optional vocabulary of named local exceptions a document may declare, each with its reason.

Unknown keys and unknown module names are errors. The kit addresses files by the package's published export names (wildcard exports allowed), never by its internal folders. `shared/manifest_check.py` checks a manifest against the schema with the keywords the schema uses (`type`, `required`, `properties`, `additionalProperties`, `enum`, `const`, `pattern`); external tools such as `ajv` can use the schema directly.

## Rules

- **Fonts** are the `@font-face` rules of any provided module, with `url()` relative to that module's file.
- **Guidance** is informational: the kit lists it in the provenance report and does nothing else with it; agents may read it from the package.
- **Contrast**: `pairs` in `modules.json` lists the foreground and background roles whose WCAG AA contrast is checked, once when the design is resolved (a design whose own pairs fail is refused) and again when a document's exception touches a pair. A pair's `fg` is one role, or a list of roles for text on a fill: every fill a renderer paints text on (`--success`, `--info`, `--warning`, `--danger`, `--muted`, `--chart-1` to `--chart-3`) takes `["--accent-ink", "--ink"]`. A list pair passes when any of its roles reaches AA on the fill, so a design may use dark fills with light text or light fills with dark text; it is refused only when no role does, and the message names every role tried with its ratio.
- **Text on a fill** (`--kit-on-*`): for each list pair the resolver declares `--kit-on-<fill>` (the fill's name without its leading dashes, such as `--kit-on-success` or `--kit-on-chart-1`) as `var(<role>)`, the first role in list order that reaches AA on that fill, or the first role of the list when a value is not a hex colour and contrast cannot be computed. The declaration sits in a `:root` block at the end of the CSS of the module that owns the fill (`core` for the state roles, `dataviz` for the chart roles), so `design_source.py css` prints it and every renderer that inlines the design gets it. Renderers paint text on a fill with `var(--kit-on-<fill>)`, never with a fixed `--ink` or `--accent-ink`. The `--kit-*` prefix is reserved for these and other renderer-owned properties; a design system themes the roles, not them.

## Dark

The `dark` module mirrors the colour roles mechanically. `mirror` in `modules.json` names the mirrored modules and the roles they hold that are not colours (`except`); every other role `--x` of those modules has the twin `--dark-x`, so a colour role added later to a mirrored module gets its twin by the same rule. Four roles have no light counterpart: `--dark-key-fill` (the fill of a dark slide's key element, a colour or a gradient), `--dark-key-base` (a solid colour no lighter than the fill's lightest point, the background of the key element's text pair), `--dark-key-edge` (its outline, a shadow value) and `--dark-accent-text` (highlighted text).

A design that provides `dark` declares at least the roles in `requiredRoles` (canvas-bg, surface, border, ink, muted, accent, accent-ink, slide-bg, slide-fg as `--dark-*`); every other dark role takes its value from the base `dark.css`, which holds literals only, never an alias to a light role. The module's `pairs` mirror every light pair onto the dark roles, plus `--dark-ink` on `--dark-key-base` and `--dark-accent-text` on `--dark-canvas-bg` and `--dark-surface`; the resolver checks them like the light pairs, whether the dark roles come from the design or the base.

The module CSS declares the `--dark-*` roles on `:root`; the renderer, never the module, remaps `--x: var(--dark-x)` on a slide or page marked dark, and chooses each `--kit-on-<fill>` again against the dark pairs.

The classes: `dark` marks a slide (on a partial's root `.slide`) or, with `theme: dark` in a deck's `config.yaml`, every slide or document page; `dark-key` is the one key element of a dark slide (fill `--dark-key-fill`, outline `--dark-key-edge`, text checked on `--dark-key-base`); `dark-accent` is highlighted text (`--dark-accent-text`). A deck never declares a `--dark-*` role itself.

A design that provides `dark` declares `contractVersion` `2.1.0` and needs delivery-comms 2.1.0 or later (a 2.0 kit refuses the unknown module). A design that omits it gets the base `dark.css`; a subset generated from a DESIGN.md always omits it in 2.1.

## Shared files

`plugins/delivery-comms/shared/` and the two contract JSON files are canonical; `scripts/sync-shared.py` copies them into each renderer's `scripts/shared/` so every skill stays self-contained (`--check` fails when a copy differs). Run it in the same commit as any change under `shared/` or `contract/`.
