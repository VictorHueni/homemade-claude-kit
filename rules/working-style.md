# Working style preferences

## Default to sequential, not parallel plan execution

When laying out a multi-plan initiative, recommend a single critical path (e.g. `01 → 01b → 02 → 03a → 03b → 04`) even when plans are architecturally parallelisable.

- Architectural dependency graphs should still show *what is parallelisable* for completeness.
- The *recommended execution order* collapses parallel plans onto one critical path.
- When asked "which plans can run in parallel?" — answer architecturally, but note the sequential preference.
- Only suggest parallel phases if I explicitly opt in.

**Why:** I want a single thread of state to reason about. Parallel execution lets subtle dependency violations manifest as silent regressions when two plans land in non-deterministic order.

## Trust but verify prior-context claims

Before acting on any "fix X that was identified earlier" instruction — tracker entry, memory file, prior-conversation analysis, plan increment referencing a past state — verify the premise against current code first.

One of:

- `git grep -n "<symbol>" <src-dir>/` to verify production callers exist
- `Read` the cited file:line to verify the code matches the description
- `\d <table>` (psql) to verify schema state
- `git log --follow <file>` to see if the file was recently restructured

The verification costs < 1 minute; the cost of acting on a false premise is 15 min to several hours. Snapshots in time go stale silently — refactors and adjacent commits invalidate claims between writing and acting.

**Special case — workaround vs structural fix:** when a memory describes a *workaround* for a problem, ask whether the underlying problem still exists or was structurally fixed. Prefer routing structural issues to architectural fixes over papering over them.

**Anti-pattern in self:** finding myself drafting code to address an issue I have not yet verified is live. Stop, verify, then act — or discover the issue does not exist.

## Never hard-wrap markdown prose

Write markdown paragraphs, blockquotes, and list items as single long lines — no forced line breaks at ~80–90 characters.

**Why:** Hard-wrapped lines create noisy diffs, look like broken sentences when rendered, and get re-wrapped by editors anyway. Let the editor handle visual soft-wrapping; the file should have one line per logical paragraph.

**How to apply:** Applies to every markdown file — docs, reports, skill outputs, research notes. Tables and fenced code blocks are unaffected (they have their own line structure).
