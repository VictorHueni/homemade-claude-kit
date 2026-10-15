"""Shared design resolver (Plan-0005 increment 03): pin, legacy refusal, registry, cache, exports, contrast."""
import base64
import hashlib
import http.server
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
SHARED = PLUGIN / "shared"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "design-systems"
sys.path.insert(0, str(SHARED))

import design_source  # noqa: E402  (fails red until the resolver exists)


def tarball(folder, extra=None, prefix="package/"):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for path in sorted(Path(folder).rglob("*")):
            if path.is_file():
                tf.add(path, prefix + path.relative_to(folder).as_posix())
        for name, data in (extra or {}).items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def integrity(data):
    return "sha512-" + base64.b64encode(hashlib.sha512(data).digest()).decode()


class Registry:
    """Local npm registry stub: serves <name>/<version> metadata and the tarball, counting requests."""

    def __init__(self):
        self.packages, self.requests = {}, []
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                outer.requests.append(self.path)
                if self.path.startswith("/tarballs/"):
                    body = outer.packages[self.path[len("/tarballs/"):]]["data"]
                else:
                    key = self.path.lstrip("/")
                    entry = outer.packages.get(key)
                    if entry is None:
                        self.send_error(404)
                        return
                    body = json.dumps({"dist": {"tarball": outer.url + "/tarballs/" + key,
                                                "integrity": entry["integrity"]}}).encode()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)

        self.server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def add(self, name, version, data, claimed=None):
        self.packages[f"{name}/{version}"] = {"data": data, "integrity": claimed or integrity(data)}

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class ResolverCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.cache = self.tmp / "cache"
        self.project = self.tmp / "project"
        (self.project / "docs" / "ux").mkdir(parents=True)
        self.registry = Registry()
        self.addCleanup(self.registry.close)
        saved = {k: os.environ.get(k) for k in ("XDG_CACHE_HOME", "DELIVERY_COMMS_NPM_REGISTRY")}
        os.environ["XDG_CACHE_HOME"] = str(self.cache)
        os.environ["DELIVERY_COMMS_NPM_REGISTRY"] = self.registry.url
        self.addCleanup(lambda: [os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
                                 for k, v in saved.items()])

    def pin(self, spec, name="@acme-test/design-system", where=None):
        folder = where or self.project / "docs" / "ux"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "package.json").write_text(json.dumps({"dependencies": {name: spec}}), encoding="utf-8")

    def publish(self, fixture="full", version="1.0.0", **kw):
        data = tarball(FIXTURES / fixture, **kw)
        self.registry.add(json.loads((FIXTURES / fixture / "package.json").read_text())["name"], version, data)
        return data

    def cache_dirs(self):
        return list(self.cache.rglob("package.tgz"))


class ResolutionOrderTest(ResolverCase):
    def test_explicit_path_wins_over_pin(self):
        self.pin("9.9.9")
        design = design_source.resolve(self.project, explicit=FIXTURES / "full")
        self.assertEqual(design.provenance["designSystem"]["source"], "path")
        self.assertEqual(self.registry.requests, [])

    def test_pin_found_walking_up(self):
        self.publish()
        self.pin("1.0.0")
        deep = self.project / "docs" / "decks" / "q1"
        deep.mkdir(parents=True)
        design = design_source.resolve(deep)
        self.assertEqual(design.provenance["designSystem"]["version"], "1.0.0")

    def test_walk_stops_after_eight_levels(self):
        self.pin("1.0.0")
        deep = self.project
        for i in range(9):
            deep = deep / f"d{i}"
        deep.mkdir(parents=True)
        design = design_source.resolve(deep)
        self.assertEqual(design.provenance["designSystem"]["source"], "base")

    def test_no_design_source_is_the_base_theme(self):
        design = design_source.resolve(self.project)
        prov = design.provenance
        self.assertEqual(prov["designSystem"]["source"], "base")
        self.assertTrue(all(src == "base" for src in prov["modules"].values()))
        self.assertEqual(len(prov["modules"]), 9)

    def test_local_folder_pin_needs_no_network(self):
        shutil.copytree(FIXTURES / "full", self.tmp / "design-system")
        self.pin("file:../../../design-system")
        design = design_source.resolve(self.project)
        self.assertEqual(design.provenance["designSystem"]["source"], "path")
        self.assertEqual(self.registry.requests, [])

    def test_inexact_version_is_refused(self):
        self.pin("^1.0.0")
        with self.assertRaises(design_source.DesignError) as cm:
            design_source.resolve(self.project)
        self.assertIn("exact", str(cm.exception))


class LegacyTest(ResolverCase):
    def test_legacy_tokens_are_refused_with_the_three_commands(self):
        for legacy in ("docs/ux/tokens.css", "docs/design/tokens.css"):
            with self.subTest(legacy=legacy):
                path = self.project / legacy
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(":root{--ink:#000}", encoding="utf-8")
                with self.assertRaises(design_source.DesignError) as cm:
                    design_source.resolve(self.project)
                self.assertEqual(cm.exception.code, 2)
                for word in ("point", "subset", "subset --from-legacy"):
                    self.assertIn(word, str(cm.exception))
                path.unlink()

    def test_cli_exit_code_is_2(self):
        (self.project / "docs/ux/tokens.css").write_text(":root{}", encoding="utf-8")
        proc = subprocess.run([sys.executable, "-I", str(SHARED / "design_source.py"), "css", "--from", str(self.project)],
                              capture_output=True, text=True, env={**os.environ})
        self.assertEqual(proc.returncode, 2)
        self.assertIn("subset --from-legacy", proc.stderr)

    def test_pin_beats_legacy_with_a_warning(self):
        self.publish()
        self.pin("1.0.0")
        (self.project / "docs/ux/tokens.css").write_text(":root{}", encoding="utf-8")
        design = design_source.resolve(self.project)
        self.assertEqual(design.provenance["designSystem"]["source"], "registry")
        self.assertTrue(any("tokens.css" in w and "delete" in w for w in design.provenance["warnings"]))


class RegistryTest(ResolverCase):
    def test_fetch_extract_and_cache(self):
        self.publish()
        self.pin("1.0.0")
        design_source.resolve(self.project)
        first = list(self.registry.requests)
        self.assertEqual(len(first), 2)
        self.assertTrue(first[0].startswith("/@acme-test/design-system/1.0.0"))
        self.assertEqual(len(self.cache_dirs()), 1)

    def test_second_resolve_makes_no_request(self):
        self.publish()
        self.pin("1.0.0")
        design_source.resolve(self.project)
        before = len(self.registry.requests)
        design_source.resolve(self.project)
        self.assertEqual(len(self.registry.requests), before)

    def test_kept_tarball_is_rechecked_on_a_cache_hit(self):
        self.publish()
        self.pin("1.0.0")
        design_source.resolve(self.project)
        kept = next(self.cache.rglob("*.tgz"))
        kept.write_bytes(kept.read_bytes() + b"tamper")
        with self.assertRaises(design_source.DesignError) as cm:
            design_source.resolve(self.project)
        self.assertIn("integrity", str(cm.exception))

    def test_tampered_tarball_is_refused_and_nothing_is_cached(self):
        data = tarball(FIXTURES / "full")
        self.registry.add("@acme-test/design-system", "1.0.0", data, claimed=integrity(data + b"x"))
        self.pin("1.0.0")
        with self.assertRaises(design_source.DesignError) as cm:
            design_source.resolve(self.project)
        self.assertIn("integrity", str(cm.exception))
        self.assertEqual(self.cache_dirs(), [])

    def test_path_traversal_member_is_refused(self):
        self.publish(extra={"../evil.txt": b"x"})
        self.pin("1.0.0")
        with self.assertRaises(design_source.DesignError):
            design_source.resolve(self.project)
        self.assertFalse((self.cache / "delivery-comms" / "evil.txt").exists())
        self.assertEqual(self.cache_dirs(), [])

    def test_unknown_version_is_refused(self):
        self.pin("3.0.0")
        with self.assertRaises(design_source.DesignError) as cm:
            design_source.resolve(self.project)
        self.assertIn("3.0.0", str(cm.exception))

    def test_no_temporary_folder_is_left_after_a_failure(self):
        data = tarball(FIXTURES / "full")
        self.registry.add("@acme-test/design-system", "1.0.0", data, claimed=integrity(b"other"))
        self.pin("1.0.0")
        with self.assertRaises(design_source.DesignError):
            design_source.resolve(self.project)
        root = self.cache / "delivery-comms" / "design-systems"
        self.assertEqual([p for p in root.rglob("*") if "tmp" in p.name.lower()] if root.exists() else [], [])


class ManifestTest(ResolverCase):
    def resolve_copy(self, fixture, mutate):
        folder = self.tmp / "ds"
        shutil.copytree(FIXTURES / fixture, folder)
        mutate(folder)
        return lambda: design_source.resolve(self.project, explicit=folder)

    def test_manifest_the_checker_refuses(self):
        def mutate(folder):
            path = folder / "kit-manifest.json"
            data = json.loads(path.read_text())
            data["contractVersion"] = "two"
            path.write_text(json.dumps(data))
        with self.assertRaises(design_source.DesignError) as cm:
            self.resolve_copy("full", mutate)()
        self.assertIn("contractVersion", str(cm.exception))

    def test_an_export_that_names_a_folder_is_refused_as_a_folder(self):
        # the contract wants one file per module, guidance included (#145)
        def mutate(folder):
            path = folder / "kit-manifest.json"
            data = json.loads(path.read_text())
            data["provides"]["guidance"] = "./guidance/"
            path.write_text(json.dumps(data))
        with self.assertRaises(design_source.DesignError) as cm:
            self.resolve_copy("full", mutate)()
        self.assertIn("is a folder", str(cm.exception))
        self.assertIn("one file", str(cm.exception))

    def test_missing_dataviz_names_the_module(self):
        with self.assertRaises(design_source.DesignError) as cm:
            design_source.resolve(self.project, explicit=FIXTURES / "minimal-invalid")
        self.assertIn("dataviz", str(cm.exception))

    def test_missing_manifest_is_refused(self):
        with self.assertRaises(design_source.DesignError) as cm:
            self.resolve_copy("full", lambda f: (f / "kit-manifest.json").unlink())()
        self.assertIn("kit-manifest.json", str(cm.exception))

    def test_exports_resolve_exact_and_wildcard(self):
        design = design_source.resolve(self.project, explicit=FIXTURES / "full")
        self.assertEqual(design.provenance["modules"]["core"], "design-system")  # exact ./core.css
        self.assertEqual(design.provenance["modules"]["type"], "design-system")  # wildcard ./css/*
        self.assertIn("--font-size-xs", design.css["type"])

    def test_module_path_outside_exports_is_refused(self):
        def mutate(folder):
            path = folder / "kit-manifest.json"
            data = json.loads(path.read_text())
            data["provides"]["type"] = "./internal/type.css"
            path.write_text(json.dumps(data))
        with self.assertRaises(design_source.DesignError) as cm:
            self.resolve_copy("full", mutate)()
        self.assertIn("exports", str(cm.exception))

    def test_failing_contrast_pair_is_refused_at_resolve_time(self):
        def mutate(folder):
            css = folder / "css" / "core.css"
            css.write_text(css.read_text().replace("--muted: #475467", "--muted: #d0d5dd"))
            data = json.loads((folder / "kit-manifest.json").read_text())
        with self.assertRaises(design_source.DesignError) as cm:
            self.resolve_copy("full", mutate)()
        message = str(cm.exception)
        self.assertIn("--muted", message)
        self.assertIn("--surface", message)
        self.assertRegex(message, r"\d+\.\d+")

    def test_fill_that_no_text_role_passes_is_refused_at_resolve_time(self):
        # a mid grey: white and --ink both fall below AA on it, so neither role can carry text
        for role in ("--success", "--chart-2"):
            with self.subTest(fill=role):
                def mutate(folder, role=role):
                    for css in (folder / "css").glob("*.css"):
                        css.write_text(re.sub(re.escape(role) + r":\s*#[0-9a-fA-F]+", f"{role}: #777777", css.read_text()))
                shutil.rmtree(self.tmp / "ds", ignore_errors=True)
                with self.assertRaises(design_source.DesignError) as cm:
                    self.resolve_copy("full", mutate)()
                line = next(l for l in str(cm.exception).splitlines() if f"on {role}" in l)
                self.assertRegex(line, r"--accent-ink \(contrast \d+\.\d+\)")
                self.assertRegex(line, r"--ink \(contrast \d+\.\d+\)")

    def test_base_theme_passes_its_own_pairs(self):
        contract = design_source._contract()
        css = "".join(design_source._base_css(module) for module in contract["modules"])
        self.assertEqual(design_source.failing_pairs(css, contract["pairs"]), [])


KIT_ON = re.compile(r"(--kit-on-[\w-]+)\s*:\s*var\((--[\w-]+)\)")
STATE_FILLS = ("success", "info", "warning", "danger", "muted")
CHART_FILLS = ("chart-1", "chart-2", "chart-3")


class FillTextTest(ResolverCase):
    """List pairs: text on a fill takes whichever text role reaches AA; the resolver writes --kit-on-<fill>."""
    resolve_copy = ManifestTest.resolve_copy

    def choices(self, design):
        """{fill: (module that declares --kit-on-<fill>, the role it reads)}."""
        found = {}
        for module, css in design.css.items():
            for prop, role in KIT_ON.findall(css):
                self.assertNotIn(prop, found, f"{prop} declared twice")
                found[prop[len("--kit-on-"):]] = (module, role)
        return found

    def test_dark_state_fills_meant_for_white_text(self):
        values = {"--ink": "#1a1a1a", "--accent-ink": "#ffffff", "--success": "#2e7d32", "--warning": "#a06400",
                  "--danger": "#d8232a", "--info": "#1565c0", "--muted": "#555555"}

        def mutate(folder):
            core = folder / "css" / "core.css"
            text = core.read_text()
            for role, value in values.items():
                text = re.sub(re.escape(role) + r":\s*#[0-9a-fA-F]+", f"{role}: {value}", text)
            core.write_text(text)
        design = self.resolve_copy("subset", mutate)()
        choices = self.choices(design)
        for fill in STATE_FILLS:
            self.assertEqual(choices[fill], ("core", "--accent-ink"), fill)
        self.assertEqual({f: choices[f] for f in CHART_FILLS},
                         {"chart-1": ("dataviz", "--accent-ink"), "chart-2": ("dataviz", "--accent-ink"),
                          "chart-3": ("dataviz", "--ink")})

    def test_base_theme_picks_the_role_that_passes_on_each_fill(self):
        choices = self.choices(design_source.resolve(self.project))
        self.assertEqual(choices, {
            "success": ("core", "--ink"),          # white 3.41, ink 4.84
            "info": ("core", "--accent-ink"),      # white 4.53
            "warning": ("core", "--ink"),          # white 1.95, ink 8.49
            "danger": ("core", "--accent-ink"),    # white 4.51
            "muted": ("core", "--accent-ink"),     # white 4.83
            "chart-1": ("dataviz", "--accent-ink"),
            "chart-2": ("dataviz", "--accent-ink"),
            "chart-3": ("dataviz", "--ink"),       # white 2.52, ink 6.56
        })

    def test_fixtures_with_dark_state_fills_take_white_text(self):
        for fixture in ("full", "subset"):
            with self.subTest(fixture=fixture):
                choices = self.choices(design_source.resolve(self.project, explicit=FIXTURES / fixture))
                self.assertEqual({f: role for f, (_, role) in choices.items()},
                                 {**{f: "--accent-ink" for f in STATE_FILLS},
                                  "chart-1": "--accent-ink", "chart-2": "--accent-ink", "chart-3": "--ink"})

    def test_a_fill_that_is_not_a_hex_colour_takes_the_first_role(self):
        # contrast cannot be computed on var(--info), so --chart-3 takes the first role of its list
        def mutate(folder):
            viz = folder / "css" / "dataviz.css"
            viz.write_text(re.sub(r"--chart-3:\s*#[0-9a-fA-F]+", "--chart-3: var(--info)", viz.read_text()))
        choices = self.choices(self.resolve_copy("subset", mutate)())
        self.assertEqual(choices["chart-3"], ("dataviz", "--accent-ink"))

    def test_css_command_prints_the_fill_text_properties(self):
        proc = subprocess.run([sys.executable, "-I", str(SHARED / "design_source.py"), "css", "--module", "core",
                               "--design-system", str(FIXTURES / "full")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--kit-on-success: var(--accent-ink)", proc.stdout)
        self.assertNotIn("--kit-on-chart-1", proc.stdout)


class AssemblyTest(ResolverCase):
    def test_package_modules_come_after_base_so_the_package_wins(self):
        design = design_source.resolve(self.project, explicit=FIXTURES / "full")
        css = design.css["core"]
        self.assertLess(css.index("#396cf5"), css.index("#0e7090"))  # base accent, then the package accent

    def test_subset_takes_omitted_modules_from_the_base(self):
        design = design_source.resolve(self.project, explicit=FIXTURES / "subset")
        mods = design.provenance["modules"]
        self.assertEqual(mods["core"], "design-system")
        self.assertEqual(mods["dataviz"], "design-system")
        for name in ("type", "brand", "print", "document", "slide-frame", "space-shape", "guidance"):
            self.assertEqual(mods[name], "base")
        self.assertIn("--font-size-md", design.css["type"])

    def test_provenance_marks_guidance_informational(self):
        design = design_source.resolve(self.project, explicit=FIXTURES / "full")
        guidance = design.provenance["guidance"]
        self.assertTrue(guidance["informational"])
        self.assertEqual(guidance["export"], "./guidance/README.md")

    def test_brand_roles_and_exceptions_are_exposed(self):
        design = design_source.resolve(self.project, explicit=FIXTURES / "full")
        self.assertEqual(set(design.brand), {"--brand-logo-on-light", "--brand-logo-on-dark", "--brand-mark", "--brand-legal"})
        self.assertIn("data:image/svg+xml;base64,", design.brand["--brand-mark"])
        self.assertEqual(design.exceptions, {})

    def test_fonts_are_inlined_as_data_uris(self):
        design = design_source.resolve(self.project, explicit=FIXTURES / "full")
        expected = base64.b64encode(b"wOF2-fake-font-bytes").decode()
        self.assertEqual(len(design.fonts), 1)
        self.assertIn("data:font/woff2;base64," + expected, design.fonts[0])
        self.assertNotIn("../fonts/acme.woff2", design.fonts[0])
        self.assertNotIn("@font-face", design.css["type"])


class CliTest(ResolverCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(SHARED / "design_source.py"), *map(str, args)],
                              capture_output=True, text=True, env={**os.environ})

    def test_css_prints_requested_modules_in_order(self):
        for fixture in ("full", "subset"):
            with self.subTest(fixture=fixture):
                proc = self.cli("css", "--module", "core,dataviz", "--design-system", FIXTURES / fixture)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                design = design_source.resolve(self.project, explicit=FIXTURES / fixture)
                self.assertEqual(proc.stdout, design.css["core"] + design.css["dataviz"])
                self.assertNotIn("--font-size-md", proc.stdout)

    def test_css_of_minimal_invalid_fails(self):
        proc = self.cli("css", "--design-system", FIXTURES / "minimal-invalid")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("dataviz", proc.stderr)

    def test_fonts_prints_inlined_faces(self):
        proc = self.cli("fonts", "--design-system", FIXTURES / "full")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("data:font/woff2;base64,", proc.stdout)
        self.assertEqual(self.cli("fonts", "--design-system", FIXTURES / "subset").stdout, "")

    def test_provenance_prints_json(self):
        proc = self.cli("provenance", "--design-system", FIXTURES / "full")
        self.assertEqual(json.loads(proc.stdout)["modules"]["core"], "design-system")

    def test_base_render_without_any_design(self):
        proc = self.cli("css", "--module", "core", "--from", self.project)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("#396cf5", proc.stdout)


if __name__ == "__main__":
    unittest.main()
