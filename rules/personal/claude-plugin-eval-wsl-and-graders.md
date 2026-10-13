---
type: rule
---

# `claude plugin eval`: WSL blockers and graders that pass on denied calls

**On WSL the eval sandbox refuses to start**, at no cost and before any session (`$0.00`, `0s`), with one of two messages. "a PATH directory could not be examined for keychain credential helpers (EACCES)" comes from the Windows `/mnt/…` entries on `PATH`; a plain `ls` of each succeeds, so strip them all. "credential store … holds a symbolic link inside it" comes from Docker Desktop's link in `~/.docker`; `DOCKER_CONFIG` does not help, so set `HOME` to a temporary directory holding only links to `~/.claude` and `~/.claude.json`. Build both into the project's eval target.

**A `tool_used` grader passes on an attempted call, even one the permission mode denied.** Prove a step through an artefact it writes, graded by a file grader, and grade what a reviewer would see. Before trusting a score, read the kept trace (`--keep-temp`: the sealed `home/` workspace and `out/trace.jsonl`) and compare each verdict with what happened. Restricted modes deny compound shell commands, so skills should say "one plain command per Bash call; write files with the Write tool".
