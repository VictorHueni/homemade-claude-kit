---
type: Implementation Plan
title: Plan-0005 — modular design contract for delivery-comms (full design system or subset)
description: Replaces the 24-token docs/ux/tokens.css contract of delivery-comms with a modular contract (required core and dataviz, seven optional modules) declared by a manifest, resolved once per render from a pinned design-system package or a local folder (a legacy token file is refused), checked after every render with a blocking validator, and authored for small projects by ux-design-system as a declared subset.
tags: [delivery-comms, design-system, tokens, com-slide-deck, com-artefact-viz, com-release-note, ux-design-system]
timestamp: 2026-10-11T18:00:00+02:00
status: draft
owner: Victor Hueni
last_reviewed: 2026-10-11
review_interval: 30d
---

# Implementation Plan: modular design contract for delivery-comms

## Summary

The three delivery-comms renderers (com-slide-deck, com-artefact-viz, com-release-note) theme themselves from one 24-token CSS file a project places at `docs/ux/tokens.css`, found three different ways, with fonts handled three different ways and no logo, legal line, chart palette, type scale or layout. A real design system carries much more: the reference implementation, `@medquantis/design-system` on npm, has 173 tokens, a chart palette, document and slide CSS, logos, a legal line and written guidelines, and its 24-token kit export drops all of it. `ux-design-system` can only author the 24 tokens, and nothing checks a render against the design.

This plan makes the contract modular, so a renderer consumes a complete design system or a declared subset, and makes the design come from one pinned package instead of a copied file. Source: research 0004 (`docs/architecture/research/0004-design-systems-for-agents.md`) and the owner rulings of 2026-10-11 restated as design constraints below. No PRD. The design-system side (publishing the modules and the manifest) is the reference implementation's own plan; the first consumer migration is the consumer repository's own plan. Both depend on this one.

Principles:

1. One increment equals one coherent change set and one commit.
2. Every increment has an executable test gate, and its tests are written first and observed red (`~/.claude/rules/plans-are-tdd.md`); the iteration's `progress.txt` entry records the red run and the green run. Exemptions are named in Scope.
3. Stdlib only. The renderers and the resolver stay Python 3 standard library; the PDF step keeps Playwright as its optional dependency. Tests run with `python3 -m unittest`, so no new tool needs a dotfiles entry.
4. One implementation of each shared concern. Resolution, the base theme and the validator exist once, in `plugins/delivery-comms/shared/`, and are synced into each skill's `scripts/` so every skill stays self-contained; a test fails if a copy differs.
5. No silent legacy path. A legacy `docs/ux/tokens.css` provides `core` only, so it is refused from the first release of this plan (owner 2026-10-11, Q-1); the error names the two ways forward, `ux-design-system point` and `ux-design-system subset`. A project with no design source at all renders on the kit's base theme, which provides every module, and its provenance report says so.

**Overall Status:** pending (draft, owner review of the increments)
**Current Increment:** --

## Design constraints (owner rulings 2026-10-11, do not re-litigate in increments)

1. **Modules.** `core` (today's 24 roles), `dataviz`, `type`, `space-shape`, `document`, `slide-frame`, `print`, `brand`, `guidance`. A design system must provide `core` and `dataviz`; the other seven are optional and come from the kit's neutral base theme when absent.
2. **Manifest.** A JSON file in the package, `kit-manifest.json`, in a format the kit owns and validates with a JSON Schema the kit ships: `contractVersion` (SemVer of the kit contract, independent of the design system's version), `provides` (module to package export path), `omitted` (module to reason), optional `exceptions` vocabulary. Not the DTCG resolver.
3. **Pin.** A project declares its design system in `docs/ux/package.json` as an exact dependency version, so Dependabot proposes bumps. The kit reads the version from that file and downloads the tarball itself (no `npm install`, no `node_modules`), verifies npm's `dist.integrity`, and caches it per machine. A local folder path is accepted for previewing an unreleased design system.
4. **Package paths.** The kit addresses files by the package's published export names, never by its internal folders.
5. **Validator blocks.** After every render the kit checks the output: no literal colour outside the resolved roles, no custom property outside the contract, text contrast at WCAG AA for the contract's text pairs. A failure writes no output and exits non-zero with a message naming the value, its location and the role to use. A document may declare named local exceptions; each is listed in the render report. A skill may not report done without a passing run.
6. **Provenance report.** Every render prints, and writes next to its output, which modules came from the design system, which from the base, and which exceptions were used.
7. **Reproducible output.** The same source and the same design produce byte-identical HTML and PDF (closes #106).
8. **`ux-design-system`** gains `point` (write the pin, validate the manifest) and `subset` (author a DESIGN.md-style file with the modules the project can fill and an `omitted` list; generate module CSS and the manifest; propose a starting dataviz palette from the accent for the owner to confirm, contrast-checked). A complete design system from a template is out of scope ([#114](https://github.com/VictorHueni/homemade-claude-kit/issues/114)).

## Owner decisions (2026-10-11)

All four questions were settled in prose with the owner.

- **Q-1. Legacy projects and the dataviz requirement.** Decided 2026-10-11: a legacy `docs/ux/tokens.css` is refused immediately, with no transition release (Principle 5).
- **Q-2. Plugin version.** Decided 2026-10-11: `delivery-comms` 2.0.0, a breaking change since legacy projects stop rendering until they move.
- **Q-3. Cache location.** Decided 2026-10-11: `${XDG_CACHE_HOME:-~/.cache}/delivery-comms/design-systems/<name>@<version>/`, shared by every project on the machine, never inside a project.
- **Q-4. Network in CI.** Decided 2026-10-11: a CI render downloads the pinned version from the npm registry when its cache is cold; workflows may cache the folder between runs. No offline mode until a project needs one.

## Increment Plan

### Increment 01: Test lane for delivery-comms

**Status:** pending

Scope:

1. **Exempt from red (characterisation):** `plugins/delivery-comms/tests/` with `unittest` cases that build one sample of each renderer from the existing examples (a deck from the com-slide-deck template, `com-artefact-viz/examples/`, `com-release-note/examples/`) with no project design and assert the HTML builds, links every CSS layer in today's order and contains the fallback accent. They pin today's behaviour before anything moves, so they pass on first run by design.
2. `plugins/delivery-comms/Makefile` with `test` (unit, no browser) and `test-pdf` (the PDF renders, skipped with a clear message when Playwright or Chromium is missing).
3. A GitHub Actions workflow running `make -C plugins/delivery-comms test` on pull requests that touch `plugins/delivery-comms/`.

Primary files:

1. `plugins/delivery-comms/tests/`, `plugins/delivery-comms/Makefile`
2. `.github/workflows/delivery-comms.yml`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `./scripts/audit-skills.sh`

Exit criteria:

1. The suite runs green locally and in CI; a deliberately broken template line turns it red.

### Increment 02: Contract v2, manifest schema and one base theme

**Status:** pending

Scope:

1. **Write first, expect red:** tests asserting (a) `contract/modules.json` lists the nine modules with their required roles and marks `core` and `dataviz` required; (b) `contract/kit-manifest.schema.json` accepts the three fixture manifests (full, subset, minimal) and rejects one missing `dataviz`, one with an unknown module and one with a non-SemVer `contractVersion`; (c) `shared/base/` defines every role of every module; (d) the three skills no longer carry their own `tokens.fallback.css` and their output is unchanged against the increment 01 characterisation.
2. `plugins/delivery-comms/contract/`: `modules.json` (module, required flag, role names, one-line purpose per role), `kit-manifest.schema.json` (JSON Schema 2020-12, `$id` carrying the contract version), `README.md` (the contract in prose, replacing `ux-design-system/references/token-contract.md`, which becomes a pointer).
3. `plugins/delivery-comms/shared/base/`: one neutral CSS file per module. `core` reproduces today's fallback values (with the `--font-heading` the slide and release-note copies lacked); `dataviz` adds `--chart-1` to `--chart-4`, `--chart-rest`, `--chart-axis`, `--chart-grid`, `--chart-highlight`.
4. Test fixtures under `tests/fixtures/design-systems/`: `full/` (every module, manifest), `subset/` (`core` and `dataviz`), `minimal-invalid/` (`core` only).

Primary files:

1. `plugins/delivery-comms/contract/`, `plugins/delivery-comms/shared/base/`
2. `plugins/delivery-comms/tests/test_contract.py`, `tests/fixtures/design-systems/`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. One contract, one base theme, three fixtures; the drifted fallback copies are gone.

### Increment 03: Shared design resolver

**Status:** pending

Scope:

1. **Write first, expect red:** `tests/test_resolver.py`: resolution order (explicit `--design-system` path, then `docs/ux/package.json` pin found by walking up from the source at most 8 levels, then the base); a legacy `docs/ux/tokens.css` found the same way is refused with exit code 2 and a message naming `ux-design-system point` and `ux-design-system subset`, even when a base render would be possible; a pinned version is fetched from a local registry stub, its `sha512` integrity checked (a tampered tarball is refused), extracted with the tar `data` filter (a path-traversal member is refused) and cached (a second resolve makes no request); a manifest failing the schema, or missing `core` or `dataviz`, is refused with the module named; a local folder pin (`"file:../design-system"`) resolves without network; the assembled CSS orders modules base first, then package, so a package value always wins; the provenance report lists each module's source.
2. `plugins/delivery-comms/shared/design_source.py`: `resolve(start_dir, explicit=None) -> Design` with the CSS per module, font files, logo paths, the legal line, the exceptions vocabulary and the provenance report. Registry access through `urllib.request` against `https://registry.npmjs.org/<name>/<version>`; the cache per Q-3.
3. `plugins/delivery-comms/scripts/sync-shared.py` and a test asserting every skill's copy of `shared/` is byte-identical to the canonical one.
4. A command-line entry for generators outside the kit (a project's own build script): `design_source.py css --module core,dataviz` prints the assembled CSS of the resolved design, and `design_source.py fonts` prints the font-face CSS, so a bespoke generator inlines the same design the kit renderers use. Tested with the three fixtures.

Primary files:

1. `plugins/delivery-comms/shared/design_source.py`, `plugins/delivery-comms/scripts/sync-shared.py`
2. `plugins/delivery-comms/tests/test_resolver.py`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. One resolver, network-tested against a stub, with integrity and traversal checks.

### Increment 04: Blocking validator

**Status:** pending

Scope:

1. **Write first, expect red:** `tests/test_validator.py`: a render using only roles passes; a literal colour in a style attribute, in a `<style>` block and in an SVG `fill` each fails with file, line and the closest role suggested; an unknown `--name` fails; a declared exception passes and appears in the report; an ink-on-canvas pair below 4.5:1 fails; the check reads the resolved design, so the same HTML passes against one design and fails against another.
2. `plugins/delivery-comms/shared/check_render.py`: parse the built HTML and its inlined CSS (stdlib `html.parser` and a small CSS tokenizer), check per constraint 5, return findings as JSON and as text. Exceptions are declared per artefact (deck `config.yaml` `design.exceptions`, viz and release-note `--exception NAME=VALUE`). A command-line entry `check_render.py <file.html> [--exception NAME=VALUE]...` checks any HTML file against the resolved design, for bespoke generators.

Primary files:

1. `plugins/delivery-comms/shared/check_render.py`
2. `plugins/delivery-comms/tests/test_validator.py`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. The validator catches each listed violation and passes every fixture render.

### Increment 05: com-slide-deck on the resolver

**Status:** pending

Scope:

1. **Write first, expect red:** with the `full` fixture, the built deck links no Google Fonts URL, embeds the package fonts, uses the slide frame (canvas size, section label, footer row), shows the logo and the legal line on every slide and the slide number at the right; with `subset`, it has no logo and no legal line and the report lists them as base; a deck whose `design/styles.css` hard-codes a contract colour fails the validator and writes nothing; `config.yaml` `fonts:` is ignored with a warning when the design provides fonts; `--recipient` and `page.footer_left` still work.
2. `build.py` and `render.py` call the resolver and the validator; `init.py` stops copying a palette into new decks; `migrate.py` reports hard-coded palette values against the resolved roles instead of the old token names.
3. The `paths.design_tokens` key is read as an explicit design source: a folder with a manifest is accepted, a single legacy token file is refused like `docs/ux/tokens.css`.

Primary files:

1. `plugins/delivery-comms/skills/com-slide-deck/scripts/{build,render,init,migrate}.py`, its templates
2. `plugins/delivery-comms/tests/test_slide_deck.py`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `make -C plugins/delivery-comms test-pdf`

Exit criteria:

1. A deck renders on-brand from the `full` fixture and cleanly from `subset`, and an off-brand deck is refused.

### Increment 06: com-artefact-viz on the resolver

**Status:** pending

Scope:

1. **Write first, expect red:** each of the five view kinds (`capability-map`, `fbs`, `delivery-roadmap`, `bmc`, `service-blueprint`) renders its example from `com-artefact-viz/examples/` against the `full` fixture and the `subset` fixture, passes the validator, and draws its marks only from contract roles (owner 2026-10-11: capability map, FBS and delivery roadmap must work on the new design system); run from a subfolder, the viz finds the project pin by walking up (today it only looks in the working directory); with `full`, the views embed the package fonts and draw series in `--chart-1` to `--chart-4` order with `--chart-rest` for remainders; `templates/tokens.domain.css` derives its status, pain and confidence tokens from the dataviz and core roles; a missing `--design-system` path is a clear error, not a traceback; the validator runs.
2. `render.py` and `renderers.py` use the resolver and the validator; the dark theme of a view, where one exists, is a declared exception set.

Primary files:

1. `plugins/delivery-comms/skills/com-artefact-viz/scripts/{render,renderers}.py`, `templates/`
2. `plugins/delivery-comms/tests/test_artefact_viz.py`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. All five view kinds render against `full` and `subset` and pass the validator.

### Increment 07: com-release-note on the resolver

**Status:** pending

Scope:

1. **Write first, expect red:** fonts come from the resolved design (no hard-coded `docs/ux/fonts/fonts.css`); with `full`, the PDF uses the print module (page size, margins), the logo and the legal line; `_resolve_token` reads the resolved values, so a `var()` token no longer falls back silently to defaults; `--font-report` is honoured only as a declared exception; the validator runs.
2. `render_pdf.py` uses the resolver and the validator.

Primary files:

1. `plugins/delivery-comms/skills/com-release-note/scripts/render_pdf.py`, `templates/`
2. `plugins/delivery-comms/tests/test_release_note.py`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `make -C plugins/delivery-comms test-pdf`

Exit criteria:

1. The example release note renders from `full` and `subset` and passes the validator.

### Increment 08: Reproducible PDFs (closes #106)

**Status:** pending

Scope:

1. **Write first, expect red:** two PDF renders of the same deck, release note and view, a minute apart, are byte-identical; the embedded date equals `SOURCE_DATE_EPOCH` when set, else the last commit date of the source folder, else the source files' newest mtime.
2. One shared post-processing step rewrites the PDF `CreationDate` and `ModDate` in place with a same-length value, so the cross-reference table stays valid; `util-provenance` timestamps stop changing on idle rebuilds.

Primary files:

1. `plugins/delivery-comms/shared/pdf_dates.py` and the three render scripts
2. `plugins/delivery-comms/tests/test_reproducible_pdf.py`

Test gate:

1. `make -C plugins/delivery-comms test-pdf`

Exit criteria:

1. Re-rendering an unchanged source changes no byte.

### Increment 09: ux-design-system `point` and `subset`

**Status:** pending

Scope:

1. **Write first, expect red:** `point @scope/name@x.y.z` writes `docs/ux/package.json` with the exact version and validates the package's manifest through the resolver; `subset docs/ux/DESIGN.md` reads YAML front matter (colours, typography, rounded, spacing) and prose sections, writes `docs/ux/design-system/` with one CSS file per filled module and `kit-manifest.json` with `omitted` taken from the file; a source without dataviz gets a proposed palette (four steps from the accent towards the neutral, a remainder fill, an axis colour) written into the source as a block marked `proposed`, and generation refuses until the owner removes the mark; contrast pairs below AA are refused; `scaffold` writes to `docs/ux/` (its documented path; today it writes `docs/design/`).
2. YAML front matter is parsed with a small stdlib reader for the flat subset DESIGN.md uses; anything else is an explicit error.
3. The old `generate` mode is removed; running it prints the `subset` command that replaces it.

Primary files:

1. `plugins/delivery-comms/skills/ux-design-system/scripts/generate_tokens.py` (renamed `design_system.py`), `SKILL.md`, `templates/`
2. `plugins/delivery-comms/tests/test_ux_design_system.py`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. A small project goes from a DESIGN.md to a validated subset the three renderers accept, without hand-written CSS.

### Increment 10: Documentation and release

**Status:** pending

Scope:

1. **Exempt from red (documentation):** the four SKILL.md files describe the resolution order, the validator and the provenance report; `contract/README.md` is linked from each; a five-line block for a project's `AGENTS.md` (pin file, manifest, validator command) goes in `ux-design-system/references/`; research 0004 is committed.
2. Plugin version per Q-2 in `plugin.json` and the marketplace; skill `metadata.version` bumped where the skill changed.
3. `./scripts/audit-skills.sh` and the full suite green; the marketplace refresh and `claude plugin update delivery-comms@<marketplace>` verified against the cache (`~/.claude/rules/claude-code-plugin-marketplace-refresh.md`).

Primary files:

1. `plugins/delivery-comms/**/SKILL.md`, `plugins/delivery-comms/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
2. `docs/architecture/research/0004-design-systems-for-agents.md`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `./scripts/audit-skills.sh`

Exit criteria:

1. The released plugin renders the three fixtures in a fresh session from the marketplace cache.

## Delivery rules

1. Tests named in Scope are written first and observed failing before the implementation lands; `progress.txt` records the failing test names, then the green run. An increment whose tests were written after its code is not done.
2. Commit scope `delivery-comms`; types: `test` (01), `feat` (02 to 07, 09), `fix` (08), `docs` (10). Trailer `Refs: Plan-0005 increment NN`.
3. No real client material in fixtures: the `full` fixture is a fictitious brand, not a copy of any real design system.
4. Foreground gates only; every iteration ends with a definitive state.
