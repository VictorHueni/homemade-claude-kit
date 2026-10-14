---
type: regex
target:
  source: file
  path: docs/strategy/capability-map.html.provenance.json
pattern: ^(?=[\s\S]*"name":\s*"@acme-test/design-system")(?=[\s\S]*"core":\s*"design-system")(?=[\s\S]*"dataviz":\s*"design-system")
---

<!-- The provenance report names the pinned design system (found by walking up from the working folder), not the base theme. -->
