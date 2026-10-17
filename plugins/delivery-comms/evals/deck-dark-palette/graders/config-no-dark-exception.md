---
type: regex
target:
  source: file
  path: docs/communication/slides/board-update/config.yaml
match: not_contains
flags: m
pattern: '^\s*"?(?:--)?dark-[\w-]+"?\s*:'
---

<!-- No `design.exceptions` entry keeps the old palette alive under its own name. -->
