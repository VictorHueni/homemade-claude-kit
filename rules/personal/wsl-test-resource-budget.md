---
type: rule
---

# Heavy test runs on the WSL machine: budget memory, never assume you are alone

This machine's WSL VM has about 10 GB, shared by every worktree's dev stack, Docker Desktop's containers and any test suite another session is running. A full suite with `pytest -n auto` starts one worker per core (8 here), and each worker holds a few hundred MB plus its own Testcontainers database. Two such suites at once, or one beside several dev stacks, is enough to exhaust the VM. Stated preference (2026-10-07): run local CI gates in the background, but watch the WSL resources.

**How to apply, before starting any full suite or aggregate CI gate:**

1. **Look for a concurrent run first.** `ps -eo pid,etime,args | grep "pytest-xdist running" | grep -v grep` and `free -m` (column "available"). If another worktree's suite is running, wait for it by its PID (`while kill -0 <pid>; do sleep 10; done`), not by a `pgrep -f` pattern, which matches the waiting shell itself.
2. **Cap the workers without editing the recipe.** `PYTEST_XDIST_AUTO_NUM_WORKERS=3` makes `-n auto` resolve to 3 (pytest-xdist ≥ 3). Prefix the make target with it; at most `-n 3` for explicit invocations. With 3 workers a full integration suite kept at least 2 GB free here.
3. **Watch memory while it runs.** Have the background runner append `free -m` every 30 s to a log next to the run's own log, and alert below about 600 MB available. Finish the run log with an `EXIT=<code>` sentinel so the verdict is read, not inferred.
4. **Subagents get the same budget in their brief:** at most 3 workers, check for a concurrent suite first, and leave the aggregate gate to the orchestrator so two never overlap.
5. **Don't change the environment under a running suite.** Dependency installs (`uv sync`, lockfile regeneration) and branch switches wait until the suite has finished.

**Reading a failed run:** hundreds of setup errors that all say `connection refused` on a **single** port mean one Testcontainers database died mid-run, not that the code broke. Check with `grep -oE "port [0-9]+ failed" <log> | sort | uniq -c`, look at `docker events --filter event=die --filter event=oom` for the window, then re-run only the test step before debugging anything.

**Shell traps met while doing this:**
- `a && b && ( loop ) & S=$!; cd dir && cmd` backgrounds the whole `a && b && (loop)` list, so later steps run in the wrong directory. Put multi-step background runs in a small script file instead.
- `pkill -f <pattern>` kills the shell running it when the pattern appears in its own command line. Kill by PID.

**Why:** the failure is either a frozen VM (all sessions lost) or a red gate that looks like a code regression. Both cost far more than one `ps` and one environment variable.
