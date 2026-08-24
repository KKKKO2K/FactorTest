# Factor Regime Zero-Base v2 — Research Status

## Bottom line

Starting again from the canonical 8-factor payoff panel, without prior B/F states, survivor variables, thresholds, clustering or portfolio rules, does **not** support a robust forecastable Factor Regime from factor returns alone.

This is a useful negative result: the prior ambiguity was not mainly a portfolio-mapping problem. The underlying factor-return state variables themselves contain only weak or short-memory predictive structure.

## Stage 0 — Empirical structure map

### Winner continuation: weak / near chance
With 8 factors, random expected current-top2 overlap with future top2 is 25%, and expected current-top2 survival into future top4 is 50%.

Observed era medians were roughly:
- top2 exact survival: 22%–29%;
- top2-in-top4 survival: 48%–55%.

Current-top2 alpha vs EW8 also changes sign across eras.

**Conclusion:** do not use unconditional factor-winner persistence as the central regime concept.

### Cross-universe coherence: very strong contemporaneously
Median pairwise 20D factor-rank correlation across the six universe definitions is about +0.69 in 2016–24 and remains above +0.70 in 2025/26. About 85%–92% of universe-pair dates have positive rank correlation.

**Conclusion:** there is a common factor tape across universe definitions, but this does not by itself imply predictability.

### Opportunity clustering: visible historically
Current cross-factor dispersion/absolute opportunity is positively associated with future 20D opportunity through 2016–24, then reverses in 2025/26.

**Conclusion:** eligible for falsification, not yet a regime signal.

## Stage 1 — Pre-registered minimal predictability

### Future factor opportunity
3 of 9 primitive predictors passed both validation and confirmation gates:
- current factor range;
- current factor dispersion;
- current mean absolute factor payoff.

These are alternative measurements of one phenomenon rather than three independent signals.

### Future cross-universe coherence
0 of 6 predictors passed.

**Conclusion:** stop forecasting aggregate coherence.

## Stage 2 — Opportunity falsification

Primary current-20D to future-20D dispersion IC was positive in all six universes in each historical era:
- 2016–19: median IC +0.164;
- 2020–22: +0.237;
- 2023–24: +0.121.

However the pre-registered falsification gate failed:
- skipping the immediately following 5D block changes 2023–24 IC to -0.085;
- non-overlapping 20D sampling reduces 2023–24 median IC to +0.003;
- 40D/60D forward horizons also lose the relation in 2023–24;
- 2025 and 2026 primary ICs are negative.

The result survives all 8 leave-one-factor-out tests and cross-universe aggregation, so it is not driven by a single factor. It is best interpreted as **short-memory factor-volatility/opportunity clustering**, not a robust investable regime.

**Conclusion:** stop Factor Opportunity as a standalone regime target.

## Stage 3 — Cross-universe confirmation

The strongest Stage-0 fact — common factor leadership across universes — was tested as a factor-level confirmation signal.

### Global rank vs local rank
Global mean factor rank does not robustly improve on local factor rank:
- 2020–22: global IC +0.137 vs local +0.083, but median global-minus-local improvement is only +0.001;
- 2023–24: global IC +0.012 vs local +0.012, global-minus-local -0.024.

Primary gate: FAIL.

### Local top2 confirmed across universes
For local-top2 factors, being top2 in at least 3 of 6 universes does not improve forward payoff in validation/confirmation:
- 2020–22 median confirmed-minus-unconfirmed payoff: -0.07%;
- 2023–24: -0.05%.

Secondary gate: FAIL.

**Conclusion:** cross-universe agreement is descriptive/common, not incrementally predictive.

## What is now frozen / rejected

Do not continue engineering new regime variables from transformations of the same 8-factor return panel. Specifically freeze:
- factor-winner persistence states;
- factor-opportunity/dispersion states;
- aggregate cross-universe coherence forecasting;
- cross-universe confirmation of current factor winners;
- new clustering/HMM/KMeans built only from these same payoff variables.

## Next research direction requires genuinely new information

### Priority 1 — All-factor stock-level internals
Build point-in-time internals for **all 8 factors across all 6 universes**, not only OPFY1 or an aggregate market proxy:
- constituent positive-return breadth;
- top-5/top-10 contribution concentration;
- constituent return dispersion;
- holding turnover/retention;
- cross-factor holdings overlap and stock multiplicity;
- trading-amount/turnover/ADV support of each factor sleeve;
- divergence between factor payoff and constituent participation.

Primary question should be factor-level quality, not market direction:

`Does the internal health of a currently strong factor distinguish durable factor payoff from a noisy/localized payoff?`

### Priority 2 — External market-state conditioning
If factor internals are weak, condition factor payoffs on information not derived from the factor panel itself:
- market breadth and index trend;
- realized volatility/drawdown;
- liquidity/trading activity;
- rates/curve/term premium;
- FX;
- sector concentration/rotation.

### Priority 3 — Factor construction robustness
Before calling any state a regime, verify that conclusions hold under alternative factor payoff definitions rather than only the current 5D LS construction.

## Current interpretation

The current data says:

> Factor returns have clear contemporaneous structure, especially a common cross-universe factor tape, but the structure is only weakly forecastable from its own recent history.

A meaningful next Factor Regime result therefore requires **new explanatory information**, not a better transformation of the same factor-return panel.
