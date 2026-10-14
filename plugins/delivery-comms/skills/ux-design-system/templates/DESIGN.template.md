---
type: Design System
title: "{{product_or_scope}} design"
status: draft
owner: "{{owner}}"
last_reviewed: "{{YYYY-MM-DD}}"
review_interval: 180d
# The design subset this project's decks, views and release notes render with. ux-design-system `subset`
# reads the keys below (contract roles without their leading dashes, see contract/README.md in the
# delivery-comms plugin) and writes docs/ux/design-system/. The values are neutral defaults: replace them.
name: "{{product_or_scope}}"
colors:
  ink: "#1a1f29"
  muted: "#6b7280"
  canvas-bg: "#f6f7f9"
  surface: "#ffffff"
  surface-2: "#eef1f5"
  border: "#d7dce3"
  accent: "#396cf5"
  accent-ink: "#ffffff"
  success: "#2e9e5b"
  warning: "#f0ad4e"
  danger: "#d5413d"
  info: "#396cf5"
typography:
  font-body: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
  font-heading: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
  font-mono: 'ui-monospace, "SF Mono", "Cascadia Code", Menlo, monospace'
  title-size: 1.6rem
rounded:
  card-radius: 12px
  btn-radius: 8px
  node-radius: 10px
spacing:
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 2rem
  shell-max: 1400px
elevation:
  shadow: "0 1px 2px rgba(16,24,40,.06), 0 1px 3px rgba(16,24,40,.10)"
# No dataviz block yet: the first `subset` run proposes one from the accent for you to review.
# Optional modules this project does not fill, with the reason (the kit base theme stands in for them).
omitted:
  type: "the core font roles are enough"
  space-shape: "the core spacing is enough"
  document: "no paginated documents"
  slide-frame: "the kit slide frame is fine"
  print: "the kit page size and margins are fine"
  brand: "no logo or legal line yet"
---

# {{product_or_scope}} design

The prose below is exported as the design's `guidance` module: agents read it, the renderers do not.

## Overview

_TODO_: the personality and the primary audience, in two or three sentences.

## Colours

_TODO_: why this accent; where the state colours (success, warning, danger, info) appear and where they do not.

## Typography

_TODO_: why these typefaces. To load a typeface, add a `fonts:` list (family, src, weight, style) whose `src` is a font file beside this DESIGN.md; the kit never loads a font from the network.

## Do's and Don'ts

- _TODO_
