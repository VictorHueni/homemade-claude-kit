#!/usr/bin/env python3
"""Render a curated release note to an A4 PDF report (plus its HTML intermediate).

Reads the committed release-note Markdown (the single source of truth), parses
its deterministic template structure, and emits:

  * a self-contained print-styled HTML file (always), themed by the resolved
    design (shared/design_source.py): the `--design-system DIR` folder, else the
    docs/ux/package.json pin found by walking up from the working directory,
    else the kit's base theme. The font faces and the `core`, `dataviz` and
    `print` modules are inlined in a <style data-design-layer> block; the page
    box comes from the `print` module. The HTML is checked against the design
    (shared/check_render.py) before anything is written: a report that breaks
    the design writes nothing and exits 1, a refused design exits 2. The
    provenance report is printed and written next to the HTML as
    <html>.provenance.json; and
  * a paginated PDF via headless Chromium (Playwright), with the shared print
    chrome in the page margins (running title, the brand logo and legal line,
    page numbers) and a link to the version's GitHub Release.

Playwright is an optional dependency — NOT auto-installed. If it is missing,
the HTML is still written and the script fails the PDF step with an explicit
message (print the HTML to PDF from a browser as a fallback).

Usage::

    python render_pdf.py docs/communication/release-notes/v1.4.0-rebooking.md
    python render_pdf.py NOTE.md --release-url https://github.com/o/r/releases/tag/v1.4.0
    python render_pdf.py NOTE.md --design-system path/to/design-system --output /tmp/note.pdf
    python render_pdf.py NOTE.md --exception=--font-report="Lora, serif"
    python render_pdf.py NOTE.md --html-only
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_TEMPLATE_DIR = _HERE.parent / "templates"

# The synced copies of the shared resolver, validator and print chrome (scripts/sync-shared.py).
sys.path.insert(0, str(_HERE / "shared"))
import check_render  # noqa: E402
import design_source  # noqa: E402
import print_chrome  # noqa: E402
from design_source import DesignError  # noqa: E402

# The modules the report reads: core (palette, fonts, radii), dataviz (the donut's chart scale) and
# print (the page box and background, and the report class vocabulary a design may style). Brand reaches
# the PDF through the page-margin chrome, not the page; the other modules style nothing the report draws.
REPORT_MODULES = ("core", "dataviz", "print")
REPORT_FONT = "--font-report"
OLD_FONTS_CSS = Path("docs/ux/fonts/fonts.css")


class RenderRefused(Exception):
    """The report breaks the resolved design; nothing was written."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code

_PRODUCT_RE = re.compile(r"^\*\*(?:(P\d+)\s*·\s*)?(.+?)\*\*$")
_CAPABILITY_RE = re.compile(r"^\*\*(C\d+(?:\.\d+)*)\s+(.+?)\*\*$")
_ENTRY_RE = re.compile(r"^(?:(C\d+(?:\.\d+)*)\s+)?([^:]{1,60}):\s*(.+)$")
_AUDIT_RE = re.compile(r"^(.*?)\s*\(([0-9A-Za-z\-]{1,12}(?:,\s*[0-9A-Za-z\-]{1,12})*)\)\s*$")
_H1_RE = re.compile(r"^#\s+(v[^:\s]+):\s*(.+?)\s*(?:\(([^()]*)\))?\s*$")
_CHANGELOG_RE = re.compile(r"^\*\*Full Changelog\*\*:\s*(.+)$")


def _fail(message: str) -> None:
    print(f"render_pdf.py: {message}", file=sys.stderr)
    raise SystemExit(1)


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


# Escaping runs first and leaves []() untouched, so these match on escaped text.
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_BARE_URL_RE = re.compile(r"^https?://\S+$")
# Only schemes that mean "go read this" — anything else (javascript:, data:) is
# rendered as plain text rather than becoming a live link in a distributed PDF.
_SAFE_URL_RE = re.compile(r"^(?:https?://|mailto:|[./#])", re.I)


def _link_sub(match: re.Match) -> str:
    """[label](url) → an <a>, or the matched text verbatim when url isn't followable.

    Returning the original spelling (rather than the bare label) keeps an
    unrenderable link visible and intact instead of quietly dropping half of it.
    """
    label, url = match.group(1), match.group(2)
    return f'<a href="{url}">{label}</a>' if _SAFE_URL_RE.match(url) else match.group(0)


def _inline(text: str) -> str:
    """Escape, then render Markdown inline code spans and links.

    A release note is a document whose whole job is to point somewhere — at a
    compare range, a PR, a spec — so an authored [text](url) has to survive into
    the PDF as a live link rather than printing its own syntax.
    """
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", _esc(text))
    return _MD_LINK_RE.sub(_link_sub, out)


# ---------------------------------------------------------------- parsing ----

def _split_frontmatter(text: str) -> tuple[dict, str]:
    """Line-based frontmatter parse (stdlib only — no PyYAML dependency)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta: dict[str, str] = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(lines[i + 1:])
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            meta[m.group(1)] = m.group(2).strip().strip('"')
    return {}, text  # unterminated frontmatter — treat as body


# Heading keyword -> model key. "fix" is tested before "new" so a heading like
# "Fixes and new improvements" resolves to the fixes section, not What's new.
_SECTION_KEYS = (("fix", "fixes"), ("platform", "platform"), ("breaking", "breaking"), ("new", "products"))
_RECOGNISED_SECTIONS = ("What's new", "Fixes and improvements", "Platform and engineering",
                        "Breaking changes")


def _section_for(heading: str) -> str | None:
    """The model key a `## heading` feeds, or None if the heading is unrecognised."""
    lowered = heading.lower()
    for needle, key in _SECTION_KEYS:
        if needle in lowered:
            return "whats-new" if key == "products" else key
    return None


def _parse_entry(text: str) -> dict:
    """Split a bullet into optional FBS ref, bold label, body text, audit IDs."""
    audit = ""
    m = _AUDIT_RE.match(text)
    if m and any(ch.isdigit() for ch in m.group(2)):
        text, audit = m.group(1), m.group(2)
    m = _ENTRY_RE.match(text)
    if m:
        return {"ref": m.group(1) or "", "label": m.group(2), "text": m.group(3), "audit": audit}
    return {"ref": "", "label": "", "text": text, "audit": audit}


def parse_note(text: str) -> dict:
    """Parse the release-note template structure into a model dict."""
    meta, body = _split_frontmatter(text)
    model: dict = {"meta": meta, "version": "", "theme": "", "daterange": "",
                   "framing": "", "products": [], "fixes": [], "platform": [],
                   "breaking": [], "changelog": "", "unknown": []}
    section = None
    product = None
    group = None
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("<!--"):
            continue
        h1 = _H1_RE.match(line)
        if h1:
            model["version"], model["theme"] = h1.group(1), h1.group(2)
            model["daterange"] = h1.group(3) or ""
            continue
        if line.startswith("## "):
            heading = line[3:].strip()
            section = _section_for(heading)
            if section is None:
                # Tracked, not dropped in silence — build_html warns about these.
                model["unknown"].append({"heading": heading, "bullets": 0})
            product = None
            group = None
            continue
        cl = _CHANGELOG_RE.match(line)
        if cl:
            model["changelog"] = cl.group(1)
            continue
        if line.startswith(">") and not model["framing"]:
            model["framing"] = line.lstrip("> ").strip("_ ")
            continue
        # Capability header checked before product: both are bare **bold** lines,
        # but a capability always carries a C-ref — check the more specific pattern
        # first so "**C2.2 Regulatory Change Monitoring**" isn't mistaken for a
        # second product.
        cm = _CAPABILITY_RE.match(line)
        if cm and section == "whats-new" and product is not None:
            group = {"id": cm.group(1), "name": cm.group(2), "entries": []}
            product["groups"].append(group)
            continue
        pm = _PRODUCT_RE.match(line)
        if pm and section == "whats-new":
            product = {"id": pm.group(1) or "", "name": pm.group(2), "groups": []}
            model["products"].append(product)
            group = None
            continue
        if line.startswith("- "):
            entry = _parse_entry(line[2:])
            if section == "whats-new":
                if product is None:  # graceful degradation — note without product headers
                    product = {"id": "", "name": "", "groups": []}
                    model["products"].append(product)
                if group is None:  # no capability header seen yet — flat, unnamed group
                    group = {"id": "", "name": "", "entries": []}
                    product["groups"].append(group)
                group["entries"].append(entry)
            elif section in ("fixes", "platform", "breaking"):
                model[section].append(entry)
            elif model["unknown"]:
                model["unknown"][-1]["bullets"] += 1
    if not model["version"]:
        _fail("no release H1 found (expected '# vX.Y.Z: theme (dates)') — is this a curated note?")
    return model


# -------------------------------------------------------------- rendering ----

def _entry_html(entry: dict, number: int | None = None, titled: bool = False) -> str:
    """One entry.

    `number` gives a sequence handle to entries carrying no FBS ref of their own,
    in the same accent chip, so both read as the same kind of handle. `titled`
    promotes the label to a heading with the text beneath — the treatment What's
    new gives a capability — for a tier whose entries are themselves groupings
    rather than leaf items.
    """
    ref, num_class = entry["ref"], ""
    if not ref and number is not None:
        ref, num_class = f"{number:02d}", " entry-num"
    chip = f'<span class="entry-ref{num_class}">{_esc(ref)}</span>' if ref else ""

    body = _inline(entry["text"])
    if entry["audit"]:
        body += f'<span class="entry-audit">({_esc(entry["audit"])})</span>'

    if titled and entry["label"]:
        # Same heading class the capability groups use, so the two tiers match.
        return (f'<li class="entry--titled">'
                f'<h3 class="capability-label">{chip}{_inline(entry["label"])}</h3>'
                f"<div>{body}</div></li>")

    label = f'<span class="entry-label">{_inline(entry["label"])}:</span> ' if entry["label"] else ""
    return f"<li>{chip}{label}{body}</li>"


def _changelog_cell(changelog: str) -> str:
    """The Full changelog row: a link when the note gives one, code otherwise.

    The template's own convention is a bare compare range (`v1.3.0...v1.4.0`),
    which is an identifier and reads as code. But an author who wrote a Markdown
    link — or pasted the compare URL — meant it to be followable, and the
    cartouche is exactly where this document puts its links.
    """
    value = (changelog or "").strip()
    if not value:
        return ""
    m = _MD_LINK_RE.fullmatch(value)
    if m and _SAFE_URL_RE.match(m.group(2)):
        return f'<a href="{_esc(m.group(2))}">{_esc(m.group(1))}</a>'
    if _BARE_URL_RE.match(value):
        return f'<a href="{_esc(value)}">{_esc(value)}</a>'
    return f"<code>{_esc(value)}</code>"


def _cartouche(model: dict, release_url: str, note_label: str, today: str) -> str:
    """The title block under the summary: all release metadata, in place of a footer.

    Rows with nothing to show are omitted, so a note without a changelog line or
    outside a GitHub repo simply carries a shorter block.
    """
    meta = model["meta"]
    rows = [
        ("Period", _esc(model["daterange"])),
        ("Owner", _esc(meta.get("owner", ""))),
        ("Status", _esc(meta.get("status", ""))),
        ("Full changelog", _changelog_cell(model["changelog"])),
        ("Release notes", f'<a href="{_esc(release_url)}">{_esc(release_url)}</a>' if release_url else ""),
        ("Generated", f'com-release-note on {_esc(today)} from <code>{_esc(note_label)}</code>. '
                      f'Source note is the single source of truth; re-render after edits.'),
    ]
    cells = "".join(f'<div class="cart-row"><span class="cart-k">{key}</span>'
                    f'<span class="cart-v">{value}</span></div>'
                    for key, value in rows if value)
    return f'<div class="cartouche">{cells}</div>'


_RANGE_RE = re.compile(r"(v?[\w.\-]+)\.\.\.?(v?[\w.\-]+)")


def _compact(n: int) -> str:
    """Stat-tile number formatting: thousands-separated, then compact past 5 digits."""
    return f"{n:,}" if n < 10_000 else f"{n / 1000:.1f}k"


def _git_stats(note_path: Path, changelog: str, exclude_paths: list[str] | None = None) -> dict:
    """Commits, active days and lines changed for the note's changelog range.

    Deterministic and offline: the range comes from the note's own Full Changelog
    line. A repo without those tags (or no git) yields nothing, and the affected
    cards are omitted rather than guessed.

    `exclude_paths` scopes only the lines-changed measure (via git pathspec
    exclusion, e.g. ["docs/**", "*.md"]) — commits and active days still count
    the whole range, since those describe the release's cadence, not its code
    volume. A project whose release note is dominated by generated seeds or
    plan-execution logs (not source) would otherwise report a "lines changed"
    figure that is mostly non-code.
    """
    match = _RANGE_RE.search(changelog or "")
    if not match:
        return {}
    rng = f"{match.group(1)}..{match.group(2)}"
    cwd = str(note_path.parent.resolve())

    def run(args: list[str]) -> str | None:
        try:
            return subprocess.run(["git", "-C", cwd, *args],
                                  capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            return None

    count = run(["rev-list", "--count", rng])
    if count is None or not count.strip().isdigit():
        return {}
    stats = {"commits": count.strip()}
    dates = run(["log", "--format=%cs", rng])
    if dates is not None:
        stats["active_days"] = len({d for d in dates.split() if d}) or ""
    # Top-anchored (":/", ":!/…") because `run()` invokes git via `-C cwd` where
    # cwd is the *note's* directory, not the repo root — a plain "." / ":!p"
    # pathspec would resolve relative to the note's own folder and silently
    # scope the whole diff down to whatever lives next to the note.
    pathspec = ["--", ":/", *[f":!/{p}" for p in exclude_paths]] if exclude_paths else []
    short = run(["diff", "--shortstat", rng, *pathspec]) or ""
    added = re.search(r"(\d+) insertion", short)
    removed = re.search(r"(\d+) deletion", short)
    if added or removed:
        stats["lines"] = (int(added.group(1)) if added else 0,
                          int(removed.group(1)) if removed else 0)
        stats["lines_scoped"] = bool(exclude_paths)
    return stats


def _measures(model: dict) -> dict:
    """Counts over the parsed note. Structural arithmetic only — no judgement."""
    caps = sum(len(g["entries"]) for p in model["products"] for g in p["groups"])
    days = ""
    dates = re.findall(r"\d{4}-\d{2}-\d{2}", model["daterange"])
    if len(dates) == 2:
        try:
            start, end = (datetime.date.fromisoformat(d) for d in dates)
            days = (end - start).days
        except ValueError:
            days = ""
    return {"products": len(model["products"]), "caps": caps, "fixes": len(model["fixes"]),
            "platform": len(model["platform"]), "breaking": len(model["breaking"]),
            "total": caps + len(model["fixes"]) + len(model["platform"]) + len(model["breaking"]),
            "days": days}


# The composition ring's ordinal ramp: the design's chart scale, darkest first, one step per tier.
_CHART_STEPS = ("--chart-1", "--chart-2", "--chart-3", "--chart-4")


_SLICE_GAP_DEG = 1.4  # blank separator between slices, ~2px at this radius

# Ring geometry in viewBox units. The thickness matches the .donut-hole inset in
# report.html.tmpl (6.5mm of a 28mm figure); keep the two in step.
_RING_THICKNESS = 100 * 6.5 / 28
_RING_RADIUS = 50 - _RING_THICKNESS / 2


def _donut_svg(slices: list, total: int) -> str:
    """The composition ring as flat-filled SVG arcs.

    Deliberately NOT a CSS conic-gradient: Chromium compiles one into a PDF
    function-based shading (/ShadingType 1 driven by a /FunctionType 4
    PostScript calculator), the least-supported corner of the shading spec —
    correct in some readers and wildly wrong in others (observed: the whole ring
    rendering pink). The ring is discrete slices, not a blend, so stroked arc
    segments express the intent directly and are plain vector fills every reader
    draws identically. Arcs are stroked on one circle via dash offsets, so a
    slice's angular position needs no path arithmetic.
    """
    steps = _CHART_STEPS
    circumference = 2 * math.pi * _RING_RADIUS
    arcs, angle = [], 0.0
    for i, (_label, count) in enumerate(slices):
        span = 360 * count / total
        drawn = max(span - _SLICE_GAP_DEG, 0.0)  # the gap is undrawn, not painted over
        arc = circumference * drawn / 360
        arcs.append(
            f'<circle cx="50" cy="50" r="{_RING_RADIUS:.2f}" fill="none" '
            f'style="stroke:var({steps[i % len(steps)]})" stroke-width="{_RING_THICKNESS:.2f}" '
            f'stroke-dasharray="{arc:.2f} {circumference - arc:.2f}" '
            f'stroke-dashoffset="{-circumference * angle / 360:.2f}"/>'
        )
        angle += span
    # Rotate so slice one starts at twelve o'clock, as a conic gradient would.
    return (f'<svg class="donut-svg" viewBox="0 0 100 100" role="presentation">'
            f'<g transform="rotate(-90 50 50)">{"".join(arcs)}</g></svg>')


def _recap(model: dict, git: dict) -> str:
    """Donut of the release's composition, with context cards beside it.

    The donut and its legend stay together as one figure; the cards carry only
    measures the donut does not already show, so no number appears twice.
    """
    m = _measures(model)
    if not m["total"]:
        return ""
    slices = [("New capabilities", m["caps"]), ("Platform items", m["platform"]),
              ("Fixes", m["fixes"]), ("Breaking changes", m["breaking"])]
    slices = [(label, count) for label, count in slices if count]

    donut_steps = _CHART_STEPS
    # The legend carries every value, so close slices are read as numbers, not arcs.
    legend = "".join(
        f'<div class="dl-row">'
        f'<span class="dl-sw" style="background:var({donut_steps[i % len(donut_steps)]})"></span>'
        f'<span class="dl-k">{_esc(label)}</span><span class="dl-v">{count}</span>'
        f'<span class="dl-p">{round(100 * count / m["total"])}%</span></div>'
        for i, (label, count) in enumerate(slices)
    )

    # Signs alone distinguish added from removed: colouring them good/bad would
    # assert a judgement the numbers do not carry (deleted code is often a win).
    lines = git.get("lines")
    lines_html = (f'<span class="rc-pair">+{_compact(lines[0])} &#8722;{_compact(lines[1])}</span>'
                  if lines else "")
    lines_label = "Lines (code)" if git.get("lines_scoped") else "Lines"
    cards = [("Days", m["days"]), ("Active days", git.get("active_days", "")),
             ("Commits", git.get("commits", "")), (lines_label, lines_html)]
    card_html = "".join(f'<div class="recap-card"><div class="rc-k">{key}</div>'
                        f'<div class="rc-v">{value}</div></div>'
                        for key, value in cards if value != "" and value is not None)

    return (f'<div class="recap"><div class="recap-label">Release at a glance</div>'
            f'<div class="recap-body">'
            f'<div class="recap-figure">'
            f'<div class="donut">{_donut_svg(slices, m["total"])}'
            f'<div class="donut-hole"><span class="donut-total">{m["total"]}</span>'
            f'<span class="donut-cap">entries</span></div></div>'
            f'<div class="donut-legend">{legend}</div></div>'
            f'<div class="recap-cards">{card_html}</div>'
            f'</div></div>')


def _bucket_section(label: str, entries: list[dict], page_break: bool = False,
                    titled: bool = False) -> str:
    """One card holding every entry — the same shape a product card takes in
    What's new, so both tiers read as a block of related items rather than a
    stack of loose cards. Used by Fixes and by Platform and engineering.

    `titled` numbers each entry and gives its label a heading, for a tier whose
    entries are groupings in their own right (the Platform buckets). Leave it off
    for leaf items such as individual fixes, which read better as run-in labels.
    """
    if not entries:
        return ""
    items = "".join(_entry_html(e, i if titled else None, titled)
                    for i, e in enumerate(entries, start=1))
    cls = "section section--page-break" if page_break else "section"
    return (f'<section class="{cls}"><div class="section-label">{_esc(label)}</div>'
            f'<div class="bucket"><ul class="entry-list">{items}</ul></div></section>')


def render_content(model: dict, release_url: str, note_label: str, today: str, git: dict) -> str:
    out = []
    out.append(f'<div class="report-kicker">Release note · {_esc(model["version"])}</div>')
    out.append(f'<h1 class="report-title">{_esc(model["theme"])}</h1>')
    if model["framing"]:
        out.append(f'<p class="report-framing">{_inline(model["framing"])}</p>')
    out.append(_cartouche(model, release_url, note_label, today))
    out.append(_recap(model, git))

    if model["products"]:
        out.append('<section class="section section--page-break">'
                   '<div class="section-label">What&#x2019;s new</div>')
        for product in model["products"]:
            out.append('<div class="product-card">')
            if product["name"]:
                chip = f'<span class="product-id">{_esc(product["id"])}</span>' if product["id"] else ""
                out.append(f'<h2 class="product-name">{chip}{_esc(product["name"])}</h2>')
            for group in product["groups"]:
                out.append('<div class="capability-group">')
                if group["name"]:
                    chip = (f'<span class="entry-ref">{_esc(group["id"])}</span>' if group["id"] else "")
                    out.append(f'<h3 class="capability-label">{chip}{_esc(group["name"])}</h3>')
                out.append('<ul class="entry-list">' +
                           "".join(_entry_html(e) for e in group["entries"]) + "</ul></div>")
            out.append("</div>")
        out.append("</section>")

    out.append(_bucket_section("Fixes and improvements", model["fixes"]))
    out.append(_bucket_section("Platform and engineering", model["platform"],
                               page_break=True, titled=True))

    if model["breaking"]:
        out.append('<section class="section section--breaking">'
                   '<div class="section-label">Breaking changes</div>'
                   '<div class="breaking"><ul class="entry-list">' +
                   "".join(_entry_html(e) for e in model["breaking"]) + "</ul></div></section>")
    return "\n".join(out)


def resolve_design(explicit: str | None):
    """The report's design: the --design-system folder, else the docs/ux/package.json pin found by walking up
    from the working directory, else the kit's base theme. A single stylesheet is refused."""
    folder = None
    if explicit:
        folder = Path(explicit)
        if folder.is_file():
            raise DesignError("--design-system names a single stylesheet; it must name a design-system folder with "
                              "a kit-manifest.json.\n" + design_source._legacy_message(folder))
        if not folder.is_dir():
            raise DesignError(f"--design-system: {folder} does not exist; name a design-system folder with a "
                              "kit-manifest.json, or leave it out to use the docs/ux/package.json pin")
    return design_source.resolve(Path.cwd(), explicit=folder)


def parse_exceptions(items: list[str]) -> dict:
    out = {}
    for item in items or []:
        name, sep, value = item.partition("=")
        if not sep or not name or not value:
            raise DesignError(f"--exception wants NAME=VALUE, got {item!r}")
        out[name] = value
    if REPORT_FONT in out and re.search(r"[;{}<>]", out[REPORT_FONT]):
        raise DesignError(f"--exception {REPORT_FONT} wants a font-family list, got {out[REPORT_FONT]!r}")
    return out


def design_layer(design) -> str:
    """The font faces, then the modules the report reads (base first, the design system after it)."""
    css = "\n".join(design.fonts + [design.css[m] for m in REPORT_MODULES if design.css.get(m)])
    return f"<style data-design-layer>\n{css}\n</style>"


def report_font_css(exceptions: dict) -> str:
    """The report's text face: --font-body, or --font-report when the run declares it as an exception, which
    re-faces the release note alone and is listed in the provenance report."""
    if REPORT_FONT in exceptions:
        return (f":root {{ {REPORT_FONT}: {exceptions[REPORT_FONT]}; "
                f"--kit-report-font: var({REPORT_FONT}); }}")
    return ":root { --kit-report-font: var(--font-body); }"


def page_rule(geometry: dict) -> str:
    return f"@page {{ size: {geometry['size']}; margin: {geometry['margin_css']}; }}"


def warn_old_fonts() -> None:
    """docs/ux/fonts/fonts.css was read before 2.0.0; say so instead of ignoring it in silence."""
    if OLD_FONTS_CSS.is_file():
        print(f"render_pdf.py: WARNING: {OLD_FONTS_CSS} is no longer read; fonts come from the design's "
              "@font-face rules (put a self-hosted face in the design's type module), and --font-report is "
              "declared with --exception=--font-report=...", file=sys.stderr)


def provenance_summary(design, report: dict) -> str:
    prov, ident = design.provenance, design.provenance["designSystem"]
    source = ident["source"] if ident["source"] == "base" else \
        f"{ident.get('name') or ident.get('path')}{'@' + ident['version'] if ident.get('version') else ''}"
    lines = [f"design {source}"]
    for origin in ("design-system", "base"):
        mods = [m for m, o in prov["modules"].items() if o == origin]
        if mods:
            lines.append(f"{origin}: {', '.join(mods)}")
    lines.append(f"inlined: {', '.join(REPORT_MODULES)}")
    lines += [f"exception {e['name']}={e['value']}" + ("" if e["known"] else " (not in the design's vocabulary)")
              for e in report["exceptions"]]
    lines += [f"warning: {w}" for w in prov.get("warnings", [])]
    return "\n".join(lines)


def write_atomic(path: Path, text: str) -> None:
    """Write beside the target, then rename into place."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


_GITHUB_REMOTE_RE = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$")


def _github_release_url(note_path: Path, version: str, explicit: str | None) -> str:
    """URL of the GitHub Release for this version, from --release-url or git origin.

    Read-only and best-effort: a note outside a repo, a non-GitHub remote, or a
    missing git simply yields no link rather than a failed render.
    """
    if explicit:
        return explicit
    if not version:
        return ""
    try:
        # `git config --get` (not `remote get-url`): the latter applies url.*.insteadOf
        # rewrites, which can turn a GitHub origin into a mirror or proxy address.
        remote = subprocess.run(["git", "-C", str(note_path.parent.resolve()),
                                 "config", "--get", "remote.origin.url"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""
    m = _GITHUB_REMOTE_RE.search(remote)
    return f"https://github.com/{m['owner']}/{m['repo']}/releases/tag/{version}" if m else ""


def _warn_unknown_sections(model: dict) -> None:
    """Never drop an authored section in silence — say what was skipped and why."""
    if not model["unknown"]:
        return
    print(f"render_pdf.py: WARNING: {len(model['unknown'])} section(s) not recognised, "
          f"omitted from the report:", file=sys.stderr)
    for item in model["unknown"]:
        dropped = f", {item['bullets']} bullet(s) dropped" if item["bullets"] else ""
        print(f"  - \"{item['heading']}\"{dropped}", file=sys.stderr)
    print(f"  Recognised headings: {', '.join(_RECOGNISED_SECTIONS)}. "
          f"Rename the section, or fold its content into one of these.", file=sys.stderr)


def build_html(note_path: Path, design, exceptions: dict, release_url: str | None,
               exclude_paths: list[str] | None = None) -> str:
    model = parse_note(note_path.read_text(encoding="utf-8"))
    _warn_unknown_sections(model)
    today = datetime.date.today().isoformat()
    url = _github_release_url(note_path, model["version"], release_url)
    try:
        note_label = os.path.relpath(note_path)
    except ValueError:
        note_label = str(note_path)
    tmpl = (_TEMPLATE_DIR / "report.html.tmpl").read_text(encoding="utf-8")
    title = model["meta"].get("title") or f'{model["version"]}: {model["theme"]}'
    for key, value in {"TITLE": _esc(title),
                       "REPORT_FONT_CSS": report_font_css(exceptions),
                       "PAGE_RULE": page_rule(print_chrome.print_geometry(design)),
                       "DESIGN_LAYER": design_layer(design),
                       "CONTENT": render_content(model, url, note_label, today,
                                                 _git_stats(note_path, model["changelog"], exclude_paths))}.items():
        tmpl = tmpl.replace("{{" + key + "}}", value)
    return tmpl


def checked_html(note_path: Path, design, exceptions: dict, release_url: str | None,
                 exclude_paths: list[str] | None, label: Path) -> tuple[str, dict]:
    """Build the report and check it against the design; raise RenderRefused with the findings when it fails."""
    text = build_html(note_path, design, exceptions, release_url, exclude_paths)
    report = check_render.check(text, design, exceptions)
    if not report["ok"]:
        raise RenderRefused(f"the report breaks the design ({len(report['findings'])} finding(s)); nothing was "
                            "written:\n" + check_render.format_text(report, label))
    return text, report


# ------------------------------------------------------------- PDF export ----

_PAGE_COUNT_RE = re.compile(rb"/Type\s*/Page[^s]")

_MIN_SCALE = 0.85  # readability floor: 10.5pt body stays ≥ 8.9pt effective


def _page_args(geometry: dict) -> dict:
    """The page box every page.pdf() call uses (probe and final render alike): the print module's size and
    margins, the same values the HTML's @page rule carries, so Chromium paginates against the box it prints."""
    return {"width": geometry["width"], "height": geometry["height"], "margin": geometry["margin"]}


def _fit_scale(page, geometry: dict) -> float:
    """Largest scale in [_MIN_SCALE, 1.0] that needs the fewest pages.

    Content ending just past a page boundary — often only the atomic document
    footer — buys a whole extra, near-empty page. A shrink of a few percent is
    barely perceptible and usually reclaims it. Probe Chromium's real pagination
    at each scale (screen-media measurements diverge from print layout) and take
    the largest scale achieving the minimum page count; when shrinking saves
    nothing, that is 1.0 and the document renders untouched. The floor keeps
    body text readable — past it, an extra page is the honest answer.
    """
    # The probe omits the running header/footer deliberately: they render inside the
    # reserved margin boxes, so they cannot change the page count (verified — counts
    # match with and without them), and leaving them out keeps each probe cheaper.
    def pages(scale: float) -> int:
        return len(_PAGE_COUNT_RE.findall(page.pdf(scale=scale, **_page_args(geometry))))

    steps = int(round((1.0 - _MIN_SCALE) * 100)) + 1
    counts = {round(1.0 - step / 100, 2): None for step in range(steps)}
    for scale in counts:
        counts[scale] = pages(scale)
    fewest = min(counts.values())
    return max(scale for scale, n in counts.items() if n == fewest)


def render_pdf(html_path: Path, pdf_path: Path, design, running_title: str = "", version: str = "") -> None:
    geometry = print_chrome.print_geometry(design)
    side = geometry["margin"]["left"]
    # Chromium draws the chrome in the page margins as a separate document; the shared print chrome inlines
    # the design's resolved --muted and --font-mono and carries the brand logo and legal line.
    header = print_chrome.header_template(design, running_title, side)
    footer = print_chrome.footer_template(design, f"Release note · {version}" if version else "", side)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        _fail(
            f"Playwright is not available — PDF step skipped (this script never auto-installs).\n"
            f"  The HTML was written to {html_path}; open it in a browser and print to PDF,\n"
            f"  or provision Playwright (pip install playwright && python -m playwright install chromium) and re-run."
        )
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:  # noqa: BLE001 — surface a clean message
            _fail(f"could not launch Chromium ({exc}). The HTML was written to {html_path}; "
                  f"ensure Playwright's Chromium build is available and re-run.")
        page = browser.new_page()
        page.emulate_media(media="screen")
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.evaluate("() => document.fonts.ready")
        # Drop the screen wrapper padding, whose overflow can mint a blank trailing
        # page. The template's @page rule is left alone: it carries the same box as
        # _page_args, so Chromium paginates against the box it prints into.
        page.add_style_tag(content=".report { padding: 0; }")
        scale = _fit_scale(page, geometry)
        if scale < 1.0:
            print(f"render_pdf.py: scaled to {scale:.2f} to save a page")
        page.pdf(
            path=str(pdf_path),
            scale=scale,
            print_background=True,
            display_header_footer=True,
            header_template=header,
            footer_template=footer,
            **_page_args(geometry),
        )
        browser.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a curated release note to a PDF report (HTML intermediate always written)."
    )
    parser.add_argument("note", type=Path, help="Path to the curated release-note Markdown.")
    parser.add_argument("--design-system", metavar="DIR",
                        help="A design-system folder with a kit-manifest.json (default: the docs/ux/package.json "
                             "pin found by walking up from the working directory, else the kit's base theme).")
    parser.add_argument("--exception", action="append", default=[], metavar="NAME=VALUE",
                        help="A named local exception the validator allows and the provenance report lists "
                             "(repeatable). --exception=--font-report=FONTS re-faces the report alone.")
    parser.add_argument("--release-url",
                        help="GitHub Release URL (default: derived from the repo's origin remote + version).")
    parser.add_argument("--output", type=Path,
                        help="Output PDF path (default: <note-dir>/pdf/<note-stem>.pdf).")
    parser.add_argument("--html-only", action="store_true", help="Write the HTML and skip the PDF step.")
    parser.add_argument("--exclude-path", action="append", default=[], metavar="PATHSPEC",
                        help="Git pathspec to exclude from the recap's 'Lines' card (repeatable), "
                             "e.g. --exclude-path 'docs/**' --exclude-path '*.md'. Scopes only that "
                             "measure to code churn; commits and active days still cover the full "
                             "range. Omit to keep the whole-tree diff (default, unchanged behaviour).")
    args = parser.parse_args(argv)

    if not args.note.is_file():
        _fail(f"note not found: {args.note}")
    pdf_path = args.output or args.note.parent / "pdf" / f"{args.note.stem}.pdf"
    html_path = pdf_path.with_suffix(".html")
    prov_path = html_path.with_name(html_path.name + ".provenance.json")

    warn_old_fonts()
    try:
        design = resolve_design(args.design_system)
        exceptions = parse_exceptions(args.exception)
        # Check, then write: a report that breaks the design writes nothing.
        text, report = checked_html(args.note, design, exceptions, args.release_url, args.exclude_path, html_path)
    except (DesignError, RenderRefused) as exc:
        print(f"render_pdf.py: REFUSED: {exc}", file=sys.stderr)
        return exc.code
    write_atomic(html_path, text)
    write_atomic(prov_path, json.dumps(design.provenance, indent=2) + "\n")
    print("render_pdf.py: check: PASS, the report uses only the design's roles")
    print("render_pdf.py: provenance: " + provenance_summary(design, report).replace("\n", "; ") + f" ({prov_path})")
    print(f"render_pdf.py: wrote {html_path}")
    if args.html_only:
        return 0

    model = parse_note(args.note.read_text(encoding="utf-8"))
    running = model["meta"].get("title") or f'{model["version"]}: {model["theme"]}'
    render_pdf(html_path, pdf_path, design, running, model["version"])
    print(f"render_pdf.py: wrote {pdf_path} ({pdf_path.stat().st_size / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
