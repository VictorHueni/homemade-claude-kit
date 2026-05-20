---
name: spec-epic-catalogue
description: "Create an Epic Catalogue — the 'Plan by Feature' artefact that groups FBS functionalities into named, scoped, priority-ordered delivery units (epics) bridging the FBS (what the product does) and PRDs (what we build next). Each epic has a stable E-NN ID, a VS stage anchor, a FBS scope list, and a PRD link. Triggers on: epic catalogue, epic list, plan by feature, group features into epics, define epics, epic planning, feature grouping, epic scope, what PRDs to write."
version: "1.0.0"
user-invocable: true
allow_implicit_invocation: false
impact: "low"
metadata:
  category: "specification"
  complexity: "low"
---

# Epic Catalogue Builder

You are an expert at producing **Epic Catalogues** — the "Plan by Feature"
artefact that bridges the Functional Breakdown Structure (what the product
does) and PRDs (what we build next). An epic is a named, scoped delivery
unit: a coherent cluster of FBS functionalities that can be designed, built,
and tested together, producing recognisable value for a specific persona.

The artifact produced by this skill is a single markdown file at
`docs/product-specs/epic-catalogue.md`. It is NOT a feature backlog, NOT
a roadmap with dates, NOT a user story map — it is **the delivery planning
layer** that answers: "given everything in the FBS, what should we commit
to building, in what clusters, and in what order?"

---

## Methodology foundation

This skill synthesises four traditions:

| Source | What it anchors |
|---|---|
| Coad, P. & De Luca, J. (1999). *Java Modeling in Color with UML.* Prentice Hall. | FDD Phase 3 "Plan by Feature" — feature set → milestone → owner; the epic as a named Business Activity cluster |
| Leffingwell, D. (2011). *Agile Software Requirements.* Addison-Wesley. §Feature | Feature as the programme-level delivery unit; feature-to-epic grouping heuristics; outcome-orientation |
| Cohn, M. (2004). *User Stories Applied.* Addison-Wesley. §Epic | Epic definition: a story or feature cluster too large for one sprint; sizing trigger (INVEST "S") |
| Patton, J. (2014). *User Story Mapping.* O'Reilly. §Backbone | Backbone Activities = epics; naming after the value delivered, not the feature implemented; release slice as epic boundary |
| BABOK v3 §9.6 (IIBA, 2015). | Solution scope per delivery increment; traceability from scope to requirements |

**FDD Phase 3 "Plan by Feature" — the primary anchor:**

> *"For each Business Activity (feature set), identify: the milestone by which
> it must be complete, the chief programmer responsible, and the sequence
> relative to other feature sets. The planning output is a feature set list
> ordered by delivery sequence, not by domain hierarchy."*
> — De Luca & Coad, FDD methodology

In our stack, the FBS capability domain provides the domain hierarchy
(like FDD's Subject Area → Business Activity). The Epic Catalogue produces
the delivery-sequence ordering — the same output as FDD's Plan by Feature,
grounded in value stream pain index rather than calendar milestones.

---

## What an epic is — and is not

**Is:** a named cluster of FBS functionalities that:
- Delivers recognisable value to a specific persona when complete
- Can be specified in a single PRD
- Can be designed, built, and tested as a coherent unit
- Has a stable E-NN ID usable as a cross-doc reference

**Is not:**
- A capability (that belongs to the BC Map)
- A user story (that belongs to the PRD)
- A sprint (that belongs to the implementation plan)
- A value stream (that belongs to the value stream doc)

**Sizing (Cohn + Leffingwell):** an epic typically covers 8–22 FBS
functionalities and represents 2–8 weeks of focused development. If a
cluster has < 5 FBS rows, it may be too thin for a standalone PRD —
consider merging with an adjacent epic. If > 25 FBS rows, it is too
coarse — split into two epics by VS stage or capability boundary.

---

## The two modes

### Mode 1 — Generate

**When:** FBS exists and PRDs have not yet been written.

**Process:**

**Step 0 — Read upstream artefacts**

```bash
cat docs/product-specs/functional-breakdown-structure/FBS.md
cat docs/business/value-streams/value-streams.md
cat docs/business/personas/personas.md
```

Extract from the FBS:
- Every functionality ID (`C-N.M.FXX`) with its VS stage link and phase tag
- The differentiator (★) markers — these functionalities anchor the most critical epics

Extract from the value streams:
- Pain index per VS stage (Critical → High → Medium → Low)
- Triggering persona per value stream

**Step 1 — Group by VS stage affinity**

Group FBS functionalities by their VS stage column. Functionalities with
`—` (no VS stage) attach to the capability domain epic that is most
contextually relevant.

Functionalities that span multiple VS stages belong to the stage they
primarily enable (the stage where they are a prerequisite).

**Step 2 — Cluster into epics**

Within each VS stage group, look at which capabilities are involved.
Apply the FDD "Business Activity" principle: functionalities that always
ship together and operationalise the same user activity form one epic.

**Clustering heuristics:**
- Same L0 capability domain + same VS stage anchor → strong clustering signal
- Differentiator (★) functionality → anchors its own epic (never merge into a secondary epic)
- Configuration / setup functionalities (C1.x, C2.x) may cluster together even if they span multiple VS stages, because they are all prerequisites before any schedule generation can run
- Platform / governance functionalities (C6.x) cluster together as a cross-cutting epic

**Step 3 — Name each epic**

Apply Patton's naming discipline: name after the **value delivered**, not
the features implemented. The name should complete the sentence: "when this
epic ships, the team can..."

| ❌ Feature-oriented | ✅ Value-oriented |
|---|---|
| "Schedule Module" | "Semester Schedule Generation" |
| "User Management" | "Clinic & Workforce Configuration" |
| "Notification System" | "Surgeon Confirmation Loop" |

**Step 4 — Order by priority**

Priority = VS pain index of the primary stage anchor:
1. Critical pain stages first
2. High pain stages next
3. Prerequisites (configuration epics) before the features they enable
4. Phase 2 epics after all Phase 1 epics

Assign E-NN IDs in priority order (E-01 = highest priority).

**Step 5 — Write the epic catalogue**

Produce the output document (see Output Structure below).

### Mode 2 — Update

**When:** PRD links need to be filled, phase assignments changed, or FBS
scope adjusted as features are added/removed.

Update specific rows in the catalogue table and the changelog. Never
change an E-NN ID once assigned — the ID is a stable cross-doc reference
used in PRDs, implementation plans, and ADRs.

---

## Output structure

```
docs/product-specs/epic-catalogue.md

<!-- doc-version: 1.0 | created: YYYY-MM-DD -->

H1: {{product}} — Epic Catalogue

Intro: what epics are, methodology anchor, how they bridge FBS and PRDs.

§Confidence legend (same as FBS: ⬜/🔄/✅)

§Epic Summary Table (the primary output)
  Columns: E-NN | Epic name | VS anchor + pain | Primary personas | 
           Capabilities | FBS count | Phase | PRD | Status

§Per-epic H2 sections (one per epic)
  - Value statement: "When this epic ships, [persona] can [outcome]."
  - VS anchor + pain index
  - Personas served (P-NN links)
  - Capabilities consumed (C-N.M links to BC Map)
  - FBS scope: full list of C-N.M.FXX IDs included
  - Phase: Phase 1 / Phase 2 / Phase 3
  - PRD link: _TODO_ until PRD is written
  - Quality attributes in scope: QA-XXNN entries that apply (if QA doc exists)
  - Sizing check: [N] functionalities — [within / below / above] recommended range

§Changelog
```

---

## Epic ID convention

`E-NN` — two-digit zero-padded integer, assigned in priority order.

- IDs are **permanent** — once assigned, never recycled or reassigned.
- If an epic is retired (scope absorbed elsewhere), mark it ❌ Retired in
  the table with a note; do not delete the row or reuse the ID.
- PRDs reference epics as `E-NN · [name]` in their §0 Architecture
  Traceability block.

---

## Discipline checks

Before declaring the catalogue complete, verify:

1. **Every Phase 1 FBS functionality appears in exactly one epic.** No
   functionality should be in two epics, and no functionality should be
   orphaned (unclaimed by any epic). Run a coverage check:
   ```bash
   grep -o "C[0-9]\.[0-9]\.F[0-9][0-9]" docs/product-specs/epic-catalogue.md | sort | uniq | wc -l
   ```
   Compare against the FBS total count.

2. **Every epic has a value statement.** If you cannot complete "when this
   epic ships, [persona] can [outcome]," the epic scope is wrong.

3. **Sizing within range.** Each epic has 5–25 FBS functionalities. Flag
   outliers for the user to decide: merge or split.

4. **Differentiator functionalities (★) anchor their own epic.** A ★
   functionality merged into a secondary epic is a scope risk — the
   product's competitive advantage ships buried in a larger PRD.

5. **E-NN ordering reflects VS pain index.** Critical-pain stage epics
   must have lower numbers (higher priority) than Medium-pain stage epics,
   unless a prerequisite dependency forces a different order (document why).

---

## Cross-references

| Reads | Why |
|---|---|
| FBS (`C-N.M.FXX` + VS stage + phase + ★) | Primary input — every functionality must land in an epic |
| Value Streams (VS-N.M pain index) | Determines epic priority ordering |
| Personas (P-NN) | Identifies which persona each epic primarily serves |
| BC Map (C-N.M) | Provides capability names for the Capabilities column |
| Quality Attributes (QA-XXNN) | Optional: note which QA entries apply per epic scope |

| Feeds | How |
|---|---|
| PRDs | One PRD per epic; PRD §0 references E-NN and the epic's FBS ID list |
| Implementation Plans | Plans reference the PRD which references the epic |
| ADRs | Architectural decisions may reference which epic they unblock |

---

## Checklist

Before declaring the work done:

- [ ] `docs/product-specs/epic-catalogue.md` created
- [ ] Every Phase 1 FBS functionality assigned to exactly one epic (coverage check run)
- [ ] Every epic has a value statement completing "when this epic ships…"
- [ ] Differentiator (★) functionalities each anchor their own epic
- [ ] E-NN IDs assigned in pain-index priority order (Critical before High before Medium)
- [ ] Sizing within 5–25 FBS functionalities per epic (outliers flagged)
- [ ] Phase 2 epics listed after Phase 1 epics
- [ ] PRD links marked `_TODO_` (filled when PRDs are written)
- [ ] Changelog entry added
