#!/usr/bin/env bash
# Stage this case's scratch project in the eval run's working directory (claude plugin eval --scaffold):
# the case fixture, a deck written before 2.1 whose styles.css draws its dark section slide with a deck-local
# palette (--dark-bg, --dark-text, --dark-highlight), then the kit's fictitious `full-dark` design system, which
# provides the dark module, as the folder the pin names.
set -euo pipefail
case_dir=$(cd "$(dirname "$0")" && pwd)
plugin=$(cd "$case_dir/../.." && pwd)
cp -R "$case_dir/fixture/." .
mkdir -p docs/ux/design-system
cp -R "$plugin/tests/fixtures/design-systems/full-dark/." docs/ux/design-system/
