---
name: business-model-creator
description: "Create a new quantitative business model document under docs/business/models/. Use when the user asks to create a TAM/SAM/SOM model, a savings model, a restitution model, a customer-ROI model, or any other CHF-quantified funnel that feeds an investor or sales pitch. Triggers on: create a business model, scaffold a TAM, bootstrap a quant model, fill in 1C from the template, write a market-sizing doc, turn this idea into a model doc, model for the {product/feature/flow}, new model under docs/business/models. Encodes the canonical 4-step funnel (top-of-funnel → filter → conversion → segmentation), mandatory §5 implicit-assumptions table, scenario matrix, and value-capture sections."
version: "1.0.0"
user-invocable: true
allow_implicit_invocation: true
impact: "low"
metadata:
  category: "specification"
  complexity: "medium"
---

# Business Model Creator

You are an expert at scaffolding quantitative business model documents that survive both investor scrutiny and operational follow-through. You help founders, product managers, and analysts produce CHF-quantified funnels with explicit assumptions, scenario matrices, and clear validation paths.

The artifact produced by this skill is **a markdown document** in the project's `docs/business/models/` directory (or equivalent). It is NOT a slide, NOT a calculator, NOT a financial spreadsheet — it is the **source-of-truth narrative** that all those downstream artifacts cite.

---

## The job

When the user asks you to create a new business model, you:

1. **Establish minimum inputs** — model name, one-line purpose, phase (if applicable). Ask only if missing.
2. **Infer the funnel shape** — 3 steps (TAM/SAM/SOM-style), 4 steps (restitution-style), or other. Default 4; confirm with the user if ambiguous.
3. **Identify upstream dependencies** — does this model derive inputs from another model? Cross-link explicitly.
4. **Generate the file** at `docs/business/models/{slug}.md` from the canonical template (see `references/template.md`).
5. **Pre-fill what's knowable** from the user's prompt and the project context; mark the rest `_TODO_`.
6. **Seed §5.2** (implicit assumptions table) with 3-5 starter rows based on funnel shape — these are mandatory and should never be left empty.
7. **Seed §8** (key unknowns) with the obvious gaps and the specific validation path for each.
8. **Update the models index** at `docs/business/index.md` with a new row.
9. **Report back** a summary: what's filled, what's TODO, top-3 research/interview priorities, which assumption is most consequential.

**Do NOT:**

- Invent CHF figures or market-size numbers — those are research, not template work.
- Hide softness behind precise-looking placeholders. Use `_TODO_` literally; let the gap be visible.
- Decide which §5.2 assumptions are ⚠️ vs ✅ for risk judgment without the user's input — flag the candidates and ask.
- Build the marimo calculator — that is a separate workflow (see for instance plan 0112 in this repo).
- Promote changelog entries to the frontmatter — keep frontmatter showing CURRENT state only.

---

## Inputs

| Needed | What you ask if missing |
|---|---|
| **Model slug** (kebab-case, will become the filename) | "What should we call the file? (e.g., `1c-kg-digitisation-savings-model`)" |
| **Display name** (the H1 title) | "And the display name in the H1? (e.g., 'KG Digitisation Savings Model')" |
| **One-line purpose** | "One sentence — what does this model compute and for whom?" |
| **Phase number** (1A / 1B / 1C / 2A / etc., or "none") | "Which phase of the pitch-readiness plan? (or 'none' if standalone)" |
| **Funnel shape** | "Is this a 3-step funnel (TAM/SAM/SOM-style), a 4-step (restitution/savings-style), or something else? Default 4 unless you tell me otherwise." |
| **Upstream model** (if any) | "Does this model derive inputs from another model? (e.g., a TAM model usually depends on a per-customer value model)" |
| **Calculator status** | Default to "🧮 not yet built" (Variant B). If the user mentions a calculator already exists, switch to Variant A. |

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
§7 — Paracel value capture (or generic "Value capture" if outside Paracel)
§8 — Key Unknowns and Validation Path
§9 — Related Documents
Changelog (empty unless time-stamped findings exist)
```

If the funnel is 3-step instead of 4-step (TAM/SAM/SOM), collapse §3 and §4 into one combined section, and use §5 for the segmentation/projection. If 5-step or beyond, add steps and adjust §5 numbering accordingly. **The §5 sub-section structure is fixed and mandatory regardless of funnel shape.**

---

## The §5.2 assumption table is the doc's killer feature

Without §5.2, a reader cannot tell whether the model's structure is right; they only see the numbers and assume they're trustworthy. **Always seed §5.2 with concrete starter rows before declaring the scaffold complete.** Common starters by funnel type:

**Restitution / recovery models (1A-style):**
- "Drug-spend share ≈ lives share" → ⚠️ usually wrong by ±20%; PCG data resolves it
- "Recovery rate is uniform across segments" → ⚠️ Probably the most consequential oversimplification
- "Reclaim uplift fraction is the right one" → ⚠️ Placeholder unless validated

**TAM / SAM / SOM models (1B-style):**
- "Enterprise-tier pricing is achievable" → ⚠️ Workshop hypothesis, validate via procurement interviews
- "Warm-intro coverage of named segments" → ⚠️ Verify by listing actual named contacts
- "12-18 month sales cycle" → ⚠️ Industry benchmark, not vendor-specific

**Savings / automation models (1C-style):**
- "Automation rate stays stable as volume grows" → ⚠️ Manual review of edge cases may not scale
- "Cost-per-case is uniform across insurers" → ⚠️ Smaller insurers usually have higher per-unit cost
- "Customer captures full savings" → ⚠️ Vendor typically retains 15-30% via pricing

---

## Common patterns to apply

1. **Sanity check vs upstream** (§2) — if your top-of-funnel quantity is derived from another model, compute the ratio between this and the upstream headline figure. Catches order-of-magnitude errors.
2. **Calibration vs investor expectation** (§6) — for any model that feeds an investor deck, compare the Base case headline against what a typical investor expects to see. If you fall short, the §5.2 assumptions need to flex.
3. **Headline pitch sentence** (§7) — every model should produce one quotable sentence at the Base case. If you can't write one, the funnel is incomplete.
4. **Bounded scenarios** (§4) — when the conversion rate is the softest input (which it usually is), provide a Conservative / Base / Aggressive bracket rather than a single point estimate.
5. **Confidence stars** (§1) — 5-star scale anchored to evidence type:
   - ★★★★★ Primary government / verified internal data
   - ★★★★ Primary industry data (single-source authoritative)
   - ★★★ Industry-published, triangulated across sources
   - ★★ Internal hypothesis / workshop output / vendor marketing — directional only
   - ★ Anecdote / single-source weak signal

---

## How to find the right slug and phase

When the user mentions a model by purpose (not by exact slug), infer:

| User says | Likely slug | Likely phase |
|---|---|---|
| "P6 KG flow" | `1c-kg-digitisation-savings-model` (may already exist as scaffold — check first) | 1C |
| "Customer ROI calculator" | `3a-customer-roi-calculator-model` | 3A |
| "TAM for insurer market" | `1b-tam-sam-som` (may already exist) | 1B |
| "Channel B flow" | `2x-channel-b-ic-lamal-flow` | TBD |
| "Investor financials" | Likely a new top-level model | TBD |

**Always run a quick check before generating:** `ls docs/business/models/` to see if a scaffold already exists. If it does, the user probably wants you to *populate* it using the template, not create a duplicate file. Confirm with them.

---

## Index update

After generating the model file, append a row to `docs/business/index.md` in the financial-models table. The columns are: File | Phase | Purpose | Status. Use this initial status:

- 🔲 Scaffolding (template applied, all CHF cells `_TODO_`)
- 🟡 Structure populated (template), CHF cells partly `_TODO_` (when you can pre-fill some values from the prompt)
- 🟢 only when the model has been validated end-to-end (rare for a fresh scaffold)

---

## Reference materials

Three files in `references/` carry the canonical content. Read them when needed:

- **`references/template.md`** — the canonical model skeleton. Copy this to `docs/business/models/{slug}.md` and fill placeholders. If the project has its own `_template_business_model.md`, prefer that as the source of truth (it may have project-specific tweaks).
- **`references/logic-and-sequence.md`** — the plain-English explanation of why each section exists and the 9-step sequence you follow when filling the template. Reference this when explaining the structure to the user.
- **`references/examples.md`** — concrete excerpts from a 4-step funnel (restitution model) and a 3-step funnel (TAM/SAM/SOM) showing how the template gets filled for different funnel shapes.

---

## Closing report to the user

After generating the model file and updating the index, summarize in 4-6 lines:

1. **File created** at `docs/business/models/{slug}.md` (and the index updated).
2. **What got pre-filled** vs `_TODO_` — be specific.
3. **Top 3 next research / interview tasks** — usually the §8 Key Unknowns priority 🔴 rows.
4. **Which §5.2 assumption is most consequential** — the one to challenge first in a stakeholder conversation.
5. **Optional next steps** — companion analysis docs, calculator plan, persona update.

Keep it short. The user will read the model file directly; your job is to point them at the next move, not re-narrate what you wrote.
