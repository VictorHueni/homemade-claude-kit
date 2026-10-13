---
type: rule
---

# `claude plugin eval`: two WSL blockers, and a `tool_used` grader that passes on denied calls

## On WSL the eval sandbox refuses to start, at no cost, for two machine reasons

A Bash-granting eval case (any `--allow-tools "Bash(...)"`) needs the sandbox to exclude credential helpers and stores. On this WSL machine it refused twice before any session started (`$0.00`, `0s`), each time with a different message:

- **`a PATH directory could not be examined for keychain credential helpers (EACCES)`**: caused by the Windows interop entries WSL appends to `PATH` (`/mnt/c/...`). A plain `ls` of each entry succeeds, so the culprit cannot be found by hand. Running with `PATH` stripped of every `/mnt/` entry fixed it.
- **`the Docker (~/.docker, DOCKER_CONFIG) credential store ... holds a symbolic link inside it`**: Docker Desktop for WSL makes `~/.docker/contexts` a link into the Windows profile. Setting `DOCKER_CONFIG` to an empty folder does **not** help: the runner inspects `~/.docker` too. What worked: run the eval with `HOME` set to a temporary directory holding only links `.claude -> ~/.claude` and `.claude.json -> ~/.claude.json`. `claude auth status` stays logged in from it, and the real Docker setup is untouched.

**How to apply:** bake both into the project's eval target (filtered `PATH`, temporary `HOME`) rather than editing `~/.docker` or the shell profile. Each refusal fails before any model call, so iterating on the environment is free; check the run's `$` and duration columns to confirm nothing was spent.

## A `tool_used` grader counts attempts, not successful runs

A grader of `type: tool_used` with `tool: Bash` and an `input_match` passes as soon as a matching Bash call is **attempted**, including one the permission mode denied. Measured case: the model chained `cp ... && cat > page.html <<EOF ... && python3 validate.py page.html`; the eval's permission mode denied the compound command, the validator never ran, and the "validator ran" grader still passed. The run scored 1.00 while the delivered page linked stylesheets that were never copied.

**How to apply:** never prove that a step happened with `tool_used`. Make the step leave an artefact (a `--record verdict.txt` option on the validator) and grade the artefact with a file grader. Also grade the deliverable for what a reviewer would see: a page that links missing local assets passes every colour check while rendering unstyled. After the first smoke run, read the kept trace (`--keep-temp`, then the sealed `home/` workspace and `out/trace.jsonl`) and compare each verdict with what actually happened before trusting any score.

**Sibling lesson for skills:** sessions in a restricted permission mode deny compound shell commands. A skill's workflow should say "one plain command per Bash call; write files with the Write tool", or its own steps get silently dropped.

**Why:** both traps report green. The environment blockers at least fail loudly; the grader one produces a perfect score for a run that skipped the step it was written to check.
