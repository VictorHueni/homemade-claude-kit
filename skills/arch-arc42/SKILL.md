---
name: arch-arc42
description: "Author and refresh the four narrative arc42 sections that have no C4 diagram counterpart: §2 Constraints (mints CST-NN), §4 Solution Strategy (links to ADRs, no new IDs), §8 Cross-Cutting Concepts (mints CC-NN), §11 Risks and Technical Debt (mints RSK-NN). Each section is a distinct mode. Reads upstream artefacts (ADRs, quality attributes, bounded contexts, FBS, personas) to fill content — never invents architectural decisions. Output: docs/architecture/arc42/02-constraints.md, 04-solution-strategy.md, 08-cross-cutting-concepts.md, 11-risks.md. Triggers on: arc42 constraints, architecture constraints, solution strategy, solution approach, cross-cutting concerns, cross-cutting concepts, logging strategy, error handling strategy, security concepts, risks, risk register, technical debt register, arc42 §2, arc42 §4, arc42 §8, arc42 §11."
version: "1.0.0"
status: active
last_reviewed: 2026-05-28
review_interval: 365d
supersedes: ~
superseded_by: ~
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "architecture"
  complexity: "medium"
---

# arc42 narrative sections — §2 / §4 / §8 / §11

Four modes covering the prose-and-table arc42 sections that require no C4 diagram. They are read-heavy: each mode scans existing kit artefacts before proposing any content.

> "Architecture documentation that is divorced from the real decisions and constraints of the project becomes fiction." — arc42 authors

**Companion skills:**
- `arch-c4` — diagram-producing sections §3 / §5 / §6 / §7
- `arch-structurizr` — Structurizr workspace foundation (not required for this skill)
- `arch-adr` — the ADR lifecycle; §4 Solution Strategy links to ADR numbers rather than re-stating rationale

---

## The four modes

| Mode | arc42 § | Output file | New IDs |
|---|---|---|---|
| `constraints` | §2 — Architecture Constraints | `docs/architecture/arc42/02-constraints.md` | `CST-NN` |
| `solution-strategy` | §4 — Solution Strategy | `docs/architecture/arc42/04-solution-strategy.md` | none (links to `ADR-NNNN`) |
| `cross-cutting` | §8 — Cross-Cutting Concepts | `docs/architecture/arc42/08-cross-cutting-concepts.md` | `CC-NN` |
| `risks` | §11 — Risks and Technical Debt | `docs/architecture/arc42/11-risks.md` | `RSK-NN` |

---

## Mode 1 — `constraints` (arc42 §2)

Architecture constraints are requirements that limit the solution space — they are non-negotiable within the project scope. They come from three sources: technical (mandated tech stack, OS, hardware), organizational (team size, timeline, budget, regulatory body), and political/legal (standards, licenses, compliance frameworks).

### Pre-flight

1. Read `docs/VISION.md` if present — the business context shapes which constraints are load-bearing.
2. Read `docs/architecture/decisions/*.md` — ADRs that record "we must use X" are evidence of constraints already decided.
3. Read `docs/product-specs/09a-quality-attributes.md` if present — some QA-XXNN attributes imply hard constraints (e.g. `QA-SE-01: GDPR compliance` → data residency constraint).
4. Read `docs/domain/02b-bounded-contexts.md` if present — Generic subdomains (SaaS providers) often impose integration constraints.

### Step 0 — Context questions

```
1. Technical constraints source?
   A. Read existing ADRs + quality attributes and propose
   B. I'll list the technology mandates interactively
   C. Mix — propose from artefacts, then I'll add/remove

2. Organizational constraints?
   A. Team is internal only, no outsourcing constraints
   B. There are vendor or partner dependencies — I'll describe
   C. Read VISION.md and propose from context

3. Legal / regulatory framework?
   A. GDPR (EU data residency, right to erasure)
   B. PCI DSS (payment card data)
   C. HIPAA (health data)
   D. SOC 2 Type II (enterprise SaaS)
   E. None / other — describe
   F. Auto-detect from quality attributes
```

### Fill process

1. Assign monotonic `CST-NN` IDs to each constraint (never reuse).
2. Classify each constraint as `technical` | `organizational` | `legal-regulatory`.
3. For each ADR that records a mandate, cross-reference it (`ADR-NNNN`) in the Rationale column.
4. Generate `docs/architecture/arc42/02-constraints.md` from `templates/arc42-02-constraints.md`.
5. On refresh: compare to ADR log for newly closed decisions that add constraints; compare to QA register for new compliance requirements.

---

## Mode 2 — `solution-strategy` (arc42 §4)

The solution strategy is a summary of the fundamental architecture decisions: technology choices, top-level decomposition, and how quality goals are addressed. It is intentionally brief — the detail lives in ADRs and other artefacts. §4 is a navigation aid, not a design document.

### Pre-flight

1. **ADRs are required.** If `docs/architecture/decisions/` is empty or missing, recommend running `arch-adr` first. §4 links to ADRs — it does not replace them.
2. Read `docs/product-specs/09a-quality-attributes.md` — quality goals (QA-XXNN) must be explicitly addressed: which architectural tactic or decision satisfies each top-N goal?
3. Read `docs/domain/02b-bounded-contexts.md` — the decomposition approach (how BCs map to services) is a key solution strategy element.
4. Read `docs/architecture/arc42/02-constraints.md` if present — constraints narrow the solution space and should appear as motivation for some decisions.

### Step 0 — Context questions

```
1. Decomposition approach?
   A. Microservices — one service per bounded context
   B. Modular monolith — single deployable with BC modules
   C. Layered monolith — classic n-tier
   D. Serverless — function-per-use-case
   E. Hybrid — I'll describe

2. Primary quality goal (top 1)?
   A. Read from docs/product-specs/09a-quality-attributes.md and propose
   B. State it explicitly

3. Technology philosophy?
   A. Conservative — proven, boring tech; innovation budget is low
   B. Moderate — industry-standard with one or two strategic bets
   C. Progressive — early adopter; fast iteration over stability
```

### Fill process

1. Open `docs/architecture/decisions/` and list all accepted ADRs — extract the `## Decision` line from each as a one-sentence summary.
2. Map each top-5 QA-XXNN quality goal to at least one architectural tactic (e.g. `QA-PE-01 → horizontal scaling via stateless containers`).
3. Summarise the decomposition: how bounded contexts map to deployables (one sentence per BC).
4. Generate `docs/architecture/arc42/04-solution-strategy.md` from `templates/arc42-04-solution-strategy.md`.
5. Do NOT re-state ADR rationale — link with `ADR-NNNN` and one-line summary. The reader opens the ADR for detail.

---

## Mode 3 — `cross-cutting` (arc42 §8)

Cross-cutting concepts are horizontal concerns that span multiple building blocks and are not specific to any single container or component. Examples: security (authentication + authorisation + RBAC), logging and observability, error handling conventions, internationalisation, persistence patterns, API conventions, session management, caching strategy.

### Pre-flight

1. Read `docs/architecture/decisions/*.md` — ADRs on logging, auth, caching, API conventions are the primary source.
2. Read `docs/product-specs/09a-quality-attributes.md` — security, maintainability, and operability QA-XXNN items spawn cross-cutting concepts.
3. Read `docs/architecture/arc42/05-building-blocks.md` if present — the technology stack in §5.1 hints at which cross-cutting concerns are relevant (e.g. Kafka → message ordering and idempotency).

### Step 0 — Context questions

```
1. Authentication / authorisation model?
   A. JWT / OAuth2 — stateless bearer token
   B. Session-based — server-side session store
   C. API key — service-to-service
   D. Mixed (e.g. OAuth2 for users, API key for M2M)
   E. Read ADRs and propose

2. Observability stack?
   A. Structured JSON logs + distributed tracing (OpenTelemetry)
   B. Structured logs only
   C. Traditional application logs (no tracing)
   D. Read ADRs and propose

3. Error handling convention?
   A. RFC 7807 Problem Details (recommended for REST APIs)
   B. Custom envelope (describe)
   C. Exception → HTTP status code mapping (framework default)

4. Which additional concepts apply? (multi-select)
   A. Internationalisation / localisation
   B. Caching strategy (CDN / in-process / distributed)
   C. Saga / compensating transactions (async error recovery)
   D. Idempotency keys (message deduplication)
   E. Feature flags / progressive rollout
   F. Data encryption at rest and in transit
```

### Fill process

1. Assign `CC-NN` IDs (monotonic, never reuse) to each cross-cutting concept.
2. For each concept: write a 2–4 sentence description + link to the governing ADR(s) + note which containers it applies to (reference `CON-NN` if §5 exists).
3. Generate `docs/architecture/arc42/08-cross-cutting-concepts.md` from `templates/arc42-08-cross-cutting.md`.
4. On refresh: check for new ADRs or QA-XXNN items that introduce new concepts; check for concept drift (containers now implement CC differently than documented).

---

## Mode 4 — `risks` (arc42 §11)

Known risks and technical debt items that have not yet been addressed. Each risk has a probability, impact, and mitigation strategy. Technical debt is logged separately with a remediation path.

> arc42 on §11: "A list of identified technical risks or technical debts, ordered by priority."

**Scope of this skill:** architectural and technical risks. Operational risks (infrastructure failure, vendor outage) belong in ops runbooks. Business risks belong in the business model. The boundary is: if the risk is rooted in an architectural decision or a deliberate technical shortcut, it belongs here.

`arch-risks` is not a tech-debt ledger — it captures risks that **should be on an architect's radar now**. Exhaustive debt tracking belongs in a future `dev-tech-debt` skill.

### Pre-flight

1. Read all existing ADRs — superseded ADRs and ADRs with `status: deprecated` often surface risks.
2. Read `docs/product-specs/09a-quality-attributes.md` — QA-XXNN items with low confidence or a `## Open Items` gap may indicate risk.
3. Read `docs/architecture/arc42/05-building-blocks.md` if present — technology choices in §5.1 with known limitations are risk candidates.
4. Read `docs/architecture/arc42/08-cross-cutting-concepts.md` if present — incomplete CC-NN concepts (e.g. "auth model TBD") signal active risks.

### Step 0 — Context questions

```
1. Risk identification source?
   A. Scan ADRs + QA register + building block view and propose
   B. I'll describe the risks interactively
   C. Mix

2. Probability scale?
   A. low / medium / high (default)
   B. Numeric 1–5

3. Impact scale?
   A. low / medium / high / critical (default)
   B. Numeric 1–5
```

### Fill process

1. Assign monotonic `RSK-NN` IDs to each risk.
2. For each risk: classify as `architectural` | `technical-debt` | `dependency` | `security`.
3. Set probability + impact; derive a `severity` = max(probability, impact) for sorting.
4. Write a mitigation strategy (what reduces the risk) and a contingency (what we do if it materialises).
5. For `technical-debt` items: add a `Remediation path` column pointing to the relevant backlog epic or ADR.
6. Generate `docs/architecture/arc42/11-risks.md` from `templates/arc42-11-risks.md`.
7. On refresh: update status for risks that have been mitigated or materialised; archive closed risks to `## Closed Risks` at bottom of file.

---

## Closing report (every mode)

- Mode executed + arc42 section written/updated
- IDs assigned (list `CST-NN` / `CC-NN` / `RSK-NN` ranges; or "none" for §4)
- Upstream artefacts read (list files)
- ADR cross-references linked (list `ADR-NNNN`)
- Open items flagged (any gaps recorded in the artefact's `## Open Items` section)
- Next step suggestion

---

## Reference materials

- `references/arc42-section-02.md` — arc42 §2 specification (embedded)
- `references/arc42-section-04.md` — arc42 §4 specification (embedded)
- `references/arc42-section-08.md` — arc42 §8 specification (embedded)
- `references/arc42-section-11.md` — arc42 §11 specification (embedded)
- `references/methodology-references.md` — bibliography for constraints taxonomy, risk frameworks (ISO 31000, SEI ATAM), cross-cutting patterns

## Templates

- `templates/arc42-02-constraints.md` — §2 skeleton (three-category table; CST-NN IDs)
- `templates/arc42-04-solution-strategy.md` — §4 skeleton (technology table + quality goal → tactic mapping)
- `templates/arc42-08-cross-cutting.md` — §8 skeleton (CC-NN concept catalogue)
- `templates/arc42-11-risks.md` — §11 skeleton (risk register table + tech-debt register)

---

## Checklist (per mode)

- [ ] Upstream artefacts read before proposing content (ADRs, QA register, BC map)
- [ ] IDs assigned monotonically; no duplicates with existing file
- [ ] Every `CST-NN` / `CC-NN` / `RSK-NN` has a cross-reference to at least one ADR or QA-XXNN (or `_TBD_` if genuinely not yet linked)
- [ ] §4 does NOT re-state ADR rationale — links only
- [ ] §11 distinguishes `architectural` risk from `technical-debt`; does NOT attempt to be an exhaustive debt ledger
- [ ] Output file has standard frontmatter (see `rules/artefact-frontmatter.md`)
- [ ] `## Open Items` section present (empty initial state: "None at present.")
- [ ] Closing report delivered
