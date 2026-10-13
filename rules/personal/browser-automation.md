---
type: rule
---

# Browser automation

## Prefer Playwright over Puppeteer

When a task needs headless/scripted browser automation (clicking UI, driving a deployed page, E2E-style checks), reach for **Playwright**, not Puppeteer.

**How to apply:** `npm i playwright`, then `chromium.launch({ executablePath: "/usr/bin/chromium", args: ["--no-sandbox", "--disable-setuid-sandbox"] })` to drive an already-installed system Chromium without downloading Playwright's bundled browsers. Use role-based locators (`page.getByRole("button", { name: "…" })`) over raw DOM queries. For throwaway one-off automation, install into a temp dir (e.g. `/tmp/…`) so the project's dependencies stay clean.

**Why:** stated preference — when offered Puppeteer the answer was "why not use playwright?". Default to Playwright unless the repo already standardises on something else.
