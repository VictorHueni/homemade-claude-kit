"""PDF renders (need Playwright and Chromium); run by `make test-pdf`."""
import json
import re
import unittest
from pathlib import Path

from helpers import SKILLS, RenderCase, run
from pdf_helpers import require_browser


class ReleaseNotePdfTest(RenderCase):
    def test_release_note_example_renders_a_pdf(self):
        require_browser(self)
        note = SKILLS / "com-release-note/examples/release-note.complete.md"
        result = run(SKILLS / "com-release-note/scripts/render_pdf.py", note, "--output", "rn.pdf", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.tmp / "rn.pdf").read_bytes().startswith(b"%PDF"))


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
