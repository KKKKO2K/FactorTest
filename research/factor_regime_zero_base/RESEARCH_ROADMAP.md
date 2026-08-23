# Zero-Base Factor Regime Research Roadmap

## Research reset

This track deliberately does **not** start from B/F regime labels, KMeans states, or previously selected thresholds. The primitive input is the canonical factor payoff panel. Regime labels may be introduced only after a continuous predictive relationship is established.

### Data contract
- Primary source: `research/factor_regime_v1/results/factor_5d_returns.csv`
- Primary payoff: canonical factor long-short return (`ls_return`)
- Canonical factors: MOM1M, MOM12_1, OP12_REV, OPFY1_REV, PBR12MF, PER12MF, PRIVATE_FLOW, FOREIGN_FLOW
- Universes: all six available universes are tested separately.
- Evaluation: expanding annual walk-forward. Each evaluation year is predicted using only earlier observations.
- 2025/2026 are reported as stress slices, not treated as pristine untouched OOS because prior research has already inspected those periods.
- No feature or threshold may be selected from 2025/2026 and then back-propagated into earlier tests.

## Ordered research program

### 1. Factor Persistence / Rotation — first priority
Question: **Will current factor leadership persist, or rotate/reverse?**

Primary targets:
1. 20D factor-rank persistence: Spearman rank correlation between trailing-20D and forward-20D factor payoffs.
2. 60D factor-rank persistence: trailing-60D vs forward-60D rank correlation.
3. Top-2 survival: fraction of current top-2 factors remaining in future top-4 / top-2.
4. Factor-momentum payoff: forward return of current top-2 minus forward return of current bottom-2.

Predeclared predictor families:
- breadth: fraction of factors with positive recent payoff;
- dispersion / range / current opportunity;
- leadership concentration and winner gap;
- recent rank stability / rank turnover;
- 20D vs 60D cross-horizon agreement;
- breadth and dispersion acceleration;
- factor commonality: average pair correlation and PC1 share;
- median factor volatility and sign alignment.

Stage-1 evidence gate for a predictor-target relation:
- train-learned direction must have positive median directed OOS Spearman in 2020-22;
- positive median directed OOS Spearman again in 2023-24;
- 2023-24 directed Spearman must be positive in at least 4/6 universe medians;
- 2023-24 train-threshold high-vs-low target spread must have the same directed sign.

Only relations that clear this gate move to a multivariate/composite or trading-policy test.

### 2. Factor Opportunity
Question: **Will factor selection have enough cross-factor dispersion to justify active factor risk?**

Targets:
- forward 20D/60D cross-factor dispersion;
- forward mean absolute factor payoff;
- forward best-minus-worst factor payoff.

Decision use:
- high opportunity -> larger active factor risk budget;
- low opportunity -> reduce factor-selection risk / diversify.

### 3. Factor Crash / Crowding Risk
Question: **Is the current winning-factor trade vulnerable to a sharp reversal?**

Targets:
- forward drawdown of current leaders;
- current top-factor future underperformance vs equal-weight factors;
- probability of top-quartile leader moving to bottom half / bottom quartile.

Predictors may add stock-level participation, turnover/ADV and holdings overlap once those inputs are available and cleanly aligned.

### 4. Market Transition — secondary use only
Question: **Does factor structure improve the probability that the current market regime deteriorates?**

The prior B x F result is retained only as a benchmark. This stage is not allowed to drive feature selection in Stages 1-3.

## Research discipline
1. Start with continuous features and predictive targets; do not pre-label regimes.
2. Use simple monotonic screens and walk-forward tests before nonlinear models.
3. Do not combine near-miss features after seeing stress-period outcomes.
4. Economic implementation is tested only after predictive stability is established.
5. If no robust persistence/opportunity/crash signal survives, the correct conclusion is that Factor Regime is descriptive/risk-monitoring information rather than a forecastable alpha state.
