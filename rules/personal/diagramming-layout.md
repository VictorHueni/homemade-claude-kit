---
type: rule
paths:
  - "**/*.svg"
  - "**/*.puml"
  - "**/*.dsl"
---

# Diagram edge routing

Orthogonal edges only, never diagonals. Prefer, in order: a straight segment (reposition boxes to align them), one elbow, two elbows, an outside detour; a turn is cheaper than a crossing. Box text never overflows: wrap it and grow the box. Audit hand-laid SVG by script: zero diagonals, elbow and crossing counts, no segment through a box, no label on a box or line.
