# Stage 4 Protocol — Pairwise Factor Relative-Value Dynamics

Stages 1–3 found no robust general state classifier or directed factor network. Stage 4 changes the estimand again.

Instead of predicting an individual factor, study the **relative payoff spread** between every pair of factors.

There are 28 unordered pairs among the 8 canonical factors.

## Common tape

Use the same clean primitive-universe common factor tape as Stage 3:
- K200
- KOSPI_EX_K200
- KOSDAQ

Each factor-universe return is normalized using 2016–19 scale only, then averaged across the three disjoint universes.

For pair `(A,B)` define 5D relative payoff:

`D[t,A,B] = F[t,A] - F[t,B]`

Pair orientation is fixed by the canonical factor list. Reversing the pair changes both predictor and target signs and therefore does not change continuation/reversal inference.

## Two pre-registered pair mechanisms

### Spec 1 — Relative momentum / reversal

`TRAIL20[t] = sum(D[t-3:t])`

Target:

`FWD20[t] = sum(D[t+1:t+4])`

Fit Discovery regression:

`FWD20 ~ 1 + TRAIL20`

- positive beta = relative continuation;
- negative beta = relative reversal.

### Spec 2 — Short-vs-slow dislocation

`TRAIL60[t] = sum(D[t-11:t])`

`DISLOCATION[t] = TRAIL20[t] - TRAIL60[t]/3`

Fit:

`FWD20 ~ 1 + DISLOCATION`

- negative beta = recent relative move mean-reverts toward its slower 60D pace;
- positive beta = relative acceleration continues.

## Evaluation

Fit coefficients in Discovery 2016–19 only and freeze them.

Compare each model with the Discovery unconditional-mean forecast using:

`incremental_OOS_R2 = 1 - MSE_model / MSE_constant`

Evaluate:
- Validation 2020–22
- Confirmation 2023–24
- Stress 2025
- Stress 2026

Target windows that cross an era boundary are excluded.

## Discovery sign stability

Estimate the predictor beta separately in:
- 2016–17
- 2018–19

Required sign stability for PASS.

## Time-shift placebo

Within each evaluation era, circularly shift the predictor sequence by every feasible non-zero offset while retaining the frozen Discovery coefficient.

Observed alignment must beat at least 90% of shifted alignments (`p <= 0.10`) in both Validation and Confirmation.

## PASS gate

A pair/spec passes only if:
1. incremental OOS R² > 0 in Validation and Confirmation;
2. discovery beta sign is stable across 2016–17 and 2018–19;
3. time-shift placebo p <= 0.10 in Validation and Confirmation.

2025/26 cannot create a PASS.

## Multiple-testing discipline

There are 28 pairs × 2 pre-registered specs = 56 tests.

Do not relax the gate or add pair-specific windows after viewing results.

Headline results:
- total passing pair/specs;
- whether passing relations are continuation or mean reversion;
- factor families recurring across passing pairs;
- any pair passing both specifications coherently.

## Next step

- If stable pair dynamics survive: falsify those exact pairs across 10D/40D horizons and then evaluate whether they improve factor allocation.
- If none survive: stop simple linear temporal dynamics and reserve Stage 5 for explicitly exploratory rotation geometry / dynamic modes.

No portfolio backtest is permitted in Stage 4.
