---
type: rule
paths:
  - "**/*.vue"
  - "**/nuxt.config.*"
  - "**/composables/**"
  - "**/utils/**"
  - "**/e2e/**"
---

# Frontend (Nuxt UI 4 / Vue 3.5 / Reka UI)

**Components.** Prefer Nuxt UI built-ins (`UAccordion`, `UTable`, `UPagination`, `USlideover`, `UInput`, `UBadge`, `UCard`, `UButton`) and compose them for domain layouts rather than replacing them. `UButton` with `to` renders a link, without it a button: in E2E tests use `getByRole('link')` and `getByRole('button')` accordingly.

**Hydration.** Fix a hydration problem at its source; `<ClientOnly>` is a last resort, and the project's frontend guide decides when it applies. When you use it, give it a `#fallback`: a disabled clone for an interactive widget (no layout shift), the default content as static HTML for a content-heavy section (keeps SEO and LCP; Nuxt UI's `ColorModeSwitch.vue` is the pattern). Non-interactive components (`UBadge`, `UCard`, `UIcon`) never need it.

**Events.** `UInput @focus` / `@blur` are unreliable during hydration and Playwright `fill()`. Use `@focusin` / `@focusout` on a wrapper and check `relatedTarget` with `contains()`.

**Routes.** A localised URL goes on an English-named page file: `definePageMeta({ path: '/localised-route' })`.

**Error pages.** `clearError({ redirect })` does not navigate in dev while the DevTools overlay is active: E2E tests assert the button there, and navigation only against a production build (`npm run build && npm run preview`).

**SSR-safe formatting.** No `toLocaleString()` or `Intl` formatters in SSR-rendered templates: Node and browser ICU data differ (a `U+2019` versus `U+0027` thousands separator, a silent fallback to `en`) and cause hydration mismatches. Use a deterministic formatter for one locale (insert `U+2019` directly), `@nuxtjs/i18n`'s `useI18n().n()` for several; `data-allow-mismatch="text"` silences the warning but still flashes.
