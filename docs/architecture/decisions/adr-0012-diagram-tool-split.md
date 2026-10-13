---
title: Diagram Tool Split — Structurizr for C4, PlantUML for All UML, Mermaid for the Rest
status: active
owner: Victor Hueni
last_reviewed: 2026-10-13
review_interval: 180d
---

# Diagram Tool Split — Structurizr for C4, PlantUML for All UML, Mermaid for the Rest

Date: 2026-10-13

## Context and Problem Statement

The kit had three diagram tools with overlapping scopes. The Mermaid rule made Mermaid the default for any diagram in GitHub markdown and PlantUML the exception for what Mermaid cannot express. `arch-c4` could draw arc42 §6 runtime scenarios as Structurizr dynamic views, while ADR-0004 also allowed an `arch-uml` sequence for the same section, split by a judgement call (cross-container flow versus intra-component detail). Skills drew domain class and state diagrams and business-process sequences in Mermaid unless the agent decided to escalate them.

The result was that the same kind of diagram landed in different tools depending on the agent's reading of a boundary rule, and the routing lived in prose spread over six skills instead of in each skill's description.

## Decision Drivers

- One tool per diagram kind, chosen mechanically, not by judgement.
- Model-invoked skill selection works from skill descriptions, so the routing must be stated there.
- UML diagrams share one notation, theme and render pipeline.
- GitHub renders Mermaid inline, which keeps simple non-UML diagrams cheap.

## Considered Options

1. **Split by diagram kind** (chosen): C4 views in Structurizr, every UML diagram in PlantUML, Mermaid only for diagrams that are neither.
2. **Mermaid-first with escalation** (status quo): fails the first driver.
3. **PlantUML for everything, C4 included**: duplicates the Structurizr model that `arch-c4` keeps as the single source of C4 truth.

## Decision Outcome

Chosen option 1.

1. **C4** (context, container, component, deployment) is drawn by `arch-c4` from the Structurizr workspace. `arch-c4` has no runtime mode and writes no `dynamic` view.
2. **Every UML diagram** (sequence, class, state, activity, ER, use-case) is drawn by `arch-uml` through the `arch-plantuml` pipeline, however simple. This includes every arc42 §6 runtime scenario figure, the domain-model class and state diagrams, business-process per-actor sequences and the use-case overview.
3. **Mermaid** is used only for diagrams that are neither C4 nor UML: flowcharts, mind maps, timelines, Gantt charts. The business-process §0 master flow stays a Mermaid flowchart.
4. **ADR-0004's §6 figure rule is superseded.** Its ownership decision stands: `arch-arc42` owns §6 prose and mints `SCN-NN`; the figure is pulled through the declared-dependency block, now always from `arch-uml sequence`.

### Positive Consequences

- The tool follows from the diagram kind; no boundary judgement remains.
- The routing sits in the descriptions of `arch-c4`, `arch-uml` and `arch-plantuml` and in the path-scoped Mermaid rule.

### Negative Consequences

- `domain-model`, `business-process` and `spec-use-case` now depend on the architecture plugin and on Docker for `arch-plantuml init`.
- UML diagrams no longer render inline on GitHub; they are committed SVGs.
- A project holding Structurizr dynamic views must redraw each as an `arch-uml sequence` titled with the same `SCN-NN` and delete the `dynamic` block.
