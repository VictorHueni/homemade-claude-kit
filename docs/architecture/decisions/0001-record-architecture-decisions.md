---
title: Record Architecture Decisions
status: active
owner: Victor Hueni
last_reviewed: 2026-05-22
review_interval: 180d
---

# Record Architecture Decisions

Date: 2026-05-22

## Status

Accepted

## Context and Problem Statement

Significant design decisions made during the evolution of the homemade-claude-kit
and its metamodel need to be traceable. Without recorded context, future skill
development diverges silently from earlier decisions.

## Decision Drivers

- Decisions made without recorded context are hard to revisit or challenge
- The kit ships as a user-global tool — design decisions affect every project it touches
- New skill authors need the history to stay consistent

## Considered Options

- Unstructured notes in README or BACKLOG
- Architecture Decision Records (MADR 4.x format)

## Decision Outcome

Chosen option: "Architecture Decision Records (MADR 4.x)", because the structured
format makes drivers, options, and trade-offs explicit and queryable.

### Positive Consequences

- Decisions are self-contained and searchable
- Supersession chains preserve the full history of a choice

### Negative Consequences

- Requires discipline to write ADRs before implementing, not after
