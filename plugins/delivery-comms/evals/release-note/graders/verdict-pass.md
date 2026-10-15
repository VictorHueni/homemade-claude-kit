---
type: regex
target:
  source: file
  path: docs/release-notes/pdf/v0.3.0.html.verdict.txt
pattern: '^PASS: no findings\nfile: (?:.*/)?docs/release-notes/pdf/v0\.3\.0\.html\ndesign: @acme-test/design-system@'
---

<!-- The verdict file `check_render.py --record` writes next to the output reads PASS, for this output, against the pinned design. -->
