#!/usr/bin/env python3
"""PreToolUse hook on Write/Edit: classify a lesson before it lands in auto-memory.

The first write to a given memory file in a session is denied with the
checklist; the retry goes through, so the classification happens once per file.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

_MEMORY = re.compile(r"/\.claude/projects/[^/]+/memory/")

CHECKLIST = (
    "[tripwire memory-hygiene] Before writing auto-memory, decide where the lesson belongs. "
    "1. It applies to any future project (tool gotchas, conventions, working style): a rule in the kit repo "
    "(the checkout `install.sh` runs from), `rules/` for shared knowledge or `rules/personal/` for the owner's "
    "preferences and machine, with `type: rule` and `paths:` when only certain files need it; or a hook when it "
    "is about one command. Commit it on a branch and run `install.sh`; never write a plain file into "
    "`~/.claude/rules/`. Kit rules stay generic: no client, product or project names, no project paths, no domain jargon in examples. "
    "2. A collaborator on this repo needs it on day one: the project's `AGENTS.md`, or the nested one for that "
    "area. 3. Only otherwise, a fact about this codebase: project auto-memory. When in doubt, choose the wider "
    "scope. If memory is still right, retry the same write; it goes through."
)


def _marker(session: str, path: str) -> Path:
    digest = hashlib.sha256(f"{session}\0{path}".encode()).hexdigest()[:24]
    return Path(tempfile.gettempdir()) / f"kit-memory-ack-{os.getuid()}" / digest


def evaluate(payload: dict) -> dict | None:
    tool_input = payload.get("tool_input")
    path = tool_input.get("file_path") if isinstance(tool_input, dict) else None
    if not isinstance(path, str) or not _MEMORY.search(path) or path.endswith("/MEMORY.md"):
        return None
    session = payload.get("session_id") or payload.get("transcript_path")
    if not session:
        return None  # No session to scope the ack to; a per-path marker would silence it for good.
    marker = _marker(str(session), path)
    if marker.exists():
        return None
    try:
        marker.parent.mkdir(mode=0o700, exist_ok=True)
        marker.touch()
    except OSError:
        return None  # Without a marker the retry would be denied too; fail open.
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": CHECKLIST,
        }
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(payload, dict) or payload.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        return 0
    result = evaluate(payload)
    if result is not None:
        json.dump(result, sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
