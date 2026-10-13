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

The three delivery-comms renderers (com-slide-deck, com-artefact-viz, com-release-note) theme themselves from one 24-token CSS file a project places at `docs/ux/tokens.css`, found three different ways, with fonts handled three different ways and no logo, legal line, chart palette, type scale or layout. A real design system carries much more: the reference implementation, a brand design system published on npm, has 173 tokens, a chart palette, document and slide CSS, logos, a legal line and written guidelines, and its 24-token kit export drops all of it. `ux-design-system` can only author the 24 tokens, and nothing checks a render against the design.

This plan makes the contract modular, so a renderer consumes a complete design system or a declared subset, and makes the design come from one pinned package instead of a copied file. Source: research 0004 (`docs/architecture/research/0004-design-systems-for-agents.md`) and the owner rulings of 2026-10-11 restated as design constraints below. No PRD. The design-system side (publishing the modules and the manifest) is the reference implementation's own plan; the first consumer migration is the consumer repository's own plan. Both depend on this one.

Principles:

1. One increment equals one coherent change set and one commit.
2. Every increment has an executable test gate, and its tests are written first and observed red (the `plan-implementation` skill's red-before-green rule); the iteration's `progress.txt` entry records the red run and the green run. Exemptions are named in Scope.
3. Python 3.12 or later, standard library plus PyYAML, which com-slide-deck already imports (`build.py`, `render.py`, `migrate.py`, `split.py`, `dev_server.py`). The PDF step keeps Playwright as its optional dependency. No JSON Schema library: the resolver checks a manifest with a small checker for the schema keywords the contract uses (Increment 02). Tests run with `python3 -m unittest`.
4. One implementation of each shared concern. Resolution, the base theme and the validator exist once, in `plugins/delivery-comms/shared/`, and `scripts/sync-shared.py` copies them into each skill so every skill stays self-contained; a test fails if a copy differs.
5. No silent legacy path. A legacy `docs/ux/tokens.css` (or the older `docs/design/tokens.css`) provides `core` only, so it is refused from the first 2.0.0 release (owner 2026-10-11, Q-1); the error names `ux-design-system point`, `ux-design-system subset` and `ux-design-system subset --from-legacy`. A project with no design source at all renders on the kit's base theme, which provides every module, and its provenance report says so.

**Overall Status:** pending (draft, owner review of the increments)
**Current Increment:** --

## Design constraints (owner rulings 2026-10-11, do not re-litigate in increments)

1. **Modules.** `core` (today's 24 roles), `dataviz`, `type`, `space-shape`, `document`, `slide-frame`, `print`, `brand`, `guidance`. A design system must provide `core` and `dataviz`; the other seven are optional and come from the kit's neutral base theme when absent. Every role belongs to exactly one module; `type` and `space-shape` add roles and never redefine a `core` role.
2. **Manifest.** A JSON file in the package, `kit-manifest.json`, in a format the kit owns and validates against the JSON Schema the kit ships: `contractVersion` (SemVer of the kit contract, independent of the design system's version; this plan defines `2.0.0`), `provides` (module to package export path), `omitted` (module to reason), optional `exceptions` vocabulary. Not the DTCG resolver.
3. **Pin.** A project declares its design system in `docs/ux/package.json` as an exact dependency version, so Dependabot proposes bumps. The kit reads the version from that file and downloads the tarball itself (no `npm install`, no `node_modules`), verifies npm's `dist.integrity`, and caches it per machine. A local folder path is accepted for previewing an unreleased design system.
4. **Package paths.** The kit addresses files by the package's published export names, never by its internal folders.
5. **Validator blocks.** After every render the kit checks the output against the rules of Increment 04: no literal colour outside the resolved design layers, no custom property outside the contract and the reserved `--kit-*` prefix, text contrast at WCAG AA for the contract's text pairs. A failure writes no output and exits non-zero with a message naming the value, its location and the role to use. A document may declare named local exceptions; each is listed in the render report. A skill may not report done without a passing run.
6. **Provenance report.** Every render prints, and writes next to its output as `<output>.provenance.json`, which modules came from the design system, which from the base, and which exceptions were used.
7. **Reproducible output.** The same source and the same design produce byte-identical HTML and PDF (closes #106).
8. **`ux-design-system`** gains `point` (write the pin, validate the manifest) and `subset` (author a DESIGN.md-style file with the modules the project can fill and an `omitted` list; generate module CSS and the manifest; propose a starting dataviz palette from the accent for the owner to confirm, contrast-checked). A complete design system from a template is out of scope ([#114](https://github.com/VictorHueni/homemade-claude-kit/issues/114)).

## Owner decisions (2026-10-11)

All eight questions were settled with the owner: Q-1 to Q-4 in prose, Q-5 to Q-8 after the peer review, from concrete examples.

- **Q-1. Legacy projects and the dataviz requirement.** A legacy `docs/ux/tokens.css` is refused immediately, with no transition release (Principle 5).
- **Q-2. Plugin version.** `delivery-comms` 2.0.0, a breaking change since legacy projects stop rendering until they move.
- **Q-3. Cache location.** `${XDG_CACHE_HOME:-~/.cache}/delivery-comms/design-systems/<name>@<version>/`, shared by every project on the machine, never inside a project.
- **Q-4. Network in CI.** A CI render downloads the pinned version from the npm registry when its cache is cold; workflows may cache the folder between runs. No offline mode until a project needs one.
- **Q-5. Viz domain colours.** Split by meaning. Status (shipped, planned, backlog) and pain keep the `core` state roles (`--success`, `--info`, `--warning`, `--danger`, `--muted`). Importance (differentiator, necessary, commodity) and confidence (validated, tested, assumed) are ordered scales and take `--chart-1` to `--chart-3`, darkest first. Red appears only where something is wrong.
- **Q-6. `guidance`.** Informational. The kit lists it in the provenance report and does nothing else with it; agents may read it from the package.
- **Q-7. Contrast check.** Both: once at resolve time, so a design whose own text pairs fail AA is refused once with one message, and again at render time for the pairs a document's local exceptions touch.
- **Q-8. Release order.** Increments 01 and 02 merge to `main`; they change no output. Increments 03 to 12 merge into a long-lived `release/2.0` branch, one PR each, and `release/2.0` merges to `main` as `delivery-comms` 2.0.0. No installed kit refuses a legacy file before `point` and `subset` exist.

## Increment Plan

### Increment 01: Test lane for delivery-comms

**Status:** pending

Scope:

1. **Exempt from red (characterisation):** `plugins/delivery-comms/tests/` with `unittest` cases that build one sample of each renderer with no project design and assert the HTML builds, links every CSS layer in today's order and contains the fallback accent: a deck scaffolded by `com-slide-deck/scripts/init.py` into a temporary folder, a view from `com-artefact-viz/examples/`, a release note from `com-release-note/examples/`. They pin today's behaviour before anything moves, so they pass on first run by design.
2. `plugins/delivery-comms/Makefile` with `test` (unit, no browser; fails fast with an install hint when Python is older than 3.12 or PyYAML is missing) and `test-pdf` (the PDF renders, skipped with a clear message when Playwright or Chromium is missing).
3. A GitHub Actions workflow on pull requests into `main` and `release/2.0` that touch `plugins/delivery-comms/`: `actions/setup-python` with 3.12, `pip install pyyaml`, then `make -C plugins/delivery-comms test`.

Primary files:

1. `plugins/delivery-comms/tests/`, `plugins/delivery-comms/Makefile`
2. `.github/workflows/delivery-comms.yml`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `./scripts/audit-skills.sh`

Exit criteria:

1. The suite runs green locally and in CI; a deliberately broken template line turns it red.

### Increment 02: Contract v2, manifest schema, one base theme and the shared sync

**Status:** pending

Scope:

1. **Write first, expect red:** `tests/test_contract.py` asserting:
   - (a) `contract/modules.json` declares `contractVersion` `2.0.0`, lists the nine modules with their roles, marks `core` and `dataviz` required, and no role appears in two modules;
   - (b) the class modules (`document`, `slide-frame`, `print`) list a `classes` vocabulary, and every class the three renderers' templates emit for those concerns is in it;
   - (c) `brand` lists `--brand-logo-on-light`, `--brand-logo-on-dark`, `--brand-mark` (CSS strings naming a package export path) and `--brand-legal` (a CSS string);
   - (d) `pairs` lists the text pairs the contrast check uses (`fg`, `bg`, `use`), each naming existing roles;
   - (e) the manifest checker accepts the three fixture manifests (full, subset, minimal) as structurally valid and rejects one missing `dataviz`, one with an unknown module, one with a non-SemVer `contractVersion` and one with an unknown key; the schema file uses only the keywords the checker implements;
   - (f) `shared/base/` defines every role of every module;
   - (g) after `scripts/sync-shared.py`, every skill's copy of `shared/` is byte-identical to the canonical one;
   - (h) the three skills no longer carry their own `tokens.fallback.css`, and their output is unchanged against the Increment 01 characterisation apart from `--font-heading`.
2. `plugins/delivery-comms/contract/`:
   - `modules.json` (contract version; per module: required flag, roles with a one-line purpose, `classes` for the class modules; `pairs`);
   - `kit-manifest.schema.json` (JSON Schema 2020-12, `$id` carrying `2.0.0`, restricted to `type`, `required`, `properties`, `additionalProperties`, `enum`, `const`, `pattern`), the specification for external tools such as `ajv`;
   - `README.md` (the contract in prose, replacing `ux-design-system/references/token-contract.md`, which becomes a pointer).
   - Rules written there: fonts are the `@font-face` rules of any provided module, with `url()` relative to that module's file; `guidance` maps to one export path (a Markdown file or a folder) and is informational (Q-6); `dataviz` roles are `--chart-1` to `--chart-4`, `--chart-rest`, `--chart-axis` (axis and baseline), `--chart-grid`, `--chart-highlight`.
3. `plugins/delivery-comms/shared/manifest_check.py`: the small checker for the keywords above.
4. `plugins/delivery-comms/shared/base/`: one neutral CSS file per module. `core` reproduces today's fallback values, with the `--font-heading` the slide and release-note copies lacked and without the `--font-sans` legacy alias. `dataviz` adds the chart roles.
5. `plugins/delivery-comms/scripts/sync-shared.py`, which copies `shared/` into each skill's `scripts/shared/`; each skill reads its base theme from that copy.
6. Test fixtures under `tests/fixtures/design-systems/`: `full/` (every module, a fictitious brand, a manifest with wildcard `exports`), `subset/` (`core` and `dataviz`), `minimal-invalid/` (`core` only).

Primary files:

1. `plugins/delivery-comms/contract/`, `plugins/delivery-comms/shared/base/`, `plugins/delivery-comms/shared/manifest_check.py`, `plugins/delivery-comms/scripts/sync-shared.py`
2. `plugins/delivery-comms/skills/ux-design-system/references/token-contract.md`
3. `plugins/delivery-comms/tests/test_contract.py`, `tests/fixtures/design-systems/`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. One contract at `2.0.0`, one base theme synced into each skill, three fixtures; the drifted fallback copies are gone.

### Increment 03: Shared design resolver

**Status:** pending

First increment on `release/2.0` (Q-8).

Scope:

1. **Write first, expect red:** `tests/test_resolver.py`, with `XDG_CACHE_HOME` and `DELIVERY_COMMS_NPM_REGISTRY` pointed at temporary values:
   - resolution order: explicit `--design-system` path, then the `docs/ux/package.json` pin found by walking up from the source at most 8 levels, then the base;
   - a legacy `docs/ux/tokens.css` or `docs/design/tokens.css` found the same way, with no pin, is refused with exit code 2 and a message naming `point`, `subset` and `subset --from-legacy`, even when a base render would be possible; with a pin present the pin wins and a warning names the legacy file to delete;
   - a pinned version is fetched from a local registry stub; its `sha512` integrity is checked (a tampered tarball is refused); it is extracted with the tar `data` filter (a path-traversal member is refused) into a temporary folder renamed into place, so a killed run leaves no half-written cache; a second resolve makes no request and re-checks the kept tarball's integrity;
   - export paths resolve through the package's `exports`, including a wildcard pattern (`./kit/*`);
   - a manifest the checker refuses, or one missing `core` or `dataviz`, is refused with the module named;
   - a design whose own `pairs` fail AA is refused at resolve time with the pair and its ratio (Q-7);
   - a local folder pin (`"file:../design-system"`) resolves without network;
   - the assembled CSS orders modules base first, then package, so a package value always wins;
   - the provenance report lists each module's source and marks `guidance` informational;
   - `design_source.py css --module core,dataviz` and `design_source.py fonts` print the expected CSS for the three fixtures, with font `url()`s inlined as data URIs.
2. `plugins/delivery-comms/shared/design_source.py`: `resolve(start_dir, explicit=None) -> Design` with the CSS per module, the font faces, the brand roles, the exceptions vocabulary and the provenance report. Registry access through `urllib.request` against `${DELIVERY_COMMS_NPM_REGISTRY:-https://registry.npmjs.org}/<name>/<version>` (a scoped name keeps its `@scope/` form); the cache per Q-3.
3. The command-line entry above, for generators outside the kit (a project's own build script), so a bespoke generator inlines the same design the kit renderers use.
4. `sync-shared.py` run; the byte-identity test covers the new file.

Primary files:

1. `plugins/delivery-comms/shared/design_source.py`
2. `plugins/delivery-comms/tests/test_resolver.py`, `tests/fixtures/registry/`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. One resolver, network-tested against a stub, with integrity, traversal, atomic-cache and resolve-time contrast checks.

### Increment 04: Blocking validator

**Status:** pending

Scope:

1. **Write first, expect red:** `tests/test_validator.py`:
   - a role-only test page passes against each of the three fixture designs;
   - a literal colour in a style attribute, in a `<style>` block and in an SVG `fill` each fails with file, line and the closest role suggested;
   - literals inside the resolved design layers the renderer inlined, and inside brand assets (inlined logo SVG, data URIs), pass;
   - a `var(--role, #hex)` fallback is stripped before the check, so it neither passes nor fails a page on its own;
   - an unknown `--name` fails; a `--kit-*` property whose value references only roles or non-colour values passes, and one carrying a literal colour fails;
   - a declared exception passes and appears in the report; the report notes whether the manifest's `exceptions` vocabulary knows the name, and an unknown name is not refused;
   - an exception that brings a `pairs` text pair below 4.5:1 fails (Q-7);
   - the check reads the resolved design, so the same HTML passes against one design and fails against another;
   - each skill's current template, with its `var()` fallbacks removed and its renderer-internal properties renamed to `--kit-*`, passes on the base theme (a dry run of what Increments 05 to 09 will do; expected red today).
2. `plugins/delivery-comms/shared/check_render.py`: parse the built HTML and its inlined CSS (stdlib `html.parser` and a small CSS tokenizer), check per constraint 5 and the rules above, return findings as JSON and as text. Exceptions are declared per artefact (deck `config.yaml` `design.exceptions`, viz and release-note `--exception NAME=VALUE`). A command-line entry `check_render.py <file.html> [--exception NAME=VALUE]...` checks any HTML file against the resolved design, for bespoke generators.
3. `sync-shared.py` run.

Primary files:

1. `plugins/delivery-comms/shared/check_render.py`
2. `plugins/delivery-comms/tests/test_validator.py`, `tests/fixtures/pages/`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. The validator catches each listed violation and passes the three fixture designs' role-only test pages. Real renders pass from Increments 05 to 09, as each renderer moves.

### Increment 05: com-slide-deck on the resolver and the validator

**Status:** pending

Scope:

1. **Write first, expect red:**
   - with the `full` fixture, the built deck links no Google Fonts URL and embeds the package fonts; with `subset` or the base and no design fonts, it uses the base system font stacks and makes no network request;
   - a deck whose `design/styles.css` hard-codes a contract colour fails the validator and writes nothing;
   - `config.yaml` `fonts:` is ignored with a warning when the design provides fonts;
   - the `paths.design_tokens` key accepts a folder with a manifest and refuses a single legacy token file like `docs/ux/tokens.css`;
   - `--recipient` and `page.footer_left` still work;
   - `<output>.provenance.json` is written next to the deck.
2. `build.py` and `render.py` call the resolver and the validator; the raw literals in `render.py` (`#fff`, `rgba(130,130,130,.95)`) become roles; the template's `var()` fallbacks go; `init.py` stops copying a palette into new decks; `migrate.py` reports hard-coded palette values against the resolved roles instead of the old token names.
3. The Increment 01 deck characterisation is updated for the dropped Google Fonts link, in the same commit.

Primary files:

1. `plugins/delivery-comms/skills/com-slide-deck/scripts/{build,render,init,migrate}.py`, its templates
2. `plugins/delivery-comms/tests/test_slide_deck.py`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `make -C plugins/delivery-comms test-pdf`

Exit criteria:

1. A deck renders from `full`, `subset` and the base and passes the validator; an off-brand deck is refused.

### Increment 06: com-slide-deck slide frame and brand

**Status:** pending

Scope:

1. **Write first, expect red:** with the `full` fixture, the deck uses the `slide-frame` module (canvas size, section label, footer row) and shows the logo and the legal line on every slide and the slide number at the right; with `subset`, it has no logo and no legal line and the report lists `slide-frame` and `brand` as base; the deck template emits only classes from the `slide-frame` vocabulary.
2. The deck template and `render.py` take the frame classes and the brand roles from the resolved design.

Primary files:

1. `plugins/delivery-comms/skills/com-slide-deck/templates/`, `scripts/render.py`
2. `plugins/delivery-comms/tests/test_slide_deck.py`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `make -C plugins/delivery-comms test-pdf`

Exit criteria:

1. A deck from `full` carries the frame, logo and legal line of the design; from `subset`, the neutral frame.

### Increment 07: com-artefact-viz domain colours on contract roles

**Status:** pending

Scope:

1. **Write first, expect red:** `templates/tokens.domain.css` defines only `--kit-*` properties; per Q-5, status (`--kit-status-shipped`, `-planned`, `-backlog`) and pain (`--kit-pain-critical` to `-low`) reference `--success`, `--info`, `--warning`, `--danger` and `--muted`; importance (`--kit-differentiator`, `--kit-necessary`, `--kit-commodity`) and confidence (`--kit-conf-validated`, `-tested`, `-assumed`) reference `--chart-1` to `--chart-3` in that order; the viz-internal properties (`--sb-lane-w`, `--viz-title-size`, `--token`) carry the `--kit-` prefix; the template has no `var()` fallback.
2. The renames in `tokens.domain.css`, `templates/` and `renderers.py`.

Primary files:

1. `plugins/delivery-comms/skills/com-artefact-viz/templates/`, `scripts/renderers.py`
2. `plugins/delivery-comms/tests/test_artefact_viz.py`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. Every colour the views draw traces to a contract role through one `--kit-*` property.

### Increment 08: com-artefact-viz on the resolver and the validator

**Status:** pending

Scope:

1. **Write first, expect red:**
   - each of the five view kinds (`capability-map`, `fbs`, `delivery-roadmap`, `bmc`, `service-blueprint`) renders its example from `com-artefact-viz/examples/` against the `full` fixture, the `subset` fixture and the base, and passes the validator (owner 2026-10-11: capability map, FBS and delivery roadmap must work on the new design system);
   - with `full`, the views embed the package fonts, and the importance and confidence legends read `--chart-1` to `--chart-3` in order;
   - run from a subfolder, the viz finds the project pin by walking up (today it only looks in the working directory);
   - a missing `--design-system` path is a clear error, not a traceback;
   - the footer date comes from the shared date source (`SOURCE_DATE_EPOCH`, else the last commit date of the source folder, else the newest source mtime), not `datetime.date.today()`;
   - `<output>.provenance.json` is written next to each view.
2. `render.py` and `renderers.py` use the resolver and the validator; `shared/source_date.py` provides the date source that Increment 10 reuses for PDFs.

Primary files:

1. `plugins/delivery-comms/skills/com-artefact-viz/scripts/{render,renderers}.py`
2. `plugins/delivery-comms/shared/source_date.py`, `plugins/delivery-comms/tests/test_artefact_viz.py`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. All five view kinds render against `full`, `subset` and the base and pass the validator.

### Increment 09: com-release-note on the resolver and the validator

**Status:** pending

Scope:

1. **Write first, expect red:** fonts come from the resolved design (no hard-coded `docs/ux/fonts/fonts.css`); with `full`, the PDF uses the `print` module (page size, margins), the logo and the legal line; `_resolve_token` reads the resolved values, so a `var()` token no longer falls back silently to defaults; `--font-report` is honoured only as a declared exception; the template has no `var()` fallback; the validator runs; `<output>.provenance.json` is written next to the HTML.
2. `render_pdf.py` uses the resolver and the validator.

Primary files:

1. `plugins/delivery-comms/skills/com-release-note/scripts/render_pdf.py`, `templates/`
2. `plugins/delivery-comms/tests/test_release_note.py`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `make -C plugins/delivery-comms test-pdf`

Exit criteria:

1. The example release note renders from `full`, `subset` and the base and passes the validator.

### Increment 10: Reproducible output (closes #106)

**Status:** pending

Scope:

1. **Write first, expect red:** two PDF renders of the same deck and release note, and two HTML renders of the same deck, view and release note, a minute apart, are byte-identical; the embedded date equals `SOURCE_DATE_EPOCH` when set, else the last commit date of the source folder, else the source files' newest mtime.
2. One shared post-processing step rewrites the PDF `CreationDate` and `ModDate` in place with a same-length value from `shared/source_date.py`, so the cross-reference table stays valid; `util-provenance` timestamps stop changing on idle rebuilds. If Chromium varies more than the two dates (the document `/ID`, XMP metadata), the red run names it and this increment normalises it the same way.

Primary files:

1. `plugins/delivery-comms/shared/pdf_dates.py`, the two PDF render scripts and the viz `render.py`
2. `plugins/delivery-comms/tests/test_reproducible.py`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `make -C plugins/delivery-comms test-pdf`

Exit criteria:

1. Re-rendering an unchanged source changes no byte.

### Increment 11: ux-design-system `point` and `subset`

**Status:** pending

Scope:

1. **Write first, expect red:**
   - `point @scope/name@x.y.z` writes `docs/ux/package.json` with the exact version, validates the package's manifest through the resolver, and prints the `.github/dependabot.yml` entry (`npm`, `directory: /docs/ux`) to add;
   - `subset docs/ux/DESIGN.md` reads YAML front matter (colours, typography, rounded, spacing) and prose sections, writes `docs/ux/design-system/` with one CSS file per filled module and `kit-manifest.json` with `omitted` taken from the file;
   - a source without dataviz gets a proposed palette (four steps from the accent towards the neutral, a remainder fill, an axis colour) written into the source as a block marked `proposed`, and generation refuses until the owner removes the mark;
   - contrast pairs below AA are refused;
   - `subset --from-legacy docs/ux/tokens.css` writes a draft `docs/ux/DESIGN.md` with `core` filled from the legacy file and a `proposed` dataviz block, and accepts `docs/design/tokens.css` the same way;
   - `scaffold` writes to `docs/ux/` (its documented path; today it writes `docs/design/`).
2. YAML front matter is parsed with PyYAML's safe loader; a key outside the subset DESIGN.md uses is an explicit error.
3. The old `generate` mode and its `refresh` alias are removed; running either prints the `subset` command that replaces it.

Primary files:

1. `plugins/delivery-comms/skills/ux-design-system/scripts/generate_tokens.py` (renamed `design_system.py`), `SKILL.md`, `templates/`
2. `plugins/delivery-comms/tests/test_ux_design_system.py`

Test gate:

1. `make -C plugins/delivery-comms test`

Exit criteria:

1. A small project goes from a DESIGN.md, or from a legacy token file, to a validated subset the three renderers accept, without hand-written CSS.

### Increment 12: Documentation and release 2.0.0

**Status:** pending

Scope:

1. **Exempt from red (documentation):** the four SKILL.md files describe the resolution order, the validator, the provenance report and the legacy migration; `contract/README.md` is linked from each; a five-line block for a project's `AGENTS.md` (pin file, manifest, validator command, Dependabot entry) goes in `ux-design-system/references/`.
2. Plugin version per Q-2 in `plugin.json` and the marketplace; skill `metadata.version` bumped where the skill changed.
3. `./scripts/audit-skills.sh` and the full suite green; `release/2.0` merged to `main` at the owner's request (Q-8); the marketplace refresh and `claude plugin update delivery-comms@<marketplace>` verified against the cache (`~/.claude/rules/claude-plugins-and-mcp.md`).

Primary files:

1. `plugins/delivery-comms/**/SKILL.md`, `plugins/delivery-comms/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
2. `plugins/delivery-comms/skills/ux-design-system/references/`

Test gate:

1. `make -C plugins/delivery-comms test`
2. `./scripts/audit-skills.sh`

Exit criteria:

1. The released plugin renders the three fixtures in a fresh session from the marketplace cache.

## Delivery Rules

1. Tests named in Scope are written first and observed failing before the implementation lands; `progress.txt` records the failing test names, then the green run. An increment whose tests were written after its code is not done.
2. Commit scope `delivery-comms`; types: `test` (01), `feat` (02 to 09, 11), `fix` (10), `docs` (12). Trailer `Refs: Plan-0005 increment NN`.
3. Branches per Q-8: Increments 01 and 02 open PRs into `main`; Increments 03 to 12 open PRs into `release/2.0`, cut from `main` after Increment 02 merges. `release/2.0` merges to `main` only in Increment 12, at the owner's request.
4. No real client material in fixtures: the `full` fixture is a fictitious brand, not a copy of any real design system.
5. Every increment that changes a file under `shared/` runs `sync-shared.py` in the same commit.
6. Foreground gates only; every iteration ends with a definitive state.

## Milestone Chunks (Standalone Delivery Groups)

| Milestone | Increments | Status | Coherent Outcome | Standalone Test Gate | Exit Criteria | Commit Guidance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| M1: Contract on main | 01-02 | pending | Test lane, contract 2.0.0, one synced base theme; no output change | `make -C plugins/delivery-comms test` | Characterisation green; fallback copies gone | `test(delivery-comms)`, `feat(delivery-comms)` |
| M2: Resolve and check | 03-04 | pending | Pinned designs resolve and renders are checked | `make -C plugins/delivery-comms test` | Stub registry, integrity and validator rules green | `feat(delivery-comms)`, PRs into `release/2.0` |
| M3: Renderers moved | 05-09 | pending | Deck, five views and release note render from the resolved design and pass the validator | `make -C plugins/delivery-comms test test-pdf` | All three fixtures render in every renderer | `feat(delivery-comms)`, PRs into `release/2.0` |
| M4: Reproducible | 10 | pending | Unchanged source, unchanged bytes | `make -C plugins/delivery-comms test test-pdf` | #106 closed | `fix(delivery-comms)` |
| M5: Authoring and release | 11-12 | pending | Projects can point, subset or migrate; 2.0.0 released | `make -C plugins/delivery-comms test`, `./scripts/audit-skills.sh` | 2.0.0 in the marketplace cache | `feat(delivery-comms)`, `docs(delivery-comms)` |
