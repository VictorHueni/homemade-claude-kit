---
name: ops-sonarcloud-audit
license: MIT
description: "Diagnose SonarCloud numbers that look stale, frozen or wrong while CI stays green: a server-side analysis failure, the LOC quota, or coverage missing on branch scans. Use before touching any Sonar configuration when the dashboard disagrees with recent commits. Triggers on: sonar numbers stale, sonarcloud not updating, sonar coverage 0, sonar quota, sonar analysis frozen. Complements SonarSource's official sonarqube plugin: not for quality gate, coverage, issue or duplication reports, which its sonar-* skills cover once the numbers are known to be current."
user-invocable: true
metadata:
  category: "operations"
  complexity: "low"
  version: "1.0.0"
  status: active
  last_reviewed: 2026-10-13
  review_interval: 180d
  impact: "low"
---

# SonarCloud: failing server-side behind a green CI

The scanner's exit 0 and `ANALYSIS SUCCESSFUL` only mean the report was uploaded. The analysis runs later as a Compute Engine task, and it can fail there. Check that task before touching any configuration, and before trusting what the official `sonar-*` skills report: they read the last stored analysis.

Use SonarSource's CLI, which carries its own login: `sonar api get "<endpoint>"`. If `sonar` is missing or unauthenticated, run the official plugin's `sonar-integrate` skill first. Without the CLI, call the same endpoints with `Authorization: Bearer <user token>`.

## 1. Read the Compute Engine task

- The scanner log's last line holds an `api/ce/task?id=…` URL: `sonar api get "/api/ce/task?id=<id>"`. Without a log, list recent tasks with `sonar api get "/api/ce/activity?component=<projectKey>"`, or use Administration → Background Tasks.
- An anonymous call to a private project answers "Project doesn't exist", which says nothing about the project.
- `status` `FAILED` with an `errorMessage` is the answer; fix that, not the scanner config.

## 2. Probe freshness

Ask for a file added in a recent commit: `sonar api get "/api/components/show?component=<projectKey>:<path>"`, plus `&branch=<name>` or `&pullRequest=<id>` for anything but the main branch. "Not found" means the stored analysis is stale, whatever the dashboard date says.

## 3. Check the LOC quota

- The quota counts `sonar.sources` only, never `sonar.tests`; Vue single-file components bill as `js`.
- Pull-request analyses skip the quota. PR decoration working while branch data is frozen points to it.

## 4. Coverage at 0 on branch scans

A branch scan with `new_coverage = 0.0` while PR scans have coverage: check whether the CI step that downloads the coverage report runs only on pull-request events.
