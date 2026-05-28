---
name: arch-c4
description: "Author and refresh C4 diagrams via the Structurizr DSL, producing arc42 §3 (Context), §5 (Building Blocks), §6 (Runtime View), and §7 (Deployment) markdown with embedded SVGs. Five modes: context (Level 1 — system + actors + external systems), container (Level 2 — internal containers + tech stack), component (Level 3 — one drill per CON-NN, derives from BC-NN.AGG-NN domain aggregates), deployment (per-environment nodes + container instances), runtime (dynamic view — key runtime scenarios as sequenced container interactions, mints SCN-NN). Mints SYS-NN / CON-NN / CMP-NN / DN-NN / SCN-NN. Edits docs/architecture/c4/workspace.dsl (foundation managed by arch-structurizr); writes arc42 markdown under docs/architecture/arc42/. Enforces boundary discipline: BBV components reference domain aggregates via properties.implements; BBV is the STATIC technical decomposition, NOT a re-statement of the domain model. Triggers on: C4 diagram, C4 context, system context, container diagram, component diagram, deployment view, runtime view, runtime scenario, sequence diagram, arc42 §3, arc42 §5, arc42 §6, arc42 §7, building block view, render C4, architecture diagram, draw architecture, c4 model, dynamic view."
version: "1.0.0"
status: active
last_reviewed: 2026-05-28
review_interval: 365d
supersedes: ~
superseded_by: ~
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "architecture"
  complexity: "high"
---

# C4 model authoring → arc42 §3 / §5 / §7

Single skill, four modes — each owns one arc42 architecture section and the corresponding C4 abstraction level. The Structurizr DSL workspace (`docs/architecture/c4/workspace.dsl`) is the single source of truth; this skill edits it, renders SVGs via `render.sh`, and writes the arc42 markdown that embeds them.

> "The C4 model is a hierarchical way to think about the static structures of a software system in terms of containers, components, and code." — Simon Brown, [c4model.com](https://c4model.com)

**Prerequisite:** `arch-structurizr init` must have run. If `docs/architecture/c4/workspace.dsl` doesn't exist, this skill aborts and points the user there.

---

## What this skill is NOT

- **Not a substitute for `domain-model`.** The Building Block View is technical decomposition (containers, components, modules — Spring Boot apps, Postgres databases, Kafka topics). It is **not** a re-statement of the domain model. See `references/boundary-discipline.md` for the three tests that keep them separate.
- **Not a substitute for `domain-model` state machines.** Runtime scenarios show how containers exchange messages to fulfil a use case. They are NOT per-aggregate lifecycle diagrams (those live in `docs/domain/07b-models/`). See `references/boundary-discipline.md` for the dynamic/behavioral boundary.
- **Not a one-off renderer.** Every edit goes through `workspace.dsl` so the model stays consistent across views. Direct SVG hand-editing is forbidden — `arch-structurizr verify` will flag drift.

---

## The four modes

Each mode (a) edits `workspace.dsl`, (b) runs `render.sh` to produce one or more SVGs, (c) writes/updates one arc42 markdown file embedding those SVGs.

| Mode | arc42 § | C4 level | DSL view type | View key pattern | Markdown file |
|---|---|---|---|---|---|
| `context` | §3 | Level 1 — System Context | `systemContext` | `systemContext` | `docs/architecture/arc42/03-context.md` |
| `container` | §5.1 | Level 2 — Container | `container` | `containers` | `docs/architecture/arc42/05-building-blocks.md` (§5.1) |
| `component` | §5.2 / §5.3 | Level 3 — Component | `component` | `components-<CON-NN>` | `docs/architecture/arc42/05-building-blocks.md` (one §5.2.x per drilled container) |
| `deployment` | §7 | Deployment | `deployment` | `deployment-<env-slug>` | `docs/architecture/arc42/07-deployment.md` (one §7.x per environment) |
| `runtime` | §6 | Dynamic (runtime) | `dynamic` | `runtime-<SCN-NN>-<slug>` | `docs/architecture/arc42/06-runtime-view.md` (one §6.x per scenario) |

---

## Mode 1 — `context` (arc42 §3, C4 Level 1)

System context: the system being documented + all communication partners (people + external systems). Black-box treatment — internals not shown.

### Pre-flight

1. `docs/architecture/c4/workspace.dsl` exists (else point to `arch-structurizr`).
2. Read `docs/business/01a-personas.md` if present — every Tier-1 persona is a candidate actor. Carry forward `P-NN` IDs.
3. Read `docs/domain/02b-bounded-contexts.md` if present — external systems may correspond to integrations with neighbouring BCs marked `Generic` (commodity, often external SaaS).
4. Read `docs/architecture/interfaces/*.md` if present — externally-facing service contracts indicate which neighbouring systems consume the API.

### Step 0 — Context questions (ask verbatim; user responds with letter codes, e.g. "1A, 2B")

```
1. What is the primary software system this context view documents?
   A. [name a specific system — e.g. "Claims Platform"]
   B. There are multiple in scope — list them and I'll pick one
   C. Re-read VISION.md and propose

2. Source for actor identification?
   A. Personas (business-persona) — all Tier-1 personas become P-NN actors
   B. Process docs (business-process) — extract actors from §Actors
   C. Discovery — describe the actors interactively

3. Source for external systems?
   A. Bounded contexts marked Generic in the BC map
   B. Service contracts (arch-service-contract) — external dependencies listed there
   C. Discovery — describe the external systems interactively
   D. None — the system is standalone

4. Diagram orientation preference?
   A. lr (left-to-right — default for context diagrams)
   B. tb (top-to-bottom — works for 8+ actors)
```

### Fill process

1. Assign the next `SYS-NN` ID to the primary system (or reuse if it exists in the DSL).
2. For each actor: assign `P-NN` (reuse from personas if matched) and add a `person` element with `tags "internal"` or `"external"`.
3. For each external system: assign `SYS-NN` and add a `softwareSystem` with `tags "external"`.
4. Add relationships: typically actor → primary system, primary system ↔ external system. One direction per relationship (Structurizr renders bidirectional as two arrows).
5. Add or update the `systemContext SYS_NN "systemContext"` view block.
6. Run `./docs/architecture/c4/render.sh systemContext` — confirm `views/systemContext.svg` is produced.
7. Generate `docs/architecture/arc42/03-context.md` from `templates/arc42-03-context.md` — embed the rendered SVG; fill §3.1 Business Context table (one row per communication partner) and §3.2 Technical Context table (channels + protocols).
8. Run discipline checks (see `references/c4-model.md` §Quality checks).

---

## Mode 2 — `container` (arc42 §5.1, C4 Level 2)

Zoom inside the primary system: show its containers (deployable runtime units — apps, services, databases, message brokers) and their relationships.

### Pre-flight

1. `arch-structurizr init` has run; `workspace.dsl` exists.
2. Context view exists (`SYS-NN` is in the DSL).
3. Read `docs/domain/02b-bounded-contexts.md` — each BC is a candidate cluster of containers. Microservices typically map 1 BC → 1+ containers; modular monoliths map N BCs → 1 container.
4. Read `docs/product-specs/07a-fbs.md` — `C-N.M.FXX` functionalities hint at which containers exist.

### Step 0 — Context questions

```
1. Container topology?
   A. Microservices — one service per BC
   B. Modular monolith — single deployable, modules per BC
   C. Layered monolith — frontend + backend + DB (BC boundaries are logical, not physical)
   D. Hybrid — I'll describe

2. Database strategy?
   A. One database per service (microservices default)
   B. Shared database (monolith default)
   C. CQRS — separate write + read stores

3. Asynchronous messaging?
   A. Yes, event bus (Kafka / NATS / RabbitMQ / SQS) — add as a queue container
   B. No, synchronous only
   C. Mixed — sync APIs + selected events
```

### Fill process

1. For each container: assign `CON-NN`, choose appropriate tag (`web`, `mobile`, `database`, `queue`, none for plain services), assign technology label (e.g. `"Node.js 20 + Fastify"`, `"PostgreSQL 16"`, `"Kafka 3.7"`).
2. Add containers as nested elements inside `SYS_NN { ... }`.
3. Add inter-container relationships with technology labels (`"HTTPS/JSON"`, `"SQL/TCP"`, `"Kafka protocol"`, etc.).
4. Add or update the `container SYS_NN "containers"` view block.
5. Run `./render.sh containers`.
6. Write/append §5.1 in `docs/architecture/arc42/05-building-blocks.md` — embed `containers.svg`; fill the containers table including the **`Domain aggregates implemented`** column. If a container implements no aggregate (e.g. an event bus), leave the cell empty. The column is mandatory — see `references/boundary-discipline.md`.

---

## Mode 3 — `component` (arc42 §5.2 / §5.3, C4 Level 3)

Drill into **one container** at a time. Each invocation produces a §5.2.x subsection. Stop drilling when the component-level diagram stops being useful (per arc42: "prefer relevance over completeness — leave out normal, simple, boring or standardised parts").

### Pre-flight

1. Container `CON-NN` to drill is supplied.
2. `domain-model` for the BC implementing this container exists at `docs/domain/07b-models/{bc-slug}.md` — components carry `properties.implements` pointing at `BC-NN.AGG-NN` IDs. Abort if missing; recommend running `domain-model` first.

### Step 0 — Context questions

```
1. Which container should I drill into?
   A. [name CON-NN, e.g. "CON-02 Claims API"]
   B. List the containers and let me pick

2. Component discovery basis?
   A. Domain aggregates (BC-NN.AGG-NN) — one component per aggregate's command-handler + query-handler + repository (recommended for Hexagonal / Clean / DDD)
   B. Tech-layer (controller / service / repository) — classic 3-layer split
   C. Existing code — reverse-engineer from src/ structure

3. Component granularity?
   A. Aggregate-level (5–12 components per container — recommended)
   B. Per-endpoint (one component per route — only for small/simple APIs)
   C. Functional cohesion — group by feature
```

### Fill process

1. For each component inside `CON_NN { ... }`: assign `CMP-NN`, give it a technology label, set `properties.implements` to the `BC-NN.AGG-NN` (or several, comma-separated) the component implements.
2. Add intra-container component relationships.
3. Add a `component CON_NN "components-CON-<NN>"` view block.
4. Run `./render.sh components-CON-<NN>`.
5. Append a §5.2.x subsection to `docs/architecture/arc42/05-building-blocks.md` — embed `components-CON-<NN>.svg`; fill the components table including `Domain aggregates implemented` (extracted from `properties.implements`) and optional `Code path` (extracted from `properties.code-path` if set).

---

## Mode 4 — `deployment` (arc42 §7)

Map containers onto infrastructure for one or more environments (dev / staging / production). One deployment view per environment.

### Pre-flight

1. Container view exists (at least one `CON-NN` defined).
2. Read `docs/architecture/decisions/*.md` — infrastructure ADRs (hosting choice, runtime platform, database provisioning, region/zone strategy) are prerequisites. Warn loudly if none exist; let the user proceed only if they confirm.

### Step 0 — Context questions

```
1. Environments to document?
   A. Production only (recommended starting point)
   B. Production + Staging
   C. Production + Staging + Development
   D. Custom list

2. Cloud / infra style?
   A. Single-cloud Kubernetes (e.g. EKS / GKE / AKS)
   B. Serverless (e.g. AWS Lambda + RDS + SQS)
   C. PaaS (e.g. Fly.io / Render / Heroku)
   D. Self-hosted VMs / on-prem
   E. Hybrid — I'll describe

3. Region / zone strategy?
   A. Single region, single AZ
   B. Single region, multi-AZ
   C. Multi-region active-passive
   D. Multi-region active-active
```

### Fill process

1. For each environment: add a `deploymentEnvironment "<Name>" { ... }` block.
2. Inside, build a tree of `deploymentNode` elements (region → AZ → cluster → namespace → pod, or region → service → instance — whatever matches the infra style). Assign `DN-NN` to nodes worth surfacing in the arc42 markdown.
3. Use `containerInstance CON_NN` to place container instances inside their deployment nodes. Reuse the container DSL identifier.
4. Add a `deployment SYS_NN "<Environment>" "deployment-<env-slug>"` view block per environment.
5. Run `./render.sh deployment-<env-slug>`.
6. Write/append §7.x in `docs/architecture/arc42/07-deployment.md` — embed `deployment-<env-slug>.svg`; fill the per-environment table (Motivation, Quality/Performance features, Mapping of building blocks to infrastructure).

---

## Mode 5 — `runtime` (arc42 §6)

Key runtime scenarios showing how containers (and optionally external systems) collaborate over time to fulfil an important use case. Uses Structurizr **dynamic views** — the same DSL elements, but ordered as a sequence with step numbers.

### Pre-flight

1. Container view exists (`CON-NN` identifiers are in the DSL). Runtime views reference those identifiers — containers must be defined first.
2. Read `docs/business/04-value-streams.md` if present — value stream stages and pain points indicate which scenarios matter most.
3. Read `docs/domain/07b-models/{bc-slug}.md` if present — commands and events in the domain model map to messages in the runtime scenario.

### Step 0 — Context questions

```
1. Which use case / user story does this scenario illustrate?
   A. Happy path for a core capability (recommended first scenario)
   B. Error / fallback path for an existing happy-path scenario
   C. A cross-cutting concern (auth, audit, notification) that touches many containers
   D. Describe — I'll name the scenario

2. Level of detail?
   A. Container-to-container (Level 2) — recommended default
   B. Component-to-component (Level 3) — only if CON-NN has been drilled via `component` mode

3. Participants?
   A. Auto-detect from the domain model commands/events for the relevant BC
   B. I'll list the participants explicitly
```

### Fill process

1. Assign the next `SCN-NN` ID to the scenario; choose a slug (e.g. `scn-01-claim-submission`).
2. Inside the DSL `dynamic` block, list elements and relationships in step order: `<source> -> <target> "<message>" { properties { "step" "1" } }`.
3. Add or update a `dynamic SYS_NN "runtime-<SCN-NN>-<slug>"` view block.
4. Run `./docs/architecture/c4/render.sh runtime-<SCN-NN>-<slug>` — confirm `views/runtime-<SCN-NN>-<slug>.svg` is produced.
5. Append a §6.x subsection to `docs/architecture/arc42/06-runtime-view.md` from `templates/arc42-06-runtime-view.md`:
   - Embed the rendered SVG.
   - Fill the step table (step number, sender, receiver, message, notes).
   - Annotate any error flows inline or as a sub-subsection.

### Boundary rules — runtime vs domain-model

| This view | Domain model (`docs/domain/07b-models/`) |
|---|---|
| Shows HOW containers communicate to deliver a use case | Shows WHAT aggregates do internally (state transitions, invariants) |
| Messages are wire-level (HTTP, Kafka events, gRPC calls) | Messages are domain commands and events |
| Participants are `CON-NN` containers (or `CMP-NN` for Level 3) | Participants are `BC-NN.AGG-NN` aggregates |
| Timeline is the call chain across deployment units | Timeline is the aggregate's own lifecycle |
| **Do NOT** show intra-aggregate state transitions here | **Do NOT** show inter-container call chains there |

---

## DSL editing rules (apply to all five modes)

1. **Forward references are forbidden** — declare every identifier before any relationship that uses it. The `validate` step in `render.sh` catches violations but the skill avoids creating them in the first place.
2. **Identifier convention** — kit IDs (`SYS-NN`, `CON-NN`, `CMP-NN`, `DN-NN`, `P-NN`) use hyphens in display names; DSL identifiers use underscores (`SYS_NN`, `CON_NN`, …). See `arch-structurizr/references/dsl-conventions.md`.
3. **One element per line** — even if the DSL accepts collapsed forms, write one element per line so the kit's audit can grep it.
4. **`properties.implements` is mandatory on every component** — the cross-reference to `domain-model` aggregates. Use `"BC-NN.AGG-NN"` (or a comma-separated list) for domain components; use the sentinel `"none"` for tech-only components (HTTP framework wrappers, generic middleware, observability hooks). Empty string `""` is **not** valid — Structurizr DSL rejects empty property values. Any component missing the `implements` property fails the boundary discipline check.
5. **Tag policy** — apply kit-standard tags only (see `arch-structurizr/references/structurizr-cheatsheet.md` §Tag conventions). Don't invent new tags without updating the styling block.

---

## Closing report (every mode)

- Mode executed (context / container / component / deployment)
- DSL edits made (number of elements added; new IDs assigned with their kit ID)
- Views rendered (list of `<view-key>.svg` files produced)
- arc42 markdown written / appended (file + section heading)
- Boundary checks: each component's `implements` field validated against `domain-model`; flag any orphan
- Next step suggestion: typically the next mode in the order context → container → component → deployment, or `arch-runtime-view` once enough containers exist

---

## Reference materials

- `references/c4-model.md` — Simon Brown's C4 abstractions; Level 1/2/3/4; when to stop drilling; quality checks
- `references/arc42-mapping.md` — exact mapping table from C4 levels to arc42 sections; what each arc42 section requires that C4 doesn't natively cover (e.g. arc42 §3.2 Technical Context — channels + protocols, which C4 doesn't model directly)
- `references/arc42-section-03.md` — arc42 §3 specification (embedded from arc42 v9.0 template; required reading before `context` mode)
- `references/arc42-section-05.md` — arc42 §5 specification (embedded); §5.1 / §5.2 / §5.3 structure rules
- `references/arc42-section-06.md` — arc42 §6 specification (embedded); runtime view purpose, content, and quality criteria
- `references/arc42-section-07.md` — arc42 §7 specification (embedded)
- `references/dsl-recipes.md` — copy-paste DSL fragments per mode
- `references/view-styling.md` — tag-driven styling cookbook; `-mode dark` rendering note
- `references/boundary-discipline.md` — the three tests separating BBV from `domain-model` and runtime view

## Templates

- `templates/arc42-03-context.md` — §3 markdown skeleton (Business Context + Technical Context tables; SVG embed)
- `templates/arc42-05-building-blocks.md` — §5 markdown skeleton (Level 1 whitebox + Level 2 black-box template; first-time generation only)
- `templates/arc42-06-runtime-view.md` — §6 markdown skeleton (one §6.x per scenario; SVG embed + step table)
- `templates/arc42-07-deployment.md` — §7 markdown skeleton (one §7.x per environment)

---

## Checklist (per mode)

- [ ] `docs/architecture/c4/workspace.dsl` exists (else `arch-structurizr init` first)
- [ ] DSL is valid (`render.sh --dry-run` passes)
- [ ] All new IDs assigned monotonically, never reused
- [ ] `properties.implements` set on every new `CMP-NN` (or explicitly empty with rationale)
- [ ] View key follows the canonical pattern (see modes table above)
- [ ] SVG rendered and committed under `docs/architecture/c4/views/`
- [ ] arc42 markdown file exists at canonical path and has standard frontmatter (see `rules/artefact-frontmatter.md`)
- [ ] Every container/component row in arc42 §5 carries the `Domain aggregates implemented` field
- [ ] (`runtime` mode) Every step in the `dynamic` view block has a step-number annotation; no orphan relationships
- [ ] (`runtime` mode) Step table in §6.x matches the DSL step count exactly
- [ ] Closing report delivered
