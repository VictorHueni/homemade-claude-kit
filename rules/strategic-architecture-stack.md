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

## The 11 artefacts and their skills

| # | Layer | Skill | Output file | Primary IDs |
|---|---|---|---|---|
| 1 | **Personas** (who) | `business-persona` | `docs/business/personas/personas.md` | `P-NN` |
| 2 | **Business Capability Map** (what abilities) | `business-capability-map` | `docs/business/capability-map/capability-map.md` | `C1`, `C1.1`, `C1.1.1` (L2 rare) |
| 3 | **Value Streams** (how value flows) | `business-value-stream` | `docs/business/value-streams/value-streams.md` + `value-proposition-canvas-{segment}.md` (optional VPC per VS) | `VS-N`, `VS-N.M` (stages) |
| 4 | **Business Processes** (operational how) | `business-process` | `docs/business/processes/{slug}-process.md` (one file per process) | per-process slug |
| 5 | **Business Model Canvas** (commercial wrapper) | `business-model-canvas` | `docs/business/business-model-canvas/business-model-canvas.md` or `lean-canvas.md` + optional `value-proposition-canvas-{segment}.md` | block IDs (CS-N, VP-N, …) |
| 6 | **Quantitative models** (numbers) | `business-quantitative-model` | `docs/business/models/{slug}.md` | per-model slug |
| 7 | **Functional Breakdown Structure** (functionality registry) | `spec-functional-breakdown-structure` | `docs/product-specs/functional-breakdown-structure/FBS.md` | `C-N.M.FXX` (capability + functionality counter) |
| 8 | **Epic Catalogue** (Plan by Feature — delivery grouping) | `spec-epic-catalogue` | `docs/product-specs/epic-catalogue.md` | `E-NN` |
| 9 | **Quality Attributes** (how well the system performs) | `spec-quality-attributes` | `docs/product-specs/quality-attributes/quality-attributes.md` | `QA-PE01`, `QA-SE03` … (characteristic prefix + counter) |
| 10 | **PRDs** (feature specs — Build by Feature) | `spec-prd` | `docs/product-specs/[NNNN]_prd_[feature].md` | `PRD-NNNN` |
| 11 | **Implementation plans** (atomic increments) | `spec-implementation-plan` | `docs/exec-plans/active/{NNNN}_{slug}/` | `Plan-NNNN`, `Inc-N` |

**Supporting skills** (not in the main build order, used as needed):
- `arch-adr` — Architecture Decision Records → `docs/architecture/decisions/{NNNN}-{slug}.md`. **Sequencing rule:** ADRs governing security, flexibility, or maintainability must be written before Step 9 (Quality Attributes) so the QA doc can reference them. All ADRs must precede Step 10 (PRDs) that depend on their decisions. Invoke ADRs as soon as an architectural choice must be made — they are not a post-hoc documentation exercise.
- `spec-idea` — captures pre-PRD ideas → `docs/ideas/{slug}.md`
- `spec-peer-review` — reviews PRDs / plans
- `business-competitive-landscape` — Porter Five Forces + Strategic Group Map + Value Curve + per-competitor profiles → `docs/business/competitive-landscape/`; soft-links to personas (P-NN), BMC, capability map (C-N.M), quantitative models; run **after Step 1 (Personas)** so competitor ICPs can be mapped to persona IDs, and **before Step 2 (BMC) is filled** so competitive positioning informs the Value Propositions block rather than following it; alternatively run alongside Step 6 (quantitative models) when the primary need is competitor pricing or market-sizing data
- `ops-runbook`, `ops-bug-rca` — operational artefacts (post-ship)
- `util-docs-audit` — periodic health check
- `dev-*` skills — developer workflow (git, PR, worktree, slide deck)

---

## Dependency graph (DAG)

```
                       ┌────────────────────────┐
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
   │ spec-epic-catalogue  │
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

**Hard rules of the graph:**
- An arrow `A → B` means *B soft-links to A by ID*. B can be scaffolded without A existing (placeholder `_TODO_`), but the link is filled when A arrives.
- **No cycles.** B never feeds back into A.
- The capability map (BC Map) is the **hub** — most other artefacts soft-link to it by `C-N.M` ID.
- ADRs are **not in the linear chain** but must precede Step 8 (Quality Attributes) and Step 9 (PRDs) when their decisions affect those artefacts.

---

## Recommended build order — greenfield software (default)

When starting a new software product or venture from scratch, follow this
order. Each step has prerequisites + outputs Claude can verify before
moving on.

### Step 1 — Personas (who)

**Skill:** `business-persona`
**Prerequisites:** project context (PRD-equivalent doc, README, vision statement, or interview notes)
**Process:**
- Mode `scaffold` → create `docs/business/personas/personas.md`
- Mode `backlog` → identify Tier-1 / Tier-2 / Tier-3 personas with Cooper persona types
- Mode `fill-one` → write 1–3 Tier-1 personas as proto-personas (Lean UX) or research-grounded (BABOK §10.43)
**Output verification:** `personas.md` exists; ≥1 Tier-1 persona filled; `P-01` through `P-NN` assigned.

### Step 2 — Business Model Canvas / Lean Canvas (commercial wrapper)

**Skill:** `business-model-canvas`
**Prerequisites:** Step 1 (personas exist for Customer Segments soft-link).
**Process:**
- Pick variant: BMC (established) or Lean Canvas (startup) at scaffold.
- Mode `scaffold` → `docs/business/business-model-canvas/business-model-canvas.md` (or `lean-canvas.md`)
- Mode `fill` → populate all 9 blocks with 3–7 terse bullets + confidence rating (Assumed/Tested/Validated)
- Mode `vpc` (optional) → one VPC companion per Tier-1 segment
**Output verification:** canvas file exists; Customer Segments link to `P-NN`; ≥1 segment populated.

### Step 3 — Business Capability Map (what abilities)

**Skill:** `business-capability-map`
**Prerequisites:** Steps 1–2 (personas for context; BMC for commercial framing).
**Process:**
- Choose L0 axis (product / value-stream / capability-domain / LOB / segment / custom). Default `capability domain` if unsure.
- Mode `scaffold` → `docs/business/capability-map/capability-map.md`
- Mode `structure` → enumerate L0 items (3–8) + L1 capabilities (5–12 per L0; ≤25 total)
- Mode `fill` → per-capability blocks (Definition + Business Object + Strategic Importance + Outcomes + Boundaries)
**Output verification:** capability map exists; `C1` through `C-N.M` assigned; ≥6 L1 capabilities filled; each capability passes noun test + tech-independence test + anti-overlap test.

### Step 4 — Value Streams (how value flows)

**Skill:** `business-value-stream`
**Prerequisites:** Step 1 (triggering stakeholders link to personas); Step 3 (stages consume capabilities by C-N.M ID).
**Process:**
- Mode `scaffold` → `docs/business/value-streams/value-streams.md`
- Mode `catalogue` → enumerate 3–10 streams per product scope, one per Tier-1 persona × value-proposition pair
- Mode `fill-one` → full stream body with 4–10 stages, each consuming 1–4 capabilities + pain index
**Output verification:** value-streams file exists; ≥1 stream fully filled; each stage links to ≥1 capability by `C-N.M` ID.

### Step 5 — Business Processes (operational how)

**Skill:** `business-process`
**Prerequisites:** Step 4 (processes operationalise value-stream stages — but processes can also exist independently for non-customer-facing operations).
**Process:**
- One process doc per major operational workflow.
- Mode `scaffold` per process → `docs/business/processes/{slug}-process.md`
- Fill BPMN-ready template (actors, activities, data, KPIs, decisions).
**Output verification:** each Tier-1 value-stream stage has ≥1 process doc operationalising it.

### Step 6 — Quantitative Models (numbers)

**Skill:** `business-quantitative-model`
**Prerequisites:** Step 2 (BMC's Revenue Streams + Cost Structure provide qualitative anchors); Step 1 (personas drive segmentation).
**Process:**
- One model per quantification need: TAM/SAM/SOM, savings, ROI, restitution, unit economics.
- Each model file in `docs/business/models/{slug}.md`.
**Output verification:** ≥1 model exists; BMC's Revenue Streams + Cost Structure link to relevant models.

### Step 7 — Functional Breakdown Structure (what product does, status-tracked)

**Skill:** `spec-functional-breakdown-structure`
**Prerequisites:** Step 3 (BC Map — FBS inherits L0+L1).
**Process:**
- Mode `scaffold` → `docs/product-specs/functional-breakdown-structure/FBS.md`
- Mode `structure` → auto-import L0+L1 from BC Map; pre-fill per-capability sections
- Mode `fill` → enumerate functionalities per capability with `C-N.M.FXX` IDs + status (✅/🔄/⬜) + optional VS-stage links + code paths
**Output verification:** FBS exists; ≥1 capability has ≥1 functionality; status distribution shows initial state.

### Step 8 — Epic Catalogue (Plan by Feature)

**Skill:** `spec-epic-catalogue`
**Prerequisites:** Step 7 (FBS fully populated with VS stage links and phase tags); Steps 3–4 (Value Streams with pain index per stage).
**Process:**
- Mode `generate` → read FBS + value streams; group functionalities by VS stage affinity + capability cluster; name each group after the value delivered; order by pain index; assign E-NN IDs; produce `docs/product-specs/epic-catalogue.md`
- Coverage check: every Phase 1 FBS functionality must appear in exactly one epic
**Output verification:** `epic-catalogue.md` exists; every Phase 1 FBS row assigned to an epic; E-NN IDs assigned in pain-index priority order; every epic has a value statement; differentiator (★) functionalities each anchor their own epic; sizing within 5–25 FBS rows per epic.

### Step 9 — Quality Attributes (how well the system performs)

**Skill:** `spec-quality-attributes`
**Prerequisites:** Step 7 (FBS differentiators ★ drive Reliability targets); Step 8 (epic scope clarifies which QA entries apply to which delivery cluster); relevant ADRs (Security, Flexibility, Maintainability QAs reference ADR decisions); Step 1 (Personas ground IC and PE entries); Steps 3–4 (VS pain index prioritises PE entries).
**Process:**
- Mode `scaffold` → create `docs/product-specs/quality-attributes/quality-attributes.md` with ISO/IEC 25010:2023 characteristic sections
- Mode `fill` → one entry per sub-characteristic × product scope; measurable acceptance criterion + verification method; persona-grounded for IC and PE; reference ADR IDs for Security/Flexibility/Maintainability decisions
**Output verification:** file exists; ≥1 entry per relevant ISO characteristic; all entries have measurable acceptance criteria; IC/PE entries reference P-NN personas; differentiator FBS features (★) have Reliability entries.

### Step 10 — PRDs (Build by Feature)

**Skill:** `spec-prd`
**Prerequisites:** Step 8 (one PRD per E-NN epic — scope pre-defined); Step 9 (PRDs reference `QA-XXNN` in acceptance criteria); relevant ADRs (PRDs do not re-open decided architectural choices).
**Process:**
- One PRD per epic: `docs/product-specs/[NNNN]_prd_[feature].md`
- Each PRD: §0 Architecture Traceability (E-NN, P-NN, C-N.M, QA-XXNN, FBS scope) · problem · goals · non-goals · user stories (persona-grounded, P-NN) · acceptance criteria · success metrics
**Output verification:** ≥1 PRD per active epic (E-NN); each PRD references its E-NN, FBS IDs, and QA IDs; FBS functionality status promoted ⬜ → 🔄; Epic Catalogue PRD link filled.

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

**Sequence:** Step 3 (BC Map) → Step 4 (value stream for the affected flow) → Step 5 (process docs for the as-is operational state) → Step 7 (FBS) → Step 8 (Epic Catalogue) → Step 9 (Quality Attributes — at minimum Reliability entries for new differentiator features) → Step 10 (PRDs) → Step 11 (plans).

### Single feature (no full architecture work)

Skip Steps 1–8 entirely. Go straight to:
- Step 10 (`spec-prd`) for the feature — manually define the E-NN scope inline in §0.
- Step 11 (`spec-implementation-plan`) for the plan.

Optionally: `spec-idea` first if the feature is still hypothetical. Write relevant ADRs before the PRD if architecture decisions are open.

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
| `C1`, `C1.1`, `C1.1.1` | Capability (L0 / L1 / L2) | `business-capability-map` |
| `VS-N` | Value stream | `business-value-stream` |
| `VS-N.M` | Value-stream stage | `business-value-stream` |
| `C-N.M.FXX` | Functionality (capability + counter) | `spec-functional-breakdown-structure` |
| `E-NN` | Epic (delivery cluster, Plan by Feature) | `spec-epic-catalogue` |
| `QA-XXNN` | Quality attribute (characteristic prefix + counter, e.g. `QA-PE01`, `QA-SE03`) | `spec-quality-attributes` |
| `PRD-NNNN` | PRD ID | `spec-prd` |
| `Plan-NNNN` | Implementation plan | `spec-implementation-plan` |
| `Inc-N` (within a plan) | Plan increment | `spec-implementation-plan` |
| `ADR-NNNN` | Architecture decision | `arch-adr` |
| Block ID in BMC (e.g., `CS-1`, `VP-1`) | Canvas block | `business-model-canvas` |

**Cross-doc linking rule:** any artefact that references another should use the ID + name + relative path:

> `[C3.2 KOGU prior-authorisation classification](../capability-map/capability-map.md#c32)` 

so that future renames (description text) don't break the link as long as the ID is stable.

---

## Canonical output paths

```
docs/
├── business/                                            ← Business Architecture artefacts
│   ├── personas/
│   │   └── personas.md
│   ├── capability-map/
│   │   └── capability-map.md
│   ├── value-streams/
│   │   ├── value-streams.md
│   │   └── value-proposition-canvas-{segment}.md (optional, per VS)
│   ├── processes/
│   │   └── {slug}-process.md (one per process)
│   ├── business-model-canvas/
│   │   ├── business-model-canvas.md  (or lean-canvas.md)
│   │   └── value-proposition-canvas-{segment}.md (optional, per CS)
│   └── models/
│       └── {slug}.md (TAM/SAM/SOM, savings, ROI per model)
├── product-specs/                                       ← `spec-` skills (product delivery)
│   ├── functional-breakdown-structure/
│   │   └── FBS.md
│   ├── epic-catalogue.md                                     ← spec-epic-catalogue
│   ├── quality-attributes/
│   │   └── quality-attributes.md
│   └── {NNNN}_prd_{feature}.md (one per PRD)
├── exec-plans/                                          ← `spec-` skills (implementation)
│   └── active/
│       └── {NNNN}_{slug}/  (one folder per plan with increments inside)
├── architecture/                                        ← `arch-` skills
│   └── decisions/                                       ← arch-adr writes here
│       └── {NNNN}-{slug}.md
├── ops/                                                 ← `ops-` skills
│   ├── runbooks/
│   │   └── {slug}.md
│   └── rcas/
│       └── {YYYY-MM-DD}-{slug}.md
└── ideas/                                               ← `spec-idea` (pre-PRD)
    └── {slug}.md
```

**Prefix → folder mapping (memorise this):**

| Prefix | Folder | Note |
|---|---|---|
| `business-` | `docs/business/` | All BIZBOK Business Architecture artefacts |
| `spec-` | `docs/product-specs/`, `docs/exec-plans/`, `docs/ideas/` | Product specs, plans, pre-PRD ideas |
| `arch-` | `docs/architecture/` | Subfolders per artefact (e.g., `decisions/` for ADRs) |
| `ops-` | `docs/ops/` | Subfolders per artefact (`runbooks/`, `rcas/`) |
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
