---
title: Example Platform — Design System
status: draft
owner: example
last_reviewed: 2026-05-29
review_interval: 180d
---

<!-- doc-version: 1.0 | created: 2026-05-29 -->

# Example Platform — Design System

A filled example. The single visual source of truth: slide decks and artefact
visualisations theme from the tokens below.

> **Authoring contract:** the `## Tokens` tables are machine-read to generate
> `tokens.css`. Keep the `Token` and `Value` columns intact.

---

## Brand rationale

- **Personality:** precise, calm, technical
- **Primary audience:** operators and engineers evaluating the platform
- **Accent reasoning:** a confident teal reads as trustworthy and modern without the SaaS-blue cliché
- **Typography reasoning:** a neutral system sans for legibility; a mono for IDs and code that recur throughout the artefacts

---

## Tokens

### Base palette

| Token | Value | Role |
|---|---|---|
| `--ink` | `#13211f` | Primary text |
| `--muted` | `#5f6b69` | Secondary text |
| `--canvas-bg` | `#f4f7f6` | Page background |
| `--surface` | `#ffffff` | Card / panel background |
| `--surface-2` | `#e8efed` | Recessed / group background |
| `--border` | `#cfdbd8` | Hairlines, dividers |
| `--accent` | `#0f9d8f` | Primary action, links, IDs |
| `--accent-ink` | `#ffffff` | Text on accent fills |

### Strategic importance (capability map)

| Token | Value | Role |
|---|---|---|
| `--differentiator` | `#c2453d` | Where the business wins or loses |
| `--necessary` | `#e0973a` | Required for operation |
| `--commodity` | `#5f6b69` | Could be outsourced |

### Delivery status (FBS, roadmap)

| Token | Value | Role |
|---|---|---|
| `--status-shipped` | `#2e9e5b` | Shipped (✅) |
| `--status-planned` | `#0f9d8f` | Planned (🔄) |
| `--status-backlog` | `#9aa3af` | Backlog (⬜) |

### Pain index (delivery roadmap)

| Token | Value | Role |
|---|---|---|
| `--pain-critical` | `#c2453d` | Critical pain |
| `--pain-high` | `#e0973a` | High pain |
| `--pain-medium` | `#0f9d8f` | Medium pain |
| `--pain-low` | `#9aa3af` | Low pain |

### Confidence (BMC / Lean Canvas)

| Token | Value | Role |
|---|---|---|
| `--conf-assumed` | `#9aa3af` | Assumed |
| `--conf-tested` | `#e0973a` | Tested |
| `--conf-validated` | `#2e9e5b` | Validated |

### Typography

| Token | Value | Role |
|---|---|---|
| `--font-sans` | `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` | Body + UI |
| `--font-mono` | `ui-monospace, "SF Mono", "Cascadia Code", Menlo, monospace` | IDs, code, labels |
| `--title-size` | `1.7rem` | View / slide title size |

### Spacing & shape

| Token | Value | Role |
|---|---|---|
| `--space-sm` | `0.5rem` | Tight gaps |
| `--space-md` | `1rem` | Default gaps |
| `--space-lg` | `2rem` | Section padding |
| `--shell-max` | `1400px` | Max content width |
| `--card-radius` | `14px` | Card corners |
| `--btn-radius` | `8px` | Button corners |
| `--node-radius` | `10px` | Tree-node / chip corners |
| `--shadow` | `0 1px 2px rgba(16,24,40,.06), 0 1px 3px rgba(16,24,40,.10)` | Card elevation |

---

## Open Items

_None at present._

---

## Changelog

| Date | Change | Author |
|---|---|---|
| 2026-05-29 | Initial example | example |
