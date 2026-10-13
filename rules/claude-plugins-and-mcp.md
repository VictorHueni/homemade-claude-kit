---
type: rule
---

# Claude Code plugins and MCP servers

**Refreshing a plugin takes two commands.** `claude plugin marketplace update <marketplace>` refreshes the catalog only; `claude plugin update <plugin>@<marketplace>` pulls the new content into the version-keyed cache (use the exact `plugin@marketplace` form `claude plugin list` shows; the bare name fails with `not found`). It only moves if the plugin's `plugin.json` version was bumped; otherwise it reports "already up to date". Check `ls ~/.claude/plugins/cache/<marketplace>/<plugin>/`, then start a new session: a running session keeps what it loaded.

**Pin every MCP server to an exact version** in its `.mcp.json` (never `@latest`), and bump the plugin version in the same commit, or the cache keeps serving the old file. Servers start once per session, so a new pin needs the refresh above and a new session; confirm with a grep of the cached `.mcp.json`, not the source repo, which disagree until then.

**A remote MCP server answering `Unrecognized client_id`** (`claude mcp list` shows `Needs authentication`) has dropped its cached OAuth registration. Run `claude mcp logout <server>`, then reconnect through `/mcp` in an interactive session (`claude mcp login` fails without a terminal). If it persists, the fault is server-side; use the provider's CLI or API meanwhile.
