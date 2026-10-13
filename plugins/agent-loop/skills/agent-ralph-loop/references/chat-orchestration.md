# Ralph Loop from chat — one subagent per increment

Use this when no terminal is available to run `ralph.sh` (mobile, remote, cloud): the chat session is the orchestrator and spawns one fresh subagent per increment, never several increments per subagent. Each subagent follows the Iteration Protocol in `SKILL.md`.

## Briefing each iteration agent

- Run the increment's test gate in the foreground and end every turn with a definitive state, never a wait on a background task: subagents do not resume on their own background notifications.
- Point the agent at `progress.txt` and paste the orchestrator's accumulated corrections (stale plan prose versus shipped reality, environment traps). A fresh-context agent repeats any mistake not written down.
- Restate the plan's test rules: write-first tests extend existing tests where they fit, red run then green, both recorded in `progress.txt`.
- Respect the machine's test budget (follow its test-budget rule if one is installed): cap workers and never overlap heavy runs. The aggregate gate (full suite, CI mirror) is the orchestrator's, run in the foreground between iterations, never the subagent's.

## Between iterations

Before spawning the next agent, check that the increment's commit is at HEAD, the tree is clean and the plan's status fields advanced; a closing report can say "done" while the tree says otherwise. If an agent stalled on a background run, confirm the process exited (`kill -0 <pid>` fails; take the PID from the agent's report or `ps -C <exe>`), then resume it with orders to re-derive the verdict and commit in the same turn.

## Where to work

Work in the checkout the session works from and point the subagent at that path. When increments ship as separate PRs, cut each increment's branch there from `origin/main` once the previous one has merged (`git fetch origin && git switch -c <type>/<slug> origin/main`); otherwise use the plan branch from Workspace Setup. Create a worktree only when the owner asks, or when another branch must stay checked out at the same time. First confirm the checkout is clean and complete for the increment: dependency extras, generated build artefacts, the gitignored `.env`.
