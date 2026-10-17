---
type: regex
target:
  source: file
  path: out/deck.html
match: count:1
pattern: 'class="(?=(?:[^"]*\s)?slide[\s"])(?=(?:[^"]*\s)?dark[\s"])'
---

<!-- Exactly one slide of the built deck carries the `dark` class: the section slide, not the whole deck (`theme: dark` would mark all three). -->
