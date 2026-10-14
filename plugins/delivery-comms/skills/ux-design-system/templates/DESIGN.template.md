---
type: Design System
title: "{{product_or_scope}} design"
status: draft
owner: "{{owner}}"
last_reviewed: "{{YYYY-MM-DD}}"
review_interval: 180d
# A Google DESIGN.md (github.com/google-labs-code/design.md): the design subset this project's decks, views
# and release notes render with. ux-design-system `subset` reads the tokens below (contract roles, see
# contract/README.md in the delivery-comms plugin) and writes docs/ux/design-system/. The values are neutral
# defaults: replace them.
name: "{{product_or_scope}}"
colors:
  # Google's primary colour is the kit's accent; keep this reference so both read the same colour.
  primary: "{colors.accent}"
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
  # The chart colours (chart-1 to chart-highlight) follow; while there are none, `subset` proposes them.
typography:
  body:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
  heading:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'
    fontSize: 1.6rem
  mono:
    fontFamily: 'ui-monospace, "SF Mono", "Cascadia Code", Menlo, monospace'
rounded:
  card-radius: 12px
  btn-radius: 8px
  node-radius: 10px
spacing:
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 2rem
  shell-max: 1400px
# What Google DESIGN.md has no key for: the card shadow, local font files (fonts: family, src, weight,
# style), and the optional modules this project does not fill, with the reason (the kit base theme stands in).
kit:
  shadow: "0 1px 2px rgba(16,24,40,.06), 0 1px 3px rgba(16,24,40,.10)"
  omitted:
    type: "the core font roles are enough"
    space-shape: "the core spacing is enough"
    document: "no paginated documents"
    slide-frame: "the kit slide frame is fine"
    print: "the kit page size and margins are fine"
    brand: "no logo or legal line yet"
---

# {{product_or_scope}} design

The prose below is exported as the design's `guidance` module: agents read it, the renderers do not. The section names and their order follow Google DESIGN.md.

## Overview

_TODO_: the personality and the primary audience, in two or three sentences.

## Colors

_TODO_: why this accent; where the state colours (success, warning, danger, info) appear and where they do not.

## Typography

_TODO_: why these typefaces. To load a typeface, add a `kit.fonts` list (family, src, weight, style) whose `src` is a font file beside this DESIGN.md; the kit never loads a font from the network.

## Do's and Don'ts

- _TODO_
