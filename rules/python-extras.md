---
paths:
  - "**/pyproject.toml"
  - "**/setup.cfg"
---

# Python extras naming

Keep `pyproject.toml` `[project.optional-dependencies]` groups semantically pure. No convenience bundles.

- `[dev]` = CI/quality tools (pytest, ruff, mypy, refurb, vulture, etc.)
- `[api]` = API server runtime (fastapi, uvicorn, bleach)
- `[llm]` = LLM extraction runtime (openai, instructor)
- Other domain extras: name them after what they install (`[pipeline]`, `[ingest]`), not after who installs them.

Never bundle one extra inside another for convenience (e.g. do not add `"<project>[api]"` to `[dev]`). Developers install combinations explicitly: `pip install ".[dev,api]"` or `uv sync --extra dev --extra api`.

**Why:** A group called `[dev]` should contain dev tools, not runtime server dependencies. Explicit composition reads clearly; hidden bundling does not.
