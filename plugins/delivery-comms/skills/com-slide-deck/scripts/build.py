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
import design_source  # noqa: E402
from design_source import DesignError  # noqa: E402
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


def build_font_url(fonts: list) -> str:
    if not fonts:
        return ""
    families = []
    for font in fonts:
        family = font["family"].replace(" ", "+")
        weights = ";".join(str(w) for w in font.get("weights", [400]))
        families.append(f"family={family}:wght@{weights}")
    return f"https://fonts.googleapis.com/css2?{'&'.join(families)}&display=swap"


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


def make_baseline_css(canvas_w: int, canvas_h: int) -> str:
    return f"""\
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
/* ── Baseline: source bar ── */
.slide-source-bar {{
  position: absolute;
  bottom: 28px;
  left: 72px;
  right: 52px;
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--muted);
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  pointer-events: none;
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
    margin-bottom: calc({canvas_h}px * (var(--kit-slide-scale) - 1));
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


def build_head(cfg: dict, design_fonts: bool = False) -> str:
    """The document head. Fonts come from the design (inlined @font-face rules); the
    config's `fonts:` Google Fonts link is used only when the design provides none."""
    configured = cfg.get("fonts") or []
    if configured and design_fonts:
        print("  [WARN] config.yaml fonts: is ignored: the design system provides the fonts (inlined, no network)")
        configured = []
    font_url = build_font_url(configured)
    font_tags = ""
    if font_url:
        font_tags = textwrap.dedent(f"""\
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="{font_url}" rel="stylesheet">
        """)
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
    {meta_tags}{font_tags}{scripts}
    """)


def update_slide_numbers(html: str, current: int, total: int, fmt: str) -> str:
    number_text = fmt.format(current=current, total=total)
    return re.sub(
        r'(<div\s+class="slide-number">)(.*?)(</div>)',
        rf"\g<1>{number_text}\g<3>",
        html,
        flags=re.DOTALL,
    )


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
    parts = [build_head(cfg, design_fonts=bool(design.fonts))]

    # Canvas dimensions (used by baseline CSS/JS)
    canvas = cfg.get("canvas", {})
    canvas_w = int(canvas.get("width",  960))
    canvas_h = int(canvas.get("height", 540))
    if is_doc:
        geom = page_geometry(cfg)
        baseline_css = make_document_css(geom)
        baseline_js = ""
        print(f"[BUILD] Page:    {geom['size']} {geom['orientation']}, margins "
              f"{geom['margin']['top']} {geom['margin']['right']} {geom['margin']['bottom']} {geom['margin']['left']}")
    else:
        baseline_css = make_baseline_css(canvas_w, canvas_h)
        baseline_js  = make_baseline_js(canvas_w)

    # Styles, in cascade order:
    #   1. the resolved design (fonts, then every module, base first and the design
    #      system after it), marked data-design-layer: the only place literals may live
    #   2. the deck's own styles.css (components, roles only) and the baseline CSS
    design_layer = "\n".join(design.fonts + [c for c in design.css.values() if c])
    parts.append("<style data-design-layer>\n" + design_layer + "\n</style>")
    css = read_file(styles_path)
    layers = [c for c in (css, baseline_css) if c]
    parts.append("<style>\n" + "\n".join(layers) + "\n</style>")
    parts.append("</head>\n<body>\n")

    # Controls hint (slides only — a document has no presentation mode)
    if not is_doc:
        parts.append(textwrap.dedent("""\
        <div class="controls-hint">
          Press <kbd>F</kbd> for fullscreen presentation &middot; <kbd>&larr;</kbd> <kbd>&rarr;</kbd> to navigate &middot; <kbd>Esc</kbd> to exit
        </div>
        """))
    else:
        parts.append('<div class="doc">\n')

    # Slides / pages (`pages:` is accepted as an alias of `slides:` in document mode)
    slide_entries = cfg.get("slides") or cfg.get("pages") or []
    total = len(slide_entries)
    numbering = cfg.get("numbering", {})
    # Document page numbers are Chromium's job at render time (partial count is
    # not page count), so .slide-number rewriting is a slides-only feature.
    num_enabled = numbering.get("enabled", True) and not is_doc
    num_format = numbering.get("format", "{current} / {total}")

    for idx, entry in enumerate(slide_entries, start=1):
        filename = entry["file"] if isinstance(entry, dict) else entry
        label = entry.get("label", "") if isinstance(entry, dict) else ""
        slide_path = slides_dir / filename

        print(f"  [{idx:02d}/{total}] {filename}", end="")
        html = read_file(slide_path)
        if not html:
            print(" (MISSING)")
            continue

        if num_enabled:
            html = update_slide_numbers(html, idx, total, num_format)

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

        parts.append(f"\n<!-- slide {idx}: {label} -->\n")
        parts.append(html.strip())
        parts.append("\n")
        print(" OK")

    if is_doc:
        parts.append("</div>\n")

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
