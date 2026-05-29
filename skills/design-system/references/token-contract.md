# Token contract

The canonical `:root` vocabulary shared by every `com-*` renderer. `tokens.css`
(generated from `design-system.md`) defines exactly these names so any consumer
can rely on them. **Names are fixed; values are free.** Renaming or dropping a
token breaks consumers; `generate_tokens.py` warns when a contract token is
missing. Projects MAY add extra tokens (kept, flagged as "not in contract").

The authoritative list also lives in `templates/tokens.template.css` — the
generator validates against it.

## Groups

### Base palette
| Token | Role |
|---|---|
| `--ink` | Primary text |
| `--muted` | Secondary text |
| `--canvas-bg` | Page background |
| `--surface` | Card / panel background |
| `--surface-2` | Recessed / group background |
| `--border` | Hairlines, dividers |
| `--accent` | Primary action, links, IDs |
| `--accent-ink` | Text on accent fills |

### Strategic importance (capability map)
| Token | Role |
|---|---|
| `--differentiator` | Where the business wins or loses |
| `--necessary` | Required for operation |
| `--commodity` | Could be outsourced |

### Delivery status (FBS, roadmap)
| Token | Role |
|---|---|
| `--status-shipped` | Shipped (✅) |
| `--status-planned` | Planned (🔄) |
| `--status-backlog` | Backlog (⬜) |

### Pain index (delivery roadmap)
| Token | Role |
|---|---|
| `--pain-critical` · `--pain-high` · `--pain-medium` · `--pain-low` | Pain bands |

### Confidence (BMC / Lean Canvas)
| Token | Role |
|---|---|
| `--conf-assumed` · `--conf-tested` · `--conf-validated` | Confidence ratings |

### Typography
| Token | Role |
|---|---|
| `--font-sans` | Body + UI |
| `--font-mono` | IDs, code, labels |
| `--title-size` | View / slide title size |

### Spacing & shape
| Token | Role |
|---|---|
| `--space-sm` · `--space-md` · `--space-lg` | Spacing scale |
| `--shell-max` | Max content width |
| `--card-radius` · `--btn-radius` · `--node-radius` | Corner radii |
| `--shadow` | Card elevation |

## Consumer mapping

| Token group | Used by |
|---|---|
| Base palette, typography, spacing | `com-slide-deck`, `com-artefact-viz` (all views) |
| Strategic importance | `com-artefact-viz` capability-map |
| Delivery status | `com-artefact-viz` fbs + roadmap |
| Pain index | `com-artefact-viz` roadmap |
| Confidence | `com-artefact-viz` bmc |

`com-slide-deck` consumes the base palette + typography + spacing groups; the
semantic groups are viz-specific but harmless in a deck context (unused tokens
cost nothing).
