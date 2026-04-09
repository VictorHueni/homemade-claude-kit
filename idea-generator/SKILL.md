---
name: idea-generator
description: "Create or update structured idea files in docs/ideas/. Use when brainstorming, capturing UX ideas, noting improvements, or updating idea status. Triggers on: /idea, new idea, add idea, update idea, idea status."
version: "1.0.0"
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "specification"
  complexity: "low"
---

# Idea Generator

You manage structured idea files for the project. Ideas capture problems, potential solutions, and decisions — one idea per file, organized by domain.

---

## Conventions

### Folder structure

```
docs/ideas/
  frontend/
    INDEX.md
    accordion-visual-weight.md
    ...
  backend/
    INDEX.md
    ...
  infra/
    INDEX.md
    ...
```

- One **domain folder** per area: `frontend`, `backend`, `infra`, `data`, `design`, `dx` (developer experience), or any other domain.
- One **file per idea**, named with a short kebab-case slug (3-5 words max).
- One **INDEX.md** per domain folder — a table listing all ideas with status and one-line summary.

### Idea file format

```markdown
---
title: Short descriptive title
domain: frontend | backend | infra | data | design | dx
status: idea | decided | done | abandoned
created: YYYY-MM-DD
decided_at:
exec_plan:
prd:
---

## Problem

What is wrong, missing, or suboptimal today. 1-3 sentences.
Include the user impact — who is affected and how.

## Decision

_Present when status is `decided` or later. Remove the Ideas section when a decision is made._

What we are doing about it. Clear, actionable statement.

## Ideas

_Present when status is `idea`. List options under consideration._

Options can use any structure that fits:
- **Lettered items** (A, B, C...) for discrete alternatives
- **Numbered list** for ranked improvements
- **Comparison table** for prototype-vs-implementation gaps
- **Freeform** for early-stage brainstorms

Each option should have enough context to evaluate independently.

## Details

Supporting information. Flexible structure — use whatever fits:
- Comparison tables (prototype vs current)
- Technical constraints or dependencies
- Backend scope / API changes needed
- Mockup descriptions

If details exceed ~100 lines, the idea should be split.

## References

Links grouped by type:
- **Current implementation:** source file paths
- **Prototypes:** HTML prototype paths
- **External:** URLs to docs, patterns, inspiration
- **Related ideas:** links to other idea files
```

### INDEX.md format

```markdown
# [Domain] Ideas

| Status | Idea | Summary |
|:-------|:-----|:--------|
| decided | [Accordion visual weight](accordion-visual-weight.md) | Single card + divide-y instead of per-item box borders |
| idea | [Search facet counts](search-facet-counts.md) | Show hit counts per filter option |
```

Sort: `idea` first, then `decided`, then `done`, then `abandoned`.
Summaries under 100 characters.

### Status lifecycle

```
idea  ->  decided  ->  done
  |
  v
abandoned
```

- **idea** — Under consideration. May have multiple options.
- **decided** — Approach chosen. Set `decided_at`. When taken for implementation, link `exec_plan` or `prd`.
- **done** — Implemented and shipped.
- **abandoned** — Dropped. Add a short reason in the Decision section.

---

## The Job

### Mode 1: Create a new idea

1. If the user does not specify a domain, ask which domain (with lettered options).
2. Discuss the problem and potential solutions with the user.
3. Generate the idea file following the format above.
4. Save to `docs/ideas/[domain]/[slug].md`.
5. Create the domain folder and INDEX.md if they don't exist.
6. Add the idea to INDEX.md.

### Mode 2: Update an existing idea

1. Read the current idea file.
2. Apply the requested change (update status, add decision, add options, link exec plan).
3. When status changes to `decided`:
   - Set `decided_at` to today's date.
   - Move the chosen approach from Ideas to Decision.
   - Remove the Ideas section.
4. When linking an exec plan or PRD, update the frontmatter field.
5. Update INDEX.md to reflect the new status/summary.

### Mode 3: List ideas

When the user asks to see ideas for a domain, read and display the INDEX.md for that domain. If they ask for all ideas, list all domain INDEX.md files.

---

## Rules

- One idea per file. If an idea covers multiple independent changes, split it.
- Always fill the References section.
- Do not duplicate content that belongs in exec plans or PRDs.
- Keep file names short: 3-5 words, kebab-case.
- When creating a domain folder for the first time, create INDEX.md simultaneously.
- Today's date format: YYYY-MM-DD.

---

## Checklist

Before saving:

- [ ] Frontmatter is complete (title, domain, status, created)
- [ ] Problem section explains user impact
- [ ] Ideas or Decision section is present (not both)
- [ ] References section has at least one link
- [ ] INDEX.md is updated
- [ ] File name is kebab-case, 3-5 words
