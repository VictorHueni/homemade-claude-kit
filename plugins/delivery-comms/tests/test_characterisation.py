"""Characterisation of today's rendering with no project design.

Pins the behaviour before the modular design contract moves it (Plan-0005
increment 01): each renderer builds, links every CSS layer in today's order and
falls back to the shipped accent. GoldenTest holds every fixture render to the
computed styles and PDF pixels of 2.0.0 (tests/goldens.py).
"""
import unittest

import goldens
from helpers import FALLBACK_ACCENT, SKILLS, RenderCase, run

FALLBACK_MARKER = "core.css — shipped neutral defaults"


class SlideDeckTest(RenderCase):
    def test_scaffolded_deck_builds_on_fallback_tokens(self):
        init = run(SKILLS / "com-slide-deck/scripts/init.py", "deck", cwd=self.tmp)
        self.assertEqual(init.returncode, 0, init.stderr)
        build = run(SKILLS / "com-slide-deck/scripts/build.py", "-c", "deck/config.yaml", cwd=self.tmp)
        self.assertEqual(build.returncode, 0, build.stderr)
        html = (self.tmp / "deck/output/slide-deck/presentation.html").read_text(encoding="utf-8")
        self.assertLayersInOrder(html, ["<style data-design-layer>", FALLBACK_MARKER, "Deck styles."])
        self.assertIn(FALLBACK_ACCENT, html)
        self.assertNotIn("fonts.googleapis.com", html)  # Increment 05: fonts come from the design, never a CDN


class ArtefactVizTest(RenderCase):
    def test_fbs_sample_builds_on_fallback_and_domain_tokens(self):
        sample = SKILLS / "com-artefact-viz/examples/fbs.sample.md"
        result = run(SKILLS / "com-artefact-viz/scripts/render.py", sample, "--out", "out/viz.html", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        html = (self.tmp / "out/viz.html").read_text(encoding="utf-8")
        # Increment 07: the domain tokens read --chart-1 to --chart-3, so the base dataviz module is inlined too
        self.assertLayersInOrder(html, [FALLBACK_MARKER, "dataviz.css — neutral defaults", "viz domain tokens (derived)"])
        self.assertIn(FALLBACK_ACCENT, html)


class ReleaseNoteTest(RenderCase):
    def test_release_note_example_builds_on_fallback_tokens(self):
        note = SKILLS / "com-release-note/examples/release-note.complete.md"
        result = run(SKILLS / "com-release-note/scripts/render_pdf.py", note,
                     "--html-only", "--output", "rn.pdf", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        html = (self.tmp / "rn.html").read_text(encoding="utf-8")
        self.assertIn(FALLBACK_MARKER, html)
        self.assertIn(FALLBACK_ACCENT, html)


class GoldenTest(RenderCase):
    """Every fixture deck, document, view and report renders the computed styles and PDF pixels of 2.0.0."""

    def test_fixture_renders_match_the_goldens(self):
        goldens.require_lane(self)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for name in goldens.CASES:
                with self.subTest(case=name):
                    actual = goldens.capture(name, SKILLS, self.tmp / name, browser)
                    self.assertEqual(goldens.differences(goldens.load(name), actual), [])
            browser.close()


if __name__ == "__main__":
    unittest.main()
