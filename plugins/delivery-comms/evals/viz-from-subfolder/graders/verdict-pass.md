---
type: regex
target:
  source: file
  path: docs/strategy/capability-map.html.verdict.txt
pattern: '^PASS: no findings\nfile: (?:.*/)?docs/strategy/capability-map\.html\ndesign: @acme-test/design-system@'
---

<!-- The verdict file `check_render.py --record` writes next to the output reads PASS, for this output, against the pinned design. -->
