"""PDF renders (need Playwright and Chromium); run by `make test-pdf`."""
import json
import os
import re
import shutil
import subprocess
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


class ReleaseNoteComputedStyleTest(RenderCase):
    """Chromium draws the report's bold weight, pill radius and breaking accent from the design's roles."""

    NAVY = "#1f2a5c"

    @staticmethod
    def rgb(hex_colour):
        h = hex_colour.lstrip("#")
        return "rgb({}, {}, {})".format(*(int(h[i:i + 2], 16) for i in (0, 2, 4)))

    def computed(self, *extra):
        note = SKILLS / "com-release-note/examples/release-note.complete.md"
        result = run(SKILLS / "com-release-note/scripts/render_pdf.py", note, "--html-only", *extra,
                     "--output", "rn.pdf", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto((self.tmp / "rn.html").as_uri())
            styles = page.evaluate("""() => {
                const cs = (sel) => getComputedStyle(document.querySelector(sel));
                return {title: cs('.report-title').fontWeight, product: cs('.product-name').fontWeight,
                        pill: cs('.product-id').borderTopLeftRadius,
                        breaking: cs('.section--breaking .section-label').color,
                        breakingRule: cs('.section--breaking .section-label').borderBottomColor};
            }""")
            browser.close()
        return styles

    def test_base_theme_keeps_700_999px_and_the_danger_colour(self):
        require_browser(self)
        sys.path.insert(0, str(PLUGIN / "shared"))
        import design_source
        danger = design_source.role_values(design_source.resolve(self.tmp).css["core"])["--danger"]
        styles = self.computed()
        self.assertEqual((styles["title"], styles["product"]), ("700", "700"))
        self.assertEqual(styles["pill"], "999px")
        self.assertEqual(styles["breaking"], self.rgb(danger))
        self.assertEqual(styles["breakingRule"], self.rgb(danger))

    def test_a_design_with_500_6px_and_a_navy_breaking_accent(self):
        require_browser(self)
        folder = self.tmp / "ds"
        shutil.copytree(DESIGNS / "full", folder)
        for name, old, new in (("type.css", "--font-weight-bold: 700;", "--font-weight-bold: 500;"),
                               ("space-shape.css", "--radius-pill: 999px;", "--radius-pill: 6px;"),
                               ("print.css", "--print-page-size: Letter;",
                                f"--print-page-size: Letter; --print-breaking: {self.NAVY};")):
            path = folder / "css" / name
            path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
        styles = self.computed("--design-system", folder)
        self.assertEqual((styles["title"], styles["product"]), ("500", "500"))
        self.assertEqual(styles["pill"], "6px")
        self.assertEqual(styles["breaking"], self.rgb(self.NAVY))
        self.assertEqual(styles["breakingRule"], self.rgb(self.NAVY))


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


class ReproduciblePdfTest(RenderCase):
    """Increment 10 (#106): two PDF renders of the same source are byte-identical, and the Info dates are the
    source date (shared/source_date.py), not Chromium's clock. Skia writes no /ID and no XMP today."""

    EPOCH = {"SOURCE_DATE_EPOCH": "31536000"}           # 1971-01-01T00:00:00Z
    STAMP = b"D:19710101000000+00'00'"

    def assertReproducible(self, first, second, stamp=STAMP):
        a, b = (self.tmp / first).read_bytes(), (self.tmp / second).read_bytes()
        dates = re.findall(rb"/(CreationDate|ModDate) \((D:[^)]*)\)", a)
        self.assertEqual(sorted(d[0] for d in dates), [b"CreationDate", b"ModDate"], dates)
        for name, value in dates:
            self.assertEqual(value, stamp, f"{first}: /{name.decode()} is {value!r}, not the source date")
        self.assertNotRegex(a, rb"/ID\s*\[", "Chromium now writes a document /ID; normalise it")
        self.assertNotIn(b"/Metadata", a, "Chromium now writes XMP metadata; normalise it")
        diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
        self.assertEqual((len(a), diff), (len(b), []), f"{first} and {second} differ")
        prov = [self.tmp / f"{n}.provenance.json" for n in (first, second)]
        if not prov[0].exists():   # the release note writes its provenance beside the HTML
            prov = [self.tmp / f"{Path(n).with_suffix('.html')}.provenance.json" for n in (first, second)]
        self.assertEqual(prov[0].read_bytes(), prov[1].read_bytes())

    def pin_full(self):
        ux = self.tmp / "docs/ux"
        ux.mkdir(parents=True)
        (ux / "package.json").write_text(json.dumps({"dependencies": {"@acme-test/full": f"file:{DESIGNS / 'full'}"}}),
                                         encoding="utf-8")

    def deck(self, mode, recipient=()):
        self.assertEqual(run(SKILLS / "com-slide-deck/scripts/init.py", mode, "--mode", mode, cwd=self.tmp).returncode, 0)
        folder = "pages" if mode == "document" else "slides"
        (self.tmp / f"{mode}/output/{folder}/01.html").write_text(
            '<div class="slide"><h2>Reproducible</h2><p>Same source, same bytes.</p></div>\n', encoding="utf-8")
        cfg = self.tmp / f"{mode}/config.yaml"
        text = cfg.read_text(encoding="utf-8")
        cfg.write_text(re.sub(r"^(slides|pages): \[\]", r'\1:\n  - file: "01.html"', text, flags=re.M),
                       encoding="utf-8")
        build = run(SKILLS / "com-slide-deck/scripts/build.py", "-c", f"{mode}/config.yaml", cwd=self.tmp, env=self.EPOCH)
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        outs = []
        for tag in ("a", "b"):
            result = run(SKILLS / "com-slide-deck/scripts/render.py", "--config", f"{mode}/config.yaml", *recipient,
                         "--output", f"{mode}-{tag}.pdf", cwd=self.tmp, env=self.EPOCH)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            outs.append(result.stdout)
        return outs

    def test_slide_deck(self):
        require_browser(self)
        self.pin_full()
        stdout = self.deck("slides", ("--recipient", "Partner Co"))
        self.assertReproducible("slides-a.pdf", "slides-b.pdf")
        self.assertIn("Prepared for Partner Co · 1971-01-01", stdout[0], "the stamp date is the source date")

    def test_document_deck(self):
        require_browser(self)
        self.pin_full()
        self.deck("document")
        self.assertReproducible("document-a.pdf", "document-b.pdf")

    def test_release_note(self):
        require_browser(self)
        note = SKILLS / "com-release-note/examples/release-note.complete.md"
        for tag in ("a", "b"):
            result = run(SKILLS / "com-release-note/scripts/render_pdf.py", note, "--design-system", DESIGNS / "full",
                         "--output", f"rn-{tag}.pdf", cwd=self.tmp, env=self.EPOCH)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertReproducible("rn-a.pdf", "rn-b.pdf")
        self.assertEqual((self.tmp / "rn-a.html").read_bytes(), (self.tmp / "rn-b.html").read_bytes())

    def test_release_note_without_epoch_takes_the_commit_date(self):
        require_browser(self)
        project = self.tmp / "project"
        project.mkdir()
        shutil.copyfile(SKILLS / "com-release-note/examples/release-note.complete.md", project / "note.md")
        git = ["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
        env = {**os.environ, "GIT_COMMITTER_DATE": "2001-02-03T12:00:00Z", "GIT_AUTHOR_DATE": "2001-02-03T12:00:00Z"}
        for args in (["init", "-q"], ["add", "note.md"], ["commit", "-q", "-m", "note"]):
            subprocess.run(git + args, check=True, env=env, capture_output=True)
        for tag in ("a", "b"):
            result = run(SKILLS / "com-release-note/scripts/render_pdf.py", project / "note.md",
                         "--output", self.tmp / f"rn-{tag}.pdf", cwd=self.tmp,
                         env={"SOURCE_DATE_EPOCH": None, "GIT_CEILING_DIRECTORIES": str(self.tmp)})
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertReproducible("rn-a.pdf", "rn-b.pdf", stamp=b"D:20010203120000+00'00'")


if __name__ == "__main__":
    unittest.main()
