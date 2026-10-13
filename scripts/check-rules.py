#!/usr/bin/env python3
"""Check the kit's rules against the size and style budget (kit ADR-0011).

Always-on rules (no ``paths:``) are sent with every request, so they carry the
tightest limits. Run: scripts/check-rules.py
"""

import re
import sys
from pathlib import Path

ALWAYS_ON_FILE_MAX = 3_000
ALWAYS_ON_TOTAL_MAX = 20_000
PATH_SCOPED_FILE_MAX = 4_000
# Restructured separately; remove from this set once it fits the budget.
SIZE_EXEMPT = {"skill-creation-sync.md"}

FORBIDDEN = [
    (re.compile(r"\b20\d\d-\d\d-\d\d\b"), "dated history"),
    (re.compile(r"measured case", re.I), "incident narrative ('Measured case')"),
    (re.compile(r"anti-pattern in self", re.I), "incident narrative ('Anti-pattern in self')"),
    (re.compile(r"\[\[[^\]]+\]\]"), "wiki-link (does not resolve in Claude Code)"),
]


def frontmatter(text: str) -> dict[str, bool] | None:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        return None
    block = match.group(1)
    return {
        "type_rule": re.search(r"(?m)^type:\s*rule\s*$", block) is not None,
        "paths": re.search(r"(?m)^paths:", block) is not None,
    }


def main() -> int:
    kit = Path(__file__).resolve().parent.parent
    rule_files = sorted((kit / "rules").glob("*.md")) + sorted((kit / "rules" / "personal").glob("*.md"))
    problems: list[str] = []
    always_on_total = 0

    for path in rule_files:
        rel = path.relative_to(kit)
        text = path.read_text()
        meta = frontmatter(text)
        if meta is None or not meta["type_rule"]:
            problems.append(f"{rel}: missing frontmatter with 'type: rule'")
            continue
        size = len(text)
        if meta["paths"]:
            if size > PATH_SCOPED_FILE_MAX and path.name not in SIZE_EXEMPT:
                problems.append(f"{rel}: path-scoped rule is {size} chars (max {PATH_SCOPED_FILE_MAX})")
        else:
            always_on_total += size
            if size > ALWAYS_ON_FILE_MAX:
                problems.append(f"{rel}: always-on rule is {size} chars (max {ALWAYS_ON_FILE_MAX})")
        for pattern, label in FORBIDDEN:
            hits = len(pattern.findall(text))
            if hits:
                problems.append(f"{rel}: {label} ({hits}x)")

    if always_on_total > ALWAYS_ON_TOTAL_MAX:
        problems.append(f"always-on total is {always_on_total} chars (max {ALWAYS_ON_TOTAL_MAX})")

    for problem in problems:
        print(problem)
    print(f"{len(rule_files)} rules, always-on total {always_on_total} chars, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
