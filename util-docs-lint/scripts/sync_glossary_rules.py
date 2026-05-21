#!/usr/bin/env python3
"""Generate .vale/styles/Local/GlossaryAliases.yml from docs/domain/glossary.md.

Reads GT-NN entries, extracts deprecated aliases, and emits a Vale
substitution rule so Vale flags alias usage and suggests the canonical term.
"""

import re
import sys
from pathlib import Path

GLOSSARY = Path("docs/domain/glossary.md")
OUT = Path(".vale/styles/Local/GlossaryAliases.yml")

if not GLOSSARY.exists():
    print("No glossary found — skipping alias rule generation.")
    sys.exit(0)

content = GLOSSARY.read_text(encoding="utf-8")
blocks = re.split(r"\n### ", content)
pairs: list[tuple[str, str]] = []

for block in blocks:
    heading = re.match(r"GT-\d+\s+[—–-]\s+(.+)", block)
    if not heading:
        continue
    canonical = heading.group(1).strip()
    aliases_match = re.search(r"\*\*[Dd]eprecated aliases?:\*\*\s*(.+)", block)
    if not aliases_match:
        continue
    for alias in aliases_match.group(1).split(","):
        alias = alias.strip()
        if alias:
            pairs.append((alias.lower(), canonical))

OUT.parent.mkdir(parents=True, exist_ok=True)

if not pairs:
    # Write an inert stub so Vale doesn't error on missing Local style
    OUT.write_text(
        "extends: existence\n"
        "message: \"Deprecated alias found.\"\n"
        "level: warning\n"
        "tokens: []\n",
        encoding="utf-8",
    )
    print("No deprecated aliases in glossary — wrote inert stub.")
    sys.exit(0)

lines = [
    "extends: substitution",
    "message: \"Use '%s' instead of '%s'.\"",
    "level: warning",
    "ignorecase: true",
    "swap:",
]
for alias, canonical in pairs:
    # Quote keys that contain spaces or special characters
    key = f'"{alias}"' if any(c in alias for c in " :-/()") else alias
    lines.append(f"  {key}: {canonical}")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Generated {OUT} with {len(pairs)} alias substitution(s).")
