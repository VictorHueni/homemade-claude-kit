---
type: regex
target:
  source: file
  path: out/figures.html.verdict.txt
pattern: '^PASS: no findings\nfile: (?:.*/)?out/figures\.html\ndesign: @acme-test/design-system@'
---

<!-- The verdict file `check_render.py --record` writes next to the output reads PASS, for this output, against the pinned design. -->
