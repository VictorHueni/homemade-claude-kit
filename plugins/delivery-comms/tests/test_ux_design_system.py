"""ux-design-system `point`, `subset`, `subset --from-legacy` and `scaffold` (Plan-0005 increment 11).

`point` is tested against the local registry stub of test_resolver (DELIVERY_COMMS_NPM_REGISTRY) and a local
folder; nothing here reaches the real npm registry.
"""
import json
import os
import re
import shutil
import sys
import unittest
from pathlib import Path

import yaml

from helpers import SKILLS, RenderCase, run
from test_resolver import Registry, tarball

PLUGIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN / "shared"))

import check_render  # noqa: E402
import design_source  # noqa: E402

UX = SKILLS / "ux-design-system"
SCRIPT = UX / "scripts/design_system.py"
DESIGNS = PLUGIN / "tests/fixtures/design-systems"
CONTRACT = design_source._contract()
DATAVIZ = set(CONTRACT["modules"]["dataviz"]["roles"])
CORE = list(CONTRACT["modules"]["core"]["roles"])

COLORS = {"ink": "#101828", "muted": "#475467", "canvas-bg": "#f9fafb", "surface": "#ffffff",
          "surface-2": "#f2f4f7", "border": "#d0d5dd", "accent": "#7a3ea8", "accent-ink": "#ffffff",
          "success": "#027a48", "warning": "#b54708", "danger": "#b42318", "info": "#7a3ea8"}
TYPOGRAPHY = {"font-body": "Georgia, serif", "font-heading": "system-ui, sans-serif",
              "font-mono": "ui-monospace, monospace", "title-size": "1.8rem"}
ROUNDED = {"card-radius": "6px", "btn-radius": "4px", "node-radius": "6px"}
SPACING = {"space-sm": "0.5rem", "space-md": "1rem", "space-lg": "2rem", "shell-max": "1200px"}
ELEVATION = {"shadow": "none"}
CHARTS = {"chart-1": "#1d2939", "chart-2": "#0e7090", "chart-3": "#6ab2c9", "chart-4": "#b7dbe6",
          "chart-rest": "#98a2b3", "chart-axis": "#475467", "chart-grid": "#eaecf0", "chart-highlight": "#b54708"}
PROSE = "\n# Small project design\n\n## Overview\n\nCalm and plain.\n\n## Do's and Don'ts\n\n- Do keep red for errors.\n"


def front(**overrides):
    data = {"name": "Small Project", "colors": dict(COLORS), "typography": dict(TYPOGRAPHY),
            "rounded": dict(ROUNDED), "spacing": dict(SPACING), "elevation": dict(ELEVATION),
            "dataviz": dict(CHARTS), "omitted": {"brand": "no logo yet", "print": "no printed reports"}}
    for key, value in overrides.items():
        if value is None:
            data.pop(key, None)
        else:
            data[key] = value
    return data


def design_md(data, prose=PROSE):
    return "---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True) + "---\n" + prose


class UxCase(RenderCase):
    def setUp(self):
        super().setUp()
        self.project = self.tmp / "project"
        self.ux = self.project / "docs/ux"
        self.ux.mkdir(parents=True)
        # a closed local port: anything that is not pointed at the registry stub fails instead of reaching npm
        self.env = {"XDG_CACHE_HOME": str(self.tmp / "cache"), "DELIVERY_COMMS_NPM_REGISTRY": "http://127.0.0.1:9"}
        self.use_env()

    def use_env(self):
        """The same cache and registry for in-process resolves as for the script runs."""
        for key, value in self.env.items():
            saved = os.environ.get(key)
            os.environ[key] = value
            self.addCleanup(lambda k=key, v=saved: os.environ.pop(k, None) if v is None
                            else os.environ.__setitem__(k, v))

    def ds(self, *args, cwd=None, env=None):
        return run(SCRIPT, *args, cwd=cwd or self.project, env={**self.env, **(env or {})})

    def write(self, data, prose=PROSE, name="DESIGN.md"):
        path = self.ux / name
        path.write_text(design_md(data, prose), encoding="utf-8")
        return path

    def subset(self, *args, code=0):
        result = self.ds("subset", *(args or ("docs/ux/DESIGN.md",)))
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def accept_proposal(self, path=None):
        path = path or self.ux / "DESIGN.md"
        text = path.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines(keepends=True) if not re.match(r"\s*proposed\s*:", line)]
        self.assertNotEqual(len(lines), len(text.splitlines()), "no proposed mark to remove")
        path.write_text("".join(lines), encoding="utf-8")


class ScriptTest(UxCase):
    def test_renamed_to_design_system_py(self):
        self.assertTrue(SCRIPT.is_file())
        self.assertFalse((UX / "scripts/generate_tokens.py").exists())

    def test_generate_and_refresh_are_removed_and_name_subset(self):
        for mode in ("generate", "refresh"):
            with self.subTest(mode=mode):
                result = self.ds(mode, "docs/ux/design-system.md")
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn("subset docs/ux/DESIGN.md", result.stdout + result.stderr)
                self.assertIn("subset --from-legacy", result.stdout + result.stderr)

    def test_the_skill_carries_its_own_shared_copy(self):
        for name in ("design_source.py", "manifest_check.py", "modules.json", "base/core.css"):
            self.assertTrue((UX / "scripts/shared" / name).is_file(), name)


class ScaffoldTest(UxCase):
    def test_writes_docs_ux_design_md_and_no_token_file(self):
        result = self.ds("scaffold")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.ux / "DESIGN.md").is_file())
        self.assertFalse((self.project / "docs/design").exists())
        self.assertFalse((self.ux / "tokens.css").exists())
        self.assertFalse((self.ux / "design-system.md").exists())

    def test_existing_file_is_kept(self):
        (self.ux / "DESIGN.md").write_text("mine\n", encoding="utf-8")
        result = self.ds("scaffold")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.ux / "DESIGN.md").read_text(encoding="utf-8"), "mine\n")

    def test_scaffolded_file_parses_and_asks_for_a_palette(self):
        self.ds("scaffold")
        result = self.subset(code=2)
        self.assertIn("proposed", result.stdout + result.stderr)


class SubsetTest(UxCase):
    def test_writes_one_css_file_per_filled_module_and_the_manifest(self):
        self.write(front())
        self.subset()
        out = self.ux / "design-system"
        manifest = json.loads((out / "kit-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["contractVersion"], CONTRACT["contractVersion"])
        self.assertEqual(set(manifest["provides"]), {"core", "dataviz", "guidance"})
        self.assertEqual(manifest["omitted"], {"brand": "no logo yet", "print": "no printed reports"})
        for module in ("core", "dataviz"):
            css = (out / f"{module}.css").read_text(encoding="utf-8")
            for role in CONTRACT["modules"][module]["roles"]:
                self.assertRegex(css, re.escape(role) + r"\s*:", f"{module}.css lacks {role}")
        self.assertFalse((out / "type.css").exists())
        self.assertIn("Do keep red for errors.", (out / "guidance.md").read_text(encoding="utf-8"))
        design = design_source.resolve(self.project, explicit=out)
        self.assertEqual(design.provenance["modules"]["core"], "design-system")
        self.assertEqual(design_source.role_values(design.css["core"])["--accent"], "#7a3ea8")

    def test_writes_the_pin_the_renderers_follow(self):
        self.write(front())
        self.subset()
        pin = json.loads((self.ux / "package.json").read_text(encoding="utf-8"))
        (name, spec), = pin["dependencies"].items()
        self.assertEqual(spec, "file:design-system")
        design = design_source.resolve(self.project / "docs/somewhere")
        self.assertEqual(design.provenance["designSystem"]["name"], name)
        self.assertEqual(design.provenance["modules"]["dataviz"], "design-system")

    def test_a_registry_pin_is_left_alone(self):
        (self.ux / "package.json").write_text(json.dumps({"dependencies": {"@acme-test/ds": "1.0.0"}}),
                                              encoding="utf-8")
        self.write(front())
        result = self.subset()
        self.assertIn("@acme-test/ds", result.stdout + result.stderr)
        self.assertEqual(json.loads((self.ux / "package.json").read_text())["dependencies"],
                         {"@acme-test/ds": "1.0.0"})

    def test_optional_modules_are_written_when_filled_whole(self):
        typography = {**TYPOGRAPHY, "font-size-xs": "0.75rem", "font-size-sm": "0.875rem", "font-size-md": "1rem",
                      "font-size-lg": "1.25rem", "font-size-xl": "2rem", "line-height-body": 1.5,
                      "line-height-tight": 1.2, "font-weight-regular": 400, "font-weight-bold": 700}
        self.write(front(typography=typography))
        self.subset()
        manifest = json.loads((self.ux / "design-system/kit-manifest.json").read_text(encoding="utf-8"))
        self.assertIn("type", manifest["provides"])
        css = (self.ux / "design-system/type.css").read_text(encoding="utf-8")
        self.assertIn("--line-height-body: 1.5;", css)
        self.assertIn("--font-weight-bold: 700;", css)

    def test_a_module_filled_in_part_is_an_error_naming_the_missing_roles(self):
        self.write(front(typography={**TYPOGRAPHY, "font-size-xs": "0.7rem"}))
        result = self.subset(code=2)
        self.assertIn("type", result.stderr)
        self.assertIn("font-size-xl", result.stderr)
        self.assertFalse((self.ux / "design-system").exists())

    def test_core_must_be_complete(self):
        colors = dict(COLORS)
        del colors["border"]
        self.write(front(colors=colors))
        result = self.subset(code=2)
        self.assertIn("border", result.stderr)
        self.assertFalse((self.ux / "design-system").exists())

    def test_a_module_both_filled_and_omitted_is_an_error(self):
        self.write(front(omitted={"dataviz": "none"}))
        self.assertIn("dataviz", self.subset(code=2).stderr)

    def test_colours_must_be_hex(self):
        self.write(front(colors={**COLORS, "accent": "rebeccapurple"}))
        result = self.subset(code=2)
        self.assertIn("accent", result.stderr)
        self.assertIn("hex", result.stderr)

    def test_a_value_that_could_break_out_of_css_is_refused(self):
        self.write(front(typography={**TYPOGRAPHY, "font-body": "serif; } body { color: red"}))
        self.assertIn("font-body", self.subset(code=2).stderr)

    def test_a_refused_run_keeps_the_previous_output(self):
        self.write(front())
        self.subset()
        before = (self.ux / "design-system/core.css").read_text(encoding="utf-8")
        self.write(front(colors={**COLORS, "accent-ink": "#9a9a9a"}))
        self.subset(code=2)
        self.assertEqual((self.ux / "design-system/core.css").read_text(encoding="utf-8"), before)
        self.assertEqual([p.name for p in self.ux.iterdir() if p.name.startswith(".")], [])

    def test_font_faces_are_copied_and_inlined_by_the_resolver(self):
        shutil.copy(DESIGNS / "full/fonts/acme.woff2", self.ux / "acme.woff2")
        self.write(front(fonts=[{"family": "Acme Sans", "src": "acme.woff2", "weight": 400}],
                         typography={**TYPOGRAPHY, "font-body": '"Acme Sans", sans-serif'}))
        self.subset()
        self.assertTrue((self.ux / "design-system/fonts/acme.woff2").is_file())
        design = design_source.resolve(self.project)
        self.assertEqual(len(design.fonts), 1)
        self.assertIn('font-family: "Acme Sans"', design.fonts[0])
        self.assertIn("data:font/woff2;base64,", design.fonts[0])

    def test_a_network_font_is_refused(self):
        self.write(front(fonts=[{"family": "Remote", "src": "https://fonts.example.test/r.woff2"}]))
        self.assertIn("fonts", self.subset(code=2).stderr)


class FrontMatterTest(UxCase):
    def test_unknown_top_level_key_names_the_key_and_the_allowed_keys(self):
        self.write(front(components={"button": {"backgroundColor": "#000"}}))
        stderr = self.subset(code=2).stderr
        self.assertIn("components", stderr)
        for allowed in ("colors", "typography", "rounded", "spacing", "omitted"):
            self.assertIn(allowed, stderr)

    def test_unknown_key_in_a_group_names_the_key_and_the_allowed_keys(self):
        self.write(front(colors={**COLORS, "primary": "#000000"}))
        stderr = self.subset(code=2).stderr
        self.assertIn("primary", stderr)
        self.assertIn("accent-ink", stderr)

    def test_unknown_omitted_module_is_an_error(self):
        self.write(front(omitted={"logo": "none"}))
        self.assertIn("logo", self.subset(code=2).stderr)

    def test_safe_loader_refuses_python_tags(self):
        path = self.ux / "DESIGN.md"
        path.write_text("---\nname: !!python/object/apply:os.system ['true']\n---\n", encoding="utf-8")
        result = self.subset(code=2)
        self.assertIn("front matter", result.stderr)

    def test_no_front_matter_is_an_error(self):
        (self.ux / "DESIGN.md").write_text("# no front matter\n", encoding="utf-8")
        self.assertIn("front matter", self.subset(code=2).stderr)

    def test_artefact_frontmatter_keys_are_allowed(self):
        data = {"type": "Design System", "title": "Small", "status": "draft", "owner": "someone",
                "last_reviewed": "2026-10-14", "review_interval": "180d", **front()}
        self.write(data)
        self.subset()


class ContrastTest(UxCase):
    def test_pairs_below_aa_are_refused_by_the_resolver_rule(self):
        self.write(front(colors={**COLORS, "accent-ink": "#f0f0f0", "accent": "#a78bfa"}))
        stderr = self.subset(code=2).stderr
        self.assertIn("--accent-ink on --accent", stderr)
        self.assertRegex(stderr, r"contrast \d+\.\d\d")
        self.assertFalse((self.ux / "design-system").exists())

    def test_a_fill_pair_passes_when_either_text_role_reaches_aa(self):
        # a light success fill with dark text: --accent-ink fails on it, --ink passes
        self.write(front(colors={**COLORS, "success": "#a6f4c5"}))
        self.subset()

    def test_a_fill_on_which_neither_text_role_passes_is_refused(self):
        self.write(front(dataviz={**CHARTS, "chart-2": "#808080"}))
        stderr = self.subset(code=2).stderr
        self.assertIn("--chart-2", stderr)
        self.assertIn("no text role reaches WCAG AA", stderr)


class ProposedPaletteTest(UxCase):
    def proposed(self, colors=None):
        self.write(front(dataviz=None, colors=colors or dict(COLORS)))
        result = self.subset(code=2)
        text = (self.ux / "DESIGN.md").read_text(encoding="utf-8")
        data = yaml.safe_load(text.split("---\n")[1])
        return result, data["dataviz"], text

    def test_a_source_without_dataviz_gets_a_proposed_block_and_no_output(self):
        result, block, text = self.proposed()
        self.assertIn("proposed", block)
        self.assertIn("proposed", result.stdout + result.stderr)
        self.assertIn(PROSE.strip(), text)
        self.assertFalse((self.ux / "design-system").exists())

    def test_the_proposal_fills_exactly_the_dataviz_roles(self):
        _, block, _ = self.proposed()
        self.assertEqual({"--" + k for k in block if k != "proposed"}, DATAVIZ)

    def test_four_steps_from_the_accent_towards_the_surface_darkest_first(self):
        _, block, _ = self.proposed()
        self.assertEqual(block["chart-1"].lower(), COLORS["accent"])
        lum = [design_source._luminance(block[f"chart-{i}"]) for i in range(1, 5)]
        self.assertEqual(lum, sorted(lum))
        self.assertLess(lum[3], design_source._luminance(COLORS["surface"]))
        self.assertEqual(block["chart-axis"].lower(), COLORS["muted"])
        self.assertEqual(block["chart-grid"].lower(), COLORS["border"])
        self.assertEqual(block["chart-highlight"].lower(), COLORS["warning"])

    def test_the_proposal_passes_the_contract_pairs(self):
        charts = [pair for pair in CONTRACT["pairs"] if pair["bg"].startswith("--chart-")]
        for accent in ("#7a3ea8", "#396cf5", "#0e7090", "#c2410c"):
            with self.subTest(accent=accent):
                self.setUp()
                _, block, _ = self.proposed(colors={**COLORS, "accent": accent})
                css = ":root {" + "".join(f"--{k}: {v};" for k, v in {**COLORS, "accent": accent}.items())
                css += "".join(f"--{k}: {v};" for k, v in block.items() if k != "proposed") + "}"
                self.assertEqual(design_source.failing_pairs(css, charts), [])

    def test_generation_refuses_while_the_mark_remains(self):
        self.proposed()
        result = self.subset(code=2)
        self.assertIn("proposed", result.stderr)
        self.assertIn("remove", result.stderr)
        self.assertFalse((self.ux / "design-system").exists())

    def test_removing_the_mark_generates(self):
        self.proposed()
        self.accept_proposal()
        self.subset()
        self.assertTrue((self.ux / "design-system/dataviz.css").is_file())


class FromLegacyTest(UxCase):
    LEGACY = (":root {\n  --ink: #13211f; --muted: #5f6b69; --canvas-bg: #f5f7f6; --surface: #ffffff;\n"
              "  --surface-2: #ecf1ef; --border: #d3dcd9; --accent: #0f766e; --accent-ink: #ffffff;\n"
              "  --success: #15803d; --warning: #b45309; --danger: #b91c1c; --info: var(--accent);\n"
              '  --font-sans: "Inter", system-ui, sans-serif; --font-mono: ui-monospace, monospace;\n'
              "  --title-size: 1.5rem; --space-sm: 0.5rem; --space-md: 1rem; --space-lg: 2rem;\n"
              "  --shell-max: 1280px; --card-radius: 10px; --btn-radius: 6px; --node-radius: 8px;\n"
              "  --shadow: 0 1px 2px rgba(0,0,0,.08);\n  --dim: #9aa5a2;\n}\n")

    def legacy(self, where="docs/ux/tokens.css"):
        path = self.project / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.LEGACY, encoding="utf-8")
        return path

    def test_writes_a_draft_design_md_with_core_and_a_proposed_dataviz_block(self):
        self.legacy()
        result = self.ds("subset", "--from-legacy", "docs/ux/tokens.css")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = (self.ux / "DESIGN.md").read_text(encoding="utf-8")
        data = yaml.safe_load(text.split("---\n")[1])
        self.assertEqual(data["colors"]["accent"], "#0f766e")
        self.assertEqual(data["colors"]["info"], "#0f766e")             # var(--accent) followed
        self.assertEqual(data["typography"]["font-body"], '"Inter", system-ui, sans-serif')  # --font-sans alias
        self.assertEqual(data["elevation"]["shadow"], "0 1px 2px rgba(0,0,0,.08)")
        self.assertIn("proposed", data["dataviz"])
        self.assertIn("--dim", result.stdout + result.stderr)            # not mapped, named
        self.assertEqual((self.ux / "tokens.css").read_text(encoding="utf-8"), self.LEGACY)

    def test_font_rules_are_named_as_not_mapped(self):
        path = self.legacy()
        path.write_text('@import url("https://fonts.example.test/css?family=Inter");\n' + self.LEGACY,
                        encoding="utf-8")
        result = self.ds("subset", "--from-legacy", "docs/ux/tokens.css")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("@import", result.stdout)
        self.assertNotIn("fonts.example.test", (self.ux / "DESIGN.md").read_text(encoding="utf-8"))

    def test_missing_core_roles_come_from_the_base_and_are_named(self):
        self.legacy()
        result = self.ds("subset", "--from-legacy", "docs/ux/tokens.css")
        data = yaml.safe_load((self.ux / "DESIGN.md").read_text(encoding="utf-8").split("---\n")[1])
        base = design_source.role_values(re.sub(r"/\*.*?\*/", "", (PLUGIN / "shared/base/core.css").read_text(
            encoding="utf-8"), flags=re.S))
        self.assertEqual(data["typography"]["font-heading"], base["--font-heading"])
        self.assertIn("font-heading", result.stdout + result.stderr)

    def test_accepts_the_older_docs_design_location(self):
        self.legacy("docs/design/tokens.css")
        result = self.ds("subset", "--from-legacy", "docs/design/tokens.css")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.ux / "DESIGN.md").is_file())

    def test_an_existing_design_md_is_not_overwritten(self):
        self.legacy()
        (self.ux / "DESIGN.md").write_text("mine\n", encoding="utf-8")
        result = self.ds("subset", "--from-legacy", "docs/ux/tokens.css")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual((self.ux / "DESIGN.md").read_text(encoding="utf-8"), "mine\n")

    def test_the_kit_sample_legacy_file_converts_and_its_accent_is_refused(self):
        # the sample's teal accent (#0f9d8f) carries white text at 3.4:1: converted as is, refused by subset
        shutil.copy(UX / "examples/legacy.tokens.css", self.ux / "tokens.css")
        result = self.ds("subset", "--from-legacy", "docs/ux/tokens.css")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.accept_proposal()
        self.assertIn("--accent-ink on --accent", self.subset(code=2).stderr)

    def test_the_kit_sample_design_md_subsets(self):
        shutil.copy(UX / "examples/DESIGN.sample.md", self.ux / "DESIGN.md")
        self.subset()


class PointTest(UxCase):
    def setUp(self):
        super().setUp()
        self.registry = Registry()
        self.addCleanup(self.registry.close)
        self.env["DELIVERY_COMMS_NPM_REGISTRY"] = self.registry.url
        self.use_env()

    def publish(self, fixture, name, version="1.2.3"):
        self.registry.add(name, version, tarball(DESIGNS / fixture))

    def test_writes_the_exact_pin_validates_and_prints_the_dependabot_entry(self):
        self.publish("full", "@acme-test/design-system")
        result = self.ds("point", "@acme-test/design-system@1.2.3")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        pin = json.loads((self.ux / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["dependencies"], {"@acme-test/design-system": "1.2.3"})
        self.assertTrue(any(p.startswith("/@acme-test/design-system/1.2.3") for p in self.registry.requests))
        entry = yaml.safe_load(result.stdout[result.stdout.index("version: 2"):])
        update, = entry["updates"]
        self.assertEqual(update["package-ecosystem"], "npm")
        self.assertEqual(update["directory"], "/docs/ux")
        self.assertFalse((self.project / ".github").exists())     # printed, not written
        design = design_source.resolve(self.project)
        self.assertEqual(design.provenance["designSystem"]["source"], "registry")

    def test_an_unscoped_name_works(self):
        self.publish("subset", "acme-design")
        result = self.ds("point", "acme-design@1.2.3")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_range_or_a_missing_version_is_refused(self):
        for spec in ("@acme-test/design-system@^1.2.3", "@acme-test/design-system", "acme-design@latest"):
            with self.subTest(spec=spec):
                result = self.ds("point", spec)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("exact version", result.stderr)
                self.assertFalse((self.ux / "package.json").exists())

    def test_an_invalid_manifest_is_refused_and_writes_no_pin(self):
        self.publish("minimal-invalid", "@acme-test/broken")
        result = self.ds("point", "@acme-test/broken@1.2.3")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("dataviz", result.stderr)
        self.assertFalse((self.ux / "package.json").exists())

    def test_an_unknown_version_is_refused_and_writes_no_pin(self):
        result = self.ds("point", "@acme-test/design-system@9.9.9")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse((self.ux / "package.json").exists())

    def test_a_local_folder_is_pinned_with_a_relative_file_spec(self):
        shutil.copytree(DESIGNS / "full", self.project / "design-preview")
        result = self.ds("point", "design-preview")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        pin = json.loads((self.ux / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["dependencies"], {"@acme-test/design-system": "file:../../design-preview"})
        self.assertEqual(self.registry.requests, [])
        self.assertEqual(design_source.resolve(self.project).provenance["modules"]["brand"], "design-system")

    def test_repointing_replaces_the_single_dependency(self):
        self.publish("full", "@acme-test/design-system")
        self.publish("subset", "@acme-test/design-subset", "2.0.0")
        self.ds("point", "@acme-test/design-system@1.2.3")
        result = self.ds("point", "@acme-test/design-subset@2.0.0")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        pin = json.loads((self.ux / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pin["dependencies"], {"@acme-test/design-subset": "2.0.0"})


class EndToEndTest(UxCase):
    """Exit criterion: a DESIGN.md, or a legacy token file, becomes a validated subset the three renderers
    accept, with no hand-written CSS."""

    def render_all(self):
        project = self.project
        design = design_source.resolve(project)
        self.assertEqual(design.provenance["designSystem"]["source"], "path")
        # com-artefact-viz: a view, from a subfolder (the pin is found walking up)
        views = project / "docs/product"
        views.mkdir(parents=True, exist_ok=True)
        viz = SKILLS / "com-artefact-viz"
        result = run(viz / "scripts/render.py", viz / "examples/fbs.sample.md", "--out", "fbs.html", cwd=views)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (views / "fbs.html").read_text(encoding="utf-8")
        self.assertEqual(check_render.check(html, design)["findings"], [])
        # com-release-note: the HTML report
        note = SKILLS / "com-release-note/examples/release-note.complete.md"
        result = run(SKILLS / "com-release-note/scripts/render_pdf.py", note, "--html-only", "--output",
                     "rn.pdf", cwd=project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (project / "rn.html").read_text(encoding="utf-8")
        self.assertEqual(check_render.check(html, design)["findings"], [])
        # com-slide-deck: a scaffolded deck, built (the build runs the validator and prints PASS)
        deck = SKILLS / "com-slide-deck/scripts"
        result = run(deck / "init.py", "deck", cwd=project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = run(deck / "build.py", "-c", "deck/config.yaml", cwd=project)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)
        for prov in (views / "fbs.html.provenance.json", project / "rn.html.provenance.json",
                     project / "deck/output/slide-deck/presentation.html.provenance.json"):
            data = json.loads(prov.read_text(encoding="utf-8"))
            self.assertEqual(data["modules"]["core"], "design-system", prov.name)
            self.assertEqual(data["modules"]["dataviz"], "design-system", prov.name)
        accent = design_source.role_values(design.css["core"])["--accent"]
        self.assertIn(accent, (project / "deck/output/slide-deck/presentation.html").read_text(encoding="utf-8"))
        return design

    def test_from_a_scaffolded_design_md(self):
        self.ds("scaffold")
        path = self.ux / "DESIGN.md"
        path.write_text(path.read_text(encoding="utf-8").replace("#396cf5", "#0e7090"), encoding="utf-8")
        self.subset(code=2)
        self.accept_proposal()
        self.subset()
        design = self.render_all()
        self.assertEqual(design_source.role_values(design.css["core"])["--accent"], "#0e7090")

    def test_from_a_legacy_token_file(self):
        (self.ux / "tokens.css").write_text(FromLegacyTest.LEGACY, encoding="utf-8")
        result = self.ds("subset", "--from-legacy", "docs/ux/tokens.css")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.accept_proposal()
        self.subset()
        os.remove(self.ux / "tokens.css")
        design = self.render_all()
        self.assertEqual(design_source.role_values(design.css["core"])["--accent"], "#0f766e")


if __name__ == "__main__":
    unittest.main()
