---
type: rule
---

# The kit's C4 `render.sh <view-key>` deletes every other rendered SVG

The `arch-structurizr` template `render.sh` (kit version 1.0.0, Structurizr `2026.05.22-playwright`) exports the whole workspace on every invocation and then, in single-view mode, runs `find views -name '*.svg' ! -name "<view-key>.svg" -delete` to keep only the requested one. So `./render.sh containers` after a full render leaves `views/` holding `containers.svg` alone; the other views' SVGs are gone from the working tree, and a `git add docs/` that follows commits their absence. Measured 2026-09-10: three of four views missing from a commit that looked complete because the `.md` embeds were untouched, discovered only when the arc42 page showed a broken image.

**How to apply:** never run the single-view form when other views exist; always `./render.sh` (all views) before committing, and check `git ls-files docs/architecture/c4/views/ | wc -l` against the number of `views { }` blocks in `workspace.dsl`. Treat "one SVG in `views/`" as the signature. The PlantUML twin (`diagrams/render.sh <name>`) has the same shape and deserves the same check.

**Why:** the failure is silent in the direction that matters: the render reports success, the embed paths still read correctly in the markdown, and only the rendered page reveals the loss. Fix belongs in the kit template (drop the delete, or export only the requested view); until then the full render is the only safe form.
