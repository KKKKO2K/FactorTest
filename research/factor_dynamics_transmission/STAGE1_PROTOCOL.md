# Stage 1 Protocol — Common/Local Factor Shocks and Cross-Universe Propagation

This protocol is frozen before viewing Stage 1 results.

## Primary data

`research/factor_regime_v1/results/factor_5d_returns.csv`

Use the same 8 canonical factors and 6 universe definitions listed in `RESEARCH_ROADMAP.md`.

## Time partitions

- Discovery: target dates in 2016–2019
- Validation: target dates in 2020–2022
- Confirmation: target dates in 2023–2024
- Stress: target dates in 2025
- Stress: target dates in 2026

2025/26 cannot create a PASS.

## Normalization

For each factor × universe series, estimate mean and standard deviation using Discovery only.

Primary normalized return:

`z[t,f,u] = (R[t,f,u] - discovery_mean[f,u]) / discovery_std[f,u]`

The normalization is frozen for all later periods.

## Test A — Common versus local factor shocks

For each factor/date:

`common[t,f] = mean_u z[t,f,u]`

`local[t,f,u] = z[t,f,u] - common[t,f]`

Report by era:
- common 1-step (next 5D) Spearman continuation for each factor;
- local-residual 1-step Spearman continuation for each factor × universe;
- median common continuation across 8 factors;
- median local continuation across 48 factor-universe series;
- common variance share by factor/era.

Interpretation:
- positive common continuation = system-wide factor shock persistence;
- negative local continuation = universe-specific deviation mean reversion;
- positive source-local to destination-local lag correlation = residual diffusion.

No PASS/FAIL is assigned from Test A alone.

## Test B — Directed same-factor cross-universe propagation

For each factor and ordered universe pair `A -> B`, build one-step-ahead models on normalized 5D returns.

Baseline:

`B[t+1] = a + b * B[t]`

Augmented:

`B[t+1] = a + b * B[t] + c * A[t]`

Fit both models using Discovery target dates only. Freeze all coefficients afterward.

For each later era compute:

`incremental_OOS_R2 = 1 - MSE_augmented / MSE_baseline`

Positive values mean the source universe adds predictive information beyond the destination's own lag.

### Primary aggregation

Do **not** treat 240 factor-edge tests as 240 independent discoveries.

The main object is each of the 30 ordered universe edges aggregated across all 8 factors.

An edge `A -> B` is a Stage-1 PASS only if BOTH Validation and Confirmation satisfy:
- median incremental OOS R² across factors > 0; and
- at least 5 of 8 factors have positive incremental OOS R².

### Directionality check

For every edge compare its result with the reverse edge `B -> A`.

A PASS edge is labelled:
- `directional` if its median incremental OOS R² exceeds the reverse edge in both Validation and Confirmation;
- `bidirectional/common` otherwise.

This prevents symmetric co-movement from being mislabelled as transmission.

## Test C — Local-residual diffusion diagnostic

For each factor and ordered universe pair `A -> B`, compute the Spearman relation between:

`local[t,f,A]` and `local[t+1,f,B]`.

Aggregate by universe edge across factors and eras.

This is diagnostic only in Stage 1. It is used to interpret any PASS from Test B as catch-up/diffusion versus common-shock contamination.

## Falsification discipline

A Stage-1 propagation claim must not be based on:
- one factor only;
- 2025/26 only;
- contemporaneous correlation;
- a source coefficient without OOS improvement;
- an edge that disappears after destination own-lag control.

No trading strategy or allocation rule is tested in Stage 1.

## Stage-2 eligibility

Stage 2 proceeds only if at least one of the following is true:
1. at least one directed universe edge passes Test B; or
2. Test A shows a stable common-vs-local asymmetry across Validation and Confirmation that motivates a separate mechanism test.

Otherwise same-factor cross-universe propagation is rejected and research moves to pairwise factor relative-value or cross-factor transmission without attempting to rescue Stage 1.
