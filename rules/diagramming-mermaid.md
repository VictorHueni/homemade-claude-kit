---
type: rule
paths:
  - "**/*.md"
---

# Mermaid diagrams on GitHub

Mermaid is the default for diagrams inline in GitHub markdown; use PlantUML (the `arch-uml` skill) only for what Mermaid cannot express, and Structurizr for C4.

GitHub's Mermaid parser is stricter than the CLI: a diagram that renders locally can fail with "Unable to render rich display / Parse error on line N".

**Flowcharts:** quote any label containing `<br/>`, apostrophes, parentheses, colons, commas or other punctuation: `Node["Foo<br/>Bar"]`, `Diamond{"Foo?"}`, edge labels `|"line1<br/>line2"|`. Error tell: "got NEWLINE" or "got STR".

**Sequence diagrams:** quoting does not help; rephrase the message. No semicolons (use `and` or `+`), no leading parentheses, no curly braces. `<br/>` works unquoted in `Note` blocks. Error tell: "Expecting SOLID_OPEN_ARROW / DOTTED_OPEN_ARROW".

Pre-commit audit:

```bash
grep -nE '\|[^"|]*<br/?>[^"|]*\||\[[^"][^]]*<br/?>[^]]*\]|\{[^"{}]*<br/?>[^"{}]*\}' file.md
grep -nE -e '->>|-->>' file.md | grep -E ': .*;|: \('
```
