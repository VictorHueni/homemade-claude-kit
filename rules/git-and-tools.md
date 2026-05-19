# Git & tool-use discipline

## Never `git commit --amend`

Always create a new commit. Amending rewrites a hash you may have already recorded elsewhere (progress logs, PR descriptions, follow-up commits) and creates self-inconsistent history.

If a pre-commit hook fails, the commit did NOT happen — the previous commit is unchanged. Fix the issue, re-stage, and create a NEW commit. Do not `--amend` to "fold the fix in."

Exception: only if the user explicitly asks for `--amend` in the same conversation.

## `Edit` tool: `replace_all=True` matches the whole `old_string`, not the inner substring

`replace_all=True` replaces every literal occurrence of the exact `old_string` you provided. If `old_string` is multi-line or contains surrounding context, occurrences of the inner substring with *different* surroundings will silently survive.

After any wide-pattern `replace_all`, follow up with:

```bash
git grep -n "<inner_string>" <dir>/
```

If grep still finds the string, those are the occurrences where the wider pattern did not match. Run targeted single-occurrence Edits for them. The grep takes 5 seconds; skipping it means the next test discovers the miss for you with a less helpful error.

**Heuristic for `old_string` width:**

- **Narrow `old_string`** (just the inner substring) + grep follow-up → safer default. Risk: over-replacement if the inner string is non-unique.
- **Wide `old_string`** (with surrounding context) → only when disambiguation is required. Risk: silent misses when surrounding context varies.

Anti-pattern: assuming a multi-line `replace_all` Edit "got everything" without verification.
