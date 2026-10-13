---
type: rule
---

# Subagent orchestration (one-agent-per-increment mode)

When driving a Ralph-style plan from chat (no terminal — one subagent per increment, per the preference in `~/.claude/CLAUDE.md`):

## Iteration agents must run gates in the foreground

Instruct every iteration subagent explicitly: run long test gates (full suites, aggregate CI mirrors) in the **foreground** and never end the turn waiting on a backgrounded process. Subagents do not self-resume on their internal background-task notifications — a subagent that backgrounds a gate and stops to "wait for the notification" stalls the loop until the orchestrator pokes it awake with a resume message (and it may re-stall the same way; measured case: two pokes needed for one increment).

**How to apply:** put "foreground only; conclude every turn with a definitive state, never a wait" in the iteration brief. If a subagent does stall: verify its background process actually finished (`pgrep`), then resume it with firm instructions to read/re-derive the verdict and commit in the same turn.

## Orchestrator verifies between iterations

Trust-but-verify each iteration's closing report before spawning the next agent: commit exists at HEAD, tree clean, plan status fields advanced. The report can say "done" while the tree says otherwise (the stall pattern above leaves work uncommitted).

## Carry learnings forward in the briefs

Each iteration brief should point the agent at the plan's `progress.txt` AND inject the orchestrator's own accumulated corrections (stale plan prose vs shipped reality, environment traps). Fresh-context agents repeat any mistake not written down.

## Directory-partitioned audits: join dead-code leads across slices

When fanning an audit out by directory (one subagent per test/source slice), a "this src function has zero production callers" finding and the test file that is its sole consumer routinely land in **different** slices. Each auditor correctly reports its half and neither sizes the pair. Measured case (2026-09-04): three dead-src clusters (~500, ~120, ~350 test LOC) were invisible to every slice report and only surfaced when the orchestrator grepped each flagged symbol across the whole `tests/` tree.

**How to apply:** after all slices return, take every src symbol any slice flagged as dead, grep it across the entire test tree, and size the test files that exist only to exercise it. Re-run each dead-src grep yourself before consolidating (the cost is seconds; a wrong "dead" claim deletes a feature). Record the joined leads in the consolidated report, not just the per-slice ones.

## Run successive increments in the owner's checkout, not a fresh worktree each

Stated preference (2026-10-07): "make sure the next increments are done in this worktree and not on a new worktree each time". When driving a plan increment by increment, cut each increment's branch in the checkout the session works from (`git fetch origin && git switch -c <branch> origin/main`) and point the iteration subagent at that path. Create a separate worktree only when the owner asks, or when another increment's branch must stay checked out at the same time.

**How to apply:** before briefing a subagent, confirm the checkout's tree is clean and that its environment is complete for the increment (dependency extras, generated build artefacts, the gitignored `.env`). A fresh worktree misses all three, and the miss shows up late: an LLM test that skips for lack of credentials, or fails on a missing optional extra, after the owner has already started the paid run.

**Why:** a worktree per increment multiplies setup (venv, node modules, env file), leaves directories and branches to clean up after every merge, and has repeatedly cost a round-trip with the owner on environment gaps the main checkout did not have.
