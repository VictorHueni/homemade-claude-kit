#!/usr/bin/env bash
# ─────────────────────────────────────────────
# Homemade Agent Skills — Install / Sync
# ─────────────────────────────────────────────
# Usage:
#   ./install.sh                  # symlink all skills, commands & rules to ~/.claude/
#   ./install.sh /path/to/project # symlink into a project's .claude/
#
# Run again after git pull to pick up new skills or commands automatically.
# ─────────────────────────────────────────────

set -euo pipefail
shopt -s nullglob

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -ge 1 ]]; then
    BASE="$1/.claude"
    echo "Installing into project: $1"
else
    BASE="$HOME/.claude"
    echo "Installing globally: $BASE"
fi

SKILLS_TARGET="$BASE/skills"
COMMANDS_TARGET="$BASE/commands"
RULES_TARGET="$BASE/rules"

mkdir -p "$SKILLS_TARGET" "$COMMANDS_TARGET" "$RULES_TARGET"

# Sync *.md files from a source subdir: install symlinks + prune orphans.
# Usage: sync_files <src_subdir> <target_dir> <label> <installed_var> <pruned_var>
sync_files() {
    local src="$1" target="$2" label="$3"
    local -n _inst="$4" _prun="$5"

    [[ -d "$src" ]] || return 0

    for src_file in "$src"/*.md; do
        local name; name="$(basename "$src_file")"
        local link="$target/$name"
        ln -sf "$(realpath --relative-to="$(dirname "$link")" "$src_file")" "$link"
        echo "  ✓ $label: $name"
        _inst=$(( _inst + 1 ))
    done

    for link in "$target"/*.md; do
        local name; name="$(basename "$link")"
        if [[ -L "$link" ]] && [[ ! -f "$src/$name" ]]; then
            rm "$link"
            echo "  ✗ pruned $label: $name"
            _prun=$(( _prun + 1 ))
        fi
    done
}

# ── Skills: each top-level dir containing SKILL.md → symlinked directory
installed_skills=0
pruned_skills=0

for skill_dir in "$SCRIPT_DIR"/*/; do
    skill_name="$(basename "${skill_dir%/}")"
    [[ -f "$skill_dir/SKILL.md" ]] || continue

    link="$SKILLS_TARGET/$skill_name"
    if [[ -L "$link" ]]; then
        rm "$link"
    elif [[ -d "$link" ]]; then
        echo "  ⚠ $skill_name: replacing embedded copy with symlink"
        rm -rf "$link"
    fi

    ln -s "$(realpath --relative-to="$(dirname "$link")" "$skill_dir")" "$link"
    echo "  ✓ skill:   $skill_name"
    installed_skills=$(( installed_skills + 1 ))
done

for link in "$SKILLS_TARGET"/*; do
    skill_name="$(basename "$link")"
    if [[ -L "$link" ]] && [[ ! -d "$SCRIPT_DIR/$skill_name" ]]; then
        rm "$link"
        echo "  ✗ pruned skill:   $skill_name"
        pruned_skills=$(( pruned_skills + 1 ))
    fi
done

# ── Commands and Rules: *.md files symlinked from their source subdir
installed_commands=0; pruned_commands=0
installed_rules=0;    pruned_rules=0

sync_files "$SCRIPT_DIR/commands" "$COMMANDS_TARGET" "command" installed_commands pruned_commands
sync_files "$SCRIPT_DIR/rules"    "$RULES_TARGET"    "rule"    installed_rules    pruned_rules

echo ""
echo "Done. $installed_skills skill(s) + $installed_commands command(s) + $installed_rules rule(s) linked to $BASE"
echo "      $pruned_skills skill(s) + $pruned_commands command(s) + $pruned_rules rule(s) pruned."
