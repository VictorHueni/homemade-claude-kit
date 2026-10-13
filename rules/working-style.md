---
type: rule
---

# Working style

- **One critical path.** Recommend a single sequential order for a multi-plan initiative even when plans could run in parallel; show what is parallelisable in the dependency graph, and propose parallel phases only when the owner opts in.
- **Verify before acting on a recorded claim.** Before fixing something a tracker, memory, earlier analysis or plan describes, check it against the current code (grep the callers, read the cited line, inspect the schema, `git log` the file). For a recorded workaround, check whether the underlying problem was fixed. Do not draft a fix for an issue you have not confirmed is live.
- **Reuse the project's own automation** (Makefile target, task recipe, script) before writing a bespoke equivalent: pointing it at the new case is what exposes its stale assumptions. Read the recipe end to end and check what it destroys, what it assumes is running, and how each line resolves its target; where semantics differ, adopt it with the constraint written at the call site. A command copy-pasted in docs is a missing target: add it. Two steps resolving the same resource by different mechanisms (an orchestrator's env file versus the shell environment) agree only while one instance exists; make such recipes fail closed on a mismatch.
- **Asynchronous systems** (DNS, CDN, certificates, queues): a write reported as successful but not yet visible is usually still propagating. Poll the downstream source for several minutes (`dig` the authoritative server; an unbumped SOA serial means not yet published) and read the stored value back; delete and recreate only when the readback proves it wrong, never to hurry propagation.
- **Comments explain why, sparingly,** at the density of the surrounding file. No narration of what the code does and no history in code (`was:`, "previously", dated notes, tombstones); delete a replaced code's comment with it.
- **Never hard-wrap markdown prose:** one line per paragraph or list item (tables and code blocks keep their own lines).
- **Sources in answers:** every figure or factual claim in a reply names its source, with an inline link when public and the arXiv or canonical ID for a paper.
