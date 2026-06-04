---
title: GitHub Open-Items Backend Stays Opt-In (Decline to Generalise)
status: active
owner: Victor Hueni
last_reviewed: 2026-06-04
review_interval: 180d
---

# GitHub Open-Items Backend Stays Opt-In (Decline to Generalise)

Date: 2026-06-04

## Context and Problem Statement

[ADR-0002](adr-0002-open-items-pluggable-backend-github-issues.md) introduced a pluggable
open-items central-plane backend (`markdown` | `github`) and adopted `github` for the kit
repo only, deferring one decision — tracked as `OI-0032` and migrated to issue
[#36](https://github.com/VictorHueni/homemade-claude-kit/issues/36):

> Should the `github` backend become the **universal contract** — the default every
> scaffolded project inherits — or stay an opt-in backend?

The kit has since dogfooded the backend: a one-way Mode 7 migration cut the kit's own ledger
over to GitHub Issues (33 issues + structural closure, backend-aware audit). This ADR records
the resulting decision and closes #36.

## Decision Drivers

- **Domain-agnostic portability** — ADR-0002 Driver #1, and the kit's founding premise: it
  scaffolds into GitHub, GitLab, Gitea, local-only, air-gapped, and no-remote projects.
- **What the cutover revealed** — the `github` backend hard-requires GitHub + `gh` auth +
  network, and needed per-repo adaptation (Issue Types are org-level → `type:` label
  fallback; ledger `owner` ≠ GitHub login → mapping; label/Project bootstrap). Fine for an
  opt-in; wrong as a forced default.
- **The pluggable design already delivers the value** — any GitHub-hosted project can adopt
  the (now-validated) backend without it being universal.

## Considered Options

1. **Decline — keep `github` opt-in (chosen).** `markdown` remains the universal default and
   the only universally-required backend; `github` is a fully-supported, validated opt-in.
2. **Generalise — make `github` the universal/default contract.** Simplest single story, but
   hard-requires GitHub for every project and breaks the domain-agnostic premise.
3. **Keep deferred.** Leave #36 open pending a longer operating period. Rejected: the
   universal-contract question is answered by the founding premise regardless of how pleasant
   the GitHub experience turns out to be.

## Decision Outcome

Chosen option: **Option 1 — decline to generalise.** `markdown` stays the universal default;
`github` is a proven, opt-in backend selected per project via `backend.yml`. The governance
contract (`rules/open-items-governance.md` §5.3) is unchanged — it already frames `github` as
an alternative backend, not the default — so no rewrite is needed.

This **extends** ADR-0002 (it answers its deferred sub-question); it does not supersede it.

A separate, softer question — *should we actively recommend the `github` backend, or teach
`util-metamodel-scaffold` to offer it?* — is **not** decided here. It genuinely benefits from
an operating period on the kit and can be raised as its own item later. It is distinct from
the universal-contract question settled above.

### Positive Consequences

- The kit stays portable to any project type; no new hard dependency is imposed on anyone.
- `github` is now an evidence-backed option, not a speculative one.

### Negative Consequences

- Two backends remain to maintain (already true since ADR-0002).
- The kit itself now runs on `github` while the default for scaffolded projects is
  `markdown` — contributors must read `backend.yml` to know which surface is live. Mitigated
  by the migration banner in `open-items.md` and §5.3.

## Open Items

None at present.
