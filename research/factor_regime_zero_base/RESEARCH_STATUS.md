# Zero-Base Factor Regime Research Status

## Current research order

1. **Factor Persistence / Rotation** — completed Stage 1 + economic Stage 1b.
2. **Factor Opportunity** — completed Stage 2 + combined Stage 2b policy.
3. **Factor Crash / Crowding** — completed factor-return-only Stage 3 + Stage 3b crash cap; factor-return-only crash research is frozen.
4. **Stock-Level Regime Extension** — completed Stage 4A aggregate stock/liquidity predictive screen + Stage 4B hard permission policy.
5. **Continuous Factor Risk Budgeting** — current next step: preserve EW8 diversification and convert surviving Persistence + Liquidity/Selectivity information into a bounded continuous tilt rather than a discrete regime switch.
6. **Leader-Specific Raw Stock Extension** — only if continuous tilt remains economically weak; reconstruct leader-specific participation, turnover/ADV, contribution concentration and holdings overlap from raw point-in-time stock data.
7. **Market Transition** — secondary use only after the factor-allocation questions above are exhausted.

## What survived

### 1. Persistence / Rotation is forecastable
Direct canonical 8-factor payoff data, with no B/F labels or KMeans, produced 29 PASS feature-target relations out of 90 predeclared screens.

Recurring structural signals:
- cross-horizon factor-rank agreement;
- current 20D/60D factor dispersion;
- leader strength / winner-vs-median separation;
- 20D/60D sign alignment;
- dispersion acceleration.

Economic implication: the persistence composite materially improves on always chasing the current top-2 factors. At 10 bps, median Sharpe improvement vs TOP2 is about +0.48 in 2023-24, +0.96 in 2025 and +0.96 in 2026. However it remains below simple EW8 diversification in median Sharpe.

**Status:** useful continuous state variable; not a standalone discrete allocation edge over EW8.

### 2. Factor Opportunity is forecastable
Future 20D cross-factor dispersion / absolute opportunity / range produced 19 PASS relations out of 54 screens.

Strong repeated predictors:
- current dispersion;
- current factor range;
- leader strength;
- current absolute opportunity;
- winner gap.

These features imply opportunity persistence: a wide factor cross-section today often precedes a wider factor cross-section over the next 20D.

But the mechanical Opportunity x Persistence tercile policy does not robustly beat EW8. At 10 bps it beats EW8 in 2023-24 but loses in 2020-22, 2025 and 2026.

**Status:** useful active-risk/context signal; hard tercile gating rejected.

### 3. Factor-return-only crash/crowding has limited incremental value
Several adverse-target relationships pass, but two target families are mechanically close to Stage-1 persistence targets and are not independent discoveries.

The useful new observation is that large cross-sectional winner/loser separation — especially loser weakness, current dispersion and top-2 premium — is associated with subsequent current-winner relative loss in historical DEV/CONFIRM samples.

A predeclared crash cap using these variables fails economically and does not improve persistence-only broadly.

**Status:** do not tune thresholds further on factor returns alone.

### 4. Aggregate stock/liquidity state adds predictive information
Point-in-time aggregate stock/liquidity features were tested without old regime labels. Stage 4A produced 16 PASS relations out of 40 screens.

The strongest relation for future current-TOP2 alpha vs EW8 is low broad market trading-activity participation:
- MKT_ACT1_BREADTH: DEV directed IC about +0.07; 2023-24 directed IC about +0.24; 6/6 confirmation universes; train-tercile forward TOP2-alpha spread about +2.04% per 20D.
- MKT_ACT5_BREADTH and changes in ACT1/ACT5 breadth also pass historically.
- FACTOR_TOP_ACT5_BREADTH_MEAN passes both TOP2-vs-EW8 alpha and factor-momentum screens and retains the expected direction in 2025/2026 stress slices.

Interpretation: **factor opportunity magnitude and factor-selection quality are different axes.** Broad market trading activity can imply a wide future factor cross-section while simultaneously reducing the relative quality of simply chasing current factor winners.

A hard top-tercile liquidity permission rule still fails to beat EW8 broadly. This reinforces the recurring pattern: predictive rank information survives, while discrete HIGH/LOW implementation destroys too much diversification.

**Status:** stock/liquidity selectivity is a credible incremental state variable, but hard permission gating is rejected.

## Current best interpretation of Factor Regime

Factor Regime should not be a single discrete F_HIGH/F_LOW label. The evidence supports a **continuous multi-axis state**:

- **Persistence axis:** how much current factor leadership should be trusted.
- **Opportunity axis:** expected magnitude of future cross-factor payoff dispersion.
- **Selectivity / liquidity axis:** whether current factor winners are supported in a selective versus market-wide trading-activity environment.
- **Crowding/crash axis:** factor-return-only proxies are insufficient; leader-specific stock-level information may be needed later.

The consistent empirical pattern is:

> predictive IC exists, but hard tercile regime switches are economically unstable.

Therefore the next experiment treats Factor Regime as a **risk-budgeting signal**, not a classification problem.

## Current predeclared research step: Continuous Factor Tilt

### Portfolio architecture
Always retain EW8 as the core portfolio.

For each state date, define the current TOP2 factors from trailing 20D factor payoff and a continuous tilt coefficient lambda:

`w_t = EW8 + lambda_t * (TOP2 - EW8)`

### Frozen mapping before the run
- Persistence block: equal-weight standardized score from the seven Stage-1 survivors for future factor momentum.
- Liquidity/selectivity block: equal-weight standardized score from MKT_ACT1_BREADTH, MKT_ACT1_CHANGE_4 and FACTOR_TOP_ACT5_BREADTH_MEAN, with direction learned only from prior data for future TOP2 alpha vs EW8.
- Combined score: equal weight of the Persistence block and Liquidity/Selectivity block.
- Convert each score to its **prior-data empirical percentile**; no OOS threshold fitting.
- Continuous tilt: `lambda = 0.25 * (2 * percentile - 1)`, bounded to [-0.25, +0.25].
  - +0.25 means a modest overweight of current TOP2 while retaining all eight factors.
  - 0 means pure EW8.
  - -0.25 means a modest underweight of current TOP2, not a wholesale switch to BOTTOM2.
- No threshold sweep and no max-tilt sweep after viewing results.
- Evaluate three variants: Persistence-only continuous tilt, Liquidity-only continuous tilt, and equal-block Combined continuous tilt.

### Evidence discipline
- expanding annual walk-forward;
- all standardization, directions and empirical percentile mappings use only prior data;
- non-overlapping 20D decisions;
- 6 universes separately;
- transaction costs 0 / 10 / 30 bps on factor-sleeve turnover;
- 2025/2026 remain stress slices, not tuning samples;
- primary benchmark is EW8;
- success requires positive median Sharpe improvement vs EW8 in both 2020-22 and 2023-24, improvement in at least 4/6 universes in 2023-24, and no dependence on 2025 or 2026 alone.

If the bounded continuous tilt fails, do not optimize its amplitude. Move to leader-specific raw stock participation/turnover/overlap or freeze Persistence/Opportunity/Selectivity as monitoring variables.
