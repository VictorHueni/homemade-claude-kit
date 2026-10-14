"""Shared helpers for the delivery-comms characterisation tests."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILLS = Path(__file__).resolve().parent.parent / "skills"
FALLBACK_ACCENT = "#396cf5"


def run(script, *args, cwd):
    """Run a skill script isolated (-I) from a project folder with no docs/ux."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, "-I", str(script), *map(str, args)],
        cwd=cwd, env=env, capture_output=True, text=True,
    )


class RenderCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def assertLayersInOrder(self, html, markers):
        positions = []
        for marker in markers:
            self.assertIn(marker, html, f"CSS layer missing: {marker!r}")
            positions.append(html.index(marker))
        self.assertEqual(positions, sorted(positions), f"CSS layers out of order: {markers}")
