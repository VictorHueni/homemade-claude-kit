---
type: rule
---

# GitHub Actions: a `GITHUB_TOKEN`-started run is a dead end for `workflow_run`, and `gh` needs `GH_REPO` without a checkout

## Two suppressions, one hop apart

The documented rule is that events created with the repository `GITHUB_TOKEN` (tag pushes, releases, commits, comments) do not trigger workflows, with `workflow_dispatch` and `repository_dispatch` as the only exemptions. Measured 2026-09-26: that suppression reaches **one hop further** than the exemption suggests. A workflow that the token started via `gh workflow run` does run, but when it **completes**, no `workflow_run` event reaches its consumers. The identical workflow dispatched by a human chained to its `workflow_run` listener in two seconds; dispatched by `github-actions[bot]`, nothing was created, ever, and nothing reported it. The downstream verification (a post-deploy smoke pack that posts a commit status) silently never happened on a production release.

**How to apply:** in any chain that begins with an automatic dispatch (release automation → deploy → verify), every subsequent hop must itself be an explicit `gh workflow run` (or `workflow_call`), never a `workflow_run` trigger. Do not keep both paths "for safety": a `workflow_run` listener that works for humans and not for bots is a fork whose behaviour depends on who clicked, and the bot path is the one nobody watches. Prove a new chain with a bot-started run, not a manual one; a manual test of a `workflow_run` hop tells you nothing about the automatic path.

## `gh` in a checkout-less job fails with "not a git repository"

`gh workflow run`, `gh pr …`, `gh api repos/{owner}/{repo}/…` resolve the target repository from the local git remote. In a job with no `actions/checkout` step they die with `failed to run git: fatal: not a git repository`, exit 1. Release-automation jobs are exactly the ones that have no checkout. Set `GH_REPO: ${{ github.repository }}` in the step's `env` (or pass `-R`). Reproduce locally by running `gh workflow list` from a non-repo directory with and without `GH_REPO`.

**Why both bite together:** a hand review of the YAML sees a correct command and a correct trigger. Neither failure is visible until the automatic path runs end to end once, which is why a release-chain change deserves a synthetic release as its acceptance test, not a review.
