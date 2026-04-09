# Ralph Loop — Iteration Prompt

This prompt is piped to a fresh agent instance by `ralph.sh` for each iteration.

---

## Instructions

You are executing one iteration of the Ralph Loop.

**Workspace:** `{{WORKSPACE_DIR}}`
**PRD Mode:** `{{PRD_MODE}}`

### Step 1: Read the protocol

Read `skills/ralph-loop-runner/SKILL.md` — specifically the **Iteration Protocol** section. This is your complete reference for what to do.

### Step 2: Read the workspace

Read these files in the workspace directory:

1. The execution plan (`*_exec_*.md`) — find the next `**Status:** pending` increment.
2. If `PRD Mode` is `with-prd`, read the PRD (`*_prd_*.md`) and use it to understand acceptance criteria.
3. `progress.txt` — understand what has been done so far.

### Step 3: Execute one increment

Follow the Iteration Protocol exactly:

1. Set the increment status to `in-progress`.
2. Implement the scope items.
3. Run the test gate commands.
4. If tests fail, fix and retry (max 3 attempts).
5. Mark the increment `done`.
6. If `PRD Mode` is `with-prd`, update PRD checkboxes.
7. Commit using the convention: `feat|fix|refactor(NNNN): increment XX — title`.
8. Append to `progress.txt`.

### Step 4: Signal completion

When you have finished one increment (or are blocked), output this exact signal on its own line:

```text
RALPH_COMPLETE
```

This tells `ralph.sh` that this iteration is done and it should check whether to spawn the next one.

---

**Important:** Do NOT attempt multiple increments in one iteration. Complete exactly one increment, then signal `RALPH_COMPLETE`.
