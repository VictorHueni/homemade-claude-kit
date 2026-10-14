---
type: llm
focus:
  source: file
  path: docs/release-notes/v0.3.0.md
---

PASS if the note is written for a non-technical management reader: plain language, benefit first, each item saying what changed for customers or staff rather than naming code areas.
PASS if it covers the three v0.3.0 features and the calendar fix, and does not present the v0.2.0 entry as new.
PASS if the dependency bump and the CI cache are left out or grouped in a short platform or engineering section, not given the same weight as the features.
FAIL if it reads as a reformatted changelog (scopes in bold such as **booking:**, pull-request numbers as the main content, commit hashes).
FAIL if it invents figures, dates or features that are not in CHANGELOG.md.
