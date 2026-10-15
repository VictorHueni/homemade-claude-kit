---
type: regex
target:
  source: file
  path: out/deck.html
match: count:3
pattern: \bclass="slide(?:\s[^"]*)?"
---

<!-- Exactly three slides, counted on the root `.slide` elements of the built deck. -->
