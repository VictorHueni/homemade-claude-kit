#!/usr/bin/env python3
"""Copy the canonical shared/ files into each renderer skill (scripts/shared/).

Each skill stays self-contained once installed, so the one implementation of the
base theme, the manifest checker and the contract is copied, never imported across
skills. `--check` copies nothing and exits 1 when any copy differs or is stale.
"""
import argparse
import filecmp
import shutil
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SKILLS = ("com-slide-deck", "com-artefact-viz", "com-release-note")
EXTRA = ("contract/modules.json", "contract/kit-manifest.schema.json")


def canonical():
    """Map of relative path in a skill's scripts/shared/ to its canonical source."""
    files = {p.relative_to(PLUGIN / "shared"): p for p in sorted((PLUGIN / "shared").rglob("*"))
             if p.is_file() and "__pycache__" not in p.parts}
    files.update({Path(Path(e).name): PLUGIN / e for e in EXTRA})
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="report differences, change nothing")
    check = ap.parse_args().check
    files, stale = canonical(), []
    for skill in SKILLS:
        target = PLUGIN / "skills" / skill / "scripts" / "shared"
        for rel, src in files.items():
            dest = target / rel
            if dest.is_file() and filecmp.cmp(src, dest, shallow=False):
                continue
            stale.append(str(dest.relative_to(PLUGIN)))
            if not check:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest)
        if target.is_dir():
            for have in sorted(p for p in target.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
                if have.relative_to(target) not in files:
                    stale.append(str(have.relative_to(PLUGIN)))
                    if not check:
                        have.unlink()
    for path in stale:
        print(("stale: " if check else "synced: ") + path)
    return 1 if check and stale else 0


if __name__ == "__main__":
    sys.exit(main())
