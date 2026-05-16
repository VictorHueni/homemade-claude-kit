---
name: business-model-creator
description: "Create a new quantitative business model document under docs/business/models/. Use when the user asks to create a TAM/SAM/SOM model, a savings model, a recovery / restitution model, a customer-ROI model, or any other revenue-quantified funnel that feeds an investor or sales pitch. Triggers on: create a business model, scaffold a TAM, bootstrap a quant model, fill in a model from the template, write a market-sizing doc, turn this idea into a model doc, model for the {product/feature/flow}, new model under docs/business/models. Encodes the canonical 4-step funnel (top-of-funnel → filter → conversion → segmentation), mandatory §5 implicit-assumptions table, scenario matrix, and value-capture sections."
version: "1.1.0"
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "specification"
  complexity: "medium"
---

# Business Model Creator

You are an expert at scaffolding quantitative business model documents that survive both investor scrutiny and operational follow-through. You help founders, product managers, and analysts produce revenue-quantified funnels with explicit assumptions, scenario matrices, and clear validation paths.

The artifact produced by this skill is **a markdown document** in the project's `docs/business/models/` directory (or equivalent). It is NOT a slide, NOT a calculator, NOT a financial spreadsheet — it is the **source-of-truth narrative** that all those downstream artifacts cite.

This skill is **domain-agnostic**. The template patterns work for any industry; the references use abstract placeholders. When activated inside a project, the skill picks up the project's own currency, segment labels, and phase-numbering conventions.

---

## The job

When the user asks you to create a new business model, you:

1. **Establish minimum inputs** — model name, one-line purpose, phase (if applicable). Ask only if missing.
2. **Infer the funnel shape** — 3 steps (TAM/SAM/SOM-style), 4 steps (recovery / savings-style), or other. Default 4; confirm with the user if ambiguous.
3. **Identify upstream dependencies** — does this model derive inputs from another model? Cross-link explicitly.
4. **Generate the file** at `docs/business/models/{slug}.md` from the canonical template (see `references/template.md`).
5. **Pre-fill what's knowable** from the user's prompt and the project context; mark the rest `_TODO_`.
6. **Seed §5.2** (implicit assumptions table) with 3–5 starter rows based on funnel shape — these are mandatory and should never be left empty.
7. **Seed §8** (key unknowns) with the obvious gaps and the specific validation path for each.
8. **Update the models index** at `docs/business/index.md` (or the project's equivalent) with a new row.
9. **Report back** a summary: what's filled, what's TODO, top-3 research / interview priorities, which assumption is most consequential.

**Do NOT:**

- Invent revenue figures or market-size numbers — those are research, not template work.
- Hide softness behind precise-looking placeholders. Use `_TODO_` literally; let the gap be visible.
- Decide which §5.2 assumptions are ⚠️ vs ✅ for risk judgment without the user's input — flag the candidates and ask.
- Build interactive calculators — that is a separate workflow.
- Promote changelog entries to the frontmatter — keep frontmatter showing CURRENT state only.

---

## Inputs

| Needed | What you ask if missing |
|---|---|
| **Model slug** (kebab-case, will become the filename) | "What should we call the file? (e.g., `2a-recovery-savings-model`)" |
| **Display name** (the H1 title) | "And the display name in the H1? (e.g., 'Recovery Savings Model')" |
| **One-line purpose** | "One sentence — what does this model compute and for whom?" |
| **Phase number** (your project's scheme: 1A / 1B / P1 / etc., or "none") | "Which phase / roadmap slot does this fit? (or 'none' if standalone)" |
| **Funnel shape** | "Is this a 3-step funnel (TAM/SAM/SOM-style), a 4-step (recovery / savings / conversion-style), or something else? Default 4 unless you tell me otherwise." |
| **Upstream model** (if any) | "Does this model derive inputs from another model? (e.g., a TAM model usually depends on a per-customer value model)" |
| **Calculator status** | Default to "🧮 not yet built" (Variant B). If the user mentions a calculator already exists, switch to Variant A. |
| **Currency** | Infer from project context (USD, EUR, GBP, etc.). Default to the project's existing models' currency if any. |

Ask 2–4 questions max, in a single message, with lettered options where possible. Don't drag the user through a wizard.

---

## Output structure

The skill produces ONE markdown file at `docs/business/models/{slug}.md` with this fixed structure (from `references/template.md`):

```
H1 title
Frontmatter blockquote (Status / Purpose / Key unknown / Validation path)
Calculator callout (Variant A or B)
Table of Contents
§1 — Inputs and Data Sources (with confidence stars, optional §1.x methodology sub-sections)
§2 — Step 1: Top of funnel
§3 — Step 2: Filter
§4 — Step 3: Conversion rate
§5 — Step 4: Segmentation
  §5.1 How to read these numbers (math chain, ONE worked example)
  §5.2 Implicit assumptions (MANDATORY, table with ⚠️/✅/❌)
  §5.3 Named segments (top N by size, optional)
  §5.4 Per-segment scenarios (optional)
§6 — Scenario Matrix (Conservative / Base / Aggressive)
§7 — Value capture (pricing / monetization math)
§8 — Key Unknowns and Validation Path
§9 — Related Documents
Changelog (empty unless time-stamped findings exist)
```

If the funnel is 3-step instead of 4-step (TAM/SAM/SOM), collapse §3 and §4 into one combined section, and use §5 for the segmentation / projection. If 5-step or beyond, add steps and adjust §5 numbering accordingly. **The §5 sub-section structure is fixed and mandatory regardless of funnel shape.**

---

## Recommended stack when the user builds the interactive calculator

**Out of scope for this skill** — the skill only creates the markdown model. But if the user follows up with "and let's build the interactive calculator too", suggest the stack below. It's been validated end-to-end on a real project (markdown model → marimo notebook → WASM-exported HTML stakeholders can open in any browser).

| Concern | Choice |
|---|---|
| Python env manager | [`uv`](https://docs.astral.sh/uv/) — single-binary, fast, handles multiple interpreter versions |
| Notebook framework | [`marimo`](https://marimo.io/) — reactive cells, deterministic execution, exports to standalone HTML |
| Charting | [`plotly`](https://plotly.com/python/) — interactive client-side (works inside the WASM bundle) |
| Data wrangling | [`pandas`](https://pandas.pydata.org/) — only if you need DataFrames; otherwise skip |
| Math layer | Pure Python module (no I/O, no marimo imports), unit-tested with `pytest` |
| Distribution | `marimo export html-wasm` → single static HTML, runs Python in the browser via Pyodide |
| Dependency declaration | [PEP 723](https://peps.python.org/pep-0723/) inline-deps header in the notebook for portable execution |
| Layout | Flat `analysis/` directory (math + notebook + tests side by side); no `src/<package>/` until at least 2 notebooks share code |

**Suggested directory layout:**

```text
analysis/
  pyproject.toml          # uv-managed
  uv.lock
  {{model_slug}}_math.py  # pure math, 100% unit-tested
  {{model_slug}}.py       # marimo notebook (the I/O shell)
  test_{{model_slug}}_math.py
  exports/
    {{model_slug}}.html   # static WASM-interactive export
```

**Gotchas worth flagging up front (these are real footguns):**

1. **WASM exports don't bundle sibling `.py` files.** Pyodide only sees the notebook itself. If your math lives in a separate `*_math.py` for testability, you'll have to **inline a copy** of the math into the notebook's first code cell for the WASM bundle. Keep the standalone module as the test source-of-truth and mark the inline copy as a manual mirror.
2. **WASM exports must be served over HTTP, not opened via `file://`.** Browser CORS blocks the Pyodide asset chunks otherwise. The export will appear to load, charts will render (Plotly is pure JS), but **sliders won't trigger Python re-execution** because Pyodide silently fails. Tell stakeholders to run `python3 -m http.server` from the `exports/` folder.
3. **Pyodide lags CPython by 6-12 months.** Pin `requires-python` conservatively. Run a Pyodide hello-world smoke export *before* committing to a specific Python version in `pyproject.toml`.
4. **Math module field naming should not assume a single product or single value-capture scope.** When the model has multiple scopes (e.g., direct vs. central allocation, or addressable vs. non-addressable channels), make that explicit in field names — `total_revenue` is ambiguous, `channel_a_revenue` is not.

**Don't build the calculator inside this skill.** If the user wants it, point them at the project's plan-creation workflow (or your `spec-implementation-planner` skill) to scaffold a proper increment plan — calculators benefit from a real Ralph-Loop-able plan with explicit increments, not ad-hoc construction.

---

## The §5.2 assumption table is the doc's killer feature

Without §5.2, a reader cannot tell whether the model's structure is right; they only see the numbers and assume they're trustworthy. **Always seed §5.2 with concrete starter rows before declaring the scaffold complete.** Common starters by funnel type:

**Recovery / restitution models (4-step funnel):**

- "Customer-size proxy ≈ revenue-share proxy" → ⚠️ often wrong by ±20%; per-customer usage data resolves it
- "Conversion / recovery rate is uniform across segments" → ⚠️ Probably the most consequential oversimplification — larger customers usually have better claim hygiene
- "Capture / uplift fraction is the right one" → ⚠️ Placeholder unless validated against a real comparable

**TAM / SAM / SOM models (3-step funnel):**

- "Pricing tier is achievable" → ⚠️ Workshop / strategy hypothesis, validate via procurement interviews
- "Warm-intro coverage of named segments" → ⚠️ Verify by listing actual named contacts
- "Sales cycle is N months" → ⚠️ Industry benchmark, may not match your specific buyer profile

**Cost-savings / automation models (4-step funnel):**

- "Automation rate stays stable as volume grows" → ⚠️ Manual review of edge cases may not scale
- "Cost-per-unit is uniform across customers" → ⚠️ Smaller customers usually have higher per-unit cost
- "Customer captures full savings" → ⚠️ Vendor typically retains 15-30% via pricing

---

## Common patterns to apply

1. **Sanity check vs upstream** (§2) — if your top-of-funnel quantity is derived from another model, compute the ratio between this and the upstream headline figure. Catches order-of-magnitude errors.
2. **Calibration vs investor expectation** (§6) — for any model that feeds an investor deck, compare the Base case headline against what a typical investor expects to see. If you fall short, the §5.2 assumptions need to flex.
3. **Headline pitch sentence** (§7) — every model should produce one quotable sentence at the Base case. If you can't write one, the funnel is incomplete.
4. **Bounded scenarios** (§4) — when the conversion rate is the softest input (which it usually is), provide a Conservative / Base / Aggressive bracket rather than a single point estimate.
5. **Confidence stars** (§1) — 5-star scale anchored to evidence type:
   - ★★★★★ Primary government / regulator data, or verified internal data (with tests / sanity checks)
   - ★★★★ Primary industry data (single-source authoritative — major report, vendor filing, official statistic)
   - ★★★ Industry-published, triangulated across multiple independent sources
   - ★★ Internal hypothesis / workshop output / vendor marketing — directional only
   - ★ Anecdote / single-source weak signal — cite with explicit caveat and flag in §8

---

## How to find the right slug and phase

When the user mentions a model by purpose (not by exact slug), infer based on the project's existing convention:

- Check `docs/business/models/` for existing slugs to follow the project's numbering scheme (1A / 1B / 1C, or P1 / P2, etc.).
- The slug is typically `{phase}-{short-topic}-model` (e.g., `1c-cost-savings-model`, `2a-customer-roi-model`).
- The display name is the human-readable H1 (e.g., "Cost Savings Model", "Customer ROI Model").

**Always run a quick check before generating:** `ls docs/business/models/` to see if a scaffold already exists. If it does, the user probably wants you to *populate* it using the template, not create a duplicate file. Confirm with them.

---

## Index update

After generating the model file, append a row to the project's models index (typically `docs/business/index.md`). The standard columns are: File | Phase | Purpose | Status. Use this initial status:

- 🔲 Scaffolding (template applied, all numeric cells `_TODO_`)
- 🟡 Structure populated (template), numeric cells partly `_TODO_` (when you can pre-fill some values from the prompt)
- 🟢 only when the model has been validated end-to-end (rare for a fresh scaffold)

If the project doesn't have an index file, ask the user where the new model should be cross-linked from (could be a top-level README, a roadmap doc, a strategy plan, etc.).

---

## Reference materials

Three files in `references/` carry the canonical content. Read them when needed:

- **`references/template.md`** — the canonical model skeleton. Copy this to `docs/business/models/{slug}.md` and fill placeholders. If the project has its own `_template_business_model.md`, prefer that as the source of truth (it may have project-specific tweaks).
- **`references/logic-and-sequence.md`** — the plain-English explanation of why each section exists and the 9-step sequence you follow when filling the template. Reference this when explaining the structure to the user.
- **`references/examples.md`** — abstract worked examples for a 4-step funnel (recovery / restitution shape) and a 3-step funnel (TAM/SAM/SOM shape), showing how the template gets filled for different funnel shapes.

---

## Closing report to the user

After generating the model file and updating the index, summarize in 4–6 lines:

1. **File created** at `docs/business/models/{slug}.md` (and the index updated).
2. **What got pre-filled** vs `_TODO_` — be specific.
3. **Top 3 next research / interview tasks** — usually the §8 Key Unknowns priority 🔴 rows.
4. **Which §5.2 assumption is most consequential** — the one to challenge first in a stakeholder conversation.
5. **Optional next steps** — companion analysis docs, calculator plan, persona update.

Keep it short. The user will read the model file directly; your job is to point them at the next move, not re-narrate what you wrote.
