"""com-artefact-viz domain colours on contract roles (Plan-0005 increment 07).

Owner ruling Q-5: status and pain keep the core state roles; importance and
confidence are ordered scales on --chart-1 to --chart-3, darkest first. Every
colour a view draws traces to a contract role through one --kit-* property.
"""
import re
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
ROLES = {role for module in design_source._contract()["modules"].values() for role in module["roles"]}
DOMAIN_MARKER = "/* ---- viz domain tokens (derived) ---- */"

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


class RenderedViewsTest(RenderCase):
    """The views as render.py writes them today (base theme; the resolver arrives in Increment 08)."""

    def render(self, kind):
        out = f"out/{kind}.html"
        if kind == "service-blueprint":
            sb = EXAMPLES / "service-blueprint"
            result = run(RENDER, "--proc", sb / "process-slot-rebooking.md", "--value-stream", sb / "value-stream.md",
                         "--personas", sb / "personas.md", "--out", out, cwd=self.tmp)
        else:
            result = run(RENDER, EXAMPLES / f"{kind}.sample.md", "--out", out, cwd=self.tmp)
        self.assertEqual(result.returncode, 0, result.stderr)
        return (self.tmp / out).read_text(encoding="utf-8")

    @staticmethod
    def split(html):
        """(inlined design CSS, everything the renderer wrote around it)."""
        start = html.index("<style>") + len("<style>")
        end = html.index(DOMAIN_MARKER)
        return html[start:end], html[:start] + html[end:]

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
                        if used.startswith("--kit-"):
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
                html = self.render(kind)
                design, rest = self.split(html)
                # Increment 08 makes render.py mark the design layer; here the test marks it.
                marked = rest.replace("<style>", f"<style data-design-layer>{design}</style>\n<style>", 1)
                report = check_render.check(marked, base)
                self.assertEqual(report["findings"], [])

    def test_text_on_every_filled_badge_is_the_role_its_pair_names(self):
        # owner 2026-10-14: text on every fill is a contract pair (modules.json "pairs")
        pairs = design_source._contract()["pairs"]
        allowed = {}
        for pair in pairs:
            allowed.setdefault(pair["bg"], set()).add(pair["fg"])
        fills = {bg for bg in allowed if bg.startswith(("--chart-", "--success", "--info", "--warning", "--danger",
                                                        "--muted", "--accent"))}
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

if __name__ == "__main__":
    unittest.main()
