#!/usr/bin/env python3
"""The path a render prints for a source, the same from any working directory and on any machine.

Relative to the root of the git repository that holds the source, else the file (or folder) name alone.
Never an absolute path and never a `../` climb, so an output neither depends on where it was rendered from
nor carries the user's home directory.
"""
import subprocess
from pathlib import Path


def _repo_root(folder):
    """The top level of the repository holding `folder`, or None outside one or without git."""
    try:
        done = subprocess.run(["git", "-C", str(folder), "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    out = done.stdout.strip()
    return Path(out).resolve() if done.returncode == 0 and out else None


def display_path(path):
    """`path` (a file or a folder) relative to its repository root, as a POSIX path, else its name."""
    path = Path(path).resolve()
    root = _repo_root(path if path.is_dir() else path.parent)
    if root is not None and root != path and root in path.parents:
        return path.relative_to(root).as_posix()
    return path.name
