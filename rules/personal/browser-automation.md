---
type: rule
---

# Prefer Playwright over Puppeteer

For scripted browser automation use Playwright unless the repo already standardises on another tool. `npm i playwright`, then drive the system Chromium without downloading bundled browsers: `chromium.launch({ executablePath: "/usr/bin/chromium", args: ["--no-sandbox", "--disable-setuid-sandbox"] })`. Use role-based locators, and install throwaway scripts into a temp directory, not the project.
