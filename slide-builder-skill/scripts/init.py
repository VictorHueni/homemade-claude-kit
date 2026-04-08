#!/usr/bin/env python3
"""
Slide Builder - Init
====================
Scaffolds a new slide deck project at a target directory.

Creates the folder structure, copies templates from the skill,
and writes a config.yaml ready to edit.

Usage:
    python init.py ./my-presentation
    python init.py ./my-presentation --name "My Talk"
    python init.py ./my-presentation --name "My Talk" --author "Jane Doe"
"""

import argparse
import shutil
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"


def init_project(target: Path, name: str = "", author: str = ""):
    if target.exists() and any(target.iterdir()):
        print(f"[WARN] Target directory is not empty: {target}")
        print("       Existing files will NOT be overwritten.\n")

    # Create folder structure
    dirs = [
        "context",
        "design",
        "output/slide-deck",
        "output/slides",
        "output/prototypes",
    ]
    for d in dirs:
        (target / d).mkdir(parents=True, exist_ok=True)

    # Copy templates (never overwrite existing files)
    copies = [
        ("brief-template.md", "context/brief-template.md"),
        ("brief-template.md", "context/brief.md"),
        ("design-system-template.md", "design/design-system-template.md"),
        ("design-system-template.md", "design/design-system.md"),
        ("config-template.yaml", "config.yaml"),
    ]

    for src_name, dest_rel in copies:
        src = TEMPLATES_DIR / src_name
        dest = target / dest_rel
        if dest.exists():
            print(f"  [SKIP] {dest_rel} (already exists)")
            continue
        if not src.exists():
            print(f"  [WARN] Template not found: {src}")
            continue
        shutil.copy2(src, dest)
        print(f"  [NEW]  {dest_rel}")

    # Create empty placeholder files (so the folder isn't empty in Git)
    placeholders = [
        ("design/styles.css", "/* Design tokens and component styles go here */\n"),
        ("design/script.js", "// Presentation mode, icon init, and helpers go here\n"),
    ]
    for rel, content in placeholders:
        path = target / rel
        if path.exists():
            print(f"  [SKIP] {rel} (already exists)")
        else:
            path.write_text(content, encoding="utf-8")
            print(f"  [NEW]  {rel}")

    # Patch config.yaml with name/author if provided
    config_path = target / "config.yaml"
    if config_path.exists() and (name or author):
        text = config_path.read_text(encoding="utf-8")
        if name:
            text = text.replace('title: "Presentation Title"', f'title: "{name}"')
        if author:
            text = text.replace('author: "Author"', f'author: "{author}"')
        config_path.write_text(text, encoding="utf-8")

    # Print summary
    skill_rel = SKILL_DIR
    print(f"\n[DONE] Project scaffolded at: {target}")
    print(f"\nNext steps:")
    print(f"  1. Fill in  {target / 'context/brief.md'}")
    print(f"  2. Fill in  {target / 'design/design-system.md'}")
    print(f"  3. Create slides in  {target / 'output/slides/'}")
    print(f"  4. Build with:")
    print(f"       python {skill_rel / 'scripts/build.py'} --config {target / 'config.yaml'}")


def main():
    parser = argparse.ArgumentParser(
        description="Scaffold a new slide deck project."
    )
    parser.add_argument(
        "target",
        help="Target directory for the new project",
    )
    parser.add_argument(
        "--name", "-n",
        default="",
        help="Presentation title (written into config.yaml)",
    )
    parser.add_argument(
        "--author", "-a",
        default="",
        help="Author name (written into config.yaml)",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    init_project(target, name=args.name, author=args.author)


if __name__ == "__main__":
    main()
