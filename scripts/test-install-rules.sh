#!/usr/bin/env bash
# Exercises install.sh's rule layers against a throwaway mini-kit, so no real
# ~/.claude, var/ state or kit file is touched. Run: scripts/test-install-rules.sh
set -uo pipefail

KIT_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

KIT="$WORK/kit"
PROJ="$WORK/proj"
RULES="$PROJ/.claude/rules"
mkdir -p "$KIT/rules/personal" "$KIT/plugins/demo/skills/demo-skill" "$PROJ"
cp "$KIT_SRC/install.sh" "$KIT/"
printf -- '---\ntype: rule\n---\nshared\n' > "$KIT/rules/shared-a.md"
printf -- '---\ntype: rule\n---\nshared\n' > "$KIT/rules/shared-b.md"
printf -- '---\ntype: rule\n---\npersonal\n' > "$KIT/rules/personal/mine.md"
printf -- '---\nname: demo-skill\n---\n' > "$KIT/plugins/demo/skills/demo-skill/SKILL.md"

failures=0
check() {
    local desc="$1"; shift
    if "$@"; then echo "  ok   $desc"; else echo "  FAIL $desc"; failures=$(( failures + 1 )); fi
}
is_link_to() { [[ -L "$1" ]] && [[ "$(realpath "$1")" == "$(realpath "$2")" ]]; }
run() { "$KIT/install.sh" "$@" "$PROJ" 2>&1; }

echo "personal layer on"
mkdir -p "$RULES"
printf 'plain local copy\n' > "$RULES/shared-a.md"
run --personal-rules on > /dev/null
check "plain file replaced by a link"           is_link_to "$RULES/shared-a.md" "$KIT/rules/shared-a.md"
check "shared rule linked"                      is_link_to "$RULES/shared-b.md" "$KIT/rules/shared-b.md"
check "personal rule linked flat"               is_link_to "$RULES/mine.md" "$KIT/rules/personal/mine.md"
check "no personal/ subfolder in target"        test ! -e "$RULES/personal"
check "setting persisted in var/"               grep -qx on "$KIT/var/personal-rules"

echo "idempotent re-run (setting read back)"
out="$(run)"
check "second run reports No changes"           grep -qx 'No changes.' <<<"$out"
check "personal rule still linked"              is_link_to "$RULES/mine.md" "$KIT/rules/personal/mine.md"

echo "rule removed from the kit"
rm "$KIT/rules/shared-b.md"
run > /dev/null
check "its link is pruned"                      test ! -e "$RULES/shared-b.md" -a ! -L "$RULES/shared-b.md"
check "personal link survives the prune"        is_link_to "$RULES/mine.md" "$KIT/rules/personal/mine.md"

echo "personal layer off"
run --personal-rules off > /dev/null
check "personal link pruned"                    test ! -L "$RULES/mine.md"
check "shared link kept"                        is_link_to "$RULES/shared-a.md" "$KIT/rules/shared-a.md"

echo "default for a fresh machine is off"
rm -f "$KIT/var/personal-rules"; rm -rf "$RULES"
run > /dev/null
check "no personal link without opt-in"         test ! -L "$RULES/mine.md"

echo "name collision between layers"
cp "$KIT/rules/personal/mine.md" "$KIT/rules/mine.md"
run --personal-rules on > /dev/null; rc=$?
check "install refuses (non-zero exit)"         test "$rc" -ne 0
rm "$KIT/rules/mine.md"

echo "invalid value"
run --personal-rules maybe > /dev/null; rc=$?
check "rejected with non-zero exit"             test "$rc" -ne 0

if (( failures > 0 )); then echo "$failures check(s) failed"; exit 1; fi
echo "all checks passed"
