<!--
=============================================================================
BUSINESS MODEL TEMPLATE — clone-and-fill
=============================================================================

Purpose: provide a consistent shape for every quantitative business model
under docs/business/models/. Use this as the starting point for every new
model (1A, 1B, 1C, future TAM funnels, savings models, etc.).

How to use:
  1. cp _template_business_model.md NN-your-model-slug.md
  2. Fill placeholders marked {{LIKE_THIS}}
  3. Drop sections that genuinely don't apply (don't pad)
  4. Keep §5 sub-sections (How to read + Implicit assumptions) — those are
     the doc's quality differentiator and are mandatory

The 4-step funnel below is the canonical shape. If your model is a 3-step
funnel (e.g., TAM → SAM → SOM), collapse Steps 2 and 3 into one section.
If it's a 5+ step funnel, add steps. The template doesn't enforce four.

Render-invisible HTML comments like this one carry guidance; markdown
previewers won't show them but they survive in the raw source for the next
author.
=============================================================================
-->

# {{Model Name}}

> **Phase {{N}} of [pitch-readiness-plan.md](../pitch-readiness-plan.md)**
>
> **Purpose:** {{One sentence — what this model computes and for whom.}}
>
<!--
Status rubric — use these definitions consistently across all models:
  🟢 = all CHF / numeric cells filled with cited values; assumptions table populated
  🟡 = some cells _TODO_ but bounded scenarios exist (e.g., conservative/base/aggressive)
  🔲 = pure scaffolding; structure exists, no values yet
-->

> **Status:**
> - 🟢 Sections {{populated section list}}
> - 🟡 Sections {{partially populated}}
> - 🔲 Sections {{scaffolding only}}
>
> **Key remaining unknown:** {{The single highest-impact validation gap. Be specific.}}
>
> **Validation path:** {{The one interview / data pull that would unblock it.}}

<!--
Interactive calculator callout — pick ONE of the two variants below depending
on whether a marimo notebook exists for this model. Delete the unused variant.
-->

<!-- VARIANT A — calculator EXISTS. Use when a marimo notebook is already shipped. -->

> **🧮 Interactive calculator:** [`analysis/{{slug}}.py`](../../../analysis/{{slug}}.py) (marimo notebook).
> Static HTML export, openable in any browser without setup: [`analysis/exports/{{slug}}.html`](../../../analysis/exports/{{slug}}.html).
> Source-of-truth Python math (unit-tested): [`analysis/{{slug}}_math.py`](../../../analysis/{{slug}}_math.py).
> Drag the sliders to explore alternative scenarios; the §6 scenario matrix below was generated from this notebook at base-case settings.

<!-- VARIANT B — calculator NOT YET BUILT. Use when only the markdown model exists. -->

> **🧮 Interactive calculator:** _Not yet built._ Planned to follow the [1A pattern](./1a-preismodelle-restitution-model.md) (range sliders for the bounded inputs, scenarios re-rendered live in a per-segment table). For now §6 below is hand-computed from base-case sliders.

---

## Table of Contents

- [§1 — Inputs and Data Sources](#1--inputs-and-data-sources)
- [§2 — Step 1: {{name of top-of-funnel quantity}}](#2--step-1-name-of-top-of-funnel-quantity)
- [§3 — Step 2: {{name of filter}}](#3--step-2-name-of-filter)
- [§4 — Step 3: {{name of conversion rate}}](#4--step-3-name-of-conversion-rate)
- [§5 — Step 4: Scale by segment](#5--step-4-scale-by-segment)
  - [§5.1 How to read these numbers](#51-how-to-read-these-numbers-math-chain)
  - [§5.2 Implicit assumptions](#52-implicit-assumptions-read-this-before-quoting-any-5-number)
  - [§5.3 Named segments](#53-named-segments)
  - [§5.4 Per-segment scenarios](#54-per-segment-scenarios)
- [§6 — Scenario Matrix](#6--scenario-matrix)
- [§7 — Paracel Value Capture](#7--paracel-value-capture)
- [§8 — Key Unknowns and Validation Path](#8--key-unknowns-and-validation-path)
- [§9 — Related Documents](#9--related-documents)
- [Changelog](#changelog)

---

<!--
§0 GLOSSARY — OPTIONAL.

Include only if your model uses 5+ domain-specific terms that aren't defined
in docs/data/glossary.md. Otherwise link to the central glossary from the
frontmatter and skip §0 entirely. Don't create parallel glossaries.
-->

## 1. Inputs and Data Sources

<!--
Standard input-table format. Confidence stars use a 5-star scale anchored to
the type of evidence backing each value:

  ★★★★★ Primary government / regulator data (BAG, Bundesgericht, parlament.ch);
        or internal data verified by unit tests + sanity-check queries
  ★★★★  Primary industry data (single-source authoritative — Helsana report,
        Interpharma Panorama, IC LAMal annual report)
  ★★★   Industry-published, supported by independent sourcing (multiple
        sources triangulating to the same answer)
  ★★    Internal hypothesis / workshop output / vendor marketing —
        directional only, needs external validation
  ★     Anecdote / single-source weak signal — cite with explicit caveat
        and flag in §8 Key Unknowns

If an input itself has a counting-methodology gotcha (different sources
counting different things), give it its own §1.x sub-section. See 1A §1.1
for an example.
-->

| Input | Value | Source | Confidence |
|---|---|---|---|
| {{Input name}} | {{Value}} | {{Inline link to source}} | ★★★★ |
| {{...}} | {{...}} | {{...}} | {{...}} |

### 1.1 {{Sub-section for any input that needs methodology explanation — OPTIONAL}}

---

## 2. Step 1 — {{Top of funnel quantity}}

<!--
First step of the funnel. What's the TOTAL relevant quantity before any
filtering? Examples:
  - 1A: total OKP drug spend on PM drugs
  - 1B: total Swiss insurer pharma-desk addressable spend
  - 1C: total industry cost of current KG process

Should produce a single headline CHF figure (or count, or rate).

Add §2.x sub-sections for triangulation, cross-checks, or empirical
brackets. See 1A §2.1, 2.2, 2.3 for the pattern.
-->

| Scenario | Assumption | Estimated value |
|---|---|---|
| Conservative | {{...}} | CHF {{...}} |
| Base | {{...}} | CHF {{...}} |
| Aggressive | {{...}} | CHF {{...}} |

**Assumption rationale:**

{{Walk through how the bracket was derived. Cite sources inline.}}

<!--
SANITY CHECK CALLOUT — RECOMMENDED when this model's §2 derives from another
model. Compare your §2 figure against the upstream model's headline number
and note the ratio. Catches order-of-magnitude errors before they propagate.
Example from 1B:
  "37 insurers × CHF 60-120K/yr = CHF 2.2M-4.4M/yr TAM. Compare to CHF 300M
   industry Channel A flow ([1A §4]) — the TAM is ~1% of the recovered flow."
-->

**Sanity check vs upstream:** {{Compare this §2 figure against the upstream model it derives from. If the ratio looks wrong, fix the assumption before continuing.}}

### 2.1 {{Triangulation / validation sub-section — OPTIONAL}}

---

## 3. Step 2 — {{Filter}}

<!--
Second step: what subset of the §2 quantity actually counts for this model?
Examples:
  - 1A: triggerable spend by PM type (PRICE / P4P / VOLUME_CAP)
  - 1B: serviceable portion (insurers we can sell to in T+3 years)
  - 1C: automatable case subset (Vertrauensarzt clear-cut cases)
-->

| {{Filter dimension}} | Distinct {{units}} | {{Triggers / criteria}} | Est. % of §2 | CHF estimate |
|---|---|---|---|---|
| {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

### 3.1 {{Per-category deep dive — OPTIONAL}}

---

## 4. Step 3 — {{Conversion rate}}

<!--
Third step: what fraction of the §3-filtered quantity flows through today?
Examples:
  - 1A: current recovery rate (30%/50%/70% bounded)
  - 1B: market-penetration assumption
  - 1C: % of cases auto-approvable today (OLUtool A/B)

This is usually the WEAKEST input — flag it explicitly and bracket it with
scenarios. Cite the methodology for picking conservative/base/aggressive.
-->

> **Bounded scenario** (until validated by interview / data pull):

| Scenario | Assumption | Implied result |
|---|---|---|
| Conservative ({{N}}%) | {{...}} | {{...}} |
| Base ({{N}}%) | {{...}} | {{...}} |
| Aggressive ({{N}}%) | {{...}} | {{...}} |

**Why this bracket:** {{cite sources, prior incidents, or analogous benchmarks}}

---

## 5. Step 4 — Scale by segment

<!--
Final step: distribute the §4 result across customer segments. This is
where per-customer / per-tier figures appear.

Mandatory sub-sections:
  §5.1 How to read these numbers — math chain (worked example)
  §5.2 Implicit assumptions table

Optional sub-sections:
  §5.3 Named segments (top N by size)
  §5.4 Per-segment scenarios
-->

### 5.1 How to read these numbers (math chain)

<!--
Walk through the calculation from the §4 result to a per-segment figure,
using ONE concrete worked example. Show every step explicitly with both the
formula and the resulting number.
-->

**Step A — anchor the {{quantity}}.**

{{Source citation + value.}}

**Step B — derive {{intermediate quantity}}.**

```
{{intermediate}} = {{previous} ÷ {{rate or fraction}}
                 = CHF {{value}}
```

**Step C — slice by {{segmentation dimension}}.**

{{Worked example for one named segment. Show the math.}}

### 5.2 Implicit assumptions (read this before quoting any §5 number)

<!--
THIS SECTION IS MANDATORY. It must be filled BEFORE the model is shown to
any stakeholder, even if other cells are still _TODO_. Without this table
a reader cannot tell if the model's STRUCTURE is right; they only see the
numbers and assume they're trustworthy.

Every assumption that could be wrong gets a row. Be brutally honest.
  ✅ = probably correct, with reason
  ⚠️ = risky oversimplification, with specific failure mode + validation path
  ❌ = known wrong, kept as floor / ceiling pending better data
-->

| # | Assumption | What it implies | Risk |
|---|---|---|---|
| 1 | {{...}} | {{...}} | ✅ Probably right — {{reason}} |
| 2 | {{...}} | {{...}} | ⚠️ {{specific failure mode + how to validate}} |
| 3 | {{...}} | {{...}} | ⚠️ **Probably the most consequential oversimplification.** {{...}} |

**The N assumptions most worth challenging in a stakeholder conversation:** {{list by row #}}.

### 5.3 Named segments

<!--
Concrete map from the model's abstraction (tiers, deciles, cohorts) to the
actual world. For Swiss insurers: top 8 named + long tail.
-->

| Rank | Segment | Size | % share | Cumulative % | Tier label |
|---|---|---|---|---|---|
| 1 | {{...}} | {{...}} | {{...}} | {{...}} | {{...}} |

### 5.4 Per-segment scenarios

<!--
The headline per-segment outputs. Format as a table the user can quote from
in a pitch sentence.
-->

| Segment | Lives / size | Headline CHF | Notes |
|---|---|---|---|
| {{...}} | {{...}} | **{{CHF ...}}** | {{...}} |

---

## 6. Scenario Matrix — The Pitch Anchor

<!--
3×N matrix: conservative / base / aggressive scenarios × the N segments
you care about. This is what the pitch quotes.

If you have an interactive calculator, note that this table was generated
from it at base-case settings, and re-generation is one command.
-->

> **Target:** a single defensible sentence per segment that the pitch can quote.

| {{Segment tier}} | Conservative | Base | Aggressive |
|---|---|---|---|
| {{...}} | {{CHF ...}} | {{CHF ...}} | {{CHF ...}} |

<!--
CALIBRATION CALLOUT — RECOMMENDED for any model that feeds the investor deck.
Compare your Base-case headline against the external expectation (investor norm,
peer benchmark, industry comparable). If you fall short, the §5.2 assumptions
either need to be more aggressive or the SOM/penetration assumption needs to be
faster. Forces honesty about whether the pitch math actually clears the bar.

Example from 1B §6: "typical seed-round Swiss B2B SaaS expects CHF 500K-1M ARR
by Year 2-3 to justify a CHF 5-10M Series A. Base case at CHF 320K Year 2 sits
below that threshold — either pricing or SOM penetration needs to be more
aggressive."
-->

**Calibration vs external expectation:** {{What does an investor / peer / comparable benchmark expect to see in this cell? If Base case falls short, what specifically needs to change in §3/§4/§5 to clear the bar?}}

---

## 7. Paracel Value Capture

<!--
Paracel-specific math: how do we monetize the addressable gap? This section
varies most per model because it depends on which Paracel product (Reclaim,
Maintainer, Explorer, KG) the model feeds.

Standard sub-sections:
  - Uplift assumption (what % of the gap can we actually capture?)
  - WTP fraction (what fraction of our recovered value does the customer pay?)
  - Headroom math (WTP ÷ list price)
  - Pricing sensitivity / band exploration
-->

Anchoring on §4's bounded scenarios:

| | Conservative | Base | Aggressive |
|---|---|---|---|
| {{Industry headline}} | CHF {{...}} | **CHF {{...}}** | CHF {{...}} |
| Per-segment | CHF {{...}} | **CHF {{...}}** | CHF {{...}} |
| Paracel capture (@ {{N}}% uplift) | CHF {{...}} | **CHF {{...}}** | CHF {{...}} |
| Implied WTP ({{N}}% of capture) | CHF {{...}} | **CHF {{...}}** | CHF {{...}} |
| Headroom vs proposed price | **{{N×}}** | **{{N×}}** | **{{N×}}** |

**Headline pitch sentence (base case):**

> {{One-sentence value prop using the base-case CHF figures.}}

**Sources for the assumptions:**

- Uplift fraction: {{cite the benchmark — Lyfegen, Cotiviti, Codoxo, etc.}}
- WTP fraction: {{cite the benchmark — typical recovery-SaaS ratio, etc.}}
- Proposed price: {{cite the workshop deliverable or pricing decision}}

---

## 8. Key Unknowns and Validation Path

<!--
Honest list of every input that's still a guess. Status emojis:
  🟢 Resolved
  🟡 Bounded by triangulation (good enough for the pitch, not for the deal)
  🟠 Partial — some validation done
  🔴 Blocker — must validate before pitching
  ⚠️ Caveat — acknowledge but accept

Each row should have a concrete next step.
-->

| Unknown | Impact on model | Status | How to resolve | Priority |
|---|---|---|---|---|
| {{...}} | {{High / Medium / Low}} | 🟡 | {{1 interview / 1 data pull / 1 desk-research session}} | {{order}} |

---

## 9. Related Documents

<!--
Upstream (what this model depends on) and downstream (what depends on it).
Use relative links.
-->

- **Upstream:** [{{...}}]({{path}}) — {{relationship}}
- **Downstream:** [{{...}}]({{path}}) — {{relationship}}
- **Companion process doc:** [{{...}}]({{path}}) — {{relationship}}
- **Pitch artefact:** [{{...}}]({{path}}) — {{how the pitch uses this model}}

---

## Changelog

<!--
Time-stamped findings that materially changed the model. New entries at the
top. Prune entries older than ~12 months or migrate to git history.

Don't promote changelog entries to the frontmatter — they age into noise.
The frontmatter should always show CURRENT state, not historical updates.
-->

### {{YYYY-MM-DD}} — {{One-line summary}}

{{What changed, why, source. Cross-reference to the section(s) affected.}}
