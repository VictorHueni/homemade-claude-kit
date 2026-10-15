"""com-release-note on the resolver and the validator (Plan-0005 increment 09), and the shared print chrome
the release note and com-slide-deck's `mode: document` draw in the Chromium page margins."""
import json
import re
import shutil
import sys
import unittest
from pathlib import Path

from helpers import SKILLS, RenderCase, run

PLUGIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN / "shared"))

import check_render  # noqa: E402
import design_source  # noqa: E402

NOTE_SKILL = SKILLS / "com-release-note"
RENDER = NOTE_SKILL / "scripts/render_pdf.py"
TEMPLATE = NOTE_SKILL / "templates/report.html.tmpl"
NOTE = NOTE_SKILL / "examples/release-note.complete.md"
DESIGNS = PLUGIN / "tests/fixtures/design-systems"
ROLES = {role for module in design_source._contract()["modules"].values() for role in module["roles"]}
PROPERTY = re.compile(r"(?<![\w-])--[a-zA-Z][\w-]*")
DECLARATION = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+?)\s*;")
FULL_LEGAL = "Acme Test is a fictitious brand."


def design_layers(html):
    """The CSS of every <style data-design-layer> block, and the page with those blocks removed."""
    blocks = re.findall(r"<style data-design-layer>(.*?)</style>", html, flags=re.S)
    return "\n".join(blocks), re.sub(r"<style data-design-layer>.*?</style>", "", html, flags=re.S)


class NoteCase(RenderCase):
    DESIGN_ARGS = {"full": ("--design-system", DESIGNS / "full"),
                   "subset": ("--design-system", DESIGNS / "subset"), "base": ()}

    def render(self, *extra, cwd=None, env=None):
        cwd = cwd or self.tmp
        result = run(RENDER, NOTE, "--html-only", "--output", "out/rn.pdf", *extra, cwd=cwd, env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.result = result
        return (cwd / "out/rn.html").read_text(encoding="utf-8")

    def provenance(self, cwd=None):
        return json.loads(((cwd or self.tmp) / "out/rn.html.provenance.json").read_text(encoding="utf-8"))

    def refused(self, *extra, cwd=None, code=2):
        cwd = cwd or self.tmp
        result = run(RENDER, NOTE, "--html-only", "--output", "out/rn.pdf", *extra, cwd=cwd)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        for name in ("rn.html", "rn.html.provenance.json", "rn.pdf"):
            self.assertFalse((cwd / "out" / name).exists(), f"a refused render wrote {name}")
        return result.stderr

    def pin(self, fixture, folder=None):
        shutil.copytree(DESIGNS / fixture, self.tmp / "design-system")
        (self.tmp / "docs/ux").mkdir(parents=True)
        (self.tmp / "docs/ux/package.json").write_text(json.dumps(
            {"dependencies": {f"@acme-test/{fixture}": "file:../../design-system"}}), encoding="utf-8")


class TemplateTest(unittest.TestCase):
    def test_template_has_no_var_fallback(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(check_render.strip_fallbacks(text), text, "a var() fallback is left")

    def test_template_and_renderer_use_only_roles_and_kit_properties(self):
        for path in (TEMPLATE, RENDER):
            with self.subTest(file=path.name):
                text = check_render.clean(path.read_text(encoding="utf-8"))
                stray = {p for p in PROPERTY.findall(text) if p not in ROLES and not p.startswith("--kit-")}
                self.assertEqual(stray - {"--font-report", "--exception", "--design-system", "--release-url",
                                          "--output", "--html-only", "--exclude-path"}, set())

    def test_template_holds_no_fixed_bold_weight_or_pill_radius(self):
        text = check_render.clean(TEMPLATE.read_text(encoding="utf-8"))
        self.assertNotRegex(text, r"font-weight:\s*(700|bold)\b", "the bold weight is --font-weight-bold")
        self.assertNotIn("999px", text, "the pill radius is --radius-pill")

    def test_template_paints_breaking_changes_with_the_print_role(self):
        text = check_render.clean(TEMPLATE.read_text(encoding="utf-8"))
        self.assertNotIn("var(--danger)", text, "the breaking accent is --print-breaking")
        self.assertIn("var(--print-breaking)", text)

    def test_template_holds_no_literal_colour_and_no_fixed_page_box(self):
        text = check_render.clean(TEMPLATE.read_text(encoding="utf-8"))
        self.assertIsNone(check_render.LITERAL.search(text))
        self.assertNotRegex(text, r"@page\s*\{\s*size:\s*A4", "the page box comes from the print module")


class DesignWeightRadiusBreakingTest(NoteCase):
    """The bold weight, the pill radius and the breaking accent come from the design, never the template."""

    NAVY = "#1f2a5c"

    def mutated(self):
        folder = self.tmp / "ds"
        shutil.copytree(DESIGNS / "full", folder)
        css = folder / "css"
        for name, old, new in (("type.css", "--font-weight-bold: 700;", "--font-weight-bold: 500;"),
                               ("space-shape.css", "--radius-pill: 999px;", "--radius-pill: 6px;"),
                               ("print.css", "--print-page-size: Letter;",
                                f"--print-page-size: Letter; --print-breaking: {self.NAVY};")):
            text = (css / name).read_text(encoding="utf-8")
            self.assertIn(old, text)
            (css / name).write_text(text.replace(old, new), encoding="utf-8")
        return folder

    def rule(self, rest, selector):
        match = re.search(re.escape(selector) + r"\s*\{([^}]*)\}", rest)
        self.assertIsNotNone(match, selector)
        return match.group(1)

    def assertDrawsWithRoles(self, rest):
        for selector in (".report-title", ".cartouche a", ".donut-total", ".dl-v", ".rc-v", ".section-label",
                         ".product-name", ".capability-label"):
            self.assertIn("font-weight: var(--font-weight-bold)", self.rule(rest, selector), selector)
        self.assertIn("border-radius: var(--radius-pill)", self.rule(rest, ".product-id"))
        label = self.rule(rest, ".section--breaking .section-label")
        self.assertIn("color: var(--print-breaking)", label)
        self.assertIn("border-bottom-color: var(--print-breaking)", label)
        box = self.rule(rest, ".breaking")
        self.assertIn("color-mix(in srgb, var(--print-breaking) 35%, transparent)", box)
        self.assertIn("color-mix(in srgb, var(--print-breaking) 8%, transparent)", box)

    def test_a_design_sets_the_bold_weight_the_pill_radius_and_the_breaking_accent(self):
        folder = self.mutated()
        html = self.render("--design-system", folder)
        self.assertEqual(check_render.check(html, design_source.resolve(self.tmp, explicit=folder))["findings"], [])
        layer, rest = design_layers(html)
        values = design_source.role_values(layer)
        self.assertEqual(values["--font-weight-bold"], "500")
        self.assertEqual(values["--radius-pill"], "6px")
        self.assertEqual(values["--print-breaking"], self.NAVY)
        self.assertDrawsWithRoles(rest)
        self.assertIn('class="section section--breaking', rest)   # the example note has a breaking section

    def test_the_base_theme_keeps_700_999px_and_the_danger_colour(self):
        layer, rest = design_layers(self.render())
        values = design_source.role_values(layer)
        self.assertEqual(values["--font-weight-bold"], "700")
        self.assertEqual(values["--radius-pill"], "999px")
        self.assertEqual(values["--print-breaking"], "var(--danger)")
        self.assertDrawsWithRoles(rest)


class ResolvedNoteTest(NoteCase):
    def test_renders_and_passes_on_full_subset_and_base(self):
        for name, extra in self.DESIGN_ARGS.items():
            with self.subTest(design=name):
                design = design_source.resolve(self.tmp, explicit=DESIGNS / name if extra else None)
                html = self.render(*extra)
                self.assertIn("<style data-design-layer>", html)
                self.assertEqual(check_render.check(html, design)["findings"], [])
                prov = self.provenance()
                self.assertEqual(prov["designSystem"]["source"], "path" if extra else "base")
                self.assertEqual(prov["modules"]["print"], "design-system" if name == "full" else "base")

    def test_inlines_core_dataviz_type_space_shape_and_print_only(self):
        # type and space-shape give the bold weight and the pill radius the report draws with
        layer, _ = design_layers(self.render(*self.DESIGN_ARGS["full"]))
        defined = {name for name, _ in DECLARATION.findall(layer)}
        modules = design_source._contract()["modules"]
        for module in ("core", "dataviz", "type", "space-shape", "print"):
            self.assertLessEqual(set(modules[module]["roles"]), defined, module)
        for module in ("document", "slide-frame", "brand"):
            self.assertEqual(set(modules[module]["roles"]) & defined, set(), module)
        self.assertIn("inlined: core, dataviz, type, space-shape, print", self.result.stdout)

    def test_full_embeds_the_package_fonts(self):
        layer, _ = design_layers(self.render(*self.DESIGN_ARGS["full"]))
        self.assertIn('font-family: "Acme Sans"', layer)
        self.assertIn("data:font/woff2;base64,", layer)
        base, _ = design_layers(self.render())
        self.assertNotIn("@font-face", base)

    def test_old_fonts_css_is_not_read(self):
        fonts = self.tmp / "docs/ux/fonts"
        fonts.mkdir(parents=True)
        (fonts / "fonts.css").write_text('@font-face { font-family: "Old Face"; src: url(old.woff2); }\n'
                                         ":root { --font-report: 'Old Face', serif; }\n", encoding="utf-8")
        (fonts / "old.woff2").write_bytes(b"wOF2")
        html = self.render()
        self.assertNotIn("Old Face", html)
        self.assertIn("docs/ux/fonts/fonts.css", self.result.stdout + self.result.stderr)  # says it is ignored

    def test_page_box_comes_from_the_print_module(self):
        html = self.render(*self.DESIGN_ARGS["full"])
        self.assertRegex(html, r"@page\s*\{\s*size:\s*Letter;\s*margin:\s*16mm 18mm 20mm;\s*\}")
        html = self.render()
        self.assertRegex(html, r"@page\s*\{\s*size:\s*A4;\s*margin:\s*14mm 16mm 18mm;\s*\}")

    def test_donut_reads_the_chart_scale_in_order(self):
        _, rest = design_layers(self.render(*self.DESIGN_ARGS["full"]))
        figure = rest.split('class="recap"', 1)[1]
        steps = re.findall(r"var\((--chart-\d)\)", figure.split('class="donut-legend"', 1)[0])
        self.assertEqual(steps, sorted(steps))
        self.assertEqual(steps[0], "--chart-1")
        self.assertIsNone(check_render.LITERAL.search(check_render.clean(rest.split("<body>", 1)[1])))


class FontReportTest(NoteCase):
    def test_body_reads_the_body_font_without_the_exception(self):
        html = self.render(*self.DESIGN_ARGS["subset"])
        _, rest = design_layers(html)
        self.assertNotIn("--font-report", rest)
        self.assertIn("--kit-report-font: var(--font-body)", rest)

    def test_declared_exception_re_faces_the_report_and_is_reported(self):
        html = self.render("--exception=--font-report=Lora, serif")
        _, rest = design_layers(html)
        self.assertIn("--font-report: Lora, serif", rest)
        self.assertIn("--kit-report-font: var(--font-report)", rest)
        self.assertEqual(self.provenance()["exceptions"], ["--font-report"])
        self.assertIn("exception --font-report=Lora, serif", self.result.stdout)


class DesignSourceTest(NoteCase):
    def test_finds_the_project_pin_from_a_subfolder(self):
        self.pin("subset")
        sub = self.tmp / "docs/communication"
        sub.mkdir(parents=True)
        layer, _ = design_layers(self.render(cwd=sub))
        self.assertIn("#7a3ea8", layer)   # the subset accent
        self.assertEqual(self.provenance(cwd=sub)["designSystem"]["name"], "@acme-test/subset")

    def test_legacy_token_file_in_the_project_is_refused(self):
        (self.tmp / "docs/ux").mkdir(parents=True)
        (self.tmp / "docs/ux/tokens.css").write_text(":root { --accent: #123456; }\n", encoding="utf-8")
        self.assertIn("ux-design-system subset --from-legacy", self.refused())

    def test_a_plain_stylesheet_is_refused_with_the_migration_message(self):
        sheet = self.tmp / "tokens.css"
        sheet.write_text(":root { --accent: #123456; }\n", encoding="utf-8")
        stderr = self.refused("--design-system", sheet)
        self.assertIn("kit-manifest.json", stderr)
        self.assertIn("ux-design-system point", stderr)

    def test_missing_design_system_path_is_a_clear_error(self):
        self.assertIn("does not exist", self.refused("--design-system", self.tmp / "nowhere"))

    def test_a_render_that_breaks_the_design_writes_nothing(self):
        # --muted on --surface at 1.16:1: the validator refuses the declared exception
        self.assertIn("contrast", self.refused("--exception=--muted=#eeeeee", code=1))


class PrintChromeTest(NoteCase):
    """shared/print_chrome.py: the header and footer Chromium draws in the page margins."""

    def setUp(self):
        super().setUp()
        import print_chrome
        self.chrome = print_chrome

    def test_full_footer_carries_the_logo_and_the_legal_line_with_resolved_roles(self):
        design = design_source.resolve(self.tmp, explicit=DESIGNS / "full")
        footer = self.chrome.footer_template(design, "Release note · v2.0.0", "16mm")
        header = self.chrome.header_template(design, "A title", "16mm")
        self.assertRegex(footer, r'<img [^>]*src="data:image/svg\+xml;base64,')
        self.assertIn(FULL_LEGAL, footer)
        self.assertIn("Release note · v2.0.0", footer)
        self.assertIn('class="pageNumber"', footer)
        for chrome in (header, footer):
            self.assertIn("#475467", chrome)              # the full fixture's --muted
            self.assertIn("ui-monospace, monospace", chrome)
            self.assertNotIn("var(", chrome)
            self.assertNotIn("rgba(", chrome)

    def test_subset_footer_has_no_logo_and_no_legal_line(self):
        design = design_source.resolve(self.tmp, explicit=DESIGNS / "subset")
        footer = self.chrome.footer_template(design, "Release note · v2.0.0", "16mm")
        self.assertNotIn("<img", footer)
        self.assertNotIn(FULL_LEGAL, footer)

    def test_a_role_that_reads_another_role_is_followed_not_defaulted(self):
        folder = self.tmp / "design"
        shutil.copytree(DESIGNS / "subset", folder)
        core = folder / "css/core.css"
        core.write_text(core.read_text(encoding="utf-8").replace("--muted: #475467", "--muted: var(--ink)"),
                        encoding="utf-8")
        design = design_source.resolve(self.tmp, explicit=folder)
        self.assertEqual(self.chrome.resolved_role(design, "--muted"), "#101828")
        self.assertIn("#101828", self.chrome.footer_template(design, "x", "16mm"))

    def test_an_unresolved_role_is_an_error_not_a_default(self):
        design = design_source.resolve(self.tmp)
        design.css["core"] += "\n:root { --muted: var(--nowhere); }\n"
        with self.assertRaises(design_source.DesignError):
            self.chrome.resolved_role(design, "--muted")

    def test_page_geometry_from_the_print_module(self):
        full = self.chrome.print_geometry(design_source.resolve(self.tmp, explicit=DESIGNS / "full"))
        self.assertEqual((full["width"], full["height"]), ("8.5in", "11in"))
        self.assertEqual(full["margin"], {"top": "16mm", "right": "18mm", "bottom": "20mm", "left": "18mm"})
        base = self.chrome.print_geometry(design_source.resolve(self.tmp))
        self.assertEqual((base["width"], base["height"]), ("210mm", "297mm"))
        self.assertEqual(base["margin"], {"top": "14mm", "right": "16mm", "bottom": "18mm", "left": "16mm"})
        self.assertEqual(self.chrome.page_box("A4 landscape"), ("297mm", "210mm"))
        self.assertEqual(self.chrome.page_box("200mm 100mm"), ("200mm", "100mm"))
        with self.assertRaises(design_source.DesignError):
            self.chrome.page_box("huge")


if __name__ == "__main__":
    unittest.main()
