#!/usr/bin/env python3
"""SessionStart hook: warn when Docker Desktop's context is active on WSL.

Stdout reaches the session as context. The tripwire on test commands repeats
the warning if the context comes back mid-session.
"""

from __future__ import annotations

import sys

from tripwires import DOCKER_CONTEXT_MESSAGE, docker_desktop_context_on_wsl


def main() -> int:
    if docker_desktop_context_on_wsl():
        print(f"WARNING: {DOCKER_CONTEXT_MESSAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
