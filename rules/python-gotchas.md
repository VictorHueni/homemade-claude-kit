---
type: rule
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/uv.lock"
---

# Python tooling gotchas

**pydantic `validation_alias` makes the field's own name inert.** `Model(my_field=x)` does not set the field unless `populate_by_name=True`. Where extra input is ignored (the `BaseModel` default, or a settings class with `extra="ignore"`) it is silently dropped and the default stays; `BaseSettings` defaults to `extra="forbid"` and raises. To override an aliased settings field in a test, `monkeypatch.setenv("ALIAS", value)` and construct with no arguments, then assert the resulting attribute.

**`monkeypatch.delenv` does not reach `env_file`.** A test asserting a settings default passes in CI (no `.env`) and fails on any machine that has one. Pass `_env_file=None` and keep the `delenv`; a test asserting that the env var overrides the default needs neither. Tell: `Settings().x` and `Settings(_env_file=None).x` differ.

**xenon `--max-average` is a whole-tree metric.** Run on one file it reports violations the real gate does not have; `--max-absolute` and `--max-modules` are safe per file. For a per-file check drop `--max-average` or use `radon cc <file> -s`; only the project's full-scope gate is authoritative, so never refactor on a subset failure.

**radon and xenon drop nested functions** unless radon gets `--show-closures` (xenon has no such flag), so Typer/Click commands registered inside a function are never graded. Compare block counts with and without the flag before trusting any complexity claim; expect the closure-aware run to go red on first use and fix those violations in the same change. Keep such logic at module level or wrap radon's harvester with closures on. SonarQube's cognitive complexity folds nested functions into their parent instead: if the nested bodies capture no enclosing names (ignore the decorator list), judge each body on its own.

**A copied or moved venv keeps absolute shebangs.** `uv run <tool>` then runs a foreign interpreter while `uv run python -m <tool>` works; `uv sync` does not repair it, and a stale `VIRTUAL_ENV` warning is the same symptom. Tell: compare the interpreter each form reports (pytest prints it in its header). Recreate the venv; never copy one.

**`uv run` from the wrong directory creates a stray project** (`uv.lock` and `.venv/` where you stood) before failing on the path. Tell: `No 'requires-python' value found`. After such an error, check `git status` for a stray `uv.lock` and delete both; run as `cd <project> && uv run …`.

**An "unused `type: ignore`" on a suspicious line means two checkers disagree** (mypy's pydantic plugin can accept what Pyright rejects; read Pyright diagnostics when shown). Re-derive the type at the source: pass the literal where a guard guarantees it, or narrow `str` to `Literal` once in the producer; never widen the contract to silence it. Build typed test objects through a helper with explicit keyword arguments, not `Model(**shared_dict)`; keep `# type: ignore` for tests that deliberately break the contract.
