"""Skip-or-fail gate for tests that need Playwright and Chromium."""
import os
import unittest


def browser_available():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            return os.path.exists(p.chromium.executable_path)
    except Exception:  # noqa: BLE001 — any failure means no usable browser
        return False


def require_browser(case):
    """Skip locally; in CI (CI=true) a missing browser is an error, not a skip."""
    if browser_available():
        return
    if os.environ.get("CI") == "true":
        case.fail("Playwright and Chromium are required in CI and are missing")
    case.skipTest("Playwright or Chromium missing: pip install playwright && python -m playwright install chromium")
