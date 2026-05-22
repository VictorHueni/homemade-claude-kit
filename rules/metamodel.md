---
paths:
  - "docs/**"
  - "rules/metamodel.md"
---

# Strategic Architecture Stack — Documentation Build Order

This rule documents the **complete strategic-architecture artefact stack**
produced by the kit's `business-*` + `spec-*` skills, the **dependency graph** between
them, and the **canonical build order** Claude should follow when starting
documentation work on any new project.

When the user says *"build the documentation stack"*, *"do the strategic
docs"*, *"start the project documentation"*, or *"follow the architecture
plan"* — this rule is the authoritative reference for **what to build, in
what order, and where to put it**.

---

## The 16 artefacts and their skills

| # | Layer | Skill | Output file | Primary IDs |
|---|---|---|---|---|
| 0 | **Product Vision** (why — the north star) | `business-vision` | `docs/VISION.md` | *(singleton — no ID; referenced by path)* |
| 1 | **Personas** (who) | `business-persona` | `docs/business/01a-personas.md` | `P-NN` |
| 2 | **Business Capability Map** (what abilities) | `business-capability-map` | `docs/business/03a-capability-map.md` | `C-N.M` (e.g. `C1`, `C1.1`, `C1.1.1` at L2 rare) |
| 2b | **Bounded Context Map** (domain boundaries + context map) | `domain-bounded-context` | `docs/domain/bounded-contexts.md` + `docs/domain/context-map.md` | `BC-NN` |
| 2c | **Domain Glossary** (ubiquitous language per bounded context) | `domain-glossary` | `docs/domain/glossary.md` | `BC-NN.GT-NN` |
| 3 | **Value Streams** (how value flows) | `business-value-stream` | `docs/business/04a-value-streams.md` + `docs/business/04a-vpc-{segment}.md` (optional VPC per VS) | `VS-N`, `VS-N.M` (stages) |
| 4.5 | **Business Objectives** (why — strategic intent) | `business-objective` | `docs/business/04b-objectives.md` | `OBJ-NN`, `KR-NN.M` |
| 4 | **Business Processes** (operational how) | `business-process` | `docs/business/05a-processes/proc-NN-{slug}.md` (one file per process) | per-process slug |
| 5 | **Business Model Canvas** (commercial wrapper) | `business-model-canvas` | `docs/business/02a-bmc.md` or `docs/business/02a-lean-canvas.md` + optional `docs/business/02a-vpc-{segment}.md` | block IDs (CS-N, VP-N, …) |
| 6 | **Quantitative models** (numbers) | `business-quantitative-model` | `docs/business/06a-models/qm-NN-{topic}.md` | per-model slug |
| 7 | **Functional Breakdown Structure** (functionality registry) | `spec-functional-breakdown-structure` | `docs/product-specs/07a-fbs.md` | `C-N.M.FXX` (capability + functionality counter) |
| 7b | **Domain Model** (entities · aggregates · value objects · domain events per BC) | `domain-model` | `docs/domain/07b-models/{bc-slug}.md` (one per BC) | `BC-NN.AGG-NN` · `BC-NN.ENT-NN` · `BC-NN.VO-NN` · `BC-NN.EVT-NN` |
| 8 | **Delivery Roadmap** (Plan by Feature — delivery grouping) | `spec-delivery-roadmap` | `docs/product-specs/08a-delivery-roadmap.md` | `E-NN` |
| 9 | **Quality Attributes** (how well the system performs) | `spec-quality-attributes` | `docs/product-specs/09a-quality-attributes.md` | `QA-PE01`, `QA-SE03` … (characteristic prefix + counter) |
| 10 | **PRDs** (feature specs — Build by Feature) | `spec-prd` | `docs/product-specs/prds/prd-NNNN-{feature}.md` | `PRD-NNNN` |
| 11 | **Implementation plans** (atomic increments) | `spec-implementation-plan` | `docs/exec-plans/active/{NNNN}_{slug}/` | `Plan-NNNN`, `Inc-N` |

**Supporting skills** (not in the main build order, used as needed):
- `arch-adr` — Architecture Decision Records → `docs/architecture/decisions/adr-{NNNN}-{slug}.md`. **Sequencing rule:** ADRs governing security, flexibility, or maintainability must be written before Step 9 (Quality Attributes) so the QA doc can reference them. All ADRs must precede Step 10 (PRDs) that depend on their decisions. Invoke ADRs as soon as an architectural choice must be made — they are not a post-hoc documentation exercise.
- `spec-idea` — captures pre-PRD ideas → `docs/ideas/{slug}.md`
- `spec-peer-review` — reviews PRDs / plans
- `arch-research` — Architecture Research notes that inform ADR decisions → `docs/architecture/research/{NNNN}-{slug}.md`; mints `Research-NNNN` in-doc ID (4-digit zero-padded, same convention as `ADR-NNNN`); lifecycle: Draft → Active → Frozen (once feeding ADRs land) → Superseded
- `business-competitive-landscape` — Porter Five Forces + Strategic Group Map + Value Curve + per-competitor profiles → `docs/business/01b-competitive-landscape/`; mints `CO-NN` per Tier-1 competitor profile; soft-links to personas (P-NN), BMC, capability map (C-N.M), quantitative models; run **after Step 1 (Personas)** so competitor ICPs can be mapped to persona IDs, and **before Step 2 (BMC) is filled** so competitive positioning informs the Value Propositions block rather than following it; alternatively run alongside Step 6 (quantitative models) when the primary need is competitor pricing or market-sizing data
- `ops-runbook`, `ops-bug-rca` — operational artefacts (post-ship)
- `util-docs-audit` — general doc staleness scan (file-level freshness, dead prose)
- `util-metamodel-audit` — deep metamodel compliance audit: 16 checks covering stack progress, folder placement, internal + external links, ID integrity + cross-references, dependency enforcement, _TODO_ density, mandatory sections, confidence distribution, expiry + staleness, orphaned files, research sync, ADR chains, FBS + epic delivery progress → report at `var/reports/metamodel-audit/`; report-only with proposed fix per finding; run monthly (active dev) or quarterly (maintenance)
- `util-metamodel-migration` — one-time migration doctor for repos built before the metamodel: scans any docs/ folder, detects misplaced files using tiered confidence scoring (filename → folder name → content signals), emits atomic fix blocks (git mv + sed link repairs) per file → report at `var/reports/metamodel-migration/`; report-only; run once before the first `util-metamodel-audit`
- `dev-*` skills — developer workflow (git, PR, worktree, ralph loop)
- `com-slide-deck` — HTML slide presentations → `docs/communication/slides/{slug}/` (one folder per deck, named after the presentation in kebab-case)

---

## Dependency graph (DAG)

```
   ┌──────────────────────────────────────────────────┐
   │  business-vision (Step 0)                        │
   │  (why — the north star)                          │
   │  Output: docs/VISION.md (singleton)              │
   │  Wires to: CLAUDE.md (agent context injection)   │
   └──────────────────────┬───────────────────────────┘
                          │ soft-links to all downstream artefacts
                          │
                       ┌──┴─────────────────────┐
                       │  business-persona      │
                       │  (who we serve)        │
                       │  Output: P-NN          │
                       └──────────┬─────────────┘
                                  │
              ┌───────────────────┼──────────────────────┐
              │                   │                      │
              ▼                   ▼                      ▼
   ┌──────────────────────┐ ┌────────────────────┐ ┌──────────────────────┐
   │ business-            │ │ business-          │ │ business-            │
   │   capability-map     │◄┤   value-stream     │ │   model-canvas       │
   │ (what abilities)     │ │ (how value flows)  │ │ (commercial wrapper) │
   │ Output: C-N.M        │ │ Output: VS-N.M     │ │ Soft-links P-NN,     │
   └──────────┬───────────┘ │ Stages consume     │ │   C-N.M, VS-N,       │
              │             │   C-N.M            │ │   quant models       │
              │             └──────────┬─────────┘ └──────────────────────┘
              │                        │
              │                        ▼
              │             ┌────────────────────┐
              │             │ business-process   │
              │             │ (operational how)  │
              │             │ Operationalises    │
              │             │   a VS stage       │
              │             └────────────────────┘
              │
              │             ┌────────────────────┐
              │             │ business-          │
              │             │  quantitative-model│
              │             │ (numbers / TAM)    │
              │             └────────────────────┘
              │
              │   ┌──────────────────────────────────────────┐
              │   │ business-objective (Step 4.5)            │
              │   │ (strategic intent — why)                 │
              │   │ Output: OBJ-NN, KR-NN.M                  │
              │   │ Reads: P-NN · VS-N.M pain · VP-NN (BMC)  │
              │   │ Soft-links to: E-NN · QA-XXNN · PRD-NNNN │
              │   └──────────────────────────────────────────┘
              │
              ▼
   ┌──────────────────────┐
   │ spec-functional-     │
   │   breakdown-structure│
   │ (what product does)  │
   │ Output: C-N.M.FXX    │
   │ Inherits L0+L1 from  │
   │   capability map     │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │ spec-delivery-roadmap  │
   │ (Plan by Feature)    │
   │ Output: E-NN         │
   │ Groups FBS by VS     │
   │   stage + capability │
   │ Orders by pain index │
   └──────────┬───────────┘
              │         ┌─────────────────────┐
              │         │ arch-adr            │
              │         │ (architecture       │
              │         │  decisions)         │
              │         │ Output: ADR-NNNN    │
              │         │ Precedes Steps 9+10 │
              │         └──────────┬──────────┘
              │                    │
              ▼                    ▼
   ┌──────────────────────────────────────────┐
   │ spec-quality-attributes                  │
   │ (how well the system performs — NFRs)    │
   │ Output: QA-XXNN                          │
   │ Reads: FBS ★ → Reliability targets      │
   │ Reads: ADRs → Security/Flexibility QAs  │
   │ Reads: Personas → IC/PE QAs             │
   │ Reads: VS pain index → PE priorities    │
   └──────────────────┬───────────────────────┘
                      │
                      ▼
   ┌──────────────────────────────────────────┐
   │ spec-prd (Build by Feature)              │
   │ Output: PRD-NNNN                         │
   │ One PRD per E-NN epic                    │
   │ References: E-NN · C-N.M.FXX · QA-XXNN  │
   └──────────────────┬───────────────────────┘
                      │
                      ▼
   ┌──────────────────────┐
   │ spec-implementation- │
   │   plan               │
   │ (atomic increments)  │
   │ Output: Plan-NNNN    │
   │ One plan per PRD     │
   └──────────────────────┘
```

### Entity-relationship view

The ER diagram shows which ID each artefact **mints** (PK) and which upstream IDs it **consumes** (FK) as cross-references — treating the documentation system as a data model.

```mermaid
erDiagram
    VISION {
        string file PK
    }
    PERSONA {
        string P_NN PK
    }
    CAPABILITY_MAP {
        string C_NM PK
    }
    VALUE_STREAM {
        string VS_NM PK
        string P_NN FK
        string C_NM FK
    }
    BUSINESS_PROCESS {
        string slug PK
        string VS_NM FK
    }
    BMC {
        string id PK
        string P_NN FK
    }
    QUANTITATIVE_MODEL {
        string slug PK
    }
    OBJECTIVE {
        string OBJ_NN PK
        string VS_NM FK
        string P_NN FK
    }
    KEY_RESULT {
        string KR_NNM PK
        string OBJ_NN FK
    }
    FBS {
        string C_NM_FXX PK
        string C_NM FK
    }
    EPIC {
        string E_NN PK
        string C_NM_FXX FK
        string VS_NM FK
    }
    ADR {
        string ADR_NNNN PK
    }
    QUALITY_ATTRIBUTES {
        string QA_XXNN PK
        string ADR_NNNN FK
        string P_NN FK
    }
    PRD {
        string PRD_NNNN PK
        string E_NN FK
        string QA_XXNN FK
        string ADR_NNNN FK
    }
    IMPLEMENTATION_PLAN {
        string Plan_NNNN PK
        string PRD_NNNN FK
    }

    PERSONA ||--o{ VALUE_STREAM : "triggers"
    PERSONA ||--o{ BMC : "Customer Segments"
    PERSONA }o--o{ QUALITY_ATTRIBUTES : "grounds IC and PE entries"
    CAPABILITY_MAP ||--o{ VALUE_STREAM : "stages consume C-NM"
    CAPABILITY_MAP ||--|| FBS : "inherits L0 and L1"
    CAPABILITY_MAP }o--o{ BMC : "Key Resources"
    VALUE_STREAM ||--o{ BUSINESS_PROCESS : "operationalised by"
    VALUE_STREAM }o--o{ QUALITY_ATTRIBUTES : "pain index drives PE"
    VALUE_STREAM }o--o{ EPIC : "VS stage anchor"
    BMC ||--o{ QUANTITATIVE_MODEL : "Revenue and Cost"
    VISION }o--o{ PERSONA : "audience scope"
    VISION }o--o{ OBJECTIVE : "objectives operationalise"
    VISION }o--o{ BMC : "VP blocks express commercially"
    VALUE_STREAM }o--o{ OBJECTIVE : "pain index informs priority"
    PERSONA }o--o{ OBJECTIVE : "whose outcomes"
    OBJECTIVE ||--o{ KEY_RESULT : "measures progress via"
    OBJECTIVE }o--o{ EPIC : "epics serve"
    KEY_RESULT }o--o{ QUALITY_ATTRIBUTES : "KR targets ground"
    FBS ||--o{ EPIC : "grouped into epics"
    FBS }o--o{ QUALITY_ATTRIBUTES : "differentiators drive Reliability"
    ADR }o--o{ QUALITY_ATTRIBUTES : "decisions inform Security and Flexibility"
    ADR }o--o{ PRD : "decisions inform architecture"
    EPIC ||--|| PRD : "one PRD per epic"
    QUALITY_ATTRIBUTES ||--o{ PRD : "QA-XXNN in acceptance criteria"
    PRD ||--|| IMPLEMENTATION_PLAN : "one plan per PRD"
```

**Hard rules of the graph:**
- An arrow `A → B` means *B soft-links to A by ID*. B can be scaffolded without A existing (placeholder `_TODO_`), but the link is filled when A arrives.
- **No cycles.** B never feeds back into A.
- The capability map (BC Map) is the **hub** — most other artefacts soft-link to it by `C-N.M` ID.
- ADRs are **not in the linear chain** but must precede Step 9 (Quality Attributes) and Step 10 (PRDs) when their decisions affect those artefacts.

---

## Recommended build order — greenfield software (default)

When starting a new software product or venture from scratch, follow this
order. Each step has prerequisites + outputs Claude can verify before
moving on.

### Step 0 — Product Vision (why — the north star)

**Skill:** `business-vision`
**Prerequisites:** minimal project context (product name + target audience is enough to scaffold).
**Process:**
- Mode `scaffold` → create `docs/VISION.md` with `_TODO_` placeholders
- Mode `fill` → populate §Elevator Pitch (Moore format) · §Problem We Solve · §World We're Building Toward · §What We Are NOT · §North Star Metric
- Mode `wire` → append vision pointer to project `CLAUDE.md` so every agent session auto-loads the vision
- Mode `refresh` → update when strategy pivots; check cascading effects on personas, objectives, and BMC VPs
**Output verification:** `docs/VISION.md` exists; ≤ 400 words / ≤ 1 page; §Elevator Pitch uses Moore format; §North Star is directional (no baseline/target/deadline — those are KRs); ≥ 3 specific "NOT" guardrails; `CLAUDE.md` contains a vision pointer (Wire mode).

---

### Step 1 — Personas (who)

**Skill:** `business-persona`
**Prerequisites:** Step 0 (Product Vision — if it exists, read it; personas should reflect the vision's target audience framing)
**Process:**
- Mode `scaffold` → create `docs/business/01a-personas.md`
- Mode `backlog` → identify Tier-1 / Tier-2 / Tier-3 personas with Cooper persona types
- Mode `fill-one` → write 1–3 Tier-1 personas as proto-personas (Lean UX) or research-grounded (BABOK §10.43)
**Output verification:** `personas.md` exists; ≥1 Tier-1 persona filled; `P-01` through `P-NN` assigned.

### Step 2 — Business Model Canvas / Lean Canvas (commercial wrapper)

**Skill:** `business-model-canvas`
**Prerequisites:** Step 1 (personas exist for Customer Segments soft-link).
**Process:**
- Pick variant: BMC (established) or Lean Canvas (startup) at scaffold.
- Mode `scaffold` → `docs/business/02a-bmc.md` (or `docs/business/02a-lean-canvas.md`)
- Mode `fill` → populate all 9 blocks with 3–7 terse bullets + confidence rating (Assumed/Tested/Validated)
- Mode `vpc` (optional) → one VPC companion per Tier-1 segment
**Output verification:** canvas file exists; Customer Segments link to `P-NN`; ≥1 segment populated.

### Step 3 — Business Capability Map (what abilities)

**Skill:** `business-capability-map`
**Prerequisites:** Steps 1–2 (personas for context; BMC for commercial framing).
**Process:**
- Choose L0 axis (product / value-stream / capability-domain / LOB / segment / custom). Default `capability domain` if unsure.
- Mode `scaffold` → `docs/business/03a-capability-map.md`
- Mode `structure` → enumerate L0 items (3–8) + L1 capabilities (5–12 per L0; ≤25 total)
- Mode `fill` → per-capability blocks (Definition + Business Object + Strategic Importance + Outcomes + Boundaries)
**Output verification:** capability map exists; `C1` through `C-N.M` assigned; ≥6 L1 capabilities filled; each capability passes noun test + tech-independence test + anti-overlap test.

### Step 2b — Bounded Context Map (domain boundaries)

**Skill:** `domain-bounded-context`
**Prerequisites:** Step 2 (Capability Map — capabilities are the raw material for BC identification); Step 1 (Personas — personas ground the ubiquitous language scope); Step 3 (Value Streams — stage boundaries signal context boundaries; run after value streams are catalogued).
**Process:**
- Mode `discover` → read capability map + value streams; group capabilities by domain cohesion; identify boundary signals (where same word means different things; where data ownership changes; where team handoff happens); name bounded contexts
- Classify each BC: Core (competitive differentiator) / Supporting (enables Core) / Generic (commodity — buy or outsource)
- Mode `fill` → per-BC definition sections + context map with integration patterns (ACL, Shared Kernel, Customer-Supplier, Open Host Service, Published Language, Conformist)
**Output verification:** `bounded-contexts.md` + `context-map.md` exist; every capability `C-N.M` assigned to exactly one `BC-NN`; each BC has subdomain type + rationale; context map names integration patterns (not just "they communicate"); 1–3 Core subdomains.

### Step 2c — Domain Glossary (ubiquitous language)

**Skill:** `domain-glossary`
**Prerequisites:** Step 2b (Bounded contexts provide the namespace — one glossary section per BC).
**Process:**
- Mode `seed` → extract nouns from capability names + value stream stage names + process actor names; assign `GT-NN` IDs per BC; write one-line definitions
- Mode `enrich` → full definitions in business language + example sentences + deprecated aliases + cross-context translations + code convention notes
**Output verification:** `glossary.md` exists; every BC-NN has a glossary section; capability names have corresponding GT-NN entries; no living synonyms within a BC; definitions in business language only.
**Living document:** the glossary is never "done" — run Mode `maintain` (Step 0: trigger type + scope) every sprint for Core BC; add changelog entry for every term added, deprecated, or retired; bump `glossary-version` on structural changes.

### Step 4 — Value Streams (how value flows)

**Skill:** `business-value-stream`
**Prerequisites:** Step 1 (triggering stakeholders link to personas); Step 3 (stages consume capabilities by C-N.M ID).
**Process:**
- Mode `scaffold` → `docs/business/04a-value-streams.md`
- Mode `catalogue` → enumerate 3–10 streams per product scope, one per Tier-1 persona × value-proposition pair
- Mode `fill-one` → full stream body with 4–10 stages, each consuming 1–4 capabilities + pain index
**Output verification:** value-streams file exists; ≥1 stream fully filled; each stage links to ≥1 capability by `C-N.M` ID.

### Step 4.5 — Business Objectives (why — strategic intent)

**Skill:** `business-objective`
**Prerequisites:** Step 1 (Personas — whose outcomes the objectives serve); Step 2 (BMC — `VP-NN` Value Propositions are the commercial intent that objectives operationalise); Step 4 (Value Streams — pain index per `VS-N.M` prioritises which objectives matter most).
**Process:**
- Mode `scaffold` → create `docs/business/04b-objectives.md` with OBJ-NN placeholder blocks
- Mode `fill` → populate each OBJ-NN: qualitative title, BSC perspective tag, timeframe, owner, "why it matters" sentence linked to `VP-NN` or `VS-N.M` pain index; 3–5 Key Results per objective (outcome statements with baseline, target, measurement method)
- Mode `align` → after the delivery roadmap exists, build the §Objective × Epic traceability matrix; flag orphaned epics (no OBJ-NN) and undelivered objectives (no E-NN)
- Mode `refresh` → update KR baselines/targets when evidence arrives; add changelog entry
**Output verification:** `objectives.md` exists; ≥1 OBJ-NN filled with qualitative title + BSC perspective + timeframe + owner; every KR is an outcome (metric change), not an output (feature delivery); every OBJ-NN traces to ≥1 `VP-NN` or `VS-N.M`; 2–5 objectives total; ≥1 Customer-perspective objective.

---

### Step 5 — Business Processes (operational how)

**Skill:** `business-process`
**Prerequisites:** Step 4 (processes operationalise value-stream stages — but processes can also exist independently for non-customer-facing operations).
**Process:**
- One process doc per major operational workflow.
- Mode `scaffold` per process → `docs/business/05a-processes/proc-NN-{slug}.md`
- Fill BPMN-ready template (actors, activities, data, KPIs, decisions).
**Output verification:** each Tier-1 value-stream stage has ≥1 process doc operationalising it.

### Step 6 — Quantitative Models (numbers)

**Skill:** `business-quantitative-model`
**Prerequisites:** Step 2 (BMC's Revenue Streams + Cost Structure provide qualitative anchors); Step 1 (personas drive segmentation).
**Process:**
- One model per quantification need: TAM/SAM/SOM, savings, ROI, restitution, unit economics.
- Each model file in `docs/business/06a-models/qm-NN-{topic}.md`.
**Output verification:** ≥1 model exists; BMC's Revenue Streams + Cost Structure link to relevant models.

### Step 7 — Functional Breakdown Structure (what product does, status-tracked)

**Skill:** `spec-functional-breakdown-structure`
**Prerequisites:** Step 3 (BC Map — FBS inherits L0+L1).
**Process:**
- Mode `scaffold` → `docs/product-specs/07a-fbs.md`
- Mode `structure` → auto-import L0+L1 from BC Map; pre-fill per-capability sections
- Mode `fill` → enumerate functionalities per capability with `C-N.M.FXX` IDs + status (✅/🔄/⬜) + optional VS-stage links + code paths
**Output verification:** FBS exists; ≥1 capability has ≥1 functionality; status distribution shows initial state.

### Step 7b — Domain Model (entities · aggregates · value objects · domain events)

**Skill:** `domain-model`
**Prerequisites:** Step 2b (Bounded contexts provide BC-NN namespace); Step 2c (Glossary terms — entity names MUST match GT-NN); Step 7 (FBS — functionalities reveal candidate entities and aggregates); Step 3 (Value Stream stages — stage transitions reveal domain events).
**Process:**
- One `domain-model.md` per bounded context: `docs/domain/07b-models/{bc-slug}.md`
- Mode `fill` → per aggregate: root, invariants, lifecycle states, command→event pairs; per entity: identity, attributes, behaviour methods; per value object: attributes, equality rule, validation invariants; per domain event: trigger, payload, consumers, business significance
- Mode `verify` → check for anemic model (entities must have behaviour); check aggregate sizing (≤5 members); check event naming (past tense + business-meaningful)
**Output verification:** one `domain-model.md` per BC-NN; every aggregate has a named root + ≥2 documented invariants; all entity names match GT-NN glossary terms; all domain events are past tense + carry business significance; Mermaid class diagram present.

### Step 8 — Delivery Roadmap (Plan by Feature + Walking Skeleton + Phase Goals)

**Skill:** `spec-delivery-roadmap`
**Prerequisites:** Step 7 (FBS — VS stage links + phase tags + ★ markers); Steps 3–4 (Value Streams — pain index + value propositions); Step 1 (Personas — for walking skeleton narrative).
**Process:**
- Read FBS + value streams + personas
- Group FBS functionalities by VS stage affinity + capability cluster → E-NN epics
- Order by pain index; assign E-NN IDs in priority order
- Define Walking Skeleton: identify the primary VS to validate; select minimum functionalities per epic covering every VS stage end-to-end; write "can / cannot yet" statement
- Define Phase Plan: declare which VS streams become fully operational per phase; write one-sentence goal per phase
- Produce `docs/product-specs/08a-delivery-roadmap.md`
- Coverage check: every Phase 1 FBS functionality in exactly one epic
**Output verification:** `docs/product-specs/08a-delivery-roadmap.md` exists; §Walking Skeleton covers every stage of primary VS; §Phase Plan has one goal per phase expressed as VS streams operational; every epic has a value statement; ★ functionalities each anchor their own epic; sizing within 5–25 FBS rows per epic; E-NN IDs in pain-index order.

### Step 9 — Quality Attributes (how well the system performs)

**Skill:** `spec-quality-attributes`
**Prerequisites:** Step 7 (FBS differentiators ★ drive Reliability targets); Step 8 (epic scope clarifies which QA entries apply to which delivery cluster); relevant ADRs (Security, Flexibility, Maintainability QAs reference ADR decisions); Step 1 (Personas ground IC and PE entries); Steps 3–4 (VS pain index prioritises PE entries).
**Process:**
- Mode `scaffold` → create `docs/product-specs/09a-quality-attributes.md` with ISO/IEC 25010:2023 characteristic sections
- Mode `fill` → one entry per sub-characteristic × product scope; measurable acceptance criterion + verification method; persona-grounded for IC and PE; reference ADR IDs for Security/Flexibility/Maintainability decisions
**Output verification:** file exists; ≥1 entry per relevant ISO characteristic; all entries have measurable acceptance criteria; IC/PE entries reference P-NN personas; differentiator FBS features (★) have Reliability entries.

### Step 10 — PRDs (Build by Feature)

**Skill:** `spec-prd`
**Prerequisites:** Step 8 (one PRD per E-NN epic — scope pre-defined); Step 9 (PRDs reference `QA-XXNN` in acceptance criteria); relevant ADRs (PRDs do not re-open decided architectural choices).
**Process:**
- One PRD per epic: `docs/product-specs/prds/prd-NNNN-{feature}.md`
- Each PRD: §0 Architecture Traceability (E-NN, P-NN, C-N.M, QA-XXNN, FBS scope) · problem · goals · non-goals · user stories (persona-grounded, P-NN) · acceptance criteria · success metrics
**Output verification:** ≥1 PRD per active epic (E-NN); each PRD references its E-NN, FBS IDs, and QA IDs; FBS functionality status promoted ⬜ → 🔄; Delivery Roadmap PRD link filled.

### Step 11 — Implementation Plans (atomic increments)

**Skill:** `spec-implementation-plan`
**Prerequisites:** Step 10 (PRDs).
**Process:**
- One plan per PRD: `docs/exec-plans/active/{NNNN}_{slug}/`
- Each plan: numbered increments (Inc-1, Inc-2, …), each small + testable + reversible.
**Output verification:** each in-flight PRD has a corresponding plan; plan increments are atomic + testable.

### Ongoing — ADRs, runbooks, ideas, audit

Not numbered in the linear build order but sequencing matters:
- `arch-adr` → invoke as soon as an architectural choice must be made; ADRs governing security, flexibility, or maintainability must precede Step 9 (Quality Attributes); all ADRs must precede Step 10 (PRDs) that depend on their decisions
- `ops-runbook` → operational procedures captured post-ship
- `ops-bug-rca` → root cause analyses post-incident
- `spec-idea` → pre-PRD idea capture (becomes a PRD when committed)
- `spec-peer-review` → PRD / plan review before implementation
- `util-docs-audit` → periodic health check (quarterly)

---

## Variants for non-greenfield projects

### Brownfield IT project (existing system, adding capability)

Start at **Step 3** (Business Capability Map), skip Steps 1–2 unless:
- The capability touches a stakeholder group not yet documented (then do Step 1 lightweight for that persona).
- The capability changes the commercial model (then do Step 2 — usually skipped).

**Sequence:** Step 3 (BC Map) → Step 4 (value stream for the affected flow) → Step 5 (process docs for the as-is operational state) → Step 2b (Bounded Context Map) → Step 2c (Glossary) → Step 7 (FBS) → Step 7b (Domain Model) → Step 8 (Delivery Roadmap) → Step 9 (Quality Attributes — at minimum Reliability entries for new differentiator features) → Step 10 (PRDs) → Step 11 (plans).

### Single feature (no full architecture work)

Skip Steps 1–8 entirely. Go straight to:
- Step 10 (`spec-prd`) for the feature — manually define the E-NN scope inline in §0.
- Step 11 (`spec-implementation-plan`) for the plan.

Optionally: `spec-idea` first if the feature is still hypothetical. Write relevant ADRs before the PRD if architecture decisions are open. Write domain model for the feature's aggregate (Step 7b) if the aggregate isn't already modelled.

### Strategy / investor / executive engagement only

Start at **Step 2** (BMC) for the strategic one-pager. Skip Steps 7–11 entirely. Optionally add:
- Step 1 (personas) — investors love seeing customer specificity.
- Step 6 (quantitative model) — TAM/SAM/SOM for the deck.
- Step 3 (BC Map) — only if the strategic conversation needs the capability lens.

---

## Cross-doc ID conventions

| ID format | Meaning | Owned by |
|---|---|---|
| `P-NN` | Persona | `business-persona` |
| `C-N.M` (e.g. `C1`, `C1.1`, `C1.1.1`) | Capability (L0 / L1 / L2) | `business-capability-map` |
| `VS-N` | Value stream | `business-value-stream` |
| `VS-N.M` | Value-stream stage | `business-value-stream` |
| `OBJ-NN` | Business Objective | `business-objective` |
| `KR-NN.M` | Key Result (M under Objective N) | `business-objective` |
| `C-N.M.FXX` | Functionality (capability + counter) | `spec-functional-breakdown-structure` |
| `BC-NN` | Bounded Context | `domain-bounded-context` |
| `BC-NN.GT-NN` | Glossary Term (scoped to bounded context) | `domain-glossary` |
| `BC-NN.AGG-NN` | Aggregate root (scoped to bounded context) | `domain-model` |
| `BC-NN.ENT-NN` | Entity (scoped to bounded context) | `domain-model` |
| `BC-NN.VO-NN` | Value Object (scoped to bounded context) | `domain-model` |
| `BC-NN.EVT-NN` | Domain Event (scoped to bounded context) | `domain-model` |
| `E-NN` | Epic + walking skeleton + phase plan (delivery roadmap) | `spec-delivery-roadmap` |
| `QA-XXNN` | Quality attribute (characteristic prefix + counter, e.g. `QA-PE01`, `QA-SE03`) | `spec-quality-attributes` |
| `PRD-NNNN` | PRD ID | `spec-prd` |
| `Plan-NNNN` | Implementation plan | `spec-implementation-plan` |
| `Inc-N` (within a plan) | Plan increment | `spec-implementation-plan` |
| `ADR-NNNN` | Architecture decision | `arch-adr` |
| `Research-NNNN` | Architecture research note | `arch-research` |
| `CO-NN` | Competitor profile (Tier-1) | `business-competitive-landscape` |
| Block ID in BMC (e.g., `CS-1`, `VP-1`) | Canvas block | `business-model-canvas` |

**BC-NN namespace rule:** All tactical DDD IDs are scoped to their bounded context. `BC-01.AGG-03` and `BC-02.AGG-03` are different aggregates. Cross-references must always include the BC prefix — bare `AGG-03` is ambiguous and invalid.

**Cross-doc linking rule:** any artefact that references another should use the ID + name + relative path:

> `[C3.2 KOGU prior-authorisation classification](../03a-capability-map.md#c32)` 

so that future renames (description text) don't break the link as long as the ID is stable.

---

## Canonical output paths

```
docs/
├── VISION.md                                            ← business-vision (Step 0 — singleton, agent north star)
├── business/                                            ← Business Architecture artefacts (numbered = build order)
│   ├── 01a-personas.md                                   ← business-persona (P-NN)
│   ├── 02a-bmc.md  (or 02a-lean-canvas.md)               ← business-model-canvas (Step 2)
│   ├── 02-vpc-{segment}.md  (optional per CS)           ← BMC VPC companions
│   ├── 03a-capability-map.md                             ← business-capability-map (C-N.M)
│   ├── 04a-value-streams.md                              ← business-value-stream (VS-N.M)
│   ├── 04-vpc-{segment}.md  (optional per VS)           ← VS VPC companions
│   ├── 04b-objectives.md                                ← business-objective (OBJ-NN, KR-NN.M)
│   ├── processes/                                       ← multi-file; keep subfolder
│   │   └── {slug}-process.md (one per process)
│   └── models/                                          ← multi-file; keep subfolder
│       └── {slug}.md (TAM/SAM/SOM, savings, ROI per model)
├── product-specs/                                       ← `spec-` skills (product delivery)
│   ├── 07a-fbs.md                                        ← spec-functional-breakdown-structure (C-N.M.FXX)
│   ├── 08a-delivery-roadmap.md                           ← spec-delivery-roadmap (E-NN)
│   ├── 09a-quality-attributes.md                         ← spec-quality-attributes (QA-XXNN)
│   └── prds/                                            ← all PRDs in dedicated subfolder
│       └── prd-NNNN-{feature}.md (one per PRD)          ← spec-prd (PRD-NNNN)
├── exec-plans/                                          ← `spec-` skills (implementation)
│   └── active/
│       └── {NNNN}_{slug}/  (one folder per plan with increments inside)
├── architecture/                                        ← `arch-` skills
│   └── decisions/                                       ← arch-adr writes here
│       └── {NNNN}-{slug}.md
├── domain/                                              ← `domain-` skills (DDD artefacts — no step prefix; named by type)
│   ├── bounded-contexts.md                              ← domain-bounded-context (BC-NN)
│   ├── context-map.md                                   ← domain-bounded-context (context map)
│   ├── glossary.md                                      ← domain-glossary (BC-NN.GT-NN)
│   └── models/                                          ← consolidated domain models
│       └── {bc-slug}.md                                 ← domain-model (one per BC)
├── ops/                                                 ← `ops-` skills
│   ├── runbooks/
│   │   └── {slug}.md
│   └── rcas/
│       └── {YYYY-MM-DD}-{slug}.md
├── communication/                                       ← `com-` skills
│   └── slides/
│       └── {slug}/                                      ← com-slide-deck (one folder per deck)
│           ├── context/
│           ├── design/
│           ├── src/                                     ← slide partials (source of truth)
│           ├── dist/                                    ← built HTML + prototypes/
│           └── config.yaml
└── ideas/                                               ← `spec-idea` (pre-PRD)
    └── {slug}.md
```

**Prefix → folder mapping (memorise this):**

| Prefix | Folder | Note |
|---|---|---|
| `business-` | `docs/business/` | All BIZBOK Business Architecture artefacts. **Exception:** `business-vision` outputs to `docs/VISION.md` (project root level) for agent-context visibility — the only `business-` skill whose output is not under `docs/business/`. |
| `spec-` | `docs/product-specs/`, `docs/exec-plans/`, `docs/ideas/` | Product specs, plans, pre-PRD ideas |
| `arch-` | `docs/architecture/` | Subfolders per artefact (e.g., `decisions/` for ADRs) |
| `domain-` | `docs/domain/` | DDD artefacts — the shared language between business and tech (bounded contexts, glossary, domain model) |
| `ops-` | `docs/ops/` | Subfolders per artefact (`runbooks/`, `rcas/`) |
| `com-` | `docs/communication/` | Communication artefacts (slide decks, presentations). Subfolders per artefact type (e.g. `slides/`). |
| `dev-` | *(no doc folder)* | Developer-workflow utilities |
| `util-` | *(no doc folder)* | Housekeeping |

---

## How Claude should use this rule

When the user invokes documentation work on a project:

1. **Detect what already exists** — `find docs -type d` to map the current state.
2. **Identify which steps are done vs missing** by checking output paths above.
3. **Pick the variant** (greenfield / brownfield / single-feature / strategy-only) based on user intent.
4. **Execute the next step** using the corresponding skill in its appropriate mode.
5. **Verify the output** before moving on — each step's "Output verification" criteria.
6. **Maintain cross-doc IDs** — every soft-link should use the ID + path format above.

When asked *"build the documentation plan"* without further context, default to:
- Confirm the variant with the user (greenfield is the default).
- Start at Step 1; ask for personas input.
- Proceed sequentially through verification checks.
- One step per session unless the user wants batch execution.

This rule is the single source of truth for the strategic-architecture
build order. When new skills join the kit, update the layer table and
DAG here.

**Maintenance coupling — update these files whenever this rule changes:**

Every change to canonical paths, artefact steps, or ID formats in this file has downstream copies that must be kept in sync:

| What changed | Also update |
|---|---|
| New artefact step, new canonical path | `util-metamodel-audit/references/check-catalogue.md` → Check 1 (stack progress paths) |
| New ID format (e.g. new `XX-NN` pattern) | `util-metamodel-audit/references/check-catalogue.md` → Check 5 (ID cross-reference regex patterns) |
| New prerequisite dependency in the DAG | `util-metamodel-audit/references/check-catalogue.md` → Check 7 (dependency enforcement rules) |
| New artefact step, new canonical path | `util-metamodel-migration/references/detection-signals.md` → §Filename patterns + §Folder name patterns + §Content signals |
| New mandatory section in a skill's template | `util-metamodel-audit/references/check-catalogue.md` → Check 9 (mandatory sections table) |

Failing to update these files after a metamodel change will cause the audit and migration skills to silently miss the new artefact — the most dangerous kind of drift.

**Already-updated coupling (business-vision, Step 0, 2026-05-21):**
`rules/metamodel.md` artefact table (row 0) + build order §0 + DAG + ER diagram + canonical paths + prefix exception note + this table · `README.md` flowchart (S0 node + edges) + ER diagram + skill index · `util-metamodel-audit/references/check-catalogue.md` Checks 1, 2 · `util-metamodel-migration/references/detection-signals.md` §Filename + §Content signals · `business-persona/SKILL.md` · `business-model-canvas/SKILL.md` · `business-objective/SKILL.md` · `spec-delivery-roadmap/SKILL.md` · `spec-prd/SKILL.md`

**Already-updated coupling (business-objective, Step 4.5, 2026-05-21):**
`rules/metamodel.md` artefact table + build order §4.5 + DAG + ER diagram + ID conventions + canonical paths + this table · `README.md` flowchart + ER diagram + skill index · `util-metamodel-audit/references/check-catalogue.md` Checks 1, 2, 5, 7, 9 · `util-metamodel-migration/references/detection-signals.md` §Filename + §Folder + §Content signals · `spec-delivery-roadmap/SKILL.md` · `spec-prd/SKILL.md` · `spec-quality-attributes/SKILL.md` · `business-value-stream/SKILL.md` · `business-model-canvas/SKILL.md`
