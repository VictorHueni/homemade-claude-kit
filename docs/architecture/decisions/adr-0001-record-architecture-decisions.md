---
title: Record Architecture Decisions
status: active
owner: Victor Hueni
last_reviewed: 2026-06-03
review_interval: 180d
---

# Record Architecture Decisions

Date: 2026-06-03

## Context and Problem Statement

We need to track significant architectural decisions made during the evolution
of this project so that future contributors understand the reasoning behind
the current design, not just the design itself.

## Decision Drivers

- Decisions made without recorded context are hard to revisit or challenge
- New contributors lack the history needed to make consistent choices

## Considered Options

- Unstructured notes in README or wiki
- Architecture Decision Records (MADR 4.x format)

## Decision Outcome

Chosen option: "Architecture Decision Records (MADR 4.x)", because the
structured format makes drivers, options, and trade-offs explicit and
queryable.

### Positive Consequences

- Decisions are self-contained and searchable
- Supersession chains preserve the full history of a choice

### Negative Consequences

- Requires discipline to write ADRs before implementing, not after
