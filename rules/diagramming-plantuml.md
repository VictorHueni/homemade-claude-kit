---
type: rule
---

# PlantUML message text: creole markup eats CLI flags

Sequence-diagram message text is parsed as creole. Two `--` pairs on one line (`--default-site MA [--allow-unclassified]`) render as **strikethrough** between them, with no warning and a clean `-checkonly` pass. One `--` alone is harmless, which is why the trap only fires on the message that lists two flags. Same family: `__x__` underlines, `**x**` bolds, `~~x~~` strikes.

**How to apply:** never paste a literal command line with several long flags into a message; describe it in words ("default site MA, optionally allowing unclassified tabs") or escape with `~`. After rendering, `grep -c "line-through" views/*.svg` is a one-line audit that catches it without opening the picture. Angle brackets in messages (`<type>.csv`) are also unsafe: PlantUML treats them as HTML-ish tags; use a plain word instead.

**Why:** the diagram validates and renders, so the only signal is visual, and a reviewer reading the SVG sees a struck-out flag and assumes it was deliberately removed. Measured 2026-09-07 on the first render of a consolidate-run sequence diagram.
