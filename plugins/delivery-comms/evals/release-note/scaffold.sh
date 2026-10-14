#!/usr/bin/env bash
# Stage this case's scratch project in the eval run's working directory (claude plugin eval --scaffold):
# the case fixture (CHANGELOG.md and the pin), the kit's fictitious `full` design system as the folder
# the pin names, and an empty docs/release-notes/ (the folder com-release-note writes to when it exists).
set -euo pipefail
case_dir=$(cd "$(dirname "$0")" && pwd)
plugin=$(cd "$case_dir/../.." && pwd)
cp -R "$case_dir/fixture/." .
mkdir -p docs/ux/design-system docs/release-notes
cp -R "$plugin/tests/fixtures/design-systems/full/." docs/ux/design-system/
