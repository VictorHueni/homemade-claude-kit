# MADR 4.x Templates

Use these templates as the default ADR structure.
Source: <https://adr.github.io/madr/> and <https://github.com/adr/madr>.

## Full Template

```markdown
# <short title>

## Context and Problem Statement

<describe context and the concrete problem>

## Decision Drivers

- <driver 1>
- <driver 2>
- <driver 3>

## Considered Options

- <option 1>
- <option 2>
- <option 3>

## Decision Outcome

Chosen option: "<option x>", because <summarize why this option is best against the drivers>.

### Positive Consequences

- <benefit 1>
- <benefit 2>

### Negative Consequences

- <trade-off 1>
- <trade-off 2>

## Pros and Cons of the Options

### <option 1>

<short summary>

#### Positive

- <pro 1>
- <pro 2>

#### Negative

- <con 1>
- <con 2>

### <option 2>

<short summary>

#### Positive

- <pro 1>
- <pro 2>

#### Negative

- <con 1>
- <con 2>

### <option 3>

<short summary>

#### Positive

- <pro 1>
- <pro 2>

#### Negative

- <con 1>
- <con 2>
```

## Minimal Template

```markdown
# <short title>

## Context and Problem Statement

<describe context and problem>

## Decision Drivers

- <driver 1>
- <driver 2>

## Considered Options

- <option 1>
- <option 2>

## Decision Outcome

Chosen option: "<option x>", because <concise rationale>.

### Consequences

- Good: <benefit>
- Bad: <trade-off>
```

## Naming and Traceability Conventions

- Keep one decision per ADR.
- Prefer concrete titles that include the decision, not only the topic.
- Keep filenames stable and searchable.
- If superseding an old ADR, reference both ADR IDs explicitly.
