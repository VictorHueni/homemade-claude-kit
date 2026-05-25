---
paths:
  - "docs/**"
---

# Artefact Frontmatter Convention

Every markdown file produced by a kit skill under `docs/` must open with this YAML frontmatter block:

```yaml
---
title: <human-readable title of this specific document instance>
status: draft
owner: <git config user.name>
last_reviewed: YYYY-MM-DD
review_interval: Nd
---
```

These five fields are **always present**. Two additional fields appear only when a specific lifecycle event occurs — never in an initial scaffold:

| Field | When it appears |
|---|---|
| `superseded_by` | Added when `status` switches to `superseded`. Points to the replacement. |
| `supersedes` | Added only on documents created specifically to replace another. Points to what was replaced. |

---

## Field rules

**`title`** — instance title, not the artefact type name.
- ✅ `"Payment Bounded Context Map"`
- ✅ `"PRD-0003 — Bulk Invoice Export"`
- ❌ `"Bounded Context Map"` (generic type — says nothing about the project)

**`status`** — one of four values:
- `draft` — being written; not yet authoritative; set this on every initial scaffold
- `active` — current and authoritative; decisions may be based on it
- `superseded` — replaced by another document; `superseded_by` is required
- `deprecated` — no longer relevant; kept for history only

**`owner`** — run `git config user.name` at creation time. Update when ownership changes.

**`last_reviewed`** — today's date in `YYYY-MM-DD`. Update on every meaningful review or edit, not just structural changes.

**`review_interval`** — cadence for staleness checks. Skill-specific defaults below; override per file when the project warrants it.

**`superseded_by`** — added to a document the moment its `status` switches to `superseded`. Relative path to the replacement. Never present on `draft`, `active`, or `deprecated` documents.

**`supersedes`** — added only to a document that was created specifically to replace another. Relative path to what it replaced. Absent on documents that were not written as a replacement for a prior document.

```yaml
# the document being retired:
status: superseded
superseded_by: docs/domain/bounded-contexts-v2.md

# the replacement document (only if it was written to replace the above):
supersedes: docs/domain/02b-bounded-contexts.md
```

---

## Default review intervals by artefact

| Interval | Artefacts |
|---|---|
| `30d` | PRDs · Implementation plans |
| `60d` | Delivery roadmap · Business objectives · Quality attributes |
| `90d` | Value streams · Processes · BMC · Competitive landscape · FBS · Ideas · Runbooks · RCAs · Architecture research |
| `180d` | Vision · Personas · Capability map · Bounded contexts · Glossary · Domain model · ADRs |

---

## ADRs — status lives in frontmatter only

The `## Status` section is **removed** from the MADR body. Frontmatter `status` is the single source of truth.

Supersession follows the same conditional field rules as all other artefacts:

```yaml
# old ADR — status switches to superseded, superseded_by is added:
status: superseded
superseded_by: docs/architecture/decisions/adr-0003-use-cockroachdb.md

# new ADR — created specifically as a replacement, so supersedes is added:
status: active
supersedes: docs/architecture/decisions/adr-0002-use-postgresql.md
```

---

## Audit enforcement (util-metamodel-audit)

The audit skill checks every `docs/**/*.md` for:

- Frontmatter block present
- `status` is one of the four allowed values
- `owner` is populated (not empty, not a placeholder)
- `last_reviewed` + `review_interval` → flags files overdue for review
- When `status: superseded` → `superseded_by` must be present and the target path must resolve to an existing file
- When `supersedes` is present → target path must resolve to an existing file with `status: superseded`
- ADR-specific: `## Status` section absent from body
