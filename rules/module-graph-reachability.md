---
type: rule
---

# A direct-importer grep is not a reachability proof

Before adding an import-time side effect to a module (`server-only`, a top-level assertion, a connection at module scope), prove it is outside the import closure of every entry point that must not load it: app server, client bundle, CLI, worker, test runner. A direct-importer grep only shows who names the file; a sibling can reach it several hops deep. Prove it by running each entry point with the change in place, with a dependency-graph tool, or by repeating the grep until nothing new turns up, and name the instrument in the claim. A plan adding such a side effect puts an entry-point run in its gate; a build or unit suite is not one. `server-only` is inert in a Next server bundle but throws at runtime in plain Node or tsx.
