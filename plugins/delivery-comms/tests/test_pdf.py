"""PDF renders (need Playwright and Chromium); run by `make test-pdf`."""
import json
import re
import sys
import unittest
from pathlib import Path

from helpers import SKILLS, RenderCase, run
from pdf_helpers import require_browser

PLUGIN = Path(__file__).resolve().parent.parent
DESIGNS = PLUGIN / "tests/fixtures/design-systems"


class ReleaseNotePdfTest(RenderCase):
    def test_release_note_example_renders_a_pdf(self):
        require_browser(self)
        note = SKILLS / "com-release-note/examples/release-note.complete.md"
        result = run(SKILLS / "com-release-note/scripts/render_pdf.py", note, "--output", "rn.pdf", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.tmp / "rn.pdf").read_bytes().startswith(b"%PDF"))
        self.assertTrue((self.tmp / "rn.html.provenance.json").is_file())

    def test_page_size_comes_from_the_print_module(self):
        # Increment 09: the full fixture's print module sets Letter; the base theme is A4
        require_browser(self)
        note = SKILLS / "com-release-note/examples/release-note.complete.md"
        for name, extra, expected in (("full", ("--design-system", DESIGNS / "full"), (612, 792)),
                                      ("base", (), (595, 842))):
            with self.subTest(design=name):
                result = run(SKILLS / "com-release-note/scripts/render_pdf.py", note, *extra,
                             "--output", f"{name}.pdf", cwd=self.tmp)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                boxes = re.findall(rb"/MediaBox\s*\[\s*0 0 ([\d.]+) ([\d.]+)\s*\]",
                                   (self.tmp / f"{name}.pdf").read_bytes())
                self.assertTrue(boxes)
                for w, h in boxes:   # Chromium rounds the page box to whole CSS pixels: within 1 pt
                    self.assertLessEqual(abs(float(w) - expected[0]), 1, (w, h))
                    self.assertLessEqual(abs(float(h) - expected[1]), 1, (w, h))


class PrintChromePdfTest(RenderCase):
    def test_full_logo_in_the_page_chrome_decodes_in_chromium(self):
        # The footer template is a separate Chromium document: the logo must be a data URI it can draw.
        require_browser(self)
        sys.path.insert(0, str(PLUGIN / "shared"))
        import design_source
        import print_chrome
        from playwright.sync_api import sync_playwright
        design = design_source.resolve(self.tmp, explicit=DESIGNS / "full")
        footer = print_chrome.footer_template(design, "Release note", "16mm")
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(footer)
            width = page.evaluate("() => { const i = document.querySelector('img'); "
                                  "return i && i.complete ? i.naturalWidth : 0; }")
            browser.close()
        self.assertGreater(width, 0)

    def test_full_document_deck_renders_with_branded_chrome(self):
        require_browser(self)
        ux = self.tmp / "docs/ux"
        ux.mkdir(parents=True)
        (ux / "package.json").write_text(json.dumps({"dependencies": {"@acme-test/full": f"file:{DESIGNS / 'full'}"}}),
                                         encoding="utf-8")
        self.assertEqual(run(SKILLS / "com-slide-deck/scripts/init.py", "doc", "--mode", "document",
                             cwd=self.tmp).returncode, 0)
        build = run(SKILLS / "com-slide-deck/scripts/build.py", "-c", "doc/config.yaml", cwd=self.tmp)
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        result = run(SKILLS / "com-slide-deck/scripts/render.py", "--config", "doc/config.yaml",
                     "--output", "doc.pdf", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.tmp / "doc.pdf").read_bytes().startswith(b"%PDF"))


class SlideDeckPdfTest(RenderCase):
    def test_scaffolded_deck_renders_a_pdf(self):
        require_browser(self)
        self.assertEqual(run(SKILLS / "com-slide-deck/scripts/init.py", "deck", cwd=self.tmp).returncode, 0)
        build = run(SKILLS / "com-slide-deck/scripts/build.py", "-c", "deck/config.yaml", cwd=self.tmp)
        self.assertEqual(build.returncode, 0, build.stderr)
        result = run(SKILLS / "com-slide-deck/scripts/render.py", "--config", "deck/config.yaml",
                     "--output", "deck.pdf", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.tmp / "deck.pdf").read_bytes().startswith(b"%PDF"))
        self.assertTrue((self.tmp / "deck.pdf.provenance.json").is_file())

    def test_recipient_stamped_deck_and_footer_left_document_render(self):
        require_browser(self)
        for mode in ("slides", "document"):
            with self.subTest(mode=mode):
                folder = f"deck-{mode}"
                self.assertEqual(run(SKILLS / "com-slide-deck/scripts/init.py", folder, "--mode", mode,
                                     cwd=self.tmp).returncode, 0)
                if mode == "document":
                    cfg = self.tmp / folder / "config.yaml"
                    cfg.write_text(cfg.read_text(encoding="utf-8") + '\npage:\n  footer_left: "{author} · v1"\n',
                                   encoding="utf-8")
                build = run(SKILLS / "com-slide-deck/scripts/build.py", "-c", f"{folder}/config.yaml", cwd=self.tmp)
                self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
                result = run(SKILLS / "com-slide-deck/scripts/render.py", "--config", f"{folder}/config.yaml",
                             "--recipient", "Partner Co", "--output", f"{folder}.pdf", cwd=self.tmp)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("Prepared for Partner Co", result.stdout)
                self.assertTrue((self.tmp / f"{folder}.pdf").read_bytes().startswith(b"%PDF"))

    def test_full_deck_prints_on_the_design_canvas_with_its_frame(self):
        # Increment 06: the page size is the design's slide canvas (1280x720 px = 960x540 pt); the footer row
        # with the logo, legal line and number is part of the slide, so it prints with it.
        require_browser(self)
        fixture = Path(__file__).resolve().parent / "fixtures/design-systems/full"
        ux = self.tmp / "docs/ux"
        ux.mkdir(parents=True)
        (ux / "package.json").write_text(json.dumps({"dependencies": {"@acme-test/full": f"file:{fixture}"}}),
                                         encoding="utf-8")
        self.assertEqual(run(SKILLS / "com-slide-deck/scripts/init.py", "deck", cwd=self.tmp).returncode, 0)
        cfg = self.tmp / "deck/config.yaml"
        for i in (1, 2):
            (self.tmp / f"deck/output/slides/0{i}.html").write_text(
                f'<div class="slide s-{i}"><div class="slide-label">Part {i}</div><h2>Slide {i}</h2></div>\n',
                encoding="utf-8")
        cfg.write_text(re.sub(r"^slides: \[\]", 'slides:\n  - file: "01.html"\n  - file: "02.html"',
                              cfg.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
        build = run(SKILLS / "com-slide-deck/scripts/build.py", "-c", "deck/config.yaml", cwd=self.tmp)
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        result = run(SKILLS / "com-slide-deck/scripts/render.py", "--config", "deck/config.yaml",
                     "--recipient", "Partner Co", "--output", "deck.pdf", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        pdf = (self.tmp / "deck.pdf").read_bytes()
        boxes = re.findall(rb"/MediaBox\s*\[\s*0 0 ([\d.]+) ([\d.]+)\s*\]", pdf)
        self.assertEqual(len(boxes), 2, boxes)
        for w, h in boxes:
            self.assertEqual((round(float(w)), round(float(h))), (960, 540))


if __name__ == "__main__":
    unittest.main()
