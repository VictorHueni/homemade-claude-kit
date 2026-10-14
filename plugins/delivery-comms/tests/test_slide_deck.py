"""com-slide-deck on the resolver and the validator (Plan-0005 increment 05)."""
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import yaml

from helpers import SKILLS, RenderCase, run

DECK = SKILLS / "com-slide-deck" / "scripts"
DESIGNS = Path(__file__).resolve().parent / "fixtures" / "design-systems"
FULL_ACCENT = "#0e7090"
SUBSET_ACCENT = "#7a3ea8"
LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\([^)]*\)")


def load(name, path):
    """Import a deck script under its own module name (another skill also ships a render.py)."""
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeckCase(RenderCase):
    def scaffold(self, mode="slides", **config):
        init = run(DECK / "init.py", "deck", "--mode", mode, cwd=self.tmp)
        self.assertEqual(init.returncode, 0, init.stdout + init.stderr)
        self.deck = self.tmp / "deck"
        if config:
            path = self.deck / "config.yaml"
            cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
            for key, value in config.items():
                if key == "paths":
                    cfg["paths"].update(value)
                else:
                    cfg[key] = value
            path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    def pin(self, fixture):
        ux = self.tmp / "docs" / "ux"
        ux.mkdir(parents=True)
        (ux / "package.json").write_text(json.dumps(
            {"private": True, "dependencies": {f"@acme-test/{fixture}": f"file:{DESIGNS / fixture}"}}), encoding="utf-8")

    def build(self):
        return run(DECK / "build.py", "-c", "deck/config.yaml", cwd=self.tmp)

    @property
    def output(self):
        name = "document" if (self.deck / "output/document").is_dir() else "slide-deck"
        filename = "document.html" if name == "document" else "presentation.html"
        return self.deck / "output" / name / filename

    def html(self):
        return self.output.read_text(encoding="utf-8")

    def provenance(self):
        return json.loads(Path(str(self.output) + ".provenance.json").read_text(encoding="utf-8"))

    def assertBuilds(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result


class FontsTest(DeckCase):
    def test_full_embeds_the_package_fonts_and_links_no_google_fonts(self):
        self.pin("full")
        self.scaffold()
        self.assertBuilds()
        html = self.html()
        self.assertIn("<style data-design-layer>", html)
        self.assertIn('font-family: "Acme Sans"', html)
        self.assertIn("data:font/woff2;base64,", html)
        self.assertIn(FULL_ACCENT, html)
        self.assertNotIn("fonts.googleapis.com", html)
        self.assertNotIn("fonts.gstatic.com", html)

    def test_subset_and_base_use_system_stacks_and_make_no_request(self):
        for name in ("subset", "base"):
            with self.subTest(design=name):
                self.setUp()
                paths = {"design_tokens": str(DESIGNS / "subset")} if name == "subset" else {}
                self.scaffold(paths=paths) if paths else self.scaffold()
                self.assertBuilds()
                html = self.html()
                self.assertNotIn("@font-face", html)
                self.assertIn("system-ui", html)
                self.assertIsNone(re.search(r"https?://", html), "the deck must not reference the network")

    def test_config_fonts_never_produce_a_network_font_url(self):
        # owner 2026-10-14: the Google Fonts opt-in is dropped in 2.0.0, whatever the design provides
        for name in ("full", "subset", "base"):
            with self.subTest(design=name):
                self.setUp()
                if name != "base":
                    self.pin(name)
                self.scaffold(fonts=[{"family": "Inter", "weights": [400, 700]}])
                result = self.assertBuilds()
                self.assertRegex(result.stdout, r"\[WARN\].*fonts:.*no longer used")
                self.assertIn("@font-face", result.stdout)
                self.assertIn("type", result.stdout)
                html = self.html()
                self.assertNotIn("fonts.googleapis.com", html)
                self.assertNotIn("fonts.gstatic.com", html)
                self.assertNotRegex(html, r"<link[^>]+https?://")

    def test_new_config_has_no_fonts_key(self):
        self.scaffold()
        cfg = yaml.safe_load((self.deck / "config.yaml").read_text(encoding="utf-8"))
        self.assertNotIn("fonts", cfg)
        result = self.assertBuilds()
        self.assertNotIn("fonts:", result.stdout)


class ValidatorTest(DeckCase):
    def test_every_design_builds_and_passes(self):
        for name in ("full", "subset", "base"):
            for mode in ("slides", "document"):
                with self.subTest(design=name, mode=mode):
                    self.setUp()
                    if name != "base":
                        self.pin(name)
                    self.scaffold(mode=mode)
                    result = self.assertBuilds()
                    self.assertIn("PASS", result.stdout)

    def test_off_brand_styles_fail_and_write_nothing(self):
        self.scaffold()
        styles = self.deck / "design" / "styles.css"
        styles.write_text(styles.read_text(encoding="utf-8") + "\n.cover { color: #1a1f2a; }\n", encoding="utf-8")
        result = self.build()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        report = result.stdout + result.stderr
        self.assertIn("#1a1f2a", report)
        self.assertIn("--ink", report)
        self.assertFalse(self.output.exists())
        self.assertFalse(Path(str(self.output) + ".provenance.json").exists())

    def test_a_refused_rebuild_keeps_the_previous_output(self):
        self.scaffold()
        self.assertBuilds()
        before = self.output.read_bytes()
        (self.deck / "output/slides/01.html").write_text(
            '<div class="slide"><p style="color: #c8102e">red</p></div>\n', encoding="utf-8")
        cfg_path = self.deck / "config.yaml"
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        cfg["slides"] = [{"file": "01.html"}]
        cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        self.assertEqual(self.build().returncode, 1)
        self.assertEqual(self.output.read_bytes(), before)

    def test_declared_exception_passes_and_is_reported(self):
        self.scaffold(design={"exceptions": {"cover-red": "#c8102e"}})
        styles = self.deck / "design" / "styles.css"
        styles.write_text(styles.read_text(encoding="utf-8") + "\n.cover { color: #c8102e; }\n", encoding="utf-8")
        result = self.assertBuilds()
        self.assertIn("cover-red", result.stdout)
        self.assertEqual(self.provenance()["exceptions"], ["cover-red"])


class DesignTokensKeyTest(DeckCase):
    def test_accepts_a_design_system_folder(self):
        self.scaffold(paths={"design_tokens": str(DESIGNS / "subset")})
        self.assertBuilds()
        self.assertIn(SUBSET_ACCENT, self.html())
        self.assertEqual(self.provenance()["designSystem"]["source"], "path")

    def test_refuses_a_legacy_token_file(self):
        legacy = self.tmp / "docs" / "ux" / "tokens.css"
        legacy.parent.mkdir(parents=True)
        legacy.write_text(":root { --accent: #123456; }\n", encoding="utf-8")
        self.scaffold(paths={"design_tokens": "../docs/ux/tokens.css"})
        result = self.build()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("ux-design-system point", result.stderr)
        self.assertIn("subset --from-legacy", result.stderr)
        self.assertFalse(self.output.exists())

    def test_missing_folder_is_a_clear_error(self):
        self.scaffold(paths={"design_tokens": "../nowhere"})
        result = self.build()
        self.assertEqual(result.returncode, 2)
        self.assertIn("nowhere", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


class ProvenanceTest(DeckCase):
    def test_written_next_to_the_deck(self):
        self.pin("full")
        self.scaffold()
        result = self.assertBuilds()
        prov = self.provenance()
        self.assertEqual(prov["designSystem"]["name"], "@acme-test/full")
        self.assertEqual(prov["modules"]["core"], "design-system")
        self.assertEqual(prov["modules"]["dataviz"], "design-system")
        self.assertTrue(prov["guidance"]["informational"])
        self.assertIn("provenance", result.stdout.lower())

    def test_base_render_says_so(self):
        self.scaffold()
        self.assertBuilds()
        prov = self.provenance()
        self.assertEqual(prov["designSystem"]["source"], "base")
        self.assertEqual(set(prov["modules"].values()), {"base"})


class RenderScriptTest(DeckCase):
    """render.py without a browser: the validator gate, the stamps and the chrome."""

    def setUp(self):
        super().setUp()
        self.render = load("slide_deck_render", DECK / "render.py")

    def test_print_css_and_stamp_hold_no_literal_colour(self):
        self.assertIsNone(LITERAL.search(self.render.print_css(960, 540)))
        self.assertIsNone(LITERAL.search(self.render._PREP_JS))
        self.assertIn("var(--muted)", self.render._PREP_JS)

    def test_recipient_stamp(self):
        self.assertEqual(self.render.stamp_text("Partner Co", "2026-10-14"), "Prepared for Partner Co · 2026-10-14")
        self.assertEqual(self.render.stamp_text(None, "2026-10-14"), "")

    def test_document_chrome_keeps_footer_left_and_recipient_and_takes_the_resolved_role(self):
        self.pin("full")
        self.scaffold(mode="document", author="A. Writer",
                      page={"footer_left": "{author} · v1", "running_header": "{title}"})
        cfg = yaml.safe_load((self.deck / "config.yaml").read_text(encoding="utf-8"))
        design = self.render.resolve_design(cfg, self.deck)
        header, footer = self.render.document_chrome(cfg, "2026-10-14", None, design)
        self.assertIn("A. Writer · v1", footer)
        self.assertIn("#475467", footer)          # the full fixture's --muted, resolved
        self.assertNotIn("rgba(", header + footer)
        _, stamped = self.render.document_chrome(cfg, "2026-10-14", "Partner Co", design)
        self.assertIn("Prepared for Partner Co · 2026-10-14", stamped)

    def test_render_refuses_an_off_brand_built_deck_and_prints_nothing(self):
        self.scaffold()
        self.assertBuilds()
        self.output.write_text(self.html().replace("</head>", "<style>.x { color: #c8102e; }</style>\n</head>", 1),
                               encoding="utf-8")
        result = run(DECK / "render.py", "--config", "deck/config.yaml", "--output", "deck.pdf", cwd=self.tmp)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("#c8102e", result.stdout + result.stderr)
        self.assertFalse((self.tmp / "deck.pdf").exists())


class MigrateTest(DeckCase):
    def test_reports_hard_coded_values_against_the_resolved_roles(self):
        self.pin("full")
        self.scaffold()
        styles = self.deck / "design" / "styles.css"
        styles.write_text(styles.read_text(encoding="utf-8") + "\n.cta { background: #0e7091; }\n", encoding="utf-8")
        result = run(DECK / "migrate.py", "--config", "deck/config.yaml", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("#0e7091", result.stdout)
        self.assertIn("var(--accent)", result.stdout)
        self.assertIn("styles.css", result.stdout)
        self.assertNotIn("tokens.css", result.stdout)


class InitTest(DeckCase):
    def test_new_decks_carry_no_palette(self):
        self.scaffold()
        styles = (self.deck / "design" / "styles.css").read_text(encoding="utf-8")
        self.assertNotRegex(re.sub(r"/\*.*?\*/", "", styles, flags=re.S), r"--[\w-]+\s*:")


if __name__ == "__main__":
    unittest.main()
