#!/usr/bin/env bash
# Stage this case's scratch project in the eval run's working directory (claude plugin eval --scaffold):
# the case fixture and, as the project's only design source, the legacy 24-token file that
# ux-design-system ships as an example (refused by the 2.0 renderers). No pin.
set -euo pipefail
case_dir=$(cd "$(dirname "$0")" && pwd)
plugin=$(cd "$case_dir/../.." && pwd)
cp -R "$case_dir/fixture/." .
mkdir -p docs/ux
cp "$plugin/skills/ux-design-system/examples/legacy.tokens.css" docs/ux/tokens.css
