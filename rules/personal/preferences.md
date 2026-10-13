---
type: rule
---

# Personal preferences

- **Naming**: prefer consistent suffix-based file naming across packages within a project (Java-style suffix discipline).
- **Code language**: all code artefacts (file names, components, variables, tests) in English; reserve French (and other languages) for user-facing UI content only. For French routes in Nuxt, use `definePageMeta({ path: '/french-route' })` on an English-named page file.
- **Ralph Loop execution**: when I have terminal access, prefer `ralph.sh` (designed for autonomous multi-increment execution with fresh context per iteration). When I do not have terminal access (mobile, remote, cloud), spawn one Agent subagent per increment — never multiple increments per subagent.
