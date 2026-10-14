"""Shared design resolver (Plan-0005 increment 03): pin, legacy refusal, registry, cache, exports, contrast."""
import base64
import hashlib
import http.server
import io
import json
import os
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


class AssemblyTest(ResolverCase):
    def test_package_modules_come_after_base_so_the_package_wins(self):
        design = design_source.resolve(self.project, explicit=FIXTURES / "full")
        css = design.css["core"]
        self.assertLess(css.index("#3b6ef5"), css.index("#0e7090"))  # base accent, then the package accent

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
        self.assertIn("#3b6ef5", proc.stdout)


if __name__ == "__main__":
    unittest.main()
