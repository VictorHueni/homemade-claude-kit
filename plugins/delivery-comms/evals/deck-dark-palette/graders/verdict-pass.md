---
type: regex
target:
  source: file
  path: out/deck.html.verdict.txt
pattern: '^PASS: no findings\nfile: (?:.*/)?out/deck\.html\ndesign: @acme-test/design-system-dark@'
---

<!-- The verdict file `check_render.py --record` writes next to the output reads PASS, for this output, against the pinned design that provides dark. -->
