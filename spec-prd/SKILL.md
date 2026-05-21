---
name: spec-prd
description: "Generate a Product Requirements Document (PRD) for a new feature. Use when planning a feature, starting a new project, or when asked to create a PRD. Triggers on: create a prd, write prd for, plan this feature, requirements for, spec out."
version: "1.1.0"
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "specification"
  complexity: "high"
---

# PRD Generator

You are an expert at writing product requirements documents (PRDs) and feature
specifications. You help product managers define what to build, why, and how to
measure success.

PRDs produced by this skill are **architecture-stack-aware**: when upstream
artefacts exist (BC Map, FBS, personas, value streams), the PRD cross-references
them by stable ID so traceability is mechanical, not narrative.

---

## Step 0: Detect upstream artefacts

Before asking any questions, silently check which upstream artefacts exist:

```bash
ls docs/business/personas/personas.md 2>/dev/null
ls docs/business/capability-map/capability-map.md 2>/dev/null
ls docs/product-specs/functional-breakdown-structure/FBS.md 2>/dev/null
ls docs/business/value-streams/value-streams.md 2>/dev/null
```

**If artefacts exist:** extract the relevant IDs and use them to enrich the PRD
(persona IDs `P-NN`, capability IDs `C-N.M`, FBS functionality IDs `C-N.M.FXX`,
value-stream stage IDs `VS-N.M`). Do not ask the user to supply IDs you can read
directly.

**If artefacts are absent:** proceed with the generic PRD format (current
behaviour). Use specific role descriptions in user stories rather than generic
"user" or "admin".

---

## Step 1: Clarifying Questions

Ask only critical questions where the initial prompt is ambiguous. Focus on:

- **Problem/Goal:** What problem does this solve?
- **Core Functionality:** What are the key actions?
- **Scope/Boundaries:** What should it NOT do?
- **Success Criteria:** How do we know it's done?

If the FBS exists, also ask:

- **FBS scope:** Which FBS capabilities / functionalities does this PRD target?
  (Show the user the relevant ⬜ rows from the FBS and ask them to confirm scope.)

### Format Questions Like This:

```text
1. What is the primary goal of this feature?
   A. Improve user onboarding experience
   B. Increase user retention
   C. Reduce support burden
   D. Other: [please specify]

2. Who is the primary persona served?
   A. P-01 Francine — OR coordinator
   B. P-03 Dr. Favre — surgeon (physician portal)
   C. Both equally
   D. Other: [please specify]

3. What is the scope?
   A. Minimal viable version
   B. Full-featured implementation
   C. Just the backend/API
   D. Just the UI
```

This lets users respond with "1A, 2C, 3B" for quick iteration.

---

## Step 2: PRD Structure

Generate the PRD with these sections.

Include an overall status at the top: `**Status:** draft | approved | in-progress | complete`

---

### §0 · Architecture Traceability

> Fill this block from the upstream artefacts detected in Step 0.
> If no upstream artefacts exist, omit this section entirely.

```markdown
**PRD-ID:** PRD-NNNN
**Status:** draft

| Field | Value |
|---|---|
| **Vision** | [Product Vision](../../VISION.md) *(if `docs/VISION.md` exists)* |
| **Personas served** | [P-01 · Francine](link) · [P-03 · Dr. Favre](link) |
| **Capabilities covered** | [C3.1 Schedule Generation](link) · [C3.2 Conflict Detection](link) |
| **Primary value stream** | [VS-1.2 · Generate Schedule Draft](link) — Pain: Critical |
| **Objective** | [OBJ-NN · Objective title](link to objectives.md) *(if objectives doc exists)* |

**FBS functionalities delivered by this PRD:**

| FBS ID | Functionality | Status before | Status after |
|---|---|---|---|
| C3.1.F02 | Generate semester schedule from recurrence rules | ⬜ | 🔄 |
| C3.2.F01 | Detect double attribution | ⬜ | 🔄 |
```

**Rules for this block:**
- Link every ID to its source document using a relative path.
- `Status after` is always `🔄` when the PRD is approved; `✅` when shipped.
- If a functionality is already `✅`, this PRD should not re-scope it — raise as
  a conflict in §8 Open Questions instead.
- After the PRD is approved, manually update the referenced FBS rows from `⬜`
  to `🔄` (see Step 4 below).

---

### 1. Problem Statement

- Describe the user problem in 2–3 sentences
- Who experiences this problem (reference persona by role + P-NN) and how often
- What is the cost of not solving it (user pain, business impact, competitive risk)
- Ground this in evidence: user research, support data, metrics, or customer feedback

---

### 2. Goals

- 3–5 specific, measurable outcomes this feature should achieve
- Each goal should answer: "How will we know this succeeded?"
- Distinguish between user goals and business goals
- Goals should be outcomes, not outputs

If a value stream stage was identified in §0, anchor one goal to its pain index:
> "Reduce VS-1.2 (Generate Schedule Draft) from 3 working days to under 5 minutes."

---

### 3. Non-Goals

- 3–5 things this feature explicitly will NOT do
- For each non-goal, briefly explain why it is out of scope
- Reference FBS IDs for functionalities explicitly deferred:
  > "C3.1.F06 (rolling schedule mode) — deferred to a future PRD; not needed for
  > the semester-based pilot."

---

### 4. User Stories

Each story MUST reference a named persona role and ID:

```
As a [persona role] (P-NN), I want [action] so that [outcome].
```

**If multiple personas share the same feature, write one story per persona.**
They have different contexts, devices, and success criteria even for the same
feature — merging them into one story produces acceptance criteria that satisfy
neither.

**User story format:**

```markdown
### US-001: [Title]

**Persona:** P-NN · [Role name]
**Status:** pending
**FBS refs:** C3.1.F02 · C3.2.F01

**Description:**
As a [persona role] (P-NN), I want [action] so that [outcome].

**Acceptance Criteria:**
- [ ] Specific verifiable criterion
- [ ] Another criterion
- [ ] Typecheck/lint passes
- [ ] **[UI stories only]** Verify in browser using dev-browser skill
```

#### 4.1 User Story Guidelines

Good user stories are:

- **Independent:** can be developed and delivered on their own
- **Negotiable:** details can be discussed, the story is not a contract
- **Valuable:** delivers value to the persona (not just the team)
- **Estimable:** the team can roughly estimate the effort
- **Small:** can be completed in one sprint/iteration
- **Testable:** there is a clear way to verify it works
- **Persona-grounded:** written for a specific P-NN, not a generic "user"

**Common Mistakes:**

- Generic persona: "As a user…" — always name the role + P-NN
- Too vague: "As a P-01, I want the product to be faster" — what specifically?
- Solution-prescriptive: "I want a dropdown menu" — describe the need, not the widget
- No benefit: "I want to click a button" — why? What does it accomplish?
- Too large: "I want to manage my surgical workforce" — break into specific capabilities
- Multiple personas merged: split into separate stories, each grounded in one P-NN

**Example (with persona + FBS refs):**

```markdown
### US-001: Generate semester OR schedule

**Persona:** P-01 · OR coordinator
**Status:** pending
**FBS refs:** C3.1.F02 · C3.1.F03 · C3.1.F04 · C3.1.F05

**Description:**
As an OR coordinator (P-01), I want to generate a 6-month OR schedule
from surgeon recurrence rules so that I no longer spend 3 working days
cross-referencing PEP and Excel to produce it manually.

**Acceptance Criteria:**
- [ ] A semester schedule is generated for all active surgeons in under 5 minutes
- [ ] Vacation exclusions are applied automatically
- [ ] Hard surgeon constraints block invalid attributions
- [ ] A conflict report is produced listing every violation with resolution context
- [ ] Generation can be re-run after constraint edits without side effects
```

#### 4.2 Tips for Acceptance Criteria

- Cover the happy path, error cases, and edge cases
- Be specific about expected behaviour, not implementation
- Include negative test cases ("must NOT show other surgeons' names")
- Reference the persona's context: device, usage frequency, time pressure
- Each criterion must be independently testable

---

### 5. Design Considerations (Optional)

- UI/UX requirements
- Link to mockups if available
- Relevant existing components to reuse
- Note the primary device for the target persona (P-03 → mobile-first; P-01 → desktop)

---

### 6. Technical Considerations (Optional)

- Known constraints or dependencies
- Integration points with existing systems
- Performance requirements grounded in the persona's context
  (e.g., "P-01 uses this during live phone calls — response time ≤ 2s")
- Reference relevant ADRs if architecture decisions apply:
  > "See ADR-0001 for the schedule generation algorithm architecture decision."

---

### 7. Success Metrics

How will success be measured?

#### 7.1 Leading Indicators

Metrics that change quickly after launch (days to weeks):

- **Adoption rate:** % of eligible personas (P-NN) who use the feature
- **Activation rate:** % of users who complete the core action
- **Task completion rate:** % of users who successfully accomplish their goal
- **Time to complete:** how long the core workflow takes
- **Error rate:** how often users encounter errors or dead ends

#### 7.2 Lagging Indicators

Metrics that take time to develop (weeks to months):

- **Retention impact:** does this feature improve user retention?
- **Revenue impact:** does this drive upgrades, expansion, or new revenue?
- **NPS / satisfaction change:** does this improve how users feel about the product?
- **Support ticket reduction:** does this reduce support load?

#### 7.3 Setting Targets

- Targets should be specific: "50% adoption within 30 days" not "high adoption"
- Base targets on comparable features, pain index from value streams, or PRD §9
- Set a "success" threshold and a "stretch" target
- Specify the measurement method and time window

---

### 8. Open Questions

Remaining questions or areas needing clarification. Include:
- Unresolved FBS scope (functionalities considered but not committed)
- Persona edge cases not yet designed for
- Dependencies on other PRDs or ADR decisions

---

## Step 3: Save the PRD

Find the next available ID:

```bash
python skills/spec-prd/scripts/get-next-id.py
# or: check docs/product-specs/ for the highest 4-digit prefix
```

Save to: `docs/product-specs/[NNNN]_prd_[feature-name].md`

**Important:** Do NOT start implementing. Just create the PRD.

---

## Step 4: Promote FBS functionalities

After saving the PRD, instruct the user to update the FBS — or do it directly
if the FBS file is accessible:

> "The following FBS functionalities are now committed by this PRD.
> Update their status from ⬜ to 🔄 in
> `docs/product-specs/functional-breakdown-structure/FBS.md`."

List each committed functionality with its ID and name. If you have write
access, make the edits directly and commit the FBS alongside the PRD.

---

## Output

- **Format:** Markdown (`.md`)
- **Location:** `docs/product-specs/`
- **Filename:** `[NNNN]_prd_[feature-name].md` (e.g., `0001_prd_semester-schedule-generation.md`)

---

## Checklist

Before saving the PRD:

- [ ] Upstream artefacts checked (BC Map, FBS, personas, value streams)
- [ ] §0 Architecture Traceability block filled (or omitted if no artefacts exist)
- [ ] OBJ-NN referenced in §0 if `docs/business/objectives/objectives.md` exists
- [ ] Clarifying questions asked with lettered options
- [ ] User answers incorporated
- [ ] Every user story references a specific persona role + P-NN ID
- [ ] User stories are small, specific, and grounded in one persona
- [ ] FBS refs listed per user story where applicable
- [ ] Non-goals reference FBS IDs for explicitly deferred functionalities
- [ ] Success metrics anchored to persona context and value-stream pain index
- [ ] Saved to `docs/product-specs/[NNNN]_prd_[feature-name].md`
- [ ] FBS promotion instructions provided (⬜ → 🔄 for committed functionalities)
