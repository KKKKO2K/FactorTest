# Factor Regime Zero-Base v2

## Why restart

This track treats all prior Factor Regime outputs, labels, survivor variables, thresholds and portfolio rules as archived evidence only. None are inputs to v2.

The only inherited research input is the canonical point-in-time factor payoff panel itself: 8 factors across 6 universes from `research/factor_regime_v1/results/factor_5d_returns.csv`.

## Non-negotiable rules

1. No B/F states, KMeans labels, prior `F_HIGH/F_LOW`, prior survivor lists, or prior thresholds.
2. Do not start from a desired trading rule. First establish what empirical phenomenon exists in the factor payoff panel.
3. Separate four questions: existence -> persistence/predictability -> robustness -> economic implementation.
4. 2025 and 2026 are never used to choose variables, thresholds or model forms.
5. Cross-universe replication is required; one universe is never sufficient evidence.
6. No feature pruning after looking at confirmation-period performance unless a new untouched validation period is reserved.
7. Portfolio implementation comes last and starts from EW8 as the benchmark; continuous sizing is preferred to hard switching unless the data clearly supports discontinuities.
8. If a phenomenon is not stable before portfolio construction, stop that branch rather than tuning it.

## Research sequence

### Stage 0 — Empirical structure map
No predictive model and no regime labels.

Measure directly:
- unconditional factor payoff distribution by factor, universe and era;
- cross-factor correlation/commonality;
- cross-universe agreement of factor rankings;
- 20D/60D factor breadth, dispersion, range and concentration;
- empirical factor-rank persistence and top-factor survival;
- unconditional winner continuation/reversal and opportunity persistence.

Purpose: decide which phenomena are real enough to deserve a forecasting study.

### Stage 1 — Pre-register targets
Only after Stage 0, select at most 2–3 phenomena with strong unconditional structure. Define exact targets before predictor search. Candidate target families may include:
- factor-rank persistence/rotation;
- future cross-factor opportunity/dispersion;
- winner continuation vs reversal;
- commonality/correlation expansion.

### Stage 2 — Minimal predictor study
Start with primitive observables, not engineered composites. Use annual expanding walk-forward. Begin with univariate rank IC and monotonicity; only then test low-dimensional multivariate models.

### Stage 3 — Stability and falsification
Require sign stability across eras and replication across the six universes. Run placebo horizons, alternative factor windows and leave-one-factor-out tests. Reject relationships that depend on one factor family or one calendar episode.

### Stage 4 — Economic translation
Only surviving phenomena become portfolio signals. Benchmark against EW8 and simple factor momentum/contrarian baselines. Use realistic costs. No threshold or max-tilt sweeps after seeing results.

### Stage 5 — Stock-level extension
Use stock-level participation/liquidity/overlap only if Stage 2–4 identifies a factor-level phenomenon that clearly needs an incremental explanatory variable. Do not add stock-level features merely to rescue a failed factor-return model.

### Stage 6 — Market-state application
Market timing is secondary. Test only after a robust factor-level phenomenon exists.

## Decision discipline

At every stage produce one of three labels:
- **STRUCTURAL**: broad, stable phenomenon worth further study.
- **CONDITIONAL**: real but unstable/segment-specific; monitor, do not trade yet.
- **REJECT**: insufficiently stable; stop that branch.

No production claim is allowed until Stage 4 passes with predeclared rules.
