# Research 0004: Design systems that agents build and consume, in full or as a subset

Date: 2026-10-11
Status: draft, for owner review; feeds the delivery-comms plan that replaces the 24-token contract
Scope: how AI products, coding agents and big design systems (1) build a design system or a subset of one, (2) store and distribute it, (3) let generators (UI, decks, charts, documents) consume all of it or part of it, and (4) keep the output on-brand. Three parallel desk-research passes on 2025-2026 sources: AI products (21 tools), agent skills and protocols (Anthropic skills, MCP servers, context files, validation, chart and slide theming), standards and architecture (DTCG 2025.10, token contracts, manifests, data-viz tokens, document theming, distribution). Claims carry a source; "unverified" marks those backed only by secondary sources.

## Why this matters for the kit

The delivery-comms renderers (com-slide-deck, com-artefact-viz, com-release-note) theme themselves from a 24-token CSS contract a project places at `docs/ux/tokens.css`. A real design system carries far more: the reference case, a brand design system published on npm, has 173 tokens in three DTCG tiers, a chart palette, a type scale, document components, a slide frame, A4 print rules, logos, a legal line and written guidelines. Its 24-token kit export keeps colours and fonts and drops the rest. The kit's `ux-design-system` skill can only author those 24 tokens. The question is how to let the kit consume a complete design system or a subset, and how an agent can build either.

## Findings

### 1. Every serious format pairs values with usage prose

Google's DESIGN.md (open-sourced April 2026, Apache-2.0) puts tokens in YAML front matter (`colors`, `typography`, `rounded`, `spacing`, `components`) and fixed prose sections ending in "Do's and Don'ts" ([design.md](https://github.com/google-labs-code/design.md)). Lovable renders `.lovable/design-system.json` into `rules/*.md` ([Lovable](https://docs.lovable.dev/features/design-systems)); Figma Make reads `guidelines/Guidelines.md` ([Figma](https://developers.figma.com/docs/code/write-design-system-guidelines/)); v0's Design Systems 2.0 stores the system as a skill ([v0](https://v0.app/docs/design-systems)); Primer's MCP server has `get_color_usage` and `get_typography_usage` next to `find_tokens` ([@primer/mcp](https://www.npmjs.com/package/@primer/mcp)). A CSS contract alone tells an agent what a value is, not when to use it.

### 2. Agents read resolved values, not DTCG

DTCG is the source and exchange format; no product hands raw DTCG to the agent. DESIGN.md exports to DTCG and Tailwind; Figma Make flattens variables to CSS values; agents work from resolved CSS variables or flat token lists plus prose ([design.md](https://github.com/google-labs-code/design.md), [Figma help, unverified](https://help.figma.com/hc/en-us/articles/33024539096471)). DTCG Format and Resolver modules 2025.10 are Final Community Group Reports, "considered stable" ([format](https://www.w3.org/community/reports/design-tokens/CG-FINAL-format-20251028/), [resolver](https://www.w3.org/community/reports/design-tokens/CG-FINAL-resolver-20251028/)); Style Dictionary 5 still lists 2025.10 support as partial and has no resolver support yet ([SD docs](https://styledictionary.com/info/dtcg/)), Terrazzo supports the resolver ([Terrazzo](https://terrazzo.app/docs/guides/resolvers)).

### 3. A subset is normal, and good systems name it

- Deck tools (Gamma, Canva, Beautiful.ai, Pitch) need only palette, fonts and logo ([Canva](https://www.canva.com/help/create-on-brand-designs/), [Beautiful.ai](https://beautiful.ai/brand-controls-themes)).
- Anthropic's theme-factory skill is 4 colours with roles plus 2 fonts per theme ([theme-factory](https://github.com/anthropics/skills/blob/main/skills/theme-factory/SKILL.md)); brand-guidelines is a palette and two fonts in prose, with no validator ([brand-guidelines](https://github.com/anthropics/skills/blob/main/skills/brand-guidelines/SKILL.md)).
- Posit's brand.yml is "by design incomplete for any given output format" and still themes Quarto HTML, dashboards, reveal.js and Typst PDF from one file ([brand.yml](https://posit-dev.github.io/brand-yml/), [Quarto](https://quarto.org/docs/authoring/brand.html)).
- DESIGN.md has an `omitted:` field that declares deliberately absent sections, and its linter warns that an agent will invent a primary colour or fall back to default fonts when they are missing.

What works is a subset that is a declared profile of the system, with explicit omissions, not an ad-hoc cut.

### 4. Big systems share one contract shape: fixed roles, swappable values, defined fallback

Material 3 roles with `on-` pairs ([M3](https://material-web.dev/theming/color/)), Carbon ("tokens never change across themes"; a custom theme falls back to a built-in theme) ([Carbon](https://carbondesignsystem.com/elements/themes/code/)), Salesforce SLDS hooks consumed as `var(--hook, fallback)` ([SLDS](https://trailhead.salesforce.com/content/learn/modules/salesforce-lightning-design-system-2-for-developers/explore-salesforce-lightning-design-system-2)), shadcn's `-foreground` pairs and `chart-1…5` ([shadcn](https://ui.shadcn.com/docs/theming)), Radix's two inputs expanding to 12-step scales ([Radix](https://radix-ui.com/themes/docs/theme/color)). Missing values come from one of three places: a base theme, derivation from a seed, or a CSS fallback.

### 5. A versioned manifest of capabilities has one good precedent

Adobe's Spectrum Design Data spec (1.0.0-draft) has platform manifests that pin and filter foundation tokens, JSON Schemas with a versioned `$id`, stable rule IDs, conformance fixtures, SemVer for the contract itself and deprecation metadata ([Spectrum](https://opensource.adobe.com/spectrum-design-data/spec)). Nothing formally named "core versus extended profile" exists elsewhere; DTCG's resolver declares sets but has no "required" or capability flag, so that belongs in a sibling manifest or `$extensions`.

### 6. Charts and slides each want their own theme shape

- Vega-Lite takes a JSON `config` whose `range` has named slots `category`, `ordinal`, `ramp`, `heatmap`, `diverging`, `symbol` ([Vega-Lite](https://vega.github.io/vega-lite/docs/scale.html)).
- ECharts takes a registered JSON theme with a `color` array ([ECharts](https://echarts.apache.org/handbook/en/concepts/style/)).
- Chart.js takes JS globals; Highcharts styled mode reads `--highcharts-color-N` CSS variables, the closest fit for a CSS contract ([Highcharts](https://www.highcharts.com/docs/chart-design-and-style/custom-themes-in-styled-mode), unverified).
- reveal.js and Marp themes are CSS variables ([Marp](https://marpit.marp.app/theme-css)).
- Carbon's data-viz palettes give the rules worth copying: a fixed categorical order, sequential ramps whose direction flips by theme ([Carbon](https://carbondesignsystem.com/data-visualization/color-palettes/)).

No maintained DTCG-to-chart-theme generator was found; systems write one adapter per target. No major design system ships an official slide or PDF layer; brand.yml and Quarto are the main multi-format precedent.

### 7. On-brand enforcement has moved from prompts to checks in the loop

Lovable scans every generation for raw colours and one-off values and retries. Primer's `lint_css` is described as the "REQUIRED FINAL STEP" of any CSS task. zeroheight's MCP server has a lint tool. `design.md lint` checks broken references and WCAG contrast and `design.md diff` exits 1 on regression. Prose-only guidance (Figma Make) produces lookalike components ([forum](https://forum.figma.com/report-a-problem-6/figma-make-not-using-my-library-components-42235)). A CHI 2026 study found assembling pre-built components from a registry gave 95.08 % design-system compliance, ahead of instruction-based and context-based strategies ([Cha et al.](https://pure.seoultech.ac.kr/en/publications/design-system-compliant-user-interface-generation-with-llm-agents/); other rates not public).

### 8. Discovery needs passive context; detail can live in skills or MCP

Vercel's evals: an 8 KB docs index in AGENTS.md scored 100 %, skills 79 % when prompted, and skills went uninvoked in 56 % of cases ([Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals), summary). Singapore's government design system says llms.txt cannot tell an agent which component to use and adds agent skills ([SGDS](https://www.designsystem.tech.gov.sg/ai/llm-txt)). Primer fetches tokens by group to save context.

### 9. Building a system: import from code beats import from pictures

v0, Lovable, Bolt and Claude Design prefer a repository or npm package as the source; extraction from screenshots or URLs (Uizard, Stitch, Lovable from scratch) is described by the vendors themselves as approximate or best-effort ([Lovable](https://docs.lovable.dev/features/design-systems)). Brad Frost: agents ignore existing patterns and build their own unless the system is machine-readable infrastructure ([Frost](https://bradfrost.com/blog/link/agentic-design-systems-in-2026-with-brad-frost/)).

## What this means for the kit

1. **The contract becomes modules, each a fixed role list.** Proposed modules: `core` (surfaces, ink, accent with its on-pair, status, three font families; today's 24 tokens), `type` (weights, sizes, roles), `space-shape` (spacing scale, radii, shadow), `dataviz` (named after Vega-Lite ranges: `category[n]`, `ordinal`, `sequential`, `diverging`, `remainder`, `highlight`), `document` (component stylesheet: cards, KPI tiles, tables, callouts, footer), `slide-frame` (canvas size, section label, footer row), `print` (page size and margins), `brand` (logo files and the legal line), and `guidance` (do/don't prose per module). Only `core` is required.
2. **A manifest declares what a design system provides.** One JSON file in the package, for example `kit-manifest.json`: `contractVersion` (SemVer of the kit contract, independent of the brand's version), the modules provided with the export name of each file, and `omitted` with a reason, as DESIGN.md does. The kit validates it against a JSON Schema it owns.
3. **Fallback is layered and explicit.** A module the package does not provide comes from the kit's own neutral base theme (Carbon's model); scales the package omits can be derived from the accent seed (Radix and M3); renderers write `var(--role, fallback)` so a palette-plus-fonts subset still renders. The renderer reports which modules came from the package and which from the base, so a reviewer knows what is on-brand.
4. **The design system generates one adapter per generator from its DTCG source.** Module CSS for the kit, a Vega-Lite config and an ECharts theme from `dataviz`, a DESIGN.md (readable by Stitch, Bolt and DESIGN.md-aware agents) and a brand.yml (Quarto, Typst, reveal.js). The kit never parses DTCG.
5. **Distribution and pin.** The package stays on npm with provenance. A docs repository pins it in `docs/ux/package.json` so Dependabot proposes bumps; the kit downloads that exact tarball once, checks npm's integrity hash and caches it, so no `npm install` and no copied token files. A local folder path is accepted for previewing an unreleased design system.
6. **Validation is a mandatory last step of every renderer.** After rendering, the kit checks that the output uses only contract roles (no raw colour, no unknown variable) and that text pairs meet contrast; the skill may not report done without a passing run. Delivered documents stay protected by a hash register.
7. **Discovery through a compact index.** A project's AGENTS.md or CLAUDE.md names the pin file, the manifest and the validator in a few lines; the skills carry the detail.
8. **Building a system or a subset.** `ux-design-system` gets two modes. *Subset*: the owner (or an agent, from a brand PDF, a website or a deck) writes a DESIGN.md-style file with the modules it can fill and an `omitted` list; the skill generates the module CSS and the manifest, so a small project gets a declared subset instead of 24 untyped values. *Full*: the reference design-system repository becomes a template (DTCG tiers, build, adapters, tests, release, agent skill) that an agent instantiates for another brand; this is a separate kit capability, not a stretch of the subset mode. Import from an existing package or code is preferred; extraction from pictures is marked approximate.

## Open decisions for the owner

1. Module list and which modules are required (proposal: `core` only).
2. Manifest format: a kit-owned JSON Schema (proposal) or DTCG resolver plus `$extensions`.
3. Whether the kit validator runs as a hard gate (fail the render) or reports only, for subsets.
4. Whether to emit DESIGN.md and brand.yml from the design system now or later.
5. Whether the full-system template is in scope now, or only the subset path.

## Caveats

Claude Design's storage format and checking, Stitch's URL extraction, Figma Make library import details, Highcharts styled-mode variable names, Supernova and Knapsack capabilities and the Vercel eval figures rest on secondary sources. The CHI 2026 figure comes from the abstract only. No source was found for official AI material from Polaris, Atlassian or Salesforce.
