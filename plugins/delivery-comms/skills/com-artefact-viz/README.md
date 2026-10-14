# com-artefact-viz

Render the kit's canonical Markdown artefacts into single-file, self-contained
interactive HTML views. The Markdown stays the source of truth; each view is a
regenerable read-out.

```
Markdown artefact ──parser──> model ──renderer──> one HTML file (CSS + JS inlined)
```

## Supported artefacts

| Kind | Source | View |
|---|---|---|
| `capability-map` | `business-capability-map` | L0-grouped cards + directional left-axis band |
| `fbs` | `spec-functional-breakdown-structure` | Collapsible tree, horizontal⇄vertical, status badges |
| `delivery-roadmap` | `plan-delivery-roadmap` | Phase-column timeline + walking skeleton + expandable epic features |
| `bmc` | `business-model-canvas` | 9-block canvas grid (BMC + Lean), confidence colour-coding |
| `service-blueprint` | `business-process` + `business-value-stream` + `business-persona` *(composition)* | Swimlane grid with the line of visibility, phase columns, pain overlays + cross-actor handoff spine |

## Usage

```bash
# Auto-detect kind, default output under docs/communication/visualisations/
python3 scripts/render.py docs/business/03a-capability-map.md

# The theme is the project design: the docs/ux/package.json pin found by walking up
# from the working directory, else the kit base theme. To preview another design,
# name a design-system folder (with a kit-manifest.json); a single stylesheet is refused.
python3 scripts/render.py docs/product-specs/07a-fbs.md --design-system path/to/design-system/

# Record the validator verdict next to the view
python3 scripts/shared/check_render.py --record docs/communication/visualisations/fbs.html.verdict.txt docs/communication/visualisations/fbs.html

# Vary the capability/FBS left-axis label + arrow per project
python3 scripts/render.py docs/business/03a-capability-map.md \
  --left-axis-label "Customer Journey" --left-axis-arrow "→"

# Live preview while editing the source
python3 scripts/dev_server.py docs/business/03a-capability-map.md --port 8000

# Compose a service blueprint (multi-source: process + value stream + personas)
python3 scripts/render.py --kind service-blueprint \
  --proc docs/business/05a-processes/proc-03-slot-rebooking.md \
  --value-stream docs/business/04a-value-stream.md \
  --personas docs/business/03b-personas/
```

Try it against the bundled fixtures:

```bash
for k in capability-map fbs delivery-roadmap bmc; do
  python3 scripts/render.py examples/$k.sample.md --out /tmp/$k.html
done

# the service blueprint fixture is a multi-file set
python3 scripts/render.py --kind service-blueprint \
  --proc examples/service-blueprint/process-slot-rebooking.md \
  --value-stream examples/service-blueprint/value-stream.md \
  --personas examples/service-blueprint/personas.md \
  --out /tmp/service-blueprint.html
```

## Layout

```
com-artefact-viz/
  SKILL.md                     Claude-facing instructions
  README.md                    This file
  templates/
    base.html.tmpl             Shell with {{slots}}
    tokens.domain.css          Domain colours as --kit-* properties on contract roles (status/pain on state roles, importance/confidence on the chart scale)
    runtime.js                 Vanilla JS: collapse, orientation, disclosure
  scripts/
    render.py                  CLI entrypoint (parse -> render -> write)
    parsers.py                 Canonical Markdown -> model (one per kind)
    shared/                    Base theme + contract, synced from plugins/delivery-comms/shared/ (do not edit here)
    renderers.py               Model -> HTML fragment + view CSS (one per kind)
    dev_server.py              Watch + serve live preview
  references/
    parsing-contract.md        Exactly what each parser reads
    viz-discipline.md          Principles and boundaries
  examples/                    Domain-neutral fixtures, one per kind
```

Python 3.12+, standard library only. No Node, no third-party packages. Each render writes `<out>.provenance.json` (which design themed it) and refuses to write a view that breaks the design contract ([`../../contract/README.md`](../../contract/README.md)).
