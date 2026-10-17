"""Skill eval suite structure (Plan-0005 increment 12; the deck-dark-palette case, Plan-0006 increment 04). Loads every case in evals/ without running a model.

The suite runs only through `make skill-evals` (`claude plugin eval`, paid). This test checks what can be checked
for free: each case folder has the files the CLI reads (prompt.md, case.yaml, graders/*.md) with the keys its
schema accepts; no grader is a tool_used or tool_order record (a denied call still counts as used), so every
grader reads a file the run leaves behind; each scaffold.sh stages its scratch project and the project resolves
to the design the case expects; nothing in the suite names a real brand; `make test` never runs the suite.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

PLUGIN = Path(__file__).resolve().parent.parent
EVALS = PLUGIN / "evals"
sys.path.insert(0, str(PLUGIN / "shared"))

import design_source  # noqa: E402

CASES = ("deck-pinned", "viz-from-subfolder", "release-note", "legacy-tokens", "bespoke-generator",
         "deck-dark-palette")
PINNED = ("deck-pinned", "viz-from-subfolder", "release-note", "bespoke-generator")
FICTITIOUS_DESIGN = "@acme-test/design-system"
FICTITIOUS_DARK_DESIGN = "@acme-test/design-system-dark"
DARK_DECK = Path("docs/communication/slides/board-update")

# Keys `claude plugin eval` accepts (2.1.300): prompt.md front matter, case.yaml, grader front matter by type.
PROMPT_KEYS = {"schema_version", "name", "description", "tags", "plugins", "runs", "expected_outcome", "model",
               "max_turns", "timeout_seconds", "allowed_tools", "disallowed_tools", "artifact_publish",
               "growthbook_overrides", "append_system_prompt", "env"}
CASE_KEYS = {"schema_version", "name", "description", "tags", "plugins", "context", "execution", "runs",
             "graders", "expected_outcome"}
CONTEXT_KEYS = {"scaffold_script", "history_file", "add_dirs"}
GRADER_KEYS = {
    "regex": {"type", "target", "pattern", "flags", "match", "weight", "arm"},
    "file_exists": {"type", "path", "exists", "weight", "arm"},
    "llm": {"type", "criteria", "focus", "weight", "arm"},
}
# Graders whose file is in the staged project before the run: they check the run left it alone.
PRESENT_BEFORE_THE_RUN = {("legacy-tokens", "tokens-untouched"),
                          ("deck-dark-palette", "section-dark-on-root"),
                          ("deck-dark-palette", "highlight-is-dark-accent"),
                          ("deck-dark-palette", "styles-no-dark-palette"),
                          ("deck-dark-palette", "config-no-dark-exception")}
# The prompt states the task; how to validate and report it is the skill's job.
SKILL_WORDS = ("check_render", "verdict", "provenance", "design_source", "--record", "subset", "kit-manifest")


def front_matter(path):
    text = path.read_text(encoding="utf-8")
    # The CLI's own rule: the front matter ends at the first `---` anywhere, not only at a line start, so a
    # pattern holding `---` (a CSS comment rule) cuts it short. Parse it the same way.
    match = re.match(r"---\s*\n([\s\S]*?)---\s*\n?", text)
    if not match:
        raise AssertionError(f"{path}: no front matter")
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise AssertionError(f"{path}: front matter does not parse the way the CLI cuts it: {exc}") from None
    return meta, text[match.end():].strip()


def graders(case):
    return {p.stem: front_matter(p) for p in sorted((EVALS / case / "graders").glob("*.md"))}


def file_target(spec):
    """The run-relative file a grader reads, or None when it reads no file."""
    if spec["type"] == "file_exists":
        return spec["path"]
    where = spec.get("target") if spec["type"] == "regex" else spec.get("focus")
    return where["path"] if isinstance(where, dict) and where.get("source") == "file" else None


def stage(case, cwd):
    """Run the case's scaffold.sh in `cwd` the way the CLI does: bash SCRIPT, a bare environment."""
    env = {"PATH": os.environ["PATH"], "HOME": str(cwd), "TERM": "dumb"}
    return subprocess.run(["bash", str(EVALS / case / "scaffold.sh")], cwd=cwd, env=env,
                          capture_output=True, text=True)


class CaseFilesTest(unittest.TestCase):
    def test_the_six_cases_and_nothing_else(self):
        found = sorted(p.name for p in EVALS.iterdir()
                       if p.is_dir() and ((p / "prompt.md").is_file() or (p / "case.yaml").is_file()))
        self.assertEqual(found, sorted(CASES))

    def test_the_manifest_points_the_cli_at_evals(self):
        manifest = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest.get("experimental", {}).get("evals"), "evals")

    def test_prompt_md(self):
        for case in CASES:
            with self.subTest(case=case):
                meta, body = front_matter(EVALS / case / "prompt.md")
                self.assertLessEqual(set(meta), PROMPT_KEYS)
                self.assertTrue(body and "TODO" not in body)
                self.assertLessEqual({"Skill", "Bash", "Write"}, set(meta["allowed_tools"]))
                for word in SKILL_WORDS:
                    self.assertNotIn(word, body, "the prompt must not hand the agent what the skill should")

    def test_case_yaml_names_the_case_and_its_scaffold(self):
        for case in CASES:
            with self.subTest(case=case):
                spec = yaml.safe_load((EVALS / case / "case.yaml").read_text(encoding="utf-8"))
                self.assertLessEqual(set(spec), CASE_KEYS)
                self.assertEqual(spec["name"], case)
                self.assertEqual(str(spec["schema_version"]).split(".")[0], "1")
                self.assertLessEqual(set(spec["context"]), CONTEXT_KEYS)
                self.assertTrue((EVALS / case / spec["context"]["scaffold_script"]).is_file())


class GraderTest(unittest.TestCase):
    def test_every_case_has_graders_of_a_file_reading_type(self):
        for case in CASES:
            with self.subTest(case=case):
                found = graders(case)
                self.assertTrue(found, "no grader")
                for name, (spec, _) in found.items():
                    self.assertIn(spec.get("type"), GRADER_KEYS, f"{name}: tool_used, tool_order and baseline "
                                  "graders do not read what the run left behind")
                    self.assertLessEqual(set(spec), GRADER_KEYS[spec["type"]], name)

    def test_every_grader_reads_a_relative_file_of_the_run(self):
        for case in CASES:
            for name, (spec, body) in graders(case).items():
                with self.subTest(case=case, grader=name):
                    target = file_target(spec)
                    self.assertIsNotNone(target, "regex target and llm focus must be {source: file, path}")
                    self.assertFalse(Path(target).is_absolute() or ".." in Path(target).parts, target)
                    if spec["type"] == "regex":
                        self.assertTrue(spec.get("pattern"))
                        self.assertRegex(spec.get("match", "contains"), r"^(?:contains|not_contains|count:\d+)$")
                        self.assertRegex(spec.get("flags", ""), r"^[dgimsuvy]*$")
                    if spec["type"] == "llm":
                        self.assertIn("PASS", body)

    def test_each_case_needs_the_run_to_produce_a_file(self):
        for case in CASES:
            with self.subTest(case=case):
                produced = [n for n, (s, _) in graders(case).items()
                            if (s["type"] == "file_exists" and s.get("exists", True))
                            or (s["type"] == "regex" and s.get("match", "contains") == "contains")]
                self.assertTrue(produced, "every grader would pass on a run that did nothing")


class ScaffoldTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def staged(self, case):
        cwd = self.tmp / case
        cwd.mkdir()
        result = stage(case, cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        return cwd

    def test_pinned_projects_resolve_to_the_fictitious_full_design(self):
        for case in PINNED:
            with self.subTest(case=case):
                design = design_source.resolve(self.staged(case))
                self.assertEqual(design.provenance["designSystem"]["name"], FICTITIOUS_DESIGN)
                modules = dict(design.provenance["modules"])
                self.assertEqual(modules.pop("dark"), "base")    # the full design has no dark module
                self.assertEqual(set(modules.values()), {"design-system"})

    def test_the_legacy_project_is_refused(self):
        cwd = self.staged("legacy-tokens")
        with self.assertRaises(design_source.DesignError) as caught:
            design_source.resolve(cwd)
        self.assertEqual(caught.exception.code, 2)
        self.assertFalse((cwd / "docs" / "ux" / "package.json").exists())

    def test_the_dark_palette_deck_resolves_to_the_dark_design_and_is_refused_as_staged(self):
        cwd = self.staged("deck-dark-palette")
        design = design_source.resolve(cwd)
        self.assertEqual(design.provenance["designSystem"]["name"], FICTITIOUS_DARK_DESIGN)
        self.assertEqual(design.provenance["modules"]["dark"], "design-system")
        styles = (cwd / DARK_DECK / "design" / "styles.css").read_text(encoding="utf-8")
        self.assertRegex(styles, r"--dark-[\w-]+\s*:", "the case starts from a deck-local dark palette")
        build = PLUGIN / "skills" / "com-slide-deck" / "scripts" / "build.py"
        result = subprocess.run([sys.executable, str(build), "--config", str(DARK_DECK / "config.yaml")],
                                cwd=cwd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("--dark-bg", result.stdout + result.stderr)

    def test_graders_read_files_the_run_writes(self):
        for case in CASES:
            cwd = self.staged(case)
            for name, (spec, _) in graders(case).items():
                with self.subTest(case=case, grader=name):
                    present = (cwd / file_target(spec)).exists()
                    self.assertEqual(present, (case, name) in PRESENT_BEFORE_THE_RUN)

    def test_the_tokens_untouched_pattern_is_the_staged_file(self):
        spec, _ = graders("legacy-tokens")["tokens-untouched"]
        staged = (self.staged("legacy-tokens") / spec["target"]["path"]).read_text(encoding="utf-8")
        pattern = spec["pattern"]
        self.assertTrue(pattern.startswith("^") and pattern.endswith("$"))
        self.assertIsNotNone(re.fullmatch(pattern[1:-1], staged))
        self.assertIsNone(re.fullmatch(pattern[1:-1], staged.replace("#0f9d8f", "#0b7a6f")))

    def test_no_real_brand_and_no_machine_path(self):
        hosts = re.compile(r"\b((?:[a-z0-9-]+\.)+(?:com|org|net|io|ch|de|fr|co|ai|app|dev))\b", re.I)
        for path in sorted(p for p in EVALS.rglob("*") if p.is_file()):
            text = path.read_text(encoding="utf-8")
            with self.subTest(file=str(path.relative_to(EVALS))):
                self.assertEqual(set(re.findall(r"@([a-z0-9-]+)/", text)) - {"acme-test"}, set())
                self.assertEqual({h.lower() for h in hosts.findall(text)} - {"example.com"}, set())
                self.assertNotRegex(text, r"/home/|/Users/|\b[A-Z]:\\")


class MakefileTest(unittest.TestCase):
    def dry_run(self, target):
        result = subprocess.run(["make", "-n", "-C", str(PLUGIN), target], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_make_test_never_runs_the_suite(self):
        self.assertNotIn("plugin eval", self.dry_run("test"))

    def test_skill_evals_runs_both_arms_sandboxed_with_the_granted_tools(self):
        recipe = self.dry_run("skill-evals")
        for flag in ("claude plugin eval .", "--trust-plugin", "--no-publish", "--scaffold", "--keep-temp",
                     "--judge-model sonnet", "--max-cost-usd 20", "--output-dir var/skill-evals/$model",
                     '--allow-tools Write Edit "Bash(python3 *)" "Bash(mkdir *)" "Bash(cp *)"',
                     "grep -v '^/mnt/'", 'ln -s "$HOME/.claude"', 'ln -s "$HOME/.claude.json"'):
            self.assertIn(flag, recipe)
        self.assertNotIn("--ablation none", recipe, "the full suite runs with and without the plugin")
        self.assertNotIn("--runs", recipe, "the full suite keeps three runs per case")

    def test_the_smoke_run_is_one_case_once_with_the_plugin_only(self):
        self.assertIn("--case deck-pinned --runs 1 --ablation none", self.dry_run("skill-evals-smoke"))


if __name__ == "__main__":
    unittest.main()
