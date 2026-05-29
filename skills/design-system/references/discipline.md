# Design-system discipline

Internal guidance for the `design-system` skill.

## Principles

1. **One design system per project.** `docs/design/` holds the single visual
   source of truth. Consumers theme from it; they do not each define their own
   palette. Two design systems = drift.

2. **Author in Markdown, generate the CSS.** `design-system.md` is the human
   artefact (rationale + token tables); `tokens.css` is generated and
   machine-owned. Durable edits go in the `.md`. Mirrors the kit pattern of
   `com-slide-deck`'s `design-system.md → styles.css`.

3. **Names are the contract; values are the brand.** Every consumer relies on
   the token *names* in `references/token-contract.md`. Change values freely to
   re-brand; never rename or drop a token. Extending with extra tokens is fine.

4. **Domain-agnostic.** Unlike Anthropic's `brand-guidelines` (which hard-codes
   Anthropic's palette), the kit is user-global, so this skill ships only
   neutral defaults and a fillable template. No real brand colour, font, or
   client name appears on the skill side — only in a project's own
   `docs/design/`.

5. **No IDs, no links.** The design system mints no IDs and carries no FK
   references to other artefacts. It is a cross-cutting foundation, not a node
   in the artefact dependency graph. It does not appear in the ER diagram or the
   cross-doc ID conventions table.

## Boundaries — what this skill is NOT

- **Not a renderer.** It produces tokens, not HTML. Decks are `com-slide-deck`;
  artefact views are `com-artefact-viz`.
- **Not a component library.** It defines tokens (colour/type/space/shape), not
  reusable HTML/CSS components. Each consumer builds its own components *from*
  the tokens.
- **Not per-deck or per-view.** It is project-scoped (`docs/design/`), not
  scoped to one deck folder. A deck may still keep deck-specific CSS, but it
  should source its base tokens here.

## Relationship to com-slide-deck (current state)

`com-slide-deck` predates this skill and generates its own `design/styles.css`
per deck from a deck-local `design-system.md`. Today the integration is
**convention-level**: when authoring a deck's `styles.css`, reference the same
token values as `docs/design/tokens.css`. Full unification — having the deck's
`styles.css` `@import` or inherit `tokens.css` directly — is a deferred
follow-up tracked in the kit ledger. `com-artefact-viz` already consumes
`tokens.css` directly (auto-detected).
