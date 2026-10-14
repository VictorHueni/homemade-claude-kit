"""com-artefact-viz domain colours on contract roles (Plan-0005 increment 07), on the resolver and the
validator (increment 08).

Owner ruling Q-5: status and pain keep the core state roles; importance and
confidence are ordered scales on --chart-1 to --chart-3, darkest first. Every
colour a view draws traces to a contract role through one --kit-* property.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from helpers import SKILLS, RenderCase, run

PLUGIN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN / "shared"))

import check_render  # noqa: E402
import design_source  # noqa: E402

VIZ = SKILLS / "com-artefact-viz"
RENDER = VIZ / "scripts/render.py"
DOMAIN = VIZ / "templates/tokens.domain.css"
TEMPLATE = VIZ / "templates/base.html.tmpl"
RENDERERS = VIZ / "scripts/renderers.py"
EXAMPLES = VIZ / "examples"
DESIGNS = PLUGIN / "tests/fixtures/design-systems"
SB = EXAMPLES / "service-blueprint"
ROLES = {role for module in design_source._contract()["modules"].values() for role in module["roles"]}
DOMAIN_MARKER = "/* ---- viz domain tokens (derived) ---- */"
KIT_ON = "--kit-on-"
FILLS = ("--success", "--info", "--warning", "--danger", "--muted", "--chart-1", "--chart-2", "--chart-3")

EXPECTED = {
    # status and pain: core state roles
    "--kit-status-shipped": "--success",
    "--kit-status-planned": "--info",
    "--kit-status-backlog": "--muted",
    "--kit-pain-critical": "--danger",
    "--kit-pain-high": "--warning",
    "--kit-pain-medium": "--info",
    "--kit-pain-low": "--muted",
    # ordered scales: --chart-1 to --chart-3, darkest first
    "--kit-differentiator": "--chart-1",
    "--kit-necessary": "--chart-2",
    "--kit-commodity": "--chart-3",
    "--kit-conf-validated": "--chart-1",
    "--kit-conf-tested": "--chart-2",
    "--kit-conf-assumed": "--chart-3",
}

# Class modifier -> the --kit-* property that paints it, per view.
PAINTS = {
    "capability-map": {"cap-imp--differentiator": "--kit-differentiator", "cap-imp--necessary": "--kit-necessary",
                       "cap-imp--commodity": "--kit-commodity"},
    "fbs": {"st--shipped": "--kit-status-shipped", "st--planned": "--kit-status-planned",
            "st--backlog": "--kit-status-backlog"},
    "delivery-roadmap": {"epic--critical": "--kit-pain-critical", "epic--high": "--kit-pain-high",
                         "epic--medium": "--kit-pain-medium", "epic--low": "--kit-pain-low",
                         "st--shipped": "--kit-status-shipped"},
    "bmc": {"bmc-conf--validated": "--kit-conf-validated", "bmc-conf--tested": "--kit-conf-tested",
            "bmc-conf--assumed": "--kit-conf-assumed"},
    "service-blueprint": {"sb-ph--critical": "--kit-pain-critical", "sb-ph--high": "--kit-pain-high",
                          "sb-ph--medium": "--kit-pain-medium", "sb-ph--low": "--kit-pain-low"},
}

DECLARATION = re.compile(r"(--[\w-]+)\s*:\s*([^;{}]+?)\s*;")
VAR = re.compile(r"var\(\s*(--[\w-]+)\s*\)")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
PROPERTY = re.compile(r"(?<![\w-])--[a-zA-Z][\w-]*")  # not a comment rule such as # -----


def declarations(css):
    return {name: value for name, value in DECLARATION.findall(css)}


class DomainTokensTest(unittest.TestCase):
    def test_domain_tokens_are_kit_properties_on_the_q5_roles(self):
        decls = declarations(DOMAIN.read_text(encoding="utf-8"))
        self.assertEqual({n: VAR.fullmatch(v).group(1) if VAR.fullmatch(v) else v for n, v in decls.items()},
                         EXPECTED)

    def test_templates_have_no_var_fallback(self):
        for path in (DOMAIN, TEMPLATE):
            with self.subTest(file=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(check_render.strip_fallbacks(text), text, "a var() fallback is left")

    def test_viz_sources_use_only_roles_and_kit_properties(self):
        for path in (DOMAIN, TEMPLATE, RENDERERS):
            with self.subTest(file=path.name):
                text = check_render.clean(path.read_text(encoding="utf-8"))
                stray = {p for p in PROPERTY.findall(text) if p not in ROLES and not p.startswith("--kit-")}
                self.assertEqual(stray, set())


def source_args(kind):
    if kind == "service-blueprint":
        return ("--proc", SB / "process-slot-rebooking.md", "--value-stream", SB / "value-stream.md",
                "--personas", SB / "personas.md")
    return (EXAMPLES / f"{kind}.sample.md",)


def split(html):
    """(the design layer render.py marked, everything the renderer wrote around it)."""
    open_tag = "<style data-design-layer>"
    start = html.index(open_tag) + len(open_tag)
    end = html.index("</style>", start)
    return html[start:end], html[:start - len(open_tag)] + html[end + len("</style>"):]


class ViewCase(RenderCase):
    """Renders an example view into the temporary folder."""

    def render(self, kind, *extra, cwd=None, env=None):
        out = f"out/{kind}.html"
        result = run(RENDER, *source_args(kind), *extra, "--out", out, cwd=cwd or self.tmp, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return ((cwd or self.tmp) / out).read_text(encoding="utf-8")

    split = staticmethod(split)


class RenderedViewsTest(ViewCase):
    """The views as render.py writes them on the base theme."""

    def test_every_colour_traces_to_a_role_through_one_kit_property(self):
        for kind, paints in PAINTS.items():
            with self.subTest(kind=kind):
                html = self.render(kind)
                design, rest = self.split(html)
                defined = set(declarations(design))
                kits = declarations(rest)
                for name, role in EXPECTED.items():
                    self.assertEqual(kits.get(name), f"var({role})", name)
                    self.assertIn(role, defined, f"{name} reads {role}, which the inlined design does not define")
                # every colour-bearing declaration reads a role, or a kit property that reads a role directly
                for prop, value in check_render.DECL.findall(check_render.clean(rest)):
                    if prop.startswith("--") or not check_render.COLOUR_PROP.search(prop):
                        continue
                    for used in VAR.findall(value):
                        if used.startswith(KIT_ON):
                            # text on a fill: declared in the design layer, reading the text role that passes
                            self.assertIn(VAR.fullmatch(declarations(design).get(used, "")).group(1),
                                          ("--accent-ink", "--ink"), f"{prop}: {value}")
                        elif used.startswith("--kit-"):
                            self.assertIn(used, EXPECTED, f"{prop}: {value}")
                        else:
                            self.assertIn(used, ROLES, f"{prop}: {value}")
                    self.assertIsNone(check_render.LITERAL.search(value), f"literal colour in {prop}: {value}")
                for cls, kit in paints.items():
                    self.assertRegex(rest, re.escape(cls) + r"\s*\{[^}]*var\(" + re.escape(kit) + r"\)", cls)

    def test_views_pass_the_validator_on_the_base_theme(self):
        base = design_source.resolve(self.tmp)
        for kind in PAINTS:
            with self.subTest(kind=kind):
                report = check_render.check(self.render(kind), base)
                self.assertEqual(report["findings"], [])

    def test_text_on_every_filled_badge_is_the_role_the_resolver_picked(self):
        # owner 2026-10-14: text on every fill is a contract pair; a list pair's text reads --kit-on-<fill>
        allowed = {}
        for pair in design_source._contract()["pairs"]:
            fg = {KIT_ON + pair["bg"][2:]} if isinstance(pair["fg"], list) else {pair["fg"]}
            allowed.setdefault(pair["bg"], set()).update(fg)
        fills = {bg for bg in allowed if bg in FILLS or bg == "--accent"}
        checked = set()
        for kind in PAINTS:
            with self.subTest(kind=kind):
                _, rest = self.split(self.render(kind))
                rules = [(sel.strip(), dict((p, v.strip()) for p, v in check_render.DECL.findall(body)))
                         for sel, body in RULE.findall(check_render.clean(rest))]
                by_selector = {sel: decls for sel, decls in rules}
                for sel, decls in rules:
                    used = VAR.fullmatch(decls.get("background", ""))
                    if not used:
                        continue
                    fill = EXPECTED.get(used.group(1), used.group(1))
                    if fill not in fills:
                        continue
                    block = re.sub(r"--[\w-]+$", "", sel.split(".")[1]) if sel.startswith(".") else sel
                    colour = decls.get("color") or by_selector.get("." + block, {}).get("color")
                    if colour is None:
                        continue   # a fill with no text (status dots)
                    checked.add(sel)
                    self.assertIn(VAR.fullmatch(colour).group(1), allowed[fill], f"{sel}: {colour} on {fill}")
        self.assertLessEqual({".cap-imp--differentiator", ".cap-imp--necessary", ".cap-imp--commodity",
                              ".bmc-conf--validated", ".bmc-conf--tested", ".bmc-conf--assumed",
                              ".epic-chip.st--shipped", ".epic-chip.st--planned", ".epic-chip.st--backlog",
                              ".sb-badge--warn", ".sb-badge--fail"}, checked)

    def test_design_layer_declares_the_text_role_for_every_fill(self):
        # the base theme: --ink where its fill is light, --accent-ink where it is dark
        design, _ = self.split(self.render("delivery-roadmap"))
        decls = declarations(design)
        self.assertEqual({fill: VAR.fullmatch(decls[KIT_ON + fill[2:]]).group(1) for fill in FILLS}, {
            "--success": "--ink", "--info": "--accent-ink", "--warning": "--ink", "--danger": "--accent-ink",
            "--muted": "--accent-ink", "--chart-1": "--accent-ink", "--chart-2": "--accent-ink", "--chart-3": "--ink"})

    def test_dark_state_fills_meant_for_white_text_get_white_badge_text(self):
        # a design-system folder (subset fixture copied) whose state fills are dark, meant for white text
        dark = self.tmp / "dark-fills"
        shutil.copytree(DESIGNS / "subset", dark)
        core = dark / "css" / "core.css"
        text = core.read_text(encoding="utf-8")
        for role, value in (("--ink", "#1a1a1a"), ("--accent-ink", "#ffffff"), ("--success", "#2e7d32"),
                            ("--warning", "#a06400"), ("--danger", "#d8232a"), ("--info", "#1565c0"),
                            ("--muted", "#555555")):
            text = re.sub(re.escape(role) + r":\s*#[0-9a-fA-F]+", f"{role}: {value}", text)
        core.write_text(text, encoding="utf-8")
        design, rest = self.split(self.render("delivery-roadmap", "--design-system", dark))
        decls = declarations(design)
        for fill in ("--success", "--info", "--warning", "--danger", "--muted"):
            self.assertEqual(decls[KIT_ON + fill[2:]], "var(--accent-ink)", fill)
        self.assertRegex(rest, r"\.epic-chip\.st--shipped\s*\{[^}]*color:\s*var\(--kit-on-success\)")


class ResolvedViewsTest(ViewCase):
    """Increment 08: every view resolves its design (folder, pin or base) and passes the validator."""

    DESIGN_ARGS = {"full": ("--design-system", DESIGNS / "full"),
                   "subset": ("--design-system", DESIGNS / "subset"), "base": ()}

    def refused(self, *extra, cwd=None, code=2):
        out = (cwd or self.tmp) / "out/roadmap.html"
        result = run(RENDER, *source_args("delivery-roadmap"), *extra, "--out", out, cwd=cwd or self.tmp)
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(out.exists(), "a refused render wrote its output")
        self.assertFalse(out.with_name(out.name + ".provenance.json").exists())
        return result.stderr

    def test_every_kind_renders_and_passes_on_full_subset_and_base(self):
        for name, extra in self.DESIGN_ARGS.items():
            design = design_source.resolve(self.tmp, explicit=DESIGNS / name if extra else None)
            for kind in PAINTS:
                with self.subTest(design=name, kind=kind):
                    html = self.render(kind, *extra)
                    self.assertIn("<style data-design-layer>", html)
                    self.assertEqual(check_render.check(html, design)["findings"], [])
                    prov = json.loads((self.tmp / f"out/{kind}.html.provenance.json").read_text(encoding="utf-8"))
                    self.assertEqual(prov["designSystem"]["source"], "path" if extra else "base")
                    self.assertEqual(prov["modules"]["dataviz"], "design-system" if extra else "base")

    def test_full_embeds_the_package_fonts(self):
        design, _ = self.split(self.render("capability-map", *self.DESIGN_ARGS["full"]))
        self.assertIn('font-family: "Acme Sans"', design)
        self.assertIn("data:font/woff2;base64,", design)
        base, _ = self.split(self.render("capability-map"))
        self.assertNotIn("@font-face", base)

    def test_full_importance_and_confidence_read_chart_1_to_3_in_order(self):
        full = design_source.role_values((DESIGNS / "full/css/dataviz.css").read_text(encoding="utf-8"))
        for kind, prefix in (("capability-map", ("differentiator", "necessary", "commodity")),
                             ("bmc", ("conf-validated", "conf-tested", "conf-assumed"))):
            with self.subTest(kind=kind):
                design, rest = self.split(self.render(kind, *self.DESIGN_ARGS["full"]))
                values, kits = design_source.role_values(design), declarations(rest)
                for step, name in enumerate(prefix, start=1):
                    self.assertEqual(kits["--kit-" + name], f"var(--chart-{step})")
                    self.assertEqual(values[f"--chart-{step}"], full[f"--chart-{step}"])

    def test_inlines_only_the_modules_the_views_use(self):
        # owner 2026-10-14: core and dataviz (and the font faces), never the slide frame or other modules
        design, _ = self.split(self.render("fbs", *self.DESIGN_ARGS["full"]))
        defined = set(declarations(design))
        modules = design_source._contract()["modules"]
        for module in ("core", "dataviz"):
            self.assertLessEqual(set(modules[module]["roles"]), defined, module)
        for module in ("type", "space-shape", "document", "slide-frame", "print", "brand"):
            self.assertEqual(set(modules[module]["roles"]) & defined, set(), module)

    def test_finds_the_project_pin_from_a_subfolder(self):
        shutil.copytree(DESIGNS / "subset", self.tmp / "design-system")
        (self.tmp / "docs/ux").mkdir(parents=True)
        (self.tmp / "docs/ux/package.json").write_text(json.dumps(
            {"dependencies": {"@acme-test/design-subset": "file:../../design-system"}}), encoding="utf-8")
        sub = self.tmp / "docs/product/views"
        sub.mkdir(parents=True)
        design, _ = self.split(self.render("fbs", cwd=sub))
        self.assertIn("#7a3ea8", design)   # the subset accent
        prov = json.loads((sub / "out/fbs.html.provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(prov["designSystem"]["name"], "@acme-test/design-subset")

    def test_legacy_token_file_in_the_project_is_refused(self):
        (self.tmp / "docs/ux").mkdir(parents=True)
        (self.tmp / "docs/ux/tokens.css").write_text(":root { --accent: #123456; }\n", encoding="utf-8")
        sub = self.tmp / "sub"
        sub.mkdir()
        stderr = self.refused(cwd=sub)
        self.assertIn("ux-design-system subset --from-legacy", stderr)

    def test_a_plain_stylesheet_is_refused_with_the_migration_message(self):
        sheet = self.tmp / "styles.css"
        sheet.write_text(":root { --accent: #123456; }\n", encoding="utf-8")
        stderr = self.refused("--design-system", sheet)
        self.assertIn("kit-manifest.json", stderr)
        self.assertIn("ux-design-system point", stderr)

    def test_missing_design_system_path_is_a_clear_error(self):
        stderr = self.refused("--design-system", self.tmp / "nowhere")
        self.assertIn("does not exist", stderr)

    def test_a_render_that_breaks_the_design_writes_nothing(self):
        # --muted on --surface at 1.16:1: the validator refuses the declared exception
        stderr = self.refused("--exception=--muted=#eeeeee", code=1)   # the = form: the value starts with --
        self.assertIn("contrast", stderr)

    def test_declared_exception_passes_and_is_reported(self):
        self.render("fbs", "--exception", "mine=#123456")
        prov = json.loads((self.tmp / "out/fbs.html.provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(prov["exceptions"], ["mine"])

    def test_out_with_a_bare_file_name(self):
        result = run(RENDER, *source_args("delivery-roadmap"), "--out", "roadmap.html", cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.tmp / "roadmap.html").is_file())
        self.assertTrue((self.tmp / "roadmap.html.provenance.json").is_file())


class FooterDateTest(RenderCase):
    """The footer date comes from the shared date source, never today's date."""

    def render_copy(self, env, prepare=None):
        project = self.tmp / "project"
        project.mkdir()
        source = project / "fbs.sample.md"
        shutil.copyfile(EXAMPLES / "fbs.sample.md", source)
        if prepare:
            prepare(project, source)
        result = run(RENDER, source, "--out", "out/fbs.html", cwd=project,
                     env={"SOURCE_DATE_EPOCH": None, "GIT_CEILING_DIRECTORIES": str(self.tmp), **env})
        self.assertEqual(result.returncode, 0, result.stderr)
        _, rest = split((project / "out/fbs.html").read_text(encoding="utf-8"))
        return re.search(r'<footer class="viz-footer">.* on (\d{4}-\d{2}-\d{2})\.', rest).group(1)

    def test_source_date_epoch_wins(self):
        self.assertEqual(self.render_copy({"SOURCE_DATE_EPOCH": "31536000"}), "1971-01-01")

    def test_last_commit_date_of_the_source_folder(self):
        def commit(project, source):
            git = ["git", "-C", str(project), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
            env = {**os.environ, "GIT_COMMITTER_DATE": "2001-02-03T12:00:00Z", "GIT_AUTHOR_DATE": "2001-02-03T12:00:00Z"}
            for args in (["init", "-q"], ["add", "fbs.sample.md"], ["commit", "-q", "-m", "source"]):
                subprocess.run(git + args, check=True, env=env, capture_output=True)
        self.assertEqual(self.render_copy({}, commit), "2001-02-03")

    def test_newest_source_mtime_outside_git(self):
        def touch(project, source):
            stamp = datetime.datetime(2003, 4, 5, 12, tzinfo=datetime.timezone.utc).timestamp()
            os.utime(source, (stamp, stamp))
        self.assertEqual(self.render_copy({}, touch), "2003-04-05")

if __name__ == "__main__":
    unittest.main()
