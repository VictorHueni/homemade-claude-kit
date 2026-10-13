---
type: rule
---

# Claude Code plugin marketplace: refreshing is two separate steps, not one

## `marketplace update` refreshes the catalog; `plugin update` materializes a new version

When a plugin's content changes upstream (a skill gets new files, a script, a reference doc) without the marketplace-channel cache picking it up, the instinct is to run `claude plugin marketplace update <name>` and assume that's the fix. It isn't sufficient on its own.

- **`claude plugin marketplace update <marketplace-name>`** refreshes the marketplace's own manifest — the list of plugins and their available versions. It does **not** re-download any individual plugin's content into the version-keyed cache directory (`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`).
- **`claude plugin update <plugin>@<marketplace-name>`** is the separate step that actually pulls the new version's content into the cache. Without it, `~/.claude/plugins/cache/<marketplace>/<plugin>/` keeps only the old version directory, even after `marketplace update` reports success and even after the marketplace's own manifest now lists the newer version.

**Both commands need the `@<marketplace-name>` suffix on the plugin argument** — `claude plugin update <plugin>` alone (no `@marketplace`) fails with `Plugin "<plugin>" not found`, even when `claude plugin list` shows it installed. Use the exact `plugin@marketplace` form the list output itself displays.

Verify the cache directly rather than trusting either command's success message: `ls ~/.claude/plugins/cache/<marketplace>/<plugin>/` should show the new version's directory with the expected new files inside it, not just the old version sitting alone.

## A version bump on the source side is also required

This whole flow only works if the plugin's own `.claude-plugin/plugin.json` `version` field was actually bumped in the source repo when its content changed. The marketplace-channel cache is keyed by version string, not content hash — pushing new file content under an unchanged version number leaves the cache with nothing to invalidate against, and `plugin update` will report "already up to date" even though the source has moved on. See [[skill-creation-sync]] for the authoring-side convention this depends on.

## Even after both steps, the running session doesn't see it

Both commands report "restart required to apply" (or equivalent). A plugin/skill fix landing in the cache does not retroactively change what the current session has already resolved — skills, in particular, may already be loaded into context for this session. Confirm the fix in the cache, then start a **new session** before relying on the updated content; don't try to "force" a live session to pick it up.

**How to apply:** when a kit-side skill/plugin change isn't showing up in a running session despite a source-repo push, check in this order: (1) source repo has the version bump committed and pushed, (2) `~/.claude/plugins/marketplaces/<name>` reflects the current source (or run `marketplace update`), (3) `claude plugin update <plugin>@<marketplace>` — not just `marketplace update` — to materialize the new version into cache, (4) verify the cache directory directly, (5) start a fresh session. Skipping step 3 is the most common miss — it looks like "the marketplace was refreshed" succeeded, but the plugin's own content never moved.

**Why:** the failure is silent in the same way the MCP-server-pin trap is (see `~/.claude/rules/mcp-server-pins-and-schema-drift.md`) — a command that reports success answers a question adjacent to the one that matters, and only inspecting the actual cache directory reveals whether the real fix landed.
