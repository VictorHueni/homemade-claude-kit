---
type: Implementation Plan
title: "Plan-0006: dark slides and a deck classification for delivery-comms (2.1.0)"
description: Adds an optional dark module to the modular design contract, so a slide marked dark switches every core role to the design's dark roles instead of declaring a deck-local dark palette, and a per-deck data classification (Public, Internal, Confidential, Strictly confidential) that com-slide-deck prints in the footer row next to the design's legal line; released as delivery-comms 2.1.0, contract 2.1.0.
tags: [delivery-comms, design-system, com-slide-deck, contract, dark-theme, classification]
timestamp: 2026-10-15T19:30:00+02:00
status: draft
owner: Victor Hueni
last_reviewed: 2026-10-15
review_interval: 30d
---

# Implementation Plan: dark slides and a deck classification

## Summary

Kit 2.0.0 (Plan-0005) renders decks from a pinned design system and refuses every custom property that is not a contract role. Two needs surfaced when the first real consumer planned its migration (Paracel Plan 0190, Q-17 and Q-19, owner decisions of 2026-10-15):

1. **Dark slides.** Paracel's six decks have dark section slides drawn with a deck-local palette (`--dark-bg`, `--dark-surface`, `--dark-text` and others). Under 2.0 each deck would copy the same literals into its exceptions, and nothing in the contract lets a slide switch roles: mapping the dark surface alone left accent text, icon fills and meters invisible until every core role was switched too. This plan adds an optional `dark` module: a design names its dark roles once, and a slide that carries the `dark` class gets every core role remapped by the kit's frame.
2. **Classification.** Kit 2.0.0 builds the slide footer itself (`build.py` `slide_footer`: logo, legal line, number) and strips any deck footer (`OLD_FOOTER`), so a deck can no longer print its own "Confidential" marking. This plan adds `classification:` to `config.yaml`, printed in the footer row on every slide and page, on the four-level scheme used with GDPR and the Swiss nFADP.

Both are additive and optional: contract 2.1.0 (same major, so every 2.0 manifest still resolves, `design_source.py` compares the major only), plugin 2.1.0. The first design to provide `dark` is `@medquantis/design-system` 1.2.0 (its own Plan 0003), whose values start from the dark slide the owner chose in Paracel Plan 0190 Q-17.

Source: Paracel Plan 0190 (Q-17, Q-19, Prerequisite 3) and its progress log of 2026-10-15; kit precedents #148 (optional `--tertiary`) and #149 (optional `--print-breaking`), which this plan follows for every new role: `contract/modules.json`, a neutral default in `shared/base/`, `scripts/sync-shared.py`, and the tests in `test_contract.py`, `test_resolver.py` and `test_ux_design_system.py`. No PRD.

Principles:

1. One increment equals one coherent change set and one commit.
2. Every increment is test-driven: write-first tests observed red, then a green test gate.
3. Additive only: a 2.0 manifest, a 2.0 deck and every existing fixture render byte-identical under 2.1.0 unless they opt in (a `dark` slide class with a design that provides `dark`, or a `classification:` key).
4. Roles, never literals: the dark remap is written in role names only; the base theme gives the module neutral defaults like every optional module, so a design without `dark` still renders a dark slide.
5. Shared code stays in sync: every change under `shared/` runs `scripts/sync-shared.py` in the same commit.

**Overall Status:** pending
**Current Increment:** --

## Plan-level decisions (agent defaults, for owner review)

| ID | Question | Default |
| :-- | :-- | :-- |
| D-1 | A module or roles inside `slide-frame`? | A new optional module `dark`: a design may provide a slide frame without a dark theme, and the provenance report says where the dark roles came from. |
| D-2 | Which roles? | `--dark-canvas-bg`, `--dark-surface`, `--dark-surface-2`, `--dark-border`, `--dark-ink`, `--dark-muted`, `--dark-tertiary`, `--dark-accent` (marks, lines, meters, frames), `--dark-accent-text` (highlighted text), `--dark-accent-fill` and `--dark-accent-ink` (a filled mark and its text), `--dark-key-fill` (the key element's fill, a colour or gradient), `--dark-glow` (the key element's shadow). |
| D-3 | Which classes? | `dark` on a slide (the class Paracel's decks already use) and `dark-key` for the one key element of a dark slide; both join the `dark` module's class vocabulary. |
| D-4 | Classification values | A closed list: `Public`, `Internal`, `Confidential`, `Strictly confidential`; any other value exits 2 naming the four; absent prints nothing. A design styles `.slide-classification`; the label text is not translated in this plan. |
| D-5 | Where the classification prints | Every slide's footer row (between the legal line and the number) and, for `mode: document`, the running footer of every page. Views and release-note reports are out of scope (follow-up if a consumer needs it). |
| D-6 | Branching | Increments open PRs into `main` (no release branch: the release is additive); the 2.1.0 version bump is the last increment and merges at the owner's request. |

## Increment Plan

### Increment 01: the dark module in the contract and the base theme

**Status:** pending

Scope:

1. **Write first, expect red:**
   - extend `tests/test_contract.py::test_declares_contract_version_and_nine_modules` (adapt: contract `2.1.0`, ten modules, `dark` optional) and `::test_no_role_in_two_modules`; new `::test_dark_roles_and_classes` (the D-2 roles, the D-3 classes); extend `::test_pairs_name_existing_roles` with the dark pairs: `--dark-ink` on `--dark-canvas-bg` and on `--dark-surface`, `--dark-muted` on `--dark-surface`, `--dark-tertiary` on `--dark-canvas-bg`, `--dark-accent-text` on `--dark-canvas-bg`, `--dark-accent-ink` on `--dark-accent-fill`; extend `::test_base_defines_every_role_of_every_module` (the base `dark.css` defines every dark role and its own pairs pass AA).
   - extend `tests/test_contract.py::test_accepts_full_and_subset` (the `full` fixture now provides `dark`) and `::test_rejects_unknown_module_bad_semver_and_unknown_key` (a 2.0 manifest naming `dark` still validates under 2.1; a module name outside the ten is still refused).
   - extend `tests/test_resolver.py`: `full` resolves `dark` from the design; `subset` resolves it from the base; the provenance report lists `dark`.
   - extend `tests/test_ux_design_system.py`: `point` accepts a manifest providing `dark` and checks its pairs; `subset` leaves `dark` to the base.
2. `contract/modules.json`: `contractVersion` 2.1.0 and the `dark` module (roles, classes, pairs); `contract/kit-manifest.schema.json` gains `dark` in the module enum; `contract/README.md` gains the module row.
3. `shared/base/dark.css`: neutral dark defaults (a near-black canvas, light text, a mid-blue accent), each base pair at AA; `tests/fixtures/design-systems/full/` gains a fictitious `dark` module and its manifest entry.
4. `scripts/sync-shared.py` run; every skill copy updated.

Primary files:

1. `plugins/delivery-comms/contract/{modules.json,kit-manifest.schema.json,README.md}`, `plugins/delivery-comms/shared/base/dark.css` and the skill copies
2. `plugins/delivery-comms/tests/{test_contract.py,test_resolver.py,test_ux_design_system.py}`, `plugins/delivery-comms/tests/fixtures/design-systems/full/`

Test gate:

1. `mise exec -- make -C plugins/delivery-comms test`
2. `mise exec -- python3 plugins/delivery-comms/scripts/sync-shared.py --check`

Exit criteria:

1. The contract declares ten modules at 2.1.0; a 2.0 manifest and the `subset` fixture resolve unchanged; `dark` comes from the base when a design omits it.

### Increment 02: a dark slide switches every core role

**Status:** pending

Scope:

1. **Write first, expect red:**
   - extend `tests/test_slide_deck.py`: a fixture deck with one slide whose `config.yaml` entry has `class: "dark"` builds against `full`; inside that slide the computed `--canvas-bg`, `--slide-bg`, `--surface`, `--surface-2`, `--border`, `--ink`, `--muted`, `--tertiary`, `--accent` and `--accent-ink` equal the `full` fixture's dark roles, and the logo uses `--brand-logo-on-dark`; an element with class `dark-key` takes `--dark-key-fill` and `--dark-glow`; the other slides keep the light roles; `check_render.py` passes on the output and the provenance lists `dark` as `design-system`.
   - extend `tests/test_slide_deck.py`: the same deck against `subset` renders the dark slide from the base `dark.css` and passes the validator.
   - extend `tests/test_characterisation.py` (or `test_reproducible.py`): every existing fixture deck, view and report renders byte-identical to its 2.0.0 output (no `dark` class, no change).
   - extend `tests/test_contract.py::test_class_vocabularies_cover_what_the_renderers_emit` with `dark` and `dark-key`.
2. `shared/base/dark.css` (or `slide-frame.css`, whichever the module layering requires): `.slide.dark { --canvas-bg: var(--dark-canvas-bg); --slide-bg: var(--dark-canvas-bg); ... }` remapping every core role in role names only, the logo on dark, and `.slide.dark .dark-key { background: var(--dark-key-fill); box-shadow: var(--dark-glow); }`.
3. `com-slide-deck/scripts/build.py`: inlines the `dark` module with the other deck modules (after `slide-frame`, before the deck's `styles.css`); views and reports do not inline it.
4. `scripts/sync-shared.py` run.

Primary files:

1. `plugins/delivery-comms/shared/base/dark.css`, `plugins/delivery-comms/skills/com-slide-deck/scripts/build.py`
2. `plugins/delivery-comms/tests/{test_slide_deck.py,test_characterisation.py,test_contract.py}` and a fixture deck under `tests/fixtures/`

Test gate:

1. `mise exec -- make -C plugins/delivery-comms test test-pdf`

Exit criteria:

1. A slide marked `dark` renders on the design's dark roles (or the base's) with no deck-local property, passes the validator, and nothing else changes.

Prediction:

1. Changed outputs: only the new dark fixture deck's output. Every existing characterisation output stays byte-identical.

### Increment 03: the deck classification in the footer

**Status:** pending

Scope:

1. **Write first, expect red:**
   - extend `tests/test_slide_deck.py`: with `classification: Confidential` in `config.yaml`, every slide's footer row holds `<span class="slide-classification">Confidential</span>` between the legal line and the number; with no key, the footer is byte-identical to 2.0.0; `classification: Secret` exits 2 and names the four allowed values; a `mode: document` deck prints the classification in the running footer of every PDF page (`test_pdf.py`, extend the document fixture case).
   - extend `tests/test_contract.py::test_slide_frame_roles_and_classes` and `::test_class_vocabularies_cover_what_the_renderers_emit` with `slide-classification`.
2. `com-slide-deck/scripts/build.py`: read and check `classification:`, add the cell in `slide_footer`; `shared/print_chrome.py` `footer_template` takes an optional classification for `mode: document`; `shared/base/slide-frame.css` styles `.slide-classification` in roles only (the tertiary text role, mono, uppercase, like the label).
3. `contract/modules.json`: `slide-classification` joins the `slide-frame` classes; `scripts/sync-shared.py` run.

Primary files:

1. `plugins/delivery-comms/skills/com-slide-deck/scripts/build.py`, `plugins/delivery-comms/shared/{print_chrome.py,base/slide-frame.css}`, `plugins/delivery-comms/contract/modules.json`
2. `plugins/delivery-comms/tests/{test_slide_deck.py,test_pdf.py,test_contract.py}`

Test gate:

1. `mise exec -- make -C plugins/delivery-comms test test-pdf`

Exit criteria:

1. A deck that declares a classification shows it on every slide and page; a deck that does not is unchanged.

Prediction:

1. Changed outputs: only the fixture decks that gain a `classification:` key in this increment.

### Increment 04: the skills teach dark slides and classification

**Status:** pending

Scope:

1. **Exempt from red-first (documentation):** `com-slide-deck` SKILL.md and its references: mark a dark slide with `class: "dark"` and use the key element class, never a deck-local dark palette; declare `classification:` with the four levels and when each applies (Strictly confidential for sensitive personal data, GDPR Art. 9). `ux-design-system` SKILL.md and `references/`: the `dark` module, its roles and pairs, what `point` and `subset` do with it; `references/agents-md-block.md` gains no line (the block stays five lines). `contract/README.md` final pass.
2. **Write first, expect red:** extend `tests/test_skill_evals.py` (or the eval case list under `evals/`) with one case: migrating a deck whose styles define `--dark-bg` and friends ends with the slide carrying `class: "dark"` and no `--dark-*` property in `styles.css`. The owner-approved eval run is optional, as in Plan-0005 increment 12.

Primary files:

1. `plugins/delivery-comms/skills/com-slide-deck/SKILL.md`, `plugins/delivery-comms/skills/ux-design-system/SKILL.md` and `references/`, `plugins/delivery-comms/contract/README.md`
2. `plugins/delivery-comms/evals/`, `plugins/delivery-comms/tests/test_skill_evals.py`

Test gate:

1. `mise exec -- make -C plugins/delivery-comms test`
2. `./scripts/audit-skills.sh`

Exit criteria:

1. An agent following the skills marks dark slides and classifications through the contract, never with deck-local properties.

### Increment 05: release 2.1.0

**Status:** pending

Scope:

1. **Exempt from red-first (versions and notes):** `plugin.json` 2.0.0 to 2.1.0; skill `metadata.version` bumped where the skill changed (minor); `CHANGELOG.md` `## 2.1.0 - <date>` naming the `dark` module, the `dark` and `dark-key` classes, `classification:`, and that 2.0 manifests and decks render unchanged.
2. Merge to `main` at the owner's request; `claude plugin marketplace update` and `claude plugin update delivery-comms@<marketplace>` verified against the cache.

Primary files:

1. `plugins/delivery-comms/.claude-plugin/plugin.json`, skill `metadata.version` fields, `plugins/delivery-comms/CHANGELOG.md`

Test gate:

1. `mise exec -- make -C plugins/delivery-comms test test-pdf`
2. `./scripts/audit-skills.sh`

Exit criteria:

1. 2.1.0 is in the marketplace cache; its scripts render the fixture deck with a dark slide and a classification against `full`, `subset` and a 2.0 design, each passing `check_render.py`.

## Delivery Rules

1. One increment per commit.
2. **Commit scope:** `delivery-comms`. Types: `feat` (01 to 03), `docs` (04), `chore` (05). Trailer `Refs: Plan-0006 increment NN`, never the plan number in the scope.
3. Each increment must be independently runnable and reversible.
4. Tests named in Scope are written or extended first and observed failing before the implementation lands; `progress.txt` records the red run (failing test names) and the green run. A write-first test that already passes is wrong or redundant: fix it, or log why. An increment whose tests were written after its code is not done.
5. Every increment that changes a file under `shared/` runs `scripts/sync-shared.py` in the same commit.
6. Additive only (Principle 3): a change to an existing fixture's output blocks the increment unless its `Prediction:` names it.
7. No real client material in fixtures; the `full` fixture's dark module is a fictitious brand.
8. Foreground gates only; every iteration ends with a definitive state.

## Milestone Chunks (Standalone Delivery Groups)

| Milestone | Increments | Status | Coherent Outcome | Standalone Test Gate | Exit Criteria | Commit Guidance |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| M1: Dark module | 01-02 | pending | A design names its dark roles once; a `dark` slide switches every core role | `make -C plugins/delivery-comms test test-pdf` | Dark slide renders on design or base roles; existing outputs byte-identical | `feat(delivery-comms)` |
| M2: Classification | 03 | pending | Every slide and page shows the deck's classification | `make -C plugins/delivery-comms test test-pdf` | Four levels, closed list, unchanged when absent | `feat(delivery-comms)` |
| M3: Skills and release | 04-05 | pending | Agents use both through the contract; 2.1.0 in the cache | `make -C plugins/delivery-comms test`, `./scripts/audit-skills.sh` | 2.1.0 renders the fixtures from the cache | `docs(delivery-comms)`, `chore(delivery-comms)` |
