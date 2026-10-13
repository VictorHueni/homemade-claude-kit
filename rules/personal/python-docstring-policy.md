---
type: rule
paths:
  - "**/*.py"
---

# Python docstrings: Google §3.8 as written, not "every public name"

Stated policy (2026-09-30, ruled point by point after a measured audit of an agent-written codebase): a rule of the form "Google-style docstrings on all public functions and classes" is stricter than the Google guide it names, and it is where docstring bloat comes from. The audit found about 84 % of docstring lines worth keeping (contracts, rationale, domain meaning, summaries); the removable part was dominated by `Args` entries restating the signature (`engine: Database engine.`) plus the scaffolding around them, then implementation detail, then history and process references.

**How to apply:**

- A docstring is required for public API, nontrivial size or non-obvious logic. A one-line summary is enough when the name and signature say the rest.
- `Args` lists only parameters whose meaning, units or constraints the name and annotation do not give. Never repeat types that are annotated. `Returns` and `Raises` only when they add to the annotation and the summary. `@override` methods need none unless they refine the contract.
- Private (`_`) helpers need no docstring; add a why-line when the logic is non-obvious.
- No hard length cap: long docstrings are usually contracts, and a cap pushes real rationale out. Instead, implementation detail goes in a comment at the line it explains, rationale that restates an ADR or doc becomes a one-line pointer, and no docstring narrates the body step by step. Treat very long docstrings as a reading lead, never as a finding.
- No process history in docstrings or comments: plan and increment numbers, PRD and review IDs, owner rulings, issue numbers, dated changelog, "replaces"/"moved from". A one-line ADR pointer or doc path is fine when it resolves.
- Docstrings that a framework renders to users (a CLI command's `--help`, for instance) are user-facing copy and follow those rules. Check which docstrings actually reach users before assuming: an app that serves a hand-authored API contract never publishes its route docstrings.
- **Do not add, expand or reformat docstrings and comments on code you did not change. When you change code, update its docstring in the same edit or delete the sentence that no longer holds.**

**Why:** peer-reviewed studies found that incorrect documentation substantially degrades an LLM's understanding of code, while missing documentation did not measurably affect it (Macke and Doyle, NAACL 2024; CodeCrash, NeurIPS 2025). In an agent-maintained codebase every docstring is the next agent's context, so a restating docstring is a future contradiction with no offsetting value. The measured case bears it out: dozens of docstrings contradicted their code, and every one had the same shape. The code changed later and the docstring kept describing the old behaviour (a removed fallback, a retired function, a data feed that stopped). The last bullet is aimed at exactly that moment.

**Anti-pattern in self:** adding an `Args:` section to a function I only touched in passing, "for completeness", or writing "(Plan NNNN Inc NN)" into a docstring to explain why the code exists. The first grows what a cleanup removes; the second is history the commit message already carries.
