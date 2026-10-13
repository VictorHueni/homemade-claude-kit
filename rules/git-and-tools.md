---
type: rule
---

# Git and tool discipline

**Never `git commit --amend`** unless asked in the same conversation; always make a new commit. A failed pre-commit hook means no commit happened: fix, re-stage, commit again.

**Commit and PR-title scope names a capability, not a work item.** Use the plan's declared `Commit scope:` if any, else a product or capability slug from the project's capability map, else the area or module (`auth`, `api`, `deps`). Never a bare plan or ticket number (`feat(0121): …`); put it in a `Refs:` trailer. A squash merge uses the PR title as the commit subject, so the PR title follows the same rule.

**Branch names say what the change does:** `<type>/<explicit-slug>`, such as `fix/osv-scanner-gitignored-worktrees`. Never name a branch only after a plan, increment or milestone number (`feat/0121-inc03`, `m02-merge`); a number may follow the descriptive slug, never replace it.

**Set `branch.autoSetupMerge = simple`** (Git 2.37+). Otherwise a branch cut from `origin/<other>` tracks it: a bare `git pull` merges that branch in, `git status` counts against it and `@{u}` answers a different question. A bare push to a mismatched upstream is refused under `push.default = simple`; check claims about push behaviour with `git push --dry-run`.

**`Edit` with `replace_all` matches the whole `old_string`.** Occurrences of the inner text with different surroundings survive. Prefer a narrow `old_string`, and after any wide replace `git grep` the inner string and fix the rest one by one.

**LSP `findReferences` on a cold server returns a partial answer.** Confirm the server exists (`command -v <server>`), then compare its file count with `git grep -lw <identifier> | wc -l`; if they differ, query once from a module that imports the symbol, then repeat. There is no rename operation, and no language server sees names inside strings (SQL, template keys, DI tokens): grep those and run the tests that execute them, since a missed string fails only at runtime.

**Never wait on a job with `pgrep -f <pattern>`:** the waiting shell matches its own pattern and the loop never ends. Wait on an artefact the job writes on completion (`echo "EXIT=$?" >> log`, then `until grep -q '^EXIT=' log`) or on a PID with `kill -0`; record the exit code at launch. To inspect the process table use `ps -C <exe>` or `pgrep -x`. Tell: a job "running" far too long while its log stops changing. `pkill -f` can kill its own shell the same way.

**Shell output can lie about success.** `$?` after a pipe is the last command's status; use `${PIPESTATUS[0]}`. Never conclude that a list is complete or all green from output piped through `tail` or `head`.

**An MCP tool error naming a parameter its schema never offered** means the server's schema and implementation drifted, possibly for that tool alone, so one working call proves nothing about the next. Stop adjusting the arguments; call the underlying REST API with the same credential and verify the effect through a read.
