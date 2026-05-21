# homemade-claude-kit

A personal Claude Code toolkit that implements a complete **strategic-architecture documentation system** — from business personas through implementation plans — using composable skills governed by a shared metamodel.

Every skill produces a named artefact with a stable ID. Artefacts cross-link by those IDs. The result is a traceable, auditable documentation stack for any software product or venture.

> **Metamodel:** [`rules/metamodel.md`](./rules/metamodel.md) — canonical artefact definitions, DAG, ID conventions, and build order.

---

## The artefact system

16 artefacts across three layers (Business Architecture · Domain · Product Specs) plus a root Step 0, built in order. Solid arrows = hard dependency. Dashed arrows = supporting skills that validate or enrich without blocking.

```mermaid
flowchart TD
    classDef business fill:#FEF3C7,stroke:#D97706,color:#92400E
    classDef domain   fill:#EDE9FE,stroke:#7C3AED,color:#4C1D95
    classDef specs    fill:#DBEAFE,stroke:#3B82F6,color:#1E40AF
    classDef delivery fill:#D1FAE5,stroke:#10B981,color:#065F46
    classDef support  fill:#F3F4F6,stroke:#9CA3AF,color:#374151

    S0["0 · business-vision · VISION.md · north star"]:::business

    subgraph BA["Business Architecture — Steps 1–6 + 4.5"]
        S1["1 · business-persona · P-NN"]:::business
        S2["2 · business-model-canvas"]:::business
        S3["3 · business-capability-map · C-N.M"]:::business
        S4["4 · business-value-stream · VS-N.M"]:::business
        S4b["4.5 · business-objective · OBJ-NN · KR-NN.M"]:::business
        S5["5 · business-process"]:::business
        S6["6 · business-quantitative-model"]:::business
    end

    subgraph DOM["Domain Layer — Steps 2b · 2c · 7b"]
        S2b["2b · domain-bounded-context · BC-NN"]:::domain
        S2c["2c · domain-glossary · BC-NN.GT-NN"]:::domain
        S7b["7b · domain-model · BC-NN.AGG / ENT / VO / EVT"]:::domain
    end

    subgraph PS["Product Specs — Steps 7–10"]
        S7["7 · spec-functional-breakdown-structure · C-N.M.FXX"]:::specs
        S8["8 · spec-delivery-roadmap · E-NN"]:::specs
        S9["9 · spec-quality-attributes · QA-XXNN"]:::specs
        S10["10 · spec-prd · PRD-NNNN"]:::specs
    end

    subgraph EX["Execution — Step 11"]
        S11["11 · spec-implementation-plan · Plan-NNNN"]:::delivery
    end

    subgraph SUP["Supporting Skills"]
        ADR["arch-adr · ADR-NNNN"]:::support
        CL["business-competitive-landscape"]:::support
        RES["business-research"]:::support
        WS["business-workshop"]:::support
    end

    S0 -.-> S1
    S0 -.-> S2
    S0 -.-> S4b
    S0 -.-> S8
    S1 --> S2
    S1 --> S3
    S1 --> S4
    S3 --> S4
    S4 --> S5
    S2 --> S6
    S1 -.-> S4b
    S2 -.-> S4b
    S4 --> S4b
    S4b -.-> S8
    S4b -.-> S9
    S4b -.-> S10
    S3 --> S2b
    S4 --> S2b
    S2b --> S2c
    S2b --> S7b
    S3 --> S7
    S7 --> S7b
    S2c --> S7b
    S7 --> S8
    S7b --> S10
    S8 --> S9
    S9 --> S10
    S10 --> S11
    ADR -.-> S9
    ADR -.-> S10
    CL -.-> S1
    CL -.-> S2
    RES -.-> S1
    RES -.-> S2
    WS -.-> S3
```

Purple = Domain layer (DDD artefacts)

---

## Data relationships

Each artefact **mints** a primary ID and **consumes** upstream IDs as cross-references. Relationship labels show which ID flows between artefacts.

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
    BOUNDED_CONTEXT {
        string BC_NN PK
        string C_NM FK
        string subdomain_type
    }
    GLOSSARY_TERM {
        string BC_NN_GT_NN PK
        string BC_NN FK
    }
    DOMAIN_MODEL {
        string BC_NN_AGG_NN PK
        string BC_NN FK
        string C_NM_FXX FK
    }
    DOMAIN_EVENT {
        string BC_NN_EVT_NN PK
        string BC_NN_AGG_NN FK
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
    CAPABILITY_MAP ||--o{ BOUNDED_CONTEXT : "capabilities group into"
    PERSONA }o--o{ BOUNDED_CONTEXT : "grounds ubiquitous language"
    VALUE_STREAM }o--o{ BOUNDED_CONTEXT : "stage boundaries signal"
    BOUNDED_CONTEXT ||--o{ GLOSSARY_TERM : "scopes GT-NN terms"
    BOUNDED_CONTEXT ||--o{ DOMAIN_MODEL : "one model per BC"
    FBS ||--o{ DOMAIN_MODEL : "functionalities become entities"
    DOMAIN_MODEL ||--o{ DOMAIN_EVENT : "aggregates produce events"
    PRD }o--o{ DOMAIN_MODEL : "references AGG-NN and EVT-NN"
```

---

## Skill index

| Prefix | Skill | Output | ID minted |
|---|---|---|---|
| `business-` | `business-persona` | `docs/business/personas/personas.md` | `P-NN` |
| `business-` | `business-capability-map` | `docs/business/capability-map/capability-map.md` | `C-N.M` |
| `business-` | `business-value-stream` | `docs/business/value-streams/value-streams.md` | `VS-N` · `VS-N.M` |
| `business-` | `business-process` | `docs/business/processes/{slug}-process.md` | slug |
| `business-` | `business-model-canvas` | `docs/business/business-model-canvas/` | block IDs |
| `business-` | `business-quantitative-model` | `docs/business/models/{slug}.md` | slug |
| `business-` | `business-vision` | `docs/VISION.md` *(Step 0 — singleton, CLAUDE.md wired)* | *(path ref — no ID)* |
| `business-` | `business-objective` | `docs/business/objectives/objectives.md` | `OBJ-NN` · `KR-NN.M` |
| `business-` | `business-competitive-landscape` | `docs/business/competitive-landscape/` | — |
| `business-` | `business-research` | `docs/business/research/` | — |
| `business-` | `business-workshop` | `docs/business/workshops/` | — |
| `domain-` | `domain-bounded-context` | `docs/domain/bounded-contexts/` | `BC-NN` |
| `domain-` | `domain-glossary` | `docs/domain/glossary/glossary.md` | `BC-NN.GT-NN` |
| `domain-` | `domain-model` | `docs/domain/{bc-slug}/domain-model.md` | `BC-NN.AGG-NN` · `BC-NN.EVT-NN` |
| `spec-` | `spec-functional-breakdown-structure` | `docs/product-specs/functional-breakdown-structure/FBS.md` | `C-N.M.FXX` |
| `spec-` | `spec-delivery-roadmap` | `docs/product-specs/delivery-roadmap.md` | `E-NN` |
| `spec-` | `spec-quality-attributes` | `docs/product-specs/quality-attributes/quality-attributes.md` | `QA-XXNN` |
| `spec-` | `spec-prd` | `docs/product-specs/{NNNN}_prd_{feature}.md` | `PRD-NNNN` |
| `spec-` | `spec-implementation-plan` | `docs/exec-plans/active/{NNNN}_{slug}/` | `Plan-NNNN` |
| `spec-` | `spec-idea` | `docs/ideas/{slug}.md` | — |
| `spec-` | `spec-peer-review` | review report | — |
| `arch-` | `arch-adr` | `docs/architecture/decisions/{NNNN}-{slug}.md` | `ADR-NNNN` |
| `ops-` | `ops-runbook` | `docs/ops/runbooks/{slug}.md` | — |
| `ops-` | `ops-bug-rca` | `docs/ops/rcas/{date}-{slug}.md` | — |
| `dev-` | `dev-git-commit` | git commit | — |
| `dev-` | `dev-pr` | GitHub pull request | — |
| `dev-` | `dev-git-worktree` | git worktree | — |
| `dev-` | `dev-ralph-loop` | autonomous increment execution | — |
| `com-` | `com-slide-deck` | HTML slide deck | — |
| `util-` | `util-metamodel-audit` | `var/reports/metamodel-audit/` | — |
| `util-` | `util-docs-audit` | doc health report | — |
| `util-` | `util-toolkit-doctor` | setup health report | — |

---

## Install

```bash
# Clone once
git clone git@github.com:VictorHueni/homemade-claude-kit.git ~/projects/homemade-claude-kit

# Symlink everything globally (~/.claude/skills/ + ~/.claude/commands/ + ~/.claude/rules/)
./install.sh
```

## Update

```bash
cd ~/projects/homemade-claude-kit
git pull
# Symlinks already point here — done.
```

## Adding a skill

1. Create `{skill-name}/SKILL.md` following the naming convention in [`rules/skill-creation-sync.md`](./rules/skill-creation-sync.md)
2. Run `./install.sh` to symlink it
3. Register it in [`rules/metamodel.md`](./rules/metamodel.md) if it produces a metamodel artefact
4. Commit and push
