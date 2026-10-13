---
type: rule
---

# Heavy test runs on this WSL machine

The VM has about 10 GB, shared by every dev stack, Docker container and running suite. Before a full suite or aggregate gate, look for a concurrent run (`ps -eo pid,etime,args | grep "[p]ytest-xdist running"`) and check `free -m`; wait on its PID with `kill -0`, never with `pgrep -f` or `pkill -f`, which match your own shell. Cap workers with `PYTEST_XDIST_AUTO_NUM_WORKERS=3` (pytest-xdist 3+), or `-n 3` when invoking pytest directly. Log `free -m` every 30 s next to the run log, stop if `available` drops under about 600 MB, and end the log with `EXIT=<code>`. Subagents get the same cap and check, and leave the aggregate gate to the orchestrator. No dependency installs or branch switches under a running suite. Put multi-step background runs in a script file.

Hundreds of setup errors with `connection refused` on one port mean a Testcontainers database died, not a code regression: count with `grep -oE "port [0-9]+ failed" <log> | sort | uniq -c`, check `docker events --filter event=die --filter event=oom`, and re-run the test step before debugging.
