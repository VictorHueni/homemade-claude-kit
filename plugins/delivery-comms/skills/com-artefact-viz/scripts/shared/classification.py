#!/usr/bin/env python3
"""A deck's data classification: the closed list of `classification:` levels and their labels per language.

The four levels are a common scheme; Strictly confidential is the level for sensitive personal data (GDPR
Art. 9, nFADP Art. 5 lit. c). The label follows the deck's `lang:`; a language without built-in labels prints
the English one and warns on stderr. Used by com-slide-deck's build.py (the footer row of every slide) and
render.py (the running footer of every document page).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from design_source import DesignError  # noqa: E402

LEVELS = ("Public", "Internal", "Confidential", "Strictly confidential")
LABELS = {
    "en": LEVELS,
    "fr": ("Public", "Interne", "Confidentiel", "Strictement confidentiel"),
    "de": ("Öffentlich", "Intern", "Vertraulich", "Streng vertraulich"),
    "it": ("Pubblico", "Interno", "Confidenziale", "Strettamente confidenziale"),
}


def label(value, lang) -> str:
    """The label of a `classification:` value in the deck's `lang:` (a primary subtag such as `fr-CH` reads as
    `fr`); "" when no classification is set. A value outside the four levels is a DesignError."""
    if value is None or str(value).strip() == "":
        return ""
    wanted = " ".join(str(value).split()).lower()
    level = next((i for i, name in enumerate(LEVELS) if name.lower() == wanted), None)
    if level is None:
        raise DesignError(f"config.yaml classification: {value!r} is not a level; use "
                          + ", ".join(LEVELS[:-1]) + f" or {LEVELS[-1]}")
    primary = str(lang or "en").replace("_", "-").split("-")[0].strip().lower()
    if primary not in LABELS:
        print(f"  [WARN] no classification labels for lang: {lang!r}; the footer prints the English label "
              f"({LEVELS[level]}). Built in: " + ", ".join(LABELS), file=sys.stderr)
        primary = "en"
    return LABELS[primary][level]
