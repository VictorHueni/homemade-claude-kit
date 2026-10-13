---
type: rule
paths:
  - "**/*.md"
---

# Mermaid diagrams on GitHub

C4 views (context, container, component, deployment) use Structurizr (`arch-c4`); every UML diagram (sequence, class, state, activity, ER, use-case, arc42 §6 runtime scenarios included) uses PlantUML (`arch-uml`); Mermaid is only for diagrams that are neither, such as flowcharts, mind maps, timelines and Gantt charts.

GitHub's Mermaid parser is stricter than the CLI: a diagram that renders locally can fail with "Unable to render rich display / Parse error on line N".

**Flowcharts:** quote any label containing `<br/>`, apostrophes, parentheses, colons, commas or other punctuation: `Node["Foo<br/>Bar"]`, `Diamond{"Foo?"}`, edge labels `|"line1<br/>line2"|`. Error tell: "got NEWLINE" or "got STR".

**Sequence diagrams:** quoting does not help; rephrase the message. No semicolons (use `and` or `+`), no leading parentheses, no curly braces. `<br/>` works unquoted in `Note` blocks. Error tell: "Expecting SOLID_OPEN_ARROW / DOTTED_OPEN_ARROW".

Pre-commit audit:

```bash
grep -nE '\|[^"|]*<br/?>[^"|]*\||\[[^"][^]]*<br/?>[^]]*\]|\{[^"{}]*<br/?>[^"{}]*\}' file.md
grep -nE -e '->>|-->>' file.md | grep -E ': .*;|: \('
```
