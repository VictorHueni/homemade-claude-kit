---
type: rule
---

# Reuse the codebase's existing pattern before proposing a leaner bespoke one

Stated preference (2026-10-05, choosing a storage design for human decisions on derived data): « I want consistency to ease maintainability ». Offered a lean separate table versus the repository's existing pattern for the same problem (an append-only result log with authority, verdict, supersession chain and schema-enforced constraints), the owner chose the existing pattern, followed faithfully, and asked that its departures be removed rather than justified.

**How to apply:** when a new subsystem solves a problem the codebase already solves elsewhere (human overrides over machine output, audit logs, review queues, versioned reference data), start from that existing design: same table shape, same enums, same column names, same command verbs. Present the mapping column by column. Name every departure explicitly and look for a way to remove it before proposing it; keep only those the new domain forces (and say which domain fact forces each). Scope cuts (deferring exceptions to a later increment) are fine; model differences are what cost maintenance.

**Why:** a second model for the same concern doubles what a maintainer must learn and keep in sync, and a « simpler » bespoke design is only simpler in isolation. The owner also asked « are we over-engineering this? » in the same discussion: the answer that held was to keep the familiar pattern and cut scope, not to invent a lighter mechanism.
