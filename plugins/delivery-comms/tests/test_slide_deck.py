"""com-slide-deck on the resolver and the validator (Plan-0005 increment 05), slide frame and brand (06)."""
import importlib.util
import json
import re
import shutil
import sys
import unittest
from pathlib import Path

import yaml

from helpers import SKILLS, RenderCase, run

DECK = SKILLS / "com-slide-deck" / "scripts"
DESIGNS = Path(__file__).resolve().parent / "fixtures" / "design-systems"
FIXTURE_DECKS = Path(__file__).resolve().parent / "fixtures" / "decks"
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

    def test_document_chrome_from_full_carries_the_logo_and_the_legal_line(self):
        # Increment 09 (owner 2026-10-14): the shared print chrome brands a document deck's page margins
        for name, branded in (("full", True), ("subset", False)):
            with self.subTest(design=name):
                self.setUp()
                self.pin(name)
                self.scaffold(mode="document")
                cfg = yaml.safe_load((self.deck / "config.yaml").read_text(encoding="utf-8"))
                design = self.render.resolve_design(cfg, self.deck)
                _, footer = self.render.document_chrome(cfg, "2026-10-14", None, design)
                self.assertEqual(bool(re.search(r'<img [^>]*src="data:image/svg\+xml;base64,', footer)), branded)
                self.assertEqual("Acme Test is a fictitious brand." in footer, branded)
                self.assertIn('class="pageNumber"', footer)

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


FULL_LEGAL = "Acme Test is a fictitious brand."
SLIDE_FRAME_CLASSES = {"slide", "active", "presenting", "controls-hint", "slide-source-bar",
                       "slide-label", "slide-footer", "slide-logo", "slide-legal", "slide-classification",
                       "slide-number"}


def classes_in(text):
    """Class names used in class attributes and in CSS selectors of `text`."""
    names = set()
    for attr in re.findall(r'class="([^"]*)"', text):
        names |= set(attr.split())
    css = re.sub(r"/\*.*?\*/", "", " ".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S)), flags=re.S)
    css = re.sub(r"url\([^)]*\)", "url()", css)
    names |= set(re.findall(r"\.([a-zA-Z][\w-]*)", re.sub(r"\{[^{}]*\}", "{}", css)))
    return names


def footers(html):
    return re.findall(r'<div class="slide-footer"[^>]*>(.*?)</div>', html, re.S)


class SlideFrameTest(DeckCase):
    """The slide frame (canvas, section label, footer row) and the brand from the resolved design (increment 06)."""

    def add_slides(self, count, legacy_number=True):
        slides = self.deck / "output" / "slides"
        entries = []
        for i in range(1, count + 1):
            number = '\n  <div class="slide-number"></div>' if legacy_number else ""
            (slides / f"{i:02d}.html").write_text(
                f'<div class="slide s-{i}">\n  <div class="slide-label">Section {i}</div>\n'
                f'  <h2>Slide {i}</h2>{number}\n</div>\n', encoding="utf-8")
            entries.append({"file": f"{i:02d}.html", "label": f"Slide {i}"})
        path = self.deck / "config.yaml"
        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        cfg["slides"] = entries
        path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    def design_layer(self, html):
        return re.search(r"<style data-design-layer>(.*?)</style>", html, re.S).group(1)

    def kit_style(self, html):
        return re.findall(r"<style>(.*?)</style>", html, re.S)[-1]

    def test_full_takes_the_frame_and_the_brand_of_the_design(self):
        self.pin("full")
        self.scaffold()
        self.add_slides(3)
        self.assertBuilds()
        html = self.html()
        layer = self.design_layer(html)
        # canvas size from the design's slide-frame module, not a number baked into the kit
        self.assertIn("--slide-width: 1280px", layer)
        self.assertIn("--slide-height: 720px", layer)
        self.assertIn("/ 1280;", html)
        self.assertIn("var(--slide-height)", self.kit_style(html))
        self.assertNotIn("540px", self.kit_style(html))
        # the frame classes the base defines, then the design's own restyle of the section label
        self.assertRegex(layer, r"\.slide-label\s*\{")
        self.assertIn("letter-spacing: 0.14em", layer)
        self.assertLess(layer.index("slide-frame.css — neutral"), layer.index("letter-spacing: 0.14em"))
        # logo, legal line and number on every slide, number at the right (last in the footer row)
        rows = footers(html)
        self.assertEqual(len(rows), 3)
        for i, row in enumerate(rows, start=1):
            self.assertRegex(row, r'<span class="slide-logo" data-brand-asset[^>]*></span>')
            self.assertIn(f'<span class="slide-legal">{FULL_LEGAL}</span>', row)
            self.assertTrue(row.rstrip().endswith(f'<span class="slide-number">{i} / 3</span>'), row)
        self.assertIn("var(--brand-logo-on-light)", layer)
        # one copy of each logo (in the design layer), not one per slide
        self.assertEqual(html.count("data:image/svg+xml"), 3)
        # the frame owns the number: the partials' legacy placeholder is dropped
        self.assertEqual(html.count('class="slide-number"'), 3)

    def test_subset_has_the_neutral_frame_and_no_brand(self):
        self.pin("subset")
        self.scaffold()
        self.add_slides(2)
        result = self.assertBuilds()
        html = self.html()
        self.assertNotIn("slide-logo\"", html.split("</head>", 1)[1])
        self.assertNotIn("slide-legal", html.split("</head>", 1)[1])
        self.assertNotIn("data:image/svg+xml", html)
        rows = footers(html)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1].strip(), '<span class="slide-number">2 / 2</span>')
        self.assertIn("--slide-width: 960px", self.design_layer(html))
        self.assertIn("/ 960;", html)
        mods = self.provenance()["modules"]
        self.assertEqual((mods["slide-frame"], mods["brand"]), ("base", "base"))
        base_line = next(line for line in result.stdout.splitlines() if "base:" in line)
        self.assertIn("slide-frame", base_line)
        self.assertIn("brand", base_line)

    def test_no_numbering_and_no_brand_means_no_footer_row(self):
        self.scaffold(numbering={"enabled": False})
        self.add_slides(2)
        self.assertBuilds()
        self.assertEqual(footers(self.html()), [])
        self.assertNotIn('class="slide-number"', self.html())

    def test_config_canvas_overrides_the_design_canvas(self):
        self.pin("full")
        self.scaffold(canvas={"width": 1024, "height": 768})
        self.add_slides(1)
        result = self.assertBuilds()
        html = self.html()
        self.assertIn("/ 1024;", html)
        self.assertRegex(self.kit_style(html), r"--slide-width:\s*1024px;\s*--slide-height:\s*768px")
        self.assertIn("1024x768", result.stdout)

    def test_new_config_takes_the_canvas_from_the_design(self):
        self.scaffold()
        cfg = yaml.safe_load((self.deck / "config.yaml").read_text(encoding="utf-8"))
        self.assertNotIn("canvas", cfg)

    def test_rebuilding_a_split_slide_keeps_one_footer_row(self):
        self.pin("full")
        self.scaffold()
        self.add_slides(1)
        self.assertBuilds()
        built = re.search(r'<div class="slide s-1">.*?</div>\s*</div>', self.html(), re.S).group(0)
        (self.deck / "output/slides/01.html").write_text(built + "\n", encoding="utf-8")
        self.assertBuilds()
        self.assertEqual(len(footers(self.html())), 1)

    def test_the_kit_emits_only_the_slide_frame_vocabulary(self):
        mods = json.loads((DECK.parent.parent.parent / "contract" / "modules.json").read_text(encoding="utf-8"))
        vocabulary = set(mods["modules"]["slide-frame"]["classes"])
        self.assertEqual(vocabulary, SLIDE_FRAME_CLASSES)
        base_frame = (DECK / "shared" / "base" / "slide-frame.css").read_text(encoding="utf-8")
        self.assertLessEqual(classes_in(f"<style>{base_frame}</style>"), vocabulary)
        self.pin("full")
        self.scaffold(classification="Internal")
        self.add_slides(2)
        self.assertBuilds()
        html = self.html()
        self.assertIn('class="slide-classification"', html)
        body = html.split("</head>", 1)[1]
        emitted = classes_in(self.kit_style(html)) | classes_in(body)
        emitted -= {"s-1", "s-2"}  # the partials' own slide classes
        self.assertLessEqual(emitted, vocabulary)


class FrameRenderTest(DeckCase):
    """render.py prints at the canvas build.py used: the design's, unless config.yaml sets one."""

    def setUp(self):
        super().setUp()
        self.render = load("slide_deck_render", DECK / "render.py")

    def test_canvas_comes_from_the_resolved_design(self):
        for name, expected in (("full", (1280, 720)), ("subset", (960, 540)), ("base", (960, 540))):
            with self.subTest(design=name):
                self.setUp()
                if name != "base":
                    self.pin(name)
                self.scaffold()
                cfg = yaml.safe_load((self.deck / "config.yaml").read_text(encoding="utf-8"))
                design = self.render.resolve_design(cfg, self.deck)
                self.assertEqual(self.render.canvas_size(cfg, design), expected)
                self.assertEqual(self.render.canvas_size({**cfg, "canvas": {"width": 800, "height": 600}}, design),
                                 (800, 600))

class FixtureDeckCase(DeckCase):
    """A copy of tests/fixtures/decks, one deck of it configured by the test (the fixture configs back the goldens)."""

    def fixture(self, name, design=None, **config):
        if not (self.tmp / "decks").exists():
            shutil.copytree(FIXTURE_DECKS, self.tmp / "decks")
        self.deck = self.tmp / "decks" / name
        path = self.deck / "config.yaml"
        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        if design:
            cfg["paths"]["design_tokens"] = str(DESIGNS / design)
        cfg.update(config)
        path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        self.cfg = cfg

    @property
    def output(self):
        return self.deck / "output" / self.cfg["paths"]["output_filename"]

    def build(self):
        return run(DECK / "build.py", "-c", self.deck / "config.yaml", cwd=self.tmp)

    def layers(self, html):
        design = re.search(r"<style data-design-layer>(.*?)</style>", html, re.S).group(1)
        kit = re.findall(r"<style>(.*?)</style>", html, re.S)[-1]
        return design, kit

    def roots(self, html):
        return re.findall(r'<(?:div|section) class="(slide [^"]*|slide|doc[^"]*)"', html)


class DarkDeckTest(FixtureDeckCase):
    """Dark slides, decks and documents: the remap lives in build.py's kit layer, the dark module is inlined only
    when a slide or the deck is dark, and nothing the light render reads moves."""

    def setUp(self):
        super().setUp()
        sys.path.insert(0, str(DECK / "shared"))
        import design_source
        self.ds = design_source
        self.contract = design_source._contract()
        self.mirror = design_source.dark_mirror(self.contract)

    def test_a_dark_slide_carries_the_remap_in_the_kit_layer(self):
        self.fixture("dark-slides", "full-dark")
        result = self.assertBuilds()
        self.assertIn("PASS", result.stdout)
        design_layer, kit = self.layers(self.html())
        rule = re.search(r"\.slide\.dark,\s*\.doc\.dark\s*\{([^}]*)\}", kit)
        self.assertIsNotNone(rule, "the remap rule is missing from the kit layer")
        for role, twin in self.mirror.items():
            self.assertIn(f"{role}: var({twin});", rule.group(1))
        self.assertIn("--slide-fg: var(--dark-slide-fg);", rule.group(1))
        # the fill-text choices recomputed against the dark roles
        design = self.ds.resolve(self.tmp, explicit=DESIGNS / "full-dark")
        chosen = self.ds.fill_text("".join(design.css.values()), self.contract["modules"]["dark"]["pairs"])
        light = {twin: role for role, twin in self.mirror.items()}
        self.assertTrue(chosen)
        for fill, text in chosen.items():
            self.assertIn(f"{self.ds.kit_on(light[fill])}: var({text});", rule.group(1))
        self.assertRegex(kit, r"\.slide\.dark \.slide-logo\s*\{[^}]*var\(--brand-logo-on-dark\)")
        key = re.search(r"\.dark \.dark-key\s*\{([^}]*)\}", kit).group(1)
        self.assertIn("var(--dark-key-fill)", key)
        self.assertIn("var(--dark-key-edge)", key)
        self.assertRegex(kit, r"\.dark \.dark-accent\s*\{[^}]*var\(--dark-accent-text\)")
        self.assertIsNone(LITERAL.search(re.sub(r"/\*.*?\*/", "", kit, flags=re.S)))
        # the dark module is inlined: the base defaults, then the design's own dark roles
        self.assertIn("dark.css, neutral defaults", design_layer)
        self.assertIn("--dark-accent: #4fd1c5", design_layer)
        self.assertEqual(self.roots(self.html()), ["slide s-1", "slide s-2 dark", "slide s-3"])
        self.assertEqual(self.provenance()["modules"]["dark"], "design-system")

    def test_a_deck_without_a_dark_slide_inlines_no_dark_css(self):
        for design in ("full-dark", "full", None):
            with self.subTest(design=design or "base"):
                self.setUp()
                self.fixture("slides", design)
                self.assertBuilds()
                html = self.html()
                self.assertNotIn("--dark-", html)
                self.assertNotIn("dark", " ".join(self.roots(html)))

    def test_theme_dark_marks_every_slide_and_every_page(self):
        self.fixture("slides", "full-dark", theme="dark")
        self.assertBuilds()
        html = self.html()
        self.assertEqual(self.roots(html), ["slide s-1 dark", "slide s-2 dark", "slide s-3 dark"])
        self.assertIn("--ink: var(--dark-ink);", self.layers(html)[1])
        self.setUp()
        self.fixture("dark-document", "full-dark")
        self.assertBuilds()
        html = self.html()
        self.assertIn('<div class="doc dark">', html)
        self.assertIn("--ink: var(--dark-ink);", self.layers(html)[1])
        self.assertIn("--dark-accent: #4fd1c5", self.layers(html)[0])

    def test_an_unknown_theme_is_refused(self):
        self.fixture("slides", theme="night")
        result = self.build()
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("theme", result.stderr)
        self.assertIn("dark", result.stderr)
        self.assertFalse(self.output.exists())

    def test_subset_renders_the_dark_slide_from_the_base(self):
        self.fixture("dark-slides", "subset")
        result = self.assertBuilds()
        self.assertIn("PASS", result.stdout)
        design_layer, kit = self.layers(self.html())
        self.assertIn("dark.css, neutral defaults", design_layer)
        self.assertIn("--ink: var(--dark-ink);", kit)
        self.assertEqual(self.provenance()["modules"]["dark"], "base")
        check = run(DECK / "shared/check_render.py", self.output, "--design-system", DESIGNS / "subset", cwd=self.tmp)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_dark_leaves_what_the_light_render_reads_unchanged(self):
        # a dark module never touches the core --kit-on-* block, a light role's value or the core pair check
        from print_chrome import role_value
        full = self.ds.resolve(self.tmp, explicit=DESIGNS / "full")
        dark = self.ds.resolve(self.tmp, explicit=DESIGNS / "full-dark")
        on_block = re.compile(r":root \{\n(?:  --kit-on-[^\n]*\n)+\}\n")
        self.assertEqual(on_block.findall(dark.css["core"]), on_block.findall(full.css["core"]))
        self.assertTrue(on_block.findall(full.css["core"]))
        for role in ("--muted", "--ink", "--accent", "--slide-fg", "--slide-bg", "--print-bg"):
            self.assertEqual(role_value(dark, role), role_value(full, role), role)
        broken = self.tmp / "broken"
        shutil.copytree(DESIGNS / "full-dark", broken)
        core = broken / "css/core.css"
        core.write_text(core.read_text(encoding="utf-8").replace("--accent-ink: #ffffff", "--accent-ink: #0e7090"),
                        encoding="utf-8")
        with self.assertRaises(self.ds.DesignError) as refused:
            self.ds.resolve(self.tmp, explicit=broken)
        self.assertIn("--accent-ink on --accent", str(refused.exception))

    def test_a_dark_document_chrome_reads_the_dark_roles(self):
        render = load("slide_deck_render", DECK / "render.py")
        self.fixture("dark-document", "full-dark")
        design = render.resolve_design(self.cfg, self.deck)
        header, footer = render.document_chrome(self.cfg, "2026-10-17", None, design)
        dark_muted = self.ds.role_values(design.css["dark"])["--dark-muted"]
        self.assertIn(dark_muted, footer)
        self.assertIn(dark_muted, header)
        self.assertNotIn("#475467", header + footer)       # the light --muted
        from print_chrome import logo_uri
        self.assertIn(logo_uri(design, "--brand-logo-on-dark"), footer)
        self.assertNotIn(logo_uri(design), footer)
        self.setUp()
        self.fixture("document", "full-dark")
        design = render.resolve_design(self.cfg, self.deck)
        _, light = render.document_chrome(self.cfg, "2026-10-17", None, design)
        self.assertIn("#475467", light)
        self.assertIn(logo_uri(design), light)


LABELS = {
    "en": ("Public", "Internal", "Confidential", "Strictly confidential"),
    "fr": ("Public", "Interne", "Confidentiel", "Strictement confidentiel"),
    "de": ("Öffentlich", "Intern", "Vertraulich", "Streng vertraulich"),
    "it": ("Pubblico", "Interno", "Confidenziale", "Strettamente confidenziale"),
}
# print_chrome.footer_template with no classification, as in 2.0.0 (the release note's footer): sha256 prefixes
FOOTER_SHA = {("full", True): "b37173225b1a9b74", ("full", False): "dc1397e36b0c7bfa",
              ("subset", True): "48f95f0972b2e4fd", ("subset", False): "1cea1607df6c1908"}


class ClassificationTest(FixtureDeckCase):
    """config.yaml `classification:` prints the deck's level in its language at the right of the footer row, just
    before the number, and in the running footer of every document page; absent, nothing changes."""

    def setUp(self):
        super().setUp()
        sys.path.insert(0, str(DECK / "shared"))
        import classification
        self.classification = classification

    def test_the_four_levels_in_each_built_in_language(self):
        for lang, labels in LABELS.items():
            for value, label in zip(LABELS["en"], labels):
                with self.subTest(lang=lang, value=value):
                    self.assertEqual(self.classification.label(value, lang), label)
        self.assertEqual(self.classification.label("Confidential", "fr-CH"), "Confidentiel")
        self.assertEqual(self.classification.label(None, "fr"), "")

    def test_every_slide_shows_the_label_in_the_deck_language_before_the_number(self):
        for lang, label in (("fr", "Confidentiel"), ("en", "Confidential"), ("de", "Vertraulich"),
                            ("it", "Confidenziale")):
            with self.subTest(lang=lang):
                self.setUp()
                self.fixture("slides", "full", classification="Confidential", lang=lang)
                result = self.assertBuilds()
                self.assertNotIn("WARN", result.stderr)
                rows = footers(self.html())
                self.assertEqual(len(rows), 3)
                for i, row in enumerate(rows, start=1):
                    self.assertTrue(row.rstrip().endswith(
                        f'<span class="slide-classification">{label}</span><span class="slide-number">{i} / 3</span>'),
                        row)

    def test_the_cell_style_is_in_the_kit_layer_in_roles_only(self):
        self.fixture("slides", "full", classification="Internal")
        self.assertBuilds()
        design_layer, kit = self.layers(self.html())
        rule = re.search(r"\.slide-classification\s*\{([^}]*)\}", kit)
        self.assertIsNotNone(rule, "the classification rule is missing from the kit layer")
        for value in ("var(--tertiary)", "var(--font-mono)", "uppercase"):
            self.assertIn(value, rule.group(1))
        self.assertRegex(kit, r"\.slide-classification\s*\+\s*\.slide-number\s*\{")
        self.assertIsNone(LITERAL.search(rule.group(1)))
        self.assertNotIn("slide-classification", design_layer)

    def test_a_classification_alone_makes_a_footer_row(self):
        self.fixture("slides", None, classification="Public", numbering={"enabled": False})
        self.assertBuilds()
        self.assertEqual([r.strip() for r in footers(self.html())],
                         ['<span class="slide-classification">Public</span>'] * 3)

    def test_another_language_prints_english_and_warns(self):
        self.fixture("slides", "full", classification="Strictly confidential", lang="es")
        result = self.assertBuilds()
        self.assertIn('<span class="slide-classification">Strictly confidential</span>', self.html())
        self.assertIn("es", result.stderr)
        self.assertIn("English", result.stderr)

    def test_no_classification_leaves_the_deck_unchanged(self):
        for design in ("full", "subset", None):
            with self.subTest(design=design or "base"):
                self.setUp()
                self.fixture("slides", design)
                self.assertBuilds()
                plain = self.output.read_bytes()
                self.assertNotIn(b"classification", plain)
                self.fixture("slides", design, classification=None)
                self.assertBuilds()
                self.assertEqual(self.output.read_bytes(), plain)

    def test_an_unknown_classification_is_refused_naming_the_four(self):
        for name in ("slides", "document"):
            with self.subTest(deck=name):
                self.setUp()
                self.fixture(name, classification="Secret")
                result = self.build()
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                for level in LABELS["en"]:
                    self.assertIn(level, result.stderr)
                self.assertIn("Secret", result.stderr)
                self.assertFalse(self.output.exists())

    def test_document_chrome_holds_the_classification_before_the_page_number(self):
        render = load("slide_deck_render", DECK / "render.py")
        self.fixture("document", "full", classification="Strictly confidential", lang="de")
        design = render.resolve_design(self.cfg, self.deck)
        header, footer = render.document_chrome(self.cfg, "2026-10-17", None, design)
        self.assertNotIn("Streng vertraulich", header)
        self.assertRegex(footer, r">Streng vertraulich</span><span><span class=\"pageNumber\">")
        self.assertIn("text-transform:uppercase", footer)
        self.cfg["page"] = {"numbering": False}
        _, unnumbered = render.document_chrome(self.cfg, "2026-10-17", None, design)
        self.assertIn(">Streng vertraulich</span>", unnumbered)
        self.assertNotIn("pageNumber", unnumbered)

    def test_a_classification_alone_turns_the_document_footer_on(self):
        render = load("slide_deck_render", DECK / "render.py")
        bare = {"mode": "document", "page": {"running_header": "", "footer_left": "", "numbering": False}}
        self.assertFalse(render.chrome_shown(bare, None))
        self.assertTrue(render.chrome_shown(bare, "Partner Co"))
        self.assertTrue(render.chrome_shown({**bare, "classification": "Internal"}, None))
        self.assertTrue(render.chrome_shown({"mode": "document"}, None))

    def test_footer_template_without_a_classification_is_unchanged(self):
        import hashlib
        import design_source
        import print_chrome
        for (name, numbering), sha in FOOTER_SHA.items():
            with self.subTest(design=name, numbering=numbering):
                design = design_source.resolve(self.tmp, explicit=DESIGNS / name)
                footer = print_chrome.footer_template(design, "Release note · 2.1.0", "18mm", numbering=numbering)
                self.assertEqual(hashlib.sha256(footer.encode()).hexdigest()[:16], sha)
                self.assertEqual(print_chrome.footer_template(design, "Release note · 2.1.0", "18mm",
                                                              numbering=numbering, classification=""), footer)


if __name__ == "__main__":
    unittest.main()
