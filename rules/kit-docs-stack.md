---
type: rule
paths:
  - "docs/**"
---

# Kit documentation stack: pointer

Work that builds, extends, audits or navigates the documentation under `docs/` starts at the `metamodel` skill (kit ADR-0007). Read it; do not restate it.

- Spine, variants and agent workflow: its `SKILL.md`. DAG, ER, per-step process, ID conventions and canonical paths: `references/metamodel-reference.md`.
- Artefact types (`id_format`, layout, `default_path`, `review_interval`, `okf_type`): `references/artefact-types-registry.yaml`. Parse it, never infer from memory; new types are authored clew-side first (clew ADR-0008).
- Every `docs/**` file a kit skill writes opens with the frontmatter in `references/artefact-frontmatter.md`; its `type:` is the registry's `okf_type`, verbatim.
- Unresolved governance work follows `references/open-items-governance.md` and is operated through `util-open-items`, whose backend is a markdown ledger or GitHub Issues per project. Inline `_TODO_` placeholders are not open items.
