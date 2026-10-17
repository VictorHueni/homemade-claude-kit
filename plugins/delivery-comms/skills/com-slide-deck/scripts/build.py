#!/usr/bin/env python3
"""
Slide Builder - Build (Stitch)
==============================
Reads individual slide partials and a shared CSS/JS layer,
then stitches them into a single self-contained HTML file
that can be opened in any browser with zero dependencies.

All paths in config.yaml are resolved relative to the config
file itself, so the skill scripts can live anywhere.

Usage:
    python build.py --config /path/to/project/config.yaml
    python build.py --config ./config.yaml
    python build.py --config ./config.yaml --output ./dist/deck.html
"""

import argparse
import html
import json
import os
import re
import sys
import textwrap
import urllib.parse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install it with: pip install pyyaml")
    sys.exit(1)

# The design comes from the shared resolver (pinned design system, local folder or the
# kit's base theme) and every build is checked by the shared validator. One copy for
# every renderer, synced from plugins/delivery-comms/shared/ by scripts/sync-shared.py.
sys.path.insert(0, str(Path(__file__).resolve().parent / "shared"))
import check_render  # noqa: E402
import classification  # noqa: E402
import design_source  # noqa: E402
from design_source import DesignError  # noqa: E402
from print_chrome import css_string, role_value  # noqa: E402  (shared with the page-margin chrome)
# Structural defaults for `mode: document` (paginated A4/Letter, flowing partials).
DOC_BASELINE = Path(__file__).resolve().parent.parent / "templates" / "doc.baseline.css"

# Paper sizes (mm) for the on-screen sheet preview in document mode.
PAGE_SIZES_MM = {"A4": (210, 297), "A3": (297, 420), "A5": (148, 210), "Letter": (216, 279), "Legal": (216, 356)}
DEFAULT_PAGE_MARGIN = {"top": "18mm", "right": "18mm", "bottom": "20mm", "left": "18mm"}


def page_geometry(cfg: dict) -> dict:
    """Normalise config.yaml's `page:` block (document mode). Shared with render.py
    so the CSS @page box and Chromium's print margins come from one source."""
    page = cfg.get("page", {}) or {}
    margin = dict(DEFAULT_PAGE_MARGIN)
    margin.update({k: str(v) for k, v in (page.get("margin") or {}).items() if k in margin})
    size = str(page.get("size", "A4"))
    orientation = str(page.get("orientation", "portrait"))
    w, h = PAGE_SIZES_MM.get(size, PAGE_SIZES_MM["A4"])
    if orientation == "landscape":
        w, h = h, w
    return {"size": size, "orientation": orientation, "margin": margin, "width_mm": w, "height_mm": h}


def make_document_css(geom: dict) -> str:
    m = geom["margin"]
    return (
        f"@page {{ size: {geom['size']} {geom['orientation']}; "
        f"margin: {m['top']} {m['right']} {m['bottom']} {m['left']}; }}\n"
        f":root {{ --kit-doc-page-width: {geom['width_mm']}mm; --kit-doc-margin-top: {m['top']}; "
        f"--kit-doc-margin-right: {m['right']}; --kit-doc-margin-bottom: {m['bottom']}; "
        f"--kit-doc-margin-left: {m['left']}; }}\n"
        + read_file(DOC_BASELINE)
    )


def load_config(config_path: Path) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_path(base: Path, relative: str) -> Path:
    return (base / relative).resolve()


def deck_sources(config_path: Path, cfg: dict) -> list:
    """The files a deck is built from (config, partials folder, styles, script, bibliography), never its
    outputs: shared/source_date.py dates the PDF from these, so a committed output cannot move the date."""
    base, paths = config_path.parent, cfg.get("paths") or {}
    keys = ("slides_dir", "styles_file", "script_file", "bibliography_file")
    return [config_path, *(resolve_path(base, paths[k]) for k in keys if paths.get(k))]


def read_file(path: Path) -> str:
    if not path.exists():
        print(f"  [WARN] File not found: {path}")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class RenderRefused(Exception):
    """The validator found violations; nothing was written. `code` is the process exit code."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


def resolve_design(cfg: dict, base: Path) -> "design_source.Design":
    """Resolve the deck's design with the shared resolver.

    `paths.design_tokens` (relative to the config file), when set, names a design-system
    folder with a kit-manifest.json; a single token file such as docs/ux/tokens.css is
    refused. Unset, the resolver walks up from the deck to the docs/ux/package.json pin,
    else the deck renders on the kit's base theme.
    """
    configured = (cfg.get("paths") or {}).get("design_tokens")
    explicit = None
    if configured:
        explicit = resolve_path(base, configured)
        if explicit.is_file():
            raise DesignError("paths.design_tokens names a single token file; it must name a design-system folder "
                              "with a kit-manifest.json.\n" + design_source._legacy_message(explicit))
        if not explicit.is_dir():
            raise DesignError(f"paths.design_tokens: {explicit} does not exist; name a design-system folder with a "
                              "kit-manifest.json, or remove the key to use the docs/ux/package.json pin")
    return design_source.resolve(base, explicit=explicit)


def design_exceptions(cfg: dict) -> dict:
    """The deck's declared local exceptions, `design.exceptions` in config.yaml: NAME: VALUE (or NAME=VALUE items)."""
    declared = (cfg.get("design") or {}).get("exceptions") or {}
    if isinstance(declared, dict):
        return {str(k): str(v) for k, v in declared.items()}
    out = {}
    for item in declared:
        name, sep, value = str(item).partition("=")
        if not sep or not name or not value:
            raise DesignError(f"design.exceptions: expected NAME=VALUE, got {item!r}")
        out[name] = value
    return out


def check_deck(text: str, design, cfg: dict, label) -> dict:
    """Run the shared validator on a built deck; raise RenderRefused with the findings when it fails."""
    report = check_render.check(text, design, design_exceptions(cfg))
    if not report["ok"]:
        raise RenderRefused(f"the deck breaks the design ({len(report['findings'])} finding(s)); nothing was written:\n"
                            + check_render.format_text(report, label))
    return report


def provenance_summary(design, report: dict) -> str:
    prov = design.provenance
    ident = prov["designSystem"]
    source = ident["source"] if ident["source"] == "base" else \
        f"{ident.get('name') or ident.get('path')}{'@' + ident['version'] if ident.get('version') else ''}"
    lines = [f"design {source}"]
    for origin in ("design-system", "base"):
        mods = [m for m, o in prov["modules"].items() if o == origin]
        if mods:
            lines.append(f"{origin}: {', '.join(mods)}")
    lines += [f"exception {e['name']}={e['value']}" + ("" if e["known"] else " (not in the design's vocabulary)")
              for e in report["exceptions"]]
    lines += [f"warning: {w}" for w in prov.get("warnings", [])]
    return "\n".join(lines)


def write_atomic(path: Path, text: str) -> None:
    """Write next to the target, then rename into place, so a failed run never leaves a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def write_provenance(output: Path, design) -> Path:
    target = output.with_name(output.name + ".provenance.json")
    write_atomic(target, json.dumps(design.provenance, indent=2) + "\n")
    return target


def load_bibliography(config: dict, base: Path) -> dict:
    """Load context/bibliography.yaml if configured. Returns {key: source_dict}.

    Returns an empty dict silently if the file is absent or the path is not
    configured — so existing projects without a bibliography are unaffected.
    """
    bib_rel = config.get("paths", {}).get("bibliography_file", "")
    if not bib_rel:
        return {}
    bib_path = resolve_path(base, bib_rel)
    if not bib_path.exists():
        return {}
    with open(bib_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("sources", {}) or {}


def format_source_bar(keys: list, bibliography: dict) -> str:
    """Resolve source keys and return a formatted .slide-source-bar div.

    Format per source: "Org · Title (year) — domain"
    Multiple sources joined by " &nbsp;|&nbsp; ".
    Unknown keys emit a build warning and are skipped without failing the build.
    """
    parts = []
    for key in keys:
        key = key.strip()
        if not key:
            continue
        if key not in bibliography:
            print(f"  [WARN] bibliography key not found: '{key}'")
            continue
        s = bibliography[key]
        # Build label: prefer org as primary identifier
        label = s.get("org", "") or s.get("title", key)
        title = s.get("title", "")
        if title and title != label:
            label = f"{label} · {title}"
        year = s.get("year")
        if year:
            label += f" ({year})"
        url = s.get("url", "")
        if url:
            domain = urllib.parse.urlparse(url).netloc.lstrip("www.")
            label += f" — {domain}"
        parts.append(label)
    if not parts:
        return ""
    return (
        '<div class="slide-source-bar">'
        + " &nbsp;|&nbsp; ".join(parts)
        + "</div>"
    )


def inject_before_slide_end(slide_html: str, injection: str) -> str:
    """Insert injection content just before the partial's root closing tag.

    Relies on the invariant that every partial ends with its root closing tag
    (</div> for a slide, </section> for a document section) as the last
    non-whitespace content, so the last closing tag is the root's.
    """
    stripped = slide_html.rstrip()
    m = re.search(r"</(div|section|article)>$", stripped)
    if m:
        return stripped[: m.start()] + injection + f"\n{m.group(0)}\n"
    return slide_html  # fallback: return unchanged if invariant not met


def canvas_size(cfg: dict, design) -> tuple:
    """(width, height) in px of the slide canvas: config.yaml `canvas:` when the deck sets it, else the
    design's slide-frame roles --slide-width and --slide-height. build.py and render.py share it."""
    canvas = cfg.get("canvas") or {}
    if canvas.get("width") and canvas.get("height"):
        return int(canvas["width"]), int(canvas["height"])
    size = []
    for role in ("--slide-width", "--slide-height"):
        value = role_value(design, role)
        m = re.fullmatch(r"(\d+(?:\.\d+)?)px", value.strip())
        if not m:
            raise DesignError(f"the design's slide-frame role {role} is {value!r}; it must be a length in px "
                              "(or set canvas: width and height in config.yaml)")
        size.append(round(float(m.group(1))))
    return size[0], size[1]


def has_logo(design) -> bool:
    return any("url(" in design.brand.get(role, "") for role in ("--brand-logo-on-light", "--brand-logo-on-dark"))


def slide_footer(design, number: str, level: str = "") -> str:
    """The footer row of the slide frame: the brand logo, the legal line, then at the right the deck's
    classification label `level` and the slide number. The logo image is the design layer's
    --brand-logo-on-light (one copy, not one per slide); an empty row is not emitted, so a design with no brand,
    no classification and no numbering gets no footer."""
    cells = []
    if has_logo(design):
        cells.append('<span class="slide-logo" data-brand-asset aria-hidden="true"></span>')
    legal = css_string(design.brand.get("--brand-legal", ""))
    if legal:
        cells.append(f'<span class="slide-legal">{html.escape(legal)}</span>')
    if level:
        cells.append(f'<span class="slide-classification">{html.escape(level)}</span>')
    if number:
        cells.append(f'<span class="slide-number">{html.escape(number)}</span>')
    return f'<div class="slide-footer">{"".join(cells)}</div>' if cells else ""


THEMES = ("light", "dark")
# A partial's root tag (after any leading comments) and its class attribute.
ROOT_CLASS = re.compile(r'^(\s*(?:<!--.*?-->\s*)*<(?:div|section|article)\b[^>]*?\bclass=")([^"]*)(")', re.S)


def deck_theme(cfg: dict) -> str:
    """config.yaml `theme:`, light when absent; `dark` marks every slide, or every page of a document, dark."""
    theme = str(cfg.get("theme") or "light").strip().lower()
    if theme not in THEMES:
        raise DesignError(f"config.yaml theme: {cfg.get('theme')!r} is not a theme; use light or dark")
    return theme


def is_dark(partial: str) -> bool:
    """True when the partial's root element carries the `dark` class."""
    m = ROOT_CLASS.match(partial)
    return bool(m) and "dark" in m.group(2).split()


def mark_dark(partial: str) -> str:
    """The partial with `dark` added to its root element's classes."""
    if is_dark(partial):
        return partial
    return ROOT_CLASS.sub(lambda m: m.group(1) + f"{m.group(2)} dark".strip() + m.group(3), partial, count=1)


def make_dark_css(design, document: bool = False) -> str:
    """The kit's dark layer, emitted only when a slide or the deck is dark. Inside `.slide.dark` and `.doc.dark`
    every role the dark module mirrors reads its --dark- twin, and each --kit-on-<fill> is chosen again against
    the dark pairs (a custom property inherits its value computed on :root, so the light choice would stay).
    `document` adds the dark page: the screen around the sheet and the printed page background."""
    contract = design_source._contract()
    mirror = design_source.dark_mirror(contract)
    light = {twin: role for role, twin in mirror.items()}
    chosen = design_source.fill_text("".join(design.css.values()), contract["modules"]["dark"]["pairs"])
    remap = [f"  {role}: var({twin});" for role, twin in mirror.items()]
    remap += [f"  {design_source.kit_on(light[fill])}: var({text});" for fill, text in chosen.items() if fill in light]
    css = ("/* ── Kit: dark slides and pages, every mirrored role read from its dark twin ── */\n"
           ".slide.dark, .doc.dark {\n" + "\n".join(remap) + "\n}\n"
           ".slide.dark .slide-logo { background-image: var(--brand-logo-on-dark); }\n"
           ".dark .dark-key { background: var(--dark-key-fill); box-shadow: var(--dark-key-edge); "
           "color: var(--dark-ink); }\n"
           ".dark .dark-accent { color: var(--dark-accent-text); }\n")
    if document:
        # Chromium paints a PDF page's margins, where the running header and footer sit, from @page only
        css += (".doc.dark { color: var(--ink); }\n"
                "html, body { background: var(--dark-canvas-bg); }\n"
                "@page { background: var(--dark-print-bg); }\n"
                "@media print {\n"
                "  html, body { background: var(--dark-print-bg); }\n"
                "  .doc.dark { background: var(--print-bg); }\n"
                "}\n")
    return css


def make_classification_css() -> str:
    """The classification cell of the footer row, emitted only for a deck that declares one: grouped with the
    number at the right, in the frame's tertiary role, mono and in capitals. It comes before the deck's
    styles.css, so a deck can restyle it."""
    return ("/* Kit: the deck's classification, at the right of the footer row before the number */\n"
            ".slide-classification {\n"
            "  margin-left: auto;\n"
            "  flex: none;\n"
            "  font-family: var(--font-mono);\n"
            "  text-transform: uppercase;\n"
            "  color: var(--tertiary);\n"
            "}\n"
            ".slide-classification + .slide-number { margin-left: 0; }\n")


# The frame owns the number and the footer row: a partial's legacy `<div class="slide-number">`
# placeholder and a footer row left by split.py are removed before the frame is injected.
LEGACY_NUMBER = re.compile(r'\s*<div\s+class="slide-number"\s*>.*?</div>', re.S)
OLD_FOOTER = re.compile(r'\s*<div\s+class="slide-footer"[^>]*>.*?</div>', re.S)


def make_baseline_css(canvas_override: tuple = None) -> str:
    """Deck behaviour CSS. The frame itself (canvas, section label, footer row, source bar) is the
    design's slide-frame module, inlined in the design layer."""
    override = (f":root {{ --slide-width: {canvas_override[0]}px; --slide-height: {canvas_override[1]}px; }}\n"
                if canvas_override else "")
    return override + f"""\
/* ── Baseline: controls hint ── */
.controls-hint {{
  text-align: center;
  padding: 10px 0 6px;
  font-family: system-ui, sans-serif;
  font-size: 12px;
  color: var(--muted);
  user-select: none;
}}
.controls-hint kbd {{
  display: inline-block;
  padding: 1px 6px;
  border: 1px solid var(--border);
  border-radius: 3px;
  font-size: 11px;
  background: var(--surface-2);
  color: var(--ink);
}}
/* ── Baseline: presentation mode ── */
body.presenting {{
  background: var(--ink);
  overflow: hidden;
}}
body.presenting .controls-hint {{ display: none; }}
body.presenting .slide:not(.active) {{ display: none; }}
body.presenting .slide.active {{
  position: fixed;
  top: 50%;
  left: 50%;
}}
/* ── Baseline: mobile responsive scaling ── */
:root {{ --kit-slide-scale: 1; }}
@media (max-width: 980px) {{
  body:not(.presenting) {{
    padding: 1rem 0;
    gap: 1rem;
  }}
  body:not(.presenting) .slide {{
    transform: scale(var(--kit-slide-scale));
    transform-origin: top center;
    margin-bottom: calc(var(--slide-height) * (var(--kit-slide-scale) - 1));
  }}
}}
"""


def make_baseline_js(canvas_w: int) -> str:
    return f"""\
// ── Baseline: mobile responsive scaling ──
(function() {{
  function setMobileScale() {{
    if (window.innerWidth < 980) {{
      var scale = (window.innerWidth - 16) / {canvas_w};
      document.documentElement.style.setProperty('--kit-slide-scale', scale);
    }} else {{
      document.documentElement.style.removeProperty('--kit-slide-scale');
    }}
  }}
  setMobileScale();
  window.addEventListener('resize', setMobileScale);
}})();
"""


def build_head(cfg: dict) -> str:
    """The document head. Fonts come only from the design's @font-face rules, inlined in
    the design layer; the 1.x `fonts:` key (a Google Fonts link) is read only to warn."""
    if cfg.get("fonts"):
        print("  [WARN] config.yaml fonts: is no longer used and loads nothing: fonts come from the design's "
              "@font-face rules. For a Google face, declare it in the project's design subset `type` module.")
    scripts = "\n".join(
        f'<script src="{url}"></script>'
        for url in cfg.get("external_scripts", [])
    )
    # Optional custom <meta> tags (e.g. rights / author / licence provenance).
    # config.yaml: meta: [{name: author, content: "..."}, ...]
    meta_tags = "\n".join(
        f'<meta name="{html.escape(str(m["name"]), quote=True)}" '
        f'content="{html.escape(str(m["content"]), quote=True)}">'
        for m in cfg.get("meta", [])
        if isinstance(m, dict) and m.get("name") and m.get("content") is not None
    )
    if meta_tags:
        meta_tags += "\n"
    lang = html.escape(str(cfg.get("lang", "en")), quote=True)
    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="{lang}">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cfg.get("title", "Presentation")}</title>
    {meta_tags}{scripts}
    """)


def build(config_path: Path, output_override: str = None):
    cfg = load_config(config_path)
    base = config_path.parent

    # All paths resolve relative to the config file
    slides_dir = resolve_path(base, cfg["paths"]["slides_dir"])
    styles_path = resolve_path(base, cfg["paths"]["styles_file"])
    script_path = resolve_path(base, cfg["paths"]["script_file"])
    output_dir = resolve_path(base, cfg["paths"]["output_dir"])
    output_file = output_dir / cfg["paths"]["output_filename"]

    if output_override:
        output_file = Path(output_override).resolve()
        output_dir = output_file.parent

    # `mode: document` swaps the fixed-canvas slide baseline for a paginated,
    # flowing document (A4 by default) — same partial/stitch model, no canvas.
    is_doc = str(cfg.get("mode", "slides")).lower() == "document"
    unit = "pages" if is_doc else "slides"

    print(f"[BUILD] Config:  {config_path}")
    print(f"[BUILD] Mode:    {'document' if is_doc else 'slides'}")
    print(f"[BUILD] Partials: {slides_dir}")
    print(f"[BUILD] Output:  {output_file}")

    # Bibliography (optional — empty dict if absent or not configured)
    bibliography = load_bibliography(cfg, base)
    if bibliography:
        print(f"[BUILD] Sources: {len(bibliography)} entries in bibliography")

    # Design: resolved once (pin, folder or base theme); a refusal raises DesignError.
    design = resolve_design(cfg, base)

    # Head
    parts = [build_head(cfg)]

    if is_doc:
        geom = page_geometry(cfg)
        baseline_css = make_document_css(geom)
        baseline_js = ""
        print(f"[BUILD] Page:    {geom['size']} {geom['orientation']}, margins "
              f"{geom['margin']['top']} {geom['margin']['right']} {geom['margin']['bottom']} {geom['margin']['left']}")
    else:
        # Canvas: the design's slide-frame module, unless config.yaml sets `canvas:` for this deck
        canvas_w, canvas_h = canvas_size(cfg, design)
        overridden = bool((cfg.get("canvas") or {}).get("width") and (cfg.get("canvas") or {}).get("height"))
        print(f"[BUILD] Canvas:  {canvas_w}x{canvas_h} px ({'config.yaml canvas' if overridden else 'design slide-frame'})")
        baseline_css = make_baseline_css((canvas_w, canvas_h) if overridden else None)
        baseline_js  = make_baseline_js(canvas_w)

    theme = deck_theme(cfg)
    level = classification.label(cfg.get("classification"), cfg.get("lang", "en"))
    css = read_file(styles_path)
    body = []

    # Slides / pages (`pages:` is accepted as an alias of `slides:` in document mode)
    slide_entries = cfg.get("slides") or cfg.get("pages") or []
    total = len(slide_entries)
    numbering = cfg.get("numbering", {})
    # Document page numbers are Chromium's job at render time (partial count is
    # not page count), so .slide-number rewriting is a slides-only feature.
    num_enabled = numbering.get("enabled", True) and not is_doc
    num_format = numbering.get("format", "{current} / {total}")
    dropped_numbers = 0

    dark_slides = 0
    for idx, entry in enumerate(slide_entries, start=1):
        filename = entry["file"] if isinstance(entry, dict) else entry
        label = entry.get("label", "") if isinstance(entry, dict) else ""
        slide_path = slides_dir / filename

        print(f"  [{idx:02d}/{total}] {filename}", end="")
        html = read_file(slide_path)
        if not html:
            print(" (MISSING)")
            continue

        if not is_doc:
            html, dropped = LEGACY_NUMBER.subn("", html)
            dropped_numbers += bool(dropped)
            html = OLD_FOOTER.sub("", html)
            if theme == "dark":
                html = mark_dark(html)
            dark_slides += is_dark(html)

        # Inject source bar if the slide declares data-sources and bibliography exists
        if bibliography:
            sources_match = re.search(
                r'data-sources=["\']([^"\']+)["\']', html
            )
            if sources_match:
                keys = sources_match.group(1).split(",")
                source_bar = format_source_bar(keys, bibliography)
                if source_bar:
                    html = inject_before_slide_end(html, "\n" + source_bar)

        # The slide frame's footer row: logo, legal line, then the classification and the number at the right
        if not is_doc:
            footer = slide_footer(design, num_format.format(current=idx, total=total) if num_enabled else "", level)
            if footer:
                html = inject_before_slide_end(html, "\n" + footer)

        body.append(f"\n<!-- slide {idx}: {label} -->\n")
        body.append(html.strip())
        body.append("\n")
        print(" OK")

    # Styles, in cascade order:
    #   1. the resolved design (fonts, then every module, base first and the design system after it;
    #      `dark` only when a slide or the deck is dark), marked data-design-layer: the only place
    #      literals may live
    #   2. for a classified deck the classification cell, then the deck's own styles.css (components, roles
    #      only), the baseline CSS and, for a dark slide or page, the kit's dark layer
    dark = dark_slides > 0 or (is_doc and theme == "dark")
    design_layer = "\n".join(design.fonts + [c for m, c in design.css.items() if c and (m != "dark" or dark)])
    parts.append("<style data-design-layer>\n" + design_layer + "\n</style>")
    cell_css = make_classification_css() if level and not is_doc else ""
    layers = [c for c in (cell_css, css, baseline_css, make_dark_css(design, is_doc) if dark else "") if c]
    parts.append("<style>\n" + "\n".join(layers) + "\n</style>")
    parts.append("</head>\n<body>\n")

    # Controls hint (slides only: a document has no presentation mode)
    if not is_doc:
        parts.append(textwrap.dedent("""\
        <div class="controls-hint">
          Press <kbd>F</kbd> for fullscreen presentation &middot; <kbd>&larr;</kbd> <kbd>&rarr;</kbd> to navigate &middot; <kbd>Esc</kbd> to exit
        </div>
        """))
    else:
        parts.append('<div class="doc dark">\n' if dark else '<div class="doc">\n')
    parts += body
    if is_doc:
        parts.append("</div>\n")
    if dropped_numbers:
        print(f"  [NOTE] {dropped_numbers} partial(s) carry a <div class=\"slide-number\"> placeholder; the slide "
              "frame now numbers every slide in its footer row, so the placeholder was left out")

    # Script (baseline responsive + project; document mode ships no baseline JS)
    js = read_file(script_path) if script_path.exists() else ""
    if baseline_js or js:
        parts.append(f"\n<script>\n{baseline_js}\n{js}\n</script>\n")

    parts.append("</body>\n</html>\n")

    # Check, then write: a deck that breaks the design writes nothing.
    final = "\n".join(parts)
    report = check_deck(final, design, cfg, output_file)
    write_atomic(output_file, final)
    prov_file = write_provenance(output_file, design)

    size_kb = output_file.stat().st_size / 1024
    print("\n[CHECK] PASS: the deck uses only the design's roles")
    print("[PROVENANCE] " + provenance_summary(design, report).replace("\n", "\n             "))
    print(f"[PROVENANCE] written to {prov_file.name}")
    print(f"\n[DONE] {output_file.name} ({size_kb:.1f} KB, {total} {unit})")


def main():
    parser = argparse.ArgumentParser(
        description="Build a single-file HTML presentation from slide partials."
    )
    parser.add_argument(
        "--config", "-c",
        required=True,
        help="Path to the project's config.yaml",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Override output file path",
    )
    args = parser.parse_args()
    try:
        build(Path(args.config).resolve(), args.output)
    except (DesignError, RenderRefused) as exc:
        print(f"[BUILD] REFUSED: {exc}", file=sys.stderr)
        sys.exit(exc.code)


if __name__ == "__main__":
    main()
