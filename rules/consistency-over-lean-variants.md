---
type: rule
---

# Reuse the codebase's existing pattern before a leaner bespoke one

When a new subsystem solves a problem the codebase already solves (human overrides of machine output, audit logs, review queues, versioned reference data), start from the existing design: same table shape, enums, column names and command verbs. Map it column by column, name every departure and try to remove it, keeping only those the new domain forces. Cut scope rather than invent a lighter mechanism.
