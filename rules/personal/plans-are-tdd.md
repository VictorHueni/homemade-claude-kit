---
type: rule
---

# Implementation plans are test-driven, not merely test-gated

Stated preference (2026-09-02, reviewing an exec plan whose increments listed tests next to the implementation and closed with a gate): "does the plan is TDD?" — the answer was no, and the fix was requested immediately.

A test gate at the end of an increment proves tests exist before the commit; it does not stop an agent from building first and writing tests that mirror what it built. The owner wants **red before green**.

**How to apply (every `plan-implementation` output):**

1. In each increment's Scope, the tests are **item 1**, prefixed `**Write first, expect red:**`, naming the concrete cases; implementation items follow.
2. A delivery rule states: tests named in Scope are written first and observed failing before the implementation lands; the iteration's `progress.txt` entry records the red run (failing test names) and then the green run; an increment whose tests were written after its code is not done.
3. Exemptions are explicit in Scope, never implicit: pure layout/styling with no logic, and browser or e2e checks (acceptance gates, written alongside the code).
4. Principle 2 of the plan ("every increment has an executable test gate") names the rule so the Ralph iteration agent sees it in the header, not only in the delivery rules.

**Why:** the plan is the only instruction a fresh-context iteration agent gets; if the plan does not order the tests first, the agent will not. Ordering is free at planning time and unrecoverable after the commit.
