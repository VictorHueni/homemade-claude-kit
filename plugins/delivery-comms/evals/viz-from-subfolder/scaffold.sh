#!/usr/bin/env bash
# Stage this case's scratch project in the eval run's working directory (claude plugin eval --scaffold):
# the case fixture, the kit's fictitious `full` design system as the folder the pin names, and the
# com-artefact-viz sample capability map in docs/strategy/.
set -euo pipefail
case_dir=$(cd "$(dirname "$0")" && pwd)
plugin=$(cd "$case_dir/../.." && pwd)
cp -R "$case_dir/fixture/." .
mkdir -p docs/ux/design-system docs/strategy
cp -R "$plugin/tests/fixtures/design-systems/full/." docs/ux/design-system/
cp "$plugin/skills/com-artefact-viz/examples/capability-map.sample.md" docs/strategy/capability-map.md
