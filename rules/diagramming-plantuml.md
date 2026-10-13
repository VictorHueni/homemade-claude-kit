---
type: rule
paths:
  - "**/*.puml"
---

# PlantUML message text

Message text is creole: two `--` on one line render as strikethrough between them (one alone is harmless; `__`, `**`, `~~` behave alike), and angle brackets (`<type>.csv`) are read as tags. Describe flags in words or escape with `~`. After rendering, `grep -c line-through views/*.svg` should be 0.
