# Skill backlog

Candidate skills to add to the kit, ordered by metamodel impact. Generated 2026-05-20 from a gap analysis of the 14-artefact stack; updated 2026-05-21 after shipping 5 items (see §Shipped below).

---

## Shipped — 2026-05-21

| Skill / task | What was done |
|---|---|
| **`business-vision`** | Step 0 — singleton `docs/VISION.md`, Moore elevator pitch + Sinek WHY + Pichler Vision Board + North Star metric. Wire mode appends agent context pointer to project CLAUDE.md. |
| **`business-objective`** | Step 4.5 — `docs/business/04b-objectives.md`, OKR structure (OBJ-NN + KR-NN.M), outcome discipline gate, BSC 4-perspective tag, Align mode for epic traceability. |
| **`com-slide-deck`** | Renamed from `dev-slide-deck`. Introduced new `com-` prefix category for communication artefacts. install.sh dangling-symlink prune bug fixed. |
| **v2 path simplification** | All 11 singleton artefacts flattened to numbered files (`01-personas.md`, `02-bmc.md`, `03-capability-map.md`, `04-value-streams.md`, `04b-objectives.md`, `07-fbs.md`, `08-delivery-roadmap.md`, `09-quality-attributes.md`; domain singletons flattened; domain models consolidated into `docs/domain/models/{bc-slug}.md`). Kit fully updated: 15 SKILL.md files, metamodel.md, README.md, check-catalogue.md, detection-signals.md. 4 pre-existing `epic-catalogue.md` bugs fixed. |
| **`util-metamodel-migration` Mode 4** | Schema migration mode — reads `references/path-migration-v2.md`, generates atomic `git mv` + `sed` script for v1→v2 project migration. Dry-run default; `--apply` opt-in; post-migration audit hook. |

---

## Tier 1 — High impact, direct metamodel gap

| Skill | Output path | Gap filled | New ID | Upstream links |
|---|---|---|---|---|
| **`arch-c4`** | `docs/architecture/c4/` | The kit has the full business + domain + product stack but no structural system diagram. C4 (Simon Brown) adds Context, Container, Component views — the "what does the system look like architecturally" layer. | `C4-L1`, `C4-L2`, `C4-L3` | `BC-NN`, `ADR-NNNN`, `QA-XXNN` |
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

---

## Tier 3 — Useful, lower metamodel coupling

| Skill | Gap filled |
|---|---|
| **`spec-release-plan`** | Release communication + rollout per E-NN epic. Feature flag plan, comms template, rollback criteria. Bridges delivery roadmap → ops. |
| **`ops-post-mortem`** | Blameless post-mortem for operational incidents. `ops-bug-rca` is code-level; post-mortem is broader org-wide incident review with timeline, contributing factors, action items. |
| **`business-stakeholder-map`** | RACI / stakeholder influence-interest grid. Internal actors vs. customers. Links to processes (actors) and value streams (stage owners). |
| **`dev-changelog`** | CHANGELOG.md management per Keep a Changelog. Bridges commit history → user-facing release notes. |
| **`dev-tech-debt`** | Log tech debt items as they are discovered — during code review, refactoring, or implementation. Each entry captures location (file + line), category (design debt / test debt / documentation debt / dependency debt), severity, discovery context, and estimated remediation effort. Output: `TECH_DEBT.md` at repo root. Companion to `ops-bug-rca` (bugs) and `arch-adr` (architectural decisions) — tech debt sits between the two. |

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
