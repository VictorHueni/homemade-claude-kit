---
type: regex
target:
  source: file
  path: out/figures.html
match: not_contains
flags: i
pattern: (?:(?<=(?:colou?r|fill|stroke|background|border|outline|shadow|caret|accent)[^;{}<>]{0,120}?)(?<![&\w])#[0-9a-fA-F]{3,8}(?![\w-])|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\()(?<!<style\b[^>]*\bdata-design-layer\b[^>]*>[^<]*)
---

<!-- No literal colour (hex, rgb()/hsl() family) in the output outside the inlined `<style data-design-layer>` block; independent of the verdict file the agent writes. -->
