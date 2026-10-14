---
type: regex
target:
  source: file
  path: make_table.py
match: not_contains
pattern: (?<![&\w])#[0-9a-fA-F]{3,8}(?![\w-])|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(
---

<!-- The script holds no literal colour. -->
