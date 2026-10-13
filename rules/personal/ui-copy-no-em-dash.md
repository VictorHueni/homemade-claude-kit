---
type: rule
---

# No em dash in user-facing copy

Stated preference (2026-09-02, after seeing it across toasts, subtitles and help text): no em dash (`—`) anywhere in text the end user reads. This covers i18n message catalogues, hardcoded JSX strings, email templates, and placeholder/example text.

**How to rewrite:** pick the punctuation that matches how the two clauses relate rather than a blanket substitute. A second clause with its own subject becomes a new sentence. An elliptical continuation ("Centre créé — disponible immédiatement…") takes a comma. A definition or list lead-in takes a colon. Two balanced independent clauses take a semicolon. A short label pairing (a title + qualifier, an option + its date) uses a middle dot `·`, if the project already uses that separator.

**Out of scope:** the em dash used as an empty-value placeholder (`contactEmail ?? "—"`, a table's "no data" cell) is a different idiom and stays unless the owner says otherwise. Code comments and internal error strings are not user-facing copy.

**Why:** dash-joined clauses read as machine-written filler; the owner wants copy that reads like a careful human wrote it. Doing the rewrite once across ~90 strings was cheap; catching them one at a time in review is not, so write them right the first time.
