---
name: pr-creator
description:
  Use this skill when asked to create a pull request (PR). It ensures all PRs
  follow the repository's established templates and standards.
---

# Pull Request Creator

This skill guides the creation of high-quality Pull Requests that adhere to the
repository's standards.

## Types (required)

| Type       | Description                         | Changelog |
| ---------- | ----------------------------------- | --------- |
| `feat`     | New feature                         | Yes       |
| `fix`      | Bug fix                             | Yes       |
| `perf`     | Performance improvement             | Yes       |
| `test`     | Adding/correcting tests             | No        |
| `docs`     | Documentation only                  | No        |
| `refactor` | Code change (no bug fix or feature) | No        |
| `build`    | Build system or dependencies        | No        |
| `ci`       | CI configuration                    | No        |
| `chore`    | Routine tasks, maintenance          | No        |

## Scopes (optional but recommended)
- `CLI` - Command Line Interface changes
- `API` - Public API changes
- `Ingestion` - Data ingestion components
- `Rules Engine` - Rules engine modifications
- `Claim Lifecycle` - Claim lifecycle management
- `Review/Operations UI` - User interface for review and operations
- `Data Store` - Data storage and retrieval systems
  
## Summary Rules

- Use imperative present tense: "Add" not "Added"
- Capitalize first letter
- No period at the end
- No ticket IDs
- Add `(no-changelog)` suffix to exclude from changelog

## Workflow

Follow these steps to create a Pull Request:
1. **Check current state**:
   ```bash
   git status
   git diff --stat
   git log origin/master..HEAD --oneline
   ```

2. **Analyze changes** to determine:
   - Type: What kind of change is this?
   - Scope: Which package/area is affected?
   - Summary: What does the change do?

3. **Push branch if needed**:
   ```bash
   git push -u origin HEAD
   ```

2.  **Locate Template**: Search for a pull request template in the repository.
    - Check `.github/pull_request_template.md`
    - Check `.github/PULL_REQUEST_TEMPLATE.md`
    - If multiple templates exist (e.g., in `.github/PULL_REQUEST_TEMPLATE/`),
      ask the user which one to use or select the most appropriate one based on
      the context (e.g., `bug_fix.md` vs `feature.md`).

3.  **Read Template**: Read the content of the identified template file.

4.  **Draft Description**: Create a PR description that strictly follows the
    template's structure.
    - **Headings**: Keep all headings from the template.
    - **Checklists**: Review each item. Mark with `[x]` if completed. If an item
      is not applicable, leave it unchecked or mark as `[ ]` (depending on the
      template's instructions) or remove it if the template allows flexibility
      (but prefer keeping it unchecked for transparency).
    - **Content**: Fill in the sections with clear, concise summaries of your
      changes.
    - **Related Issues**: Link any issues fixed or related to this PR (e.g.,
      "Fixes #123").

5.  **Create PR**: Use the `gh` CLI to create the PR. To avoid shell escaping
    issues with multi-line Markdown, write the description to a temporary file
    first.
    ```bash
    # 1. Write the drafted description to a temporary file
    # 2. Create the PR using the --body-file flag
    gh pr create --title "type(scope): succinct description" --body-file <temp_file_path>
    # 3. Remove the temporary file
    rm <temp_file_path>
    ```
    - **Title**: Ensure the title follows the
      [Conventional Commits](https://www.conventionalcommits.org/) format if the
      repository uses it (e.g., `feat(ui): add new button`,
      `fix(core): resolve crash`).

## Principles

- **Compliance**: Never ignore the PR template. It exists for a reason.
- **Completeness**: Fill out all relevant sections.
- **Accuracy**: Don't check boxes for tasks you haven't done.



## Examples

### Feature in editor
```
feat(editor): Add workflow performance metrics display
```

### Bug fix in core
```
fix(core): Resolve memory leak in execution engine
```

### Node-specific change
```
fix(Slack Node): Handle rate limiting in message send
```

### Breaking change (add exclamation mark before colon)
```
feat(API)!: Remove deprecated v1 endpoints
```

### No changelog entry
```
refactor(core): Simplify error handling (no-changelog)
```

### No scope (affects multiple areas)
```
chore: Update dependencies to latest versions
```

## Validation

The PR title must match this pattern:
```
^(feat|fix|perf|test|docs|refactor|build|ci|chore|revert)(\([a-zA-Z0-9 ]+( Node)?\))?!?: [A-Z].+[^.]$
```

Key validation rules:
- Type must be one of the allowed types
- Scope is optional but must be in parentheses if present
- Exclamation mark for breaking changes goes before the colon
- Summary must start with capital letter
- Summary must not end with a period
