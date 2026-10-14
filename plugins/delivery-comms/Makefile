# delivery-comms test lane. Needs Python 3.12+ and PyYAML; test-pdf also needs Playwright and Chromium.
PYTHON ?= python3
UNITTEST = cd tests && PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -B -m unittest

.PHONY: test test-pdf check-python

check-python:
	@$(PYTHON) -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else "delivery-comms tests need Python 3.12 or later")'
	@$(PYTHON) -c 'import yaml' 2>/dev/null || { echo "PyYAML missing: pip install pyyaml"; exit 1; }

# Unit tests, no browser.
test: check-python
	$(UNITTEST) -v test_characterisation test_contract test_resolver test_validator test_slide_deck test_artefact_viz test_release_note test_reproducible

# PDF renders. A missing browser skips locally and fails when CI=true.
test-pdf: check-python
	$(UNITTEST) -v test_pdf
