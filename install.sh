#!/usr/bin/env bash
# ─────────────────────────────────────────────
# Homemade Agent Skills — Install / Sync
# ─────────────────────────────────────────────
# Usage:
#   ./install.sh                  # symlink all skills & commands to ~/.claude/
#   ./install.sh /path/to/project # symlink into a project's .claude/
#
# Run again after git pull to pick up new skills or commands automatically.
# ─────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine target base directory
if [[ $# -ge 1 ]]; then
    BASE="$1/.claude"
    echo "Installing into project: $1"
else
    BASE="$HOME/.claude"
    echo "Installing globally: $BASE"
fi

SKILLS_TARGET="$BASE/skills"
COMMANDS_TARGET="$BASE/commands"

mkdir -p "$SKILLS_TARGET" "$COMMANDS_TARGET"

# ── Skills: each top-level dir containing SKILL.md → symlinked directory
installed_skills=0
for skill_dir in "$SCRIPT_DIR"/*/; do
    skill_name="$(basename "$skill_dir")"

    # Skip if no SKILL.md (not a real skill)
    [[ -f "$skill_dir/SKILL.md" ]] || continue

    link="$SKILLS_TARGET/$skill_name"

    # Remove existing (stale symlink or old copy)
    if [[ -L "$link" ]]; then
        rm "$link"
    elif [[ -d "$link" ]]; then
        echo "  ⚠ $skill_name: replacing embedded copy with symlink"
        rm -rf "$link"
    fi

    ln -s "$skill_dir" "$link"
    echo "  ✓ skill:   $skill_name"
    installed_skills=$((installed_skills + 1))
done

# ── Commands: each *.md file in commands/ → symlinked file
installed_commands=0
if [[ -d "$SCRIPT_DIR/commands" ]]; then
    for cmd_file in "$SCRIPT_DIR/commands"/*.md; do
        # Handle empty commands/ directory (glob yields literal pattern)
        [[ -f "$cmd_file" ]] || continue

        cmd_name="$(basename "$cmd_file")"
        link="$COMMANDS_TARGET/$cmd_name"

        # Remove existing (stale symlink or plain file copy)
        if [[ -L "$link" ]] || [[ -f "$link" ]]; then
            rm "$link"
        fi

        ln -s "$cmd_file" "$link"
        echo "  ✓ command: $cmd_name"
        installed_commands=$((installed_commands + 1))
    done
fi

echo ""
echo "Done. $installed_skills skill(s) + $installed_commands command(s) linked to $BASE"
