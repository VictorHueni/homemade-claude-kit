---
type: rule
paths:
  - "**/*.sql"
  - "**/alembic/**"
  - "**/migrations/**"
  - "**/db/schema/**"
  - "**/repositories/**"
---

# PostgreSQL schema and query gotchas

**A nullable column in a UNIQUE constraint is dormant until something writes it.** NULLs are distinct by default (unless the constraint is `NULLS NOT DISTINCT`), so a path that leaves the column NULL is never constrained; starting to write a value arms the constraint with no DDL in the diff. Before writing into such a column, list every unique constraint or index naming it and ask what else is constant across the rows that path writes. Then trace the real entry points for an upstream dedupe before designing a remedy for the collision. A design that says "reuse nullable column X" has not done this check: do it, and record the result in the decision or plan.

**An aggregate over a nullable column turns "not measured" into 0.** `count(*) FILTER (WHERE col)` and `sum(CASE…)` read an all-NULL column as a genuine zero. When a column becomes nullable or stops arriving, find every aggregate reading it; guard with `CASE WHEN count(col) = 0 THEN NULL ELSE … END` and say in the object comment which value means "not measured". Tell: a counter that drops to exactly 0 from one period on while its neighbours stay healthy; check with `count(*) FILTER (WHERE col IS TRUE / IS FALSE / IS NULL)` grouped by period, against the whole series.

**`jsonb_path_query(doc, '$.**.key')` over-counts.** Lax mode reaches some nodes twice. Use `$.**` to find, never to count; count with a single-visit traversal and prefer the writer's own reported number.

**`IS NOT NULL` counts JSON nulls as present.** A JSON `null` is a jsonb value, not SQL NULL. Group readbacks by `jsonb_typeof(q)` (or test `q = 'null'::jsonb`), with strict-mode paths; a readback that matches the expected total with zero nulls is unverified.

**An equijoin on a nullable key drops rows silently** (`NULL = NULL` is not true; GROUP BY and PARTITION BY are fine). If a key leg can be NULL at that grain, join on a `row_number()` surrogate from the producing CTE, not on `COALESCE` sentinels.

**One unguarded clause turns a boolean OR-chain NULL.** Lead every predicate over a nullable column with an explicit `IS NULL` / `IS NOT NULL` guard; in review, look for the one clause unlike its siblings.

**A view that is fast alone can hang once composed.** The planner inlines its CTEs and misestimates the join. Reference analytical views as `WITH x AS MATERIALIZED (SELECT * FROM the_view)` (PG12+), wrap the other side the same way if it is also a multi-join subtree, and `EXPLAIN` (without `ANALYZE`) the composed query. Cancelling the client does not stop the server: find the PID in `pg_stat_activity` and `pg_terminate_backend()` it.

**SQLAlchemy binds Python `None` on a JSON/JSONB column as JSON `null`** (`none_as_null=False`). Use `sa.null()` for SQL NULL; when a jsonb branch test misbehaves, grep the fixtures for `=None` on JSONB columns. Guard `jsonb_array_elements(x)` with `jsonb_typeof(x) = 'array'` unless a constraint enforces the shape.
