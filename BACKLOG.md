# Skill backlog

Candidate skills to add to the kit, ordered by metamodel impact. Generated 2026-05-20 from a gap analysis of the 14-artefact stack; updated 2026-05-22 after shipping further items (see §Shipped below).

---

## Shipped — 2026-05-28 (Milestone 2)

| Skill / task | What was done |
|---|---|
| **`arch-c4` runtime mode** (arc42 §6) | Fifth mode added to the existing skill — `runtime` produces arc42 §6 Runtime View via Structurizr `dynamic` view blocks. Mints `SCN-NN` IDs. One scenario per invocation; each appends a `## 6.x` subsection to `06-runtime-view.md` with an embedded SVG + step table. Boundary rules added: runtime view shows HOW containers collaborate (wire-level messages) — NOT per-aggregate state machines (those stay in domain-model). New files: `references/arc42-section-06.md` (embedded §6 spec), `templates/arc42-06-runtime-view.md`. |
| **`arch-arc42`** (arc42 §2 / §4 / §8 / §11) | New four-mode skill covering the narrative arc42 sections with no C4 diagram counterpart. `constraints` mode (§2): three-category table (technical / organizational / legal-regulatory), mints `CST-NN`, cites source + ADR per constraint. `solution-strategy` mode (§4): navigation aid — technology decision table + quality goal → tactic mapping table; links to ADR-NNNN, never re-states rationale; no new IDs. `cross-cutting` mode (§8): eleven-area concept catalogue (authentication, authorisation, session, logging, tracing, error-handling, persistence, caching, i18n, transport security, feature flags), mints `CC-NN`, each entry names governing ADR + affected CON-NN containers. `risks` mode (§11): risk register with four types (`architectural`, `technical-debt`, `dependency`, `security`), mints `RSK-NN`, explicit boundary with ops runbooks, hook left for future `dev-tech-debt` skill. Each mode reads upstream artefacts before proposing content. Embedded arc42 §2/§4/§8/§11 specs + methodology-references bibliography + four output templates. |
| **Metamodel updated** | `rules/metamodel.md`: `arch-c4` bullet updated (5 modes + SCN-NN); `arch-arc42` bullet added; ID conventions table (`SCN-NN`, `CST-NN`, `CC-NN`, `RSK-NN`); canonical paths tree (arc42/ subtree expanded to all 8 sections). `README.md`: `arch-arc42` row + updated `arch-c4` row. `util-metamodel-audit/references/check-catalogue.md`: Check 1 (5 new arc42 file detectors) + Check 5 (4 new ID patterns) + Check 9 (5 new mandatory-section rules). `util-metamodel-migration/references/detection-signals.md`: 6 new filename patterns (§6 + §2/§4/§8/§11 canonical + misplaced) + content signals. |

---

## Shipped — 2026-05-28 (Milestone 1)

| Skill / task | What was done |
|---|---|
| **`arch-structurizr`** (supporting — Milestone 1 foundation) | New skill — scaffolds the Structurizr DSL workspace + Docker render pipeline that powers all C4 / arc42 architecture diagrams. Output: `docs/architecture/c4/{workspace.dsl, render.sh, README.md, views/}`. Three modes: `init`, `verify`, `upgrade`. Uses the consolidated Structurizr vNext tool (`structurizr/structurizr:2026.05.22-playwright`) — the EOL `structurizr-cli` is not used. Direct SVG export via bundled headless Chromium; no PlantUML stage. References: `dsl-conventions.md`, `docker-pipeline.md`, `structurizr-cheatsheet.md`, `mcp-optional.md`. Pin policy: `:latest` forbidden; `-playwright` suffix mandatory. |
| **`arch-c4`** (supporting — Milestone 1 authoring) | New skill — four modes producing arc42 §3 / §5 / §7 markdown with embedded C4 SVGs. `context` mints `SYS-NN` (arc42 §3, C4 Level 1). `container` mints `CON-NN` (arc42 §5.1, C4 Level 2). `component` mints `CMP-NN` (arc42 §5.2 / §5.3, C4 Level 3) with mandatory `properties.implements "BC-NN.AGG-NN"` back-reference into `domain-model` (or `"none"` for tech-only components). `deployment` mints `DN-NN` (arc42 §7). Embeds arc42 v9.0 spec under `references/arc42-section-{03,05,07}.md` so skill is self-contained. Boundary discipline file documents the three tests separating BBV from `domain-model` and runtime view. Retires the Tier 1 `arch-c4` backlog candidate. |
| **`examples/c4-demo`** (kit-internal validation) | End-to-end validation snapshot of the pipeline. Claims Platform system with 5 containers + 4 components inside CON-02 + Production deployment. All 4 modes exercised; all 8 SVGs (4 views + 4 legends) committed. The 3 arc42 markdown files (§3, §5, §7) show the populated templates with the `Domain aggregates implemented` column and the `"none"` sentinel for tech-only CMP-01. |
| **Pipeline bugfixes** | render.sh shell precedence bug (REPO_ROOT concatenated two paths) + root-owned files from Docker (`--user $(id -u):$(id -g)` added) + `theme default` removal (cloud service EOLs 2026-09-30) + first-run timing claim correction (Chromium is bundled in `-playwright` image, not downloaded on demand — actual render is 5–10 s, not 3+ minutes) + DSL empty-property rejection (`"implements" ""` is invalid; use `"implements" "none"` sentinel). All four landed in the Milestone 1 commits. |
| **Metamodel updated** | `rules/metamodel.md`: supporting-skills list (2 new bullets) + ID conventions (`SYS-NN`, `CON-NN`, `CMP-NN`, `DN-NN`) + canonical paths (`docs/architecture/c4/` + `docs/architecture/arc42/` subtrees) + maintenance coupling log entry. `README.md`: skill index (6 new rows; also patched missing `arch-service-contract` + `arch-cli-contract` + `dev-stack-guide` + `dev-getting-started` rows from prior commits). `util-metamodel-audit/references/check-catalogue.md`: Check 1 (arc42 + c4 path detection) + Check 2 (canonical placement rules + Milestone 2 forward-compat note) + Check 5 (C4 ID regex patterns) + Check 9 (mandatory sections per file type including the Domain-aggregates-implemented column). `util-metamodel-migration/references/detection-signals.md`: §Filename (workspace.dsl, render.sh, 03/05/07-*.md) + §Folder (c4/, arc42/) + §Content signals (DSL workspace block; arc42 §N headings; SYS/CON/CMP/DN ID patterns). |
| **`dev-stack-guide`** | New skill — researches a technology stack's latest official docs, finds the official MCP server (four-step discovery process: modelcontextprotocol/servers index → vendor GitHub → community search → tech's own docs), and writes a developer guide covering core patterns (5–10), anti-patterns, project conventions, and coding-agent integration. Three modes: `research` (→ `docs/dev-guides/research/{tech-slug}-research.md`), `draft` (→ `docs/dev-guides/{tech-slug}.md`), `refresh` (re-researches, diffs version pin, updates). Frontmatter `verified-for:` field pins the exact verified version; `review_interval: 90d` triggers staleness flag. References: `references/research-methodology.md` (source quality tiers, MCP discovery decision tree, pattern extraction heuristics, version pinning strategy), `templates/guide-template.md` (canonical output). |
| **`dev-getting-started`** | New skill — scaffolds and populates a project-specific getting-started guide at `docs/dev-guides/getting-started.md`. Reads project files (package.json, go.mod, docker-compose.yml, .env.example, Makefile/justfile/Taskfile, CI config, CLAUDE.md, .mcp.json) to emit exact commands — no invented content. Covers: prerequisites, clone & bootstrap, environment setup (every .env.example var documented), running locally (services + ports), common dev tasks, coding agent setup (CLAUDE.md + MCP servers), troubleshooting (3 universal entries + project-specific). Three modes: `scaffold` (structure + auto-detects runtime), `fill` (populates from project files), `refresh` (detects changes, updates stale sections). `review_interval: 180d`. Template: `templates/guide-template.md`. |
| **Metamodel updated (dev-* skills)** | `rules/metamodel.md`: supporting-skills list expanded (dev-stack-guide + dev-getting-started bullets; dev-* workflow bullet split from new doc-producing skills) + canonical paths tree (`docs/dev-guides/` subtree added after `discovery/`) + prefix→folder mapping (`dev-` row updated with exception note for the two new skills) + maintenance coupling log entry. `util-metamodel-audit/references/check-catalogue.md`: Check 2 updated (docs/dev-guides/ paths added as canonical). `util-metamodel-migration/references/detection-signals.md`: §Filename patterns (getting-started.md + {tech-slug}-research.md), §Folder patterns (dev-guides/), §Content signals (## Stack identity → dev-stack-guide; ## Clone & bootstrap → dev-getting-started). |

---

## Shipped — 2026-05-25

| Skill / task | What was done |
|---|---|
| **`arch-service-contract`** (Step 7c) | New skill — defines the external interface contract for a bounded context. One artefact per `BC-NN`. Mints `BC-NN.CTR-NN` IDs. Four modes: scaffold, contract-first (derives REST resources + async events from `BC-NN.AGG/ENT/EVT`), document-existing (reverse-engineer from code), refresh (drift detection + deprecation). Embeds: Fielding REST dissertation constraints, Richardson Maturity Model (target Level 2+), RFC 9110 HTTP method semantics, RFC 7807 Problem Details error format, CloudEvents 1.0.3 envelope, Hyrum's Law, Postel's Law (with RFC 9110 qualification), Tolerant Reader pattern, cursor-based pagination default, breaking-change classification. References: Google API Design Guide, Stripe API patterns, Microsoft REST Guidelines, Semantic Versioning, AsyncAPI 3.0 vocabulary, EIP event/command message patterns. Output: `docs/architecture/interfaces/{bc-slug}.md`. |
| **`arch-cli-contract`** (supporting skill) | New skill — defines the external CLI surface contract for a user-facing command-line tool. One artefact per tool. Mints `CLI-NN` and `CLI-NN.CMD-NN` IDs. Four modes: scaffold, design (contract-first from FBS), document-existing (reverse-engineer from `--help`), refresh. Embeds: POSIX.1-2017 Section 12 utility conventions, GNU Coding Standards Chapter 4, ESR *Art of Unix Programming* Rules (Silence, Composition, Separation, Repair), CLI Guidelines (clig.dev 2021) stdout/stderr contract and color policy, 12-Factor Config precedence chain, sysexits.h exit code catalogue (64–78 + 130/131), NO_COLOR convention, `isatty()` + `TERM=dumb` color check, `--` end-of-options marker, `--dry-run` requirement for mutating commands. References: kubectl noun-verb taxonomy, Click/Cobra conventions, Heroku CLI patterns. Output: `docs/architecture/interfaces/cli-{slug}.md`. |
| **Metamodel updated** | `rules/metamodel.md`: added Step 7c row + build order section + DAG node + ER entities (`INTERFACE_CONTRACT`, `CLI_SURFACE`, `CLI_COMMAND`) + ID conventions (`BC-NN.CTR-NN`, `CLI-NN`, `CLI-NN.CMD-NN`) + canonical paths (`docs/architecture/interfaces/`) + `arch-cli-contract` supporting skill bullet + maintenance coupling entry. |

---

## Shipped — 2026-05-22

| Skill / task | What was done |
|---|---|
| **`util-docs-lint`** | New skill — scaffolds GitHub Actions CI workflow (3 parallel jobs: dprint formatting, Vale + Microsoft style prose, markdown-link-check links). Templates for `.vale.ini`, `dprint.json`, `.mlc-config.json`. Glossary alias sync script. |
| **`arch-adr` v1.1** | Added `init` mode (bootstraps `docs/architecture/decisions/` + writes `0001` meta-ADR), `supersede` mode (atomic two-file operation: new ADR + old ADR frontmatter update), auto-numbering via `find`. |
| **Artefact frontmatter convention** | New `rules/artefact-frontmatter.md` — canonical 5-field schema (`title`, `status`, `owner`, `last_reviewed`, `review_interval`) + conditional `superseded_by` / `supersedes` fields. All 21 skills updated with frontmatter output bullet + skill-specific `review_interval` default. `spec-idea` schema aligned (removed `created`, `decided_at`, `exec_plan`, `prd`; added standard fields). ADR `## Status` body section replaced by frontmatter `status` field. |
| **`util-metamodel-audit` Check 17** | Dedicated frontmatter validity check extracted from Check 9 — covers block presence, 5 required fields, valid status enum, `superseded_by` enforcement, supersession link integrity, `owner` non-empty, `last_reviewed` date format. Count updated 16 → 17. |
| **Metamodel ID audit + fixes** | Cross-checked all skill SKILL.md files against metamodel ID declarations. Fixed: `arch-research` → `Research-NNNN` added; `business-competitive-landscape` → `CO-NN` added; capability map notation unified to `C-N.M`; `business-model-canvas` block IDs (`CS-N`–`CT-N`) defined; `spec-prd` explicit auto-numbering rule added. Check-catalogue updated (Checks 5, 6, 9, 12, 15). |
| **PRD path + naming** | PRDs moved to `docs/product-specs/prds/prd-NNNN-{feature}.md`. Skill, metamodel, and all 6 audit check references updated. Find command scoped to `prds/` + `prd-*` pattern. |
| **`com-slide-deck` path** | Output moved to `docs/communication/slides/{slug}/`. Internal structure renamed: `output/slides/` → `src/`, `output/slide-deck/` → `dist/`. `com-` prefix added to metamodel prefix→folder table and canonical paths tree. `skill-creation-sync.md` updated. |

---

## Shipped — 2026-05-21

| Skill / task | What was done |
|---|---|
| **`business-vision`** | Step 0 — singleton `docs/VISION.md`, Moore elevator pitch + Sinek WHY + Pichler Vision Board + North Star metric. Wire mode appends agent context pointer to project CLAUDE.md. |
| **`business-objective`** | Step 4.5 — `docs/business/04b-objectives.md`, OKR structure (OBJ-NN + KR-NN.M), outcome discipline gate, BSC 4-perspective tag, Align mode for epic traceability. |
| **`com-slide-deck`** | Renamed from `dev-slide-deck`. Introduced new `com-` prefix category for communication artefacts. install.sh dangling-symlink prune bug fixed. |
| **v2 path simplification** | All 11 singleton artefacts flattened to numbered files (`01-personas.md`, `02-bmc.md`, `03-capability-map.md`, `04-value-streams.md`, `04b-objectives.md`, `07-fbs.md`, `08-delivery-roadmap.md`, `09-quality-attributes.md`; domain singletons flattened; domain models consolidated into `docs/domain/07b-models/{bc-slug}.md`). Kit fully updated: 15 SKILL.md files, metamodel.md, README.md, check-catalogue.md, detection-signals.md. 4 pre-existing `epic-catalogue.md` bugs fixed. |
| **`util-metamodel-migration` Mode 4** | Schema migration mode — reads `references/path-migration-v2.md`, generates atomic `git mv` + `sed` script for v1→v2 project migration. Dry-run default; `--apply` opt-in; post-migration audit hook. |

---

## Tier 1 — High impact, direct metamodel gap

| Skill | Output path | Gap filled | New ID | Upstream links |
|---|---|---|---|---|
| **`domain-event-storming`** | `docs/domain/event-storming/` | `domain-bounded-context` assumes you already know your BCs. Event Storming (Brandolini) is how you *discover* them. Produces a big-picture event catalogue (pivotal events, hotspots, rough BC boundaries) that feeds Step 2b. | `ES-EVT-NN`, `ES-CMD-NN` | feeds `BC-NN`, `BC-NN.EVT-NN` |
| **`spec-test-strategy`** | `docs/product-specs/test-strategy/` | `spec-quality-attributes` says *what* quality targets are. Nothing covers *how* to verify them — test pyramid, coverage targets, contract testing strategy, QA-XXNN → test type mapping. Big gap between NFR spec and implementation plan. | `TS-NN` | `QA-XXNN`, `E-NN`, `ADR-NNNN` |
| **`business-customer-journey-map`** | `docs/business/customer-journeys/` | The value stream is business-view (capability-consuming, stage-based). A customer journey map is experience-view (touchpoints, emotions, pain moments, channel). Feeds persona enrichment and VS pain-index calibration. | `CJ-N.M` | `P-NN`, `VS-N.M` |

---

## Tier 2 — Strong value, architectural completeness

| Skill | Output path | Gap filled | New ID | Upstream links |
|---|---|---|---|---|
| **`arch-team-topology`** | `docs/architecture/team-topology/` | Once you have `BC-NN` bounded contexts, Conway's Law demands team structure mirrors domain boundaries. Team Topologies (Skelton & Pais): stream-aligned / platform / enabling / complicated-subsystem. Nothing models this today. | `TEAM-NN` | `BC-NN`, `C-N.M` |
| **`ops-slo`** | `docs/ops/slos/` | `spec-quality-attributes` (QA-XXNN) are design-time targets. After go-live they become operational contracts: SLI definitions, SLO thresholds, error budgets, alert burn-rate policies (Google SRE). Bridges spec → day-2 monitoring. | `SLO-NN` | `QA-XXNN`, ops runbooks |
| **`arch-threat-model`** | `docs/architecture/threat-model/` | `spec-quality-attributes` can document security NFRs but there is no structured threat-modelling artefact. STRIDE per data-flow, DREAD scoring, mitigations, residual risk. Should precede security QAs and feeds ADR inputs. | `THR-NN` | feeds `ADR-NNNN`, `QA-SE-NN` |
| **`domain-integration-contract`** | `docs/domain/integration-contracts/` | The context map names integration patterns (ACL, Shared Kernel, etc.) but never produces the concrete contract for each BC-pair — event schema, API contract, data ownership rules. One stub per integration pair. | `INT-NN` | `BC-NN` pairs, `BC-NN.EVT-NN` |
| **Cross-skill web visualisations** | Shared HTML/SVG/Canvas views generated from the same canonical Markdown data used by the business and architecture skills. Target artefacts include capability maps, competitive landscapes, business model canvases, personas, delivery roadmaps, and functional breakdown structures. This would give each skill a consistent browser-based presentation layer for sharing ideas and for reuse in slide-deck builder workflows, without making Markdown the rendering source of truth. |

---

## Tier 3 — Useful, lower metamodel coupling

| Skill | Gap filled |
|---|---|
| **`spec-release-plan`** | Release communication + rollout per E-NN epic. Feature flag plan, comms template, rollback criteria. Bridges delivery roadmap → ops. |
| **`ops-post-mortem`** | Blameless post-mortem for operational incidents. `ops-bug-rca` is code-level; post-mortem is broader org-wide incident review with timeline, contributing factors, action items. |
| **`business-stakeholder-map`** | RACI / stakeholder influence-interest grid. Internal actors vs. customers. Links to processes (actors) and value streams (stage owners). |
| **`dev-changelog`** | CHANGELOG.md management per Keep a Changelog. Bridges commit history → user-facing release notes. |
| **`dev-tech-debt`** | Log, prioritise, and track both technical debt and documentation debt as they are discovered — during code review, refactoring, implementation, or doc audits. Each entry captures: location (file + line or doc path), category (design / test / documentation / dependency / architecture debt), severity (critical / major / minor), discovery context, estimated remediation effort, and owner. Modes: `log` (add a new debt item), `triage` (prioritise backlog by severity × effort), `close` (mark resolved with resolution note), `report` (summary table by category + severity). Output: `TECH_DEBT.md` at repo root. Companion to `ops-bug-rca` (bugs) and `arch-adr` (architectural decisions) — tech and docs debt sits between the two. |
| **`util-open-items` deterministic runner** | Optional future hardening for the existing `util-open-items` skill. Add a deterministic script/CLI that implements the documented contract: parse canonical `## Open Items` tables, mint monotonic `OI-NNNN` IDs, sync source artefacts into `docs/project-control/open-items/open-items.md`, validate close/drop tracker refs, detect duplicates, archive terminal rows, and emit reports. Keep the current skill-driven workflow as the human/operator interface; use the runner when mechanical repeatability, CI checks, or batch sync become necessary. |

---

---

## Structural decisions pending

Convention gaps that need a decision before more artefacts accumulate. Not new skills — metamodel + skill updates only.

| Item | Question | Options |
|---|---|---|
| **PRD naming with epic reference** | `prd-NNNN-{feature}.md` does not encode which epic it belongs to. Hard to tell `prd-0003-checkout.md` belongs to `E-02` without opening the file. | (A) Encode epic in filename: `prd-0003-e02-checkout.md` · (B) Subfolder per epic inside `prds/`: `prds/e02/prd-0003-checkout.md` · (C) Keep flat — epic is in §0 traceability, audit enforces the link |
| **Exec-plan folder organisation + PRD links** | `docs/exec-plans/active/{NNNN}_{slug}/` uses its own sequential NNNN, unrelated to the PRD's NNNN. No enforced naming relationship between a plan and its PRD. Hard to find which plan belongs to which PRD. | (A) Match NNNN to PRD: `exec-plans/active/prd-0003-checkout/` · (B) Reference PRD in folder name: `exec-plans/active/0001-prd0003-checkout/` · (C) Nest plan inside PRD folder: `product-specs/prds/prd-0003-checkout/plan/` |

---

## Recommended build order (if extending the metamodel)

```
arch-c4                     ← fills the biggest structural gap (adds a whole system-diagram layer)
domain-event-storming       ← makes Step 2b discoverable, not assumed
spec-test-strategy          ← closes the QA-XXNN → verification loop
arch-team-topology          ← completes the BC-NN → team mapping
ops-slo                     ← closes the QA-XXNN → day-2 operational loop
```

Tier 2 and Tier 3 candidates improve completeness but are not structural gaps in the current metamodel.
