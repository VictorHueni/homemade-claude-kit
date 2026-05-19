---
name: business-quantitative-model
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

## What a "good quantitative model" means

A model doc is good when a reader can answer, without ambiguity:

| Question | Where it lives |
|---|---|
| **What does this model compute, and for whom?** | Frontmatter blockquote §Purpose |
| **What is the funnel shape?** | §2–§5 section headings + §5.1 math chain |
| **What are the inputs and how confident are we?** | §1 Inputs and Data Sources (confidence stars) |
| **What are the key assumptions that could be wrong?** | §5.2 Implicit assumptions table (⚠️/✅/❌) |
| **What happens in Conservative / Base / Aggressive scenarios?** | §6 Scenario Matrix |
| **What is the headline revenue / savings number?** | §7 Value capture (one quotable sentence) |
| **What do we still not know, and how do we find out?** | §8 Key Unknowns and Validation Path |

---

## The three modes of operation

The skill operates in one of three modes. Detect which mode the user wants from their prompt; ask if ambiguous.

### Mode 1 — Scaffold

**When:** no model file exists yet for this slug.

**Output:** ONE file at `docs/business/models/{slug}.md` from the canonical template — all numeric cells `_TODO_`, structure complete.

Seed §5.2 (implicit assumptions) with 3–5 starter rows matched to the funnel type — this section is mandatory and must never be left empty.
Seed §8 (key unknowns) with the obvious gaps and their validation path.
Update the models index at `docs/business/index.md` (or equivalent) with a new row at status 🔲 Scaffolding.

Do NOT invent revenue figures or market-size numbers in scaffold mode.

### Mode 2 — Fill

**When:** the scaffold exists (or the user wants to create + fill in one pass) and the user has context to populate the funnel.

**Step 0 — Clarifying questions (ask BEFORE generating)**

Ask the user the following 4 questions in a single message with lettered options. Users respond like `1A, 2C, 3B, 4A`:

```text
1. Funnel shape?
   A. 3-step — TAM/SAM/SOM-style (top-of-funnel → filter → conversion)
   B. 4-step — recovery / savings / conversion-style (top-of-funnel → filter → conversion → segmentation) [default]
   C. Other / custom — please describe the steps

2. Phase / roadmap slot?
   A. Standalone (no phase number)
   B. Has a phase number — please name it (e.g., 1A, P2, Phase 3)

3. Upstream model dependency?
   A. Standalone — no inputs derived from another model
   B. Derives inputs from an existing model — please name it

4. Calculator status?
   A. Not yet built — scaffold markdown only [default]
   B. Calculator already exists — I will provide the link
```

If the user gives "Other" or pushes back, ask one follow-up to clarify, then proceed.

**Inputs needed before generating:**

| Needed | What you ask if missing |
|---|---|
| **Model slug** (kebab-case, becomes the filename) | "What should we call the file? (e.g., `2a-recovery-savings-model`)" |
| **Display name** (the H1 title) | "And the human-readable display name?" |
| **One-line purpose** | "One sentence — what does this model compute and for whom?" |
| **Currency** | Infer from project context. Ask if not determinable. |

**Process:**
1. If funnel shape is not 4-step (default), adjust §2–§5 section count accordingly: 3-step collapses §3+§4; 5-step adds a section.
2. Read project context to pre-fill what is knowable from PRDs, personas, BMC, process docs.
3. Fill each funnel section — pre-fill known inputs with confidence stars; mark the rest `_TODO_`.
4. Seed §5.2 with starter assumption rows matched to the funnel type (see §5.2 patterns below).
5. Seed §8 with gaps + specific validation path per gap.
6. Update the models index row to 🟡 Structure populated.

**Do NOT:**
- Invent revenue figures or market-size numbers — those are research, not template work.
- Hide softness behind precise-looking placeholders — use `_TODO_` literally; let the gap be visible.
- Decide which §5.2 assumptions are ⚠️ vs ✅ without the user's input — flag candidates and ask.
- Build interactive calculators — that is a separate workflow.
- Promote changelog entries to the frontmatter — keep frontmatter showing CURRENT state only.

### Mode 3 — Refresh

**When:** new data arrives (interview findings, market research, actuals) and one or more inputs need recalibration.

**Process:**
1. Identify the specific §1 inputs or §5.2 assumptions to update.
2. Update confidence stars where evidence has improved.
3. Recalculate affected funnel steps and scenario matrix.
4. Promote §5.2 rows from ⚠️ to ✅ where the assumption is now validated.
5. Update the models index row status if the model has materially improved.
6. Add a changelog entry: date · what changed · evidence source.

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

**Don't build the calculator inside this skill.** If the user wants it, point them at the project's plan-creation workflow (or your `spec-implementation-plan` skill) to scaffold a proper increment plan — calculators benefit from a real Ralph-Loop-able plan with explicit increments, not ad-hoc construction.

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

## Cross-reference — the 3-layer artifact lifecycle

A model doc is one of three artifact types that together describe a domain operationally:

| Layer | Job | Owns |
|---|---|---|
| **Strategic analysis** | "Why this matters / what could change" | Business case, strategic argument, market-opportunity framing |
| **Process** | "What happens — who, what, how, with what data" | Descriptive walkthrough, actors, activities, data flows, KPIs |
| **Model** *(this skill)* | "How much / how big" | Quantification (TAM, savings, recovery, customer-ROI, etc.) |

### The content-routing rule (one rule)

When you're uncertain where a piece of content belongs, ask three questions in order:

1. **Is it a fact about how things work today?** → process doc. (What exists, who does what, how it's applied, what it produces.)
2. **Is it an argument about why things are this way, or what could change?** → analysis doc. (Why something exists, what it tries to solve, the strategic case for changing it.)
3. **Is it a number that quantifies an opportunity?** → model doc. (Volumes, rates, financial impact, scenario sensitivity.) ← **this is your layer**

**Tie-breaker test:** "Would this still be true if no one ever changed anything?" If yes → it's a fact, process owns it. If no → it's an argument (analysis) or a projection (model).

### What belongs in a model doc

- Volumes, growth rates, conversion rates
- Pricing tiers, value-capture math, headroom analysis
- TAM / SAM / SOM funnel
- Scenario matrix (conservative / base / aggressive)
- Implicit assumptions about market structure
- Per-segment / per-customer / per-tier projections
- Break-even / cost-base analysis
- Validation paths for the model's key unknowns

### What does NOT belong in a model doc

- **The mechanism / process that generates the volume** → process doc owns this (e.g., the workflow that creates the unclaimed-rebate gap; the operational steps that generate the cost the model quantifies)
- **The strategic argument for why the market exists** → analysis doc owns this (e.g., the regulatory or competitive context; the historical reason the opportunity exists; the policy critique)
- **The legal / regulatory mechanism** → process doc owns this (statute citations, ordinance references, official actor responsibilities)
- **The reasoning behind the pricing strategy** → analysis doc owns this (competitive positioning, customer-segment psychology); the *CHF numbers* and headroom math stay in the model

### Abstract worked example — a pricing tier

A "pricing tier offered to customers" gets split cleanly across the three layers:

| Content | Layer | Why |
|---|---|---|
| What the customer receives at each tier (features / volume allowance / SLA) | **Process** | Operational fact: this is what the product delivers |
| How customers consume / interact with each tier in practice | **Process** | Operational fact about current state |
| **Why** the company chose this pricing structure (competitive positioning, customer-segment fit) | **Analysis** | Argument about strategy |
| **Why** a flat-tier vs value-based vs usage-based pricing was selected | **Analysis** | Argument about pricing-model choice |
| The CHF / $ / € amounts per tier | **Model** §1 inputs | Quantification |
| The headroom math (tier price vs implied customer WTP) | **Model** §7 value capture | Quantification |
| Sensitivity to tier-price changes across scenarios | **Model** §6 scenario matrix | Quantification |
| Estimated revenue per segment at each tier | **Model** §5 segmentation | Quantification |

The model doc owns the CHF math and the headroom analysis. The reasoning behind *why* this pricing strategy was chosen lives in the analysis. The customer-facing reality of *what each tier delivers* lives in the process. Each layer is independently complete.

### Soft-reference principle

The layers cross-reference each other *as pointers, not as dependencies*.

- **Each layer is independently complete.** A reader of the model doc should understand the quantification without having to read the analysis or process. Cross-references add depth, not prerequisites.
- **Cross-references are light.** When the model doc mentions a process that generates a volume (e.g., "the process described in {process doc} produces ~N events/year"), the model names it briefly + links — it does not re-explain the process.
- **Linkage is many-to-many, not strict.** A model is typically anchored to one analysis (the strategic argument it quantifies) and may draw volume / rate / KPI inputs from one or more processes. Some standalone models (e.g., headline TAM scoping) may exist before any process is documented — that's fine.
- **Do not block a model on the existence of an analysis or process doc.** If the analysis doesn't exist yet, the model still ships; flag the missing strategic context in §8 Key Unknowns.

### When in doubt — the symptom test

If you're scaffolding a model doc and you find yourself writing:

- "*The way the system works is...*" (descriptive multi-paragraph workflow) → that belongs in process. Reference it; don't replicate it.
- "*Why this opportunity exists in the first place...*" (multi-paragraph strategic context) → analysis. Reference it; don't argue for it inside the model.
- "*The 4-step process for customer X is...*" (operator-level detail) → process.
- "*N customers × CHF Y per customer = CHF Z TAM*" → this is your job.
- "*If we changed Z, the impact would be Y*" (sensitivity analysis) → this is your job.

When the user asks you to produce a model doc but the conversation has been about market mechanics or strategic positioning, gently surface this distinction and confirm they want the quantification layer — and offer to also scaffold the missing process / analysis docs if those gaps are blocking the model.

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

**Never overwrite an existing model file.** Switch modes if it exists:
- Scaffold mode → skip (report what's already there).
- Fill mode → open the existing file and populate empty sections; never regenerate wholesale.
- Refresh mode → targeted updates + changelog entry only.

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

---

## Checklist

Before declaring the work done:

- [ ] Model file exists at `docs/business/models/{slug}.md` (scaffold / fill mode).
- [ ] Funnel shape chosen and §2–§5 section count matches it.
- [ ] §1 Inputs table populated with confidence stars (even if values are `_TODO_`).
- [ ] §5.1 math chain present with ONE worked example.
- [ ] §5.2 Implicit assumptions table has ≥3 rows with ⚠️/✅/❌ ratings.
- [ ] §6 Scenario Matrix has Conservative / Base / Aggressive columns.
- [ ] §7 Value capture has one quotable headline sentence at Base case.
- [ ] §8 Key Unknowns populated with validation paths.
- [ ] Models index updated with correct status.
- [ ] No revenue figures or market-size numbers invented — `_TODO_` used for unknowns.
- [ ] No strategic argument or process narrative leaked into the model doc.
- [ ] Closing report delivered.
