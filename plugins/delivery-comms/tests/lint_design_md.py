"""Run Google's DESIGN.md linter on every DESIGN.md the kit writes (`make test-design-md`; needs Node and the network).

The files: the ux-design-system template as shipped, a scaffolded DESIGN.md, the sample, a --from-legacy draft
(with its proposed chart colours) and a scaffolded file after `subset` wrote its proposed chart palette. All
are generated into a temporary folder. A file passes when the linter exits 0 with no error and no warning.

Usage: python3 lint_design_md.py PACKAGE   (PACKAGE: the linter at an exact version, such as @google/design.md@0.4.0)
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

UX = Path(__file__).resolve().parent.parent / "skills/ux-design-system"
SCRIPT = UX / "scripts/design_system.py"


def ds(*args, cwd):
    done = subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True)
    return done.returncode, done.stdout + done.stderr


def generate(tmp):
    """{label: path} of the DESIGN.md files to lint, written under tmp."""
    files = {"template": tmp / "template/DESIGN.md", "sample": tmp / "sample/DESIGN.md"}
    sources = {"template": UX / "templates/DESIGN.template.md", "sample": UX / "examples/DESIGN.sample.md"}
    for label, source in sources.items():
        files[label].parent.mkdir(parents=True)
        shutil.copyfile(source, files[label])

    scaffolded = tmp / "scaffold"
    scaffolded.mkdir()
    code, out = ds("scaffold", "docs", cwd=scaffolded)
    assert code == 0, out
    files["scaffolded"] = scaffolded / "docs/ux/DESIGN.md"

    proposal = tmp / "proposal"
    proposal.mkdir()
    ds("scaffold", "docs", cwd=proposal)
    code, out = ds("subset", "docs/ux/DESIGN.md", cwd=proposal)
    assert code == 2 and "proposed" in out, out
    files["proposed palette"] = proposal / "docs/ux/DESIGN.md"

    legacy = tmp / "legacy/docs/ux"
    legacy.mkdir(parents=True)
    shutil.copyfile(UX / "examples/legacy.tokens.css", legacy / "tokens.css")
    code, out = ds("subset", "--from-legacy", "docs/ux/tokens.css", cwd=tmp / "legacy")
    assert code == 0, out
    files["from-legacy draft"] = legacy / "DESIGN.md"
    return files


def lint(package, path):
    npx = shutil.which("npx")
    if npx is None:
        sys.exit("lint_design_md: npx not found; install Node.js 18 or later")
    done = subprocess.run([npx, "--yes", package, "lint", str(path)], capture_output=True, text=True)
    try:
        report = json.loads(done.stdout)
    except ValueError:
        report = None
    return done.returncode, report, done.stdout + done.stderr


def main(argv):
    if len(argv) != 1 or "@" not in argv[0][1:]:
        sys.exit(__doc__)
    package = argv[0]
    failed = 0
    with tempfile.TemporaryDirectory(prefix="design-md-lint-") as tmp:
        for label, path in generate(Path(tmp)).items():
            code, report, raw = lint(package, path)
            if report is None:
                print(f"FAIL {label}: exit {code}, no JSON report\n{raw}")
                failed += 1
                continue
            summary = report["summary"]
            ok = code == 0 and summary.get("errors", 0) == 0 and summary.get("warnings", 0) == 0
            failed += not ok
            print(f"{'PASS' if ok else 'FAIL'} {label}: exit {code}, {json.dumps(summary)}")
            for finding in report["findings"]:
                print(f"    {finding['severity']}: {finding.get('rule', '')} {finding.get('path', '')} "
                      f"{finding['message']}".rstrip())
    print(f"{package}: {failed} of 5 files failed" if failed else f"{package}: 5 files pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
