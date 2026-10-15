# Deck Design Notes

> The palette, typography, spacing, slide canvas, slide frame (section label,
> logo, legal line, slide number) and fonts come from the **project's design
> system**, resolved by `build.py` and inlined before this deck's
> `styles.css`. This file records only what the deck adds on top: its
> components and layout rules. A deck that uses the frame and plain text needs
> nothing here; fill a section when the deck adds what it describes.
> Copy this template to `design-system.md` in the same folder.

---

## 1. Design Philosophy

_Describe in 2-3 sentences what this deck's layouts should convey, within the project design (whose written guidance, when it provides the `guidance` module, the provenance report names)._

**Principles** (list 3-5):

1. ...
2. ...
3. ...

---

## 2. Colour Roles

The deck's colours are the project design's **contract roles**, inlined by
`build.py` in a `<style data-design-layer>` before `styles.css`. The design
comes from `paths.design_tokens` in `config.yaml` (a design-system folder),
else the `docs/ux/package.json` pin found by walking up from the deck, else
the kit's neutral base theme. A project without a design gets one from the
[`ux-design-system`](../../../../ux-design-system/SKILL.md) skill (`point` a
published package, or `subset` from a `docs/ux/DESIGN.md`); a legacy
`docs/ux/tokens.css` is refused and moves with `subset --from-legacy`.
The full role list is the contract (`plugins/delivery-comms/contract/README.md`).

**Do not define colours in `styles.css`.** The build refuses a literal colour
outside the design layer and a custom property outside the contract (and the
reserved `--kit-*` prefix), and writes nothing until the CSS uses roles.

### Core roles (use, never redefine)

| Role           | Usage                                          |
|----------------|------------------------------------------------|
| `--canvas-bg`  | Page background                                |
| `--surface`    | Card and cell background                       |
| `--surface-2`  | Recessed / grouped background                  |
| `--ink`        | Primary text                                   |
| `--muted`      | Secondary and tertiary text                    |
| `--border`     | Card borders, dividers, separators             |
| `--accent`     | Primary accent (highlights, labels)            |
| `--accent-ink` | Text on accent fills                           |
| `--success` / `--warning` / `--danger` / `--info` | State colours |

Text on a filled background uses `var(--kit-on-<fill>)` (for example `var(--kit-on-success)`), which the resolver points at the text role that reaches WCAG AA on that fill. Charts use `--chart-1` to `--chart-4` (darkest first), `--chart-rest`, `--chart-axis`, `--chart-grid`, `--chart-highlight`.

### Deck-local values (declared exceptions)

Prefer a role (`--muted` for tertiary text, `color-mix(in srgb, var(--accent) 14%, var(--surface))` for a light accent). A value the owner wants that no role gives is declared in `config.yaml` under `design.exceptions` (`NAME: VALUE`) and listed in the provenance report:

| Name | Value | Why the design does not give it |
|------|-------|---------------------------------|
|      |       |                                 |

### Migration map (renaming an older deck onto the contract)

| Old deck token | Contract role |
|----------------|---------------|
| `--bg`         | `--canvas-bg`  |
| `--text`       | `--ink`        |
| `--card-bg`    | `--surface`    |
| `--font-sans`  | `--font-body`  |
| `--danger-lt`  | `color-mix(in srgb, var(--danger) 14%, var(--surface))` |
| `--dim` / `--accent-lt` / extended | a role, or a declared exception |

---

## 3. Typography

The font roles (`--font-body`, `--font-heading`, `--font-mono`), the title size and, when the design provides the `type` module, the type scale come from the design; so do the font faces (its `@font-face` rules, inlined by `build.py`; no network font link is emitted). A new typeface goes in the project design, not here.

### Deck type usage

| Element              | Role (font)  | Size role or value | Notes |
|----------------------|--------------|--------------------|-------|
| Hero title           | heading      |                    |       |
| Content slide title  | heading      |                    |       |
| Body text            | body         |                    |       |
| Card label           | body         |                    |       |
| Card sublabel / meta | mono         |                    |       |

---

## 4. Canvas

The canvas is the design's slide frame: `--slide-width` by `--slide-height` (960x540 in the base theme), background `--slide-bg`. Set `canvas:` in `config.yaml` only to give this one deck another size.

_Document mode (`mode: document`): replace this section with the page geometry (size, orientation, margins) from `config.yaml`'s `page:` block and the print measure (page width minus side margins)._

---

## 5. Layout & Spacing

The frame places the section label (`.slide-label`, top left) and the footer row (logo, legal line, slide number, bottom). Content sits between them.

### Content regions

| Region               | Position                          |
|----------------------|-----------------------------------|
| Slide title          | `top: ___; left: ___;`            |
| Content area start   | `top: ___;` (below title)         |
| Content area padding | `left: ___; right: ___;`          |

### Spacing

Use the design's spacing roles (`--space-sm`, `--space-md`, `--space-lg`, and `--space-xs`, `--space-xl` when it provides `space-shape`).

| Context                  | Role or value |
|--------------------------|---------------|
| Card gap                 |               |
| Grid gap                 |               |
| Title to content         |               |

---

## 6. Iconography

### Icon Library

| Property   | Value                                     |
|------------|-------------------------------------------|
| Library    | (e.g. Lucide, Feather, Heroicons, custom) |
| CDN URL    |                                           |
| Init call  | (e.g. `lucide.createIcons()`)             |

### Icon Usage Rules

- Colouring: (inherit from parent / a role)
- Default stroke width:
- Size ranges: (small / medium / large with px values)
- Usage in HTML: (e.g. `<i data-lucide="name"></i>`)
- What to avoid: (e.g. no emoji as primary icons, no mixing libraries)

---

## 7. Reusable Atoms

_The frame already styles `.slide`, `.slide-label`, the footer row and `.slide-source-bar`. Define here the deck's own small building blocks, with roles only._

### Slide Title

```css
.slide-title {
  /* fill in */
}
```

### Accent Line

```css
.accent-line {
  /* fill in */
}
```

---

## 8. Component Library

_For each component: name, purpose, HTML structure, variant classes._

### Component: (Name)

**Purpose**: ...

**HTML**:
```html
<!-- structure -->
```

**Variants**: (list variant classes and what they change)

**Rules**: (any constraints on usage)

---

_(Copy the component block above for each component. Common components:
info card, pain/problem card, numbered list, data table, flow lane,
hub/satellite diagram, status card, tag/badge, comparison columns, timeline.)_

---

## 9. Link Styling

| State   | Style                                          |
|---------|-------------------------------------------------|
| Default |                                                 |
| Hover   |                                                 |
| Target  | (e.g. `target="_blank"` on all external links)  |

---

## 10. Presentation Mode

_Document mode has none: write "N/A (document mode)"._

| Property            | Value                                    |
|---------------------|------------------------------------------|
| Navigation keys     |                                          |
| Enter key           |                                          |
| Exit key            |                                          |

---

## 11. Do / Don't Rules

### Do

- ...

### Don't

- ...

---

## 12. Checklist

- [ ] No colour, font family or custom property outside the contract in `styles.css`; any deck-local value is a declared exception in `config.yaml`
- [ ] Every component in section 8 is implemented in `design/styles.css` with roles only
- [ ] The build prints PASS and the provenance names the intended design
