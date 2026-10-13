---
type: rule
paths:
  - "**/*.py"
---

# Python docstrings: Google §3.8 as written, not "every public name"

- A docstring is required for public API, nontrivial size or non-obvious logic. A one-line summary is enough when the name and signature say the rest.
- `Args` lists only parameters whose meaning, units or constraints the name and annotation do not give, never with types. `Returns` and `Raises` only when they add to the annotation and summary. `@override` methods need none unless they refine the contract.
- Private (`_`) helpers need no docstring; add a why-line when the logic is non-obvious.
- No length cap; treat a very long docstring as a reading lead, never as a finding. Implementation detail goes in a comment at the line it explains; rationale that restates an ADR or doc becomes a one-line pointer; no docstring narrates the body.
- No process history in docstrings or comments: plan or increment numbers, PRD or review IDs, rulings, issue numbers, dated notes, "replaces"/"moved from". A one-line ADR or doc pointer is fine when it resolves.
- Docstrings a framework shows to users (a CLI command's `--help`) are user-facing copy and follow those rules. Check which ones actually reach users: an app serving a hand-authored API contract never publishes its route docstrings.
- **Do not add, expand or reformat docstrings and comments on code you did not change. When you change code, update its docstring in the same edit or delete the sentence that no longer holds.**

Why: an outdated docstring misleads the next agent more than a missing one, and every docstring is its context.
