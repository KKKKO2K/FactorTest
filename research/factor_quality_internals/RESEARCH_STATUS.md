# Factor Return Quality / Internals — Research Status

## Scope
Fresh stock-level research asking whether the **quality/source of a recent factor move** adds information for the next 5D factor payoff after controlling for trailing 20D raw factor performance.

No prior Factor Regime labels, clustering, KMeans states, or portfolio rules are used.

Primary universes are the three disjoint primitive universes:
- K200
- KOSPI_EX_K200
- KOSDAQ

Era discipline:
- 2016–19 discovery/context
- 2020–22 validation
- 2023–24 confirmation
- 2025 / 2026 stress only

## Stage 1 — Stock-level quality panel
Using PIT factor values, stock returns, trading amount, and the frozen WICS decomposition, four preregistered quality axes were built for every factor/universe/non-overlapping 5D block:

1. within-sector support;
2. Top-vs-Bottom pairwise stock breadth;
3. contribution concentration;
4. relative trading-activity support.

QA:
- 519 non-overlapping blocks;
- 24,912 factor/universe rows;
- rebuilt raw factor payoff max difference vs frozen sector panel: ~1.0e-16;
- median trading-activity coverage: 100%.

## Stage 2 — Incremental quality test
Each quality axis was aggregated using only the four completed prior 5D blocks. The baseline predictor is trailing RAW20.

The primary statistic is cross-sectional partial rank IC of a direction-aware quality score versus next raw 5D factor payoff, controlling RAW20 rank.

A second decision diagnostic compares, within the RAW20 Top4, the next-5D payoff of the two higher-quality factors versus the two lower-quality factors.

### Preregistered survival gate
A feature survives only if both 2020–22 and 2023–24 have:
1. median primitive-universe primary partial IC > +0.02;
2. positive primary IC in at least 2/3 primitive universes;
3. median primitive-universe Top4 quality spread > 0;
4. positive Top4 spread in at least 2/3 primitive universes.

## Results
### WITHIN_ALIGNMENT — FAIL
2020–22:
- median primitive pIC +0.034, 2/3 positive;
- median Top4 spread +0.126% per next 5D, 2/3 positive;
- passes that era.

2023–24:
- median primitive pIC only +0.008, 2/3 positive;
- median Top4 spread +0.185%, 2/3 positive;
- fails the pIC threshold.

Interpretation: within-sector support contains some information, but the relationship is not uniformly strong across universes/eras and is not sufficiently stable as a standalone quality selector.

### BREADTH_ALIGNMENT — FAIL
2020–22:
- median primitive pIC +0.051, 3/3 positive;
- pooled mean pIC +0.043, t=+2.23;
- but median Top4 spread -0.016%, only 1/3 positive.

2023–24:
- median primitive pIC -0.002, 1/3 positive;
- median Top4 spread +0.097%, 2/3 positive.

Interpretation: broad participation had cross-sectional ranking information in 2020–22, but that information did not translate into choosing better factors among the already-strong RAW20 candidates. The relation also weakened in 2023–24.

### BROAD_CONTRIBUTION — FAIL
2020–22:
- median primitive pIC +0.020, 2/3 positive;
- median Top4 spread -0.059%, 1/3 positive.

2023–24:
- median primitive pIC +0.003, 2/3 positive;
- median Top4 spread -0.156%, 0/3 positive.

Interpretation: lower dependence on the five largest stock contributions is not a useful standalone predictor of factor durability in this sample.

### LIQUIDITY_SUPPORT20 — FAIL
2020–22:
- median primitive pIC +0.006, 2/3 positive;
- median Top4 spread -0.023%, 1/3 positive;
- fails.

2023–24:
- median primitive pIC +0.023, 2/3 positive;
- median Top4 spread +0.214%, 2/3 positive;
- passes that era.

Interpretation: relative trading-activity support became informative in 2023–24, but it was not stable in the earlier validation era.

## Stress observations
These do not alter the decision:
- 2025: no feature passes a robust selection-quality interpretation.
- 2026: breadth is unusually strong (median primitive pIC +0.142, 3/3 positive; Top4 spread +0.916%, 3/3), while liquidity support is negative. This is stress-only and too short to promote.

## Canonical conclusion
**No preregistered stock-level factor-quality axis survives both validation and confirmation.**

The data do support a weaker conclusion:
- recent factor payoff magnitude does not tell the whole story;
- within-sector support, breadth, and liquidity support can each contain incremental information in particular eras;
- but the useful confirmation mechanism changes over time and none is stable enough to become a standalone factor-selection rule.

Contribution concentration is the clearest negative result.

## Research discipline / stop rule
Do not, on this same sample:
- flip feature signs;
- optimize thresholds;
- search alternative top-k values;
- combine the four features into a fitted quality score;
- promote 2026 breadth as validation evidence.

Because no Stage 2 axis passed the preregistered two-era gate, no survivor falsification or portfolio rule is run in this track.

A genuinely new follow-up would need a separately specified hypothesis rather than tuning these four measures after seeing results.
