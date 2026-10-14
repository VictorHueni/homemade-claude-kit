---
type: regex
target:
  source: file
  path: make_table.py
pattern: ^(?=[\s\S]*design_source\.py)(?=[\s\S]*["']css["'])
---

<!-- The script obtains its CSS from `design_source.py css`: its source names the script and the `css` command. -->
