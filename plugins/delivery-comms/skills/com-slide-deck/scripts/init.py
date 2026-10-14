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


DOC_SCRIPT = """\
// Document mode: no presentation controls. Only icon initialisation.
if (typeof lucide !== 'undefined') lucide.createIcons();
"""


def init_project(target: Path, name: str = "", author: str = "", mode: str = "slides"):
    if target.exists() and any(target.iterdir()):
        print(f"[WARN] Target directory is not empty: {target}")
        print("       Existing files will NOT be overwritten.\n")

    is_doc = mode == "document"

    # Create folder structure
    dirs = [
        "context",
        "design",
        "output/document" if is_doc else "output/slide-deck",
        "output/pages" if is_doc else "output/slides",
        "output/prototypes",
    ]
    for d in dirs:
        (target / d).mkdir(parents=True, exist_ok=True)

    # Copy templates (never overwrite existing files)
    copies = [
        ("brief-template.md",          "context/brief-template.md"),
        ("brief-template.md",          "context/brief.md"),
        ("design-system-template.md",  "design/design-system-template.md"),
        ("design-system-template.md",  "design/design-system.md"),
        ("bibliography-template.yaml", "context/bibliography-template.yaml"),
        ("bibliography-template.yaml", "context/bibliography.yaml"),
        ("config-template.yaml",       "config.yaml"),
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

    # Create placeholder / default files (never overwrite existing)
    DEFAULT_SCRIPT = """\
// ── Initialize Lucide icons (no-op if library not loaded) ───
if (typeof lucide !== 'undefined') lucide.createIcons();

// ── Fullscreen presentation mode ────────────────────────────
// Keyboard controls:
//   F          → enter fullscreen presentation
//   Esc        → exit
//   → / ↓ / Space  → next slide
//   ← / ↑          → previous slide
(function () {
  var slides = Array.from(document.querySelectorAll('.slide'));
  if (!slides.length) return;

  var current   = 0;
  var presenting = false;

  // Read canvas dimensions from the first slide element so this
  // script works regardless of the canvas size set in config.yaml.
  var W = slides[0].offsetWidth;
  var H = slides[0].offsetHeight;

  function scaleSlides() {
    var margin = 40;
    var scale  = Math.min(
      (window.innerWidth  - margin * 2) / W,
      (window.innerHeight - margin * 2) / H
    );
    slides.forEach(function (s) {
      s.style.transform = presenting
        ? 'translate(-50%, -50%) scale(' + scale + ')'
        : '';
    });
  }

  function showSlide(n) {
    current = Math.max(0, Math.min(n, slides.length - 1));
    slides.forEach(function (s, i) {
      s.classList.toggle('active', i === current);
    });
  }

  function enter() {
    presenting = true;
    document.body.classList.add('presenting');
    showSlide(current);
    if (document.documentElement.requestFullscreen) {
      document.documentElement.requestFullscreen();
    }
    setTimeout(scaleSlides, 100);
  }

  function exit() {
    presenting = false;
    document.body.classList.remove('presenting');
    slides.forEach(function (s) {
      s.classList.remove('active');
      s.style.transform = '';
    });
    if (document.fullscreenElement && document.exitFullscreen) {
      document.exitFullscreen();
    }
  }

  window.addEventListener('resize', function () {
    if (presenting) scaleSlides();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'f' || e.key === 'F') {
      if (!presenting) enter();
    } else if (e.key === 'Escape') {
      if (presenting) exit();
    } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
      if (presenting) { e.preventDefault(); showSlide(current + 1); }
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      if (presenting) showSlide(current - 1);
    }
  });

  // Catch browser-native Esc (exits fullscreen before keydown fires)
  document.addEventListener('fullscreenchange', function () {
    if (!document.fullscreenElement && presenting) exit();
  });
})();
"""

    DEFAULT_STYLES = """/*
 * Deck styles. The palette, typography and every other design value come from the
 * project's design system, resolved by build.py and inlined BEFORE this file: the
 * docs/ux/package.json pin (or paths.design_tokens), else the kit's base theme.
 * Use contract roles only, var(--ink), var(--surface), var(--accent), var(--muted),
 * var(--font-body), var(--font-mono): build.py refuses a literal colour or a custom
 * property outside the contract. A deliberate local value is declared in config.yaml
 * under design.exceptions. Contract roles: plugins/delivery-comms/contract/README.md.
 */

/* Component styles go here. */
"""

    placeholders = [
        ("design/styles.css", DEFAULT_STYLES),
        ("design/script.js",  DOC_SCRIPT if is_doc else DEFAULT_SCRIPT),
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
    if config_path.exists() and (name or author or is_doc):
        text = config_path.read_text(encoding="utf-8")
        if name:
            text = text.replace('title: "Presentation Title"', f'title: "{name}"')
        if author:
            text = text.replace('author: "Author"', f'author: "{author}"')
        if is_doc:
            text = text.replace("mode: slides", "mode: document")
            text = text.replace('slides_dir:        "output/slides"', 'slides_dir:        "output/pages"')
            text = text.replace('output_dir:        "output/slide-deck"', 'output_dir:        "output/document"')
            text = text.replace('output_filename:   "presentation.html"', 'output_filename:   "document.html"')
        config_path.write_text(text, encoding="utf-8")

    # Print summary
    skill_rel = SKILL_DIR
    print(f"\n[DONE] Project scaffolded at: {target}")
    print(f"\nNext steps:")
    print(f"  1. Fill in  {target / 'context/brief.md'}")
    print(f"  2. Note deck components (optional) in  {target / 'design/design-system.md'}")
    print(f"  3. Create {'pages' if is_doc else 'slides'} in  {target / ('output/pages/' if is_doc else 'output/slides/')}")
    print(f"  4. Build with:")
    print(f"       python3 {skill_rel / 'scripts/build.py'} --config {target / 'config.yaml'}")
    print(f"  5. Record the verdict on the built HTML:")
    print(f"       python3 {skill_rel / 'scripts/shared/check_render.py'} --record <output>.verdict.txt <output>")


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
    parser.add_argument(
        "--mode", "-m",
        choices=["slides", "document"],
        default="slides",
        help="slides (16:9 deck, default) or document (paginated A4/Letter)",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()
    init_project(target, name=args.name, author=args.author, mode=args.mode)


if __name__ == "__main__":
    main()
