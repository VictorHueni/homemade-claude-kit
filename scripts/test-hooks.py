#!/usr/bin/env python3
"""Tests for the plugin hooks. Run: python3 scripts/test-hooks.py"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HOOKS = Path(__file__).resolve().parent.parent / "plugins" / "kit-core" / "hooks"
sys.path.insert(0, str(HOOKS))

import memory_write_check  # noqa: E402  # pyright: ignore[reportMissingImports]
import tripwires  # noqa: E402  # pyright: ignore[reportMissingImports]


def _decision(command: str) -> str | None:
    result = tripwires.evaluate(command)
    if result is None:
        return None
    out = result["hookSpecificOutput"]
    return out.get("permissionDecision") or ("note" if "additionalContext" in out else "?")


def _run(script: str, stdin: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOKS / script)], input=stdin, capture_output=True, text=True, env=env
    )


class TripwireTest(unittest.TestCase):
    def assertDecisions(self, expected, commands):
        for cmd in commands:
            self.assertEqual(_decision(cmd), expected, cmd)

    def test_denies_amend(self):
        self.assertDecisions("deny", [
            "git commit --amend",
            "git commit -a --amend --no-edit",
            "git -C kit commit --amend",
            "git -c user.name=x commit --amend",
            "git add . && git commit --amend",
            "git commit \\\n  --amend",
            "bash -c 'git commit --amend'",
            "eval \"git commit --amend\"",
            "git commit --amend # tripwire-ack",
        ])

    def test_ignores_amend_as_text(self):
        heredoc = "git commit -F - <<'EOF'\nfeat: block git commit --amend\nEOF"
        self.assertDecisions(None, [
            'git commit -m "hooks block --amend"',
            heredoc,
            "echo git commit --amend >> notes.md",
            "grep -rn 'git commit --amend' rules/",
            "git commit -m x # --amend",
            "git log --oneline",
        ])

    def test_denies_pgrep_wait_loop(self):
        self.assertDecisions("deny", [
            "until ! pgrep -f be-ci-local; do sleep 5; done",
            "while pgrep -af pytest >/dev/null; do sleep 1; done",
            'while [ -n "$(pgrep -f job)" ]; do sleep 1; done',
            "while pgrep --full job\ndo\n  sleep 1\ndone",
        ])

    def test_allows_other_process_lookups(self):
        self.assertDecisions(None, [
            "pgrep -f pytest",
            "until grep -q '^EXIT=' log; do sleep 5; done",
            "while read l; do echo $l; done < f; pgrep -f job",
            "ps -C python3",
        ])

    def test_issue_transfer_needs_ack(self):
        self.assertEqual(_decision("gh issue transfer 12 owner/other"), "deny")
        self.assertIsNone(_decision("gh issue transfer 12 owner/other  # tripwire-ack"))
        self.assertIsNone(_decision("gh help issue | grep 'gh issue transfer'"))

    def test_single_select_mutation_needs_ack(self):
        cmd = "gh api graphql -f query='mutation { updateProjectV2Field(input: {}) { clientMutationId } }'"
        self.assertEqual(_decision(cmd), "deny")
        self.assertIsNone(_decision(cmd + " # tripwire-ack"))

    def test_single_select_name_outside_a_graphql_call_passes(self):
        self.assertDecisions(None, [
            "grep -rn updateProjectV2Field docs/",
            "git commit -m 'note updateProjectV2Field'",
        ])

    def test_osv_scanner_gets_a_note_without_a_decision(self):
        out = tripwires.evaluate("osv-scanner scan source -r .")["hookSpecificOutput"]
        self.assertNotIn("permissionDecision", out)
        self.assertIn("--no-ignore", out["additionalContext"])
        self.assertDecisions(None, ["cat osv-scanner.toml", "rg osv-scanner docs/"])

    def test_plugin_mcp_and_dns_commands_get_notes(self):
        self.assertDecisions("note", [
            "claude plugin update kit-core@homemade-claude-kit",
            "claude plugin marketplace update homemade-claude-kit",
            "claude mcp list",
            "dig @ns1.example.net example.com SOA +short",
            "nslookup example.com",
            "echo example.com | xargs dig",
        ])
        self.assertDecisions(None, [
            "claude plugin list",
            "git commit -m 'run claude mcp list'",
            "grep -rn dig src/",
            "host=db ./run.sh",
        ])

    def test_cli_ignores_other_tools_and_bad_input(self):
        for stdin in (
            json.dumps({"tool_name": "Edit", "tool_input": {"command": "git commit --amend"}}),
            json.dumps({"tool_name": "Bash", "tool_input": {"command": 3}}),
            "[]",
            "not json",
        ):
            run = _run("tripwires.py", stdin)
            self.assertEqual((run.returncode, run.stdout, run.stderr), (0, "", ""), stdin)

    def test_cli_emits_deny_json(self):
        stdin = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git commit --amend"}})
        out = json.loads(_run("tripwires.py", stdin).stdout)["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")


class MemoryWriteTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.mkdtemp()
        patcher = mock.patch.object(memory_write_check.tempfile, "gettempdir", return_value=tmp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _write(self, path: str, session: str = "s1") -> dict | None:
        return memory_write_check.evaluate({"session_id": session, "tool_input": {"file_path": path}})

    def test_first_write_per_file_and_session_is_denied_once(self):
        path = "/home/u/.claude/projects/-home-u-repo/memory/feedback_x.md"
        self.assertEqual(self._write(path)["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIsNone(self._write(path))
        self.assertIsNotNone(self._write(path, session="s2"))
        self.assertIsNotNone(self._write(path.replace("feedback_x", "feedback_y")))

    def test_no_session_id_is_not_scoped_to_the_path_forever(self):
        path = "/home/u/.claude/projects/-home-u-repo/memory/feedback_x.md"
        self.assertIsNone(memory_write_check.evaluate({"tool_input": {"file_path": path}}))

    def test_other_paths_and_the_index_pass(self):
        for path in (
            "/home/u/.claude/projects/-home-u-repo/memory/MEMORY.md",
            "/home/u/repo/docs/memory/notes.md",
            "/home/u/repo/src/app.py",
        ):
            self.assertIsNone(self._write(path), path)

    def test_cli_ignores_bash_and_bad_input(self):
        for stdin in (json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}}), "[]", "not json"):
            run = _run("memory_write_check.py", stdin)
            self.assertEqual((run.returncode, run.stdout, run.stderr), (0, "", ""), stdin)


class DockerContextTest(unittest.TestCase):
    def setUp(self):
        self.config_dir = tempfile.mkdtemp()
        patcher = mock.patch.dict(os.environ, {"DOCKER_CONFIG": self.config_dir})
        patcher.start()
        self.addCleanup(patcher.stop)

    def _context(self, body: str) -> None:
        Path(self.config_dir, "config.json").write_text(body)

    def test_test_run_gets_a_note_on_wsl_with_desktop_context(self):
        self._context('{"currentContext": "desktop-linux"}')
        with mock.patch.object(tripwires, "_on_wsl", return_value=True):
            self.assertEqual(_decision("uv run pytest -m integration"), "note")
            self.assertEqual(_decision("make test-integration"), "note")
            self.assertIsNone(_decision("git status"))

    def test_silent_off_wsl_or_with_another_context(self):
        self._context('{"currentContext": "desktop-linux"}')
        with mock.patch.object(tripwires, "_on_wsl", return_value=False):
            self.assertIsNone(_decision("uv run pytest"))
        with mock.patch.object(tripwires, "_on_wsl", return_value=True):
            for body in ("{}", "[]", "not json"):
                self._context(body)
                self.assertIsNone(_decision("uv run pytest"), body)

    def test_session_start_prints_only_when_broken(self):
        self._context("{}")
        run = _run("docker_context_check.py", "", env=dict(os.environ))
        self.assertEqual((run.returncode, run.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
