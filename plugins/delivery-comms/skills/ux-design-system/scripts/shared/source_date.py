#!/usr/bin/env python3
"""The date a render stamps on its output, taken from its sources, never from the clock.

Order: `SOURCE_DATE_EPOCH` (reproducible-builds.org), else the newest last-commit date of the sources
themselves (a source file, or every file under a source folder), else the newest modification time of the
source files. The same sources give the same date on every run, so a re-render of unchanged sources changes
no byte. The commit date is the sources' own, not their folder's: an output written beside its source (a
release note's pdf/ folder) and then committed must not move the date of the next render.
"""
import datetime
import os
import subprocess


class SourceDateError(ValueError):
    """SOURCE_DATE_EPOCH is set but is not a whole number of seconds."""


def _files(paths):
    for path in paths:
        if os.path.isdir(path):
            for top, dirs, names in os.walk(path):
                dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                yield from (os.path.join(top, n) for n in sorted(names))
        elif os.path.isfile(path):
            yield path


def _last_commit(path):
    """Unix time of the last commit touching `path` (a file, or anything under a folder), or None outside a
    repository, for a path git does not track, or without git."""
    path = os.path.abspath(path)
    folder, spec = (path, ".") if os.path.isdir(path) else (os.path.dirname(path), os.path.basename(path))
    try:
        done = subprocess.run(["git", "-C", folder, "log", "-1", "--format=%ct", "--", spec],
                              capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    out = done.stdout.strip()
    return int(out) if done.returncode == 0 and out.isdigit() else None


def source_datetime(paths):
    """A timezone-aware UTC datetime for `paths` (source files or folders), per the order above."""
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch is not None and epoch.strip():
        if not epoch.strip().isdigit():
            raise SourceDateError(f"SOURCE_DATE_EPOCH must be a whole number of seconds, got {epoch!r}")
        stamp = int(epoch)
    else:
        commits = [t for t in (_last_commit(p) for p in sorted(set(map(str, paths))) if os.path.exists(p))
                   if t is not None]
        mtimes = [os.path.getmtime(f) for f in _files(paths)]
        stamp = max(commits) if commits else int(max(mtimes)) if mtimes else 0
    return datetime.datetime.fromtimestamp(stamp, tz=datetime.timezone.utc)


def source_date(paths):
    """The UTC calendar date of `source_datetime(paths)`."""
    return source_datetime(paths).date()
