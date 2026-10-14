---
type: regex
target:
  source: file
  path: out/deck.html.provenance.json
pattern: ^(?=[\s\S]*"name":\s*"@acme-test/design-system")(?=[\s\S]*"core":\s*"design-system")(?=[\s\S]*"dataviz":\s*"design-system")(?=[\s\S]*"slide-frame":\s*"design-system")(?=[\s\S]*"brand":\s*"design-system")
---

<!-- The provenance report next to the deck names the pinned design system as the source of core, dataviz, slide-frame and brand. -->
