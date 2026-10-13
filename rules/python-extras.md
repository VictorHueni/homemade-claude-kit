---
type: rule
paths:
  - "**/*.py"
  - "**/pyproject.toml"
  - "**/uv.lock"
---

# Python extras — cross-project gotchas

## Pydantic v2 `validation_alias` silently ignores same-name kwargs

When a `pydantic`/`pydantic-settings` field declares `validation_alias="ENV_VAR_NAME"`, constructing the model with a keyword matching the **Python field name** (not the alias) is silently ignored — the field falls back to its default, with no error or warning. `Model(my_field=value)` behaves identically to `Model()`.

**Why:** `validation_alias` restricts validation input to the alias only, unless `model_config = SettingsConfigDict(populate_by_name=True)` (or `ConfigDict` for plain `BaseModel`) is also set. Silent fallback-to-default is the trap — no `TypeError`, no unexpected-kwarg warning; the test just asserts the wrong thing and passes accidentally (e.g. a "mode X enables the limiter" test still passing when the constructor arg was fully inert and the code path never varied).

**How to apply:** to construct/override an aliased settings field in a test, use `monkeypatch.setenv("ENV_VAR_NAME", value)` then build the model with no args — never pass the field by its Python name expecting it to take effect. Before trusting any test that constructs a `BaseSettings` subclass with a keyword arg, check whether that field has `validation_alias` set; if so, verify the test actually exercises different code paths (e.g. print/assert the resulting attribute) rather than trusting the kwarg silently worked.

**Why it matters:** discovered when two parametrized "enabled" tests for both non-default values passed only because the kwarg was inert and the default (`OFF`) happened to satisfy the OFF-path assertion by coincidence, while the LOG/ENFORCE assertions failed loudly once a differing default was in play — the bug was real and caught, but only because the two states produced different outcomes for once. A test with the same expected outcome across all constructor values would have passed silently on inert input forever.

## `monkeypatch.delenv` does not reach `env_file` — a default-asserting settings test is red on dev and green in CI

A `BaseSettings` subclass with `model_config = SettingsConfigDict(env_file=(".env", …))` reads **two** sources: the process environment *and* the dotenv file. `monkeypatch.delenv("VAR")` clears only the first. So a test written as `monkeypatch.delenv("VAR"); assert Settings().field == <default>` still receives the dotenv's value on any machine that has a populated `.env` — and asserts against it.

**The failure inverts the usual direction: it is green in CI and red locally.** CI checks out a clean tree with no `.env` (it is gitignored), so the default really is unset there and the test passes on the merge that introduces it. Every developer with a working `.env` then gets a red local gate on code they did not touch, which reads as a broken checkout rather than a defective test. Any consumer of a *shared* dev env file (`.env.local`, `.envrc`, a direnv-managed tree, a docker-compose `env_file`) fails the same way.

**How to apply:** a test that asserts a settings **default** must pass `_env_file=None` (pydantic-settings accepts it as a per-instantiation override); keep the `delenv` too, since the two sources are independent and an exported variable still wins. Conversely, a test asserting that the *env var overrides* the default needs neither — `setenv` outranks the dotenv in the resolution order, which is why that sibling test keeps passing and makes the failure look selective. Discriminator when a settings test fails locally but not in CI: print `Settings().field` next to `Settings(_env_file=None).field`; if they differ, the dotenv is the input, not the environment.

**Why:** the natural reading of `delenv` is "the variable is now unset", and for a plain `os.environ` lookup it would be. `env_file` silently widens the input surface beyond what the scrubbing tool addresses, so the test's isolation is partial in a way nothing reports. **Anti-pattern in self:** on seeing a settings test fail locally and pass in CI, reaching for "stale venv / dirty environment" — the environment was clean; the file was the leak.

## xenon `--max-average` is a whole-tree metric — per-file invocations produce phantom failures

xenon's three thresholds have different scope semantics. `--max-absolute` (per-block grade) and `--max-modules` (per-module average) are subset-safe — they yield the same verdict whether you scan one file or the whole tree. `--max-average` averages over **all scanned blocks**, so running xenon on a single changed file evaluates that file's own average against a threshold calibrated for the full codebase — and exits non-zero on a "violation" the real gate does not have. A file whose module average is legally B (under `--max-modules B`) will *always* fail a per-file `--max-average A` check.

**Why:** the average threshold answers "is the codebase simple on the whole?", not "is this file OK?" — a handful of grade-C functions dominates a 16-block file average but vanishes into a 1500-block tree average. The per-function and per-module caps are what prevent complex code hiding behind dilution; the tree average adds nothing at file scope. The red exit code is the trap: an agent seeing it concludes the increment broke the complexity gate and starts refactoring legal code (or invokes a complexity-reduction agent) to fix a metric artifact.

**How to apply:** for a per-file sanity check use `radon cc <file> -s` (per-block grades, no aggregate gate) or drop `--max-average` from the xenon flags; treat the project's full-scope gate invocation (Makefile/CI) as the only authoritative signal for the average threshold. Never start refactoring off a subset-scoped xenon failure — re-run the full gate first. (Observed twice in one autonomous loop: a CLI module averaging B alone while the tree averaged A, both runs green on the real gate.)

## radon/xenon silently DISCARD nested functions — a complexity gate is blind to any closure-based idiom

`radon cc` and `xenon` do not analyse nested `def`s unless `--show-closures` is passed. The complexity is **dropped entirely** — not folded into the enclosing function, not reported separately. A wrapper whose body is only decorator applications therefore reports **CC 1, grade A**, no matter how much logic sits inside it.

This is not a corner case: it is exactly the shape of the ubiquitous CLI registration idiom (Typer/Click `def register(app): @app.command() def cmd(...): ...`), plus decorator factories, `functools.partial` builders, and pytest fixture factories. Measured case: an 800-ncloc CLI module reporting one grade-A block actually contained eleven, one of them **grade D (CC 26)** — a violation of the `--max-absolute C` threshold already in force, that the gate had never once evaluated. Tree-wide, 28 of 1 555 blocks were invisible.

**How to apply:** run `radon cc <dir> -j --show-closures` and diff the block count against the default run before trusting any statement about a codebase's worst function or its complexity distribution — if the counts differ, the default numbers are unsound. When a gate exists, note that only `radon cc` has `--show-closures`; xenon (0.9.3, the only release) has no such flag and hard-codes closures off. Either wrap radon's harvester with `show_closures=True` and xenon's `find_infractions` in a small script, or keep plain xenon and make the premise true by convention (Typer commands and other logic at module level, never in a nested `def`), with `radon cc -s --show-closures` as a periodic hand audit. Expect the closure-aware run to turn red on first use: fix the newly-revealed violations in the same PR.

**Cross-check against a cognitive-complexity tool if one is available** (SonarQube `python:S3776`), because it fails the *opposite* way: Sonar aggregates nested-function complexity into the enclosing function, so it reports one implausible number (e.g. cognitive 115) where ten independent commands exist. To tell artifact from substance, check whether the nested bodies actually close over the enclosing scope — walk each body's `ast.Name` nodes **excluding the decorator list**, since the decorator always references the parent's app object and will otherwise fake a capture. Bodies that capture nothing are independent functions that merely happen to be lexically nested, so the aggregate describes nothing real — but a genuine violation can still hide inside it. Neither tool states the true fact alone; only `--show-closures` does.

**Why:** the failure is silent and inverts the usual risk direction — the gate reports green, the metric looks excellent, and the conclusion "our complexity is under control" is drawn from a scan that never read the code. **Anti-pattern in self:** asserting a mechanism ("radon scores nested defs as separate blocks") from a plausible reading of the output instead of testing the flag that would have falsified it in one command.

## A copied virtualenv keeps its old absolute shebangs — every console script silently runs the wrong interpreter

A venv is not relocatable. Every console script in `.venv/bin/` carries an **absolute** shebang naming the interpreter that created it, and the `activate*` scripts hard-code `VIRTUAL_ENV` the same way. Copy or move the directory — cloning a checkout with `cp -a`, duplicating a worktree, restoring a backup, renaming the parent folder — and all of them still point home. If that original path still exists you get a working but *wrong* environment; if it was deleted you get a fallback to whatever interpreter the system finds, usually the version manager's global one.

**Why it is hard to see:** the venv itself is fine. `pyvenv.cfg` is correct, `.venv/bin/python` resolves, `uv run python -c "import <dep>"` succeeds, and a tool runner reports the right venv path when asked. Only the *console-script* entry points are broken, so `uv run <tool>` fails while `uv run python -m <tool>` succeeds — in the same shell, same second. The resulting `ModuleNotFoundError` for a dependency that is demonstrably installed reads as a packaging or dependency bug and sends you into the lockfile.

**Discriminator (one command, no guessing):** run the tool both ways and compare the interpreter each reports. `pytest` prints it in its own header (`platform … -- /path/to/python`); most tools have a `--version`/verbose equivalent, else `head -1 .venv/bin/<tool>`. Same interpreter → the dependency really is missing. Different → the scripts are stale. Confirm the blast radius with `grep -l '<old-path>' .venv/bin/* | wc -l`.

**`uv sync` / `pip install -e .` will NOT fix it.** They see a satisfied environment and never rewrite entry points. Either rewrite line 1 of every affected script to the current venv's python (fast, surgical — remember the `activate*` scripts too, they are the source of the stale exported `VIRTUAL_ENV` that makes every subsequent command warn), or delete `.venv` and re-create it (clean, slower).

**How to apply:** never copy a venv — recreate it (`uv sync`, `python -m venv`) in the destination. When setting up a new worktree, create its venv there rather than copying a sibling's. Treat a stale-`VIRTUAL_ENV` warning as a symptom to investigate, not noise to ignore. And when a gate prepends `.venv/bin` to `PATH` to pin tool versions, remember that pin is only as good as those shebangs — a copied venv makes the whole local CI gate run on the wrong interpreter while looking correct.

**Anti-pattern in self:** on seeing `uv run pytest` fail with a missing dependency, concluding "the runner falls through to the global tool on `PATH`" from `command -v` output — without checking what the runner *actually executed*. The runner had resolved the right script; the script's own first line was the lie. One look at the tool's reported interpreter would have settled it immediately.

## `uv run` from the wrong directory fails loudly and bootstraps a stray project silently

`uv run <cmd>` issued outside the project root (one directory too high, or from a script's own out-of-tree folder) does not simply error. It **creates a new uv project where you stood** — writing a `uv.lock` and a `.venv/` there — and only then fails on whatever path argument was wrong. The tell is the warning `No 'requires-python' value found in the workspace` preceding the real error.

The residue is asymmetric and that is what makes it bite later: `.venv/` is usually gitignored, so it sits there indefinitely shadowing nothing until some tool resolves against it; `uv.lock` at a non-project root usually is **not** ignored, so the next `git add -A` stages a lockfile for a project that does not exist.

**How to apply:** after any `uv` invocation that errored on a path, run `git status` and look for a stray `uv.lock`, and `ls -d .venv` in the directory you ran from. Delete both. Prefer `cd <project> && uv run …` as one command rather than relying on the shell's current directory — in agent harnesses the working directory persists between calls, so "it worked last time" is not evidence about where you are now.

**Why:** the failure that gets your attention (a missing test path) is not the failure that costs you — that one is silent, and its footprint outlives the session. Same shape as the copied-venv trap above: the environment looks fine and the wrong thing is one directory over.

## An "unused `type: ignore`" on a suspicious line means two checkers disagree — re-derive the type, don't delete the comment

mypy's pydantic plugin can silently accept a plain `str` argument for a `Literal[...]`-typed pydantic field — and when a defensive `# type: ignore[arg-type]` is added to that line, mypy reports the ignore itself as **unused**, inviting you to delete it and move on. Pyright, checking the same line independently, flags the real `reportArgumentType` error. The line was genuinely type-unsafe; one checker's plugin just couldn't see it.

**How to apply:** treat "unused ignore" on a line that *looks* type-unsafe as a checker-divergence signal, not as confirmation the code is fine. Re-derive the correct static type at the source instead: pass the literal value directly where the invariant guarantees it (with a comment naming the guard that makes it safe), or narrow `str → Literal` once inside the producing function — never by widening the contract or trusting an ignore one checker calls dead. When an IDE/harness surfaces Pyright diagnostics alongside mypy, read them: they catch pydantic-plugin blind spots.

**Sibling trap, same family:** constructing strictly-typed pydantic models via `Model(**shared_dict)` in tests defeats per-parameter checking — a generic dict's values cannot be narrowed to each constructor parameter's type, so strict mypy either errors unhelpfully or (with plugins) checks nothing. Use a typed helper function with explicit keyword-argument overrides for test-object construction; reserve `# type: ignore` for the tests that deliberately violate the contract (extra-field / frozen-assignment probes).

**Why:** the failure is inverted trust — the tool's own "this suppression is unnecessary" message is what talks you into removing the only marker of a real bug. Measured case: a `str`-typed value flowing into a `Literal`-typed field passed a strict-mypy gate for a full increment; caught only because Pyright ran independently.
