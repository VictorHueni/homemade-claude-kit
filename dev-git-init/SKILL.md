---
name: dev-git-init
description: 'Scaffold the deterministic git enforcement stack for a project in one Q&A pass — husky hooks (commit-msg, pre-commit, pre-push), commitlint with Conventional Commits, gitleaks secret detection, .gitignore + .gitattributes + .editorconfig, CONTRIBUTING.md narrative, GitHub PR template + CODEOWNERS + 3 issue templates, optional GitHub Actions workflows for CI gates, and a copy-paste-ready scripts/setup-branch-protection.sh. Two modes: scaffold (interactive Q&A; idempotent — never blindly overwrites) and audit (read-only check of which components are in place). Does NOT execute installers or apply branch protection — emits the install command and writes the protection script for operator review. Triggers on: scaffold git, git init, set up git hooks, install husky, install commitlint, set up commit conventions, set up PR template, set up CODEOWNERS, branch protection, git workflow setup, dev workflow setup, repo conventions, scaffold contributing.'
version: "1.0.0"
status: active
last_reviewed: 2026-05-28
review_interval: 180d
user-invocable: true
allow_implicit_invocation: true
impact: "medium"
metadata:
  category: "infrastructure"
  complexity: "medium"
---

# Git Enforcement Stack Scaffolder

## Overview

`dev-git-init` provisions the **deterministic git enforcement stack** for a project — the layered set of client-side hooks, server-side checks, and convention files that make every contributor (human or AI) produce compliant commits, branches, and PRs without having to remember the rules. It is the one-shot scaffolder that lands before the project's first real commit.

**Two-layer model the skill assumes** (per industry standard pre-AI tooling):

- **Client-side hooks** = fast, bypassable feedback (husky / commitlint / gitleaks pre-commit)
- **Server-side checks** = authoritative, unbypassable truth (GitHub Actions + branch protection)

Both layers exist; the AI-skill layer is purely a *compliance helper* on top — it does not replace enforcement.

**Scope discipline:**
- This skill **writes files** — it does NOT install dependencies (`pnpm add ...`), execute hooks, or apply remote configuration (branch protection on GitHub). It emits commands for the operator to run.
- It **never blindly overwrites** existing files. Every detected conflict prompts the operator: skip / overwrite / diff.
- It produces no `.claude/*.yaml` config file. The scaffolded standard files (`commitlint.config.js`, `.husky/`, `CONTRIBUTING.md`, `.github/*`) ARE the source of truth that downstream skills (`dev-git-commit`, `dev-pr`) read.

---

## Output catalogue

What the skill writes when all questions answered with defaults:

| File | Purpose | Skipped if exists? |
|---|---|---|
| `.husky/commit-msg` | Runs commitlint on the just-written message | Prompt |
| `.husky/pre-commit` | Runs gitleaks on staged diff | Prompt |
| `.husky/pre-push` | Optional heavy checks (project-defined) | Prompt |
| `commitlint.config.js` | Allowed types / scope rules / subject case / max length | Prompt |
| `.gitleaks.toml` | Allowlist for known false-positive patterns | Prompt |
| `.gitignore` | Stack-appropriate ignores (Node / Python / Go / etc.) | Merge if exists |
| `.gitattributes` | Line endings + binary marking | Prompt |
| `.editorconfig` | Universal indent / charset / EOL per file type | Prompt |
| `CONTRIBUTING.md` | Branching + commit + PR + reviewer + protection conventions | Prompt |
| `.github/PULL_REQUEST_TEMPLATE.md` | Auto-loaded PR body skeleton | Prompt |
| `.github/CODEOWNERS` | Reviewer routing (default: `* <owner>`) | Prompt |
| `.github/ISSUE_TEMPLATE/{bug,feature,docs}.md` | Structured issue templates | Prompt each |
| `.github/workflows/{lint-build,typecheck,test,gitleaks}.yml` | CI gate workflows | Prompt each (gated by Q6) |
| `scripts/setup-branch-protection.sh` | Idempotent `gh api` script to apply branch protection rules | Prompt |

What the skill does **NOT** write:
- `lint-staged` config (varies too much by stack — defer to per-stack skill)
- PR title enforcement Action like `amannn/action-semantic-pull-request` (commitlint on commits + reviewer's checklist on PR title covers it at MVP)
- ADRs (the operator runs `arch-adr` separately if they want one — closing report names this)
- `package.json` script entries (operator adds via the emitted install command — skill does not silently mutate package.json)
- `.claude/*.yaml` config (classical configs above ARE the source of truth — no parallel schema)

---

## Modes

| Mode | Purpose | Side effects |
|---|---|---|
| `scaffold` | Interactive Q&A → generate the stack | Writes files (with confirmation on conflict) |
| `audit` | Read-only check: which stack components are in place vs missing | None — report only |

`refresh` mode (detect drift between declared conventions and what's installed) is deferred to a future version. For now, re-running `scaffold` against an existing project performs the equivalent function via the per-file conflict prompts.

---

## Mode: `audit` (read-only)

Run first whenever the project already has any of the stack components.

### Step 1 — detect existing files

```bash
# Run from project root
for f in \
  .husky/commit-msg .husky/pre-commit .husky/pre-push \
  commitlint.config.js commitlint.config.mjs .commitlintrc.yaml .commitlintrc.json \
  .gitleaks.toml \
  .gitignore .gitattributes .editorconfig \
  CONTRIBUTING.md \
  .github/PULL_REQUEST_TEMPLATE.md \
  .github/CODEOWNERS \
  .github/ISSUE_TEMPLATE/bug.md .github/ISSUE_TEMPLATE/feature.md .github/ISSUE_TEMPLATE/docs.md \
  .github/workflows/lint-build.yml .github/workflows/typecheck.yml .github/workflows/test.yml .github/workflows/gitleaks.yml \
  scripts/setup-branch-protection.sh; do
  [ -e "$f" ] && echo "✅ $f" || echo "⬜ $f"
done
```

Also detect:
- Stack: `package.json` (Node) · `pyproject.toml` (Python) · `go.mod` (Go) · `Cargo.toml` (Rust)
- Package manager (Node only): presence of `pnpm-lock.yaml` / `yarn.lock` / `package-lock.json`
- Default branch: `git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'`
- Repo platform: `git remote get-url origin` (github.com / gitlab.com / bitbucket.org)

### Step 2 — report

Report format:

```
## Audit — git enforcement stack

**Stack detected:** Node + pnpm (pnpm-lock.yaml present)
**Default branch:** main
**Platform:** github.com (VictorHueni/blocops)

**In place (8 of 14):**
- ✅ CONTRIBUTING.md
- ✅ .github/PULL_REQUEST_TEMPLATE.md
- ✅ .github/CODEOWNERS
- ✅ .github/ISSUE_TEMPLATE/{bug, feature, docs}.md
- ✅ scripts/setup-branch-protection.sh

**Missing (6 of 14):**
- ⬜ .husky/commit-msg
- ⬜ .husky/pre-commit
- ⬜ .husky/pre-push
- ⬜ commitlint.config.js
- ⬜ .gitleaks.toml
- ⬜ .editorconfig
- ⬜ .gitattributes
- ⬜ .github/workflows/{lint-build, typecheck, test, gitleaks}.yml

**Next action:** run `scaffold` mode to fill the missing 6 components.
The 8 in-place components will be skipped automatically (prompted only if --force).
```

End audit mode.

---

## Mode: `scaffold` (interactive Q&A)

### Step 0 — ask the question set

Ask all questions in one message. User responds like `1A, 2A, 3B, 4A, 5A, 6yes, 7no`.

```
1. Language / package manager?
   A. pnpm (Node) — recommended for new projects
   B. npm (Node)
   C. yarn (Node)
   D. python + pre-commit framework
   E. go
   F. rust
   G. other / no package manager — install hooks via plain git

2. Default branch?
   A. main (recommended)
   B. master
   C. custom (specify)

3. Conventional Commit types allowed?
   A. Minimal recommended: feat, fix, docs, chore, refactor, test, perf
   B. Full standard set: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
   C. Custom (specify list)

4. Branching strategy + merge mode?
   A. Trunk-based + squash-merge (recommended for solo + small teams + continuous deploy)
   B. GitLab Flow with develop integration branch + squash to main on release cadence
   C. GitFlow (develop + release/* + hotfix/*)

5. Reviewer model?
   A. Solo founder — admin bypass for self-merge (no required approval at start)
   B. Mutual peer review — every PR needs 1 approval from any team member
   C. CODEOWNERS-driven — required approval from owners of changed paths

6. Generate GitHub Actions workflows for the four CI gates (lint-build, typecheck, test, gitleaks)?
   A. Yes — scaffold workflow shells (mostly _TODO_ until the app exists)
   B. No — I'll add later

7. Closing report should suggest recording the branching decision as an ADR via arch-adr?
   A. Yes (default)
   B. No
```

Recommended default answers: `1A, 2A, 3A, 4A, 5A, 6A, 7A`.

### Step 1 — detect existing project state

Run the audit detection from §Mode: audit. Capture the list of files that already exist — those go into the "skip / prompt" set for Step 3.

Also capture:
- Owner for CODEOWNERS catch-all: `gh repo view --json owner -q .owner.login 2>/dev/null` or `git config user.name`
- Repo full name: `gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null` or parse from `git remote get-url origin`

### Step 2 — confirm scope

Echo back the scoped plan:

```
## Plan

**Will scaffold (6 missing files):**
- .husky/commit-msg, .husky/pre-commit, .husky/pre-push
- commitlint.config.js
- .gitleaks.toml
- .editorconfig
- .gitattributes
- .github/workflows/{lint-build, typecheck, test, gitleaks}.yml

**Will skip (8 already exist, use --force to overwrite):**
- CONTRIBUTING.md, .github/PULL_REQUEST_TEMPLATE.md, .github/CODEOWNERS,
  .github/ISSUE_TEMPLATE/{bug, feature, docs}.md, scripts/setup-branch-protection.sh

**Will emit (not execute):**
- pnpm install command for husky + commitlint + gitleaks
- `./scripts/setup-branch-protection.sh` instruction (run after first CI workflow)
- arch-adr instruction to record branching decision (per Q7)

Proceed? (y/n)
```

Wait for confirmation. Stop on n.

### Step 3 — write files

For each file in the scoped scaffold list, write the appropriate template from §File templates below, substituting per-answer values.

**Idempotency:**
- File exists → skip silently (already reported as "Will skip" in Step 2)
- File doesn't exist + parent dir doesn't exist → create dir + file
- File doesn't exist + parent dir exists → create file

`--force` mode (operator-flagged): for each existing file, prompt:
```
File exists: CONTRIBUTING.md (1247 bytes, modified 2026-05-25)
  o = overwrite with skill template
  s = skip (keep existing)
  d = show diff between existing and template
Choice [s]:
```

Never blindly overwrite. The default action on conflict is always skip.

### Step 4 — closing report

```
## Scaffolded
- ✅ .husky/commit-msg (calls commitlint)
- ✅ .husky/pre-commit (calls gitleaks)
- ✅ .husky/pre-push (placeholder for heavy checks)
- ✅ commitlint.config.js (Conventional Commits + 7-type subset per Q3)
- ✅ .gitleaks.toml (default + project allowlist scaffold)
- ✅ .gitattributes (LF line endings, binary marking)
- ✅ .editorconfig (2-space indent, UTF-8, LF, trim trailing whitespace)
- ✅ .github/workflows/lint-build.yml (shell with _TODO_ until app scaffolds)
- ✅ .github/workflows/typecheck.yml (shell)
- ✅ .github/workflows/test.yml (shell)
- ✅ .github/workflows/gitleaks.yml (full-history scan)

## Skipped (already present — use --force to overwrite)
- CONTRIBUTING.md
- .github/PULL_REQUEST_TEMPLATE.md
- .github/CODEOWNERS
- .github/ISSUE_TEMPLATE/{bug, feature, docs}.md
- scripts/setup-branch-protection.sh

## Next steps

1. Install dependencies (run as operator — skill does not execute):

   pnpm add -D husky @commitlint/cli @commitlint/config-conventional
   pnpm exec husky init
   # gitleaks installed via OS package (brew install gitleaks / scoop install gitleaks / etc.)

2. Verify hooks fire:

   echo "test commit" | pnpm exec commitlint     # should reject
   echo "feat: test commit" | pnpm exec commitlint  # should pass

3. Commit the scaffold:

   git add .husky/ commitlint.config.js .gitleaks.toml .editorconfig .gitattributes .github/workflows/
   git commit -m "chore(repo): scaffold git enforcement stack via dev-git-init"

4. Push and open the first PR to trigger CI workflows (so status check names register with GitHub).

5. Apply branch protection (once workflows have run at least once):

   ./scripts/setup-branch-protection.sh

6. (Per Q7) Record the branching decision as an ADR:

   Run the arch-adr skill: arch-adr create "ADR-XXXX — Git Branching Strategy and Merge Mode"
   (Use trunk-based + squash-merge from Q4 as the chosen option; document the triggers
    that would re-open the decision.)
```

End scaffold mode.

---

## File templates

The templates below are inline for self-contained execution. Substitute placeholders per the Q&A answers.

### `.husky/commit-msg`

```sh
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx --no -- commitlint --edit "$1"
```

Make executable: `chmod +x .husky/commit-msg`.

### `.husky/pre-commit`

```sh
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# Secret scanning on staged diff
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks protect --staged --no-banner --redact
else
  echo "⚠ gitleaks not installed — skipping secret scan. Install via your OS package manager."
fi
```

Make executable: `chmod +x .husky/pre-commit`.

### `.husky/pre-push`

```sh
#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

# Heavy pre-push checks. Uncomment as the project gains the corresponding scripts.
# pnpm typecheck
# pnpm test
```

Make executable: `chmod +x .husky/pre-push`.

### `commitlint.config.js` (per Q3 answer)

For Q3 = A (minimal 7-type subset):

```js
/** @type {import('@commitlint/types').UserConfig} */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', ['feat', 'fix', 'docs', 'chore', 'refactor', 'test', 'perf']],
    'subject-case': [2, 'always', 'lower-case'],
    'subject-max-length': [2, 'always', 72],
    'body-max-line-length': [2, 'always', 72],
    'header-max-length': [2, 'always', 100],
  },
};
```

For Q3 = B (full standard set): omit the `type-enum` override (use the preset's default list).

For Q3 = C (custom list): substitute the custom array in `type-enum`.

### `.gitleaks.toml`

```toml
# gitleaks config — extends the default ruleset.
# Add per-project allowlist entries below as false positives surface.

[allowlist]
description = "Project-specific allowlist"
paths = [
  # '''docs/business/06a-models/.*\.md''',  # example: documentation containing fake API keys
]
regexes = [
  # '''AKIA[0-9A-Z]{16}''',  # example: a specific known-safe pattern
]
```

### `.gitignore`

Per Q1 stack, write the appropriate ignore set. For Node + Next.js:

```
# Node
node_modules/
.pnpm-store/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Next.js
.next/
out/
build/
.vercel/

# Environment
.env
.env.local
.env.*.local
!.env.example

# Editor
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Supabase local
supabase/.branches/
supabase/.temp/
```

For other stacks, generate from https://www.toptal.com/developers/gitignore equivalent ruleset.

If `.gitignore` already exists, append missing sections rather than overwrite (prompt confirms append).

### `.gitattributes`

```
# Normalize line endings on checkout to LF
* text=auto eol=lf

# Specific text types
*.md     text
*.json   text
*.yml    text
*.yaml   text
*.sh     text eol=lf
*.js     text
*.ts     text
*.tsx    text
*.css    text

# Binary types (never diff or merge)
*.png    binary
*.jpg    binary
*.jpeg   binary
*.gif    binary
*.svg    text
*.ico    binary
*.pdf    binary
*.zip    binary
*.gz     binary
```

### `.editorconfig`

```
# https://editorconfig.org
root = true

[*]
charset = utf-8
end_of_line = lf
indent_style = space
indent_size = 2
insert_final_newline = true
trim_trailing_whitespace = true
max_line_length = 100

[*.md]
trim_trailing_whitespace = false
max_line_length = off

[Makefile]
indent_style = tab
```

### `CONTRIBUTING.md`

(Generated from `references/templates/contributing-template.md` with per-answer substitution. The template covers: TL;DR · branching strategy per Q4 · branch naming table per Q3 type set · Conventional Commits per Q3 · PR workflow · CI gates per Q6 · reviewer's checklist · review model per Q5 · local pre-flight · AI-assisted dev habits · branch protection rules per Q5 + Q6 · conventions-change process. Include the canonical-rationale pointer to the ADR if Q7 = yes.)

### `.github/PULL_REQUEST_TEMPLATE.md`

```markdown
<!--
Auto-loaded on every PR. Fill every section; delete sections that genuinely don't
apply (don't leave empty placeholders). See CONTRIBUTING.md for the full workflow.
-->

## Summary

<!-- 1–3 sentences. What does this PR change? -->

## Why

<!-- Link the upstream artefact: issue #, ADR-NNNN, PRD-NNNN, or a business reason. -->

Closes #
References:

## What's NOT in this PR

<!--
Anti-scope-creep checkpoint. List anything a reviewer might expect to see here that
you intentionally deferred to another PR. If nothing, write "Nothing — fully scoped."
-->

## Pre-flight (tick before requesting review)

- [ ] Ran local pre-flight commands — all green
- [ ] Verified every external API call exists in current vendor docs
- [ ] No secrets, no PII, no `.env` content in the diff
- [ ] Self-reviewed the diff in the GitHub UI before requesting review

## Reviewer attention

<!-- Anything specific to look at? Edge cases? A section you're less sure about? -->

## Test plan

<!-- How did you verify this works? What scenarios did you exercise? -->
```

### `.github/CODEOWNERS`

```
# CODEOWNERS — first-match-wins; later patterns override earlier ones.
# Docs: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-security/customizing-your-repository/about-code-owners

# Catch-all — every file requires owner visibility by default
*    @{{owner}}
```

Substitute `{{owner}}` with the detected GitHub username.

For Q5 = C (CODEOWNERS-driven), include path-specific entries the operator can extend:

```
*                      @{{owner}}
/.github/              @{{owner}}
/CONTRIBUTING.md       @{{owner}}
```

### `.github/ISSUE_TEMPLATE/bug.md`

```markdown
---
name: Bug report
about: Something is broken or behaving unexpectedly
title: "fix: "
labels: bug
---

## What happened

<!-- 1–2 sentences. What did you observe? -->

## What you expected

<!-- 1 sentence. What should have happened instead? -->

## Steps to reproduce

1. 
2. 
3. 

## Environment

- Browser / device:
- URL or page:
- Timestamp:

## Screenshots / logs

<!-- Paste relevant link, console output, or screenshot -->
```

### `.github/ISSUE_TEMPLATE/feature.md`

```markdown
---
name: Feature request
about: A new capability or improvement
title: "feat: "
labels: feature
---

## What user need does this serve

## What does success look like

## Acceptance criteria

- [ ] 
- [ ] 

## Linked artefacts

- PRD:
- ADR:
- Related issue: #
```

### `.github/ISSUE_TEMPLATE/docs.md`

```markdown
---
name: Documentation
about: A doc is missing, wrong, or unclear
title: "docs: "
labels: documentation
---

## What's wrong / missing

## What should it say
```

### `.github/workflows/lint-build.yml` (per Q6)

```yaml
name: lint-build
on:
  pull_request:
    branches: [{{default_branch}}]
  push:
    branches: [{{default_branch}}]

jobs:
  lint-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: latest
      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm build
```

Substitute `{{default_branch}}` per Q2. Adapt commands per Q1 stack (npm / yarn / Python / Go / Rust).

### `.github/workflows/typecheck.yml`

```yaml
name: typecheck
on:
  pull_request:
    branches: [{{default_branch}}]
  push:
    branches: [{{default_branch}}]

jobs:
  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: latest
      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm typecheck
```

### `.github/workflows/test.yml`

```yaml
name: test
on:
  pull_request:
    branches: [{{default_branch}}]
  push:
    branches: [{{default_branch}}]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
        with:
          version: latest
      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'
          cache: pnpm
      - run: pnpm install --frozen-lockfile
      - run: pnpm test
```

### `.github/workflows/gitleaks.yml`

```yaml
name: gitleaks
on:
  pull_request:
    branches: [{{default_branch}}]
  push:
    branches: [{{default_branch}}]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # full history for full-repo scan
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # GITLEAKS_LICENSE: not required for public repos; required for private orgs at scale
```

### `scripts/setup-branch-protection.sh`

```bash
#!/usr/bin/env bash
# Idempotent — re-run anytime to re-apply branch protection rules.
# Pre-requisites:
#   - gh CLI installed and authenticated with admin scope on the repo
#   - First PR has run at least once so required status check names exist
#
# Usage:
#   ./scripts/setup-branch-protection.sh                       # detects repo + uses main
#   ./scripts/setup-branch-protection.sh owner/repo            # explicit repo
#   ./scripts/setup-branch-protection.sh owner/repo branch     # explicit branch

set -euo pipefail

REPO="${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}"
BRANCH="${2:-{{default_branch}}}"

echo "Applying branch protection to ${REPO}:${BRANCH} ..."

gh api "repos/${REPO}/branches/${BRANCH}/protection" -X PUT --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["lint-build", "typecheck", "test", "gitleaks"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": {{required_approving_review_count}},
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": {{require_code_owner_reviews}}
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON

echo "✅ Branch protection applied. Verify in the GitHub UI:"
echo "   https://github.com/${REPO}/settings/branches"
```

Substitute per Q5 answer:
- Q5 = A (solo founder): `required_approving_review_count: 1`, `require_code_owner_reviews: true`, **leave `enforce_admins: false`** so founder can `gh pr merge --admin`
- Q5 = B (mutual): `required_approving_review_count: 1`, `require_code_owner_reviews: false`, `enforce_admins: false`
- Q5 = C (CODEOWNERS): `required_approving_review_count: 1`, `require_code_owner_reviews: true`, `enforce_admins: true` (stricter — admins can't bypass)

Make executable: `chmod +x scripts/setup-branch-protection.sh`.

---

## Stack-specific adaptations (Q1)

| Q1 answer | Hook manager | Lint runner | Workflow runtime |
|---|---|---|---|
| pnpm (Node) — default | husky | (project's `pnpm lint`) | `pnpm/action-setup@v3` + `actions/setup-node@v4` |
| npm (Node) | husky | `npm run lint` | `actions/setup-node@v4` |
| yarn (Node) | husky | `yarn lint` | `actions/setup-node@v4` |
| python + pre-commit framework | `pre-commit` (`.pre-commit-config.yaml`) | covered by pre-commit hooks | `actions/setup-python@v5` + `pre-commit/action@v3` |
| go | `lefthook` or plain `.git/hooks/` install script | `golangci-lint` | `actions/setup-go@v5` + `golangci/golangci-lint-action@v4` |
| rust | `cargo-husky` (committed as dev-dependency in `Cargo.toml`) | `cargo clippy` | `actions-rust-lang/setup-rust-toolchain@v1` |
| other / plain git | shell scripts installed manually | project-defined | project-defined |

For non-Node stacks the hook installation step changes — the closing report's "Next steps" should emit the right install command for the chosen stack.

---

## Anti-patterns

1. **Silently overwriting existing files.** If `CONTRIBUTING.md` already exists, the operator wrote it for a reason. Always prompt; default to skip.
2. **Running installers.** The skill is a scaffolder, not an installer. Emit `pnpm add -D ...` for the operator to run; do not invoke it.
3. **Applying branch protection from the skill.** Branch protection is a remote side effect with lockout risk. Write the script; do not run it.
4. **Generating `.claude/dev-skills.yaml`.** The classical configs ARE the source of truth. Do not mint a parallel schema.
5. **Hardcoding project-specific scopes** (insurance domain, claims lifecycle, etc.) in templates. Templates must be domain-agnostic; operators add project-specific content in their CONTRIBUTING.md after scaffolding.
6. **Skipping the audit step on existing projects.** Always detect what's present before scaffolding; never blindly write.
7. **Forgetting `chmod +x` on `.husky/*` and `scripts/*.sh`.** Hooks won't fire if not executable. The skill's file-write step must explicitly set the executable bit on scripts.

---

## Checklist

**Before reporting done in scaffold mode:**

- [ ] Q&A answers captured in scope summary (Step 2)
- [ ] Existing-file conflicts surfaced; operator decisions respected
- [ ] All written files exist at their target paths
- [ ] All `.husky/*` and `.sh` files are executable (`chmod +x` applied)
- [ ] Closing report lists what was scaffolded vs skipped
- [ ] Next-steps section names the install command for the chosen stack
- [ ] If Q7 = yes, closing report explicitly suggests `arch-adr create "ADR-XXXX — Git Branching Strategy and Merge Mode"` with the chosen Q4 + Q5 values to seed the ADR

**In audit mode:**

- [ ] All 14 standard files checked
- [ ] Stack + default branch + repo platform detected
- [ ] Report shows in-place / missing split
- [ ] Next-action recommendation given

---

## Relations to other skills

- **Consumed by `dev-git-commit`** (post-rewrite): reads `commitlint.config.js` for type/scope rules, `.husky/commit-msg` to know what's about to run, `package.json scripts` for pre-flight commands, `CONTRIBUTING.md` for narrative fallback
- **Consumed by `dev-pr`** (post-rewrite): reads `commitlint.config.js` for PR title format, `.github/PULL_REQUEST_TEMPLATE.md` for body skeleton, `.github/CODEOWNERS` for reviewer acknowledgement, `docs/architecture/decisions/adr-*.md` glob for auto-linking ADR references
- **Suggests `arch-adr`** (post-scaffold, via closing report): operator runs arch-adr to record the branching decision formally
- **Independent of `dev-git-worktree`, `dev-ralph-loop`, `dev-stack-guide`** — they operate alongside the enforcement stack without depending on its scaffolding state
- **Detected by `util-metamodel-audit`** indirectly — the optional ADR (if scaffolded via arch-adr) is checked for frontmatter validity and ID conventions
