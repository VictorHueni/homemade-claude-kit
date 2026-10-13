---
type: rule
---

# A direct-importer grep is not a reachability proof

## "Who names this file" and "is this file loaded when X runs" are different questions

Before adding an import-time side effect to a module — a poison marker like `server-only`, a top-level env assertion, a connection opened at module scope, anything that throws or acts when the file is *loaded* — the question that matters is whether the module is in the **transitive import closure** of each entry point (app server, app client bundle, CLI, worker, test runner). A grep for direct importers (`grep -rln 'from ".*<file>"'`) answers a strictly weaker question: who names the file by path. The two diverge exactly when a *sibling* file inside an already-reachable feature is the one doing the reaching — the entry point never names the guarded file, but loads a neighbour that does.

Measured case: a plan asserted two modules were safe to guard with `server-only` because "no importer outside their own feature" (direct grep, recorded as *verified*). A CLI reached both anyway, three hops deep, through a cross-feature static import chain (entry → composition root A → query file in A → reads file in B → composition root B). The guard killed every CLI subcommand at import time. The claim's grep was true; the conclusion drawn from it was false. The reviewer had even raised the reachability question explicitly — then closed it with the same insufficient instrument.

**How to apply:** to prove non-reachability, walk the closure from the entry point, not toward the file: run the entry point with the change in place (a smoke test in the gate — cheapest and authoritative), or trace with a bundler/`madge`-style dependency-graph tool, or at minimum iterate the grep transitively until fixpoint. When a plan schedules an import-time side effect for module M, the increment's test gate must **execute every entry point** that could plausibly load M — a build and a unit suite do not exercise a CLI's resolution context. Write reachability claims with the instrument named ("no direct importer outside the feature, per grep" — not "not reachable"), so the next reader knows what was actually proven.

**Sibling trap, same family:** packages with `react-server`-conditional exports (`server-only` and friends) behave differently per resolution context — inert in a Next server bundle, a build error in a client bundle, a **runtime throw in plain Node/tsx**. A gate that only builds the app has never tested the third context; a plain-Node CLI sharing the app's module graph is exactly where the throw lands.

**Why:** the failure is a confident false negative — the grep returns empty, "verified" gets written down, and every app-side gate stays green because the app *is* safe; only the unexercised entry point breaks. **Anti-pattern in self:** answering a transitive-closure question with a single-hop instrument because the single-hop command is the one that fits in a grep.
