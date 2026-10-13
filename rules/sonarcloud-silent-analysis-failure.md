---
type: rule
paths:
  - "**/sonar-project.properties"
  - "**/.sonarcloud.properties"
  - "**/.github/workflows/*sonar*"
---

# SonarCloud numbers that look stale

A green scanner step only means the report was uploaded; the analysis can still fail server-side. When Sonar numbers look stale or frozen, run the `ops-sonarcloud-audit` skill before changing any Sonar configuration.
