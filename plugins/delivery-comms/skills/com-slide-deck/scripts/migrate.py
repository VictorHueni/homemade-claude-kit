#!/usr/bin/env python3
"""
migrate.py — com-slide-deck: migrate a pre-design-system deck onto the design
contract (plugins/delivery-comms/contract/README.md).

Resolves the deck's design the way build.py does (docs/ux/package.json pin,
paths.design_tokens folder, else the kit's base theme), reports every hard-coded
colour in the deck's styles.css and slide partials with the closest resolved role,
detects legacy token names, maps the ones that changed to the contract, and either:

    python migrate.py --config CONFIG            report only (no writes; default)
    python migrate.py --config CONFIG --apply    add a backwards-compatible alias
                                                 shim to styles.css (additive, safe)
    python migrate.py --config CONFIG --rename    rewrite legacy names -> contract
                                                 names across styles.css + partials

`--apply` and `--rename` are mutually exclusive. `--apply` is the low-risk path
(no partial edits — old var(--bg) keeps working via the shim). `--rename` is the
thorough path (no shim needed afterwards). Commit the deck first; changes are
easy to review in git.

Standard library + PyYAML.
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install it with: pip install pyyaml")
    sys.exit(1)

# Legacy deck token -> contract token (ONLY the names that changed).
RENAME = {
    "--bg":        "--canvas-bg",
    "--text":      "--ink",
    "--card-bg":   "--surface",
    "--font-sans": "--font-body",
}
# Legacy deck-only names with no contract role. build.py refuses them: replace each
# with a role (e.g. --dim -> --muted) or declare it under design.exceptions.
DECK_ONLY = ["--dim", "--accent-lt", "--danger-lt"]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import DesignError, design_exceptions, resolve_design  # noqa: E402
import check_render  # noqa: E402  (on the path through build.py)

SHIM_START = "/* >>> com-slide-deck migrate: legacy-token shim >>> */"
SHIM_END = "/* <<< com-slide-deck migrate <<< */"


def tok_re(name):
    """Match a CSS custom-property name as a whole token (so --bg != --bgx)."""
    return re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")


def resolve(base, rel):
    return (base / rel).resolve()


def gather_files(base, cfg):
    paths = cfg.get("paths", {})
    styles = resolve(base, paths.get("styles_file", "design/styles.css"))
    slides_dir = resolve(base, paths.get("slides_dir", "output/slides"))
    files = []
    if styles.exists():
        files.append(styles)
    partials = []
    if slides_dir.exists():
        partials += sorted(slides_dir.glob("*.html"))
    for proto in (slides_dir.parent / "prototypes", base / "dist" / "prototypes",
                  base / "output" / "prototypes"):
        if proto.exists():
            partials += sorted(proto.glob("*.html"))
    files += partials
    return files, styles, partials


def scan(files):
    """Return {token: {path: count}} for every legacy token found."""
    found = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        for name in list(RENAME) + DECK_ONLY:
            n = len(tok_re(name).findall(text))
            if n:
                found.setdefault(name, {})[str(f)] = n
    return found


def design_findings(files, design, cfg):
    """{path: [finding]} from the shared validator, each file checked on its own against the resolved design."""
    exceptions = design_exceptions(cfg)
    out = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        page = f"<style>\n{text}\n</style>" if f.suffix == ".css" else text
        report = check_render.check(page, design, exceptions)
        if report["findings"]:
            offset = 1 if f.suffix == ".css" else 0
            for item in report["findings"]:
                if item.get("line"):
                    item["line"] -= offset
            out[str(f)] = report["findings"]
    return out


def rel(p, base):
    try:
        return str(Path(p).resolve().relative_to(base.resolve()))
    except ValueError:
        return str(p)


# --------------------------------------------------------------------------- #

def do_report(base, cfg, found, files):
    print("=== com-slide-deck migrate — report ===\n")

    try:
        design = resolve_design(cfg, base)
    except DesignError as exc:
        print(f"[todo] the deck's design is refused:\n{exc}")
        return 2
    ident = design.provenance["designSystem"]
    if ident["source"] == "base":
        print("[todo] no project design system: the deck renders on the kit's base theme.")
        print("       pin one with  ux-design-system point   or author one with  ux-design-system subset")
    else:
        print(f"[ok]   design system: {ident.get('name') or ident.get('path')} {ident.get('version', '')}".rstrip())

    findings = design_findings(files, design, cfg)
    if findings:
        print("\nValues the build will refuse (closest resolved role shown):\n")
        for path, items in findings.items():
            for item in items:
                line = f":{item['line']}" if item.get("line") else ""
                hint = f"use var({item['suggest']})" if item.get("suggest") else item["message"]
                print(f"    {rel(path, base)}{line}  {item['value']}  {hint}")
        print("\n       replace each with its role, or declare a deliberate value under design.exceptions")
    else:
        print("\n[ok]   no hard-coded colour or unknown property: the deck passes the validator.")

    if not found:
        print("\n[ok]   no legacy token names detected.")
        return 0
    print("\nLegacy tokens detected:\n")
    renamable = {t: m for t, m in found.items() if t in RENAME}
    keepers = {t: m for t, m in found.items() if t in DECK_ONLY}

    if renamable:
        print("  Changed names (need shim or rename):")
        for t, m in sorted(renamable.items()):
            where = ", ".join(f"{rel(p, base)}×{c}" for p, c in m.items())
            print(f"    {t:14s} -> {RENAME[t]:14s}  [{where}]")
    if keepers:
        print("\n  Deck-only names (no contract role: replace with a role or declare under design.exceptions):")
        for t, m in sorted(keepers.items()):
            print(f"    {t}")

    print("\nNext:")
    print("  --rename  rewrite the changed names across styles.css + partials (recommended)")
    print("  --apply   add an alias shim to styles.css; build.py accepts the aliased names only when")
    print("            they are declared under design.exceptions")
    return 0


def do_apply(base, found, styles):
    used = [t for t in RENAME if t in found]
    if not used:
        print("[apply] no changed legacy tokens in use — nothing to shim.")
        return
    if not styles.exists():
        print(f"[apply] styles.css not found: {styles}")
        return
    text = styles.read_text(encoding="utf-8")
    # remove any prior shim block
    text = re.sub(re.escape(SHIM_START) + r".*?" + re.escape(SHIM_END) + r"\n?",
                  "", text, flags=re.DOTALL)
    lines = [SHIM_START,
             "/* Legacy deck token names aliased to the contract so existing slide",
             "   partials keep working. Remove this block once partials are renamed",
             "   (or run migrate.py --rename to do that automatically). */",
             ":root {"]
    for t in used:
        lines.append(f"  {t}: var({RENAME[t]});")
    lines += ["}", SHIM_END, ""]
    shim = "\n".join(lines)
    styles.write_text(shim + "\n" + text, encoding="utf-8")
    print(f"[apply] wrote alias shim for {', '.join(used)} into {rel(styles, base)}")
    print("        rebuild with build.py; old partials now resolve to contract values.")


def do_rename(base, found, files):
    used = [t for t in RENAME if t in found]
    if not used:
        print("[rename] no changed legacy tokens in use — nothing to rename.")
        return
    total = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        new = text
        n = 0
        for t in used:
            new, k = tok_re(t).subn(RENAME[t], new)
            n += k
        if n:
            f.write_text(new, encoding="utf-8")
            total += n
            print(f"[rename] {rel(f, base)}: {n} replacement(s)")
    print(f"[rename] done — {total} replacement(s) across {len(files)} file(s). "
          f"No shim needed.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Migrate a deck onto the shared design-system tokens.")
    ap.add_argument("--config", required=True, help="Path to the deck's config.yaml")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--apply", action="store_true", help="Add the legacy-token alias shim to styles.css")
    g.add_argument("--rename", action="store_true", help="Rewrite legacy names -> contract names in place")
    args = ap.parse_args(argv)

    config_path = Path(args.config).resolve()
    if not config_path.is_file():
        sys.exit(f"error: config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    base = config_path.parent

    files, styles, _partials = gather_files(base, cfg)
    found = scan(files)

    if args.apply:
        do_apply(base, found, styles)
    elif args.rename:
        do_rename(base, found, files)
    else:
        sys.exit(do_report(base, cfg, found, files))


if __name__ == "__main__":
    main()
