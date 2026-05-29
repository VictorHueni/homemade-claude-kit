---
title: {{product_or_scope}} — Design System
status: draft
owner: {{owner}}
last_reviewed: {{YYYY-MM-DD}}
review_interval: 180d
---

<!-- doc-version: 1.0 | created: {{YYYY-MM-DD}} -->

# {{product_or_scope}} — Design System

The single visual source of truth for this project. Every generated visual
artefact — slide decks (`com-slide-deck`), artefact visualisations
(`com-artefact-viz`) — themes itself from the tokens defined here. Edit the
token tables below, regenerate `tokens.css`, and every deck and view re-themes
with no change to any renderer.

> **Authoring contract:** the `## Tokens` tables below are machine-read by the
> `design-system` skill to generate [`tokens.css`](./tokens.css). Keep the
> `Token` and `Value` columns intact; the `Role` column is for humans. Token
> *names* are the fixed contract (see the skill's `references/token-contract.md`)
> — change values freely, but do not rename or drop a token.

---

## Brand rationale

*Why the palette and type choices fit this product / audience. Replace the
placeholders; keep it short.*

- **Personality:** _TODO_ (e.g. "precise, calm, technical")
- **Primary audience:** _TODO_
- **Accent reasoning:** _TODO_ (why this accent colour)
- **Typography reasoning:** _TODO_ (why these typefaces)

---

## Tokens

### Base palette

| Token | Value | Role |
|---|---|---|
| `--ink` | `#1a1f29` | Primary text |
| `--muted` | `#6b7280` | Secondary text |
| `--canvas-bg` | `#f6f7f9` | Page background |
| `--surface` | `#ffffff` | Card / panel background |
| `--surface-2` | `#eef1f5` | Recessed / group background |
| `--border` | `#d7dce3` | Hairlines, dividers |
| `--accent` | `#3b6ef5` | Primary action, links, IDs |
| `--accent-ink` | `#ffffff` | Text on accent fills |

### Strategic importance (capability map)

| Token | Value | Role |
|---|---|---|
| `--differentiator` | `#d9534f` | Where the business wins or loses |
| `--necessary` | `#f0ad4e` | Required for operation |
| `--commodity` | `#6b7280` | Could be outsourced |

### Delivery status (FBS, roadmap)

| Token | Value | Role |
|---|---|---|
| `--status-shipped` | `#2e9e5b` | Shipped (✅) |
| `--status-planned` | `#3b6ef5` | Planned (🔄) |
| `--status-backlog` | `#9aa3af` | Backlog (⬜) |

### Pain index (delivery roadmap)

| Token | Value | Role |
|---|---|---|
| `--pain-critical` | `#d9534f` | Critical pain |
| `--pain-high` | `#f0ad4e` | High pain |
| `--pain-medium` | `#3b6ef5` | Medium pain |
| `--pain-low` | `#9aa3af` | Low pain |

### Confidence (BMC / Lean Canvas)

| Token | Value | Role |
|---|---|---|
| `--conf-assumed` | `#9aa3af` | Assumed |
| `--conf-tested` | `#f0ad4e` | Tested |
| `--conf-validated` | `#2e9e5b` | Validated |

### Typography

| Token | Value | Role |
|---|---|---|
| `--font-sans` | `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` | Body + UI |
| `--font-mono` | `ui-monospace, "SF Mono", "Cascadia Code", Menlo, monospace` | IDs, code, labels |
| `--title-size` | `1.6rem` | View / slide title size |

### Spacing & shape

| Token | Value | Role |
|---|---|---|
| `--space-sm` | `0.5rem` | Tight gaps |
| `--space-md` | `1rem` | Default gaps |
| `--space-lg` | `2rem` | Section padding |
| `--shell-max` | `1400px` | Max content width |
| `--card-radius` | `12px` | Card corners |
| `--btn-radius` | `8px` | Button corners |
| `--node-radius` | `10px` | Tree-node / chip corners |
| `--shadow` | `0 1px 2px rgba(16,24,40,.06), 0 1px 3px rgba(16,24,40,.10)` | Card elevation |

---

## How consumers use this

| Consumer | How it themes from this design system |
|---|---|
| `com-artefact-viz` | `python scripts/render.py SRC.md --design-system docs/design/tokens.css` (auto-detected if present) |
| `com-slide-deck` | Reference these token values when generating the deck's `design/styles.css` |

---

## Open Items

_None at present._

---

## Changelog

| Date | Change | Author |
|---|---|---|
| {{YYYY-MM-DD}} | Initial scaffold | {{owner}} |
