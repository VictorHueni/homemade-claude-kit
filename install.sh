#!/usr/bin/env bash
# ─────────────────────────────────────────────
# Homemade Agent Skills — Install / Sync
# ─────────────────────────────────────────────
# Usage:
#   ./install.sh                  # symlink all skills to ~/.claude/skills/
#   ./install.sh /path/to/project # symlink all skills into a project's .claude/skills/
#
# Run again after git pull to pick up new skills automatically.
# ─────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine target directory
if [[ $# -ge 1 ]]; then
    TARGET="$1/.claude/skills"
    echo "Installing skills into project: $1"
else
    TARGET="$HOME/.claude/skills"
    echo "Installing skills globally: $TARGET"
fi

mkdir -p "$TARGET"

# Find all skill directories (contain a SKILL.md)
installed=0
for skill_dir in "$SCRIPT_DIR"/*/; do
    skill_name="$(basename "$skill_dir")"

    # Skip if no SKILL.md (not a real skill)
    [[ -f "$skill_dir/SKILL.md" ]] || continue

    link="$TARGET/$skill_name"

    # Remove existing (stale symlink or old copy)
    if [[ -L "$link" ]]; then
        rm "$link"
    elif [[ -d "$link" ]]; then
        echo "  ⚠ $skill_name: replacing embedded copy with symlink"
        rm -rf "$link"
    fi

    ln -s "$skill_dir" "$link"
    echo "  ✓ $skill_name → $skill_dir"
    installed=$((installed + 1))
done

echo ""
echo "Done. $installed skill(s) linked to $TARGET"
