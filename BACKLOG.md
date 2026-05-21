# Skill backlog

Candidate skills to add to the kit, ordered by metamodel impact. Generated 2026-05-20 from a gap analysis of the 14-artefact strategic-architecture stack.

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

---

## Design tasks — metamodel housekeeping

Non-skill work that improves the kit's internal consistency or usability.

---

### Output path audit + simplification (2026-05-21)

**Problem:** The current canonical output paths have inconsistent nesting depth and no ordering signal. A user browsing `docs/` cannot tell the build sequence from the filenames alone. Some paths are over-nested for no structural reason.

**Specific pain points observed:**

| Current path | Problem |
|---|---|
| `docs/business/personas/personas.md` | Redundant subfolder — one file, one folder, same name. Could be `docs/business/01-personas.md` |
| `docs/business/business-model-canvas/business-model-canvas.md` | Doubly redundant — folder name = file name = artefact name. |
| `docs/domain/{bc-slug}/domain-model.md` | One file per BC, scattered across slug-named subfolders. Finding all domain models requires globbing. Could consolidate into `docs/domain/models/{bc-slug}.md` |
| `docs/domain/bounded-contexts/bounded-contexts.md` + `context-map.md` | Two files in a `bounded-contexts/` subfolder. Could live directly in `docs/domain/`. |
| `docs/domain/glossary/glossary.md` | Same redundancy — `docs/domain/glossary.md` is simpler. |
| `docs/product-specs/functional-breakdown-structure/FBS.md` | Long subfolder for one file. |
| `docs/product-specs/quality-attributes/quality-attributes.md` | Same pattern. |

**Proposed direction (to validate in the design task):**

1. **Numbered flat files per layer** — files carry a step-number prefix so they sort in metamodel build order in any file browser:
   ```
   docs/
   ├── VISION.md                    ← Step 0 (already flat — good)
   ├── business/
   │   ├── 01-personas.md
   │   ├── 02-bmc.md               (or lean-canvas.md)
   │   ├── 03-capability-map.md
   │   ├── 04-value-streams.md
   │   ├── 04.5-objectives.md
   │   ├── 05-processes/           ← keep subfolder (one file per process)
   │   └── 06-models/              ← keep subfolder (one file per model)
   ├── domain/
   │   ├── bounded-contexts.md     ← flat
   │   ├── context-map.md          ← flat
   │   ├── glossary.md             ← flat
   │   └── models/                 ← one file per BC: {bc-slug}.md
   ├── product-specs/
   │   ├── 07-fbs.md
   │   ├── 08-delivery-roadmap.md
   │   ├── 09-quality-attributes.md
   │   └── {NNNN}_prd_{feature}.md
   └── architecture/
       └── decisions/              ← keep (one file per ADR)
   ```

2. **Rule:** subfolders only when there are genuinely multiple files of the same type (processes, models, PRDs, ADRs, domain models). Singletons live as flat files.

3. **Numbering convention:** prefix mirrors the metamodel step number (`01`, `02`, `03`, `04`, `04.5`, ...). Domain layer steps (`2b`, `2c`, `7b`) use their step numbers too.

**Impact if adopted:** HIGH — all canonical paths in `rules/metamodel.md`, every skill's output path, `check-catalogue.md`, `detection-signals.md`, and all cross-reference links in generated project docs would need updating.

**Prerequisite decision:** keep `docs/VISION.md` at root (maximum agent visibility) or move to `docs/00-vision.md` (consistent numbering)? The two goals are in slight tension and must be resolved before any migration work begins.

---

### util-metamodel-migration — Mode 4: Schema migration (2026-05-21)

**Dependency of:** Output path audit + simplification above. Must be built before any project migration can happen safely.

**Why the current skill is insufficient:**

The current `util-metamodel-migration` is a *detection* tool — it scans unknown pre-metamodel repos and guesses canonical paths using 3-tier confidence scoring. A schema migration (v1 paths → v2 paths) is a *transformation* tool. Three fundamental differences:

| Dimension | Current Mode 1–3 (detection) | New Mode 4 (schema migration) |
|---|---|---|
| **Path mapping** | Unknown → inferred from signals | Fully known before/after table |
| **Confidence tiers** | Required (guessing) | Not needed (deterministic) |
| **Scope** | Project docs only | Project docs + kit-internal files (skills, metamodel, audit/migration references) |
| **Relative path arithmetic** | Source folder depth is stable | Depth CHANGES (e.g. `business/personas/personas.md` → `business/01-personas.md`) — every `../` chain must be recomputed |
| **Run cadence** | Once per repo (onboarding) | Once per schema version bump |

**What Mode 4 needs:**

1. **Path mapping table** — a new reference file (e.g. `references/path-migration-v2.md`) containing the full before/after mapping for every artefact. Sourced from the output path audit design task above.

2. **Two-phase execution:**
   - Phase A — **Project migration**: for each project that uses the metamodel, generate `git mv` + relative-path-corrected `sed` commands for all docs. The relative path arithmetic is the hard part — when a file moves up or down in the tree, every inbound link changes its `../` depth.
   - Phase B — **Kit migration**: update the kit's own files — each skill's SKILL.md output path, `rules/metamodel.md` canonical paths, `README.md` skill index, `check-catalogue.md` Check 1/2, `detection-signals.md` filename/folder patterns. This is a separate pass because kit files live outside `docs/` and have different link patterns.

3. **CLAUDE.md awareness** — if `docs/VISION.md` moves, the skill must detect and rewrite the `CLAUDE.md` pointer that `business-vision` Wire mode injected.

4. **Dry-run and apply modes:**
   - `--dry-run` (default): emit the full migration script to a report file, never modify anything
   - `--apply` (explicit opt-in): execute the generated script atomically after user confirmation

5. **Verification hook** — after apply, automatically run `util-metamodel-audit` Mode 1 to confirm zero misplaced files.

**Implementation note:** the relative path rewriting is significantly harder than the current skill's link tracking. When `docs/business/personas/personas.md` moves to `docs/business/01-personas.md` (depth -1), every file that linked with `../../personas/personas.md` must now use `../01-personas.md`. This requires computing the new relative path from each linking file's location to the new target — the current skill does this with a `python3 os.path.relpath()` call, but the schema migration must do it for every artefact in every project simultaneously.

**Recommended build order:**
1. Finish the output path audit design task (settle numbering convention + before/after table)
2. Build Mode 4 against the agreed-upon path mapping table
3. Test on a sample project before running against production repos
4. Update the kit atomically in one branch (Phase B) after all projects are migrated (Phase A)
