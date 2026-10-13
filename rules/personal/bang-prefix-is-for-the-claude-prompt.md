---
type: rule
---

# A `! command` suggestion must say it goes in the Claude Code prompt, not the terminal

When I hand the owner a command to run as `! cd <repo> && make <target>`, the `!` is Claude Code's run-in-session prefix. Pasted into a plain zsh or bash prompt, `!` is the pipeline negation operator: `! cd <repo>` runs `cd`, inverts its (successful) exit status to failure, and the `&& make …` never executes. The shell prints nothing, the directory changes, and the owner reasonably reports "done". Measured 2026-09-23: a database migration the whole increment waited on was "run" this way and had not happened; the stack was still on the old revision.

**How to apply:** when suggesting a `!`-prefixed command, say in the same sentence that it is typed into the Claude Code prompt, and give the plain form (without `!`) for a terminal. After the owner reports it done, verify the effect (the migration level, the branch tip, the PR state) before building on it; "done" describes what they typed, not what happened.

**Why:** the failure is silent in both directions. The shell shows no error, and I have no view of the owner's terminal. The verification is one read-only query and saves a whole detour.
