# Zero-Base Factor Regime Research Status

## Current research order

1. **Factor Persistence / Rotation** — completed Stage 1 + economic Stage 1b.
2. **Factor Opportunity** — completed Stage 2 + combined Stage 2b policy.
3. **Factor Crash / Crowding** — completed factor-return-only Stage 3 + Stage 3b crash cap; next extension requires genuinely new stock-level information.
4. **Stock-Level Regime Extension** — next: participation, turnover/ADV, selection overlap and contribution concentration, constructed without old B/F regime labels.
5. **Market Transition** — secondary use only after the factor-allocation questions above are exhausted.

## What survived

### 1. Persistence / Rotation is forecastable
Direct canonical 8-factor payoff data, with no B/F labels or KMeans, produced 29 PASS feature-target relations out of 90 predeclared screens.

The recurring structural signals are:
- cross-horizon factor-rank agreement;
- current 20D/60D factor dispersion;
- leader strength / winner-vs-median separation;
- 20D/60D sign alignment;
- dispersion acceleration.

Economic implication: the persistence composite materially improves on **always chasing the current top-2 factors**. At 10 bps, median Sharpe improvement vs TOP2 is +0.48 in 2023-24, +0.96 in 2025 and +0.96 in 2026. However it remains below simple EW8 diversification in median Sharpe.

**Status:** useful state variable; not yet a standalone allocation edge over EW8.

### 2. Factor Opportunity is forecastable
Future 20D cross-factor dispersion / absolute opportunity / range produced 19 PASS relations out of 54 screens.

The strongest repeated predictors are:
- current dispersion;
- current factor range;
- leader strength;
- current absolute opportunity;
- winner gap.

These features suggest opportunity has persistence: a wide factor cross-section today often precedes a wider factor cross-section over the next 20D.

But the mechanical Opportunity x Persistence policy does not robustly beat EW8. At 10 bps it beats EW8 in 2023-24, but loses in 2020-22, 2025 and 2026.

**Status:** useful active-risk/context signal; simple tercile gating rejected.

### 3. Factor-return-only crash/crowding has limited incremental value
Several adverse-target relationships pass, but two target families are mechanically close to the Stage-1 persistence targets and should not be counted as independent discoveries.

The genuinely useful new observation is that large cross-sectional winner/loser separation — especially loser weakness, current dispersion and top-2 premium — is associated with subsequent current-winner relative loss in historical DEV/CONFIRM samples.

A predeclared crash cap using these three variables fails economically: it does not improve persistence-only broadly and does not close the gap to EW8.

**Status:** do not tune thresholds further on factor returns alone.

## Current best interpretation of Factor Regime

Factor Regime should not be a single discrete F_HIGH/F_LOW label. The evidence supports a **continuous multi-axis state**:

- **Persistence axis:** probability that current factor leadership continues vs rotates.
- **Opportunity axis:** expected magnitude of future cross-factor payoff dispersion.
- **Crowding/crash axis:** requires additional stock-level information; factor-return-only proxies are insufficient.

The first two axes contain predictive information, but a simple 3-state trading rule has not yet beaten EW8 robustly. Therefore the next research question is whether stock-level participation/liquidity/crowding can identify the subset of high-opportunity periods where active factor selection is actually worth taking.

## Next predeclared research step: Stock-Level Regime Extension

Build state-date features independently of prior B/F labels:

### Participation
- universe positive-20D breadth;
- selected-factor portfolio positive-20D breadth;
- participation divergence: factor-sleeve strength vs underlying-stock breadth;
- breadth acceleration / deterioration.

### Liquidity / trading activity
- selected holdings median and percentile turnover/ADV/activity rank;
- fraction of selected holdings with elevated recent trading activity;
- change in activity rank vs prior 20D/60D baseline;
- contribution-weighted trading activity if raw turnover/ADV is available.

### Concentration / crowding
- top-5 contribution concentration;
- selected-holding return dispersion;
- holding retention / turnover;
- overlap of leaders across factor sleeves;
- all-factor selection multiplicity / crowding.

### Targets
Do **not** target market direction first. Primary targets are:
1. future factor-selection alpha vs EW8;
2. future top-factor relative loss / reversal;
3. future cross-factor opportunity conditional on active-selection success.

### Evidence discipline
- expanding annual walk-forward;
- all thresholds learned from prior data;
- 6 universes separately;
- 2025/2026 remain stress slices, not tuning samples;
- no ad-hoc composite from near-misses;
- if stock-level features fail, freeze Persistence and Opportunity as monitoring/risk-budget variables and stop searching for a factor-allocation regime in the current data stack.
