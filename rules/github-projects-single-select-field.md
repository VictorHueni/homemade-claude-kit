---
type: rule
---

# Adding a GitHub Projects single-select option clears every item's value

`updateProjectV2Field` replaces the field's whole option array: send every existing option (name, colour, description) plus the new one, or the missing ones are deleted. Even then it regenerates every option id, so every item loses its value. Before the mutation, snapshot each item's id and option *name*; afterwards restore the values by name and diff a fresh snapshot against the old one (same item count, same per-option distribution). Without a snapshot, add the option in the web UI instead.
