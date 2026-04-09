---
name: spec-implementation-planner
description: Create a small-step, testable implementation roadmap from a PRD or feature request. Use when asked to "create an implementation plan", "write a roadmap", or "plan this feature" following the project's atomic increment standard.
version: "1.0.0"
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "specification"
  complexity: "high"
---

# Implementation Planner

This skill guides you through creating a high-quality, structured implementation plan based on the project's standard for atomic increments and test-gated milestones.

## Workflow

1. **Deconstruct Requirement:** Read the PRD or feature request. Identify the core architectural components and the order of operations.
2. **Define Summary:** State the purpose, reference the source PRD, and list the guiding principles (e.g., isolation, small steps, test gates).
3. **Draft Increments:** Break the implementation into small, coherent increments. Each increment MUST be a standalone changeset with a test gate.
4. **Define Delivery Rules:** Include project-wide constraints (e.g., "one increment per commit", "no live API keys").
5. **Group into Milestones:** Create a table grouping increments into logical, standalone delivery chunks.
6. **Save the Plan:** Save the completed plan to `docs/exec-plans/active/[NNNN]_exec_[feature-name].md`. The `[NNNN]` MUST match the ID of the corresponding PRD.

## Output

- **Format:** Markdown (`.md`)
- **Location:** `docs/exec-plans/active/`
- **Filename:** `[NNNN]_exec_[feature-name].md` (e.g., 0001_exec_onboard-agent.md)

## Implementation Plan Template

Use the following Markdown structure exactly:

```markdown
# Implementation Plan: [Feature Name]

## Summary

[High-level context and reference to the PRD]

Principles:

1. One increment equals one coherent change set.
2. Every increment has an explicit test gate.
3. [Project-specific principle]

**Overall Status:** pending
**Current Increment:** --

## Increment Plan

### Increment XX: [Descriptive Title]

**Status:** pending

Scope:

1. [Actionable item]
2. [Actionable item]

Primary files:

1. [File path]
2. [File path]

Test gate:

1. [Command to verify success]

Exit criteria:

1. [Outcome 1]
2. [Outcome 2]

[Repeat for each increment...]

## Delivery Rules

1. One increment per commit.
2. Each increment must be independently runnable and reversible.
3. [Other standard rules...]

## Milestone Chunks (Standalone Delivery Groups)

| Milestone      | Increments    | Status  | Coherent Outcome | Standalone Test Gate   | Exit Criteria      | Commit Guidance |
| :------------- | :------------ | :------ | :--------------- | :--------------------- | :----------------- | :-------------- |
| [M-ID]: [Name] | [Start]-[End] | pending | [Description]    | [Verification command] | [Success criteria] | [Commit style]  |
```

## Guiding Principles for Planning

- **Atomic Changes:** An increment should be small enough to review easily but large enough to provide value or a foundation.
- **Test-Driven Gates:** Every increment must have a `Test gate`. If no logic is added, use a `smoke test` or `import test`.
- **Deterministic Outcomes:** Exit criteria must be objective and verifiable.
- **Sequential Flow:** Order increments to minimize rework and respect dependencies.
- **Ralph Loop Ready:** Status fields on every increment and milestone enable autonomous execution via the `ralph-loop-runner` skill. Use `**Status:** pending | in-progress | done` to track progress.
