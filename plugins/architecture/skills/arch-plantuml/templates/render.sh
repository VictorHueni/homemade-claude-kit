#!/usr/bin/env bash
#
# Render the PlantUML diagrams of this folder (*.puml) to SVG, in a light
# and a dark variant: views/*.svg and views/dark/*.svg.
#
# Single-image pipeline using the official plantuml/plantuml CLI image
# (https://hub.docker.com/r/plantuml/plantuml — bundles plantuml.jar +
# a JRE + Graphviz):
#
#   1. validate every .puml with -checkonly (parse, no output)
#   2. render each to SVG with -tsvg, light
#   3. render each again with -DDARK=1, which selects the dark branch
#      of _palette.puml
#
# Files whose name starts with `_` (e.g. _theme.puml, _palette.puml) are
# INCLUDE fragments, not diagrams — they are never rendered.
#
# Pinned version is kit-maintained — bump via `arch-plantuml upgrade`.
# Do NOT use `:latest` — reproducibility matters.
#
# Usage:
#   ./render.sh                  Render all diagrams, both variants
#   ./render.sh <diagram-name>   Render a single diagram (stem or filename)
#   ./render.sh --dry-run        Validate (-checkonly) + confirm Docker; no render
#
# Exit codes:
#   0  All steps succeeded
#   1  A .puml failed validation
#   2  Docker not available
#   3  Render failed
#   4  No renderable diagrams found

set -euo pipefail
shopt -s nullglob

# ─── Pinned image (bump via `arch-plantuml upgrade`) ──────────────────
PLANTUML_VERSION="{{plantuml_version}}"
IMAGE="plantuml/plantuml:${PLANTUML_VERSION}"

# ─── UID/GID — write SVGs as the invoking user, not root ──────────────
DOCKER_USER="$(id -u):$(id -g)"

# ─── Paths ────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# The mount is the git repository when there is one, else this folder itself,
# so the script works wherever the diagrams live.
if REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel 2>/dev/null)" && [[ -n "${REPO_ROOT}" ]]; then
    :
else
    REPO_ROOT="${SCRIPT_DIR}"
fi
DIAGRAMS_DIR_REL="$(realpath --relative-to="${REPO_ROOT}" "${SCRIPT_DIR}")"
VIEWS_DIR_CONTAINER="/work/${DIAGRAMS_DIR_REL}/views"

DRY_RUN=0
DIAGRAM_NAME=""
for arg in "$@"; do
    case "${arg}" in
        --dry-run) DRY_RUN=1 ;;
        --help|-h)
            sed -n '3,31p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'
            exit 0
            ;;
        *) DIAGRAM_NAME="${arg}" ;;
    esac
done

# ─── 0. Docker availability ───────────────────────────────────────────
if ! docker version >/dev/null 2>&1; then
    echo "ERROR: docker not available. Install Docker and ensure the daemon is running." >&2
    exit 2
fi

# ─── 1. Collect renderable files (exclude _*.puml includes) ───────────
# Build a list of container-side paths (/work/...). The host glob expands
# here; each match is mapped to its path inside the mounted /work volume.
declare -a CONTAINER_FILES=()
for f in "${SCRIPT_DIR}"/*.puml; do
    base="$(basename "${f}")"
    [[ "${base}" == _* ]] && continue                      # skip include fragments
    if [[ -n "${DIAGRAM_NAME}" ]]; then
        # Match either "seq-01-foo" or "seq-01-foo.puml"
        [[ "${base}" == "${DIAGRAM_NAME}" || "${base}" == "${DIAGRAM_NAME}.puml" ]] || continue
    fi
    CONTAINER_FILES+=("/work/${DIAGRAMS_DIR_REL}/${base}")
done

if [[ ${#CONTAINER_FILES[@]} -eq 0 ]]; then
    if [[ -n "${DIAGRAM_NAME}" ]]; then
        echo "ERROR: no diagram matching '${DIAGRAM_NAME}'. Available:" >&2
    else
        echo "ERROR: no renderable .puml files in ${DIAGRAMS_DIR_REL}/ (only _*.puml includes?)." >&2
    fi
    for f in "${SCRIPT_DIR}"/*.puml; do
        base="$(basename "${f}")"; [[ "${base}" == _* ]] && continue
        echo "  ${base%.puml}" >&2
    done
    exit 4
fi

# ─── 2. Validate (parse only) ─────────────────────────────────────────
echo "→ Validating ${#CONTAINER_FILES[@]} diagram(s) (${IMAGE})"
if ! docker run --rm --user "${DOCKER_USER}" -v "${REPO_ROOT}:/work" "${IMAGE}" \
        -checkonly -failfast2 "${CONTAINER_FILES[@]}"; then
    echo "ERROR: a .puml failed validation. Fix it before re-rendering." >&2
    exit 1
fi

if [[ "${DRY_RUN}" == "1" ]]; then
    echo "✓ Dry-run passed. All diagrams parse; Docker available. No render performed."
    exit 0
fi

# ─── 3. Render to SVG, light then dark ────────────────────────────────
mkdir -p "${SCRIPT_DIR}/views/dark"

echo "→ Rendering to SVG → ${DIAGRAMS_DIR_REL}/views/ (light) and views/dark/"
if ! docker run --rm --user "${DOCKER_USER}" -v "${REPO_ROOT}:/work" "${IMAGE}" \
        -tsvg -failfast2 -o "${VIEWS_DIR_CONTAINER}" "${CONTAINER_FILES[@]}"; then
    echo "ERROR: render failed." >&2
    exit 3
fi
if ! docker run --rm --user "${DOCKER_USER}" -v "${REPO_ROOT}:/work" "${IMAGE}" \
        -tsvg -failfast2 -DDARK=1 -o "${VIEWS_DIR_CONTAINER}/dark" "${CONTAINER_FILES[@]}"; then
    echo "ERROR: dark render failed." >&2
    exit 3
fi

# ─── 4. Report ────────────────────────────────────────────────────────
echo
echo "✓ Rendered views (each also in views/dark/):"
find "${SCRIPT_DIR}/views" -maxdepth 1 -name '*.svg' -printf '  %f\n' | sort

echo
echo "Embed in markdown via:  ![diagram-name](views/<diagram-name>.svg)  (dark: views/dark/<diagram-name>.svg)"
