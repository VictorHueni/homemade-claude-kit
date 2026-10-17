---
type: regex
target:
  source: file
  path: docs/communication/slides/board-update/output/slides/02-section.html
pattern: '<div\s+class="(?=(?:[^"]*\s)?slide[\s"])(?=(?:[^"]*\s)?dark[\s"])'
---

<!-- The section slide is marked dark on its partial's root `.slide` element, the switch the contract reads. -->
