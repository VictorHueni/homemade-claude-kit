# Examples — how the template gets filled for different funnel shapes

Two real-world examples drawn from a Swiss pharma project (`swiss-aos-drug-reimbursement-model`). Both follow the same template but instantiate the funnel differently.

> **Generic-use note:** the examples are domain-specific (Swiss health insurance). The *patterns* — how each step is filled, how §5.2 is seeded, how §6 is bracketed — generalize. Substitute your own domain terms.

---

## Example 1 — 4-step restitution funnel (1A model)

**Purpose:** quantify the annual restitution obligation a Swiss insurer should claw back from pharma, and how much goes unclaimed today.

| Step | Filled value | Notes |
|---|---|---|
| **§2 Top of funnel** | Total OKP drug spend on PM drugs ≈ CHF 3B (33% of CHF 9.2B) | Quadruply validated: BAG, Helsana, APV, Krebsliga |
| **§3 Filter** | Triggerable PM dossiers by type: 142 PRICE-CONFIDENTIAL + 91 PRICE-PUBLIC + 19 P4P-PUBLIC + 5 VolCap + 1 P4P-CONFIDENTIAL | DB-verified counts; rates of trigger partly TODO |
| **§4 Conversion rate** | Bounded scenario: 30% / **50%** / 70% recovery rate | The single biggest unknown; anchored by Interpharma's CHF 300M |
| **§5 Segmentation** | Per-tier: Large (1.5M lives) CHF 102M obligation → Small (100K lives) CHF 7M | Lives-share proxy for drug-spend share (assumption #3 in §5.2) |

### Key §5.2 assumptions seeded

| # | Assumption | Risk |
|---|---|---|
| 1 | Industry-total anchor reflects all 37 insurers | ✅ Probably right |
| 2 | 50% recovery is the right base case | ⚠️ Biggest single unknown — pharma-desk-analyst interview confirms |
| 3 | Drug-spend share ≈ lives share | ⚠️ Mildly wrong (±20% skew); PCG data resolves |
| 4 | PM formulary coverage is uniform | ✅ Mostly true (federally mandated LS) |
| 5 | Recovery rate uniform across segments | ⚠️ **Probably the most consequential oversimplification** |
| 6 | Capture-rate uplift is the right one | ⚠️ Placeholder until validated |

### §6 Scenario matrix (excerpt)

| Segment | Conservative (70% recovery) | Base (50%) | Aggressive (30%) |
|---|---|---|---|
| Large | CHF 21.8M unclaimed | CHF 50.8M | CHF 118.5M |
| Mid-large | CHF 11.6M | CHF 27.1M | CHF 63.2M |
| Mid | CHF 7.3M | CHF 16.9M | CHF 39.5M |
| Small | CHF 1.5M | CHF 3.4M | CHF 7.9M |

### §7 Headline pitch sentence (Base case)

> *"A Swiss insurer with ~10% market share has approximately CHF 60M in annual restitution obligations, recovers ~CHF 30M today, and leaves ~CHF 30M on the table each year."*

---

## Example 2 — 3-step TAM/SAM/SOM funnel (1B model)

**Purpose:** quantify Paracel's total addressable / serviceable / obtainable market for the investor deck.

| Step | Filled value | Notes |
|---|---|---|
| **§2 TAM** | 37 Swiss insurers × Enterprise pricing → CHF 2.2M–4.4M / yr revenue ceiling | Sanity-check vs upstream: ~1% of CHF 300M Channel A flow — TAM is conservatively priced |
| **§3 SAM** | Top 8 insurers reachable in 3 yrs ≈ 83% of OKP lives | Concrete named insurers from upstream 1A model's §5.3 |
| **§4 SOM** | 2 / 4 / 6 pilots (Bear / Base / Bull) by end of Year 2 | 12-18 month sales cycle assumption |
| **§5 Segmentation** | Per-segment ARR: Large 2×CHF 100K + Mid-large 4×CHF 80K + Mid 2×CHF 70K = CHF 660K steady-state | Long-tail Small / regional insurers are out of SAM at Enterprise pricing |

### Key §5.2 assumptions seeded

| # | Assumption | Risk |
|---|---|---|
| 1 | CHF 5–10K/month Enterprise pricing is achievable | ⚠️ Biggest single unknown — Phase 2B Leistungseinkauf interview |
| 2 | Pharma-sales co-founders give warm intros to ~8 insurers | ⚠️ Verify by listing actual named contacts |
| 3 | 12–18 month sales cycle | ⚠️ Industry-standard, not Swiss-rebate-specific |
| 4 | Small / regional insurers out of SAM | ✅ Probably right at Enterprise pricing |
| 5 | Flat Enterprise pricing | ⚠️ Probably wrong; value-based could double TAM |
| 6 | One subscription per insurer (no seat expansion) | ✅ Conservative |

### §6 Calibration vs investor expectation

Typical seed-round Swiss B2B SaaS expects CHF 500K-1M ARR by Year 2-3 to justify a CHF 5-10M Series A. Base case at CHF 320K Year 2 sits below that threshold — either pricing assumption #1 needs to flex (value-based) or SOM penetration rate needs to be faster.

This callout was forced by the template; without §6's calibration prompt, the gap would have been invisible.

---

## What both examples have in common

1. **§5.2 was the highest-value section** — both surfaced "the most consequential oversimplification" that wasn't in the original scaffold.
2. **The Base case quotable sentence** in §7 anchors the pitch deck.
3. **Bounded scenarios** in §4 + §6 prevent over-confidence in single point estimates.
4. **Upstream cross-links** make the model's dependencies explicit (1B → 1A for per-insurer values).
5. **Calculator callout** keeps the markdown narrative and the interactive truth from drifting (1A has Variant A, 1B has Variant B "not yet built").

---

## What to copy when filling a new model

If you're writing a **4-step funnel** (restitution / savings / recovery model), use Example 1 as the structural reference.

If you're writing a **3-step funnel** (TAM/SAM/SOM / market-sizing model), use Example 2.

If you're writing something else (e.g., a 5-step funnel for outcome-based contracting, or a 2-step model for a back-of-envelope), follow the template's section labels but add or collapse steps. The mandatory parts (§5.2 assumptions, §6 scenario matrix, §8 key unknowns, Changelog) stay regardless of funnel length.
