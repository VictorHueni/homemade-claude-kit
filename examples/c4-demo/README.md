# c4-demo — kit dogfood example

A throwaway demo system ("Claims Platform") used to validate the end-to-end pipeline of `arch-structurizr` + `arch-c4`. Not a real product, not maintained beyond what's needed to keep the kit's render pipeline working.

## How this demo was produced

```
# 1. Foundation (acting as arch-structurizr init)
cp arch-structurizr/templates/workspace.dsl   examples/c4-demo/docs/architecture/c4/workspace.dsl
cp arch-structurizr/templates/render.sh       examples/c4-demo/docs/architecture/c4/render.sh
cp arch-structurizr/templates/c4-readme.md    examples/c4-demo/docs/architecture/c4/README.md
# substitute {{structurizr_version}} and {{project_name}}/{{project_description}}
chmod +x render.sh

# 2. Authoring (acting as arch-c4 context, container, component, deployment)
# manually edit workspace.dsl to add all four C4 levels of detail
# manually generate arc42 markdown from arch-c4/templates/

# 3. Render
./docs/architecture/c4/render.sh
```

## What this validates

- `structurizr/structurizr:2026.05.22-playwright` can be pulled and run on WSL2 + Docker Desktop
- `workspace.dsl` parses against the seed grammar conventions
- `render.sh` validates + exports SVGs without manual intervention
- All four view types render: systemContext, containers, components-CON-XX, deployment-production
- arc42 markdown templates resolve relative SVG paths correctly when committed to `docs/architecture/arc42/`
- The `Domain aggregates implemented` column in §5 surfaces `properties.implements` from the DSL

## Re-rendering

Run `./docs/architecture/c4/render.sh` from inside `examples/c4-demo/`. Bumping the kit's pinned Structurizr image means updating `render.sh` here too and committing the re-rendered SVGs.
