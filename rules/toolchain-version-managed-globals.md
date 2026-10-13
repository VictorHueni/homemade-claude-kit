---
type: rule
---

# A declared CLI tool missing from PATH was usually installed under an older runtime

`npm -g`, `pip install --user` and `gem install` install into the active runtime version's directory, and a floating pin (`node = "24"`) rolls forward and hides them. Before concluding a tool was never installed, list the globals per installed version (`ls ~/.local/share/mise/installs/node/*/lib/node_modules`). Execute a shim before trusting it (`No version is set for shim` means an orphan), and check whether the shims directory is on `PATH` at all.

A runtime bump changes no script content, so chezmoi's `run_onchange_` installer never re-fires. Run that one script (`chezmoi execute-template < run_onchange_install-X.sh.tmpl | bash`), never `chezmoi apply --force`, which re-runs every script. Use the `npm`/`node` on `PATH` rather than `mise exec`, which can resolve an unrelated (on WSL, Windows-side) config; never `trust` an unfamiliar config to get past an error. Prefer exact runtime pins, and after reinstalling run the project's lint gate to catch a shadowed duplicate.
