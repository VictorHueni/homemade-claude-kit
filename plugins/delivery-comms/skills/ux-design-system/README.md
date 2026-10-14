# ux-design-system

Gives a project the design its decks, views and release notes render with: a published design-system package pinned at an exact version (`point`), or a declared subset generated from a DESIGN.md (`subset`). The three delivery-comms renderers resolve that design themselves; the contract is [`contract/README.md`](../../contract/README.md).

```
DESIGN.md  --subset-->  docs/ux/design-system/  <--file: pin--  docs/ux/package.json  <--  renderers
                        (module CSS, manifest)                  (or an exact package version, from point)
```

## Usage

```bash
# A published design system: pin it, then add the printed Dependabot entry
python3 scripts/design_system.py point @scope/name@1.2.3

# No design system: start a DESIGN.md, fill it, generate the subset
python3 scripts/design_system.py scaffold
python3 scripts/design_system.py subset docs/ux/DESIGN.md

# A legacy docs/ux/tokens.css the renderers refuse: draft the DESIGN.md from it
python3 scripts/design_system.py subset --from-legacy docs/ux/tokens.css
```

The DESIGN.md is a [Google DESIGN.md](https://github.com/google-labs-code/design.md): it passes Google's linter (`make -C plugins/delivery-comms test-design-md`), and `subset` reads a Google DESIGN.md, skipping the keys and tokens the kit does not use. The first `subset` run on a DESIGN.md without chart colours writes a proposed chart palette into its `colors` and stops; the owner reviews it and removes the `proposed:` line.

## Layout

```
ux-design-system/
  SKILL.md                    Claude-facing instructions
  README.md                   This file
  scripts/
    design_system.py          point, subset, subset --from-legacy, scaffold
    shared/                   The kit resolver and contract, synced from the plugin's shared/
  templates/
    DESIGN.template.md        The DESIGN.md scaffold writes
  references/
    token-contract.md         Pointer to the plugin's contract/README.md
    discipline.md             Principles and boundaries
  examples/
    DESIGN.sample.md          A filled DESIGN.md
    legacy.tokens.css         A legacy token file to try --from-legacy on
```

Output: `docs/ux/`. Python 3.12+ and PyYAML.
