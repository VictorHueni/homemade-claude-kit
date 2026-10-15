# Changelog

All notable changes to the `delivery-comms` plugin. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the plugin follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html). The release date is set when the release merges to `main`.

## 2.0.0 - Unreleased

Decks, artefact views and release notes now render in your organisation's real design system, pinned at an exact version, and every render is checked against it before anything is written. The same source and the same design now give the same bytes every time.

This is a breaking release: a project whose only design source is a legacy `docs/ux/tokens.css` (or `docs/design/tokens.css`) stops rendering until it moves to the new design contract. The move takes one command; see **Upgrading**.

### What you get

- **Your design system, pinned.** `docs/ux/package.json` names one design-system package at an exact version. The package carries a `kit-manifest.json` that says which design modules it provides (`core` and `dataviz` are required; type, spacing and shape, document, slide frame, print, brand and guidance are optional) and why it leaves any out. The renderers download the pinned version once, check its integrity and cache it per machine. Anything a design leaves out comes from the kit's neutral base theme, so a small design still renders whole. ([#131](https://github.com/VictorHueni/homemade-claude-kit/pull/131), [#132](https://github.com/VictorHueni/homemade-claude-kit/pull/132))
- **Point at a design, or describe your own.** `ux-design-system point <package>@<x.y.z>` pins a published design system after checking its manifest and its contrast, and prints the Dependabot entry so version bumps arrive as pull requests. A project without a design system writes a Google-format `DESIGN.md` with the modules it can fill, and `ux-design-system subset` turns it into a design-system folder, its manifest and the pin. When the chart colours are missing, `subset` proposes a contrast-checked palette from the accent colour for you to confirm. ([#141](https://github.com/VictorHueni/homemade-claude-kit/pull/141))
- **Every render is checked before it is written.** A validator refuses a hard-coded colour outside the design, a style property the contract does not know, and text whose contrast falls below WCAG AA. A refused render writes nothing and names the value, where it is and the design role to use instead. After rendering, `check_render.py --record` writes a short verdict file next to the output (`PASS: no findings`, or the findings). ([#133](https://github.com/VictorHueni/homemade-claude-kit/pull/133))
- **A provenance report with every output.** Each render writes `<output>.provenance.json`: which design and version it used, and which modules came from the design and which from the base theme, with any declared exceptions and warnings. ([#132](https://github.com/VictorHueni/homemade-claude-kit/pull/132), [#134](https://github.com/VictorHueni/homemade-claude-kit/pull/134), [#138](https://github.com/VictorHueni/homemade-claude-kit/pull/138), [#139](https://github.com/VictorHueni/homemade-claude-kit/pull/139))
- **Slide decks carry your brand frame.** `com-slide-deck` builds from the resolved design and the validator, and takes its canvas, logo, legal line and slide number from the design's slide frame and brand modules. ([#134](https://github.com/VictorHueni/homemade-claude-kit/pull/134), [#135](https://github.com/VictorHueni/homemade-claude-kit/pull/135))
- **Views use colour by meaning.** `com-artefact-viz` paints status and pain with the design's state colours and importance and confidence with its ordered chart scale, so red appears only where something is wrong. Its five views render from the resolved design and pass the validator. ([#137](https://github.com/VictorHueni/homemade-claude-kit/pull/137), [#138](https://github.com/VictorHueni/homemade-claude-kit/pull/138))
- **Release-note reports follow the design too.** `com-release-note` renders its HTML and PDF report from the resolved design, with the design's fonts, logo and legal line. ([#139](https://github.com/VictorHueni/homemade-claude-kit/pull/139))
- **Same source, same bytes.** Two renders of an unchanged source with the same design give byte-identical HTML, PDF and provenance files. Every printed or embedded date now comes from the source (`SOURCE_DATE_EPOCH`, else the source's last commit), and printed paths are relative to the repository. ([#140](https://github.com/VictorHueni/homemade-claude-kit/pull/140))
- **Agents follow the new path.** The four skills now tell an agent how to resolve the design, run the validator and record the verdict, and how to migrate a legacy project, and an eval suite checks that they do. ([#143](https://github.com/VictorHueni/homemade-claude-kit/pull/143))
- The pre-commit hook checks that every skill's copy of the shared scripts matches the canonical one. ([#136](https://github.com/VictorHueni/homemade-claude-kit/pull/136))

### Breaking changes

- **A legacy `docs/ux/tokens.css` or `docs/design/tokens.css` is refused.** With no `docs/ux/package.json` pin, every renderer stops with exit 2 and a message naming `ux-design-system point`, `ux-design-system subset` and `ux-design-system subset --from-legacy`. There is no transition release. ([#132](https://github.com/VictorHueni/homemade-claude-kit/pull/132))
- **`ux-design-system generate` and `refresh` are removed.** Both now exit 2 and print the `subset` command that replaces them. `docs/ux/design-system.md` and `tokens.css` are replaced by `docs/ux/DESIGN.md` and the generated `docs/ux/design-system/` folder. ([#141](https://github.com/VictorHueni/homemade-claude-kit/pull/141))
- **`com-artefact-viz --design-system` takes a design-system folder** with a `kit-manifest.json`; a single stylesheet is refused. ([#138](https://github.com/VictorHueni/homemade-claude-kit/pull/138))
- **Every delivery-comms PDF changes bytes once.** The first render with 2.0.0 differs from any earlier render of the same source, because the dates and paths are now fixed by the source. After that, an unchanged source keeps its bytes. ([#140](https://github.com/VictorHueni/homemade-claude-kit/pull/140))
- **`util-provenance` tokens over PDFs made before 2.0.0 are superseded, not invalid.** Such a token still proves that the exact bytes it names existed at its date, so keep those bytes (the record's git blob anchors them, or keep the file). Do not re-render over a timestamped PDF without keeping its bytes; timestamp the new render if you need proof of it, and note in the old record that the new one supersedes it. See [ADR-0013](../../docs/architecture/decisions/adr-0013-reproducible-delivery-comms-output.md).

### Upgrading

1. Update the plugin: `claude plugin update delivery-comms@<marketplace>`.
2. Give the project its design, one of:
   - an organisation design system: `ux-design-system point <package>@<x.y.z>`, then add the printed Dependabot entry to `.github/dependabot.yml`;
   - a project without one: `ux-design-system scaffold`, fill `docs/ux/DESIGN.md`, then `ux-design-system subset docs/ux/DESIGN.md`;
   - a project with a legacy token file: `ux-design-system subset --from-legacy docs/ux/tokens.css`, review the drafted `docs/ux/DESIGN.md` and its proposed chart colours, delete the `proposed:` line, then `ux-design-system subset docs/ux/DESIGN.md`. The legacy file is never edited; delete it yourself once the subset renders.
3. Re-render, check that each verdict reads `PASS: no findings`, and handle any timestamped PDFs as described above before you commit the new bytes.
4. Optionally, copy the five-line block in [`skills/ux-design-system/references/agents-md-block.md`](skills/ux-design-system/references/agents-md-block.md) into the project's `AGENTS.md`.
