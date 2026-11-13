---
type: Slice Design Sheet
title: "Rebook a slot"
eyebrow: "Booking service · slice design sheet · release 3"
description: "A customer moves a booked slot to another free one. One operation, three tables, no new screen."
status: active
---

# Rebook a slot (fixture)

A synthetic slice folder for the `slice-design` kind of `com-artefact-viz`: a README whose frontmatter gives the page its title, its lead and the line above the title, one HTML partial per tab (`api.html`, `code.html`, `database.html`; no `screens.html`, so that tab shows its empty state), `header.html` and `footer.html` for the labels under the lead and the foot of the page, an OpenAPI document and the rendered diagrams.

The two `.puml` sources were rendered with the `arch-plantuml` pipeline (`init` in this folder, then `./render.sh`), which wrote `views/*.svg` and `views/dark/*.svg`. The pipeline files themselves are not kept in the fixture.

Render it from the repository root:

```bash
python3 plugins/delivery-comms/skills/com-artefact-viz/scripts/render.py --kind slice-design --slice plugins/delivery-comms/skills/com-artefact-viz/examples/slice-design --out /tmp/rebook-a-slot.html
```
