# Detection Signals — util-metamodel-migration

Internal Claude reference. Never copied to projects. Update this file when the metamodel gains new artefacts.

The three-tier detection system. A finding requires ≥2 tiers to agree before being reported with a fix block. Single-tier matches are flagged Low confidence.

---

## §Filename patterns (Tier 1 — High signal)

A file whose name matches one of these patterns is likely the artefact type listed.

| Filename pattern (glob) | Likely artefact type | Canonical skill | Canonical path |
|---|---|---|---|
| `*_prd_*.md` or `*-prd-*.md` | PRD | `spec-prd` | `docs/product-specs/NNNN_prd_*.md` (flat, not in subdirs) |
| `[0-9][0-9][0-9][0-9]-*.md` or `[0-9][0-9][0-9][0-9]_*.md` in a decisions-like folder | ADR | `arch-adr` | `docs/architecture/decisions/NNNN-{topic}.md` |
| `*-adr-*.md` (redundant adr in name) | ADR naming issue | `arch-adr` | Rename: remove `-adr` from filename |
| `*runbook*.md` | Runbook | `ops-runbook` | `docs/ops/runbooks/{slug}.md` |
| `*-rca*.md` or `*-incident*.md` or `*-postmortem*.md` | Bug RCA | `ops-bug-rca` | `docs/ops/rcas/{date}-{slug}.md` |
| `*-process.md` or `*-workflow.md` | Business process | `business-process` | `docs/business/processes/{slug}-process.md` |
| `*persona*.md` or `*personas*.md` | Personas | `business-persona` | `docs/business/personas/personas.md` |
| `*capability-map*.md` or `*capabilities*.md` | Capability map | `business-capability-map` | `docs/business/capability-map/capability-map.md` |
| `*value-stream*.md` or `*value-streams*.md` | Value streams | `business-value-stream` | `docs/business/value-streams/value-streams.md` |
| `*business-model-canvas*.md` or `*lean-canvas*.md` or `*bmc*.md` | BMC / Lean Canvas | `business-model-canvas` | `docs/business/business-model-canvas/` |
| `*glossary*.md` | Domain glossary | `domain-glossary` | `docs/domain/glossary/glossary.md` |
| `*information-model*.md` or `*domain-model*.md` or `*canonical*model*.md` | Domain model | `domain-model` | `docs/domain/{bc-slug}/domain-model.md` |
| `*bounded-context*.md` or `*context-map*.md` | Bounded context | `domain-bounded-context` | `docs/domain/bounded-contexts/` |
| `FBS.md` or `*functional-breakdown*.md` | FBS | `spec-functional-breakdown-structure` | `docs/product-specs/functional-breakdown-structure/FBS.md` |
| `*quality-attributes*.md` or `*nfr*.md` or `*non-functional*.md` | Quality attributes | `spec-quality-attributes` | `docs/product-specs/quality-attributes/quality-attributes.md` |
| `*delivery-roadmap*.md` or `*epic-catalogue*.md` or `*epic-catalog*.md` | Delivery roadmap | `spec-delivery-roadmap` | `docs/product-specs/delivery-roadmap/delivery-roadmap.md` |
| `*competitive-landscape*.md` or `*competitor*.md` | Competitive landscape | `business-competitive-landscape` | `docs/business/competitive-landscape/` |
| `*quant-model*.md` or `*tam-*.md` or `*savings-model*.md` | Quantitative model | `business-quantitative-model` | `docs/business/models/{slug}.md` |
| `VISION.md` or `*vision*.md` or `*north-star*.md` | Product vision | `business-vision` | `docs/VISION.md` (singleton at docs root) |
| `*objectives*.md` or `*okr*.md` or `*key-results*.md` | Business objectives | `business-objective` | `docs/business/objectives/objectives.md` |

**ADR naming redundancy rule:** if a file is already in `docs/architecture/decisions/` and its name contains `-adr-` (e.g. `0003-adr-clean-architecture.md`), flag as Tier 1 naming issue. Proposed fix: `git mv 0003-adr-clean-architecture.md 0003-clean-architecture.md`. The `-adr-` prefix is redundant since the folder already signals the type.

**PRD subdirectory rule:** if `*_prd_*.md` files are found at depth ≥2 under `docs/product-specs/` (i.e., in a subdirectory), flag as misplacement. The canonical location is flat at `docs/product-specs/NNNN_prd_*.md`.

---

## §Folder name patterns (Tier 2 — Medium signal)

A folder whose name matches one of these patterns, AND is not already at the canonical path, is likely misplaced.

| Folder name pattern | Likely artefact type | Canonical path | Detection command |
|---|---|---|---|
| `runbooks/` or `runbook/` | `ops-runbook` | `docs/ops/runbooks/` | `find docs -type d -iname "runbook*" \| grep -v "docs/ops/runbooks"` |
| `bugs/` or `bug-reports/` or `rcas/` or `incidents/` | `ops-bug-rca` | `docs/ops/rcas/` | `find docs -type d -iname "bug*" -o -type d -iname "rca*" -o -type d -iname "incident*" \| grep -v "docs/ops"` |
| `workshop*/` or `workshops/` | `business-workshop` | `docs/business/workshops/` | `find docs -type d -iname "workshop*" \| grep -v "docs/business/workshops"` |
| `objectives/` or `okr/` or `okrs/` | `business-objective` | `docs/business/objectives/` | `find docs -type d -iname "objective*" -o -type d -iname "okr*" \| grep -v "docs/business/objectives"` |
| `personas/` or `persona/` | `business-persona` | `docs/business/personas/` | `find docs -type d -iname "persona*" \| grep -v "docs/business/personas"` |
| `capabilities/` or `capability-map/` | `business-capability-map` | `docs/business/capability-map/` | `find docs -type d -iname "capabilit*" \| grep -v "docs/business/capability-map"` |
| `value-streams/` or `journeys/` or `customer-journeys/` | `business-value-stream` | `docs/business/value-streams/` | `find docs -type d -iname "value-stream*" -o -type d -iname "journey*" \| grep -v "docs/business/value-streams"` |
| `processes/` or `workflows/` | `business-process` | `docs/business/processes/` | `find docs -type d -iname "process*" -o -type d -iname "workflow*" \| grep -v "docs/business/processes"` |
| `decisions/` or `adrs/` or `adr/` | `arch-adr` | `docs/architecture/decisions/` | `find docs -type d -iname "decision*" -o -type d -iname "adr*" \| grep -v "docs/architecture/decisions"` |
| `glossary/` or `ubiquitous-language/` or `vocabulary/` | `domain-glossary` | `docs/domain/glossary/` | `find docs -type d -iname "glossar*" -o -type d -iname "ubiquitous*" \| grep -v "docs/domain/glossary"` |
| `models/` containing `*model*.md` files | `business-quantitative-model` or `domain-model` | `docs/business/models/` or `docs/domain/` | Confirm with Tier 1 + Tier 3 |
| `ideas/` or `proposals/` | `spec-idea` | `docs/ideas/` | `find docs -type d -iname "idea*" -o -type d -iname "proposal*" \| grep -v "docs/ideas"` |

---

## §Content signals (Tier 3 — Confirmation, first 50 lines only)

Read only `head -50 {file}`. Check for these high-signal headings. A content signal alone = Low confidence; combined with Tier 1 or 2 = High confidence.

| Heading pattern (grep -iE) | Artefact type confirmed |
|---|---|
| `## Porter.s Five Forces` or `## Five Forces` | `business-competitive-landscape` |
| `## Persona Backlog` or `## Cooper Persona` | `business-persona` |
| `## §8 KPI` or `^## KPIs` with `## §3 Actors` nearby | `business-process` |
| `## L0 axis` or `## Capability Index` or `## Global overview` | `business-capability-map` |
| `## Value Stream Catalogue` or `## Catalogue` with `VS-[0-9]` nearby | `business-value-stream` |
| `## Aggregate catalogue` or `## Domain event catalogue` | `domain-model` |
| `## Subdomain catalogue` or `## Bounded Context` with `BC-[0-9]` | `domain-bounded-context` |
| `## Implicit assumptions` or `§5\.2` or `## Scenario Matrix` | `business-quantitative-model` |
| `§0 Architecture Traceability` or `## Acceptance criteria` with `PRD-[0-9]` | `spec-prd` |
| `\*\*Status:\*\*.*Accepted` or `\*\*Status:\*\*.*Deprecated` with `## Context` | `arch-adr` |
| `## Customer Segments` or `## Value Propositions` with `## Revenue Streams` | `business-model-canvas` |
| `## Ubiquitous Language` or `GT-[0-9][0-9]` pattern | `domain-glossary` |
| `✅\|🔄\|⬜` in functionality table rows | `spec-functional-breakdown-structure` |
| `QA-[A-Z]{2}[0-9]{2}` pattern | `spec-quality-attributes` |
| `E-[0-9][0-9].*epic` | `spec-delivery-roadmap` |
| `## The Elevator Pitch` or `## North Star Metric` heading | `business-vision` |
| `OBJ-[0-9][0-9]` pattern or `KR-[0-9][0-9]\.[0-9]` pattern | `business-objective` |
| `## Objective.*Epic traceability` | `business-objective` |

---

## §Outside metamodel scope patterns

Folders/files that are valid project docs but have NO equivalent metamodel artefact. Flag as Info — no action needed, no fix block.

| Pattern | Why outside scope |
|---|---|
| `docs/developer/` or `docs/dev-guide/` or `docs/contributing/` | Developer guides — not a metamodel artefact |
| `docs/design/` or `docs/ui/` or `docs/ux/` | Design system — not in metamodel (com-slide-deck handles presentations) |
| `docs/ci-cd/` or `docs/deployment/` or `docs/infra/` | CI/CD and infra docs — not in metamodel |
| `docs/data/` (excluding glossary/info-model files) | Data engineering docs — not in metamodel (glossary/info-model are DDD candidates) |
| `docs/codebase/` or `docs/valuation/` | Business/financial analysis — not in metamodel |
| `docs/pipeline*/` or `docs/pipeline steps/` | Pipeline technical guides — not in metamodel |
| `docs/developer/` | Developer onboarding — not in metamodel |
| Files with `.pptx`, `.html`, `.pdf` | Binary/presentation formats — not text artefacts in the metamodel |

---

## §DDD migration candidate signals

Files that predate the domain- skill layer but contain content that belongs in `docs/domain/`. These get §4 treatment (Warning, no git mv fix block — the domain skill must process them first).

| Signal | Likely destination | Skill to run |
|---|---|---|
| File named `*glossary*.md` outside `docs/domain/glossary/` | `docs/domain/glossary/glossary.md` | `domain-glossary` Mode 2 (seed from existing) |
| File named `*information-model*.md` or `*canonical*model*.md` or `*domain-model*.md` outside `docs/domain/` | `docs/domain/{bc-slug}/domain-model.md` | `domain-model` Mode 2 (fill from existing) |
| File named `*entity*.md` or `*entities*.md` or `*aggregate*.md` | `docs/domain/{bc-slug}/domain-model.md` | `domain-model` Mode 2 |
| File named `*bounded-context*.md` outside `docs/domain/bounded-contexts/` | `docs/domain/bounded-contexts/bounded-contexts.md` | `domain-bounded-context` Mode 3 (fill) |
| Content signal: `## Ubiquitous Language` or `GT-[0-9]` IDs anywhere | `docs/domain/glossary/` | `domain-glossary` Mode 3 (enrich) |

**DDD candidate note:** do NOT emit `git mv` for DDD candidates. The domain skill (domain-glossary, domain-model) should be invoked first to scaffold the target doc at the correct path — it reads the existing content and imports it. Moving first would leave the domain skill with nothing to import.
