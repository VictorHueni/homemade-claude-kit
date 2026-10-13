---
type: rule
paths:
  - "**/i18n/**"
  - "**/locales/**"
  - "**/lang/**"
  - "**/messages/**"
  - "**/composables/**"
  - "**/stores/**"
  - "**/templates/**"
  - "**/*.vue"
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/*.html"
  - "**/*.po"
---

# No em dash in user-facing copy

No em dash (`—`) in text the end user reads: message catalogues, UI strings, toasts, email and auth templates, placeholder and example text. Rewrite by how the clauses relate: a new sentence when the second clause has its own subject, a comma for a continuation, a colon for a definition or list lead-in, a semicolon for two balanced clauses, a middle dot `·` for a label pairing if the project already uses it. Out of scope: an em dash as an empty-value placeholder, code comments, internal error strings.
