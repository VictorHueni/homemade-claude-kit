---
title: "{{project_name}} — Runtime View (arc42 §6)"
status: draft
owner: {{owner}}
last_reviewed: {{today}}
review_interval: 180d
---

# 6. Runtime View

> "The runtime view describes the concrete behavior and interactions of the system's building blocks in form of scenarios." — arc42 §6

Each scenario below shows how containers in {{project_name}} collaborate to fulfil a specific use case. For the static structure of those containers, see [§5 Building Block View](./05-building-blocks.md). For aggregate-internal state machines, see [`docs/domain/07b-models/`](../../domain/07b-models/).

---

<!-- One §6.x block per scenario. Append via `arch-c4 runtime` mode. -->

## 6.1 {{scenario_title}} (`SCN-01`)

**Motivation:** _TODO_ — one sentence explaining why this scenario is architecturally significant (e.g. "Shows the end-to-end claim submission flow, highlighting the async handoff to the insurer integration service").

**Participants:** _TODO_ — list `CON-NN` containers (and any `P-NN` actors or external `SYS-NN`) involved.

![{{scenario_slug}}](../c4/views/runtime-SCN-01-{{scenario_slug}}.svg)

### Step table

| Step | From | To | Message / action | Notes |
|---|---|---|---|---|
| 1 | _TODO_ | _TODO_ | _TODO_ | _TODO_ |

(One row per annotated step in the Structurizr dynamic view. Numbering must match the DSL `"step"` property values.)

### Error / alternative flows

_TODO_ — describe what happens when step N fails. Skip if error handling is trivial (caller receives HTTP 5xx, retries handled by client). Document when the error path involves a saga rollback, compensating transaction, dead-letter queue, or circuit breaker.

---

## Cross-references

| Linked artefact | Relationship |
|---|---|
| [`docs/architecture/arc42/05-building-blocks.md`](./05-building-blocks.md) | Static structure of the `CON-NN` containers appearing in scenarios |
| [`docs/domain/07b-models/`](../../domain/07b-models/) | Aggregate lifecycle state machines — do NOT duplicate here |
| [`docs/architecture/arc42/07-deployment.md`](./07-deployment.md) | Where the containers here actually run |
| [`docs/business/04-value-streams.md`](../../business/04-value-streams.md) | Value stream stages that motivated the scenario selection |
| [`docs/architecture/decisions/`](../decisions/) | ADRs governing async patterns, retry policies, saga patterns visible in scenarios |

## Open Items

| OI-ID | Type | Summary | Source anchor | Source heading | Resolution path | Priority | Status | Owner | Due / Review date | Tracker ref |
| :---- | :--- | :------ | :------------ | :------------- | :-------------- | :------- | :----- | :---- | :---------------- | :---------- |

_None at present._
