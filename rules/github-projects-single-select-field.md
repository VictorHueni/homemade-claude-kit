---
type: rule
---

# Adding one option to a GitHub Projects single-select field silently clears every item's value

## Passing the full option list protects the *options*, not the *item values*

`updateProjectV2Field` **replaces** a single-select field's whole `singleSelectOptions` array. The widely-known half of this trap is that omitting the existing options deletes them — so the standard advice is "read all options first, then send existing + new".

That advice is necessary and **not sufficient**. GitHub **regenerates every option id** on the mutation, including ids for options whose name, colour and description are byte-identical to before. Item values are stored by option *id*, so every item pointing at an old id is orphaned: the field reads back with a perfect option list while **every item's value is silently cleared**. No error, no warning, and the natural verification (re-read the options — all present, correctly named, correctly ordered) confirms success while the damage sits one level down, on the items.

Measured case: adding a 30th capability to a 29-option field cleared **155 item values across 214 project items**. The mutation returned 30 correctly-named options.

## The only safe procedure

1. **Snapshot every item before touching the field** — item id + the option *name* it currently holds (names survive; ids do not). This is the restore key, and it cannot be reconstructed afterwards.
2. Read all existing options (name, colour, description) and send the complete list plus the new one.
3. **Read the items back and expect the loss.** Map each snapshotted option *name* to its new option id and restore the values in batched mutations.
4. Verify by diffing a fresh full-board snapshot against the pre-mutation one: same item count, same value count, identical per-option distribution, zero mismatches.

**How to apply:** treat "add an option to a single-select field" as a destructive migration requiring a backup, never as an additive edit. If you cannot snapshot the items first, do not run the mutation — add the option through the web UI instead, which preserves values. Where a project has many items, budget for the restore step rather than treating it as contingency.

**Why:** every signal available after the mutation says it worked. The failure is invisible in the thing you changed and only visible in a thing you did not think to re-read — the same shape as the silent-failure family in `~/.claude/rules/sonarcloud-silent-analysis-failure.md`, where a truthful-looking signal reports on the wrong object. **Anti-pattern in self:** reasoning "I passed the complete option list, so nothing was lost" — that sentence is true about options and false about items, and the ambiguity in "nothing was lost" is exactly where the data goes.
