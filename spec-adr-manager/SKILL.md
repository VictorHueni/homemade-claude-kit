---
name: spec-adr-manager
description: Create, review, and update Architecture Decision Records (ADRs) using MADR 4.x conventions and repository ADR patterns. Use when asked to document an architecture/technical decision, compare options with rationale, supersede an older ADR, or improve ADR quality.
version: "1.0.0"
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "specification"
  complexity: "high"
---

# MADR ADR Decision

Use this skill to produce ADRs that are explicit, auditable, and easy to revisit.

## Workflow

1. Classify the request.

   - `Create`: write a new ADR from scratch.
   - `Update`: revise an existing ADR and keep decision history clear.
   - `Review`: audit an ADR and return findings plus a proposed rewrite.

2. Gather missing inputs before drafting.

   - Ask only for critical gaps: problem context, decision drivers, options, chosen option, consequences, status/date, and stakeholders.
   - Keep questions short and decision-oriented.

3. Apply repository conventions first, then MADR structure.

   - **First**, check for a `CONVENTIONS.md` in the ADR directory. If present, follow its naming, scoping, and style rules exactly.
   - Default location: `docs/design-docs/architecture-decisions/`.
   - If ADR numbering exists, continue the numbering pattern.
   - If the repo already has ADR style/location conventions, preserve those while ensuring MADR-quality decision content.

4. Draft the ADR using the MADR templates in `references/madr-templates.md`.

   - Use the full template for high-impact decisions.
   - Use the minimal template for small, localized decisions.

5. Validate quality with `references/adr-quality-checklist.md`.

   - Ensure one ADR contains one decision.
   - Ensure options, trade-offs, and consequences are explicit.
   - Ensure the chosen option is justified by decision drivers.

6. Finalize for traceability.

   - Link superseded/superseding ADRs where applicable.
   - Ensure title and filename are stable and searchable.
   - Keep language specific; remove vague claims like "best" without criteria.

## Output Rules

- Produce Markdown only.
- Keep the narrative factual and concise.
- Prefer complete ADR drafts over outlines unless the user asks for an outline.
- If inputs are incomplete and user wants speed, draft with explicit `[ASSUMPTION]` markers and list required confirmations at the end.

## Review Mode

When asked to review an ADR:

1. Report findings first, ordered by severity (`critical`, `major`, `normal`, `low`).
2. Reference exact file paths and lines when available.
3. Focus on decision quality problems:

   - missing decision drivers,
   - missing alternatives,
   - unjustified outcome,
   - unclear consequences,
   - broken traceability to prior ADRs.

4. Provide a corrected ADR text after findings if requested.

## References

- Use `references/madr-templates.md` for canonical section structure.
- Use `references/adr-quality-checklist.md` for acceptance criteria before finalizing.
