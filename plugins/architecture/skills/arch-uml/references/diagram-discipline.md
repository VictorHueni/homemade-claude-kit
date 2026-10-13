# Diagram discipline — readability + boundaries

Internal Claude guidance for `arch-uml`. Read before authoring. Two halves: **layout discipline** (make the diagram readable) and **boundary discipline** (don't draw what another skill owns).

---

## Part 1 — Layout discipline

PlantUML auto-lays-out via Graphviz; you steer it, you don't hand-place. The goal is a diagram a reader parses in seconds.

### The cardinal rule: fewest directed statements

Borrowed from C4-PlantUML's [layout best practices](https://deepwiki.com/plantuml-stdlib/C4-PlantUML/4.4-layout-best-practices): **use the fewest layout/direction hints that achieve the result.** Every forced direction fights the auto-layout and tends to create new crossings elsewhere. Add a hint, re-render, keep it only if it helped.

### One concern per diagram

The single biggest readability lever. A `.puml` should cover **one** scenario, **one** bounded context's classes, **one** aggregate's lifecycle. Symptoms you've overloaded it:

| Symptom | Fix |
|---|---|
| You need to scroll/zoom to read it | Split into two numbered files of the same type (`seq-01`, `seq-02`) |
| A sequence exceeds ~12 messages | Extract a sub-scenario or a `ref` |
| A class diagram exceeds ~10 classes | Split by aggregate / bounded context |
| A use-case diagram exceeds ~8 use cases | Split by actor group or subsystem |

### Direction, deliberately

- Default is top-down. `left to right direction` reads better for **use-case** diagrams and wide **activity** flows.
- Sequence diagrams have a fixed left-to-right participant axis — order participants by who initiates (leftmost) to reduce arrow length.
- For class/ER, let Graphviz decide; only nudge with relationship ordering if crossings are bad.

### Edge routing

- Orthogonal edges only, never diagonals. Prefer, in order: a straight segment (reposition boxes so they align, placing each next to its strongest connections), one elbow, two elbows, an outside detour. A turn is cheaper than a crossing, but prefer fewer of both.
- Treat layout as a joint problem: swapping two boxes' rows or columns often removes several elbows at once.
- Box text never overflows: wrap it and grow the box (SVG `<text>` neither wraps nor clips).
- Audit hand-laid SVG by script, not by eye: zero diagonals, elbow and crossing counts, no segment through a box, no label on a box or line.

### Labels and legends

- Every relationship/transition carries a label (the verb, event, or multiplicity). An unlabelled arrow is a question for the reader.
- Use a `legend` only when the notation isn't self-evident (e.g. a colour or stereotype convention). Place it `right` or `bottom`.
- Carry the **upstream ID** in the `title` and on the key elements (`UC-01`, `BC-01.AGG-02`). The rendered SVG must let a reviewer cross-reference without opening the source.

### Theme, not inline styling

Never hard-code colours/fonts in a diagram — they belong in `_theme.puml` so re-theming is one edit. If a diagram needs a one-off highlight, use a stereotype (`<<critical>>`) and add the style to the theme, not the diagram.

---

## Part 2 — Boundary discipline (what NOT to draw here)

`arch-uml` overlaps three neighbours. Keep the lines clean.

### vs `arch-c4` / `arch-structurizr` — the C4 boundary

**Do not draw C4 diagrams in PlantUML.** Context, container, component and deployment views are the Structurizr toolchain's job — it owns the single C4 model and renders all four view types from it. If asked for "the architecture diagram," disambiguate:

| The user wants… | Send to |
|---|---|
| How the system fits among users + external systems | `arch-c4 context` |
| The containers/tech stack inside the system | `arch-c4 container` |
| Components inside a container | `arch-c4 component` |
| Where it deploys | `arch-c4 deployment` |
| How containers collaborate at runtime (arc42 §6) | **`arch-uml sequence`**, lifelines named with their `CON-NN` |
| A **behavioural** or structural UML view (an aggregate's state machine, a class model) | **`arch-uml`** |

### vs Mermaid — the non-UML boundary

`rules/diagramming-mermaid.md` sends every UML diagram here, however simple. Mermaid keeps only diagrams that are neither UML nor C4: flowcharts, mind maps, timelines, Gantt charts.

### vs `domain-model` — the ownership boundary

`domain-model` **owns** the domain's aggregates, entities, events, and lifecycles as the authoritative text. `arch-uml` **visualises** them — a class/state/ER diagram is a *view* of the domain model, not a second source of truth. So:

- Read the domain-model artefact first; carry its names and `BC-NN.AGG-NN` IDs verbatim.
- If the diagram and the domain-model text disagree, the **text wins** — fix the diagram (or flag the domain-model gap), never let the SVG become the de-facto spec.
- A state machine here is a *rendering* of the aggregate lifecycle the domain model describes; it does not invent states.

---

## Quick authoring checklist (readability)

- [ ] One concern; fits on screen without scrolling
- [ ] Fewest direction hints that achieve a clean layout
- [ ] Every arrow/transition labelled
- [ ] Upstream ID in the title + on key elements
- [ ] Styling comes from `_theme.puml`, not inline
- [ ] Correct tool chosen (UML, not a C4 view, not a flowchart or other non-UML diagram)
