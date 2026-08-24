# Pairwise Ranking + Abstention / Confidence Sizing — Research Protocol

## Purpose

This follow-up uses the already-frozen Discovery-trained pairwise ranking model from `research/nonstationary_factor_selection` and asks a different question:

> Can we identify when the ranking signal is strong enough to justify active factor selection, while otherwise abstaining and staying at EW8?

This is **post-hoc exploratory research** because prior 2020–24 pairwise results have already been inspected. It is not an untouched OOS confirmation.

No new ranking coefficients are fit on 2020+ data and no threshold is chosen using 2020+ performance.

## Data

Canonical panel: `research/factor_regime_v1/results/factor_5d_returns.csv`

8 factors × 6 universes, 5D factor long-short returns.

The ranking model is fit on 2016–19 only, exactly as in the prior non-stationary selection track.

## Pairwise model

For each factor pair, the frozen Discovery-only logistic model uses differences in:
- current 5D return
- trailing 20D return
- trailing 60D return
- trailing 20D volatility
- current cross-sectional rank

The model produces 28 pairwise probabilities and an 8-factor tournament/Borda score each decision date.

## Confidence variables

Confidence is derived **only from the predicted pairwise probability geometry**, not from future returns.

Predeclared diagnostics:

1. `PAIR_MARGIN`
   - mean across 28 pairs of `2 * abs(p_ij - 0.5)`.
   - high when pairwise contests are far from 50/50.

2. `SCORE_SD`
   - cross-sectional standard deviation of the 8 Borda/tournament scores.
   - high when predicted factor quality is well separated.

3. `TOP_GAP`
   - top-ranked Borda score minus second-ranked score.

4. `CYCLE_RATE`
   - fraction of all 56 factor triples that form a directed majority cycle under `p_ij > 0.5`.
   - lower means the pairwise ranking is more internally transitive/consistent.

5. `COMBINED_CONF`
   - equal-weight average of Discovery-standardized `PAIR_MARGIN`, `SCORE_SD`, `TOP_GAP`, and negative `CYCLE_RATE`.
   - standardization moments are estimated on 2016–19 only and frozen.

No outcome variable is used to choose or weight these confidence features.

## Discovery-only abstention calibration

Hard high-confidence threshold:
- 80th percentile of `COMBINED_CONF` in 2016–19.

Continuous confidence intensity:
- convert `COMBINED_CONF` to its empirical percentile in the frozen 2016–19 distribution;
- intensity = `max(0, 2 * percentile - 1)`;
- therefore the strategy fully abstains below the Discovery median and scales smoothly from 0 to 1 above it.

No alternative confidence thresholds are searched after seeing results.

## Portfolio rules

EW8 is the default portfolio in every rule.

### 1. `CONF_SOFT`
- if `COMBINED_CONF` > Discovery 80th percentile: use the frozen `PAIRWISE_SOFT` weights;
- otherwise: EW8.

### 2. `CONF_HALF_TOP3`
- if high confidence: `EW8 + 0.5 * (PAIRWISE_TOP3 - EW8)`;
- otherwise: EW8.

This keeps all 8 factors positive while giving moderate emphasis to the top 3.

### 3. `CONT_HALF_TOP3`
- `EW8 + 0.5 * intensity * (PAIRWISE_TOP3 - EW8)`.

This is continuous confidence sizing with automatic abstention below the Discovery median.

### 4. `CONF_BOTTOM2_VETO`
- if high confidence: equal-weight the six factors excluding the predicted bottom two;
- otherwise: EW8.

This tests whether confidence is more useful for negative selection than concentrated winner selection.

Benchmarks:
- `EW8`
- `PAIRWISE_SOFT`
- `PAIRWISE_TOP3`
- prior exploratory `PAIRWISE_BOTTOM2_VETO`

## Diagnostic test before portfolio attribution

For each period, assign dates to five bins using **Discovery confidence quintile cut points**.

Within each confidence bin report:
- realized cross-sectional rank IC of the predicted Borda score vs same-period 5D factor returns;
- realized top3-minus-EW8 5D spread;
- realized bottom2-veto-minus-EW8 5D spread;
- number of observations.

Primary scientific question:

> Does higher ex-ante confidence actually correspond to better ranking accuracy or larger selection spread?

A confidence filter is not considered meaningful if Q5 does not improve ranking/spread relative to lower-confidence bins in both 2020–22 and 2023–24.

## Economic evaluation

Costs: 0 / 10 / 30 bps per unit factor-weight turnover.

Periods:
- Validation: 2020–22
- Confirmation-style historical check: 2023–24
- Stress diagnostics: 2025, 2026

Primary-style economic gate at 10 bps:
- median ΔSharpe vs EW8 > 0 in 2020–22 and 2023–24;
- >=4/6 universes improve in both periods.

Because this entire follow-up was motivated after inspecting prior results, passing this gate is still **exploratory evidence**, not clean OOS validation.

## Interpretation hierarchy

- `CONFIDENCE_VALID`: confidence Q5 improves ranking diagnostics in both 2020–22 and 2023–24, and at least one abstention strategy passes the primary-style economic gate.
- `DIAGNOSTIC_ONLY`: confidence predicts ranking quality but no economic rule passes.
- `IMPLEMENTATION_ONLY`: economic improvement occurs without confidence-quality monotonicity; treat cautiously as path-dependent implementation effect.
- `REJECT`: confidence does not reliably identify better ranking periods and no abstention rule passes.

## Anti-overfitting rules

- Do not refit pairwise coefficients after 2019.
- Do not change 80th percentile threshold.
- Do not change 50% top3 tilt cap.
- Do not change bottom-two veto size.
- Do not add extra confidence metrics after results.
- Do not use 2025/26 to create a PASS.
