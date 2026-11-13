#!/usr/bin/env bash
# Exercises the arch-plantuml pipeline against throwaway folders: scaffolds as `init` does, renders, and
# checks the two variants, the palette, the folder argument and what a render leaves behind.
# Needs Docker and pulls the pinned image; skips with a message when Docker is absent.
# Run: scripts/test-arch-plantuml.sh
set -uo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL="$KIT/plugins/architecture/skills/arch-plantuml"
RESOLVER="$KIT/plugins/delivery-comms/shared/design_source.py"

if ! docker version >/dev/null 2>&1; then
    echo "test-arch-plantuml: SKIP, Docker is not available"
    exit 0
fi

PIN="$(grep -oE '`[0-9]+\.[0-9]{4}\.[0-9]+`' "$SKILL/references/docker-pipeline.md" | head -1 | tr -d '`')"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

failures=0
check() {
    local desc="$1"; shift
    if "$@"; then echo "  ok   $desc"; else echo "  FAIL $desc"; failures=$(( failures + 1 )); fi
}

# What `init DIR` does: the theme, the palette, the seed diagram and the pinned render script.
scaffold() {
    mkdir -p "$1"
    cp "$SKILL/templates/diagrams/_theme.puml" "$SKILL/templates/diagrams/_palette.puml" \
       "$SKILL/templates/diagrams/seq-00-example.puml" "$1/"
    sed "s/{{plantuml_version}}/$PIN/" "$SKILL/templates/render.sh" > "$1/render.sh"
    chmod +x "$1/render.sh"
}

# One small diagram of each type the pipeline renders, so the theme is checked on every one.
probes() {
    printf '@startuml\n!include _theme.puml\ntitle Class probe\npackage "Group" {\n  class Order {\n    +id: String\n    +total(): Money\n  }\n  interface Priced\n}\nOrder ..|> Priced\nnote right of Order : a note\n@enduml\n' > "$1/class-01-probe.puml"
    printf '@startuml\n!include _theme.puml\ntitle State probe\n[*] --> Open\nOpen --> Closed : close\nClosed --> [*]\n@enduml\n' > "$1/state-01-probe.puml"
    printf '@startuml\n!include _theme.puml\ntitle Activity probe\nstart\nif (valid?) then (yes)\n  :accept;\nelse (no)\n  :reject;\nendif\nstop\n@enduml\n' > "$1/act-01-probe.puml"
    printf '@startuml\n!include _theme.puml\ntitle ER probe\nentity "order" as o {\n  *id : bigint\n  --\n  total : numeric\n}\nentity "line" as l {\n  *id : bigint\n}\no ||--o{ l\n@enduml\n' > "$1/er-01-probe.puml"
    printf '@startuml\n!include _theme.puml\ntitle Use case probe\nactor Customer\nrectangle Shop {\n  usecase "Place an order" as UC1\n}\nCustomer --> UC1\n@enduml\n' > "$1/uc-01-probe.puml"
}

# variable FILE light|dark NAME: the value of a palette variable in one branch.
variable() { awk -v branch="$2" -v name="$3" '
    /^!ifdef DARK/ { cur = "dark" } /^!else/ { cur = "light" }
    cur == branch && $1 == "!$" name { gsub(/"/, "", $3); print $3 }' "$1"; }
canvas_of() { grep -oiE 'background:#[0-9a-f]{6}' "$1" | head -1 | cut -d: -f2 | tr 'a-f' 'A-F'; }
has_colour() { grep -qi "$2" "$1"; }
# PlantUML's own black and near-black defaults; a fully transparent hit area does not count.
no_black() { ! grep -oE '<[a-z]+ [^>]*>' "$1" | grep -v 'fill-opacity="0\.0*"' | grep -qiE '#000000|#181818|#222222'; }
listing() { (cd "$1" && find . -mindepth 1 | sort); }

DIAGRAMS=(seq-00-example class-01-probe state-01-probe act-01-probe er-01-probe uc-01-probe)

echo "another folder than the default, outside a git repository"
DIR="$WORK/some/other/folder"
scaffold "$DIR"
probes "$DIR"
out="$("$DIR/render.sh" 2>&1)"; code=$?
check "render exits 0"                               test "$code" -eq 0
[[ $code -eq 0 ]] || echo "$out" | tail -n 15
for d in "${DIAGRAMS[@]}"; do
    check "$d has a light variant"                   test -s "$DIR/views/$d.svg"
    check "$d has a dark variant"                    test -s "$DIR/views/dark/$d.svg"
    check "$d dark variant has no black mark"        no_black "$DIR/views/dark/$d.svg"
done
light_canvas="$(variable "$DIR/_palette.puml" light canvas)"
dark_canvas="$(variable "$DIR/_palette.puml" dark canvas)"
check "the palette gives two different canvases"     test -n "$light_canvas" -a -n "$dark_canvas" -a "$light_canvas" != "$dark_canvas"
check "the light variant sits on the light canvas"   test "$(canvas_of "$DIR/views/class-01-probe.svg")" = "${light_canvas^^}"
check "the dark variant sits on the dark canvas"     test "$(canvas_of "$DIR/views/dark/class-01-probe.svg")" = "${dark_canvas^^}"
check "the head colour of each variant is drawn"     has_colour "$DIR/views/class-01-probe.svg" "$(variable "$DIR/_palette.puml" light head)"
check "the dark head colour is drawn"                has_colour "$DIR/views/dark/class-01-probe.svg" "$(variable "$DIR/_palette.puml" dark head)"
check "includes are never rendered"                  test ! -e "$DIR/views/_theme.svg" -a ! -e "$DIR/views/_palette.svg"
expected="$( { printf './%s\n' _palette.puml _theme.puml render.sh views views/dark
              for d in "${DIAGRAMS[@]}"; do printf './%s\n' "$d.puml" "views/$d.svg" "views/dark/$d.svg"; done; } | sort)"
check "a render leaves nothing it did not declare"   test "$(listing "$DIR")" = "$expected"
[[ "$(listing "$DIR")" = "$expected" ]] || diff <(echo "$expected") <(listing "$DIR")

echo "a palette from a design changes both variants, the theme untouched"
theme_before="$(sha256sum < "$DIR/_theme.puml")"
cat > "$DIR/_palette.puml" <<'EOF'
!ifdef DARK
!$canvas = "#101820"
!$panel = "#1B2733"
!$border = "#3B4A5A"
!$head = "#7A1F5C"
!$head_ink = "#FFF4FB"
!$ink = "#EDE7F0"
!$muted = "#B9AFC0"
!$accent = "#E58CC8"
!$success = "#5FD39A"
!$warning = "#F5B75C"
!$danger = "#FF8A80"
!$info = "#6CC4FF"
!else
!$canvas = "#FAF0E6"
!$panel = "#F0E2D0"
!$border = "#C9B79F"
!$head = "#5C1F7A"
!$head_ink = "#FFFFFF"
!$ink = "#2A1F33"
!$muted = "#6B5A78"
!$accent = "#5C1F7A"
!$success = "#027A48"
!$warning = "#B54708"
!$danger = "#B42318"
!$info = "#0E7090"
!endif
EOF
"$DIR/render.sh" > /dev/null 2>&1
check "the light canvas follows the palette"         test "$(canvas_of "$DIR/views/class-01-probe.svg")" = "#FAF0E6"
check "the dark canvas follows the palette"          test "$(canvas_of "$DIR/views/dark/class-01-probe.svg")" = "#101820"
check "the light head follows the palette"           has_colour "$DIR/views/class-01-probe.svg" "#5C1F7A"
check "the dark head follows the palette"            has_colour "$DIR/views/dark/class-01-probe.svg" "#7A1F5C"
check "the theme was not edited"                     test "$(sha256sum < "$DIR/_theme.puml")" = "$theme_before"

echo "the arguments and exit codes of render.sh"
rm -rf "$DIR/views"
"$DIR/render.sh" --dry-run > /dev/null 2>&1
check "--dry-run exits 0"                            test $? -eq 0
check "--dry-run renders nothing"                    test ! -e "$DIR/views"
"$DIR/render.sh" class-01-probe > /dev/null 2>&1
check "one diagram by name exits 0"                  test $? -eq 0
check "only that diagram is rendered, light"         test "$(ls "$DIR/views" | grep -c '\.svg$')" -eq 1 -a -s "$DIR/views/class-01-probe.svg"
check "only that diagram is rendered, dark"          test "$(ls "$DIR/views/dark" | grep -c '\.svg$')" -eq 1 -a -s "$DIR/views/dark/class-01-probe.svg"
"$DIR/render.sh" no-such-diagram > /dev/null 2>&1
check "an unknown diagram exits 4"                   test $? -eq 4
printf '@startuml\n!include _theme.puml\nthis is not plantuml ->\n@enduml\n' > "$DIR/seq-99-broken.puml"
"$DIR/render.sh" > /dev/null 2>&1
check "a diagram that does not parse exits 1"        test $? -eq 1
rm "$DIR/seq-99-broken.puml"

echo "the default folder, inside a git repository"
REPO="$WORK/repo"
scaffold "$REPO/docs/architecture/diagrams"
git -C "$REPO" init -q
"$REPO/docs/architecture/diagrams/render.sh" > /dev/null 2>&1
check "render exits 0"                               test $? -eq 0
check "the seed diagram has both variants"           test -s "$REPO/docs/architecture/diagrams/views/seq-00-example.svg" -a -s "$REPO/docs/architecture/diagrams/views/dark/seq-00-example.svg"
check "nothing is written outside the folder"        test -z "$(git -C "$REPO" status --porcelain --untracked-files=all | grep -v ' docs/architecture/diagrams/')"

echo "the scaffolded palette is the palette of the kit base theme"
if [[ -f "$RESOLVER" ]] && command -v python3 > /dev/null; then
    mkdir -p "$WORK/empty"
    check "the template equals the resolver's output"  diff -q <(python3 -B "$RESOLVER" plantuml --from "$WORK/empty") "$SKILL/templates/diagrams/_palette.puml"
else
    echo "  skip (no resolver or no python3)"
fi

echo
if [[ $failures -eq 0 ]]; then echo "test-arch-plantuml: all checks passed"; else echo "test-arch-plantuml: $failures check(s) failed"; fi
exit $(( failures > 0 ))
