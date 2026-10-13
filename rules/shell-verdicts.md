---
type: rule
---

# Shell output can lie about success

`$?` after a pipe is the last command's status; use `${PIPESTATUS[0]}`. Never conclude that a list is complete or all green from output piped through `tail` or `head`.

**Never wait on a job with `pgrep -f`** (in Claude Code the tripwire hook blocks it in a wait loop): record the exit code at launch and wait on the log's `EXIT=` line or on a PID with `kill -0`; `pkill -f` can kill its own shell the same way. Tell: a job "running" far too long while its log stops changing. Use `ps -C <exe>` or `pgrep -x` to inspect the process table.
