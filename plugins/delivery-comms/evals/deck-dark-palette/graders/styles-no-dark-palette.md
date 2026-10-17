---
type: regex
target:
  source: file
  path: docs/communication/slides/board-update/design/styles.css
match: not_contains
pattern: '--dark-[\w-]+\s*:'
---

<!-- The deck's styles.css declares no `--dark-*` property: the dark roles come from the design, never from a deck-local palette. -->
