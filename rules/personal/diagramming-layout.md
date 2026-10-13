---
type: rule
---

# Diagram edge-routing preferences (SVG, PlantUML, any hand-laid diagram)

Stated preference (2026-08-25, while iterating on a hand-drawn SVG conceptual model): minimize the number of elbows ("coudes") in connector edges, and use straight orthogonal lines — **never diagonals**.

**Priority order when routing edges:**

1. Straight single-segment line (align the two boxes on a shared row/column if a small reposition buys it — place each entity on the row/side nearest its strongest connections so edges span less).
2. One elbow (L-shape).
3. Two elbows (Z-shape) only when boxes block the L.
4. A longer detour around an outside margin beats a shorter path with crossings: turns are visually cheaper than intersections, but prefer fewer of both.

**How to apply:** treat layout as joint optimization — swapping two boxes' rows/columns often converts several 3-turn margin detours into straight verticals (measured: 13 elbows → 7 and 2 crossings → 1 on one pass, purely by repositioning). After routing, audit programmatically rather than eyeballing: parse the segments, assert zero diagonals, count elbows and orthogonal-segment crossings, and check no segment passes through a box interior and no label sits on a box or line.

**Related:** entity/box text must never overflow its box — wrap onto several lines and grow the box instead (SVG `<text>` neither wraps nor clips; with a monospace attr font, `len(text) × advance` makes overflow provable by script).
