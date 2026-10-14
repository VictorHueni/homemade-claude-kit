---
name: ux-design-system
license: MIT
description: "Point a project at the design system its decks, views and release notes render with, or author a declared subset of one. Modes: point (pin a published design-system package at an exact version in docs/ux/package.json, validate its kit manifest through the kit resolver, print the Dependabot entry), subset (read a DESIGN.md in Google's DESIGN.md format, write docs/ux/design-system/ with one CSS file per filled module and kit-manifest.json; propose a contrast-checked chart palette from the accent for the owner to confirm), subset --from-legacy (draft that DESIGN.md from a legacy docs/ux/tokens.css, which the 2.0 renderers refuse), scaffold (a DESIGN.md template). Use when the user wants a design system, brand tokens, theme, colour or chart palette, or typography for generated decks and views, or when a render refuses a legacy tokens.css. Triggers on: design system, design tokens, DESIGN.md, theme, colour palette, pin design system, migrate tokens.css. Output: docs/ux/. Mints no IDs."
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/design_system.py *)
user-invocable: true
metadata:
  category: "ux"
  complexity: "low"
  version: "1.0.0"
  status: active
  last_reviewed: 2026-10-14
  review_interval: 180d
  impact: "low"
---

# ux-design-system: the project's design source

The three delivery-comms renderers (`com-slide-deck`, `com-artefact-viz`, `com-release-note`) theme every output from one design, resolved once per render: an explicit `--design-system` folder, else the pin in `docs/ux/package.json` found by walking up from the working folder, else the kit's neutral base theme. The design is modular (contract `2.0.0`: `core` and `dataviz` required, seven optional modules); the contract is [`contract/README.md`](../../contract/README.md), the role list `contract/modules.json`. A legacy `docs/ux/tokens.css` (or `docs/design/tokens.css`) is refused by every renderer.

This skill gives a project its design in one of two ways:

- **`point`**: the project uses a published design-system package. The pin holds an exact version, so Dependabot proposes bumps.
- **`subset`**: the project has no design system of its own. The owner writes a DESIGN.md (a Google DESIGN.md) with the modules it can fill and a `kit.omitted` list; the skill generates the module CSS, the manifest and the pin.

It mints no IDs and links to no other artefact. A complete design system from a template is out of scope ([#114](https://github.com/VictorHueni/homemade-claude-kit/issues/114)).

## Quick reference

| Task | Command |
|---|---|
| Use a published design system | `python3 scripts/design_system.py point @scope/name@1.2.3` |
| Preview an unreleased design-system folder | `python3 scripts/design_system.py point ../design-system` |
| Start a DESIGN.md | `python3 scripts/design_system.py scaffold` (writes `docs/ux/DESIGN.md`) |
| Build the subset from a DESIGN.md | `python3 scripts/design_system.py subset docs/ux/DESIGN.md` |
| Migrate a refused legacy token file | `python3 scripts/design_system.py subset --from-legacy docs/ux/tokens.css` |

Every refusal exits 2 with a message naming what to change. `generate` and its `refresh` alias were removed in 2.0.0: running either exits 2 and prints the `subset` commands above.

Restricted sessions deny compound commands: run one plain command per Bash call and write files with the Write tool.

## Modes

### `point SPEC [--docs DOCS]`

`SPEC` is a package with an exact version (`@scope/name@1.2.3` or `name@1.2.3`; a range such as `^1.2.3` or a tag such as `latest` is refused) or a design-system folder.

1. A package is downloaded through the kit resolver (registry `${DELIVERY_COMMS_NPM_REGISTRY:-https://registry.npmjs.org}`, `dist.integrity` checked, cached under `${XDG_CACHE_HOME:-~/.cache}/delivery-comms/design-systems/`) and resolved: its `kit-manifest.json` against the schema, `core` and `dataviz` present, every export path present, the contract's text pairs at WCAG AA. A folder is resolved the same way, without the network.
2. Only then is `DOCS/ux/package.json` written: one dependency, the design system, at the exact version (or `file:<relative path>` for a folder). Other keys of an existing file are kept; a previous dependency is replaced.
3. For a package, it prints the `.github/dependabot.yml` entry (`package-ecosystem: "npm"`, `directory: "/docs/ux"`) for the owner to add. The skill never writes that file.

A folder pin is for previewing an unreleased design; pin a published version before sharing renders.

### `subset SRC`

`SRC` is a DESIGN.md: a [Google DESIGN.md](https://github.com/google-labs-code/design.md) (format `alpha`; spec in `docs/spec.md` there), YAML front matter (read with PyYAML's safe loader) then prose. The files the skill writes (template, scaffold, proposal, `--from-legacy` draft, `examples/DESIGN.sample.md`) pass Google's linter with no error and no warning (`make -C plugins/delivery-comms test-design-md`). The front matter keys are:

| Key | Holds |
|---|---|
| `name` | the design's name (the generated package is `<name>-design-subset`) |
| `colors` | the colour roles by contract name: `ink`, `muted`, `canvas-bg`, `surface`, `surface-2`, `border`, `accent`, `accent-ink`, `success`, `warning`, `danger`, `info` (`core`), and `chart-1` to `chart-4` (darkest first), `chart-rest`, `chart-axis`, `chart-grid`, `chart-highlight` (`dataviz`); hex only. `primary: "{colors.accent}"` keeps Google's primary colour on the accent. |
| `typography` | Google typography tokens, each an object (`fontFamily`, `fontSize`, `fontWeight`, `lineHeight`, ...); the mapping is below |
| `rounded` | `card-radius`, `btn-radius`, `node-radius` (`core`); `radius-sm`, `radius-pill` (`space-shape`) |
| `spacing` | `space-sm`, `space-md`, `space-lg`, `shell-max` (`core`); `space-xs`, `space-xl` (`space-shape`) |
| `kit` | the kit's extension key, for what Google DESIGN.md has no key for: `shadow` (`core`), `border-width` (`space-shape`), `fonts` (font faces: `family`, `src` a font file beside the DESIGN.md and never a URL, `weight`, `style`; their `@font-face` goes in `type` if filled, else `core`), `omitted` (optional module name to the reason it is not provided; the manifest's `omitted`) |
| `proposed` | the mark of an unreviewed chart palette: the chart colours `subset` proposed |

Typography mapping (token and property to contract role):

| Token | `fontFamily` | `fontSize` | `lineHeight` | `fontWeight` |
|---|---|---|---|---|
| `body` | `--font-body` | `--font-size-md` | `--line-height-body` | `--font-weight-regular` |
| `heading` | `--font-heading` | `--title-size` | `--line-height-tight` | `--font-weight-bold` |
| `mono` | `--font-mono` | | | |
| `text-xs`, `text-sm`, `text-lg`, `text-xl` | | `--font-size-xs`, `--font-size-sm`, `--font-size-lg`, `--font-size-xl` | | |

`body.fontFamily`, `heading.fontFamily`, `heading.fontSize` and `mono.fontFamily` are `core`; the other cells are the `type` module. Google's `rounded` takes px, rem or em only, so keep those units for the linter to pass.

Reading a Google DESIGN.md: keys and tokens the kit does not use (`version`, `description`, Google's `omitted` list, `components`, colours such as `primary` or `secondary`, typography tokens such as `h1`, properties such as `letterSpacing`) are skipped, listed in one printed note. The artefact front matter keys (`type`, `title`, `tags`, `timestamp`, `status`, `owner`, `last_reviewed`, `review_interval`) are ignored silently. A top-level key within two edits of a key the kit reads (`colours`) is an error naming the key it resembles, as are an unknown property inside a kit typography token and an unknown key under `kit`; the pre-Google keys `dataviz`, `elevation` and `fonts` are errors naming where their content goes.

Rules:

- `core` is required and filled whole; a missing role is named by its DESIGN.md path (`colors.accent`, `typography.heading.fontSize`, `kit.shadow`), with a skipped token it may be a typo of, and, when Google's `primary` is a hex colour and `accent` is missing, the `accent:` line to add. An optional module is filled whole or not at all; a module filled in part is an error naming the missing roles. A module both filled and in `kit.omitted` is an error.
- A value is one CSS value: `;`, `{`, `}`, `<`, `>` and comments are refused.
- **No chart colours**: the run writes a proposed palette at the end of `colors` and a top-level `proposed: [chart-1, ...]` line after it, and stops (exit 2) without generating anything. The mark is a YAML key, not a comment, because the safe loader drops comments; Google's linter ignores it. The proposal: `chart-1` to `chart-4` are four steps from `accent` towards `surface` (0, 25, 50 and 75 per cent, darkest first), each step moved further towards the surface until `accent-ink` or `ink` reaches AA on it; `chart-rest` (the remainder fill) is `muted` halfway towards `surface`; `chart-axis` is `muted`; `chart-grid` is `border`; `chart-highlight` is `warning`. Show it to the owner. Generation refuses while the `proposed:` line remains; only the owner removes it.
- The prose after the front matter becomes the `guidance` module (`guidance.md`), informational, unless `kit.omitted` lists `guidance`. Its `##` sections follow Google's order: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts.

Output, beside `SRC`: `design-system/` with `<module>.css` per filled module, `guidance.md`, `kit-manifest.json` (contract `2.0.0`, `provides`, `omitted` from the file) and a `package.json` naming the exports. The folder is written to a staging folder and resolved there by the kit resolver, the same rules a render applies (a contrast pair below AA is refused with the pair and its ratio; a fill passes when either text role reaches AA); a refused run leaves the previous `design-system/` untouched. Then, when `docs/ux/package.json` does not exist, it is written as `file:design-system`, so every renderer finds the subset; a project already pinned to another design keeps that pin, and the run prints the `point` command that switches.

The generated CSS is a machine artefact: change the DESIGN.md and run `subset` again.

### `subset --from-legacy TOKENS`

`TOKENS` is a legacy `docs/ux/tokens.css` or `docs/design/tokens.css`. Writes a draft `docs/ux/DESIGN.md` (never overwriting one) with:

- every `core` role found in the file, `var()` references to another property of the file followed to their value, and the legacy `--font-sans` alias taken as `font-body`;
- each `core` role the file lacks taken from the kit base theme, and named by its DESIGN.md path in the output and in a comment;
- `primary: "{colors.accent}"`, proposed chart colours under the `proposed` mark (see `subset`), and `guidance` in `kit.omitted`.

It prints what it could not map: properties that are not contract roles (deck-only names such as `--dim`, domain names such as `--status-shipped`), colours that are not hex (subset refuses them until changed), and `@font-face` or `@import` rules (fonts move to `kit.fonts` with a local file). It leaves `TOKENS` unedited; delete it once the subset renders, since a render with both a pin and a legacy file prints a warning.

### `scaffold [DOCS]`

Creates `DOCS/ux/DESIGN.md` (default `docs/ux/DESIGN.md`) from `templates/DESIGN.template.md`: neutral `core` values, every optional module in `kit.omitted`, prose sections to fill, no chart colours (the first `subset` run proposes them). An existing file is kept. `owner` comes from `git config user.name`.

## Operating sequence

1. **A published design system exists**: `point` it, add the printed Dependabot entry, done.
2. **No design system**: `scaffold` (or `subset --from-legacy` when a refused `tokens.css` exists), fill the values and the prose with the owner, run `subset`, show the proposed chart palette to the owner, and run `subset` again once the owner has removed the `proposed:` line.
3. Render with any of the three skills. Each prints and writes `<output>.provenance.json` naming which modules came from the design and which from the base, and validates the output before writing it.

Do not hand-write CSS to get around a refusal, and do not edit `design-system/` by hand.

## Verification checklist

1. [ ] `docs/ux/package.json` pins exactly one design system: an exact version, or `file:design-system` for a subset.
2. [ ] `point` or `subset` exited 0; no `proposed:` line is left in the DESIGN.md.
3. [ ] `kit.omitted` gives a reason for every optional module the project does not fill.
4. [ ] A render's provenance lists `core` and `dataviz` from the design system, and its validator verdict is PASS.
5. [ ] No legacy `tokens.css` is left in `docs/ux/` or `docs/design/`.

## See also

- [`contract/README.md`](../../contract/README.md): modules, manifest, contrast pairs, fonts.
- `references/discipline.md`: principles and boundaries.
- `examples/DESIGN.sample.md` (a filled DESIGN.md) and `examples/legacy.tokens.css` (a legacy file to try `--from-legacy` on; its accent is refused for contrast).
- `com-slide-deck`, `com-artefact-viz`, `com-release-note`: the renderers.
