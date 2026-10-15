"""Reproducible output (Plan-0005 increment 10, closes #106): the same source and the same design give the same
bytes, whatever the clock says and whatever folder the render runs from.

The clock is simulated, never waited on: each render runs under a small bootstrap that moves `time.time`,
`datetime.date.today` and `datetime.datetime.now` to a fixed instant, so two renders "a minute apart" are
23:59:30 and 00:00:30 UTC on consecutive days (a minute apart that crosses midnight, the case a date stamp
shows). Chromium's own clock cannot be moved this way; the PDF tests in test_pdf.py assert the embedded dates
equal the source date instead.
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

DESIGNS = PLUGIN / "tests/fixtures/design-systems"
VIZ = SKILLS / "com-artefact-viz/scripts/render.py"
VIZ_SOURCE = SKILLS / "com-artefact-viz/examples/fbs.sample.md"
NOTE_RENDER = SKILLS / "com-release-note/scripts/render_pdf.py"
NOTE = SKILLS / "com-release-note/examples/release-note.complete.md"
DECK = SKILLS / "com-slide-deck/scripts"

# Run a script with the clock at a fixed instant (argv: epoch seconds, script, script args...).
BOOT = r"""
import datetime, runpy, sys, time
fake, script = float(sys.argv[1]), sys.argv[2]
start, real = time.time(), time.time
time.time = lambda: fake + (real() - start)
_date, _datetime = datetime.date, datetime.datetime
class FakeDate(_date):
    @classmethod
    def today(cls):
        return _date.fromtimestamp(time.time())
class FakeDateTime(_datetime):
    @classmethod
    def now(cls, tz=None):
        return _datetime.fromtimestamp(time.time(), tz)
    @classmethod
    def today(cls):
        return _datetime.fromtimestamp(time.time())
    @classmethod
    def utcnow(cls):
        return _datetime.fromtimestamp(time.time(), datetime.timezone.utc).replace(tzinfo=None)
datetime.date, datetime.datetime = FakeDate, FakeDateTime
sys.argv = [script, *sys.argv[3:]]
runpy.run_path(script, run_name="__main__")
"""
BEFORE_MIDNIGHT = datetime.datetime(2030, 1, 1, 23, 59, 30, tzinfo=datetime.timezone.utc).timestamp()
AFTER_MIDNIGHT = BEFORE_MIDNIGHT + 60


def run_at(instant, script, *args, cwd, env=None):
    """Run `script` like helpers.run, with the clock at `instant` (UTC) instead of now."""
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TZ": "UTC", **(env or {})}
    env = {k: v for k, v in env.items() if v is not None}
    return subprocess.run([sys.executable, "-I", "-c", BOOT, repr(instant), str(script), *map(str, args)],
                          cwd=cwd, env=env, capture_output=True, text=True)


def repo_relative(path):
    """The path the renders should print: relative to the source's repository root, else the file name."""
    path = Path(path).resolve()
    done = subprocess.run(["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True)
    if done.returncode != 0:
        return path.name
    return path.relative_to(Path(done.stdout.strip()).resolve()).as_posix()


def git_commit(folder, files, when):
    """Commit `files` (relative to `folder`) with author and committer date `when` (ISO, UTC)."""
    git = ["git", "-C", str(folder), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    env = {**os.environ, "GIT_COMMITTER_DATE": when, "GIT_AUTHOR_DATE": when}
    if not (folder / ".git").exists():
        subprocess.run(git + ["init", "-q"], check=True, env=env, capture_output=True)
    subprocess.run(git + ["add", *files], check=True, env=env, capture_output=True)
    subprocess.run(git + ["commit", "-q", "-m", "c"], check=True, env=env, capture_output=True)


class ReproCase(RenderCase):
    NO_EPOCH = {"SOURCE_DATE_EPOCH": None}

    def assertSameBytes(self, first, second):
        a, b = Path(first).read_bytes(), Path(second).read_bytes()
        if a != b:
            diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
            at = diff[0] if diff else min(len(a), len(b))
            self.fail(f"{Path(first).name} and {Path(second).name} differ ({len(diff)} byte(s), sizes "
                      f"{len(a)} and {len(b)}); first at {at}: {a[max(0, at - 60):at + 40]!r} vs "
                      f"{b[max(0, at - 60):at + 40]!r}")

    def assertNoMachinePath(self, path):
        text = Path(path).read_text(encoding="utf-8")
        self.assertNotIn(str(Path.home()), text, f"{Path(path).name} carries the home directory")
        self.assertNotIn(str(self.tmp), text, f"{Path(path).name} carries an absolute path")
        self.assertNotRegex(text, r"(?:\.\./){2,}", f"{Path(path).name} climbs out with ../")

    def ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result


class ClockTest(ReproCase):
    """Two HTML renders a minute apart across midnight are byte-identical, provenance included."""

    def twice(self, script, *args, outputs):
        for tag, instant in (("a", BEFORE_MIDNIGHT), ("b", AFTER_MIDNIGHT)):
            self.ok(run_at(instant, script, *[a.format(tag=tag) if isinstance(a, str) else a for a in args],
                           cwd=self.tmp, env=self.NO_EPOCH))
        for name in outputs:
            with self.subTest(output=name):
                self.assertSameBytes(self.tmp / name.format(tag="a"), self.tmp / name.format(tag="b"))

    def test_view(self):
        self.twice(VIZ, VIZ_SOURCE, "--design-system", DESIGNS / "full", "--out", "{tag}/view.html",
                   outputs=("{tag}/view.html", "{tag}/view.html.provenance.json"))

    def test_release_note(self):
        self.twice(NOTE_RENDER, NOTE, "--design-system", DESIGNS / "full", "--html-only", "--output", "{tag}/rn.pdf",
                   outputs=("{tag}/rn.html", "{tag}/rn.html.provenance.json"))

    def test_deck(self):
        self.ok(run(DECK / "init.py", "deck", cwd=self.tmp))
        self.twice(DECK / "build.py", "-c", "deck/config.yaml", "-o", "{tag}/deck.html",
                   outputs=("{tag}/deck.html", "{tag}/deck.html.provenance.json"))


class WorkingDirectoryTest(ReproCase):
    """Renders from two working directories are byte-identical and print a stable source path: relative to
    the source's repository root, else the file name; never absolute, never a ../ climb."""

    def cwds(self):
        near, far = self.tmp / "one", self.tmp / "two/deeper/still"
        near.mkdir()
        far.mkdir(parents=True)
        return near, far

    def test_view_footer_path(self):
        outs = []
        for cwd in self.cwds():
            out = cwd / "view.html"
            self.ok(run(VIZ, VIZ_SOURCE, "--design-system", DESIGNS / "full", "--out", out, cwd=cwd))
            outs.append(out)
        self.assertSameBytes(*outs)
        self.assertSameBytes(*(o.with_name(o.name + ".provenance.json") for o in outs))
        text = outs[0].read_text(encoding="utf-8")
        self.assertIn(f"from <code>{repo_relative(VIZ_SOURCE)}</code>", text)
        for out in (outs[0], outs[0].with_name(outs[0].name + ".provenance.json")):
            self.assertNoMachinePath(out)

    def test_release_note_cartouche_path(self):
        outs = []
        for cwd in self.cwds():
            self.ok(run(NOTE_RENDER, NOTE, "--design-system", DESIGNS / "full", "--html-only",
                        "--output", cwd / "rn.pdf", cwd=cwd))
            outs.append(cwd / "rn.html")
        self.assertSameBytes(*outs)
        self.assertSameBytes(*(o.with_name(o.name + ".provenance.json") for o in outs))
        self.assertIn(f"from <code>{repo_relative(NOTE)}</code>", outs[0].read_text(encoding="utf-8"))
        for out in (outs[0], outs[0].with_name(outs[0].name + ".provenance.json")):
            self.assertNoMachinePath(out)

    def test_deck(self):
        self.ok(run(DECK / "init.py", "deck", cwd=self.tmp))
        outs = []
        for cwd in self.cwds():
            out = cwd / "deck.html"
            self.ok(run(DECK / "build.py", "-c", self.tmp / "deck/config.yaml", "-o", out, cwd=cwd))
            outs.append(out)
        self.assertSameBytes(*outs)
        self.assertSameBytes(*(o.with_name(o.name + ".provenance.json") for o in outs))

    def test_source_outside_a_repository_prints_the_file_name(self):
        source = self.tmp / "src/fbs.sample.md"
        source.parent.mkdir()
        shutil.copyfile(VIZ_SOURCE, source)
        result = run(VIZ, source, "--out", "view.html", cwd=self.tmp / "src",
                     env={"GIT_CEILING_DIRECTORIES": str(self.tmp)})
        self.ok(result)
        self.assertIn("from <code>fbs.sample.md</code>", (self.tmp / "src/view.html").read_text(encoding="utf-8"))

    def test_provenance_names_the_design_folder_without_the_machine_path(self):
        # a design pinned with file: outside any repository is named by its folder name
        shutil.copytree(DESIGNS / "full", self.tmp / "design-system")
        ux = self.tmp / "project/docs/ux"
        ux.mkdir(parents=True)
        (ux / "package.json").write_text(json.dumps({"dependencies": {"@acme-test/full": "file:../../../design-system"}}),
                                         encoding="utf-8")
        (ux / "tokens.css").write_text(":root { --accent: #123456; }\n", encoding="utf-8")
        self.ok(run(VIZ, VIZ_SOURCE, "--out", "view.html", cwd=self.tmp / "project",
                    env={"GIT_CEILING_DIRECTORIES": str(self.tmp)}))
        prov_file = self.tmp / "project/view.html.provenance.json"
        prov = json.loads(prov_file.read_text(encoding="utf-8"))
        self.assertEqual(prov["designSystem"]["path"], "design-system")
        self.assertTrue(prov["warnings"], "the ignored legacy file should be warned about")
        self.assertNoMachinePath(prov_file)
        # a design inside a repository is named relative to its root
        self.ok(run(VIZ, VIZ_SOURCE, "--design-system", DESIGNS / "full", "--out", "view2.html", cwd=self.tmp))
        prov = json.loads((self.tmp / "view2.html.provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(prov["designSystem"]["path"], repo_relative(DESIGNS / "full"))


class ReleaseNoteDateTest(ReproCase):
    """The cartouche date comes from shared/source_date.py, never from the clock."""

    def render_copy(self, env, prepare=None):
        project = self.tmp / "project"
        project.mkdir()
        note = project / "note.md"
        shutil.copyfile(NOTE, note)
        if prepare:
            prepare(project, note)
        self.ok(run(NOTE_RENDER, note, "--html-only", cwd=project,
                    env={"SOURCE_DATE_EPOCH": None, "GIT_CEILING_DIRECTORIES": str(self.tmp), **env}))
        self.html = project / "pdf/note.html"
        text = self.html.read_text(encoding="utf-8")
        return re.search(r"com-release-note on (\d{4}-\d{2}-\d{2}) from", text).group(1)

    def test_source_date_epoch_wins(self):
        self.assertEqual(self.render_copy({"SOURCE_DATE_EPOCH": "31536000"}), "1971-01-01")

    def test_last_commit_date_of_the_source(self):
        self.assertEqual(self.render_copy({}, lambda project, note: git_commit(project, ["note.md"],
                                                                               "2001-02-03T12:00:00Z")), "2001-02-03")

    def test_newest_source_mtime_outside_git(self):
        def touch(project, note):
            stamp = datetime.datetime(2003, 4, 5, 12, tzinfo=datetime.timezone.utc).timestamp()
            os.utime(note, (stamp, stamp))
        self.assertEqual(self.render_copy({}, touch), "2003-04-05")

    def test_committing_the_output_beside_the_source_changes_no_byte(self):
        # The default output sits in <note-dir>/pdf/; committing it must not move the date of the next render.
        self.render_copy({}, lambda project, note: git_commit(project, ["note.md"], "2001-02-03T12:00:00Z"))
        first = self.html.read_bytes()
        git_commit(self.tmp / "project", ["pdf"], "2005-06-07T12:00:00Z")
        self.ok(run(NOTE_RENDER, self.tmp / "project/note.md", "--html-only", cwd=self.tmp / "project",
                    env={**self.NO_EPOCH, "GIT_CEILING_DIRECTORIES": str(self.tmp)}))
        self.assertEqual(self.html.read_bytes(), first)


class PdfDatesTest(unittest.TestCase):
    """shared/pdf_dates.py rewrites the Info dates in place, same length, so the xref table stays valid."""

    SAMPLE = (b"%PDF-1.4\n1 0 obj\n<</Creator (Chromium)\n/Producer (Skia/PDF m148)\n"
              b"/CreationDate (D:20261014170548+00'00')\n/ModDate (D:20261014170548+00'00')>>\nendobj\n"
              b"xref\n0 2\n0000000000 65535 f \n0000000009 00000 n \ntrailer\n<</Size 2 /Info 1 0 R>>\n"
              b"startxref\n130\n%%EOF\n")

    def setUp(self):
        import pdf_dates
        self.pdf_dates = pdf_dates
        self.when = datetime.datetime(1971, 1, 1, tzinfo=datetime.timezone.utc)

    def test_rewrites_both_dates_same_length(self):
        out = self.pdf_dates.normalise_bytes(self.SAMPLE, self.when)
        self.assertEqual(len(out), len(self.SAMPLE))
        self.assertIn(b"/CreationDate (D:19710101000000+00'00')", out)
        self.assertIn(b"/ModDate (D:19710101000000+00'00')", out)
        self.assertEqual(out.replace(b"19710101000000", b"20261014170548"), self.SAMPLE)

    def test_a_pdf_without_dates_is_refused(self):
        with self.assertRaises(self.pdf_dates.PdfDateError):
            self.pdf_dates.normalise_bytes(self.SAMPLE.replace(b"/CreationDate", b"/Other"), self.when)

    def test_an_unexpected_date_shape_is_refused_not_resized(self):
        with self.assertRaises(self.pdf_dates.PdfDateError):
            self.pdf_dates.normalise_bytes(self.SAMPLE.replace(b"+00'00'", b"Z", 1), self.when)

    def test_a_document_id_or_xmp_is_refused(self):
        # Skia writes neither today; if a Chromium update starts to, the render must stop being called reproducible.
        for extra in (b"/ID [<00><00>]", b"/Metadata 9 0 R"):
            with self.subTest(extra=extra):
                with self.assertRaises(self.pdf_dates.PdfDateError):
                    self.pdf_dates.normalise_bytes(self.SAMPLE.replace(b"/Size 2", b"/Size 2 " + extra), self.when)

    def test_normalise_file_in_place(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.pdf"
            path.write_bytes(self.SAMPLE)
            self.pdf_dates.normalise(path, self.when)
            self.assertIn(b"D:19710101000000+00'00'", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
