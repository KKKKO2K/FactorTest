# Stage 2 Protocol — Falsification of KOSDAQ -> K200 Factor Propagation

Stage 1 was used to select the one clean directed edge among the three mutually disjoint primitive universes:

`KOSDAQ -> K200`

The other primitive universe is `KOSPI_EX_K200`.

This stage does **not** search over the 30 edges again. It attempts to falsify this exact selected edge.

Because the edge was selected after looking at 2020–24 Stage-1 results, Stage 2 is a robustness/falsification exercise, not an independent untouched OOS confirmation.

## Primitive-universe restriction

Primary tests use only:
- KOSDAQ
- K200
- KOSPI_EX_K200

Composite universes are excluded from the primary mechanism test to remove mechanical overlap from union definitions.

## Primary test — unique KOSDAQ information after third-universe control

For each of the 8 factors, fit on Discovery 2016–19:

Model 0:

`K200[t+1] ~ 1 + K200[t]`

Model EX:

`K200[t+1] ~ 1 + K200[t] + KOSPI_EX_K200[t]`

Model KQ:

`K200[t+1] ~ 1 + K200[t] + KOSDAQ[t]`

Model BOTH:

`K200[t+1] ~ 1 + K200[t] + KOSPI_EX_K200[t] + KOSDAQ[t]`

The key quantity is the unique incremental value of KOSDAQ after the ex-K200 factor tape is already known:

`unique_KQ_R2 = 1 - MSE_BOTH / MSE_EX`

For symmetry also compute:

`unique_EX_R2 = 1 - MSE_BOTH / MSE_KQ`

A strong KOSDAQ-leading interpretation requires in BOTH 2020–22 and 2023–24:
- median `unique_KQ_R2 > 0` across 8 factors;
- >=5/8 factors positive;
- median `unique_KQ_R2 > unique_EX_R2`.

## Horizon test

Fit separate discovery models for:
- next 5D: target block t+1;
- gap 5D: target block t+2;
- next 10D: sum of normalized K200 returns over t+1 and t+2;
- next 20D: sum over t+1 ... t+4.

The 5D result is primary. Longer horizons show whether the effect accumulates, dissipates, or reverses.

A propagation effect is allowed to be short-lived; loss of the edge at gap/20D is not automatically a failure. But a sign reversal immediately at 10D would materially weaken the interpretation.

## Discovery coefficient stability

For the primary 5D BOTH model, separately estimate source coefficients in:
- 2016–17;
- 2018–19.

Report factor-by-factor sign stability. This is diagnostic, not a tunable gate.

## Leave-one-factor-out robustness

For the primary unique KOSDAQ R², recompute the edge-level median after dropping each of the 8 factors.

If dropping one factor flips the aggregate sign in either Validation or Confirmation, classify the result as factor-fragile.

## Time-shift placebo

For each factor and evaluation period, keep the frozen Discovery coefficients but circularly shift the KOSDAQ current-return sequence relative to K200 by all feasible non-zero offsets.

Recompute the augmented-model incremental R² under each false temporal alignment.

At the edge level, compare the observed median incremental R² with the distribution of shifted medians.

This asks whether **the actual time ordering matters**, rather than KOSDAQ merely being a highly correlated proxy for the same common tape.

## Stress slices

Report 2025 and 2026, but they cannot create a PASS.

## Interpretation labels

- `ROBUST_DIRECTIONAL`: primary unique-control gate passes, leave-one-factor-out is stable, and observed temporal alignment is better than most placebo shifts in both Validation and Confirmation.
- `WEAK_DIRECTIONAL`: Stage-1 edge survives some but not all falsification checks.
- `COMMON_PROXY`: KOSDAQ loses incremental value once ex-K200/common information is controlled.
- `REJECT`: primary unique-control relation is non-positive or inconsistent across Validation and Confirmation.

No portfolio backtest is permitted in Stage 2.
