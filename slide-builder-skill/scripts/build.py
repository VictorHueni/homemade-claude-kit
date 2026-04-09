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
import re
import sys
import textwrap
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install it with: pip install pyyaml")
    sys.exit(1)


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


def build_font_url(fonts: list) -> str:
    if not fonts:
        return ""
    families = []
    for font in fonts:
        family = font["family"].replace(" ", "+")
        weights = ";".join(str(w) for w in font.get("weights", [400]))
        families.append(f"family={family}:wght@{weights}")
    return f"https://fonts.googleapis.com/css2?{'&'.join(families)}&display=swap"


BASELINE_CSS = """\
/* ── Baseline: mobile responsive scaling ── */
@media (max-width: 980px) {
  body:not(.presenting) {
    padding: 1rem 0;
    gap: 1rem;
  }
  body:not(.presenting) .slide {
    transform: scale(var(--slide-scale, 1));
    transform-origin: top center;
    margin-bottom: calc(540px * (var(--slide-scale, 1) - 1));
  }
}
"""

BASELINE_JS = """\
// ── Baseline: mobile responsive scaling ──
(function() {
  function setMobileScale() {
    if (window.innerWidth < 980) {
      var scale = (window.innerWidth - 16) / 960;
      document.documentElement.style.setProperty('--slide-scale', scale);
    } else {
      document.documentElement.style.removeProperty('--slide-scale');
    }
  }
  setMobileScale();
  window.addEventListener('resize', setMobileScale);
})();
"""


def build_head(cfg: dict) -> str:
    font_url = build_font_url(cfg.get("fonts", []))
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
    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{cfg.get("title", "Presentation")}</title>
    {font_tags}{scripts}
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

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[BUILD] Config:  {config_path}")
    print(f"[BUILD] Slides:  {slides_dir}")
    print(f"[BUILD] Output:  {output_file}")

    # Head
    parts = [build_head(cfg)]

    # Styles (project + baseline responsive)
    css = read_file(styles_path)
    if css:
        parts.append(f"<style>\n{css}\n{BASELINE_CSS}\n</style>")
    else:
        parts.append(f"<style>\n{BASELINE_CSS}\n</style>")
    parts.append("</head>\n<body>\n")

    # Controls hint
    parts.append(textwrap.dedent("""\
    <div class="controls-hint">
      Press <kbd>F</kbd> for fullscreen presentation &middot; <kbd>&larr;</kbd> <kbd>&rarr;</kbd> to navigate &middot; <kbd>Esc</kbd> to exit
    </div>
    """))

    # Slides
    slide_entries = cfg.get("slides", [])
    total = len(slide_entries)
    numbering = cfg.get("numbering", {})
    num_enabled = numbering.get("enabled", True)
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

        parts.append(f"\n<!-- slide {idx}: {label} -->\n")
        parts.append(html.strip())
        parts.append("\n")
        print(" OK")

    # Script (baseline responsive + project)
    js = read_file(script_path)
    parts.append(f"\n<script>\n{BASELINE_JS}\n{js}\n</script>\n")

    parts.append("</body>\n</html>\n")

    # Write
    final = "\n".join(parts)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final)

    size_kb = output_file.stat().st_size / 1024
    print(f"\n[DONE] {output_file.name} ({size_kb:.1f} KB, {total} slides)")


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
    build(Path(args.config).resolve(), args.output)


if __name__ == "__main__":
    main()
