---
name: ops-runbook-creator
description: Create operator-grade runbooks for any project. Use when asked to write a runbook, document an operational procedure, capture a workflow just executed, or produce a step-by-step operator guide. Triggers on "create a runbook", "write a runbook for", "document this procedure", "add a runbook", "ops procedure", "operator guide", "incident playbook".
version: "1.0.0"
user-invocable: true
---

# Ops Runbook Creator

Produces clear, executable runbooks that an on-call operator can follow without prior context.
The output must be immediately usable: copy-paste ready commands, verifiable at every step, with troubleshooting grounded in real failure modes.

## When to invoke

Invoke when the user asks to:

- Write a new runbook for an operational procedure
- Capture a workflow just executed interactively (most common — extract from conversation history)
- Document non-obvious steps, workarounds, or failure modes discovered during ops work
- Write an incident playbook or troubleshooting guide for a recurring failure pattern
- Produce a reference runbook (secrets inventory, naming conventions, environment map)

**Do NOT invoke for:**

- Architecture decision records → use `spec-adr-manager`
- Implementation plans → use `spec-implementation-planner`
- General API or code documentation → use `technical-writer`
- Post-incident reports → those have a different structure (timeline, impact, root cause, action items)

## Workflow

### 1. Discover existing runbook conventions

Before drafting, check whether the project already has runbooks and what structure they follow:

```bash
find . -type f -name "*.md" | xargs grep -l "## Prerequisites\|## Troubleshooting" 2>/dev/null | head -10
ls docs/runbooks/ 2>/dev/null || ls runbooks/ 2>/dev/null || ls docs/ops/ 2>/dev/null
```

Read up to 2 existing runbooks to extract:
- Section order and naming
- Table formatting style (left-aligned `|:---|` vs default)
- How environments are labeled (Local/Staging/Production vs Dev/Prod vs nothing)
- Separator style in Related Documents (`--` vs `—` vs `-`)
- Whether expected output is shown inline or omitted

If existing runbooks have a clear style, follow it exactly. If none exist, use the canonical template in `references/runbook-template.md`.

### 2. Gather inputs

If the user just ran the procedure in conversation, extract everything from history — do not ask for what is already known. Otherwise ask for:

| Input | Why it matters |
|:------|:---------------|
| What operation does this cover? | Title and scope |
| Who runs it? (developer / DBA / on-call / data engineer) | Determines assumed knowledge level and command verbosity |
| Which environments? (local / staging / prod / all) | Determines whether to show per-environment variants |
| Prerequisites | What must be true before step 1 |
| Steps in order | The procedure itself |
| Success criteria | What verifies the operation completed correctly |
| Known failure modes | Real errors observed, not hypothetical ones |
| Related runbooks or docs | Cross-links |

### 3. Classify and choose structure

| Type | When | Key sections |
|:-----|:-----|:-------------|
| **Procedure** | Sequential steps to execute an operation | Steps + Expected output + Step summary table |
| **Reference** | Lookup information (secrets, naming, IDs) | Tables, minimal prose, no steps |
| **Troubleshooting-only** | Failure catalogue for an existing procedure | Symptom/Cause/Fix entries, link to parent runbook |

Most new runbooks are **Procedure** type. Use `references/runbook-template.md`.

### 4. Draft following the conventions

Apply every rule in `references/runbook-conventions.md`. The non-negotiable ones:

- **Copy-paste ready commands.** No mental assembly. Replace `<PLACEHOLDER>` values with the exact source instruction (`from Step 2 output`, `from the DB query above`, `GitHub → Settings → ...`).
- **Expected output at every write step.** If a step modifies state, it must have a `### Expected output` block with a real sample. The operator uses this to confirm success without reading logs.
- **Destructive warning before the command.** A `> **Warning:**` block must appear *before* any command that deletes, drops, wipes, or overwrites. Never after.
- **Non-obvious choices explained inline.** A `> **Why X:**` callout at the exact step where a gotcha lives — not collected in a "Notes" section at the end.
- **Dry-run first.** Any command that supports `--dry-run` must show the dry-run invocation before the real one.
- **Environment variants in the same step.** If the command differs between environments, show both labeled variants in one step block rather than separating them into different sections.

### 5. Write troubleshooting from real failure modes

Each troubleshooting entry must have:

- **Symptom:** the exact error message or observable behavior the operator sees
- **Cause:** the root cause (not "an error occurred")
- **Fix:** exact commands or steps to resolve

Do not invent hypothetical failures. Only document:
- Failure modes observed in the current conversation
- Failure modes documented in existing runbooks for the same system
- Failure modes that are structurally guaranteed (e.g., duplicate-key errors when a unique constraint exists)

### 6. Add the step summary table

After all steps, include a compact table:

```markdown
## Step summary

| # | Step | Command / action |
|:--|:-----|:-----------------|
| 1 | ... | `short command` |
```

If multiple environments apply, add a column per environment. This table is the quick-reference card for operators re-running the procedure.

### 7. Cross-link

- Add the new runbook to `## Related Documents` of the closest existing runbook
- Add related existing runbooks to the new runbook's `## Related Documents`
- Separator: use whatever separator style the existing runbooks use (default: `--`)

### 8. Save and report

Save to `docs/runbooks/<kebab-case-name>.md` (or wherever existing runbooks live in the project).
Tell the user:
- File path
- Which existing runbooks were updated with cross-links
- Any `<PLACEHOLDER>` values left in the draft that need the user's input to fill

## Quality checklist

Before finalizing, verify every item:

- [ ] Every step that modifies state has a `### Expected output` block with real sample output
- [ ] Every destructive command has a `> **Warning:**` block *before* it
- [ ] No unexplained `<PLACEHOLDER>` — every one has a source instruction
- [ ] Prerequisites table has a `How to verify` column with copy-paste commands
- [ ] Troubleshooting entries describe real failure modes with exact symptoms
- [ ] Step summary table present and covers all steps
- [ ] Commands are copy-paste ready — no assembly required by the operator
- [ ] Non-obvious decisions have inline `> **Why X:**` callouts
- [ ] `## Related Documents` section present with cross-links
- [ ] No emojis in the runbook body

## References

- `references/runbook-template.md` — blank procedure runbook template
- `references/runbook-conventions.md` — full style, formatting, and ops-efficiency rules
