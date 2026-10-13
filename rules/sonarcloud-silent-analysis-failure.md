---
type: rule
---

# SonarCloud can fail server-side behind a green CI

The scanner's exit 0 and `ANALYSIS SUCCESSFUL` only mean the report was uploaded. The analysis runs later as a Compute Engine task. When Sonar numbers look stale or frozen, check that task before touching any configuration: the `api/ce/task?id=…` URL on the log's last line (or Administration → Background Tasks), called with `Authorization: Bearer $SONARQUBE_TOKEN`; an anonymous call to a private project answers "Project doesn't exist". Freshness probe: ask the API for a file added in a recent commit; "not found" means the stored analysis is stale.

The LOC quota counts `sonar.sources` only, never `sonar.tests`, and Vue SFCs bill as `js`. Pull-request analyses skip the quota, so PR decoration working while branch data is frozen points to it. A branch scan with `new_coverage = 0.0`: check whether the coverage download step runs only on pull-request events.
