---
type: llm
focus:
  source: file
  path: docs/release-notes/v0.3.0.md
---

PASS if the note is written for a non-technical management reader: plain language, benefit first, each item saying what changed for customers or staff rather than naming code areas.
PASS if it covers the three v0.3.0 features and the calendar fix, and does not present the v0.2.0 entry as new.
PASS if the dependency bump and the CI cache are left out or grouped in a short platform or engineering section, not given the same weight as the features.
The skill's own format is allowed and is not a reason to fail: items grouped under a plain-language area or capability name (bold or as a lead-in such as "Booking:"), and a short pull-request reference at the end of an item, such as "(#41)", as a citation.
FAIL if it reads as a reformatted changelog: items that keep the commit wording or a conventional-commit scope prefix (`feat(booking):`, `booking:` followed by developer wording), pull-request numbers or commit hashes as the content of an item rather than a trailing citation, or code areas instead of what changed for people.
FAIL if it invents figures, dates or features that are not in CHANGELOG.md.
