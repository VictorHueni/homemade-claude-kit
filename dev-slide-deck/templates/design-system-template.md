# Design System Definition

> **This document must be completed before building any slides.**
> Every section is required. The build process and all slide authoring
> decisions depend on the tokens, components, and rules defined here.
> Copy this template to `design-system.md` in the same folder and fill
> every section. Leave nothing as a placeholder.

---

## 1. Design Philosophy

_Describe the visual identity in 2-3 sentences. What feeling should the
presentation convey? What principles guide layout and decoration choices?_

**Name**: (give the design system a short name)

**Principles** (list 3-5):

1. ...
2. ...
3. ...

---

## 2. Color Tokens

Define every color as a CSS custom property on `:root`. No hardcoded hex
values should appear anywhere else in the stylesheet.

### Core Palette

| Token         | Hex Value | Usage                                      |
|---------------|-----------|---------------------------------------------|
| `--bg`        |           | Slide background                            |
| `--text`      |           | Primary text color                          |
| `--muted`     |           | Secondary text (descriptions, body)         |
| `--dim`       |           | Tertiary text (timestamps, meta, captions)  |
| `--border`    |           | Card borders, dividers, separators          |
| `--accent`    |           | Primary accent (CTAs, highlights, labels)   |
| `--accent-lt` |           | Light accent (backgrounds, hover states)    |
| `--card-bg`   |           | Card and cell background                    |

### Semantic Colors (optional, add rows as needed)

| Token         | Hex Value | Usage                                      |
|---------------|-----------|---------------------------------------------|
| `--success`   |           | Positive / done / green states              |
| `--warning`   |           | Caution / in-progress states                |
| `--danger`    |           | Negative / error / problem states           |
| `--danger-lt` |           | Light danger background                     |

### Extended Palette (optional, for multi-level or multi-category systems)

_If the deck uses color to distinguish levels, categories, or columns,
define each named color here._

| Name   | Hex Value | Usage                          |
|--------|-----------|--------------------------------|
|        |           |                                |

---

## 3. Typography

### Font Stack

| Token            | Font Family + Fallback           | Usage                     |
|------------------|----------------------------------|---------------------------|
| `--font-heading` |                                  | Titles, hero text, h1-h2  |
| `--font-body`    |                                  | Body text, labels, cards  |
| `--font-mono`    |                                  | Code, tags, metadata      |

### Font Loading

_Specify how fonts are loaded (Google Fonts CDN, self-hosted, system fonts).
Include the exact URL or @font-face declarations needed._

```
(font loading URL or method)
```

### Type Scale

| Element              | Font    | Size  | Weight | Line-Height | Letter-Spacing |
|----------------------|---------|-------|--------|-------------|----------------|
| Hero title           | heading |       |        |             |                |
| Content slide title  | heading |       |        |             |                |
| Section label        | mono    |       |        |             |                |
| Body text            | body    |       |        |             |                |
| Card label           | body    |       |        |             |                |
| Card sublabel / meta | mono    |       |        |             |                |
| Slide number         | mono    |       |        |             |                |

---

## 4. Canvas

| Property     | Value | Notes                                  |
|--------------|-------|----------------------------------------|
| Width        |       | in px                                  |
| Height       |       | in px (should produce 16:9 ratio)      |
| Background   |       | CSS token reference                    |
| Overflow     |       | typically `hidden`                     |
| Positioning  |       | `relative` (children use absolute)     |

---

## 5. Layout & Spacing

### Standard Regions

_Define the typical content zones within a slide._

| Region               | Position                          |
|----------------------|-----------------------------------|
| Section label        | `top: ___; left: ___;`            |
| Slide title          | `top: ___; left: ___;`            |
| Content area start   | `top: ___;` (below title)         |
| Content area padding | `left: ___; right: ___;`          |
| Slide number         | `bottom: ___; right: ___;`        |

### Spacing Scale

| Context                  | Value  |
|--------------------------|--------|
| Card gap                 |        |
| Grid gap                 |        |
| Section label to title   |        |
| Title to content         |        |
| Bottom margin (numbers)  |        |

---

## 6. Iconography

### Icon Library

| Property   | Value                                     |
|------------|-------------------------------------------|
| Library    | (e.g. Lucide, Feather, Heroicons, custom) |
| CDN URL    |                                           |
| Init call  | (e.g. `lucide.createIcons()`)             |

### Icon Usage Rules

_Define how icons are used across the deck:_

- Coloring: (monochrome / colored / inherit from parent)
- Default stroke width:
- Size ranges: (small / medium / large with px values)
- Usage in HTML: (e.g. `<i data-lucide="name"></i>`)
- What to avoid: (e.g. no emoji as primary icons, no mixing libraries)

---

## 7. Reusable Atoms

_Define the small, repeated building blocks. For each atom, provide
the CSS class name, a short description, and the CSS declaration._

### Section Label

```css
.section-label {
  /* fill in */
}
```

### Slide Title

```css
.slide-title {
  /* fill in */
}
```

### Accent Line

_Horizontal bar for visual separation._

```css
.accent-line {
  /* fill in */
}
```

### Accent Bar Left

_Full-height left edge bar on hero slides (if used)._

```css
.accent-bar-left {
  /* fill in */
}
```

### Dot Grid / Decorative Element

_Any decorative texture element (dots, lines, shapes). Remove if unused._

```css
.dot-grid {
  /* fill in */
}
```

### Slide Number

```css
.slide-number {
  /* fill in */
}
```

---

## 8. Component Library

_Define every reusable component pattern available for slide authors.
For each component, provide: name, purpose, HTML structure, and any
variant classes._

### Component: (Name)

**Purpose**: ...

**HTML**:
```html
<!-- structure -->
```

**Variants**: (list variant classes and what they change)

**Rules**: (any constraints on usage)

---

_(Copy the component block above for each component in the system.
Common components include: info card, pain/problem card, numbered list,
data table, flow lane, hub/satellite diagram, status card, tag/badge,
comparison columns, timeline, maturity ring, etc.)_

---

## 9. Link Styling

| State   | Style                                          |
|---------|-------------------------------------------------|
| Default |                                                 |
| Hover   |                                                 |
| Target  | (e.g. `target="_blank"` on all external links)  |

---

## 10. Presentation Mode

_Define the behavior when the deck enters fullscreen/presentation mode._

| Property            | Value                                    |
|---------------------|------------------------------------------|
| Background          |                                          |
| Scaling method      | (e.g. `transform: scale()` proportional) |
| Navigation keys     |                                          |
| Enter key           |                                          |
| Exit key            |                                          |
| Fullscreen API      | (yes / no)                               |

---

## 11. Do / Don't Rules

### Do

- ...
- ...
- ...

### Don't

- ...
- ...
- ...

---

## 12. Checklist Before Building

Before creating any slides, confirm all of the following are true:

- [ ] Every color token in section 2 has a hex value
- [ ] Every font in section 3 has a family, fallback, and loading method
- [ ] The type scale in section 3 is fully filled in
- [ ] Canvas dimensions in section 4 are set
- [ ] At least the section label, slide title, and slide number atoms are defined
- [ ] At least one component is documented in section 8
- [ ] Icon library is specified with CDN URL and init call
- [ ] Presentation mode behavior is documented
- [ ] `design/styles.css` contains the CSS implementing all tokens and atoms above
