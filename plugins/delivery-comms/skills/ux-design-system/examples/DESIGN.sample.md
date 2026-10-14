---
type: Design System
title: "Example Platform design"
status: draft
owner: example
last_reviewed: "2026-10-14"
review_interval: 180d
name: Example Platform
colors:
  primary: "{colors.accent}"
  ink: "#13211f"
  muted: "#5f6b69"
  canvas-bg: "#f4f7f6"
  surface: "#ffffff"
  surface-2: "#e8efed"
  border: "#cfdbd8"
  accent: "#0b7a6f"
  accent-ink: "#ffffff"
  success: "#2e9e5b"
  warning: "#e0973a"
  danger: "#c2453d"
  info: "#0b7a6f"
  chart-1: "#0b7a6f"
  chart-2: "#489b93"
  chart-3: "#85bcb7"
  chart-4: "#c2dedb"
  chart-rest: "#afb5b4"
  chart-axis: "#5f6b69"
  chart-grid: "#cfdbd8"
  chart-highlight: "#e0973a"
typography:
  body:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
  heading:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 1.7rem
  mono:
    fontFamily: 'ui-monospace, "SF Mono", "Cascadia Code", Menlo, monospace'
rounded:
  card-radius: 14px
  btn-radius: 8px
  node-radius: 10px
spacing:
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 2rem
  shell-max: 1400px
kit:
  shadow: "0 1px 2px rgba(16,24,40,.06), 0 1px 3px rgba(16,24,40,.10)"
  omitted:
    type: "the core font roles are enough"
    space-shape: "the core spacing is enough"
    document: "no paginated documents"
    slide-frame: "the kit slide frame is fine"
    print: "the kit page size and margins are fine"
    brand: "no logo yet"
---

# Example Platform design

A filled example, drafted from `legacy.tokens.css` with `subset --from-legacy` and then completed. The legacy teal accent (#0f9d8f) carried white text at 3.4:1, below WCAG AA, so `subset` refused it; the accent here is the same hue darkened to #0b7a6f. The chart palette is the proposal `subset` made from that accent, accepted as is.

## Overview

Precise, calm, technical. Read by operators and engineers evaluating the platform.

## Colors

A confident teal reads as trustworthy without the usual product blue. Red appears only where something is wrong.

## Typography

A neutral system sans for legibility; a mono for the IDs and code that recur throughout the artefacts.

## Do's and Don'ts

- Do keep the accent for links, IDs and the primary action.
- Don't use the warning amber as text on white: it is a fill colour.
