---
type: Slice Design Sheet
title: "{{slice_title}}"
eyebrow: "{{eyebrow}}"
description: "{{lead}}"
tags: [slice-design]
timestamp: {{timestamp}}
status: draft
owner: {{owner}}
last_reviewed: {{date}}
review_interval: 30d
---

# {{slice_title}}: slice design sheet

The architectural view of one vertical slice, in four layers from the outside in: screens, API and contracts, code organisation, database. It is read before the slice's plan or tickets are cut, and they cite this folder by its path.

**Specification:** {{specification}}

**Authority.** This sheet follows the specification. When the two differ, the specification decides and the sheet is corrected.

## What is in this folder

| File | What it is |
|---|---|
| `README.md` | This file. Its frontmatter gives the page its title (`title`), its lead (`description`) and the line above the title (`eyebrow`). |
| `header.html`, `footer.html` | The labels under the lead, and the foot of the page. |
| `screens.html`, `api.html`, `code.html`, `database.html` | The content of one tab each. A file left with its summary line only is a layer the slice does not touch. |
| `openapi.json` (or `openapi.yaml`) | The OpenAPI document the API tab shows, when it has one. |
| `*.puml`, `_theme.puml`, `_palette.puml`, `render.sh` | The diagram sources and their render pipeline. |
| `views/`, `views/dark/` | The rendered diagrams, light and dark. Committed. |
| `out/` | The built page and its verdict. Generated, ignored by git. |

## Rebuild

```bash
# 1. The diagrams, light and dark (needs Docker)
./render.sh

# 2. The page, then its verdict; <com-artefact-viz> is the folder of that skill
python3 <com-artefact-viz>/scripts/render.py --kind slice-design --slice . --out out/{{slice_slug}}.html
python3 <com-artefact-viz>/scripts/shared/check_render.py --record out/{{slice_slug}}.html.verdict.txt out/{{slice_slug}}.html
```

The build is done when `out/{{slice_slug}}.html.verdict.txt` opens with `PASS: no findings`.

**Published page:** not published yet.
