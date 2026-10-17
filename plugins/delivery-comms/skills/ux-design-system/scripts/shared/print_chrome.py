#!/usr/bin/env python3
"""Print chrome: the running header and footer Chromium draws in the page margins of a paginated PDF.

Chromium renders `header_template` and `footer_template` as a separate document that the page's CSS
cannot reach, so the chrome inlines the resolved values of the design's `--muted` and `--font-mono`
roles (var() chains followed; a role that resolves to nothing is an error, never a silent default),
shows the brand logo as a data URI and the legal line as text. On a dark document it reads `--dark-muted`
and the on-dark logo instead. Used by com-release-note and by
com-slide-deck's `mode: document`, so both brand their page margins the same way.

`print_geometry` reads the page box from the `print` module: `--print-page-size` (a named size, optionally
landscape, or a width and a height) and `--print-margin` (CSS margin shorthand).
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import design_source  # noqa: E402
from design_source import DesignError  # noqa: E402

PAGE_SIZES = {"A3": ("297mm", "420mm"), "A4": ("210mm", "297mm"), "A5": ("148mm", "210mm"),
              "LETTER": ("8.5in", "11in"), "LEGAL": ("8.5in", "14in")}
LENGTH = re.compile(r"\d+(?:\.\d+)?(?:mm|cm|in|px)|0")
LOGO_HEIGHT = "3.5mm"
_DATA_URL = re.compile(r"""url\(\s*(['"]?)(data:[^'")]+)\1\s*\)""")
_VAR = re.compile(r"var\(\s*(--[\w-]+)\s*\)")


def role_value(design, role):
    """The resolved value of a contract role, following var() references within the design; "" when absent."""
    values = design_source.role_values("".join(design.css.values()))
    value = values.get(role, "")
    for _ in range(8):
        ref = _VAR.fullmatch(value)
        if not ref:
            break
        value = values.get(ref.group(1), "")
    return value


def resolved_role(design, role):
    """Like role_value, but a role that does not resolve to a concrete value is a DesignError."""
    value = role_value(design, role).strip()
    if not value or "var(" in value:
        raise DesignError(f"the design's {role} does not resolve to a value; the print chrome is drawn outside the "
                          "page and needs a concrete value")
    return value


def css_string(value):
    """The text of a CSS string value such as `"Acme Ltd."`; empty for none or no value."""
    value = (value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    elif value in ("none", "initial", "normal"):
        return ""
    value = re.sub(r"\\([0-9a-fA-F]{1,6})\s?", lambda m: chr(int(m.group(1), 16)), value)
    return re.sub(r"\\(.)", r"\1", value)


def logo_uri(design, role="--brand-logo-on-light"):
    """The data URI of a brand logo (the resolver inlined it), or "" when the design has none."""
    match = _DATA_URL.search(design.brand.get(role, ""))
    return match.group(2) if match else ""


def legal_line(design):
    return css_string(design.brand.get("--brand-legal", ""))


def page_box(value):
    """(width, height) CSS lengths for a --print-page-size value."""
    words = (value or "").split()
    landscape = bool(words) and words[-1].lower() == "landscape"
    if words and words[-1].lower() in ("landscape", "portrait"):
        words = words[:-1]
    if len(words) == 1 and words[0].upper() in PAGE_SIZES:
        width, height = PAGE_SIZES[words[0].upper()]
    elif len(words) == 2 and all(LENGTH.fullmatch(w) for w in words):
        width, height = words
    else:
        raise DesignError(f"the design's --print-page-size is {value!r}; use A3, A4, A5, Letter or Legal (optionally "
                          "followed by landscape) or a width and a height in mm, cm, in or px")
    return (height, width) if landscape else (width, height)


def margins(value):
    """{top, right, bottom, left} from a --print-margin value in CSS shorthand order."""
    parts = (value or "").split()
    if not 1 <= len(parts) <= 4 or not all(LENGTH.fullmatch(p) for p in parts):
        raise DesignError(f"the design's --print-margin is {value!r}; use one to four lengths in mm, cm, in or px")
    top, right, bottom, left = {1: parts * 4, 2: parts * 2, 3: [*parts, parts[1]], 4: parts}[len(parts)]
    return {"top": top, "right": right, "bottom": bottom, "left": left}


def print_geometry(design):
    """The page box of the `print` module: {"size", "width", "height", "margin", "margin_css"}."""
    size = resolved_role(design, "--print-page-size")
    margin_css = resolved_role(design, "--print-margin")
    width, height = page_box(size)
    return {"size": size, "width": width, "height": height, "margin": margins(margin_css), "margin_css": margin_css}


def _style(design, side, dark=False):
    muted = "--dark-muted" if dark else "--muted"
    return (f"width:100%;padding:0 {side};font-family:{resolved_role(design, '--font-mono')};font-size:8px;"
            f"color:{resolved_role(design, muted)};display:flex;justify-content:space-between;"
            "align-items:center;gap:4mm;")


def header_template(design, text, side, dark=False):
    """Running head on the left of the top margin; an empty span when there is no text."""
    if not text:
        return "<span></span>"
    style = html.escape(_style(design, side, dark) + "padding-bottom:2mm;")
    return f'<div style="{style}"><span>{html.escape(text)}</span><span></span></div>'


def footer_template(design, left, side, numbering=True, dark=False, classification=None):
    """Footer row: the brand logo and `left` text, the legal line, then the page position at the right.
    A design without a logo or a legal line simply leaves those cells out; `dark` takes the on-dark logo;
    a `classification` label prints in capitals just before the page position."""
    uri = logo_uri(design, "--brand-logo-on-dark" if dark else "--brand-logo-on-light")
    logo = (f'<img src="{uri}" alt="" data-brand-asset style="height:{LOGO_HEIGHT};width:auto;display:block">'
            if uri else "")
    start = f'<span style="display:flex;align-items:center;gap:2mm">{logo}<span>{html.escape(left or "")}</span></span>'
    legal = legal_line(design)
    middle = f"<span>{html.escape(legal)}</span>" if legal else "<span></span>"
    right = ('<span><span class="pageNumber"></span> / <span class="totalPages"></span></span>' if numbering
             else "<span></span>")
    if classification:
        position = right if numbering else ""
        right = (f'<span style="display:flex;align-items:center;gap:4mm"><span style="text-transform:uppercase">'
                 f'{html.escape(classification)}</span>{position}</span>')
    return f'<div style="{html.escape(_style(design, side, dark))}">{start}{middle}{right}</div>'
