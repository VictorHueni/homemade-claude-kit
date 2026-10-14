"""PDF renders (need Playwright and Chromium); run by `make test-pdf`."""
import unittest

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


if __name__ == "__main__":
    unittest.main()
