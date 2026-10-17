"""Contract v2 (Plan-0005 increment 02): modules, manifest schema, base theme, shared sync."""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from helpers import SKILLS, RenderCase, run

PLUGIN = Path(__file__).resolve().parent.parent
CONTRACT = PLUGIN / "contract"
SHARED = PLUGIN / "shared"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "design-systems"
RENDERERS = ("com-slide-deck", "com-artefact-viz", "com-release-note")
MODULES = ("core", "dataviz", "type", "space-shape", "document", "slide-frame", "dark", "print", "brand", "guidance")
# the colour roles the dark module mirrors as --dark-<role>, module by module
MIRRORED = {
    "core": ("--ink", "--muted", "--tertiary", "--canvas-bg", "--surface", "--surface-2", "--border", "--accent",
             "--accent-ink", "--success", "--warning", "--danger", "--info", "--shadow"),
    "dataviz": ("--chart-1", "--chart-2", "--chart-3", "--chart-4", "--chart-rest", "--chart-axis", "--chart-grid",
                "--chart-highlight"),
    "slide-frame": ("--slide-bg", "--slide-fg"),
    "document": ("--doc-page-bg", "--doc-rule"),
    "print": ("--print-bg",),
}
DARK_EXTRA = ("--dark-key-fill", "--dark-key-base", "--dark-key-edge", "--dark-accent-text")
DARK_REQUIRED = {"--dark-canvas-bg", "--dark-surface", "--dark-border", "--dark-ink", "--dark-muted", "--dark-accent",
                 "--dark-accent-ink", "--dark-slide-bg", "--dark-slide-fg"}

sys.path.insert(0, str(SHARED))


def modules():
    return json.loads((CONTRACT / "modules.json").read_text(encoding="utf-8"))


def css_classes(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return set(re.findall(r"\.([a-zA-Z][\w-]*)", css))


class ModulesTest(unittest.TestCase):
    def test_declares_contract_version_and_ten_modules(self):
        data = modules()
        self.assertEqual(data["contractVersion"], "2.1.0")
        self.assertEqual(tuple(data["modules"]), MODULES)
        required = {name for name, m in data["modules"].items() if m["required"]}
        self.assertEqual(required, {"core", "dataviz"})

    def test_no_role_in_two_modules(self):
        seen = {}
        for name, m in modules()["modules"].items():
            for role in m["roles"]:
                self.assertNotIn(role, seen, f"{role} in {seen.get(role)} and {name}")
                seen[role] = name

    def test_dark_mirrors_every_colour_role(self):
        # the mirror is generated from modules.json: every role of a mirrored module except the listed ones
        mods = modules()["modules"]
        dark = mods["dark"]
        self.assertEqual(tuple(dark["mirror"]["modules"]), tuple(MIRRORED))
        generated = [role for name in dark["mirror"]["modules"] for role in mods[name]["roles"]
                     if role not in dark["mirror"]["except"]]
        self.assertEqual(generated, [role for roles in MIRRORED.values() for role in roles])
        import design_source
        twins = {role: "--dark-" + role[2:] for role in generated}
        self.assertEqual(design_source.dark_mirror(modules()), twins)
        self.assertEqual(list(dark["roles"]), list(twins.values()) + list(DARK_EXTRA))
        self.assertEqual(set(dark["requiredRoles"]), DARK_REQUIRED)
        self.assertLessEqual(set(dark["requiredRoles"]), set(dark["roles"]))
        self.assertEqual(set(dark["classes"]), {"dark", "dark-key", "dark-accent"})
        self.assertFalse(dark["required"])

    def test_dark_pairs_mirror_the_light_pairs(self):
        data = modules()
        twins = {role: "--dark-" + role[2:] for roles in MIRRORED.values() for role in roles}

        def key(pair):
            fg = tuple(pair["fg"]) if isinstance(pair["fg"], list) else (pair["fg"],)
            return fg, pair["bg"]

        expected = []
        for pair in data["pairs"]:
            fg, bg = key(pair)
            if all(role in twins for role in (*fg, bg)):
                expected.append((tuple(twins[role] for role in fg), twins[bg]))
        self.assertEqual(len(expected), len(data["pairs"]))   # every light pair has mirrored roles today
        expected += [(("--dark-ink",), "--dark-key-base"), (("--dark-accent-text",), "--dark-canvas-bg"),
                     (("--dark-accent-text",), "--dark-surface")]
        dark_pairs = data["modules"]["dark"]["pairs"]
        self.assertEqual([key(p) for p in dark_pairs], expected)
        roles = set(data["modules"]["dark"]["roles"])
        for pair in dark_pairs:
            self.assertEqual(set(pair), {"fg", "bg", "use"})
            self.assertTrue(pair["use"].strip())
            self.assertLessEqual({*key(pair)[0], pair["bg"]}, roles)

    def test_core_keeps_todays_24_roles_plus_tertiary(self):
        # the 24 roles of the old contract, plus the optional --tertiary text role added for 2.0.0
        roles = modules()["modules"]["core"]["roles"]
        self.assertEqual(len(roles), 25)
        self.assertIn("--tertiary", roles)

    def test_tertiary_text_is_a_checked_pair(self):
        self.assertIn({"fg": "--tertiary", "bg": "--canvas-bg"},
                      [{"fg": p["fg"], "bg": p["bg"]} for p in modules()["pairs"]])

    def test_slide_footer_and_source_bar_use_tertiary(self):
        css = (PLUGIN / "shared" / "base" / "slide-frame.css").read_text(encoding="utf-8")
        for selector in (".slide-footer", ".slide-source-bar"):
            with self.subTest(selector=selector):
                block = css[css.index(selector + " {"):]
                block = block[:block.index("}")]
                self.assertIn("color: var(--tertiary)", block)

    def test_dataviz_roles(self):
        roles = set(modules()["modules"]["dataviz"]["roles"])
        self.assertEqual(roles, {"--chart-1", "--chart-2", "--chart-3", "--chart-4", "--chart-rest",
                                 "--chart-axis", "--chart-grid", "--chart-highlight"})

    def test_every_filled_badge_has_a_text_pair(self):
        # owner 2026-10-14: text on every fill the renderers paint text on is a checked pair; either text role
        # may carry it (a list pair passes when any of its roles reaches AA, the resolver picks that role)
        fills = ("--success", "--info", "--warning", "--danger", "--muted", "--chart-1", "--chart-2", "--chart-3")
        pairs = modules()["pairs"]
        for bg in fills:
            with self.subTest(fill=bg):
                named = [p for p in pairs if p["bg"] == bg]
                self.assertEqual([p["fg"] for p in named], [["--accent-ink", "--ink"]])
                self.assertIn("text on", named[0]["use"].lower())

    def test_single_role_pairs_stay_single(self):
        single = {(p["fg"], p["bg"]) for p in modules()["pairs"] if isinstance(p["fg"], str)}
        self.assertLessEqual({("--ink", "--canvas-bg"), ("--ink", "--surface"), ("--muted", "--surface"),
                              ("--accent-ink", "--accent"), ("--accent", "--surface")}, single)

    def test_class_vocabularies_cover_what_the_renderers_emit(self):
        mods = modules()["modules"]
        doc = css_classes((SKILLS / "com-slide-deck/templates/doc.baseline.css").read_text(encoding="utf-8"))
        doc -= {"controls-hint", "slide-source-bar"}
        self.assertLessEqual(doc, set(mods["document"]["classes"]))
        build = (SKILLS / "com-slide-deck/scripts/build.py").read_text(encoding="utf-8")
        body = build.split("def make_baseline_css", 1)[1].split("\ndef ", 1)[0]
        self.assertLessEqual(css_classes(body), set(mods["slide-frame"]["classes"]))
        report = (SKILLS / "com-release-note/templates/report.html.tmpl").read_text(encoding="utf-8")
        page = {c for c in css_classes(report) if re.match(r"(report|section)(-|$)|section--", c)}
        self.assertLessEqual(page, set(mods["print"]["classes"]))
        for name in ("core", "dataviz", "brand"):
            self.assertNotIn("classes", mods[name])

    def test_slide_frame_roles_and_classes(self):
        frame = modules()["modules"]["slide-frame"]
        self.assertEqual(set(frame["roles"]), {"--slide-bg", "--slide-fg", "--slide-padding",
                                               "--slide-width", "--slide-height"})
        self.assertEqual(set(frame["classes"]), {"slide", "active", "presenting", "controls-hint", "slide-source-bar",
                                                 "slide-label", "slide-footer", "slide-logo", "slide-legal",
                                                 "slide-number"})
        base = css_classes((SHARED / "base/slide-frame.css").read_text(encoding="utf-8"))
        self.assertIn("slide-footer", base)
        self.assertLessEqual(base, set(frame["classes"]))

    def test_print_roles(self):
        # Increment 09: the print module gives the page box (size and margin) and the page background
        # plus --print-breaking, the optional accent of breaking changes in printed reports (defaults to --danger)
        roles = modules()["modules"]["print"]["roles"]
        self.assertEqual(set(roles), {"--print-bg", "--print-margin", "--print-page-size", "--print-breaking"})
        self.assertIn("optional", roles["--print-breaking"])
        self.assertIn("--danger", roles["--print-breaking"])

    def test_print_breaking_defaults_to_danger_in_the_base_theme(self):
        css = (SHARED / "base/print.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"--print-breaking:\s*var\(--danger\);")

    def test_brand_roles(self):
        self.assertEqual(set(modules()["modules"]["brand"]["roles"]),
                         {"--brand-logo-on-light", "--brand-logo-on-dark", "--brand-mark", "--brand-legal"})

    def test_pairs_name_existing_roles(self):
        roles = {r for m in modules()["modules"].values() for r in m["roles"]}
        pairs = modules()["pairs"]
        self.assertTrue(pairs)
        for pair in pairs:
            self.assertEqual(set(pair), {"fg", "bg", "use"})
            fg = pair["fg"] if isinstance(pair["fg"], list) else [pair["fg"]]
            self.assertTrue(fg, pair)
            self.assertEqual(len(set(fg)), len(fg), pair)
            for role in fg:
                self.assertIn(role, roles)
            self.assertIn(pair["bg"], roles)
            self.assertNotIn(pair["bg"], fg)
            self.assertTrue(pair["use"].strip())


class ManifestCheckTest(unittest.TestCase):
    def setUp(self):
        import manifest_check
        self.check = manifest_check.check
        self.schema = json.loads((CONTRACT / "kit-manifest.schema.json").read_text(encoding="utf-8"))
        self.implemented = manifest_check.KEYWORDS

    def fixture(self, name):
        return json.loads((FIXTURES / name / "kit-manifest.json").read_text(encoding="utf-8"))

    def errors(self, manifest):
        return self.check(manifest, self.schema)

    def test_accepts_full_and_subset(self):
        self.assertEqual(self.errors(self.fixture("full")), [])
        self.assertEqual(self.errors(self.fixture("subset")), [])
        self.assertEqual(self.errors(self.fixture("full-dark")), [])
        self.assertIn("dark", self.fixture("full-dark")["provides"])
        self.assertNotIn("dark", self.fixture("full")["provides"])

    def test_rejects_missing_dataviz(self):
        self.assertTrue(any("dataviz" in e for e in self.errors(self.fixture("minimal-invalid"))))

    def test_rejects_unknown_module_bad_semver_and_unknown_key(self):
        base = self.fixture("subset")
        self.assertTrue(self.errors({**base, "provides": {**base["provides"], "sparkles": "./x.css"}}))
        self.assertTrue(self.errors({**base, "contractVersion": "2.0"}))
        self.assertTrue(self.errors({**base, "colour": "red"}))
        # a 2.0 manifest still validates under 2.1, and dark may be omitted with a reason
        self.assertEqual(base["contractVersion"], "2.0.0")
        self.assertEqual(self.errors(base), [])
        self.assertEqual(self.errors({**base, "omitted": {**base["omitted"], "dark": "no dark theme"}}), [])
        for module in MODULES:
            self.assertEqual(self.errors({**base, "omitted": {module: "reason"}}), [], module)
        self.assertTrue(self.errors({**base, "omitted": {"night": "reason"}}))

    def test_schema_uses_only_implemented_keywords(self):
        annotations = {"$schema", "$id", "title", "description"}

        def walk(node):
            used = set(node) - annotations
            self.assertLessEqual(used, self.implemented)
            for sub in node.get("properties", {}).values():
                walk(sub)
            if isinstance(node.get("additionalProperties"), dict):
                walk(node["additionalProperties"])
        walk(self.schema)
        self.assertIn("2.1.0", self.schema["$id"])
        self.assertIn("contract 2.1.0", self.schema["title"])

    def test_schema_id_has_no_fragment(self):
        # JSON Schema 2020-12 forbids a non-empty fragment in $id, and ajv refuses the schema with one
        self.assertNotIn("#", self.schema["$id"].rstrip("#"))


class BaseThemeTest(unittest.TestCase):
    def test_base_defines_every_role_of_every_module(self):
        base = SHARED / "base"
        for name, m in modules()["modules"].items():
            if not m["roles"]:
                continue
            css = (base / f"{name}.css").read_text(encoding="utf-8")
            for role in m["roles"]:
                self.assertRegex(css, re.escape(role) + r"\s*:", f"{name}.css lacks {role}")
        # dark: literals on :root only (an alias to a light role would make the remap a cycle), pairs at AA
        import design_source
        css = re.sub(r"/\*.*?\*/", "", (base / "dark.css").read_text(encoding="utf-8"), flags=re.S)
        self.assertEqual([s.strip() for s in re.findall(r"([^{}]+)\{", css)], [":root"])
        self.assertNotIn("var(", css)
        dark = modules()["modules"]["dark"]
        self.assertEqual(set(design_source.role_values(css)), set(dark["roles"]))
        values = design_source.role_values(css)
        for pair in dark["pairs"]:
            with self.subTest(pair=pair["use"]):
                tried = design_source.pair_ratios(values, pair)
                self.assertIsNotNone(tried, "every role of a dark pair is a hex colour in the base")
                self.assertTrue(any(ratio >= 4.5 for _, ratio in tried), tried)

    def test_core_has_heading_font_and_no_legacy_alias(self):
        css = (SHARED / "base/core.css").read_text(encoding="utf-8")
        self.assertIn("--font-heading:", css)
        self.assertNotIn("--font-sans", css)


class SyncTest(RenderCase):
    def test_every_skill_copy_matches_the_canonical_shared(self):
        result = run(PLUGIN / "scripts/sync-shared.py", "--check", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_fallback_copies_are_gone_and_renderers_still_theme(self):
        for skill in RENDERERS:
            self.assertFalse((SKILLS / skill / "templates/tokens.fallback.css").exists(), skill)
        init = run(SKILLS / "com-slide-deck/scripts/init.py", "deck", cwd=self.tmp)
        self.assertEqual(init.returncode, 0, init.stderr)
        run(SKILLS / "com-slide-deck/scripts/build.py", "-c", "deck/config.yaml", cwd=self.tmp)
        html = (self.tmp / "deck/output/slide-deck/presentation.html").read_text(encoding="utf-8")
        self.assertIn("--font-heading:", html)
        note = SKILLS / "com-release-note/examples/release-note.complete.md"
        run(SKILLS / "com-release-note/scripts/render_pdf.py", note, "--html-only", "--output", "rn.pdf", cwd=self.tmp)
        self.assertIn("--font-heading:", (self.tmp / "rn.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
