"""Goldens: the computed styles and the PDF pixels of the fixture renders, captured from the 2.0.0 release.

A golden holds, for one render, the computed style of every element of the page (cascade values only: no box
geometry, which follows the fonts a machine has) and, for each PDF page, a grid of mean colours. Styles compare
exactly. A grid cell may move by CELL_TOLERANCE per channel: the fixtures use system font stacks, and glyphs
rasterise differently from one machine to the next, while a role that changes colour moves whole cells.

The goldens run in the browser lane (`make test-pdf` sets DELIVERY_COMMS_GOLDENS=1) and read the PDF pages
with pypdfium2. To capture them from a kit checkout (run with the interpreter of the test lane):
    python3 tests/goldens.py capture <checkout>/plugins/delivery-comms/skills tests/goldens
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
GOLDENS = HERE / "goldens"
DESIGNS = {"base": None, "full": FIXTURES / "design-systems/full", "subset": FIXTURES / "design-systems/subset"}
EPOCH = "31536000"          # 1971-01-01: the render date, printed in a document's footer, never moves
CELL_PX = 8                 # a grid cell is the mean of CELL_PX x CELL_PX rendered pixels
COLUMNS = 16
CELL_TOLERANCE = 24
LONG_VALUE = 96             # a longer computed value (an inlined logo) is kept as its hash

# Cascade values only: margins, widths and heights are used values that follow the text metrics.
PROPERTIES = (
    "color", "background-color", "background-image", "border-top-color", "border-right-color",
    "border-bottom-color", "border-left-color", "border-top-style", "border-bottom-style", "border-top-width",
    "border-bottom-width", "border-left-width", "border-top-left-radius", "box-shadow", "outline-color",
    "font-family", "font-size", "font-weight", "font-style", "letter-spacing", "line-height", "text-transform",
    "text-decoration-color", "opacity", "display", "position", "visibility", "fill", "stroke",
    "padding-top", "padding-left",
)

CASES = {}
for _design in ("base", "full", "subset"):
    CASES[f"slides-{_design}"] = ("deck", "slides", _design)
    CASES[f"document-{_design}"] = ("deck", "document", _design)
for _sample in ("fbs", "capability-map", "delivery-roadmap", "bmc"):
    for _design in ("base", "full"):
        CASES[f"view-{_sample}-{_design}"] = ("view", _sample, _design)
for _design in ("base", "full"):
    CASES[f"report-{_design}"] = ("report", "release-note.complete", _design)

_STYLES_JS = """(props) => Array.from(document.querySelectorAll('html, body, body *'))
  .filter((el) => !['SCRIPT', 'STYLE'].includes(el.tagName))
  .map((el) => {
    const cs = getComputedStyle(el);
    const name = el.tagName.toLowerCase() + Array.from(el.classList).map((c) => '.' + c).join('');
    return [name, props.map((p) => cs.getPropertyValue(p))];
  })"""


def require_lane(case):
    """Skip outside the browser lane; there, a missing browser or rasteriser fails in CI and skips elsewhere."""
    if os.environ.get("DELIVERY_COMMS_GOLDENS") != "1":
        case.skipTest("the goldens run in the browser lane: make test-pdf")
    from pdf_helpers import require_browser
    require_browser(case)
    require_rasteriser(case)


def require_rasteriser(case):
    """Skip locally without pypdfium2; in CI (CI=true) it is an error, not a skip."""
    try:
        import pypdfium2  # noqa: F401
    except ImportError:
        if os.environ.get("CI") == "true":
            case.fail("pypdfium2 is required in CI to read the PDF pages and is missing")
        case.skipTest("pypdfium2 missing: pip install pypdfium2")


def _run(script, *args, cwd):
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "SOURCE_DATE_EPOCH": EPOCH}
    result = subprocess.run([sys.executable, "-I", str(script), *map(str, args)], cwd=cwd, env=env,
                            capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{Path(script).name} failed ({result.returncode}):\n{result.stdout}{result.stderr}")


def render(name, skills, work):
    """Render case `name` with the scripts under `skills` into `work`; (html path, pdf path or None)."""
    kind, source, design = CASES[name]
    folder = DESIGNS[design]
    work.mkdir(parents=True, exist_ok=True)
    if kind == "deck":
        shutil.copytree(FIXTURES / "decks", work / "decks")
        config = work / "decks" / source / "config.yaml"
        cfg = yaml.safe_load(config.read_text(encoding="utf-8"))
        if folder:
            cfg["paths"]["design_tokens"] = str(folder)
        config.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
        scripts = skills / "com-slide-deck/scripts"
        _run(scripts / "build.py", "-c", config, cwd=work)
        _run(scripts / "render.py", "--config", config, "--output", work / "out.pdf", cwd=work)
        return config.parent / "output" / cfg["paths"]["output_filename"], work / "out.pdf"
    extra = ("--design-system", folder) if folder else ()
    if kind == "view":
        sample = skills / f"com-artefact-viz/examples/{source}.sample.md"
        _run(skills / "com-artefact-viz/scripts/render.py", sample, "--out", work / "view.html", *extra, cwd=work)
        return work / "view.html", None
    note = skills / f"com-release-note/examples/{source}.md"
    _run(skills / "com-release-note/scripts/render_pdf.py", note, *extra, "--output", work / "rn.pdf", cwd=work)
    return work / "rn.html", work / "rn.pdf"


def _short(value):
    value = " ".join(value.split())
    return value if len(value) <= LONG_VALUE else "sha256:" + hashlib.sha256(value.encode()).hexdigest()[:16]


def computed_styles(browser, html_path):
    """{"properties", "values", "styles": unique rows of value indexes, "elements": ["<tag.classes> <row>", ...] in
    document order}."""
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto(html_path.as_uri(), wait_until="networkidle")
    rows = page.evaluate(_STYLES_JS, list(PROPERTIES))
    page.close()
    table, seen, styles, index, elements = [], {}, [], {}, []
    for element, values in rows:
        row = []
        for value in map(_short, values):
            if value not in seen:
                seen[value] = len(table)
                table.append(value)
            row.append(seen[value])
        row = tuple(row)
        if row not in index:
            index[row] = len(styles)
            styles.append(list(row))
        elements.append(f"{element} {index[row]}")
    return {"properties": list(PROPERTIES), "values": table, "styles": styles, "elements": elements}


def pdf_cells(pdf_path):
    """[{"grid": [columns, rows], "cells": hex RGB means, row by row}] for each page of the PDF."""
    import pypdfium2
    pages = []
    document = pypdfium2.PdfDocument(str(pdf_path))
    try:
        for page in document:
            width, height = page.get_size()
            rows = max(1, round(COLUMNS * height / width))
            bitmap = page.render(scale=COLUMNS * CELL_PX / width, rev_byteorder=True)
            data, stride, channels = bytes(bitmap.buffer), bitmap.stride, bitmap.n_channels
            out = bytearray()
            for r in range(rows):
                y0, y1 = r * bitmap.height // rows, (r + 1) * bitmap.height // rows
                for c in range(COLUMNS):
                    x0, x1 = c * bitmap.width // COLUMNS, (c + 1) * bitmap.width // COLUMNS
                    sums, count = [0, 0, 0], max(1, (y1 - y0) * (x1 - x0))
                    for y in range(y0, y1):
                        line = y * stride
                        for x in range(x0, x1):
                            at = line + x * channels
                            sums[0] += data[at]
                            sums[1] += data[at + 1]
                            sums[2] += data[at + 2]
                    out += bytes(round(s / count) for s in sums)
            pages.append({"grid": [COLUMNS, rows], "cells": out.hex()})
            page.close()
    finally:
        document.close()
    return pages


def capture(name, skills, work, browser):
    """The golden of case `name`, rendered with the scripts under `skills`."""
    html_path, pdf_path = render(name, skills, work)
    golden = {"case": name, "styles": computed_styles(browser, html_path)}
    if pdf_path is not None:
        golden["pages"] = pdf_cells(pdf_path)
    return golden


def load(name):
    return json.loads((GOLDENS / f"{name}.json").read_text(encoding="utf-8"))


def differences(expected, actual, limit=12):
    """Readable lines for each way `actual` departs from the golden `expected`; [] when it matches."""
    out = []
    want, got = expected["styles"], actual["styles"]
    if want["properties"] != got["properties"]:
        return ["the golden records other properties; capture it again"]
    if len(want["elements"]) != len(got["elements"]):
        out.append(f"{len(got['elements'])} elements, the golden has {len(want['elements'])}")
    for i, (w, g) in enumerate(zip(want["elements"], got["elements"])):
        w_name, w_row = w.rsplit(" ", 1)
        g_name, g_row = g.rsplit(" ", 1)
        if w_name != g_name:
            out.append(f"element {i}: {g_name}, the golden has {w_name}")
            break
        w_values = [want["values"][v] for v in want["styles"][int(w_row)]]
        g_values = [got["values"][v] for v in got["styles"][int(g_row)]]
        for prop, a, b in zip(want["properties"], w_values, g_values):
            if a != b:
                out.append(f"element {i} {g_name}: {prop} is {b!r}, the golden has {a!r}")
        if len(out) >= limit:
            return out[:limit]
    want_pages, got_pages = expected.get("pages"), actual.get("pages")
    if (want_pages is None) != (got_pages is None) or len(want_pages or []) != len(got_pages or []):
        out.append(f"{len(got_pages or [])} PDF pages, the golden has {len(want_pages or [])}")
        return out[:limit]
    for number, (w, g) in enumerate(zip(want_pages or [], got_pages or []), start=1):
        if w["grid"] != g["grid"]:
            out.append(f"page {number}: grid {g['grid']}, the golden has {w['grid']}")
            continue
        a, b = bytes.fromhex(w["cells"]), bytes.fromhex(g["cells"])
        worst = max(range(len(a)), key=lambda k: abs(a[k] - b[k]))
        if abs(a[worst] - b[worst]) > CELL_TOLERANCE:
            cell = worst // 3
            out.append(f"page {number}: cell (column {cell % w['grid'][0]}, row {cell // w['grid'][0]}) moves by "
                       f"{abs(a[worst] - b[worst])} on a channel, more than {CELL_TOLERANCE}")
    return out[:limit]


def main(argv):
    if len(argv) != 3 or argv[0] != "capture":
        print(__doc__, file=sys.stderr)
        return 2
    import tempfile
    from playwright.sync_api import sync_playwright
    skills, out = Path(argv[1]).resolve(), Path(argv[2]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        browser = p.chromium.launch()
        for name in CASES:
            golden = capture(name, skills, Path(tmp) / name, browser)
            (out / f"{name}.json").write_text(json.dumps(golden, separators=(",", ":")) + "\n", encoding="utf-8")
            print(f"captured {name}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
