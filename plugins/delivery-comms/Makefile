# delivery-comms test lane. Needs Python 3.12+ and PyYAML; test-pdf also needs Playwright and Chromium;
# test-design-md also needs Node.js 18+ (npx) and the network.
PYTHON ?= python3
UNITTEST = cd tests && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -B -m unittest

# Google's DESIGN.md linter, pinned at an exact version (published 2026-07-27).
DESIGN_MD_LINTER ?= @google/design.md@0.4.0

.PHONY: test test-pdf test-design-md check-python skill-evals skill-evals-smoke

check-python:
	@$(PYTHON) -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else "delivery-comms tests need Python 3.12 or later")'
	@$(PYTHON) -c 'import yaml' 2>/dev/null || { echo "PyYAML missing: pip install pyyaml"; exit 1; }

# Unit tests, no browser.
test: check-python
	$(UNITTEST) -v test_characterisation test_contract test_resolver test_validator test_slide_deck test_artefact_viz test_release_note test_reproducible test_ux_design_system test_skill_evals

# PDF renders. A missing browser skips locally and fails when CI=true.
test-pdf: check-python
	$(UNITTEST) -v test_pdf

# Google's DESIGN.md linter on every DESIGN.md ux-design-system writes (template, sample, scaffold, proposal,
# --from-legacy draft): exit 0, no error, no warning. Not in `test`: it fetches the linter with npx.
test-design-md: check-python
	cd tests && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -B lint_design_md.py $(DESIGN_MD_LINTER)

# Skill evals (Plan-0005 increment 12): `claude plugin eval` runs the cases in evals/ (found through
# plugin.json experimental.evals), each case three times with the plugin and three times without it, and
# writes report.html and aggregate-result.json to var/skill-evals/<model>/ (gitignored). Each run calls a
# model on your account and costs money: never part of `test`, run it only when you mean to pay for it.
#   mise exec -- make -C plugins/delivery-comms skill-evals          full suite (5 cases x 3 runs x 2 arms)
#   mise exec -- make -C plugins/delivery-comms skill-evals-smoke    one case, one run, no baseline arm
# --scaffold runs each case's scaffold.sh (author-supplied bash, run as you) to stage its scratch project;
# --keep-temp keeps each run's sandbox (/tmp/claude-eval-*: home/cwd and out/trace.jsonl) so the traces can
# be read against the verdicts. SKILL_EVAL_ARGS passes extra flags, e.g. --case deck-pinned --runs 1.
# --max-cost-usd is checked before each run starts, so the overrun is at most the run in flight.
# The agent's python3 is the first one on PATH: run under `mise exec` so it is Python 3.12+ with PyYAML.
# Two WSL workarounds, harmless elsewhere: the eval sandbox refuses a PATH directory it cannot examine,
# so the /mnt/ entries (Windows interop) are dropped; and it refuses a ~/.docker credential store holding
# a symlink (Docker Desktop for WSL creates one), so claude runs with HOME set to a temporary directory
# that holds only links to the real ~/.claude and ~/.claude.json. The real HOME is never touched; the
# trap removes the two links and the directory, if claude left nothing else in it.
SKILL_EVAL_MODELS ?= sonnet
SKILL_EVAL_JUDGE ?= sonnet
SKILL_EVAL_MAX_COST ?= 20
SKILL_EVAL_ARGS ?=
SKILL_EVAL_SMOKE_CASE ?= deck-pinned
SKILL_EVAL_SMOKE_MAX_COST ?= 3

skill-evals: check-python
	@set -e; \
	eval_path=$$(printf '%s\n' "$$PATH" | tr ':' '\n' | grep -v '^/mnt/' | paste -sd: -); \
	PATH="$$eval_path" python3 -c 'import sys, yaml; sys.exit(0 if sys.version_info >= (3, 12) else "skill-evals: python3 on PATH is older than 3.12")'; \
	eval_home=$$(mktemp -d); \
	trap 'rm -f "$$eval_home/.claude" "$$eval_home/.claude.json"; rmdir "$$eval_home" 2>/dev/null || true' EXIT; \
	ln -s "$$HOME/.claude" "$$eval_home/.claude"; \
	ln -s "$$HOME/.claude.json" "$$eval_home/.claude.json"; \
	for model in $(SKILL_EVAL_MODELS); do \
		HOME="$$eval_home" PATH="$$eval_path" claude plugin eval . --model $$model \
			--judge-model $(SKILL_EVAL_JUDGE) --max-cost-usd $(SKILL_EVAL_MAX_COST) \
			--trust-plugin --no-publish --scaffold --keep-temp \
			--output-dir var/skill-evals/$$model \
			--allow-tools Write Edit "Bash(python3 *)" "Bash(mkdir *)" "Bash(cp *)" \
			$(SKILL_EVAL_ARGS); \
	done

# One case once, with the plugin only: the cheap check that the suite loads and the sandbox starts.
skill-evals-smoke:
	$(MAKE) skill-evals SKILL_EVAL_MAX_COST=$(SKILL_EVAL_SMOKE_MAX_COST) \
		SKILL_EVAL_ARGS="--case $(SKILL_EVAL_SMOKE_CASE) --runs 1 --ablation none"
