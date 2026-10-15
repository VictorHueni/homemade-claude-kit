#!/usr/bin/env python3
"""
render.py — com-artefact-viz CLI.

Render a canonical kit artefact (capability map, FBS, delivery roadmap, BMC) to
a single self-contained interactive HTML file — or compose a service blueprint
from several source artefacts (multi-source; see --proc below).

    python render.py SOURCE.md [options]
    python render.py --kind service-blueprint --proc PROC.md [--value-stream VS.md] [--personas PATH]

Options:
    --out PATH              Output HTML path. Default:
                            docs/communication/visualisations/<kind>.html
    --kind KIND             Force the artefact kind (capability-map | fbs |
                            delivery-roadmap | bmc | service-blueprint).
                            Auto-detected from path/content when omitted.
    --proc FILE             A business-process doc to compose into a service
                            blueprint (repeatable). Implies --kind service-blueprint.
    --value-stream FILE     Value-stream doc supplying the blueprint's phase
                            columns (optional; falls back to §6 step order).
    --personas PATH         Persona doc or directory used to derive the line of
                            visibility (front/back-stage). Repeatable.
    --stream VS-N           Limit blueprint phase columns to one value stream.
    --design-system DIR     A design-system folder (with a kit-manifest.json),
                            bypassing the docs/ux/package.json pin. Without it
                            the pin is found by walking up from the working
                            directory, else the kit's base theme is used. A
                            single stylesheet (a legacy tokens.css) is refused.
    --exception NAME=VALUE  A named local exception the validator allows and the
                            provenance report lists (repeatable).
    --left-axis-label TEXT  Override the capability-map / FBS left-axis label
                            (the directional "arrow" band). Defaults to the
                            artefact's declared L0 axis.
    --left-axis-arrow CHAR  Arrow glyph for that band (default "▼").
    --title TEXT            Override the page title.
    --detect                Print the detected kind and exit (no render).

The design is resolved once per render (shared/design_source.py) and the written
HTML is checked against it (shared/check_render.py): a view that breaks the
design writes nothing and exits 1; a refused design exits 2. The provenance
report is printed and written next to the view as <out>.provenance.json.

Standard library only. Run from the repo root or anywhere — paths are resolved
relative to the current directory. The footer names each source relative to its
repository root (else by file name) and dates it from the sources
(shared/source_date.py), so the same sources give the same bytes from any folder.
"""

import argparse
import json
import os
import sys
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import parsers  # noqa: E402
import renderers  # noqa: E402

sys.path.insert(0, os.path.join(HERE, "shared"))
import check_render  # noqa: E402  (the synced copies of the shared resolver, validator and date source)
import design_source  # noqa: E402
import source_date  # noqa: E402
from source_path import display_path  # noqa: E402
from design_source import DesignError  # noqa: E402

# The modules the views read: core (every colour, font and spacing role), dataviz (the --chart-*
# scale steps), type (the bold weight) and space-shape (the pill radius). The other modules (document,
# slide-frame, print, brand) style nothing a view draws, so they are not inlined; guidance is informational.
VIEW_MODULES = ("core", "dataviz", "type", "space-shape")

SKILL_DIR = os.path.dirname(HERE)
TEMPLATE_DIR = os.path.join(SKILL_DIR, "templates")


def _read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fill_template(slots):
    tmpl = _read(os.path.join(TEMPLATE_DIR, "base.html.tmpl"))
    for key, value in slots.items():
        tmpl = tmpl.replace("{{" + key + "}}", value)
    return tmpl


def _read_personas(paths):
    """A persona arg may be a file or a directory of persona docs; read all."""
    texts = []
    for path in paths or []:
        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                if name.lower().endswith(".md"):
                    texts.append(_read(os.path.join(path, name)))
        elif os.path.isfile(path):
            texts.append(_read(path))
        else:
            sys.exit(f"error: --personas path not found: {path}")
    return texts


def build(source_path, args):
    options = {
        "left_axis_label": args.left_axis_label,
        "left_axis_arrow": args.left_axis_arrow,
        "stream": args.stream,
        "title": args.title,
    }

    # ---- Multi-source composition lens (service blueprint) -----------------
    if args.proc or args.kind == "service-blueprint":
        kind = "service-blueprint"
        if not args.proc:
            sys.exit("error: --kind service-blueprint needs at least one --proc FILE.")
        for p in args.proc:
            if not os.path.isfile(p):
                sys.exit(f"error: --proc file not found: {p}")
        if args.value_stream and not os.path.isfile(args.value_stream):
            sys.exit(f"error: --value-stream file not found: {args.value_stream}")
        if args.detect:
            print(kind)
            return None
        proc_texts = [_read(p) for p in args.proc]
        vs_text = _read(args.value_stream) if args.value_stream else None
        persona_texts = _read_personas(args.personas)
        model = parsers.parse_service_blueprint(proc_texts, vs_text, persona_texts, options)
        rendered = renderers.RENDERERS[kind](model, options)
        sources = [*args.proc, *([args.value_stream] if args.value_stream else []), *(args.personas or [])]
        return _emit(model, rendered, kind, args, source_label=", ".join(map(display_path, args.proc)),
                     sources=sources)

    # ---- Single-source path (capability-map | fbs | delivery-roadmap | bmc) -
    if not source_path:
        sys.exit("error: provide a SOURCE.md (or use --proc for a service blueprint).")
    text = _read(source_path)
    kind = args.kind or parsers.detect_kind(source_path, text)
    if not kind:
        sys.exit(
            f"error: could not detect artefact kind for {source_path!r}. "
            f"Pass --kind capability-map|fbs|delivery-roadmap|bmc."
        )
    if kind not in parsers.PARSERS:
        sys.exit(f"error: unknown kind {kind!r}.")

    if args.detect:
        print(kind)
        return None

    model = parsers.PARSERS[kind](text)
    rendered = renderers.RENDERERS[kind](model, options)
    return _emit(model, rendered, kind, args, source_label=display_path(source_path), sources=[source_path])


class RenderRefused(Exception):
    """The view breaks the resolved design; nothing was written."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


def resolve_design(args):
    """The view's design: the --design-system folder, else the docs/ux/package.json pin found by walking up
    from the working directory, else the kit's base theme. A single stylesheet is refused."""
    explicit = None
    if args.design_system:
        explicit = Path(args.design_system)
        if explicit.is_file():
            raise DesignError("--design-system names a single stylesheet; it must name a design-system folder with "
                              "a kit-manifest.json.\n" + design_source._legacy_message(explicit))
        if not explicit.is_dir():
            raise DesignError(f"--design-system: {explicit} does not exist; name a design-system folder with a "
                              "kit-manifest.json, or leave it out to use the docs/ux/package.json pin")
    return design_source.resolve(Path.cwd(), explicit=explicit)


def parse_exceptions(items):
    out = {}
    for item in items or []:
        name, sep, value = item.partition("=")
        if not sep or not name or not value:
            raise DesignError(f"--exception wants NAME=VALUE, got {item!r}")
        out[name] = value
    return out


def design_layer(design):
    """The font faces, then the modules the views read (base first, the design system after it)."""
    return "\n".join(design.fonts + [design.css[m] for m in VIEW_MODULES if design.css.get(m)])


def provenance_summary(design, report):
    prov, ident = design.provenance, design.provenance["designSystem"]
    source = ident["source"] if ident["source"] == "base" else \
        f"{ident.get('name') or ident.get('path')}{'@' + ident['version'] if ident.get('version') else ''}"
    lines = [f"design {source}"]
    for origin in ("design-system", "base"):
        mods = [m for m, o in prov["modules"].items() if o == origin]
        if mods:
            lines.append(f"{origin}: {', '.join(mods)}")
    lines.append(f"inlined: {', '.join(VIEW_MODULES)}")
    lines += [f"exception {e['name']}={e['value']}" + ("" if e["known"] else " (not in the design's vocabulary)")
              for e in report["exceptions"]]
    lines += [f"warning: {w}" for w in prov.get("warnings", [])]
    return "\n".join(lines)


def write_atomic(path, text):
    """Write beside the target, then rename into place; a bare file name writes in the working directory."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _emit(model, rendered, kind, args, source_label, sources):
    # Cascade: the resolved design (font faces, core, dataviz, type, space-shape; marked data-design-layer,
    # the only place literals may live, and declaring --kit-on-<fill> for text on each fill), then the viz
    # domain colours (--kit-* on contract roles), the baseline layout and the view CSS (roles only).
    design = resolve_design(args)
    exceptions = parse_exceptions(args.exception)
    domain = "/* ---- viz domain tokens (derived) ---- */\n" + _read(os.path.join(TEMPLATE_DIR, "tokens.domain.css"))

    runtime = _read(os.path.join(TEMPLATE_DIR, "runtime.js"))
    title = args.title or model["title"]
    try:
        stamped = source_date.source_date(sources).isoformat()
    except source_date.SourceDateError as exc:
        raise DesignError(str(exc))
    footer = (
        f'Generated by com-artefact-viz from '
        f'<code>{_esc(source_label)}</code> on {stamped}. '
        f'Source artefact is the single source of truth — re-render after edits.'
    )

    html = fill_template({
        "TITLE": _esc(title),
        "KIND": _esc(rendered["kind_label"]),
        "META": rendered["meta"],
        "TOOLBAR": rendered["toolbar"],
        "CONTENT": rendered["content"],
        "DESIGN_LAYER": design_layer(design),
        "DOMAIN_CSS": domain,
        "VIEW_CSS": rendered["view_css"],
        "RUNTIME_JS": runtime,
        "FOOTER": footer,
    })

    out = args.out or default_out(kind)
    # Check, then write: a view that breaks the design writes nothing.
    report = check_render.check(html, design, exceptions)
    if not report["ok"]:
        raise RenderRefused(f"the view breaks the design ({len(report['findings'])} finding(s)); nothing was "
                            "written:\n" + check_render.format_text(report, out))
    write_atomic(out, html)
    prov_file = out + ".provenance.json"
    write_atomic(prov_file, json.dumps(design.provenance, indent=2) + "\n")
    print("check: PASS, the view uses only the design's roles")
    print("provenance: " + provenance_summary(design, report).replace("\n", "; ") + f" ({prov_file})")
    return out


def _esc(s):
    import html
    return html.escape(s or "", quote=True)


def default_out(kind):
    return os.path.join("docs", "communication", "visualisations", f"{kind}.html")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render a kit artefact to interactive HTML.")
    ap.add_argument("source", nargs="?",
                    help="Source Markdown artefact (single-source kinds). Omit for --proc.")
    ap.add_argument("--out")
    ap.add_argument("--kind", choices=sorted(parsers.PARSERS) + list(parsers.MULTISOURCE_KINDS))
    ap.add_argument("--design-system", dest="design_system", metavar="DIR",
                    help="A design-system folder with a kit-manifest.json (bypasses the docs/ux/package.json pin).")
    ap.add_argument("--exception", action="append", metavar="NAME=VALUE",
                    help="A named local exception the validator allows (repeatable).")
    ap.add_argument("--left-axis-label", dest="left_axis_label")
    ap.add_argument("--left-axis-arrow", dest="left_axis_arrow", default="▼")
    ap.add_argument("--title")
    ap.add_argument("--detect", action="store_true")
    # service-blueprint composition lens (multi-source)
    ap.add_argument("--proc", action="append", metavar="FILE",
                    help="A business-process doc to compose (repeatable).")
    ap.add_argument("--value-stream", dest="value_stream", metavar="FILE",
                    help="Value-stream doc supplying the phase columns (optional).")
    ap.add_argument("--personas", action="append", metavar="PATH",
                    help="Persona doc or directory; classifies front/back-stage (repeatable).")
    ap.add_argument("--stream", metavar="VS-N",
                    help="Limit phase columns to one value stream (e.g. VS-1).")
    args = ap.parse_args(argv)

    if args.source and not os.path.isfile(args.source):
        sys.exit(f"error: source not found: {args.source}")

    try:
        out = build(args.source, args)
    except (DesignError, RenderRefused) as exc:
        print(f"com-artefact-viz: REFUSED: {exc}", file=sys.stderr)
        sys.exit(exc.code)
    if out:
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
