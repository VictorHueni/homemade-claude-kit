---
type: rule
paths:
  - "**/.github/workflows/**"
  - "**/.github/actions/**"
  - "**/action.yml"
  - "**/Makefile"
  - "**/*.mk"
---

# CI workflows

**No CI-only tooling.** A change that adds a tool to CI (linter, scanner, diff gate) ships its local counterpart in the same plan increment: declare the tool in the dev environment (the version-manager config in the dotfiles; check whether it is already declared) unless the project's lockfile already pins it, and add a Makefile target reproducing the CI invocation. Wire the target into the local CI aggregate when it is self-contained; keep it standalone when it needs external state (a base ref, a live URL).

**A run started with `GITHUB_TOKEN` does not trigger `workflow_run` when it completes**, even though `workflow_dispatch` itself works. In a chain that starts automatically (release, deploy, verify), make every later hop an explicit `gh workflow run` or `workflow_call`, never a `workflow_run` trigger, and do not keep a `workflow_run` listener alongside it "for safety": it works for humans and silently not for bots. Prove the chain with a bot-started run, not a manual one.

**`gh` in a job without `actions/checkout` fails** with `not a git repository`. Set `GH_REPO: ${{ github.repository }}` in the step's `env` (or pass `-R`). Reproduce locally with `gh workflow list` from a non-repo directory.
