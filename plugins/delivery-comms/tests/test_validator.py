"""Blocking validator (Plan-0005 increment 04): literal colours, unknown properties, exceptions, contrast."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SHARED = PLUGIN / "shared"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
DESIGNS = FIXTURES / "design-systems"
PAGE = (FIXTURES / "pages" / "role-only.html").read_text(encoding="utf-8")
sys.path.insert(0, str(SHARED))

import design_source  # noqa: E402
import check_render  # noqa: E402  (fails red until the validator exists)

ROLES = {role for module in design_source._contract()["modules"].values() for role in module["roles"]}


def page(style="", body=""):
    """The role-only page with extra CSS in a plain <style> block and extra body markup."""
    return PAGE.replace("</style>\n</head>", style + "\n</style>\n</head>", 1).replace("</body>", body + "\n</body>")


class ValidatorCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.base = design_source.resolve(self.tmp)

    def check(self, html, design=None, exceptions=None):
        return check_render.check(html, design or self.base, exceptions)

    def kinds(self, report):
        return sorted({f["kind"] for f in report["findings"]})


class RoleOnlyPagesTest(ValidatorCase):
    def test_passes_against_each_fixture_design(self):
        for name, design in (("base", self.base),
                             ("full", design_source.resolve(self.tmp, explicit=DESIGNS / "full")),
                             ("subset", design_source.resolve(self.tmp, explicit=DESIGNS / "subset"))):
            with self.subTest(design=name):
                report = self.check(PAGE, design)
                self.assertEqual(report["findings"], [])
                self.assertTrue(report["ok"])

    def test_var_fallback_is_stripped_so_it_neither_passes_nor_fails(self):
        self.assertTrue(self.check(page(".x { color: var(--muted, #6b7280); }"))["ok"])
        report = self.check(page(".x { color: var(--nope, var(--muted, #6b7280)); }"))
        self.assertEqual(self.kinds(report), ["unknown-property"])


class LiteralColourTest(ValidatorCase):
    def one(self, html, **kw):
        report = self.check(html, **kw)
        self.assertFalse(report["ok"])
        self.assertEqual(self.kinds(report), ["literal-colour"], report)
        return report["findings"][0]

    def test_style_attribute(self):
        found = self.one(page(body='<p style="color: #123456">x</p>'))
        self.assertEqual(found["value"], "#123456")
        self.assertIn("style attribute", found["where"])

    def test_style_block_with_line_and_closest_role(self):
        html = page(".x {\n  color: #1a1f2a;\n}")
        found = self.one(html)
        line = html.split("\n").index("  color: #1a1f2a;") + 1
        self.assertEqual(found["line"], line)
        self.assertEqual(found["suggest"], "--ink")
        self.assertIn("--ink", found["message"])

    def test_svg_fill(self):
        found = self.one(page(body='<svg><circle r="1" fill="#ff0000"/></svg>'))
        self.assertEqual(found["value"], "#ff0000")
        self.assertIn("fill", found["where"])

    def test_rgb_and_hsl_literals(self):
        for value in ("rgb(1, 2, 3)", "rgba(1,2,3,.5)", "hsl(10 20% 30%)"):
            with self.subTest(value=value):
                self.one(page(f".x {{ color: {value}; }}"))

    def test_design_layers_and_brand_assets_may_hold_literals(self):
        # the fixture page already carries a literal in a design layer, a brand asset and a data URI
        self.assertIn("#396cf5", PAGE)
        self.assertIn('fill="#c8102e"', PAGE)
        self.assertTrue(self.check(PAGE)["ok"])

    def test_transparent_and_current_colour_are_not_literals(self):
        self.assertTrue(self.check(page(".x { background: transparent; border-color: currentColor; }"))["ok"])


class CustomPropertyTest(ValidatorCase):
    def test_unknown_name_fails_in_use_and_in_declaration(self):
        for css in (".x { color: var(--mystery); }", ":root { --mystery: 1px; }"):
            with self.subTest(css=css):
                report = self.check(page(css))
                self.assertEqual(self.kinds(report), ["unknown-property"])
                self.assertIn("--mystery", report["findings"][0]["message"])

    def test_class_name_with_a_double_hyphen_modifier_is_not_a_property(self):
        # BEM modifiers such as .doc-section--flow (com-slide-deck doc.baseline.css)
        self.assertTrue(self.check(page(".doc-section.doc-section--flow { break-before: auto; }"))["ok"])
        self.assertEqual(self.kinds(self.check(page(".a--b { color: var(--nope); }"))), ["unknown-property"])

    def test_kit_property_with_roles_or_plain_values_passes(self):
        self.assertTrue(self.check(page(":root { --kit-a: var(--accent); --kit-b: 3rem; --kit-c: 1px solid var(--border); }"))["ok"])

    def test_kit_property_carrying_a_literal_fails(self):
        report = self.check(page(":root { --kit-a: #abcdef; }"))
        self.assertEqual(self.kinds(report), ["literal-colour"])

    def test_every_contract_role_is_known(self):
        css = ".x { " + " ".join(f"--kit-probe: var({role});" for role in sorted(ROLES)) + " }"
        self.assertTrue(self.check(page(css))["ok"])


class ExceptionTest(ValidatorCase):
    def test_declared_exception_passes_and_is_reported(self):
        html = page(".x { color: #c8102e; }")
        report = self.check(html, exceptions={"brand-red": "#c8102e"})
        self.assertTrue(report["ok"])
        self.assertEqual([e["name"] for e in report["exceptions"]], ["brand-red"])
        self.assertFalse(report["exceptions"][0]["known"])

    def test_exception_matches_only_its_value(self):
        report = self.check(page(".x { color: #c8102f; }"), exceptions={"brand-red": "#c8102e"})
        self.assertFalse(report["ok"])

    def test_vocabulary_reports_known_names_and_never_refuses_unknown(self):
        design = design_source.resolve(self.tmp, explicit=DESIGNS / "full")
        design.exceptions = {"brand-red": "the one red allowed on covers"}
        report = self.check(page(".x { color: #c8102e; }"), design, {"brand-red": "#c8102e", "other": "#00ff00"})
        self.assertTrue(report["ok"])
        known = {e["name"]: e["known"] for e in report["exceptions"]}
        self.assertEqual(known, {"brand-red": True, "other": False})

    def test_exception_that_breaks_a_text_pair_fails(self):
        # --muted on --surface is a contract pair; #cccccc on white is 1.6:1
        report = self.check(PAGE, exceptions={"--muted": "#cccccc"})
        self.assertFalse(report["ok"])
        self.assertEqual(self.kinds(report), ["contrast"])
        self.assertIn("--muted", report["findings"][0]["message"])

    def test_exception_that_keeps_the_pair_passes(self):
        self.assertTrue(self.check(PAGE, exceptions={"--muted": "#4b5563"})["ok"])

    def test_exception_on_a_fill_passes_when_either_text_role_reaches_aa(self):
        # --success is a list pair (--accent-ink or --ink): a dark green keeps white text above AA
        self.assertTrue(self.check(PAGE, exceptions={"--success": "#1b5e20"})["ok"])
        self.assertTrue(self.check(PAGE, exceptions={"--success": "#8fd19e"})["ok"])   # light: --ink carries it

    def test_exception_on_a_fill_fails_when_no_text_role_reaches_aa(self):
        report = self.check(PAGE, exceptions={"--success": "#777777"})   # white 4.48, --ink 3.8
        self.assertEqual(self.kinds(report), ["contrast"])
        message = report["findings"][0]["message"]
        self.assertIn("on --success", message)
        self.assertRegex(message, r"--accent-ink \(contrast \d+\.\d+\)")
        self.assertRegex(message, r"--ink \(contrast \d+\.\d+\)")

    def test_exception_named_as_a_property_allows_that_property(self):
        # a project re-faces the release note alone with --font-report (com-release-note SKILL.md)
        html = page(":root { --font-report: Lora, serif; } body { font-family: var(--font-report); }")
        refused = self.check(html)
        self.assertEqual(self.kinds(refused), ["unknown-property"])
        self.assertIn("declare it as an exception", refused["findings"][0]["message"])
        report = self.check(html, exceptions={"--font-report": "Lora, serif"})
        self.assertTrue(report["ok"], report["findings"])
        self.assertEqual([e["name"] for e in report["exceptions"]], ["--font-report"])


class ResolvedDesignTest(ValidatorCase):
    def test_same_html_passes_one_design_and_fails_another(self):
        grey = self.tmp / "grey-surface"
        shutil.copytree(DESIGNS / "subset", grey)
        core = grey / "css" / "core.css"
        core.write_text(re.sub(r"--surface:\s*#[0-9a-fA-F]+", "--surface: #e5e7eb", core.read_text()))
        exception = {"--muted": "#6b7280"}   # 4.83:1 on white, 3.90:1 on #e5e7eb
        white = design_source.resolve(self.tmp, explicit=DESIGNS / "subset")
        self.assertTrue(self.check(PAGE, white, exception)["ok"])
        report = self.check(PAGE, design_source.resolve(self.tmp, explicit=grey), exception)
        self.assertEqual(self.kinds(report), ["contrast"])


class TemplateDryRunTest(ValidatorCase):
    """Increments 05 to 09 dropped the var() fallbacks and renamed renderer-internal properties to --kit-*."""
    MIGRATED = {
        "com-slide-deck": ("templates/doc.baseline.css",),   # Increment 05
        "com-artefact-viz": ("templates/base.html.tmpl", "templates/tokens.domain.css"),   # Increment 07
        "com-release-note": ("templates/report.html.tmpl",),   # Increment 09
    }

    def test_migrated_templates_pass_as_shipped(self):
        for skill, files in self.MIGRATED.items():
            for rel in files:
                with self.subTest(template=f"{skill}/{rel}"):
                    text = (PLUGIN / "skills" / skill / rel).read_text(encoding="utf-8")
                    wrap = (lambda c: c) if rel.endswith(".tmpl") else (lambda c: f"<style>{c}</style>")
                    self.assertEqual(self.check(wrap(text))["findings"], [])
                    self.assertEqual(check_render.strip_fallbacks(text), text, "a var() fallback is left")


class CliCase(ValidatorCase):
    def run_cli(self, html, *args):
        path = self.tmp / "out.html"
        path.write_text(html, encoding="utf-8")
        return subprocess.run([sys.executable, "-I", str(SHARED / "check_render.py"), str(path), *args],
                              capture_output=True, text=True)


class CommandLineTest(CliCase):
    def test_exit_codes_and_json(self):
        ok = self.run_cli(PAGE)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        bad = self.run_cli(page(".x { color: #123456; }"), "--json")
        self.assertEqual(bad.returncode, 1)
        self.assertEqual(json.loads(bad.stdout)["findings"][0]["kind"], "literal-colour")
        allowed = self.run_cli(page(".x { color: #123456; }"), "--exception", "mine=#123456")
        self.assertEqual(allowed.returncode, 0, allowed.stdout)

    def test_text_output_names_value_location_and_role(self):
        bad = self.run_cli(page(".x { color: #1a1f2a; }"))
        self.assertIn("#1a1f2a", bad.stdout)
        self.assertIn("--ink", bad.stdout)
        self.assertRegex(bad.stdout, r"out\.html:\d+")

    def test_refused_design_exits_2(self):
        bad = self.run_cli(PAGE, "--design-system", str(DESIGNS / "minimal-invalid"))
        self.assertEqual(bad.returncode, 2)


class RecordTest(CliCase):
    """--record FILE writes the verdict the skill evals grade (Plan-0005 increment 12); the exit code is unchanged."""

    def record(self, html, *args):
        verdict = self.tmp / "out.html.verdict.txt"
        result = self.run_cli(html, "--record", str(verdict), *args)
        return result, verdict.read_text(encoding="utf-8").splitlines()

    def test_a_clean_page_records_pass_the_file_and_the_design(self):
        result, lines = self.record(PAGE, "--design-system", str(DESIGNS / "full"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(lines[0], "PASS: no findings")
        self.assertEqual(lines[1], f"file: {self.tmp / 'out.html'}")
        self.assertEqual(lines[2], "design: @acme-test/design-system@1.0.0")

    def test_the_base_theme_is_named(self):
        result, lines = self.record(PAGE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(lines[2], "design: base")

    def test_findings_are_recorded_with_a_fail_line(self):
        result, lines = self.record(page(".x { color: #123456; } .y { color: #654321; }"))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(lines[0], "FAIL: 2 finding(s)")
        self.assertTrue(lines[1].startswith("file: "), lines)
        self.assertTrue(any("#123456" in line for line in lines[3:]), lines)
        self.assertIn("#123456", result.stdout, "the findings are still printed")

    def test_declared_exceptions_are_recorded(self):
        result, lines = self.record(page(".x { color: #123456; }"), "--exception", "mine=#123456")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(lines[0], "PASS: no findings")
        self.assertIn("exception mine=#123456 (not in the design's vocabulary)", lines)

    def test_a_refused_design_is_recorded_as_a_fail(self):
        result, lines = self.record(PAGE, "--design-system", str(DESIGNS / "minimal-invalid"))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(lines[0], "FAIL: the design was refused")
        self.assertTrue(lines[1].startswith("file: "), lines)
        self.assertTrue(any("dataviz" in line for line in lines[2:]), lines)

    def test_without_record_no_verdict_file_is_written(self):
        self.run_cli(PAGE)
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["out.html"])


if __name__ == "__main__":
    unittest.main()
