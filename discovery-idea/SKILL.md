---
name: discovery-idea
description: "Capture, refine, and graduate pre-formal ideas — product, business, architecture, process, dx, or ops. Use when brainstorming a vague concept, pressure-testing an early hunch, drafting a one-pager before a PRD/ADR/OBJ, or routing an idea to the right downstream skill. Triggers on: /idea, /ideate, new idea, refine idea, pressure-test idea, one-pager, pre-PRD idea, idea status, graduate idea."
version: "2.0.0"
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "discovery"
  complexity: "medium"
---

# Discovery — Idea Capture, Refinement, and Graduation

You manage pre-formal ideas — the upstream layer that feeds **every** downstream artefact in the metamodel: personas, business objectives, BMC blocks, ADRs, PRDs, FBS functionalities, or process docs.

An idea here is **pre-classification**. At capture, it does not yet know whether it will become a `PRD-NNNN`, an `OBJ-NN`, an `ADR-NNNN`, or be abandoned. The skill's job is to (1) capture it cleanly, (2) pressure-test it, and (3) **graduate** it to the right downstream skill when it is ready — never to do the downstream work itself.

This skill does **not** replicate persona design, value-proposition shaping, hypothesis-anchored interview scripting, market sizing, ADR analysis, PRD acceptance criteria, or implementation breakdown. Those are owned by `business-persona`, `business-model-canvas`, `discovery-research`, `business-quantitative-model`, `arch-adr`, `spec-prd`, and `spec-implementation-plan` respectively. When the idea matures past its capture phase, route to them — do not absorb their work.

---

## Position in the metamodel

`discovery-idea` is a **pre-Step-0** cross-cutting node. It sits alongside `discovery-research` (1:1 interviews) and `discovery-workshop` (group sessions) under the shared `docs/discovery/` parent — the three skills together form the **discovery family**, the reality-check layer that feeds every downstream artefact.

```
docs/discovery/
├── ideation/      ← discovery-idea  (this skill)
│   ├── INDEX.md
│   └── {slug}.md
├── interviews/    ← discovery-research
└── workshops/     ← discovery-workshop
```

Every idea file declares a `graduates_to:` field naming the downstream skill that will own the matured artefact. Graduation is explicit and the skill drives it — an idea is never silently abandoned in the folder.

---

## File layout and ID convention

**Output path:** `docs/discovery/ideation/IDEA-NNNN-{slug}.md` (flat — no per-domain subfolders; `domain:` is a frontmatter tag; the `IDEA-NNNN-` filename prefix carries the ID so the slug stays free for human-readable kebab-case).

**ID format:** `IDEA-NNNN` (4-digit zero-padded, monotonic per project). Assigned at scaffold time. Embedded in both the filename and the frontmatter `idea_id:` field. Used in cross-doc references when the idea is cited from a downstream artefact ("This PRD originated from IDEA-0042").

**Filename rule:** `IDEA-{NNNN}-{slug}.md` — e.g. `IDEA-0042-sms-reorder-for-regulars.md`. The ID prefix guarantees uniqueness without per-domain subfolders; the slug is kebab-case, 3–5 words, human-readable. Same convention as `prd-NNNN-{feature}.md` and `adr-NNNN-{slug}.md` in the kit.

**Index:** one `docs/discovery/ideation/INDEX.md` listing every idea with status, domain, graduates-to target, and one-line summary. Filterable by the `domain:` column.

---

## Frontmatter schema

Every file opens with the canonical artefact frontmatter from `rules/artefact-frontmatter.md`, extended with three idea-specific fields:

```yaml
---
title: <short descriptive title>
status: draft        # draft | active | superseded | deprecated
owner: <git config user.name>
last_reviewed: YYYY-MM-DD
review_interval: 90d

# discovery-idea specific
idea_id: IDEA-NNNN
domain: product | business | architecture | process | dx | ops
lifecycle: captured | refining | ready | graduated | abandoned
graduates_to: spec-prd | business-persona | business-objective | business-model-canvas | arch-research | arch-adr | business-process | spec-functional-breakdown-structure | _TBD_
target_id: _TBD_     # filled when lifecycle = graduated (e.g. PRD-0007, OBJ-03, ADR-0012)
---
```

**Field rules:**

- `status` follows the standard artefact lifecycle (`draft` until refine completes; `active` once published; `superseded` if replaced; `deprecated` if abandoned long-term).
- `lifecycle` is **idea-specific** and orthogonal to `status` — it tracks the idea's maturity (captured → refining → ready → graduated | abandoned), not the document's authority. A `lifecycle: refining` idea still has `status: draft`.
- `graduates_to` MUST be set by end of Refine mode. `_TBD_` is allowed only during initial capture.
- `target_id` is `_TBD_` until graduation actually happens; then it holds the minted downstream ID (e.g., `PRD-0007`).

**Review interval default:** `90d` (per `rules/artefact-frontmatter.md`).

---

## Document structure

Every ideation file uses this section order. Sections marked _conditional_ appear only at certain lifecycle stages.

```markdown
---
<frontmatter>
---

# IDEA-NNNN — <title>

## Problem statement

"How Might We …" framing of the underlying problem. 1–3 sentences. Names a specific user
or stakeholder and an observable pain. Avoid solution language.

## Context

Why this idea surfaced now. What triggered it (interview signal, workshop output, customer
complaint, architectural smell, competitive shift). Soft-link to upstream sources by ID when
they exist: `P-NN`, `BC-NN`, `VS-N.M`, `C-N.M`, `Research-NNNN`, audit finding, etc.

## Variations          _(Refine mode — divergent phase)_

5–8 named alternatives generated by ideation lenses. Each has a one-line label and 2–4
sentences of reasoning. Lenses include (pick what fits — do not run all):

- SCAMPER (Substitute · Combine · Adapt · Modify · Put to other uses · Eliminate · Reverse)
- Inversion (what if the assumption flipped?)
- Constraint removal (what if X were free / infinite / instant?)
- Audience shift (what if it were for someone else?)
- Simplification (what if it could only do one thing?)
- Analogous inspiration (structural — not "Uber for X")
- Pre-mortem (12 months out it failed — why?)

## Direction          _(Refine mode — convergent phase)_

The 1–3 clusters that emerged. For each cluster, three stress-test paragraphs:

- **User value** — painkiller vs. vitamin, name 3 specific users, what they do today instead,
  frequency, intensity. Cite `P-NN` if a persona already exists.
- **Feasibility** — technical feasibility (known-hard vs. novel), resource feasibility,
  time-to-value, critical path. Soft-link to `ADR-NNNN` / `Research-NNNN` if relevant.
- **Differentiation** — what is genuinely new (capability / 10x / audience / context / UX /
  price). Durability against fast-followers.

## Assumption audit          _(Refine mode)_

Three-tier list. The "Must be true" tier sets the validation budget for the next step.

- **Must be true (dealbreakers)** — assumptions that, if wrong, kill the idea.
- **Should be true (important)** — assumptions that change the approach but not the bet.
- **Might be true (nice to have)** — secondary optimisations; validate after the core.

Each row names the validation method (interview · prototype · data pull · expert review).
Items that need a structured research wave become Open Items routed to `discovery-research`.

## Recommended direction

The single direction picked for graduation. One paragraph. References the cluster ID from
§Direction and names the strongest stress-test outcome.

## MVP / first move          _(Refine mode — only when graduates_to ∈ { spec-prd, arch-research })_

What gets built or researched first. One job, done well. Time-boxed, not feature-listed. The
purpose is to test the riskiest "Must be true" assumption. **Not** a substitute for the PRD
or research plan — it is the pre-spec sketch that the downstream skill turns into the formal
artefact.

## Not doing (and why)

Explicit, reasoned, and short. Each item is something a reader might *expect* but that is
deliberately excluded. The "Not Doing" list is mandatory — the idea is not refined if this
section is empty.

## Graduation          _(Ready / Graduated lifecycle stages)_

- **Routing skill:** `<value of graduates_to>`
- **Pre-flight checks:** what must be true before invoking the downstream skill (e.g., "PRD
  requires an existing E-NN epic — confirm in delivery roadmap" or "ADR requires the
  architectural choice to be currently open").
- **Graduation date:** YYYY-MM-DD (filled when lifecycle moves to `graduated`).
- **Resulting artefact:** `<target_id>` + relative path to the downstream file.

## References

- **Upstream sources:** interviews, workshops, audits, customer messages, competitive intel
- **Related ideas:** other `IDEA-NNNN` files
- **External:** URLs (with `Last verified: YYYY-MM-DD` per `rules/writing-citations.md`)

## Open Items

Canonical document-level section per `rules/open-items-governance.md` §4. Schema:

| OI-ID  | Type            | Summary | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref |
| :----- | :-------------- | :------ | :------------ | :------------- | :-------------- | :------- | :----- | :---- | :---------------- | :---------- |

Use the `Type` taxonomy: `doc-gap` (missing info needed before graduation) · `decision-gap`
(unresolved choice between variations) · `execution-item` (validation task — invoke
`discovery-research` or run a probe) · `tech-debt` (rare — refactor implied by the idea).

## Changelog

| Date       | Lifecycle change            | Note                                  |
| :--------- | :-------------------------- | :------------------------------------ |
| YYYY-MM-DD | captured                    | initial scaffold                      |
| YYYY-MM-DD | refining → ready            | refine pass completed                 |
| YYYY-MM-DD | ready → graduated           | PRD-0007 minted; target_id filled     |
```

---

## Modes

The skill operates in five modes. Each maps to a lifecycle transition.

### Mode 1 — Capture (lifecycle: → captured)

Triggers: `/idea`, `new idea`, `add idea`, `capture idea <text>`.

1. Read the user's one-line idea.
2. Assign next available `IDEA-NNNN` ID by scanning `docs/discovery/ideation/` for the highest existing `IDEA-NNNN-*.md` filename prefix and incrementing.
3. If `domain` is not stated, ask once (lettered options: a=product · b=business · c=architecture · d=process · e=dx · f=ops).
4. Scaffold the file at `docs/discovery/ideation/IDEA-{NNNN}-{slug}.md` with frontmatter + `## Problem statement` + `## Context` + `## Not doing` + `## Open Items` (empty) + `## Changelog` (one row).
5. Set `lifecycle: captured`, `graduates_to: _TBD_`, `target_id: _TBD_`, `status: draft`.
6. Update `docs/discovery/ideation/INDEX.md` (create if missing).
7. Report the ID and the path. Offer to enter Refine mode immediately.

**Verification:** file exists with valid frontmatter, monotonic IDEA-NNNN, INDEX.md updated, `## Open Items` section present even if empty.

### Mode 2 — Refine (lifecycle: captured → refining → ready)

Triggers: `refine IDEA-NNNN`, `refine <slug>`, `pressure-test`, `ideate`.

This is the **socratic core**. Run it in three phases, in order. Do not skip.

**Phase A — Diverge.**
1. Restate the problem as a sharper "How Might We …" question. Show two-to-three reframings.
2. Ask the user 2–3 sharpening questions targeting (a) *who* specifically, (b) what *success* looks like, (c) what *constraint* matters most.
3. Generate 5–8 labelled variations using the lenses listed in §Variations of the doc template. Label each by lens (e.g., `Inversion — `, `Simplification — `, `Audience shift — `). Each variation is 2–4 sentences explaining the *bet* it makes, not just the *feature* it adds.
4. Write to the `## Variations` section.

**Phase B — Converge.**
1. Cluster the variations into 2–3 distinct directions. Name each cluster.
2. For each cluster, write the three stress-test paragraphs (User value · Feasibility · Differentiation) per the §Direction template.
3. Have an **opinion**. Push back on weak directions. Name what is genuinely new vs. what is "X but better". Quote from `refinement-criteria.md` when needed (load the reference file before this phase).
4. Surface hidden assumptions and split them into the three tiers (Must / Should / Might be true) in `## Assumption audit`. Add validation method per row.

**Phase C — Pick + route.**
1. State the recommended direction in one paragraph in `## Recommended direction`.
2. Write the `## MVP / first move` if and only if `graduates_to ∈ { spec-prd, arch-research }`. Otherwise omit.
3. Fill `## Not doing` with at least 3 reasoned items.
4. Set `graduates_to:` in frontmatter to the downstream skill name.
5. Set `lifecycle: ready`.
6. Append a Changelog row.
7. Sync `docs/discovery/ideation/INDEX.md`.

**Verification:** all of §Variations, §Direction, §Assumption audit, §Recommended direction, §Not doing are non-empty; `graduates_to` is no longer `_TBD_`; ≥3 items in `## Not doing`; ≥1 "Must be true" assumption; INDEX.md row matches.

### Mode 3 — Graduate (lifecycle: ready → graduated)

Triggers: `graduate IDEA-NNNN`, `promote idea`, `ship idea to PRD/ADR/OBJ`.

1. Read the idea file. Confirm `lifecycle: ready` and `graduates_to:` is set.
2. Run pre-flight checks per the routing target:
   - `spec-prd` → verify an `E-NN` epic exists in the delivery roadmap that this PRD would belong to. If absent, route to `spec-delivery-roadmap` first.
   - `business-persona` → verify `docs/business/01a-personas.md` exists.
   - `business-objective` → verify `docs/business/04b-objectives.md` exists; if not, scaffold via `business-objective` Mode 1.
   - `business-model-canvas` → verify the canvas file exists.
   - `arch-research` → no prerequisite; routes directly.
   - `arch-adr` → confirm the architectural choice is still open (not already decided).
   - `business-process` → verify the parent `VS-N.M` value-stream stage exists.
   - `spec-functional-breakdown-structure` → verify the parent capability `C-N.M` exists.
3. Invoke the downstream skill in its scaffold mode. **Do not write the downstream artefact yourself** — only invoke and pass the idea's `Recommended direction` + `Assumption audit` + `Not doing` as context.
4. Once the downstream skill mints its ID, write that ID into `target_id:` and add the relative path to `## Graduation §Resulting artefact`.
5. Set `lifecycle: graduated`. Append Changelog row. Update INDEX.md.

**Cross-link:** the new downstream artefact MUST reference back to the idea in its §0 traceability block (e.g., "Originated from `IDEA-0042`"). The downstream skill is responsible for that back-link.

**Verification:** `lifecycle: graduated`; `target_id` filled; downstream file exists at the expected path; downstream file mentions `IDEA-NNNN`; INDEX.md reflects graduated status.

### Mode 4 — Abandon (lifecycle: any → abandoned)

Triggers: `abandon IDEA-NNNN`, `drop idea`, `kill idea`.

1. Set `lifecycle: abandoned` and `status: deprecated`.
2. Add a 1–3 sentence rationale at the end of `## Recommended direction` (replacing the prior content if any).
3. Append Changelog row including the rationale.
4. Update INDEX.md (move row to bottom; do not delete the file).

**Verification:** `lifecycle: abandoned`; rationale present; INDEX.md reflects abandoned status.

### Mode 5 — Maintain (lifecycle: graduated → review)

Triggers: monthly cadence; user runs the maintenance pass; `util-metamodel-audit` Check 12 flags overdue review.

1. For each idea where `lifecycle: graduated`, verify the `target_id` artefact still exists at the recorded path.
2. If the downstream artefact has been superseded, set this idea's `status: superseded` + `superseded_by: <path>`.
3. For each idea where `lifecycle: ready` for >`review_interval` days, prompt the user to graduate or re-refine.
4. Sync INDEX.md.

---

## Relationships of the IDEA artefact

An `IDEA-NNNN` is a hub with five kinds of edges. Understanding which edge applies prevents the skill from over-reaching into downstream territory.

### 1. Inbound — where ideas come FROM

Source signals that *generate* ideas. Not modeled as foreign keys (the source is "human + evidence", not another artefact's ID) but the originating signal is recorded in `## Context` and `## References`.

- `discovery-research` interview synthesis surfaces a hunch → captured as `IDEA-NNNN`
- `discovery-workshop` output produces several candidate directions → each captured
- `util-metamodel-audit` flags a gap requiring ideation (e.g. an `Assumed` claim with no evidence) → captured
- An open item of type `decision-gap` in any artefact may spawn a new idea
- External signals: customer messages, competitive moves, individual hunches

### 2. Outbound — graduation (the only edge type modeled in the ER)

Eight possible targets, set per idea via the `graduates_to:` frontmatter field. Each idea graduates to **exactly one** target (or is abandoned). The target mints its own ID; the idea stores it in `target_id` after graduation.

| `graduates_to:` | Mints | Typical trigger |
|---|---|---|
| `business-persona` | `P-NN` | Research reveals a new persona type |
| `business-objective` | `OBJ-NN` + `KR-NN.M` | Strategic priority candidate |
| `business-model-canvas` | New BMC block entry (`VP-NN`, `CS-NN`, …) | New value proposition or segment |
| `business-process` | New `proc-NN-{slug}.md` | Operational improvement to a VS stage |
| `arch-research` | `Research-NNNN` | Architectural question needs evidence first |
| `arch-adr` | `ADR-NNNN` | A decided architectural choice |
| `spec-functional-breakdown-structure` | New `C-N.M.FXX` row | New functionality on an existing capability |
| `spec-prd` | `PRD-NNNN` | Feature-scoped build commitment |

### 3. Body-text citations INTO the idea (no FK column — markdown soft-links)

Cited inside `## Context`, `## Direction`, and `## References` to ground claims. These IDs appear as plain markdown links, not as structural foreign keys:

- `P-NN` — User Value claims naming a real persona
- `VS-N.M` — pain-index context
- `C-N.M` — parent capability for FBS-graduation ideas
- `BC-NN` — for architecture / domain ideas
- `Research-NNNN`, `ADR-NNNN` — existing evidence base
- `OI-NNNN` — when the idea originates from an open item
- Other `IDEA-NNNN` — sibling explorations or supersession chains

### 4. Body-text back-references FROM the target (after graduation)

The graduated artefact cites `IDEA-NNNN` in its body — **not** as a structural FK column on the target entity (per the ER hard rule). The back-reference appears in:

- `spec-prd` → §0 Architecture Traceability
- `arch-adr` → §Context
- `business-objective` → "why it matters" sentence
- `business-persona` → persona description origin note

The graduating skill is responsible for writing this back-link during its own scaffold/fill mode.

### 5. Open-Items routing (cross-cutting dispatch layer)

The idea's local `## Open Items` section acts as a dispatcher:

| `Type` | Routes to | Resolution path text |
|---|---|---|
| `execution-item` (validation) | `discovery-research` | "Run `discovery-research` Mode 2 with hypothesis: `<Must-be-true statement>`" |
| `execution-item` (alignment) | `discovery-workshop` | "Run `discovery-workshop` Mode 1 with focus question: `<Decision question>`" |
| `decision-gap` | stays local | "Refine pass — pick between variations A/B/C" |
| `doc-gap` | blocks graduation | "Fill `<missing section>` before graduating to `<target skill>`" |

After `util-open-items` sync, the row gets a canonical `OI-NNNN` in `docs/project-control/open-items/`.

### 6. Lifecycle: supersession

Standard artefact frontmatter applies (per `rules/artefact-frontmatter.md`):

- `status: superseded` + `superseded_by: <path>` when a refined variant replaces an earlier idea
- `lifecycle: abandoned` is **orthogonal** to `status` — used when the idea is dropped without a replacement, not when it's replaced by another

### What ideas do NOT graduate to

Worth knowing because it tells you when the skill is being misused. These artefacts are derived or structural — they emerge from upstream architecture, not from individual ideas:

| Artefact | Why not a graduation target |
|---|---|
| `business-vision` | Project-level singleton; emerges from founding intent |
| `business-capability-map` | Derived from vision + BMC; the L0 axis is a structural choice |
| `business-value-stream` | Falls out of personas × value propositions |
| `business-quantitative-model` | Commissioned modelling; one model serves many decisions |
| `domain-bounded-context` · `domain-glossary` · `domain-model` | Emerge from Event Storming + capability cohesion |
| `spec-delivery-roadmap` · `spec-quality-attributes` · `spec-implementation-plan` | Downstream of FBS / PRDs; mechanical groupings, not creative bets |

**Diagnostic:** if an "idea" wants to graduate to one of these, the underlying artefact is probably missing or stale. Don't graduate — invoke the missing skill directly. Example: an idea like "we need to track our value flows" doesn't graduate to anything; it means `business-value-stream` Mode 1 (scaffold) should run.

---

## How this skill interacts with siblings

| Skill | Relationship |
|---|---|
| `discovery-research` | Receives `execution-item` Open Items from idea refine. When an assumption needs interview validation, the OI row's `Resolution path` says "Run `discovery-research` Mode 2 with hypothesis: `<Must-be-true statement>`". Conversely, when `discovery-research` synthesis surfaces a new hunch, it can create a Mode 1 idea here. |
| `discovery-workshop` | Workshop synthesis often produces multiple candidate ideas; each gets a Mode 1 capture call. Conversely, ideation can request a workshop to align stakeholders before graduating — emit an Open Item routing to `discovery-workshop`. |
| `spec-prd` | Most common graduation target for `product` domain ideas. PRD §0 must reference the originating `IDEA-NNNN`. |
| `arch-adr`, `arch-research` | Graduation target for `architecture` domain ideas. ADR's `## Context` references the originating `IDEA-NNNN`. |
| `business-objective`, `business-model-canvas`, `business-persona` | Graduation targets for `business` domain ideas. |
| `business-process` | Graduation target for `process` domain ideas. |
| `spec-functional-breakdown-structure` | Graduation target when an idea is "add this functionality `C-N.M.FXX` to an existing capability". |
| `util-open-items` | Picks up the local `## Open Items` rows on sync and writes them to `docs/project-control/open-items/open-items.md` with canonical `OI-NNNN` IDs. |
| `util-metamodel-audit` | Reports on stale `ready` ideas, missing `graduates_to`, dead `target_id` links, and `## Open Items` schema drift. |

---

## INDEX.md schema

```markdown
---
title: Discovery — Ideation Index
status: active
owner: <git config user.name>
last_reviewed: YYYY-MM-DD
review_interval: 90d
---

# Discovery — Ideation Index

| ID         | Status     | Domain       | Title                              | Graduates to        | Target ID  | Summary                                       |
| :--------- | :--------- | :----------- | :--------------------------------- | :------------------ | :--------- | :-------------------------------------------- |
| IDEA-0001  | ready      | product      | [SMS-first reorder for regulars]() | spec-prd            | _TBD_      | Direct reorder via SMS, zero restaurant ops   |
| IDEA-0002  | graduated  | architecture | [Token-based partner auth]()       | arch-adr            | ADR-0004   | Move from API keys to scoped JWTs             |
| IDEA-0003  | abandoned  | business     | [Subscription pricing flip]()      | _TBD_               | _TBD_      | Customers won't pay subscription — dropped    |

Sort: `refining` → `ready` → `captured` → `graduated` → `abandoned` (active states first).
```

---

## Rules

- **One idea per file.** If a captured idea covers two independent problems, split during Refine mode.
- **`graduates_to` must be set before lifecycle leaves `captured`.** No idea graduates with `_TBD_` routing.
- **Do not do downstream work.** The skill never writes a PRD body, an ADR analysis, a persona profile, or a domain-event catalogue. It writes the *sketch* and *invokes* the right skill.
- **`## Not doing` is mandatory.** An idea with no exclusions is not refined.
- **Sources cited.** Every variation cluster in §Direction with a "User value" claim that names an existing persona must use the `P-NN` ID. Fabricated personas are forbidden — route to `business-persona` first.
- **Assumption tier discipline.** "Must be true" assumptions become Open Items with `Type: execution-item` and `Resolution path: discovery-research` (or another evidence skill).
- **Cross-doc linking.** Use `[IDEA-NNNN — title](../../discovery/ideation/IDEA-NNNN-{slug}.md)` from anywhere else in `docs/`.
- **Today's date format:** `YYYY-MM-DD`.

---

## Checklist before saving

- [ ] Frontmatter complete per `rules/artefact-frontmatter.md` + idea-specific fields (`idea_id`, `domain`, `lifecycle`, `graduates_to`, `target_id`)
- [ ] `IDEA-NNNN` is the next available ID, 4-digit zero-padded; filename matches `IDEA-NNNN-{slug}.md`
- [ ] `## Problem statement` is HMW-framed and names a specific user/stakeholder
- [ ] If `lifecycle ≥ ready`: §Variations, §Direction, §Assumption audit, §Recommended direction, §Not doing are all non-empty
- [ ] If `lifecycle = ready`: `graduates_to` is set (not `_TBD_`) and matches the recommended direction
- [ ] If `lifecycle = graduated`: `target_id` is filled, downstream artefact exists, downstream artefact back-references `IDEA-NNNN`
- [ ] `## Open Items` section uses canonical schema from `rules/open-items-governance.md` §4
- [ ] `## Changelog` has at least one row reflecting the latest lifecycle change
- [ ] `INDEX.md` updated and sorted
- [ ] Slug is kebab-case, 3–5 words
