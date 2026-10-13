---
type: rule
paths:
  - "**/*.sql"
  - "**/alembic/**"
  - "**/migrations/**"
  - "**/db/schema/**"
  - "**/repositories/**"
---

# PostgreSQL schema gotchas

## A nullable column inside a UNIQUE constraint is a *dormant* constraint — backfilling it arms one

PostgreSQL treats NULLs as **distinct** in a unique constraint (the default; `NULLS NOT DISTINCT` is opt-in and rare). So a multi-column unique constraint containing a column that some write path always leaves NULL **does not constrain that path at all** — any number of rows can share every other leg. The constraint is real, indexed, and enforced for the paths that populate the column, and simultaneously inert for the paths that don't.

The trap is that starting to write a real value into that column **arms a constraint that has never once fired on this code path**, silently converting a previously-tolerable duplicate into a hard `UniqueViolation` at runtime. Nothing in the change looks schema-shaped: no DDL, no migration, no `alembic check` diff — it can be a single new keyword argument on a repository function.

**How to apply:** before writing a value into any column that a code path currently leaves NULL, grep the schema for every `UniqueConstraint` / `Index(unique=True)` that names it, and for each one ask *what else is constant across the rows this path writes?* If the remaining legs are shared (a batch that reuses one parent id across members, a loop under one transaction, a job row per request), you may have introduced a collision the old NULLs were hiding.

**Then do the second half, which is where I got it wrong: prove the duplicate-producing input is actually reachable through the real entry points.** Trace the input from the outermost caller inward and look for an upstream normalisation — a parser that already deduplicates, a set-typed intermediate, a guard clause — that makes the collision unconstructible in practice. Do this *before* designing remediation around it.

Measured case, including the correction: a per-request job row carried a nullable hash column inside `UNIQUE (parent_run_id, version_id, hash, call_type, seq)`. Every row that path wrote had `hash = NULL`, so the constraint was dormant, and persisting a real content digest — pure signature change, zero DDL — would arm it. I identified the collision as "the same id listed twice in one batch file" and wrote a prerequisite dedupe step into the plan to prevent it. **Review found the batch-file parser already deduplicated, three call-frames upstream** — so the dedupe was a no-op, the test written to prove it was unconstructible, and the step ordering it justified was a false dependency. The constraint really does arm; the *reachable* collision was a different, much narrower path (an operator explicitly reusing a run identifier across two otherwise-identical submissions).

**Why the second half matters as much as the first:** an unreachable collision written into a plan costs more than the bug would have. It adds a step that does nothing, a test that cannot be written, and a dependency between increments that constrains ordering for no reason — all defended by a confident-sounding mechanism. **Anti-pattern in self:** identifying a genuine schema hazard, reaching for the first plausible way to trigger it, and building remediation on that guess without tracing whether the input can actually arrive in that shape.

**Why:** the reasoning that misleads is "the column already exists and is nullable, so writing to it is free". Existence and nullability say nothing about participation in a key. The failure is invisible in review (no schema diff to notice), invisible to migration drift checks (nothing structural changed), and only reproduces when the *duplicate-producing input* happens to occur — so it ships green and fires later on real data. **Anti-pattern in self:** treating "reuse an existing unused column" as inherently cheaper than adding one, without reading the constraints that column participates in.

## Corollary: an architecture decision that says "reuse column X, it's NULL today" has not checked this

Design documents reach for a spare nullable column precisely *because* it is unused, and that framing ("it's NULL on every row this path writes") is one clause away from the danger without naming it. When implementing such a decision, treat the constraint audit as part of grounding the work, not as an implementation detail — and record the finding back into the decision or its plan, since the next reader inherits the same blind spot.

## An aggregate over a nullable column converts "unknown" into a stated zero

`count(*) FILTER (WHERE flag)` — and equally `count(*) FILTER (WHERE col = 'x')`, `sum(CASE WHEN … THEN 1 ELSE 0 END)`, and any `COUNT(col)` — treats NULL as *not matching*. So a column that is **entirely NULL** does not yield NULL, an error, or an empty result. It yields **`0`**, indistinguishable from a genuine, measured zero.

The failure is a category error, not an arithmetic one: the row-grain field is honestly blank, and the rollup republishes that blank as a fact. Downstream this is the *confidently wrong* tier — strictly worse than being down, because a dashboard reading "0 items in category X" looks authoritative and nobody investigates a healthy-looking zero.

**When it bites:** an upstream feed stops carrying a field, a source-format migration drops an extension, a nullable column is added and not yet backfilled, or a disposition explicitly *accepts* the loss of a field. That last one is the nastiest — the loss is signed off and documented at row grain (the API even types the field nullable), while the aggregate built on it silently keeps asserting a number. The signature is a counter that steps along plausibly for years and then reads exactly `0` from one period onward, while every neighbouring counter on the same row stays healthy.

**How to apply:** when a column becomes nullable — or when a feed change makes an existing column stop arriving — grep for every aggregate that reads it before deciding the change is contained at row grain. Where the counter should distinguish *none* from *not measured*, guard it so an all-NULL input yields NULL rather than 0 (e.g. `CASE WHEN count(col) = 0 THEN NULL ELSE count(*) FILTER (WHERE col) END`), and say in the object's comment which value means *not measured*. When auditing, compare against the *whole* prior series rather than the previous period only: a counter that collapses and stays collapsed is invisible to a "changed since last period" check after its first period, which is exactly how these survive.

**Discriminator, one query:** `count(*) FILTER (WHERE col IS TRUE) / IS FALSE / IS NULL` grouped by period. All-NULL on the latest period with real true/false splits earlier is a lost measurement; a genuine zero shows `IS FALSE` carrying the whole population. Do not settle for `count(*) FILTER (WHERE col)` — that is the very expression that cannot tell the two apart.

**Why:** every natural check agrees the pipeline is fine — the query runs, the type is right, no NULL surfaces anywhere, and the number is in range. The only signal is the *history*, and only if something is looking at it. **Anti-pattern in self:** treating a nullable-field disposition as contained once the row-grain contract is honest, without asking what aggregates were already built on the column.

## `jsonb_path_query(doc, '$.**.key')` over-counts — lax mode reaches the same node twice

`$.**` is a recursive descent, and JSON path runs in **lax mode by default**, which auto-unwraps arrays. The combination means one object can be reached by more than one path, so `count(*)` over `jsonb_path_query(doc, '$.**.some_key')` reports **more matches than there are keys in the document**. Measured case: a document tree with exactly 556 `some_key` keys reported 632.

The failure is the confidently-wrong kind — the query runs, the type is right, the number is in range and plausibly close, and it is used to confirm that a write landed. Nothing says "this counted some nodes twice".

**How to apply:** never use `$.**` to *count* anything. Use it to *find* (existence, a sample), and get the count from a traversal that visits each node once — the application's own walk over the fetched payload, or a `jsonb_path_query` with an explicit path rather than a recursive one. When cross-checking a write, prefer the writer's own reported number and confirm it with a single-visit traversal; a recursive-descent count that merely *exceeds* the expected figure is not evidence of extra data.

**Anti-pattern in self:** reading a higher-than-expected count as "the payload gained nodes in transit" instead of testing the counting mechanism first.

## `IS NOT NULL` on a `jsonb_path_query` result counts JSON nulls as present values

A JSON `null` inside a document is a **jsonb value** whose type is `null` — it is not SQL `NULL`. So every row `jsonb_path_query` emits for a key whose value is JSON null satisfies `IS NOT NULL`, and a query written as

```sql
count(*) FILTER (WHERE q IS NOT NULL)   -- counts JSON nulls too
```

reports the *total* number of keys found, while the companion `count(*) FILTER (WHERE q IS NULL)` reports **0** for a document set that genuinely contains missing values. Measured case: a write of 182 evidence nodes, 181 with a value and 1 deliberately null, read back as "182 present / 0 null" — the one absent value was invisible, and the number looked like a clean full-coverage result.

The failure is the confidently-wrong tier again: the query runs, the count is in range, and it *agrees with the expected total*, which is exactly what makes it persuasive. Only the row that should have been missing is gone.

**Discriminator, one column:** `jsonb_typeof(q)` — group by it. `string 181 / null 1` is the truth; `IS NOT NULL` cannot produce that split. `q = 'null'::jsonb` also isolates them, and `jsonb_path_query` in **strict** mode plus `jsonb_typeof` is the combination that answers both this and the lax-mode over-count above.

**How to apply:** when reading a nullable field back out of a jsonb column to verify a write, never predicate on `IS NOT NULL`. Group by `jsonb_typeof` and check the split against the writer's own reported figures. Treat a readback that exactly matches the expected *total* while reporting zero nulls as unverified rather than as confirmation — that is the signature of the trap, not of success.

## `NULL = NULL` never matches — an equijoin on a legitimately-NULL key silently drops rows

A `JOIN ... ON`/`USING` keyed on a column that can be NULL at the joined grain silently loses every row whose key leg is NULL: `NULL = NULL` is not true in SQL, so those rows fail to match with no error, and downstream derived columns read SQL NULL instead of their intended defaults. `GROUP BY`/`PARTITION BY` treat NULLs as equal and are safe on their own — **only joins bite**.

**How to apply:** before keying any join in a view/CTE chain, ask which key legs can legitimately be NULL at that grain (optional identifiers, rows of an older schema version, synthesized default rows). If any can, do not "fix" it with `COALESCE` sentinels — introduce a non-null surrogate key (`row_number() OVER ()`) in the producing CTE and join on that alone.

**Why it ships silently:** a real-data validation pass misses it whenever the live corpus happens to have no NULL-keyed rows on the exercised path — the defect only fires on the data shape that wasn't sampled. Measured case: an analytics view whose derived flags read NULL for exactly the rows keyed by a nullable identity leg; caught only by an edge-shaped test fixture asserting `IS FALSE` and getting `NULL`. **Anti-pattern in self:** trusting a natural-key tuple because it "identifies the row conceptually" without checking each leg's nullability at that grain.

## Three-valued logic poisons boolean OR-chains — one unguarded clause turns the whole flag NULL

`col IN (...) AND other IS NULL` evaluates to `NULL` (not `FALSE`) when `col IS NULL` (`NULL IN (...)` is `NULL`, `NULL AND TRUE` is `NULL`), and then `FALSE OR NULL = NULL` propagates through the whole chain — a completeness/validity flag built as an OR of predicates reads NULL instead of FALSE for exactly the rows where an input was absent.

**How to apply:** in any boolean expression aggregating predicates over nullable columns, lead every predicate with an explicit `IS NULL`/`IS NOT NULL` guard so each clause is provably two-valued before it enters the chain. When reviewing, look for the *one* clause that doesn't follow the pattern its siblings do — measured case: five guarded predicates and one unguarded, and only the unguarded one poisoned the flag.

## A view fast standalone is not evidence it stays fast composed — force `MATERIALIZED` on analytical-view references

Composing a plain (non-materialized) view that contains internal CTEs and window functions into a larger query's `FROM` clause lets the planner inline the view's whole CTE chain into the outer join tree. Cardinality estimates across that flattened boundary can be wrong by orders of magnitude — measured case: two halves fast in isolation (~6.5s / ~1.6s), the composed query estimated tens of billions of join rows and genuinely hung (killed after 10+ minutes). Client-side timeout/Ctrl-C does **not** stop the server-side query — find the PID in `pg_stat_activity` and `pg_terminate_backend()` it.

**How to apply:** when a composed query references such a view, wrap the reference as `WITH x AS MATERIALIZED (SELECT * FROM the_view)` (PG12+) so it computes once as an opaque relation with its true row count before joining. Symmetrically wrap the other side if it is also a multi-join subtree. Treat "each half is fast alone" as zero evidence about the composition; `EXPLAIN` (without `ANALYZE` — it may never return) the composed form before shipping.

## SQLAlchemy binds Python `None` on a JSON/JSONB column as JSON `null`, not SQL `NULL`

Write-path sibling of the jsonb-read traps above: `insert(...).values(json_col=None)` stores the **jsonb scalar `null`** (SQLAlchemy JSON types default `none_as_null=False`), so a later `WHERE json_col IS NULL` doesn't match the row and code branches keyed on SQL NULL silently take the wrong path. Use `sa.null()` where true SQL NULL is intended — most often in test fixtures doing direct inserts, where the wrong branch makes the test assert against an unintended state and the failure looks like application logic.

**How to apply:** in any direct INSERT/UPDATE touching a JSON/JSONB column, never pass bare `None` when SQL NULL is the intent; grep fixtures for `=None` on JSONB columns when a jsonb branch test behaves inexplicably. Also guard `jsonb_array_elements(x)` with `jsonb_typeof(x) = 'array'` unless the shape is constraint-enforced — it raises `cannot extract elements from a scalar` on malformed stored documents.
