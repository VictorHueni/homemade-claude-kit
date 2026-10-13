---
title: Rules Single Authoring Surface and Shared/Personal Layers
status: active
owner: Victor Hueni
last_reviewed: 2026-10-13
review_interval: 180d
---

# Rules Single Authoring Surface and Shared/Personal Layers

Date: 2026-10-13

## Context and Problem Statement

`install.sh` links `rules/*.md` into `~/.claude/rules/`. An audit of the owner's machine on 2026-10-13 found 39 files there: 17 links into the kit and 22 plain files that existed on that machine only, in no repository. The global `~/.claude/CLAUDE.md` was in no repository either.

The drift had one cause: the memory-hygiene instruction in the global `CLAUDE.md` told the agent to write cross-project lessons to `~/.claude/rules/<topic>.md`. Every session that followed it created a rule the kit never saw. One of them (`python-extras.md`) had been removed from the kit as too specific and came back that way.

The kit also had no way to separate rules meant for anyone who installs it from the owner's own preferences and machine notes, which matters once a teammate runs the same installer. The kit repository is public.

## Decision Drivers

- One source of truth per fact (ADR-0006): a rule exists in exactly one versioned place.
- A teammate's install must not inherit the owner's preferences or machine-specific workarounds.
- The installer stays idempotent and never loses a local edit silently.
- Claude Code plugins cannot ship rules (only skills, agents, hooks, MCP and LSP servers, commands), so the installer remains the rule channel.

## Considered Options

1. **Kit `rules/` plus an opt-in `rules/personal/` layer, both linked flat** (chosen).
2. **Personal rules in the private dotfiles repo** (`dot_claude/rules/`). Fully private, but two places to author rules and two install paths to keep consistent.
3. **Status quo.** Fails the first driver; the drift recurs.

## Decision Outcome

Chosen option 1.

1. **Every rule is authored in the kit.** `~/.claude/rules/` holds only links managed by `install.sh`. A plain file there is a defect, reported as blocking by `util-toolkit-doctor`.
2. **Two layers.** `rules/` holds shared engineering rules, installed for everyone. `rules/personal/` holds the owner's preferences and this machine's setup, installed only after `./install.sh --personal-rules on`, persisted per machine in `var/personal-rules` (default off). Both layers link flat into the same target, so a file name may exist in one layer only; the installer refuses a collision.
3. **Pruning is exact.** A link is pruned only when it resolves to a file directly inside the layer directory being synced, so the shared layer never prunes personal links and turning the personal layer off removes exactly its links.
4. **The global `CLAUDE.md` moves into rules.** Its preferences become `rules/personal/preferences.md`; memory hygiene becomes the shared `rules/memory-hygiene.md`, which now points new lessons at the kit. `~/.claude/CLAUDE.md` is no longer needed.
5. **ADR-0006's rule count is superseded** by the README's Rules tables, which list both layers.

### Positive Consequences

- A new lesson lands in a versioned, reviewable place and reaches every machine through the existing chezmoi hook.
- A teammate gets the shared layer only, with no change to their install command.
- The installer behaviour is covered by `scripts/test-install-rules.sh`.

### Negative Consequences

- Personal rules are public, because the kit repository is. Each one gets a privacy read before it is committed.
- Rule links point into the working checkout, so an uncommitted rule edit is live in every session on the machine at once.

## Open Items

- Rule content is unchanged by this decision; trimming incident narrative and moving rare gotchas into skills or hooks is follow-up work.
