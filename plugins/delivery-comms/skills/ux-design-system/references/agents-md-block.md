# AGENTS.md block

A project that renders with delivery-comms copies the five lines below into its own `AGENTS.md`, so any agent working there finds the design system, its manifest, the check every render must pass, and how version bumps arrive. Leave `<skill-dir>` as written: an agent fills it in from the "Base directory for this skill" line of the delivery-comms skill it runs (`com-slide-deck`, `com-artefact-viz`, `com-release-note` or `ux-design-system`).

```markdown
## Design system (delivery-comms)
- Pin: `docs/ux/package.json` names the one design system at an exact version (or `file:design-system` for a generated subset). Change it only with `ux-design-system point <package>@<x.y.z>` or `subset`, never by hand, and never add a `docs/ux/tokens.css`.
- Manifest: the design system's `kit-manifest.json` (in the pinned package, or `docs/ux/design-system/kit-manifest.json` for a subset) lists the modules it provides and the ones it omits; the kit's base theme fills the omitted ones, and each render's `<output>.provenance.json` says which came from where.
- Validator: after every render, run `python3 <skill-dir>/scripts/shared/check_render.py --record <output>.verdict.txt <output>`; the output is not done until the verdict reads `PASS: no findings`.
- Dependabot: `.github/dependabot.yml` keeps an `npm` entry with `directory: "/docs/ux"` (the one `point` prints), so design-system version bumps arrive as pull requests.
```
