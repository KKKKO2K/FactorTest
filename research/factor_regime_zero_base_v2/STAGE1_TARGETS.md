# Stage 1 Target Pre-Registration

This file is written after Stage 0 and before any Stage-1 predictor result is observed.

## Stage-0 facts that determine target eligibility

### Winner continuation is not eligible
With 8 factors, a random current top-2 set has expected future top-2 overlap share of 25% and expected future top-4 survival share of 50%.

Observed medians across the six universes were approximately:
- exact top-2 survival: 22%–29% by era;
- top-2 surviving in future top-4: 48%–55% by era.

Current-top2 alpha vs EW8 also changes sign across eras. Therefore winner continuation is not sufficiently structural to be a primary v2 target.

### Opportunity clustering is eligible
Current 20D factor dispersion has positive current-to-future association through 2016–24 across most universes. Absolute opportunity shows a weaker but similar pattern. The relationship reverses in 2025/26, which will be treated as stress evidence rather than tuning input.

### Cross-universe coherence is eligible
The same 8-factor ranking is strongly shared across universe definitions. Median pairwise 20D factor-rank correlation across the six universes is about +0.69 in 2016–24 and remains above +0.70 in 2025/26, with roughly 85%–92% of universe-pair dates positive.

This suggests that the most structural object may be a common factor tape shared across K200, KOSDAQ, KOSPI ex-K200 and broader universes.

## Primary target A — Future factor opportunity

For each universe and signal date t:

`FUTURE_DISPERSION20 = std(factor returns over t+1 ... t+20 across the 8 factors)`

Primary question: can current primitive factor-market structure forecast whether the next 20D offers a large or small factor-selection opportunity set?

Predeclared primitive predictors:
1. current 20D dispersion;
2. current 20D mean absolute factor payoff;
3. current 20D factor range;
4. current 20D positive-factor breadth;
5. current leader absolute-payoff concentration;
6. trailing 60D average pairwise factor correlation;
7. trailing 60D PC1 share;
8. current 20D-vs-60D factor-rank agreement;
9. current cross-universe factor-rank coherence.

## Primary target B — Future cross-universe coherence

For each signal date t:

`FUTURE_COHERENCE20 = median pairwise Spearman rank correlation across the 15 universe pairs, using each universe's 8-factor forward-20D payoff vector.`

Primary question: can the degree of common factor leadership across universe definitions be forecast from current factor-market structure?

Predeclared predictors:
1. current cross-universe coherence;
2. median current 20D factor dispersion across universes;
3. median current 20D mean absolute factor payoff;
4. median trailing 60D average factor correlation;
5. median trailing 60D PC1 share;
6. median current 20D-vs-60D rank agreement.

## Samples

- Discovery/sign learning: 2016–2019.
- Validation: 2020–2022.
- Confirmation: 2023–2024.
- Stress only: 2025 and 2026.

No predictor or direction may be changed because of 2020+ results.

## Stage-1 gates

### Opportunity target
A predictor is Stage-1 PASS only if:
- median directed IC > +0.05 in 2020–22;
- median directed IC > +0.05 in 2023–24;
- positive directed IC in at least 4/6 universes in both periods;
- median frozen-tercile directed target spread > 0 in both periods.

### Coherence target
A predictor is Stage-1 PASS only if:
- directed IC > +0.10 in 2020–22;
- directed IC > +0.10 in 2023–24;
- frozen-tercile directed target spread > 0 in both periods.

2025/2026 can falsify confidence but cannot create a PASS.

## What happens after Stage 1

Only Stage-1 PASS relationships may enter Stage 2. No composite, clustering or portfolio rule is allowed in Stage 1.
