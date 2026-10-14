#!/usr/bin/env python3
"""Check a built HTML file against the resolved design: the blocking validator.

Rules (Plan-0005 constraint 5):
  literal-colour    a hex, rgb()/hsl()-family or named colour in a style attribute, a <style> block or an
                    SVG presentation attribute. Exempt: <style data-design-layer> (the resolved design the
                    renderer inlined), elements marked data-brand-asset, url() contents, declared exceptions.
  unknown-property  a custom property outside the contract's roles and the reserved --kit-* prefix.
  contrast          a contract text pair that an exception brings below WCAG AA.
A `var(--role, fallback)` is read as `var(--role)`: the fallback neither passes nor fails a page.

An exception is NAME=VALUE: it allows the literal VALUE. When NAME is a contract role (`--muted=#6b7280`) it
also stands in for that role when the contract's text pairs are checked.

As a command, for generators outside the kit:
    check_render.py FILE.html [--exception NAME=VALUE]... [--json] [--design-system DIR | --from DIR]
Exit 0 pass, 1 findings, 2 the design was refused.
"""
import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import design_source  # noqa: E402

KIT_PREFIX = "--kit-"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SVG_COLOUR_ATTRS = ("fill", "stroke", "stop-color", "flood-color", "lighting-color", "color")
NAMED = ("aqua black blue brown fuchsia gold gray green grey lime maroon navy olive orange pink purple red "
         "silver teal white yellow").split()
HEX = r"#[0-9a-fA-F]{3,8}\b"
FUNC = r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\([^)]*\)"
LITERAL = re.compile(f"{HEX}|{FUNC}")
NAMED_RE = re.compile(r"(?<![\w#-])(?:" + "|".join(NAMED) + r")(?![\w-])", re.I)
COLOUR_PROP = re.compile(r"color|background|border|outline|fill|stroke|shadow|accent|caret|column-rule", re.I)
DECL = re.compile(r"([\w-]+)\s*:\s*([^;{}]*[^;{}\s])(?=\s*(?:[;}]|$))")
CUSTOM = re.compile(r"--[\w-]+")


def blank(match):
    return re.sub(r"[^\n]", " ", match.group(0))


def strip_fallbacks(text):
    """Rewrite `var(--x, fallback)` as `var(--x)`, keeping the removed text's line breaks."""
    out, i = [], 0
    while True:
        start = text.find("var(", i)
        if start < 0:
            out.append(text[i:])
            return "".join(out)
        out.append(text[i:start + 4])
        j, depth, comma = start + 4, 1, None
        while j < len(text) and depth:
            c = text[j]
            depth += (c == "(") - (c == ")")
            if c == "," and depth == 1 and comma is None:
                comma = j
            j += 1
        if comma is None or depth:
            i = start + 4
            continue
        out.append(text[start + 4:comma].rstrip() + ")" + "\n" * text.count("\n", comma, j))
        i = j


def clean(text):
    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.S)
    text = re.sub(r"url\([^)]*\)", lambda m: "url()" + "\n" * m.group(0).count("\n"), text)
    return strip_fallbacks(text)


def parse_colour(value):
    value = value.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})", value)
    if m:
        h = m.group(1)
        h = "".join(c * 2 for c in h[:3]) if len(h) <= 4 else h[:6]
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)\b[^)]*\)", value)
    return tuple(int(g) for g in m.groups()) if m else None


def norm(value):
    return re.sub(r"\s+", "", value).lower()


class Scanner(HTMLParser):
    def __init__(self, known_props, allowed, role_colours):
        super().__init__(convert_charrefs=False)
        self.known, self.allowed, self.role_colours = known_props, allowed, role_colours
        self.findings, self.used = [], set()
        self.style = None          # (start line, text parts) of the <style> block being read
        self.skip = 0              # depth inside a data-brand-asset element
        self.depth = 0

    def finding(self, kind, value, line, where, message, suggest=None):
        item = {"kind": kind, "value": value, "line": line, "where": where, "message": message}
        if suggest:
            item["suggest"] = suggest
        self.findings.append(item)

    def suggestion(self, value):
        rgb = parse_colour(value)
        if rgb is None or not self.role_colours:
            return None
        return min(self.role_colours, key=lambda r: sum((a - b) ** 2 for a, b in zip(rgb, self.role_colours[r])))

    def scan(self, text, line, where, colour_attr=False):
        text = clean(text)
        for prop in CUSTOM.findall(text):
            if prop not in self.known and not prop.startswith(KIT_PREFIX):
                at = line + text[:text.index(prop)].count("\n")
                self.finding("unknown-property", prop, at, where,
                             f"{prop} is not a contract role or a {KIT_PREFIX}* renderer property; use a role from "
                             f"contract/modules.json or rename it {KIT_PREFIX}{prop[2:]}")
        spans = [(m.start(2), m.group(1), m.group(2)) for m in DECL.finditer(text)] if not colour_attr \
            else [(0, "color", text)]
        for offset, prop, value in spans:
            found = [(m.start(), m.group(0)) for m in LITERAL.finditer(value)]
            if COLOUR_PROP.search(prop):
                found += [(m.start(), m.group(0)) for m in NAMED_RE.finditer(value)]
            for pos, literal in found:
                if norm(literal) in self.allowed:
                    self.used.add(norm(literal))
                    continue
                at = line + text[:offset + pos].count("\n")
                role = self.suggestion(literal)
                self.finding("literal-colour", literal, at, where,
                             f"{literal} is a literal colour" + (f"; the closest role is var({role})" if role
                                                                  else "; use a design role, var(--role)"), role)

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        a = dict(attrs)
        if self.skip:
            self.skip += tag not in VOID
        elif "data-brand-asset" in a and tag not in VOID:
            self.skip = 1
        if not self.skip:
            if a.get("style"):
                self.scan(a["style"], line, "style attribute")
            for name in SVG_COLOUR_ATTRS:
                if a.get(name):
                    self.scan(a[name], line, f"{name} attribute", colour_attr=True)
            if tag == "style" and "data-design-layer" not in a:
                self.style = (line, [])
        elif tag == "style":
            self.style = None

    def handle_data(self, data):
        if self.style is not None:
            self.style[1].append(data)

    def handle_endtag(self, tag):
        if tag == "style" and self.style is not None:
            line, parts = self.style
            self.scan("".join(parts), line, "<style> block")
            self.style = None
        elif self.skip:
            self.skip -= 1


def _hex_roles(design):
    values = design_source.role_values("".join(design.css.values()))
    return {r: parse_colour(v) for r, v in values.items() if parse_colour(v) and not r.startswith("--font")}, values


def check(html, design, exceptions=None, name=None):
    """Return {"ok", "findings", "exceptions"} for `html` against the resolved `design`."""
    exceptions = dict(exceptions or {})
    contract = design_source._contract()
    known = {role for module in contract["modules"].values() for role in module["roles"]}
    role_colours, values = _hex_roles(design)
    scanner = Scanner(known, {norm(v) for v in exceptions.values()}, role_colours)
    scanner.feed(html)
    scanner.close()
    findings = list(scanner.findings)

    for pair in contract["pairs"]:
        touched = [r for r in (pair["fg"], pair["bg"]) if r in exceptions]
        if not touched:
            continue
        fg, bg = (exceptions.get(pair[k]) or values.get(pair[k], "") for k in ("fg", "bg"))
        if parse_colour(fg) and parse_colour(bg):
            ratio = design_source.contrast(_hex(fg), _hex(bg))
            if ratio < design_source.AA:
                findings.append({"kind": "contrast", "value": ", ".join(f"{r}={exceptions[r]}" for r in touched),
                                 "line": None, "where": "exception",
                                 "message": f"exception brings {pair['fg']} on {pair['bg']} ({pair['use']}) to "
                                            f"{ratio:.2f}:1, below WCAG AA {design_source.AA}"})
    report = {"ok": not findings, "findings": findings,
              "exceptions": [{"name": n, "value": v, "known": n in design.exceptions} for n, v in exceptions.items()]}
    design.provenance["exceptions"] = [e["name"] for e in report["exceptions"]]
    return report


def _hex(value):
    return "#%02x%02x%02x" % parse_colour(value)


def format_text(report, file):
    lines = [f"{file}{':%d' % f['line'] if f['line'] else ''}: {f['kind']} {f['value']}: {f['message']} ({f['where']})"
             for f in report["findings"]]
    lines += [f"exception {e['name']}={e['value']}" + ("" if e["known"] else " (not in the design's vocabulary)")
              for e in report["exceptions"]]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--exception", action="append", default=[], metavar="NAME=VALUE")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--design-system", help="a design-system folder, bypassing the pin")
    ap.add_argument("--from", dest="start", help="folder to start the pin search from (default: the file's folder)")
    args = ap.parse_args(argv)
    exceptions = {}
    for item in args.exception:
        key, sep, value = item.partition("=")
        if not sep or not key or not value:
            ap.error(f"--exception wants NAME=VALUE, got {item!r}")
        exceptions[key] = value
    path = Path(args.file)
    try:
        design = design_source.resolve(Path(args.start) if args.start else path.resolve().parent,
                                       explicit=args.design_system)
    except design_source.DesignError as exc:
        print(f"check_render: {exc}", file=sys.stderr)
        return exc.code
    report = check(path.read_text(encoding="utf-8"), design, exceptions)
    print(json.dumps(report, indent=2) if args.json else format_text(report, path))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
