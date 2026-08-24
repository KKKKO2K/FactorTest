# Stage 5 Protocol — Recurrent Factor Configurations / Analog Forecasting

Stages 1–4 rejected simple state labels, directed one-lag transmission, and linear pairwise spread laws. Stage 5 changes methodology rather than adding another linear feature.

The hypothesis is:

> Factor dynamics may be **locally recurrent**: when the 8-factor configuration or recent trajectory resembles a historical episode, the next factor move may resemble what followed those historical analogs.

No clustering, discrete regime labels, regression coefficients, or pair-specific thresholds are used.

## Clean 8-factor tape

Use the same three mutually disjoint primitive universes:
- K200
- KOSPI_EX_K200
- KOSDAQ

Normalize each factor-universe 5D return with 2016–19 mean/std and equal-weight the three primitive universes into an 8-dimensional common factor vector `F[t]`.

For analog matching, remove the cross-sectional mean from each date so the state represents **relative factor leadership**, not the average level of all factor payoffs.

## Two pre-registered representations

### A. SNAPSHOT

Current 8-factor relative vector:

`S[t] = demean_cross_section(F[t])`

Normalize `S[t]` to unit L2 norm for cosine-distance matching.

### B. PATH20

Concatenate the last four normalized snapshot vectors:

`P[t] = [S[t-3], S[t-2], S[t-1], S[t]]`

This describes the recent 20D path/rotation rather than only the endpoint.

## Analog library

Use **Discovery 2016–19 only** as the historical analog library for every later period.

For each library state retain its realized next-5D relative factor vector.

For every evaluation date:
1. compute cosine similarity to all valid Discovery states;
2. select the fixed `k = 10` nearest analogs;
3. forecast the next relative factor vector as the equal-weight mean of those 10 analog outcomes.

`k` is fixed before results and is not swept.

## Baselines

Compare analog forecasts with:

1. `UNCONDITIONAL`: Discovery mean next relative factor vector;
2. `PERSISTENCE`: current relative factor vector as the next relative factor forecast.

## Metrics

For each evaluation date:
- cross-sectional Spearman rank correlation between predicted and realized 8-factor vector;
- vector MSE;
- predicted-top2 versus realized-top2 overlap share.

Aggregate by era:
- Validation 2020–22;
- Confirmation 2023–24;
- Stress 2025;
- Stress 2026.

## Primary PASS gate

A representation passes only if in BOTH Validation and Confirmation:
- analog mean vector MSE is lower than both baselines;
- analog median cross-sectional rank IC is higher than both baselines.

Top2 overlap is diagnostic, not part of the gate.

2025/26 cannot create a PASS.

## Outcome-association placebo

Keep the Discovery analog state library fixed, but circularly shift the mapping from library states to their next-period outcomes by 1...N-1 positions.

For each false mapping, rerun the analog forecast using the same nearest neighbors.

Observed median rank IC must beat at least 90% of shifted-outcome mappings (`p <= 0.10`) in both Validation and Confirmation for a representation to be labelled `ROBUST_RECURRENT`.

## Interpretation labels

- `ROBUST_RECURRENT`: primary gate + placebo gate pass.
- `WEAK_RECURRENT`: primary gate passes but placebo fails, or one representation shows economically consistent but incomplete evidence.
- `NO_RECURRENCE`: neither representation passes.

## Research discipline

Do not tune:
- k;
- distance metric;
- lookback length;
- factor subset;
- target horizon

after results.

If Stage 5 fails, the current 8-factor return panel should be considered to have **descriptive contemporaneous structure but little exploitable temporal structure under the tested linear and local-nonlinear methods**. Any further work should add new information or be explicitly exploratory spectral/DMD research rather than alpha mining.

No portfolio backtest is permitted in Stage 5.
